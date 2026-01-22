import asyncio
import logging
import sys
import os

# Ensure app is in python path
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.db.database_manager import db_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    tenant_id = "dev_tenant"
    db_name = f"tenant_{tenant_id}"

    # 1. Insert into Shared DB
    logger.info("Checking Shared DB for tenant...")
    shared_engine = db_manager.get_shared_engine()

    async with shared_engine.begin() as conn:
        # Check if exists
        result = await conn.execute(
            text("SELECT 1 FROM tenants WHERE tenant_id = :tid"), {"tid": tenant_id}
        )
        if not result.scalar():
            logger.info(f"Creating tenant record: {tenant_id}")
            # Insert simple tenant
            # Note: id is auto-increment
            await conn.execute(
                text(
                    "INSERT INTO tenants (tenant_id, name, status) VALUES (:tid, :name, 'active')"
                ),
                {"tid": tenant_id, "name": "Development Tenant"},
            )
        else:
            logger.info("Tenant record exists.")

    # 1.5 Drop existing DB to ensure clean state
    logger.info(f"Dropping database {db_name} if exists...")
    maintenance_url = str(shared_engine.url).replace(
        shared_engine.url.database, "postgres"
    )
    # We need a new engine for maintenance (postgres db)
    # db_manager uses a private method _build_postgres_url in settings, but we can construct it or use settings if exposed.
    # To keep it simple, we can hack it from shared_engine url or use settings.
    # Let's import settings.
    from app.core.config import settings

    maintenance_url = settings._build_postgres_url("postgres")

    from sqlalchemy.ext.asyncio import create_async_engine

    temp_engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    async with temp_engine.connect() as conn:
        # Terminate connections first
        await conn.execute(
            text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid()
        """)
        )
        await conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
    await temp_engine.dispose()

    # 2. Provision physical DB only (do NOT create schema)
    logger.info("Provisioning physical database...")
    await db_manager.provisioner.provision_database(tenant_id, None, None)

    logger.info("Done. Tenant 'dev_tenant' is ready for migration.")


if __name__ == "__main__":
    asyncio.run(main())
