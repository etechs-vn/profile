from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import SharedBase


class User(SharedBase):
    """
    Model cho shared database - Thông tin người dùng chung.
    Lưu trong shared database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tenant(SharedBase):
    """
    Model cho shared database - Thông tin tenant/cá thể.
    Lưu trong shared database để quản lý các tenant.
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    
    # Database Connection Info (Cho phép Tenant nằm ở server khác)
    # Nếu db_host là NULL -> Dùng Default Strategy (config.py)
    db_host = Column(String, nullable=True)
    db_port = Column(Integer, nullable=True)
    db_name = Column(String, nullable=True)
    db_user = Column(String, nullable=True)
    db_password = Column(String, nullable=True)
    db_driver = Column(String, default="postgresql+asyncpg")  # hoặc sqlite+aiosqlite
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)