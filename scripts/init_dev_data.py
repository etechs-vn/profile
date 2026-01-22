import asyncio
import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.db.database_manager import db_manager
from app.modules.auth.models import Tenant
from app.core.config import settings
from sqlalchemy import select


async def main():
    print("Initializing dev data...")
    engine = db_manager.get_shared_engine()

    # Ensure tables exist (in case alembic didn't run or for safety)
    # But we just ran alembic.

    async with engine.begin() as conn:
        # Check and create sample tenant
        result = await conn.execute(
            select(Tenant).where(Tenant.tenant_id == "dev_tenant")
        )
        if not result.scalar():
            print("Creating 'dev_tenant'...")
            await conn.execute(
                Tenant.__table__.insert().values(
                    tenant_id="dev_tenant",
                    name="Development Tenant",
                    status="active",
                    # db_host=None implies default strategy (e.g. sqlite file ./tenants/tenant_dev_tenant.db)
                )
            )
        else:
            print("'dev_tenant' already exists.")

    # Provision Database if Postgres
    if settings.postgres_server:
        print("Provisioning Postgres DB for dev_tenant...")
        try:
            # New provisioner API
            # Get config first or assume defaults
            await db_manager.provisioner.provision_database("dev_tenant", None, None)
        except Exception as e:
            print(f"Provisioning failed (might already exist): {e}")

    print("Done.")
    await db_manager.dispose_all()


if __name__ == "__main__":
    asyncio.run(main())
