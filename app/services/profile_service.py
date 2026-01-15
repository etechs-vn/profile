from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.shared import User
from app.models.tenant import Profile, SocialPost
from app.schemas.profile import (
    ProfileCreate, ProfileUpdate, StudentProfileUpdate, 
    TeacherProfileUpdate, SocialPostCreate, TenantProfileResponse
)

class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession = None):
        self.tenant_db = tenant_db
        self.shared_db = shared_db

    async def get_all_profiles(self) -> list[Profile]:
        result = await self.tenant_db.execute(select(Profile))
        return result.scalars().all()

    async def get_profile_by_id(self, profile_id: int) -> Profile:
        result = await self.tenant_db.execute(select(Profile).where(Profile.id == profile_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def create_profile(self, data: ProfileCreate) -> Profile:
        if not self.shared_db:
            raise ValueError("Shared DB session is required for creating profile")

        result = await self.shared_db.execute(select(User).where(User.id == data.user_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="User không tồn tại trong shared database")

        result = await self.tenant_db.execute(select(Profile).where(Profile.user_id == data.user_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Profile đã tồn tại cho user này")

        new_profile = Profile(
            user_id=data.user_id,
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
            bio=data.bio,
            avatar_url=data.avatar_url,
            role="unspecified",
            verification_status="unverified"
        )
        self.tenant_db.add(new_profile)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)
        return new_profile

    async def get_profile_with_user(self, user_id: int) -> TenantProfileResponse:
        if not self.shared_db:
            raise ValueError("Shared DB session is required")
            
        result = await self.shared_db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User không tồn tại")

        result = await self.tenant_db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = result.scalar_one_or_none()

        return TenantProfileResponse(
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
            },
            profile=profile,
        )

    async def update_student_info(self, user_id: int, data: StudentProfileUpdate) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)
        profile.role = "student"
        # Sử dụng model_dump cho Pydantic V2
        profile.student_info = data.student_info.model_dump(by_alias=True)
        
        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    async def update_teacher_info(self, user_id: int, data: TeacherProfileUpdate) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)
        profile.role = "teacher"
        profile.teacher_info = data.teacher_info.model_dump()
        
        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    async def update_general_info(self, user_id: int, data: ProfileUpdate) -> Profile:
        profile = await self._get_profile_by_user_id(user_id)
        
        obj_data = data.model_dump(exclude_unset=True)
        if "privacy_settings" in obj_data and obj_data["privacy_settings"]:
            obj_data["privacy_settings"] = data.privacy_settings.model_dump()

        for key, value in obj_data.items():
            setattr(profile, key, value)
        
        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    async def create_social_post(self, user_id: int, data: SocialPostCreate) -> SocialPost:
        profile = await self._get_profile_by_user_id(user_id)
        
        new_post = SocialPost(
            profile_id=profile.id,
            content=data.content,
            media_urls=data.media_urls,
            privacy=data.privacy
        )
        self.tenant_db.add(new_post)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_post)
        return new_post

    async def get_social_posts(self, user_id: int):
        profile = await self._get_profile_by_user_id(user_id)
        result = await self.tenant_db.execute(
            select(SocialPost).where(SocialPost.profile_id == profile.id).order_by(SocialPost.created_at.desc())
        )
        return result.scalars().all()