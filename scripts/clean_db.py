import asyncio
from sqlalchemy import text
from app.db.database_manager import db_manager
from app.models.shared import User, Tenant  # Ensure models are registered
from app.db.base import SharedBase


async def clean():
    print("Connecting to shared database...")
    engine = db_manager.get_shared_engine()
    async with engine.begin() as conn:
        print("Dropping all tables defined in SharedBase...")
        await conn.run_sync(SharedBase.metadata.drop_all)

        print("Dropping alembic_version table...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

    print("Database cleaned successfully.")
    await db_manager.dispose_all()


if __name__ == "__main__":
    asyncio.run(clean())
