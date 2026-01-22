import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.profile.models import (
    Profile,
    Education,
    IdentityDocument,
    UserInterest,
)
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileUpdate,
    EducationCreate,
    IdentityDocumentCreate,
    UserInterestCreate,
)


class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession | None = None):
        self.tenant_db = tenant_db
        self.shared_db = shared_db

    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> list[Profile]:
        result = await self.tenant_db.execute(select(Profile).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_profile_by_id(self, profile_id: str) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.profile_id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile không tồn tại")
        return profile

    async def get_profile_by_user_id(self, user_id: int) -> Profile:
        # Assuming we still link via user_id, even if loosely
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=404, detail="Profile chưa được tạo cho user này"
            )
        return profile

    async def create_profile(self, user_id: int, data: ProfileCreate) -> Profile:
        # Check if profile already exists for this user
        existing = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Profile đã tồn tại")

        # Generate UUID for profile_id
        profile_id = str(uuid.uuid4())

        new_profile = Profile(
            profile_id=profile_id,
            user_id=user_id,  # Link to shared DB User
            nickname=data.nickname,
            dob=data.dob,
            gender=data.gender,
            address=data.address,
            avatar_url=data.avatar_url,
            bio=data.bio,
            metadata_id=data.metadata_id,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
        )
        self.tenant_db.add(new_profile)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)
        return new_profile

    async def update_profile(self, profile_id: str, data: ProfileUpdate) -> Profile:
        profile = await self.get_profile_by_id(profile_id)

        obj_data = data.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(profile, key, value)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    # --- Sub-resources ---

    async def add_education(self, profile_id: str, data: EducationCreate) -> Education:
        # Verify profile exists
        await self.get_profile_by_id(profile_id)

        edu_id = str(uuid.uuid4())
        new_edu = Education(
            education_id=edu_id, profile_id=profile_id, **data.model_dump()
        )
        self.tenant_db.add(new_edu)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_edu)
        return new_edu

    async def add_identity_document(
        self, profile_id: str, data: IdentityDocumentCreate
    ) -> IdentityDocument:
        await self.get_profile_by_id(profile_id)

        doc_id = str(uuid.uuid4())
        new_doc = IdentityDocument(
            identity_id=doc_id, profile_id=profile_id, **data.model_dump()
        )
        self.tenant_db.add(new_doc)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_doc)
        return new_doc

    async def add_interest(
        self, profile_id: str, data: UserInterestCreate
    ) -> UserInterest:
        await self.get_profile_by_id(profile_id)

        interest_id = str(uuid.uuid4())
        new_interest = UserInterest(
            interest_id=interest_id, profile_id=profile_id, **data.model_dump()
        )
        self.tenant_db.add(new_interest)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_interest)
        return new_interest
