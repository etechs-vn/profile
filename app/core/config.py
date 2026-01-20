from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Profile API"
    debug: bool = False

    # Postgres Configuration
    postgres_server: str | None = None
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_port: int = 5432
    postgres_db: str = "shared_db"  # Default DB name for shared

    # Shared Database
    shared_database_url: str | None = None

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Tenant Databases
    tenant_database_dir: str = "./tenants"
    tenant_database_template: str = "tenant_{tenant_id}.db"

    # Backward compatibility
    database_url: str | None = None
    database_secondary_url: str | None = None
    database_analytics_url: str | None = None
    database_urls: Dict[str, str] = {}

    def _build_postgres_url(self, db_name: str) -> str:
        """Helper to build Postgres URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{db_name}"
        )

    def get_shared_database_url(self) -> str:
        """
        Lấy URL cho shared database.
        Ưu tiên Postgres nếu cấu hình, nếu không dùng SQLite.
        """
        if self.shared_database_url:
            return self.shared_database_url

        if self.postgres_server:
            return self._build_postgres_url(self.postgres_db)

        return "sqlite+aiosqlite:///./shared.db"

    def get_tenant_database_url(self, tenant_id: str) -> str:
        """
        Tạo database URL cho tenant cụ thể.
        """
        if self.postgres_server:
            # Postgres: mỗi tenant là một database riêng (tenant_xxx)
            # Lưu ý: Database này cần được tạo trước
            return self._build_postgres_url(f"tenant_{tenant_id}")

        # SQLite: fallback
        tenant_dir = Path(self.tenant_database_dir)
        tenant_dir.mkdir(parents=True, exist_ok=True)
        db_path = (
            tenant_dir / self.tenant_database_template.format(tenant_id=tenant_id)
        ).resolve()
        return f"sqlite+aiosqlite:///{db_path}"


settings = Settings()
