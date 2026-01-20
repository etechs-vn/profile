from datetime import date, datetime, timezone
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

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Connection(TenantBase):
    """
    Model quản lý mối quan hệ giữa các Profile (Bạn bè, Follow).
    """

    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    # Status: "pending", "accepted", "blocked"
    status: Mapped[str] = mapped_column(String, default="pending")

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Đảm bảo mỗi cặp chỉ có 1 connection duy nhất
    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_connection_req_rec"),
    )


class SocialPost(TenantBase):
    """
    Model cho trang mạng xã hội cá nhân (Quy trình 3.3.2)
    """

    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    # Hỗ trợ chia sẻ bài viết (Share)
    original_post_id: Mapped[int | None] = mapped_column(
        ForeignKey("social_posts.id"), nullable=True
    )

    content: Mapped[str] = mapped_column(Text)
    media_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Cấu hình quyền riêng tư cho từng bài viết: "public", "friends", "private"
    privacy: Mapped[str] = mapped_column(default="public")

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships (Optional but helpful for query)
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(TenantBase):
    """
    Model cho bình luận bài viết.
    """

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    post = relationship("SocialPost", back_populates="comments")


class Like(TenantBase):
    """
    Model cho lượt thích bài viết.
    """

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("post_id", "author_id", name="uq_like_post_author"),
    )

    post = relationship("SocialPost", back_populates="likes")


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
