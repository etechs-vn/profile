import logging
from typing import OrderedDict, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.provisioner import TenantProvisioner
from app.db.tenant_config import TenantConfigProvider

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Quản lý database engines tập trung cho kiến trúc multi-tenant.
    Phiên bản tối ưu:
    - Separation of Concerns: ConfigProvider, Provisioner.
    - Connection Pooling Management: LRU Cache (giới hạn số lượng connection).
    """

    MAX_TENANT_CONNECTIONS = 50  # Giới hạn số lượng tenant engine giữ trong bộ nhớ

    def __init__(self) -> None:
        self._shared_engine: AsyncEngine | None = None
        self._shared_session_factory: async_sessionmaker[AsyncSession] | None = None

        # LRU Cache implementation using OrderedDict
        # Key: tenant_id, Value: AsyncEngine
        self._tenant_engines: OrderedDict[str, AsyncEngine] = OrderedDict()

        # Cache for session factories
        self._tenant_session_factories: dict[str, async_sessionmaker[AsyncSession]] = {}

        # Track provisioned tenants to avoid redundant checks
        self._tenant_tables_created: set[str] = set()

        self._initialize_shared_engine()

        # Helper components
        assert self._shared_engine is not None
        self.config_provider: TenantConfigProvider = TenantConfigProvider(
            self._shared_engine
        )
        self.provisioner: TenantProvisioner = TenantProvisioner()

    def _initialize_shared_engine(self) -> None:
        """Khởi tạo shared database engine."""
        url = settings.get_shared_database_url()
        self._shared_engine = create_async_engine(
            url,
            echo=settings.debug,
            future=True,
        )
        self._shared_session_factory = async_sessionmaker(
            self._shared_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    def get_shared_engine(self) -> AsyncEngine:
        if self._shared_engine is None:
            self._initialize_shared_engine()
        assert self._shared_engine is not None
        return self._shared_engine

    def get_shared_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._shared_session_factory is None:
            self._initialize_shared_engine()
        assert self._shared_session_factory is not None
        return self._shared_session_factory

    async def get_tenant_engine(self, tenant_id: str) -> AsyncEngine:
        """
        Lấy engine cho tenant. Implement LRU Cache để tránh leak connection.
        """
        # 1. Cache Hit
        if tenant_id in self._tenant_engines:
            # Move to end to mark as recently used
            self._tenant_engines.move_to_end(tenant_id)
            return self._tenant_engines[tenant_id]

        # 2. Cache Miss - Create new engine
        # Before creating, check limit and evict if necessary
        if len(self._tenant_engines) >= self.MAX_TENANT_CONNECTIONS:
            await self._evict_oldest_connection()

        # Fetch config
        tenant_config = await self.config_provider.get_config(tenant_id)

        # Determine URL
        db_url = self._build_tenant_db_url(tenant_id, tenant_config)

        # Create Engine
        engine = create_async_engine(
            db_url,
            echo=settings.debug,
            future=True,
        )

        # Cache it
        self._tenant_engines[tenant_id] = engine
        return engine

    async def _evict_oldest_connection(self) -> None:
        """Đóng kết nối tenant lâu không dùng nhất."""
        try:
            oldest_tenant, engine = self._tenant_engines.popitem(last=False)
            logger.info(f"Evicting idle connection for tenant: {oldest_tenant}")

            # Clean up related objects
            if oldest_tenant in self._tenant_session_factories:
                del self._tenant_session_factories[oldest_tenant]

            # Close connection
            await engine.dispose()
        except Exception as e:
            logger.error(f"Error evicting connection: {e}")

    def _build_tenant_db_url(self, tenant_id: str, config: Any | None) -> str:
        """Logic quyết định connection string."""
        if config and config.get("db_host"):
            # Custom Strategy
            logger.info(f"Using custom database for tenant {tenant_id}")
            driver = config.get("db_driver") or "postgresql+asyncpg"
            user = config.get("db_user")
            password = config.get("db_password")
            host = config.get("db_host")
            port = config.get("db_port")
            dbname = config.get("db_name")
            return f"{driver}://{user}:{password}@{host}:{port}/{dbname}"

        # Default Strategy
        return settings.get_tenant_database_url(tenant_id)

    async def get_tenant_session_factory(
        self, tenant_id: str
    ) -> async_sessionmaker[AsyncSession]:
        """Lấy session factory, lazy create nếu chưa có."""
        if tenant_id not in self._tenant_session_factories:
            engine = await self.get_tenant_engine(tenant_id)
            self._tenant_session_factories[tenant_id] = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._tenant_session_factories[tenant_id]

    async def ensure_tenant_tables(self, tenant_id: str) -> None:
        """
        Đảm bảo Database và Schema tồn tại.
        """
        if tenant_id in self._tenant_tables_created:
            return

        # 1. Fetch config để biết tên DB/Host (cho provisioner)
        tenant_config = await self.config_provider.get_config(tenant_id)
        db_name = tenant_config.get("db_name") if tenant_config else None
        db_host = tenant_config.get("db_host") if tenant_config else None

        # 2. Provision Database (Create DB physically if Postgres)
        await self.provisioner.provision_database(tenant_id, db_name, db_host)

        # 3. Create Schema (Tables)
        engine = await self.get_tenant_engine(tenant_id)
        await self.provisioner.ensure_schema(engine)

        self._tenant_tables_created.add(tenant_id)

    async def dispose_all(self) -> None:
        """Dispose tất cả engines khi shutdown."""
        logger.info("Disposing all database connections...")
        if self._shared_engine:
            await self._shared_engine.dispose()

        # Copy values to list to avoid runtime error during iteration
        for engine in list(self._tenant_engines.values()):
            await engine.dispose()

        self._tenant_engines.clear()
        self._tenant_session_factories.clear()
        self._tenant_tables_created.clear()


# Global instance
db_manager = DatabaseManager()
