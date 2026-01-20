from sqlalchemy import ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TenantBase


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

    post = relationship("SocialPost", back_populates="comments")


class Like(TenantBase):
    """
    Model cho lượt thích bài viết.
    """

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    __table_args__ = (
        UniqueConstraint("post_id", "author_id", name="uq_like_post_author"),
    )

    post = relationship("SocialPost", back_populates="likes")
