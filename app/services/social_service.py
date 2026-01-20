from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.tenant import SocialPost, Profile, Comment, Like, Connection
from app.schemas.profile import SocialPostCreate, CommentCreate


class SocialService:
    def __init__(self, tenant_db: AsyncSession):
        self.tenant_db = tenant_db

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def create_post(self, user_id: int, data: SocialPostCreate) -> SocialPost:
        profile = await self._get_profile_by_user_id(user_id)

        new_post = SocialPost(
            profile_id=profile.id,
            content=data.content,
            media_urls=data.media_urls,
            privacy=data.privacy,
            original_post_id=data.original_post_id,
        )
        self.tenant_db.add(new_post)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_post)
        return new_post

    async def get_feed(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[SocialPost]:
        profile = await self._get_profile_by_user_id(user_id)

        # 1. Get list of friend IDs
        # This duplicates logic from ConnectionService a bit, but for efficiency in query building
        # we might want to do it here or inject ConnectionService.
        # For now, simple query.

        friends_query = select(Connection).where(
            (Connection.status == "accepted")
            & (
                (Connection.requester_id == profile.id)
                | (Connection.receiver_id == profile.id)
            )
        )
        friends_result = await self.tenant_db.execute(friends_query)
        connections = friends_result.scalars().all()

        friend_ids = []
        for conn in connections:
            fid = (
                conn.receiver_id
                if conn.requester_id == profile.id
                else conn.requester_id
            )
            friend_ids.append(fid)

        # 2. Build Query
        # Show posts from:
        # - Myself
        # - Friends (where privacy is 'public' or 'friends')
        # - (Optional: Followed users if implemented)

        query = (
            select(SocialPost)
            .where(
                (SocialPost.profile_id == profile.id)
                | (
                    (SocialPost.profile_id.in_(friend_ids))
                    & (SocialPost.privacy.in_(["public", "friends"]))
                )
            )
            .order_by(desc(SocialPost.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(SocialPost.comments), selectinload(SocialPost.likes))
        )

        result = await self.tenant_db.execute(query)
        return list(result.scalars().all())

    async def get_post(self, post_id: int) -> SocialPost:
        query = (
            select(SocialPost)
            .where(SocialPost.id == post_id)
            .options(selectinload(SocialPost.comments), selectinload(SocialPost.likes))
        )
        result = await self.tenant_db.execute(query)
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Bài viết không tồn tại")
        return post

    async def comment_post(
        self, user_id: int, post_id: int, data: CommentCreate
    ) -> Comment:
        profile = await self._get_profile_by_user_id(user_id)
        post = await self.get_post(post_id)  # Check existence

        comment = Comment(post_id=post.id, author_id=profile.id, content=data.content)
        self.tenant_db.add(comment)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(comment)
        return comment

    async def like_post(self, user_id: int, post_id: int) -> bool:
        profile = await self._get_profile_by_user_id(user_id)
        post = await self.get_post(post_id)

        # Check if already liked
        query = select(Like).where(
            (Like.post_id == post.id) & (Like.author_id == profile.id)
        )
        existing_like = (await self.tenant_db.execute(query)).scalar_one_or_none()

        if existing_like:
            # Unlike
            await self.tenant_db.delete(existing_like)
            await self.tenant_db.commit()
            return False  # Unliked
        else:
            # Like
            new_like = Like(post_id=post.id, author_id=profile.id)
            self.tenant_db.add(new_like)
            await self.tenant_db.commit()
            return True  # Liked

    async def delete_post(self, user_id: int, post_id: int):
        profile = await self._get_profile_by_user_id(user_id)
        post = await self.get_post(post_id)

        if post.profile_id != profile.id:
            raise HTTPException(
                status_code=403, detail="Không có quyền xóa bài viết này"
            )

        await self.tenant_db.delete(post)
        await self.tenant_db.commit()
