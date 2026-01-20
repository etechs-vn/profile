import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.core.config import settings
from app.db.base import TenantBase

# IMPORTANT: Import tenant models to ensure they are registered in metadata
# This fixes the bug where tables were not created because models weren't loaded
import app.models.tenant  # noqa: F401

logger = logging.getLogger(__name__)


class TenantProvisioner:
    """
    Chịu trách nhiệm khởi tạo Database (Postgres) và Tables (Schema).
    """

    async def provision_database(
        self, tenant_id: str, db_name: str | None, db_host: str | None
    ) -> None:
        """
        Tạo database vật lý trên Postgres server nếu cần thiết.
        """
        if not settings.postgres_server:
            # Nếu không dùng Postgres (ví dụ chạy SQLite), skip bước tạo DB vật lý
            return

        # Check host policy
        if db_host and db_host not in [
            "localhost",
            "127.0.0.1",
            settings.postgres_server,
        ]:
            logger.info(f"Skipping provision for remote host: {db_host}")
            return

        target_db_name = db_name if db_name else f"tenant_{tenant_id}"

        # Kết nối tới database 'postgres' (maintenance DB) để chạy lệnh CREATE DATABASE
        maintenance_url = settings._build_postgres_url("postgres")
        temp_engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")

        try:
            async with temp_engine.connect() as conn:
                check_query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
                result = await conn.execute(check_query, {"dbname": target_db_name})

                if not result.scalar():
                    logger.info(
                        f"Provisioning new database for tenant: {target_db_name}"
                    )
                    # Postgres không cho phép bind params trong lệnh CREATE DATABASE
                    # Cần sanitize db_name cẩn thận, nhưng ở đây ta tin tưởng system generated name
                    await conn.execute(text(f'CREATE DATABASE "{target_db_name}"'))
        except (OperationalError, ProgrammingError) as e:
            logger.warning(
                f"Warning during tenant DB provisioning ({target_db_name}): {e}"
            )
        finally:
            await temp_engine.dispose()

    async def ensure_schema(self, engine: AsyncEngine) -> None:
        """
        Đảm bảo các bảng (tables) đã được tạo trong tenant database.
        """
        try:
            async with engine.begin() as conn:
                await conn.run_sync(TenantBase.metadata.create_all)
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            raise
