import asyncio
from logging.config import fileConfig

from sqlalchemy import select

from alembic import context

from app.db.base import TenantBase
from app.db.database_manager import db_manager
from app.models.shared import Tenant

# Import models to ensure they are registered in metadata
from app.models import tenant as tenant_models  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = TenantBase.metadata


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode for tenants."""

    # 1. Determine target tenants
    # Usage: alembic -n tenant upgrade head -x tenant_id=abc
    x_args = context.get_x_argument(as_dictionary=True)
    target_tenant_id = x_args.get("tenant_id")

    tenant_ids = []

    if target_tenant_id:
        print(f"Targeting single tenant: {target_tenant_id}")
        tenant_ids = [target_tenant_id]
    else:
        print("Targeting ALL tenants")
        try:
            shared_engine = db_manager.get_shared_engine()
            async with shared_engine.connect() as conn:
                # Ensure shared tables exist (User/Tenant) to query tenants?
                # Usually shared migration runs first.
                # But if we run this on a fresh install, Shared DB might be empty or tables not exists.
                # Assuming shared migration has run.
                result = await conn.execute(select(Tenant.tenant_id))
                tenant_ids = list(result.scalars().all())
        except Exception as e:
            print(f"Error querying tenants from Shared DB: {e}")
            return

    if not tenant_ids:
        print("No tenants found to migrate.")
        return

    # 2. Iterate and migrate
    for tenant_id in tenant_ids:
        print(f"--- Migrating Tenant: {tenant_id} ---")
        try:
            # Check if engine is valid/active before migrating
            try:
                engine = await db_manager.get_tenant_engine(tenant_id)
            except Exception as e:
                print(f"Skipping tenant {tenant_id} due to connection error: {e}")
                continue

            async with engine.connect() as connection:
                await connection.run_sync(do_run_migrations)

            print(f"--- Completed Tenant: {tenant_id} ---")

        except Exception as e:
            print(f"!!! Failed to migrate tenant {tenant_id}: {e}")
            # We continue to the next tenant

    # Clean up connections explicitly
    await db_manager.dispose_all()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Note: Offline mode for multi-tenant is tricky because we need the URL for each tenant.
    We typically don't run offline migrations for dynamic tenants easily.
    Here we implement a placeholder or basic offline for a default tenant if needed.
    """
    print("Offline migrations not fully supported for dynamic tenants yet.")
    # url = ...
    # context.configure(
    #     url=url,
    #     target_metadata=target_metadata,
    #     literal_binds=True,
    #     dialect_opts={"paramstyle": "named"},
    # )
    # with context.begin_transaction():
    #     context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
