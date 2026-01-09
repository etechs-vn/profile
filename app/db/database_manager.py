from typing import Dict, Set

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings
from app.db.base import SharedBase, TenantBase


class DatabaseManager:
    """
    Quản lý database engines với kiến trúc multi-tenant:
    - Shared database: Database chung chứa thông tin cơ bản
    - Tenant databases: Database riêng cho từng cá thể (SQLite)
    """

    def __init__(self):
        self._shared_engine: AsyncEngine | None = None
        self._tenant_engines: Dict[str, AsyncEngine] = {}  # Cache tenant engines
        self._tenant_tables_created: Set[str] = set()  # Track tenants đã tạo tables
        self._other_engines: Dict[
            str, AsyncEngine
        ] = {}  # Các engines khác (backward compatibility)
        self._initialize_engines()

    def _initialize_engines(self):
        """Khởi tạo shared database engine."""
        # Khởi tạo shared database
        self._shared_engine = create_async_engine(
            settings.shared_database_url,
            echo=settings.debug,
            future=True,
        )

        # Backward compatibility - giữ lại các engines khác nếu có
        databases: Dict[str, str] = {}

        if settings.database_urls:
            databases.update(settings.database_urls)
        else:
            if (
                settings.database_url
                and settings.database_url != settings.shared_database_url
            ):
                databases["default"] = settings.database_url
            if settings.database_secondary_url:
                databases["secondary"] = settings.database_secondary_url
            if settings.database_analytics_url:
                databases["analytics"] = settings.database_analytics_url

        for name, url in databases.items():
            self._other_engines[name] = create_async_engine(
                url,
                echo=settings.debug,
                future=True,
            )

    def get_shared_engine(self) -> AsyncEngine:
        """
        Lấy shared database engine (database chung).

        Returns:
            AsyncEngine instance cho shared database
        """
        if self._shared_engine is None:
            raise RuntimeError("Shared database engine chưa được khởi tạo")
        return self._shared_engine

    def get_tenant_engine(self, tenant_id: str) -> AsyncEngine:
        """
        Lấy engine cho tenant database cụ thể.
        Tự động tạo engine nếu chưa có trong cache.

        Args:
            tenant_id: ID của tenant/cá thể

        Returns:
            AsyncEngine instance cho tenant database
        """
        if tenant_id not in self._tenant_engines:
            # Tạo engine mới cho tenant
            db_url = settings.get_tenant_database_url(tenant_id)
            self._tenant_engines[tenant_id] = create_async_engine(
                db_url,
                echo=settings.debug,
                future=True,
            )

        return self._tenant_engines[tenant_id]

    async def ensure_tenant_tables(self, tenant_id: str) -> None:
        """
        Đảm bảo tables đã được tạo cho tenant database.
        Chỉ tạo một lần cho mỗi tenant.

        Args:
            tenant_id: ID của tenant/cá thể
        """
        if tenant_id not in self._tenant_tables_created:
            engine = self.get_tenant_engine(tenant_id)
            async with engine.begin() as conn:
                # Chỉ tạo các bảng thuộc TenantBase (schema dành cho tenant databases)
                await conn.run_sync(TenantBase.metadata.create_all)
            self._tenant_tables_created.add(tenant_id)

    def get_engine(self, name: str | None = None) -> AsyncEngine:
        """
        Lấy engine theo tên database (backward compatibility).
        Nếu name là "shared", trả về shared engine.

        Args:
            name: Tên database. Nếu None, trả về shared engine.

        Returns:
            AsyncEngine instance

        Raises:
            ValueError: Nếu database name không tồn tại
        """
        if name is None or name == "shared":
            return self.get_shared_engine()

        if name not in self._other_engines:
            raise ValueError(
                f"Database '{name}' không tồn tại. "
                f"Các database có sẵn: {list(self._other_engines.keys())}"
            )

        return self._other_engines[name]

    def add_engine(self, name: str, url: str) -> AsyncEngine:
        """
        Thêm một engine mới động tại runtime (backward compatibility).

        Args:
            name: Tên database
            url: Database URL

        Returns:
            AsyncEngine instance mới được tạo
        """
        engine = create_async_engine(
            url,
            echo=settings.debug,
            future=True,
        )
        self._other_engines[name] = engine
        return engine

    def remove_tenant_engine(self, tenant_id: str) -> None:
        """
        Xóa tenant engine khỏi cache (không dispose).
        Engine sẽ được dispose khi app shutdown.

        Args:
            tenant_id: ID của tenant
        """
        if tenant_id in self._tenant_engines:
            del self._tenant_engines[tenant_id]

    async def dispose_all(self) -> None:
        """Dispose tất cả engines. Gọi khi app shutdown."""
        # Dispose shared engine
        if self._shared_engine:
            await self._shared_engine.dispose()

        # Dispose tất cả tenant engines
        for engine in self._tenant_engines.values():
            await engine.dispose()
        self._tenant_engines.clear()

        # Dispose các engines khác
        for engine in self._other_engines.values():
            await engine.dispose()
        self._other_engines.clear()

    def list_tenants(self) -> list[str]:
        """Trả về danh sách tenant IDs đã được cache."""
        return list(self._tenant_engines.keys())

    def list_databases(self) -> list[str]:
        """Trả về danh sách tên các database khác (backward compatibility)."""
        return list(self._other_engines.keys())

    @property
    def shared_engine(self) -> AsyncEngine:
        """Trả về shared engine."""
        return self.get_shared_engine()

    @property
    def default_engine(self) -> AsyncEngine:
        """Trả về shared engine (default)."""
        return self.get_shared_engine()

    @property
    def engines(self) -> Dict[str, AsyncEngine]:
        """Trả về dictionary tất cả engines (backward compatibility)."""
        result = {"shared": self._shared_engine} if self._shared_engine else {}
        result.update(self._other_engines)
        return result


# Global database manager instance
db_manager = DatabaseManager()
