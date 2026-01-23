import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.profile.models import (
    Profile,
    Education,
    IdentityDocument,
    UserInterest,
    Wallet,
    StudentInfo,
    TeacherInfo,
    ProfilePrivacySettings,
)
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileUpdate,
    EducationCreate,
    IdentityDocumentCreate,
    UserInterestCreate,
    ProfileProvision,
    StudentInfoCreate,
    TeacherInfoCreate,
    PrivacySettingsUpdate,
    VerificationRequest,
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

    # --- Profile Provisioning (Internal API) ---

    async def provision_profile(
        self, data: ProfileProvision
    ) -> tuple[Profile, Wallet, ProfilePrivacySettings]:
        """
        Tự động tạo Profile + Wallet + PrivacySettings cho user mới.
        Được gọi bởi Auth Service sau khi user đăng ký.
        """
        # Check if profile already exists for this user
        existing = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == data.user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Profile đã tồn tại cho user này")

        # 1. Create Profile
        profile_id = str(uuid.uuid4())
        new_profile = Profile(
            profile_id=profile_id,
            user_id=data.user_id,
            nickname=data.nickname,
            avatar_url=data.avatar_url,
            verification_status="unverified",
        )
        self.tenant_db.add(new_profile)

        # 2. Create Wallet
        wallet_id = str(uuid.uuid4())
        new_wallet = Wallet(
            wallet_id=wallet_id,
            profile_id=profile_id,
            ets=0,
        )
        self.tenant_db.add(new_wallet)

        # 3. Create default Privacy Settings
        privacy_id = str(uuid.uuid4())
        new_privacy = ProfilePrivacySettings(
            id=privacy_id,
            profile_id=profile_id,
        )
        self.tenant_db.add(new_privacy)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)
        await self.tenant_db.refresh(new_wallet)
        await self.tenant_db.refresh(new_privacy)

        return new_profile, new_wallet, new_privacy

    # --- Student/Teacher Info ---

    async def add_student_info(
        self, profile_id: str, data: StudentInfoCreate
    ) -> StudentInfo:
        """Thêm thông tin học sinh vào profile."""
        profile = await self.get_profile_by_id(profile_id)

        # Check if already has student info
        existing = await self.tenant_db.execute(
            select(StudentInfo).where(StudentInfo.profile_id == profile_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Thông tin học sinh đã tồn tại")

        student_id = str(uuid.uuid4())
        new_student = StudentInfo(
            id=student_id,
            profile_id=profile_id,
            **data.model_dump(),
        )
        self.tenant_db.add(new_student)

        # Update profile role if not set
        if not profile.role:
            profile.role = "student"

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_student)
        return new_student

    async def add_teacher_info(
        self, profile_id: str, data: TeacherInfoCreate
    ) -> TeacherInfo:
        """Thêm thông tin giáo viên vào profile."""
        profile = await self.get_profile_by_id(profile_id)

        # Check if already has teacher info
        existing = await self.tenant_db.execute(
            select(TeacherInfo).where(TeacherInfo.profile_id == profile_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Thông tin giáo viên đã tồn tại")

        teacher_id = str(uuid.uuid4())
        new_teacher = TeacherInfo(
            id=teacher_id,
            profile_id=profile_id,
            **data.model_dump(),
        )
        self.tenant_db.add(new_teacher)

        # Update profile role if not set
        if not profile.role:
            profile.role = "teacher"

        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_teacher)
        return new_teacher

    # --- Verification ---

    async def request_verification(
        self, profile_id: str, data: VerificationRequest
    ) -> Profile:
        """Yêu cầu xác minh vai trò."""
        profile = await self.get_profile_by_id(profile_id)

        # Check if already verified
        if profile.verification_status in ("verified", "certified"):
            raise HTTPException(
                status_code=400, detail="Profile đã được xác minh"
            )

        # Check if has required info based on role
        if data.role == "student":
            existing = await self.tenant_db.execute(
                select(StudentInfo).where(StudentInfo.profile_id == profile_id)
            )
            if not existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Vui lòng thêm thông tin học sinh trước khi yêu cầu xác minh",
                )
        elif data.role == "teacher":
            existing = await self.tenant_db.execute(
                select(TeacherInfo).where(TeacherInfo.profile_id == profile_id)
            )
            if not existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Vui lòng thêm thông tin giáo viên trước khi yêu cầu xác minh",
                )

        # Update status to pending
        profile.verification_status = "pending"
        profile.role = data.role

        await self.tenant_db.commit()
        await self.tenant_db.refresh(profile)
        return profile

    # --- Privacy Settings ---

    async def get_privacy_settings(self, profile_id: str) -> ProfilePrivacySettings:
        """Lấy cài đặt quyền riêng tư của profile."""
        await self.get_profile_by_id(profile_id)

        result = await self.tenant_db.execute(
            select(ProfilePrivacySettings).where(
                ProfilePrivacySettings.profile_id == profile_id
            )
        )
        settings = result.scalar_one_or_none()
        if not settings:
            # Auto create if not exists
            privacy_id = str(uuid.uuid4())
            settings = ProfilePrivacySettings(
                id=privacy_id,
                profile_id=profile_id,
            )
            self.tenant_db.add(settings)
            await self.tenant_db.commit()
            await self.tenant_db.refresh(settings)

        return settings

    async def update_privacy_settings(
        self, profile_id: str, data: PrivacySettingsUpdate
    ) -> ProfilePrivacySettings:
        """Cập nhật cài đặt quyền riêng tư."""
        settings = await self.get_privacy_settings(profile_id)

        obj_data = data.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(settings, key, value)

        await self.tenant_db.commit()
        await self.tenant_db.refresh(settings)
        return settings

