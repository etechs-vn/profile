import uuid
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.profile.models import Profile
from app.modules.social.models import (
    Post,
    Comment,
    CommentPost,
    PostInteraction,
    Group,
    Message,
    UserAction,
    Poll,
    PollOption,
    PollVote,
    Appointment,
)
from app.modules.social.schemas import (
    PostCreate,
    CommentCreate,
    GroupCreate,
    MessageCreate,
    PollCreate,
    AppointmentCreate,
)


class SocialService:
    def __init__(self, tenant_db: AsyncSession):
        self.tenant_db = tenant_db

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            # For social actions, profile MUST exist
            raise HTTPException(status_code=404, detail="Profile chưa được tạo")
        return profile

    # --- Posts ---

    async def create_post(self, user_id: int, data: PostCreate) -> Post:
        profile = await self._get_profile_by_user_id(user_id)

        post_id = str(uuid.uuid4())
        new_post = Post(
            post_id=post_id,
            content=data.content,
            file_url=data.file_url,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_post)

        # Log User Action (Ownership)
        action_id = str(uuid.uuid4())
        user_action = UserAction(
            action_id=action_id,
            profile_id=profile.profile_id,
            action_type="create_post",
            object_type="post",
            object_id=post_id,
        )
        self.tenant_db.add(user_action)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_post)
        return new_post

    async def get_post(self, post_id: str) -> Post:
        result = await self.tenant_db.execute(
            select(Post).where(Post.post_id == post_id)
        )
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Bài viết không tồn tại")
        return post

    async def delete_post(self, user_id: int, post_id: str):
        profile = await self._get_profile_by_user_id(user_id)

        # Check ownership via UserAction
        action_check = await self.tenant_db.execute(
            select(UserAction).where(
                UserAction.profile_id == profile.profile_id,
                UserAction.object_id == post_id,
                UserAction.action_type == "create_post",
            )
        )
        if not action_check.scalar_one_or_none():
            raise HTTPException(
                status_code=403, detail="Không có quyền xóa bài viết này"
            )

        post = await self.get_post(post_id)
        await self.tenant_db.delete(post)
        # Should also delete related actions/comments ideally, but Cascade might handle it if configured
        await self.tenant_db.commit()

    async def get_feed(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        # Simple feed: All posts sorted by time
        query = select(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit)
        result = await self.tenant_db.execute(query)
        return list(result.scalars().all())

    # --- Comments ---

    async def comment_post(
        self, user_id: int, post_id: str, data: CommentCreate
    ) -> Comment:
        profile = await self._get_profile_by_user_id(user_id)
        # Verify post exists
        await self.get_post(post_id)

        comment_id = str(uuid.uuid4())
        new_comment = Comment(
            comment_id=comment_id,
            content=data.content,
            file_url=data.file_url,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_comment)

        # Link Comment -> Post -> Profile
        cp_id = str(uuid.uuid4())
        link = CommentPost(
            comment_post_id=cp_id,
            post_id=post_id,
            comment_id=comment_id,
            profile_id=profile.profile_id,
        )
        self.tenant_db.add(link)

        # User Action
        ua_id = str(uuid.uuid4())
        action = UserAction(
            action_id=ua_id,
            profile_id=profile.profile_id,
            action_type="comment",
            object_type="post",
            object_id=post_id,  # Or comment_id? Usually ref the main object
        )
        self.tenant_db.add(action)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_comment)
        return new_comment

    async def get_comments(self, post_id: str) -> list[Comment]:
        # Query comments via CommentPost table
        query = (
            select(Comment)
            .join(CommentPost, Comment.comment_id == CommentPost.comment_id)
            .where(CommentPost.post_id == post_id)
            .order_by(Comment.created_at)
        )
        result = await self.tenant_db.execute(query)
        return list(result.scalars().all())

    # --- Interactions ---

    async def interact_post(
        self, user_id: int, post_id: str, action_type: str = "like"
    ) -> PostInteraction:
        profile = await self._get_profile_by_user_id(user_id)
        await self.get_post(post_id)

        # Check existing
        existing = await self.tenant_db.execute(
            select(PostInteraction).where(
                PostInteraction.post_id == post_id,
                PostInteraction.profile_id == profile.profile_id,
                PostInteraction.action == action_type,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Đã tương tác rồi")

        interaction_id = str(uuid.uuid4())
        new_interaction = PostInteraction(
            interaction_id=interaction_id,
            post_id=post_id,
            profile_id=profile.profile_id,
            action=action_type,
        )
        self.tenant_db.add(new_interaction)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_interaction)
        return new_interaction

    # --- Groups ---

    async def create_group(self, user_id: int, data: GroupCreate) -> Group:
        profile = await self._get_profile_by_user_id(user_id)

        group_id = str(uuid.uuid4())
        new_group = Group(
            group_id=group_id,
            profile_id=profile.profile_id,  # Creator
            role=True,  # Admin/Leader
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_group)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_group)
        return new_group

    async def get_groups(self, user_id: int) -> list[Group]:
        # Return groups created by user?
        # Or groups user is member of?
        # Current Group table has `profile_id` as FK.
        # Does `profile_id` mean "Member" or "Creator"?
        # Spec: "profile_id | FK -> profile.profile_id | Liên kết profile"
        # "role | boolean | 0 thành viên, 1 nhóm trưởng"
        # This implies the `groups` table IS the membership table (many-to-many relationship table with extra group info?)
        # Wait, usually Group table defines the Group entity.
        # If `groups` table has `profile_id` and `role`, and `group_id` is PK...
        # Then `group_id` identifies the MEMBERSHIP record, NOT the Group entity itself?
        # BUT `polls` has FK `group_id`. If `group_id` is unique per membership, how do we link polls to a "Group"?
        #
        # Let's re-read spec:
        # ## groups
        # group_id | PK, unique | Mã được tạo qua hệ thống
        # profile_id | FK | Liên kết profile
        # role | boolean | ...
        #
        # If I create a group, I get a row. If YOU join, you get a row?
        # Do we share `group_id`? PK must be unique.
        # So `group_id` cannot be the Group Entity ID if it's PK of this table and we have multiple members.
        # UNLESS this table IS the Group Entity and members are stored elsewhere?
        # But there is no "group_members" table in the spec.
        #
        # Critical Analysis:
        # The spec seems to conflate "Group Entity" and "Membership".
        # Or maybe `groups` table IS the membership table, and `group_id` is actually `membership_id`?
        # But `polls` links to `groups.group_id`. If I create a poll for a group, I link to... my membership? That makes no sense.
        #
        # Alternative interpretation:
        # `groups` table IS the Group Entity.
        # `profile_id` is the Creator/Owner.
        # Where are the members?
        # Maybe `user_actions`? (action_type="join_group").
        # Or `messages` (group chat).
        #
        # Let's assume `groups` table = Group Entity.
        # `profile_id` = Owner.
        # Members = People who have `user_actions` of type "join_group" linked to `group_id`.
        # This fits the "Event Sourcing / Action Log" pattern seen elsewhere.

        profile = await self._get_profile_by_user_id(user_id)

        # Get groups owned by user
        query = select(Group).where(Group.profile_id == profile.profile_id)
        result = await self.tenant_db.execute(query)
        return list(result.scalars().all())

    # --- Messages ---

    async def send_message(self, user_id: int, data: MessageCreate) -> Message:
        profile = await self._get_profile_by_user_id(user_id)

        msg_id = str(uuid.uuid4())

        # Determine scope
        scope = 0
        if data.group_id:
            scope = 1

        new_msg = Message(
            message_id=msg_id,
            msg_scope=scope,
            group_id=data.group_id,
            receiver_id=data.receiver_id,
            content=data.content,
            file_url=data.file_url,
            metadata_id=data.metadata_id,
        )

        self.tenant_db.add(new_msg)

        action_id = str(uuid.uuid4())
        action = UserAction(
            action_id=action_id,
            profile_id=profile.profile_id,
            action_type="send_message",
            object_type="message",
            object_id=msg_id,
            group_id=data.group_id,
            msg_scope=scope,
        )
        self.tenant_db.add(action)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_msg)
        return new_msg

    # --- Polls ---

    async def create_poll(self, user_id: int, group_id: str, data: PollCreate) -> Poll:
        profile = await self._get_profile_by_user_id(user_id)

        poll_id = str(uuid.uuid4())
        new_poll = Poll(
            poll_id=poll_id,
            group_id=group_id,
            profile_id=profile.profile_id,
            title=data.title,
            is_closed=False,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_poll)

        for opt in data.options:
            option_id = str(uuid.uuid4())
            new_option = PollOption(
                option_id=option_id,
                poll_id=poll_id,
                option_text=opt.option_text,
            )
            self.tenant_db.add(new_option)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_poll)
        # Fetch with options to avoid lazy loading issues
        result = await self.tenant_db.execute(
            select(Poll)
            .options(selectinload(Poll.options))
            .where(Poll.poll_id == poll_id)
        )
        return result.scalar_one()

    async def get_poll(self, poll_id: str) -> Poll:
        result = await self.tenant_db.execute(
            select(Poll)
            .options(selectinload(Poll.options))
            .where(Poll.poll_id == poll_id)
        )
        poll = result.scalar_one_or_none()
        if not poll:
            raise HTTPException(status_code=404, detail="Bình chọn không tồn tại")
        return poll

    async def get_group_polls(self, group_id: str) -> list[Poll]:
        result = await self.tenant_db.execute(
            select(Poll)
            .options(selectinload(Poll.options))
            .where(Poll.group_id == group_id)
            .order_by(Poll.created_at)
        )
        return list(result.scalars().all())

    async def vote_poll(self, user_id: int, poll_id: str, option_id: str) -> PollVote:
        poll = await self.get_poll(poll_id)
        if poll.is_closed:
            raise HTTPException(status_code=400, detail="Bình chọn đã đóng")

        poll_vote_id = str(uuid.uuid4())
        new_vote = PollVote(
            poll_vote_id=poll_vote_id,
            option_id=option_id,
        )
        self.tenant_db.add(new_vote)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_vote)
        return new_vote

    async def close_poll(self, user_id: int, poll_id: str) -> Poll:
        profile = await self._get_profile_by_user_id(user_id)

        poll = await self.get_poll(poll_id)

        if poll.profile_id != profile.profile_id:
            raise HTTPException(
                status_code=403, detail="Không có quyền đóng bình chọn này"
            )

        poll.is_closed = True
        await self.tenant_db.commit()
        await self.tenant_db.refresh(poll)
        return poll

    # --- Appointments ---

    async def create_appointment(
        self, user_id: int, group_id: str, data: AppointmentCreate
    ) -> Appointment:
        appointment_id = str(uuid.uuid4())
        new_appt = Appointment(
            appointment_id=appointment_id,
            group_id=group_id,
            title=data.title,
            start_time=data.start_time,
            end_time=data.end_time,
            note=data.note,
            remind_enabled=data.remind_enabled,
            remind_before_minutes=data.remind_before_minutes,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_appt)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_appt)
        return new_appt

    async def get_appointment(self, appointment_id: str) -> Appointment:
        result = await self.tenant_db.execute(
            select(Appointment).where(Appointment.appointment_id == appointment_id)
        )
        appt = result.scalar_one_or_none()
        if not appt:
            raise HTTPException(status_code=404, detail="Cuộc hẹn không tồn tại")
        return appt

    async def get_group_appointments(self, group_id: str) -> list[Appointment]:
        result = await self.tenant_db.execute(
            select(Appointment)
            .where(Appointment.group_id == group_id)
            .order_by(Appointment.start_time)
        )
        return list(result.scalars().all())

    async def update_appointment(
        self, user_id: int, appointment_id: str, data: AppointmentCreate
    ) -> Appointment:
        profile = await self._get_profile_by_user_id(user_id)

        appt = await self.get_appointment(appointment_id)

        if appt.group_id:
            group_result = await self.tenant_db.execute(
                select(Group).where(Group.group_id == appt.group_id)
            )
            group = group_result.scalar_one_or_none()
            if group and group.profile_id != profile.profile_id:
                raise HTTPException(
                    status_code=403, detail="Không có quyền sửa cuộc hẹn này"
                )

        appt.title = data.title
        appt.start_time = data.start_time
        appt.end_time = data.end_time
        appt.note = data.note
        appt.remind_enabled = data.remind_enabled
        appt.remind_before_minutes = data.remind_before_minutes
        appt.metadata_id = data.metadata_id

        await self.tenant_db.commit()
        await self.tenant_db.refresh(appt)
        return appt

    async def delete_appointment(self, user_id: int, appointment_id: str):
        profile = await self._get_profile_by_user_id(user_id)

        appt = await self.get_appointment(appointment_id)

        if appt.group_id:
            group_result = await self.tenant_db.execute(
                select(Group).where(Group.group_id == appt.group_id)
            )
            group = group_result.scalar_one_or_none()
            if group and group.profile_id != profile.profile_id:
                raise HTTPException(
                    status_code=403, detail="Không có quyền xóa cuộc hẹn này"
                )

        await self.tenant_db.delete(appt)
        await self.tenant_db.commit()
