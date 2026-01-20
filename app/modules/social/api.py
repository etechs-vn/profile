from typing import List

from fastapi import APIRouter, Path, Query

from app.api.deps import SocialServicePathDep, ConnectionServicePathDep
from app.modules.social.schemas import (
    SocialPostCreate,
    SocialPostResponse,
    CommentCreate,
    CommentResponse,
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
)
from app.modules.social.schemas import (
    SocialPostResponse as ProfileResponse,
)  # Wait, get_connections returns ProfileResponse?

# Check logic: get_connections returns List[ProfileResponse].
# But ProfileResponse is in Profile module.
# So we need to import ProfileResponse from Profile Schemas (or Shared if moved).
# Currently ProfileResponse is in app.modules.profile.schemas.

from app.modules.profile.schemas import ProfileResponse

router = APIRouter()


# --- Social Posts Endpoints ---


@router.post(
    "/{tenant_id}/social/user/{user_id}/posts", response_model=SocialPostResponse
)
async def create_post(
    post_data: SocialPostCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
):
    return await service.create_post(user_id, post_data)


@router.get(
    "/{tenant_id}/social/user/{user_id}/feed",
    response_model=List[SocialPostResponse],
)
async def get_feed(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await service.get_feed(user_id, skip=skip, limit=limit)


@router.get(
    "/{tenant_id}/social/posts/{post_id}",
    response_model=SocialPostResponse,
)
async def get_post_detail(
    service: SocialServicePathDep,
    post_id: int = Path(...),
):
    return await service.get_post(post_id)


@router.post(
    "/{tenant_id}/social/user/{user_id}/posts/{post_id}/comments",
    response_model=CommentResponse,
)
async def create_comment(
    comment_data: CommentCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: int = Path(...),
):
    return await service.comment_post(user_id, post_id, comment_data)


@router.post(
    "/{tenant_id}/social/user/{user_id}/posts/{post_id}/likes",
    response_model=bool,
)
async def toggle_like(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: int = Path(...),
):
    """Returns True if liked, False if unliked"""
    return await service.like_post(user_id, post_id)


@router.delete(
    "/{tenant_id}/social/user/{user_id}/posts/{post_id}",
    status_code=204,
)
async def delete_post(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: int = Path(...),
):
    await service.delete_post(user_id, post_id)


# --- Connection Endpoints ---


@router.post(
    "/{tenant_id}/profiles/user/{user_id}/connections",
    response_model=ConnectionResponse,
)
async def send_connection_request(
    connection_data: ConnectionCreate,
    service: ConnectionServicePathDep,
    user_id: int = Path(...),
):
    return await service.send_request(user_id, connection_data)


@router.put(
    "/{tenant_id}/profiles/user/{user_id}/connections/{connection_id}",
    response_model=ConnectionResponse,
)
async def respond_connection_request(
    update_data: ConnectionUpdate,
    service: ConnectionServicePathDep,
    user_id: int = Path(...),
    connection_id: int = Path(...),
):
    return await service.respond_to_request(user_id, connection_id, update_data.status)


@router.get(
    "/{tenant_id}/profiles/user/{user_id}/connections",
    response_model=List[ProfileResponse],
)
async def get_connections(
    service: ConnectionServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_connections(user_id)
