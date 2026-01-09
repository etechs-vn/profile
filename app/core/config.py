from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Profile API"
    debug: bool = False
    
    # Shared Database - Database chung chứa thông tin cơ bản
    # Có thể là PostgreSQL, MySQL, hoặc SQLite
    shared_database_url: str = "sqlite+aiosqlite:///./shared.db"
    
    # Tenant Databases - Database riêng cho từng cá thể (SQLite)
    # Thư mục chứa các tenant database files
    tenant_database_dir: str = "./tenants"
    # Template cho tenant database path: {tenant_id} sẽ được thay thế
    tenant_database_template: str = "tenant_{tenant_id}.db"
    
    # Backward compatibility - giữ lại cho các code cũ
    database_url: str = "sqlite+aiosqlite:///./profile.db"  # Default database
    
    # Các database URLs bổ sung (nếu cần)
    database_secondary_url: str | None = None
    database_analytics_url: str | None = None
    
    # Hoặc sử dụng dictionary format (nếu cần)
    database_urls: Dict[str, str] = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_tenant_database_path(self, tenant_id: str) -> Path:
        """
        Tạo đường dẫn database cho tenant cụ thể.
        
        Args:
            tenant_id: ID của tenant/cá thể
            
        Returns:
            Path object đến tenant database file
        """
        tenant_dir = Path(self.tenant_database_dir)
        tenant_dir.mkdir(parents=True, exist_ok=True)
        
        db_filename = self.tenant_database_template.format(tenant_id=tenant_id)
        return tenant_dir / db_filename
    
    def get_tenant_database_url(self, tenant_id: str) -> str:
        """
        Tạo database URL cho tenant cụ thể.
        
        Args:
            tenant_id: ID của tenant/cá thể
            
        Returns:
            Database URL dạng SQLite async
        """
        db_path = self.get_tenant_database_path(tenant_id)
        # Chuyển đổi path thành URL format (absolute path)
        absolute_path = db_path.resolve()
        return f"sqlite+aiosqlite:///{absolute_path}"


settings = Settings()
