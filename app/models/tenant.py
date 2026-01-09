from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import TenantBase


class Profile(TenantBase):
    """
    Model cho tenant database - Thông tin profile riêng của từng tenant.
    Mỗi tenant có database riêng chứa profile của họ.
    """
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # ID từ shared database
    full_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    bio = Column(Text)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Document(TenantBase):
    """
    Model cho tenant database - Tài liệu riêng của từng tenant.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
