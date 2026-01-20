from datetime import datetime, timezone
from typing import Any

from sqlalchemy import ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TenantBase


class Profile(TenantBase):
    """
    Model cho tenant database - Thông tin profile riêng của từng tenant.
    Mỗi tenant có database riêng chứa profile của họ.
    """

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        index=True
    )  # ID từ shared database. nullable=False by default for Mapped[int]
    full_name: Mapped[str]
    phone: Mapped[str | None] = mapped_column(nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    # Quy trình 3.3.1: Trạng thái & Vai trò
    # Roles: "unspecified", "student", "teacher"
    role: Mapped[str] = mapped_column(default="unspecified")
    # Status: "unverified", "verified", "authenticated"
    verification_status: Mapped[str] = mapped_column(default="unverified")

    # Quy trình 3.5 & 3.6: Thông tin chi tiết (Lưu dạng JSON cho linh hoạt)
    # student_info: school, class_name, major, ...
    student_info: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    # teacher_info: work_unit, subject, specialty, title, ...
    teacher_info: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Quy trình 3.7: Quyền riêng tư
    privacy_settings: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        default=lambda: {
            "visibility": "public",  # public, private, connections
            "show_contact": False,
            "allow_interaction": True,
        },
    )

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SocialPost(TenantBase):
    """
    Model cho trang mạng xã hội cá nhân (Quy trình 3.3.2)
    """

    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    content: Mapped[str] = mapped_column(Text)
    media_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Cấu hình quyền riêng tư cho từng bài viết
    privacy: Mapped[str] = mapped_column(default="public")

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Document(TenantBase):
    """
    Model cho tenant database - Tài liệu riêng của từng tenant.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
