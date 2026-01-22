from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TenantBase

if TYPE_CHECKING:
    from app.modules.profile.models import Profile


class Post(TenantBase):
    """
    Bảng bài đăng (posts).
    Lưu ý: Theo đặc tả, bảng này KHÔNG có foreign key liên kết trực tiếp với profile.
    Quan hệ nằm ở bảng trung gian comment_post hoặc post_interactions (cho like/share).
    """

    __tablename__ = "posts"

    post_id: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    comments_association: Mapped[list["CommentPost"]] = relationship(
        back_populates="post"
    )
    interactions: Mapped[list["PostInteraction"]] = relationship(back_populates="post")


class Comment(TenantBase):
    """
    Bảng bình luận (comments).
    Lưu ý: Theo đặc tả, bảng này KHÔNG có foreign key liên kết trực tiếp với post hay profile.
    Quan hệ nằm ở bảng trung gian comment_post.
    """

    __tablename__ = "comments"

    comment_id: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    post_association: Mapped[list["CommentPost"]] = relationship(
        back_populates="comment"
    )
    interactions: Mapped[list["CommentInteraction"]] = relationship(
        back_populates="comment"
    )


class CommentPost(TenantBase):
    """
    Bảng liên kết bình luận và bài viết (comment_post).
    Đây là nơi liên kết Post - Comment - Profile.
    """

    __tablename__ = "comment_post"

    comment_post_id: Mapped[str] = mapped_column(String, primary_key=True)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.post_id"))
    comment_id: Mapped[str] = mapped_column(ForeignKey("comments.comment_id"))
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))

    post: Mapped["Post"] = relationship(back_populates="comments_association")
    comment: Mapped["Comment"] = relationship(back_populates="post_association")
    profile: Mapped["Profile"] = relationship()


class PostInteraction(TenantBase):
    """
    Bảng tương tác bài viết (post_interactions).
    """

    __tablename__ = "post_interactions"

    interaction_id: Mapped[str] = mapped_column(String, primary_key=True)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.post_id"))
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))
    action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    post: Mapped["Post"] = relationship(back_populates="interactions")
    profile: Mapped["Profile"] = relationship()


class CommentInteraction(TenantBase):
    """
    Bảng tương tác bình luận (comment_interactions).
    """

    __tablename__ = "comment_interactions"

    interaction_id: Mapped[str] = mapped_column(String, primary_key=True)
    comment_id: Mapped[str] = mapped_column(ForeignKey("comments.comment_id"))
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))
    action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    comment: Mapped["Comment"] = relationship(back_populates="interactions")
    profile: Mapped["Profile"] = relationship()


class Group(TenantBase):
    """
    Bảng nhóm (groups).
    """

    __tablename__ = "groups"

    group_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))
    role: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="groups")
    polls: Mapped[list["Poll"]] = relationship(back_populates="group")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="group")


class Message(TenantBase):
    """
    Bảng tin nhắn (messages).
    """

    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    msg_scope: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    group_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("groups.group_id"), nullable=True
    )
    receiver_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("profile.profile_id"), nullable=True
    )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    group: Mapped[Optional["Group"]] = relationship()
    receiver: Mapped[Optional["Profile"]] = relationship()

    __table_args__ = (CheckConstraint("msg_scope IN (0, 1)", name="check_msg_scope"),)


class UserAction(TenantBase):
    """
    Bảng hành động người dùng (user_actions).
    """

    __tablename__ = "user_actions"

    action_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))
    action_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    object_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    object_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    group_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    msg_scope: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="user_actions")

    __table_args__ = (
        CheckConstraint("msg_scope IN (0, 1)", name="check_action_msg_scope"),
    )


class Poll(TenantBase):
    """
    Bảng bình chọn (polls).
    """

    __tablename__ = "polls"

    poll_id: Mapped[str] = mapped_column(String, primary_key=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.group_id"))
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_closed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    group: Mapped["Group"] = relationship(back_populates="polls")
    profile: Mapped["Profile"] = relationship()
    options: Mapped[list["PollOption"]] = relationship(back_populates="poll")


class PollOption(TenantBase):
    """
    Bảng tùy chọn bình chọn (poll_options).
    """

    __tablename__ = "poll_options"

    option_id: Mapped[str] = mapped_column(String, primary_key=True)
    poll_id: Mapped[str] = mapped_column(ForeignKey("polls.poll_id"))
    option_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    poll: Mapped["Poll"] = relationship(back_populates="options")
    votes: Mapped[list["PollVote"]] = relationship(back_populates="option")


class PollVote(TenantBase):
    """
    Bảng phiếu bầu bình chọn (poll_votes).
    """

    __tablename__ = "poll_votes"

    poll_vote_id: Mapped[str] = mapped_column(String, primary_key=True)
    option_id: Mapped[str] = mapped_column(ForeignKey("poll_options.option_id"))

    option: Mapped["PollOption"] = relationship(back_populates="votes")


class Appointment(TenantBase):
    """
    Bảng cuộc hẹn/nhắc hẹn (appointments).
    """

    __tablename__ = "appointments"

    appointment_id: Mapped[str] = mapped_column(String, primary_key=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.group_id"))
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remind_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    remind_before_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    group: Mapped["Group"] = relationship(back_populates="appointments")
