from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Shared Base ---
class SocialBaseResponse(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Post Schemas ---
class PostCreate(BaseModel):
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None


class PostResponse(SocialBaseResponse):
    post_id: str
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None

    # We might inject author info manually in the service layer if needed
    # author_profile_id: str | None = None


# --- Comment Schemas ---
class CommentCreate(BaseModel):
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None


class CommentResponse(SocialBaseResponse):
    comment_id: str
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None


# --- Group Schemas ---
class GroupCreate(BaseModel):
    metadata_id: str | None = None
    # Usually groups have a name, but the spec only has metadata_id.
    # Maybe name is in metadata? Or we use 'metadata_id' as a pointer.
    # We'll follow the spec strictly.


class GroupResponse(SocialBaseResponse):
    group_id: str
    profile_id: str  # Creator/Admin
    role: bool | None = None
    joined_at: datetime | None = None
    metadata_id: str | None = None


# --- Message Schemas ---
class MessageCreate(BaseModel):
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None
    # For group msg:
    group_id: str | None = None
    # For private msg:
    receiver_id: str | None = None


class MessageResponse(SocialBaseResponse):
    message_id: str
    msg_scope: int  # 0 or 1
    group_id: str | None = None
    receiver_id: str | None = None
    content: str | None = None
    file_url: str | None = None
    metadata_id: str | None = None


# --- Poll Schemas ---
class PollOptionCreate(BaseModel):
    option_text: str


class PollOptionResponse(BaseModel):
    option_id: str
    poll_id: str
    option_text: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PollVoteCreate(BaseModel):
    option_id: str


class PollVoteResponse(BaseModel):
    poll_vote_id: str
    option_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PollCreate(BaseModel):
    title: str | None = None
    metadata_id: str | None = None
    options: list[PollOptionCreate] = []


class PollResponse(SocialBaseResponse):
    poll_id: str
    group_id: str
    profile_id: str
    title: str | None = None
    is_closed: bool | None = None
    metadata_id: str | None = None
    options: list[PollOptionResponse] = []


# --- Appointment Schemas ---
class AppointmentCreate(BaseModel):
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    note: str | None = None
    remind_enabled: bool | None = None
    remind_before_minutes: int | None = None
    metadata_id: str | None = None


class AppointmentResponse(SocialBaseResponse):
    appointment_id: str
    group_id: str
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    note: str | None = None
    remind_enabled: bool | None = None
    remind_before_minutes: int | None = None
    metadata_id: str | None = None
