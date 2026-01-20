from datetime import date
from typing import Any

from sqlalchemy import Date, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    # Định danh duy nhất cho trang cá nhân (VD: /profiles/nguyenvana)
    slug: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    phone: Mapped[str | None] = mapped_column(nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Ngày sinh
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)

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
            "dob_visibility": "friends",  # public, private, friends
            "email_visibility": "private",
            "education_visibility": "public",
            "show_contact": False,
            "allow_interaction": True,
        },
    )
