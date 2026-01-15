"""
Database module - Export các thành phần chính.

Sử dụng:
    # Shared database
    from app.db import SharedBase, get_shared_db
    
    # Tenant databases
    from app.db import TenantBase, get_tenant_db_from_path, get_tenant_db_from_header
"""

from app.db.base import Base, SharedBase, TenantBase
from app.db.database_manager import db_manager
from app.db.session import (
    get_shared_db,
    get_tenant_db_dependency,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)

__all__ = [
    # Base classes
    "Base",          # Alias -> SharedBase
    "SharedBase",    
    "TenantBase",    
    
    # Database Manager
    "db_manager",
    
    # Shared Database
    "get_shared_db",
    
    # Tenant Databases
    "get_tenant_db_from_path",
    "get_tenant_db_from_query",
    "get_tenant_db_from_header",
    "get_tenant_db_dependency",
]