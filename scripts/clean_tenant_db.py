import asyncio
from sqlalchemy import text, inspect
from app.db.database_manager import db_manager
from app.db.base import TenantBase


async def clean_tenant():
    tenant_id = "dev_tenant"
    print(f"Connecting to tenant database: {tenant_id}...")
    try:
        engine = await db_manager.get_tenant_engine(tenant_id)
    except Exception as e:
        print(f"Could not connect to tenant db (might not exist yet): {e}")
        return

    async with engine.begin() as conn:
        print("Dropping all tables defined in TenantBase metadata...")
        await conn.run_sync(TenantBase.metadata.drop_all)

        # Also force drop alembic_version if exists
        print("Dropping alembic_version table...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

        # Inspect and drop any other tables not in metadata (leftovers)
        # Note: drop_all only drops tables in metadata.
        def get_all_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_all_tables)
        if tables:
            print(f"Found remaining tables: {tables}, dropping them...")
            for table in tables:
                print(f"Dropping {table}...")
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

    print(f"Tenant database {tenant_id} cleaned successfully.")
    await db_manager.dispose_all()


if __name__ == "__main__":
    asyncio.run(clean_tenant())
