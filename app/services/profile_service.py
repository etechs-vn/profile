from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.graph import GraphManager
from app.models.shared import User
from app.models.tenant import Profile
from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    StudentProfileUpdate,
    TeacherProfileUpdate,
    TenantProfileResponse,
)
from app.schemas.shared import UserResponse
from app.services.connection_service import ConnectionService


class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession | None = None):
        self.tenant_db = tenant_db
        self.shared_db = shared_db
        # We access the driver directly via singleton for now, or could inject it.
        # Ideally, we should inject it, but for simplicity in MVP:
        self.neo4j_driver = GraphManager.get_driver()

    async def _sync_to_shared_and_graph(
        self, user_id: int, full_name: str, slug: str | None, avatar_url: str | None
    ):
        """
        Synchronous sync to Shared DB and Neo4j.
        """
        # 1. Sync to Shared DB (User table)
        if self.shared_db:
            # We assume shared_db session is passed and active
            user_result = await self.shared_db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user.full_name = full_name
                if slug:
                    user.slug = slug
                if avatar_url:
                    user.avatar_url = avatar_url
                await self.shared_db.commit()  # Commit shared DB changes

        # 2. Sync to Neo4j
        async with self.neo4j_driver.session() as session:
            await session.run(
                """
                MERGE (p:Person {user_id: $user_id})
                SET p.name = $name,
                    p.slug = $slug,
                    p.avatar_url = $avatar_url,
                    p.updated_at = datetime()
                """,
                user_id=user_id,
                name=full_name,
                slug=slug,
                avatar_url=avatar_url,
            )

    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> list[Profile]:
        result = await self.tenant_db.execute(select(Profile).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_profile_by_id(self, profile_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def get_profile_by_slug(
        self, slug: str, viewer_user_id: int | None = None
    ) -> ProfileResponse:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.slug == slug)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")

        # Privacy Check Logic
        if viewer_user_id is None:
            # Guest view
            return self._apply_privacy_filter(profile, is_owner=False, is_friend=False)

        # Verify viewer has a profile
        await self._get_profile_by_user_id(viewer_user_id)

        is_owner = profile.user_id == viewer_user_id
        if is_owner:
            return ProfileResponse.model_validate(profile)

        # Check connection
        conn_service = ConnectionService(self.tenant_db)
        is_friend = await conn_service.check_friendship(profile.user_id, viewer_user_id)

        return self._apply_privacy_filter(profile, is_owner=False, is_friend=is_friend)

    def _apply_privacy_filter(
        self, profile: Profile, is_owner: bool, is_friend: bool
    ) -> ProfileResponse:
        data = ProfileResponse.model_validate(profile)
        settings = profile.privacy_settings or {}

        # Helper to check visibility
        def is_visible(setting_key, default="public"):
            visibility = settings.get(setting_key, default)
            if visibility == "public":
                return True
            if visibility == "private":
                return False  # Only owner (handled before)
            if visibility == "friends":
                return is_friend
            return False

        # Filter fields
        if not is_visible("dob_visibility", "friends"):
            data.dob = None

        if not is_visible("email_visibility", "private"):
            # Assuming email is in profile? No, it's in User model usually.
            # But if we had email in profile...
            pass

        # Note: If education_visibility is private, we might want to hide student_info/teacher_info
        if not is_visible("education_visibility", "public"):
            data.student_info = None
            data.teacher_info = None

        return data

    async def create_profile(self, data: ProfileCreate) -> Profile:
        if not self.shared_db:
            raise ValueError("Shared DB session is required for creating profile")

        result = await self.shared_db.execute(
            select(User).where(User.id == data.user_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=404, detail="User không tồn tại trong shared database"
            )

        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == data.user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Profile đã tồn tại cho user này"
            )

        # Check slug uniqueness if provided
        if data.slug:
            slug_check = await self.tenant_db.execute(
                select(Profile).where(Profile.slug == data.slug)
            )
            if slug_check.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Slug đã được sử dụng")

        new_profile = Profile(
            user_id=data.user_id,
            full_name=data.full_name,
            slug=data.slug,
            dob=data.dob,
            phone=data.phone,
            address=data.address,
            bio=data.bio,
            avatar_url=data.avatar_url,
            role="unspecified",
            verification_status="unverified",
        )
        self.tenant_db.add(new_profile)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)

        # Sync to Global
        await self._sync_to_shared_and_graph(
            user_id=data.user_id,
            full_name=data.full_name,
            slug=data.slug,
            avatar_url=data.avatar_url,
        )

        return new_profile

    async def get_profile_with_user(self, user_id: int) -> TenantProfileResponse:
        if not self.shared_db:
            raise ValueError("Shared DB session is required")

        result = await self.shared_db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User không tồn tại")

        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        from app.schemas.profile import ProfileResponse

        return TenantProfileResponse(
            user=UserResponse.model_validate(user),
            profile=ProfileResponse.model_validate(profile) if profile else None,
        )

    async def update_student_info(
        self, user_id: int, data: StudentProfileUpdate
    ) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)
        profile.role = "student"
        # Sử dụng model_dump cho Pydantic V2
        profile.student_info = data.student_info.model_dump(by_alias=True)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    async def update_teacher_info(
        self, user_id: int, data: TeacherProfileUpdate
    ) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)
        profile.role = "teacher"
        profile.teacher_info = data.teacher_info.model_dump()

        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    async def update_general_info(self, user_id: int, data: ProfileUpdate) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)

        # Check slug uniqueness if changing
        if data.slug and data.slug != profile.slug:
            slug_check = await self.tenant_db.execute(
                select(Profile).where(Profile.slug == data.slug)
            )
            if slug_check.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Slug đã được sử dụng")

        obj_data = data.model_dump(exclude_unset=True)

        for key, value in obj_data.items():
            setattr(profile, key, value)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)

        # Sync to Global
        # Need to fetch current values if not updated, or just update what changed.
        # Simple approach: pass current values from profile object
        await self._sync_to_shared_and_graph(
            user_id=user_id,
            full_name=profile.full_name,
            slug=profile.slug,
            avatar_url=profile.avatar_url,
        )

        return profile
