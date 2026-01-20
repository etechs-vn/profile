from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.graph import GraphManager
from app.models.tenant import Connection, Profile
from app.schemas.profile import ConnectionCreate


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

    # Override check_friendship to use Neo4j for speed?
    # Or keep using Tenant DB as it's consistent within tenant context?
    # Let's keep Tenant DB for now for safety, but Neo4j is ready.

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
            # user_id2 might be just an ID, but we need profile ID if we store profile IDs in connection
            # Wait, check_friendship usually takes profile IDs or User IDs?
            # The system uses user_id for auth, but profile_id for relations.
            # Let's assume input is user_id for convenience.

            # We need profile ID for user_id2 as well
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
