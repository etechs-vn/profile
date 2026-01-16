import logging
from typing import Dict, Set

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings
from app.db.base import TenantBase

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Quản lý database engines tối giản cho kiến trúc multi-tenant.
    Hỗ trợ:
    1. SQLite (file-based)
    2. PostgreSQL (shared instance, separate DB per tenant)
    3. Isolated Database (Tenant có server riêng)
    """

    def __init__(self):
        self._shared_engine: AsyncEngine | None = None
        self._tenant_engines: Dict[str, AsyncEngine] = {}
        self._tenant_tables_created: Set[str] = set()
        self._initialize_shared_engine()

    def _initialize_shared_engine(self):
        """Khởi tạo shared database engine."""
        url = settings.get_shared_database_url()
        self._shared_engine = create_async_engine(
            url,
            echo=settings.debug,
            future=True,
        )

    def get_shared_engine(self) -> AsyncEngine:
        """Lấy shared database engine."""
        if self._shared_engine is None:
            self._initialize_shared_engine()
        return self._shared_engine

    async def _get_tenant_config(self, tenant_id: str) -> dict | None:
        """Helper để lấy thông tin cấu hình tenant từ Shared DB."""
        # Import local để tránh circular import
        from app.models.shared import Tenant

        try:
            shared_engine = self.get_shared_engine()
            async with shared_engine.connect() as conn:
                result = await conn.execute(
                    select(Tenant.db_host, Tenant.db_port, Tenant.db_name, 
                           Tenant.db_user, Tenant.db_password, Tenant.db_driver)
                    .where(Tenant.tenant_id == tenant_id)
                )
                return result.mappings().one_or_none()
        except Exception as e:
            logger.error(f"Error fetching tenant config for {tenant_id}: {e}")
            return None

    async def get_tenant_engine(self, tenant_id: str) -> AsyncEngine:
        """
        Lấy hoặc tạo mới engine cho tenant database.
        Hàm này là ASYNC vì cần query Shared DB để lấy thông tin connection của tenant.
        """
        if tenant_id in self._tenant_engines:
            return self._tenant_engines[tenant_id]

        # 1. Tra cứu thông tin Tenant trong Shared DB
        tenant_config = await self._get_tenant_config(tenant_id)

        # 2. Quyết định Connection URL
        db_url = None
        
        if tenant_config and tenant_config["db_host"]:
            # === Custom Strategy (Isolated DB) ===
            logger.info(f"Using custom database for tenant {tenant_id}")
            driver = tenant_config["db_driver"] or "postgresql+asyncpg"
            user = tenant_config["db_user"]
            password = tenant_config["db_password"]
            host = tenant_config["db_host"]
            port = tenant_config["db_port"]
            dbname = tenant_config["db_name"]
            
            db_url = f"{driver}://{user}:{password}@{host}:{port}/{dbname}"
        else:
            # === Default Strategy ===
            # SQLite hoặc Postgres trên cùng cluster
            db_url = settings.get_tenant_database_url(tenant_id)

        # 3. Tạo Engine
        self._tenant_engines[tenant_id] = create_async_engine(
            db_url,
            echo=settings.debug,
            future=True,
        )
        return self._tenant_engines[tenant_id]

    async def _provision_tenant_database_postgres(self, tenant_id: str, db_name: str | None = None, db_host: str | None = None) -> None:
        """
        Postgres only: Tạo database vật lý cho tenant nếu chưa tồn tại.
        Hỗ trợ cả Default Strategy và Custom Strategy (nếu trỏ về cùng server).
        """
        if not settings.postgres_server:
            return

        # Nếu db_host được cung cấp và khác localhost/postgres_server, ta không thể provision (assume remote).
        # Đơn giản hóa: Nếu db_host != None và không phải localhost, skip.
        if db_host and db_host not in ["localhost", "127.0.0.1", settings.postgres_server]:
            logger.info(f"Skipping provision for remote host: {db_host}")
            return
        
        target_db_name = db_name if db_name else f"tenant_{tenant_id}"
        
        maintenance_url = settings._build_postgres_url("postgres")
        temp_engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
        
        try:
            async with temp_engine.connect() as conn:
                check_query = text(f"SELECT 1 FROM pg_database WHERE datname = :dbname")
                result = await conn.execute(check_query, {"dbname": target_db_name})
                
                if not result.scalar():
                    logger.info(f"Provisioning new database for tenant: {target_db_name}")
                    await conn.execute(text(f'CREATE DATABASE "{target_db_name}"'))
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Warning during tenant DB provisioning ({target_db_name}): {e}")
        finally:
            await temp_engine.dispose()

    async def ensure_tenant_tables(self, tenant_id: str) -> None:
        """
        Đảm bảo Database và Tables đã được tạo cho tenant.
        """
        if tenant_id in self._tenant_tables_created:
            return

        # 1. Fetch config để biết tên DB
        tenant_config = await self._get_tenant_config(tenant_id)
        db_name = tenant_config["db_name"] if tenant_config else None
        db_host = tenant_config["db_host"] if tenant_config else None

        # 2. Provision Database (nếu cần)
        await self._provision_tenant_database_postgres(tenant_id, db_name=db_name, db_host=db_host)

        # 3. Connect và tạo Tables (Schema)
        # get_tenant_engine giờ là async
        engine = await self.get_tenant_engine(tenant_id) 
        
        try:
            async with engine.begin() as conn:
                await conn.run_sync(TenantBase.metadata.create_all)
            self._tenant_tables_created.add(tenant_id)
        except Exception as e:
            logger.error(f"Failed to ensure tables for tenant {tenant_id}: {e}")
            raise

    async def dispose_all(self) -> None:
        """Dispose tất cả engines khi shutdown."""
        if self._shared_engine:
            await self._shared_engine.dispose()

        for engine in self._tenant_engines.values():
            await engine.dispose()
        self._tenant_engines.clear()
        self._tenant_tables_created.clear()


# Global instance
db_manager = DatabaseManager()