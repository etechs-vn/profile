"""
Database module - Export các thành phần chính để dễ dàng import.

Sử dụng:
    # Shared database
    from app.db import SharedBase, get_shared_db
    
    # Tenant databases
    from app.db import TenantBase, get_tenant_db, get_tenant_db_from_path, get_tenant_db_from_header
    
    # Backward compatibility
    from app.db import Base, engine, get_db, async_session, db_manager
"""

from app.db.base import Base, SharedBase, TenantBase
from app.db.database_manager import db_manager
from app.db.session import (
    async_session,
    engine,
    get_db,
    get_db_by_name,
    get_db_dependency,
    get_db_from_header,
    get_shared_db,
    get_tenant_db,
    get_tenant_db_dependency,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)

__all__ = [
    # Base classes
    "Base",          # Backward-compat alias -> SharedBase
    "SharedBase",    # Explicit shared DB base
    "TenantBase",    # Explicit tenant DB base
    # Database Manager
    "db_manager",
    # Engines (backward compatibility)
    "engine",
    "async_session",
    # Shared Database
    "get_shared_db",
    # Tenant Databases
    "get_tenant_db",
    "get_tenant_db_from_path",
    "get_tenant_db_from_query",
    "get_tenant_db_from_header",
    "get_tenant_db_dependency",
    # Backward compatibility
    "get_db",
    "get_db_by_name",
    "get_db_from_header",
    "get_db_dependency",
]
