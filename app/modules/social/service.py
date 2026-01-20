from sqlalchemy import select, desc, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.graph import GraphManager
from app.modules.profile.models import (
    Profile,
)  # Temporary dependency until Profile module is moved
from app.modules.social.models import SocialPost, Comment, Like, Connection
from app.modules.social.schemas import SocialPostCreate, CommentCreate, ConnectionCreate


class ConnectionService:
    def __init__(self, tenant_db: AsyncSession):
        self.tenant_db = tenant_db
        self.neo4j_driver = GraphManager.get_driver()

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def send_request(
        self, requester_user_id: int, data: ConnectionCreate
    ) -> Connection:
        requester = await self._get_profile_by_user_id(requester_user_id)
        receiver = await self.tenant_db.get(Profile, data.receiver_id)

        if not receiver:
            raise HTTPException(status_code=404, detail="Người nhận không tồn tại")

        if requester.id == receiver.id:
            raise HTTPException(
                status_code=400, detail="Không thể kết bạn với chính mình"
            )

        # Check existing connection in Tenant DB
        existing = await self.tenant_db.execute(
            select(Connection).where(
                or_(
                    and_(
                        Connection.requester_id == requester.id,
                        Connection.receiver_id == receiver.id,
                    ),
                    and_(
                        Connection.requester_id == receiver.id,
                        Connection.receiver_id == requester.id,
                    ),
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Mối quan hệ đã tồn tại hoặc đang chờ"
            )

        # Create Pending Connection in Tenant DB
        new_connection = Connection(
            requester_id=requester.id, receiver_id=receiver.id, status="pending"
        )
        self.tenant_db.add(new_connection)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_connection)

        # Sync to Neo4j (Relationship: FRIEND_REQUEST)
        async with self.neo4j_driver.session() as session:
            await session.run(
                """
                MATCH (p1:Person {user_id: $uid1})
                MATCH (p2:Person {user_id: $uid2})
                MERGE (p1)-[r:FRIEND_REQUEST {created_at: datetime()}]->(p2)
                """,
                uid1=requester.user_id,
                uid2=receiver.user_id,
            )

        return new_connection

    async def respond_to_request(
        self, receiver_user_id: int, connection_id: int, status: str
    ) -> Connection:
        if status not in ["accepted", "blocked"]:
            raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")

        receiver = await self._get_profile_by_user_id(receiver_user_id)
        connection = await self.tenant_db.get(Connection, connection_id)

        if not connection:
            raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")

        if connection.receiver_id != receiver.id:
            raise HTTPException(
                status_code=403, detail="Không có quyền xử lý yêu cầu này"
            )

        connection.status = status
        await self.tenant_db.commit()
        await self.tenant_db.refresh(connection)

        # Sync to Neo4j
        requester_profile = await self.tenant_db.get(Profile, connection.requester_id)
        if requester_profile:  # Should always exist
            async with self.neo4j_driver.session() as session:
                if status == "accepted":
                    # Remove REQUEST, Add FRIEND
                    await session.run(
                        """
                        MATCH (p1:Person {user_id: $uid1})-[r:FRIEND_REQUEST]-(p2:Person {user_id: $uid2})
                        DELETE r
                        MERGE (p1)-[:FRIEND {created_at: datetime()}]->(p2)
                        """,
                        uid1=requester_profile.user_id,
                        uid2=receiver.user_id,
                    )
                elif status == "blocked":
                    # Maybe add BLOCKED relationship? For now just remove request.
                    await session.run(
                        """
                        MATCH (p1:Person {user_id: $uid1})-[r:FRIEND_REQUEST]-(p2:Person {user_id: $uid2})
                        DELETE r
                        """,
                        uid1=requester_profile.user_id,
                        uid2=receiver.user_id,
                    )

        return connection

    async def get_connections(
        self, user_id: int, status: str = "accepted"
    ) -> list[Profile]:
        profile = await self._get_profile_by_user_id(user_id)

        # Get connections where user is either requester or receiver and status matches
        query = select(Connection).where(
            and_(
                or_(
                    Connection.requester_id == profile.id,
                    Connection.receiver_id == profile.id,
                ),
                Connection.status == status,
            )
        )
        result = await self.tenant_db.execute(query)
        connections = result.scalars().all()

        friend_ids = []
        for conn in connections:
            if conn.requester_id == profile.id:
                friend_ids.append(conn.receiver_id)
            else:
                friend_ids.append(conn.requester_id)

        if not friend_ids:
            return []

        # Get profiles of friends
        friends_result = await self.tenant_db.execute(
            select(Profile).where(Profile.id.in_(friend_ids))
        )
        return list(friends_result.scalars().all())

    async def check_friendship(self, user_id1: int, user_id2: int) -> bool:
        """Helper for privacy checks"""
        try:
            p1 = await self._get_profile_by_user_id(user_id1)
            result = await self.tenant_db.execute(
                select(Profile).where(Profile.user_id == user_id2)
            )
            p2 = result.scalar_one_or_none()
            if not p2:
                return False

            query = select(Connection).where(
                and_(
                    or_(
                        and_(
                            Connection.requester_id == p1.id,
                            Connection.receiver_id == p2.id,
                        ),
                        and_(
                            Connection.requester_id == p2.id,
                            Connection.receiver_id == p1.id,
                        ),
                    ),
                    Connection.status == "accepted",
                )
            )
            res = await self.tenant_db.execute(query)
            return res.scalar_one_or_none() is not None

        except HTTPException:
            return False


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
