from typing import List

from fastapi import APIRouter, Path, Query

from app.api.deps import SocialServicePathDep
from app.modules.social.schemas import (
    PostCreate,
    PostResponse,
    CommentCreate,
    CommentResponse,
    GroupCreate,
    GroupResponse,
    MessageCreate,
    MessageResponse,
    PollCreate,
    PollResponse,
    PollVoteCreate,
    PollVoteResponse,
    AppointmentCreate,
    AppointmentResponse,
)

router = APIRouter()


# --- Posts ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/posts",
    response_model=PostResponse,
)
async def create_post(
    post_data: PostCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
):
    return await service.create_post(user_id, post_data)


@router.get(
    "/{tenant_id}/users/{user_id}/social/feed",
    response_model=List[PostResponse],
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
    response_model=PostResponse,
)
async def get_post_detail(
    service: SocialServicePathDep,
    post_id: str = Path(...),
):
    return await service.get_post(post_id)


@router.delete(
    "/{tenant_id}/users/{user_id}/social/posts/{post_id}",
    status_code=204,
)
async def delete_post(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: str = Path(...),
):
    await service.delete_post(user_id, post_id)


# --- Comments ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/posts/{post_id}/comments",
    response_model=CommentResponse,
)
async def create_comment(
    comment_data: CommentCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: str = Path(...),
):
    return await service.comment_post(user_id, post_id, comment_data)


@router.get(
    "/{tenant_id}/social/posts/{post_id}/comments",
    response_model=List[CommentResponse],
)
async def get_post_comments(
    service: SocialServicePathDep,
    post_id: str = Path(...),
):
    return await service.get_comments(post_id)


# --- Interactions ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/posts/{post_id}/like",
    status_code=200,
)
async def like_post(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    post_id: str = Path(...),
):
    # Just generic interact for now
    await service.interact_post(user_id, post_id, action_type="like")
    return {"message": "Liked"}


# --- Groups ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/groups",
    response_model=GroupResponse,
)
async def create_group(
    group_data: GroupCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
):
    return await service.create_group(user_id, group_data)


@router.get(
    "/{tenant_id}/users/{user_id}/social/groups",
    response_model=List[GroupResponse],
)
async def get_my_groups(
    service: SocialServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_groups(user_id)


# --- Messages ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/messages",
    response_model=MessageResponse,
)
async def send_message(
    msg_data: MessageCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
):
    return await service.send_message(user_id, msg_data)


# --- Polls ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/groups/{group_id}/polls",
    response_model=PollResponse,
)
async def create_poll(
    poll_data: PollCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    group_id: str = Path(...),
):
    return await service.create_poll(user_id, group_id, poll_data)


@router.get(
    "/{tenant_id}/social/groups/{group_id}/polls",
    response_model=List[PollResponse],
)
async def get_group_polls(
    service: SocialServicePathDep,
    group_id: str = Path(...),
):
    return await service.get_group_polls(group_id)


@router.get(
    "/{tenant_id}/social/polls/{poll_id}",
    response_model=PollResponse,
)
async def get_poll(
    service: SocialServicePathDep,
    poll_id: str = Path(...),
):
    return await service.get_poll(poll_id)


@router.post(
    "/{tenant_id}/users/{user_id}/social/polls/{poll_id}/vote",
    response_model=PollVoteResponse,
)
async def vote_poll(
    vote_data: PollVoteCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    poll_id: str = Path(...),
):
    return await service.vote_poll(user_id, poll_id, vote_data.option_id)


@router.post(
    "/{tenant_id}/users/{user_id}/social/polls/{poll_id}/close",
    response_model=PollResponse,
)
async def close_poll(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    poll_id: str = Path(...),
):
    return await service.close_poll(user_id, poll_id)


# --- Appointments ---


@router.post(
    "/{tenant_id}/users/{user_id}/social/groups/{group_id}/appointments",
    response_model=AppointmentResponse,
)
async def create_appointment(
    appt_data: AppointmentCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    group_id: str = Path(...),
):
    return await service.create_appointment(user_id, group_id, appt_data)


@router.get(
    "/{tenant_id}/social/groups/{group_id}/appointments",
    response_model=List[AppointmentResponse],
)
async def get_group_appointments(
    service: SocialServicePathDep,
    group_id: str = Path(...),
):
    return await service.get_group_appointments(group_id)


@router.get(
    "/{tenant_id}/social/appointments/{appointment_id}",
    response_model=AppointmentResponse,
)
async def get_appointment(
    service: SocialServicePathDep,
    appointment_id: str = Path(...),
):
    return await service.get_appointment(appointment_id)


@router.put(
    "/{tenant_id}/users/{user_id}/social/appointments/{appointment_id}",
    response_model=AppointmentResponse,
)
async def update_appointment(
    appt_data: AppointmentCreate,
    service: SocialServicePathDep,
    user_id: int = Path(...),
    appointment_id: str = Path(...),
):
    return await service.update_appointment(user_id, appointment_id, appt_data)


@router.delete(
    "/{tenant_id}/users/{user_id}/social/appointments/{appointment_id}",
    status_code=204,
)
async def delete_appointment(
    service: SocialServicePathDep,
    user_id: int = Path(...),
    appointment_id: str = Path(...),
):
    await service.delete_appointment(user_id, appointment_id)
