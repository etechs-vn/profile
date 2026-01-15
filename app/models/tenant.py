from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, ForeignKey

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
    
    # Quy trình 3.3.1: Trạng thái & Vai trò
    # Roles: "unspecified", "student", "teacher"
    role = Column(String, default="unspecified", nullable=False)
    # Status: "unverified", "verified", "authenticated"
    verification_status = Column(String, default="unverified", nullable=False)
    
    # Quy trình 3.5 & 3.6: Thông tin chi tiết (Lưu dạng JSON cho linh hoạt)
    # student_info: school, class_name, major, ...
    student_info = Column(JSON, nullable=True)
    # teacher_info: work_unit, subject, specialty, title, ...
    teacher_info = Column(JSON, nullable=True)
    
    # Quy trình 3.7: Quyền riêng tư
    privacy_settings = Column(JSON, default=lambda: {
        "visibility": "public",  # public, private, connections
        "show_contact": False,
        "allow_interaction": True
    })

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SocialPost(TenantBase):
    """
    Model cho trang mạng xã hội cá nhân (Quy trình 3.3.2)
    """
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, nullable=True)  # Danh sách ảnh/video
    
    # Cấu hình quyền riêng tư cho từng bài viết
    privacy = Column(String, default="public") 
    
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
