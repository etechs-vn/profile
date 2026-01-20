from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Interaction Schemas ---


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    # Optional: include author info if needed, but keeping it simple for now

    model_config = ConfigDict(from_attributes=True)


class LikeCreate(BaseModel):
    pass  # No content needed for like


class LikeResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectionCreate(BaseModel):
    receiver_id: int


class ConnectionUpdate(BaseModel):
    status: str  # "accepted", "blocked"


class ConnectionResponse(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Social Post Schemas ---


class SocialPostCreate(BaseModel):
    content: str
    media_urls: list[str] | None = None
    privacy: str = "public"
    original_post_id: int | None = None


class SocialPostResponse(BaseModel):
    id: int
    profile_id: int
    content: str
    media_urls: list[str] | None = None
    privacy: str
    original_post_id: int | None = None
    created_at: datetime
    updated_at: datetime

    comments: list[CommentResponse] = []
    likes: list[LikeResponse] = []

    # Count fields
    likes_count: int = 0
    comments_count: int = 0

    model_config = ConfigDict(from_attributes=True)
