from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.shared import UserResponse

# --- Sub-schemas ---


class StudentInfo(BaseModel):
    school: str | None = None
    class_name: str | None = Field(None, alias="class")
    major: str | None = None
    academic_year: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class TeacherInfo(BaseModel):
    work_unit: str | None = None
    subject: str | None = None
    specialty: str | None = None
    title: str | None = None


class PrivacySettings(BaseModel):
    visibility: str = "public"  # public, private, connections
    show_contact: bool = False
    allow_interaction: bool = True


# --- Main Schemas ---


class ProfileCreateBase(BaseModel):
    full_name: str
    phone: str | None = None
    address: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class ProfileBase(ProfileCreateBase):
    role: str = "unspecified"
    verification_status: str = "unverified"
    student_info: StudentInfo | None = None
    teacher_info: TeacherInfo | None = None
    privacy_settings: PrivacySettings | None = Field(
        default_factory=lambda: PrivacySettings()
    )


class ProfileCreate(ProfileCreateBase):
    user_id: int


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    privacy_settings: PrivacySettings | None = None


class StudentProfileUpdate(BaseModel):
    student_info: StudentInfo
    # Tự động cập nhật role thành student trong logic xử lý


class TeacherProfileUpdate(BaseModel):
    teacher_info: TeacherInfo
    # Tự động cập nhật role thành teacher trong logic xử lý


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Social Post Schemas ---


class SocialPostCreate(BaseModel):
    content: str
    media_urls: list[str] | None = None
    privacy: str = "public"


class SocialPostResponse(BaseModel):
    id: int
    profile_id: int
    content: str
    media_urls: list[str] | None = None
    privacy: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Combined Response ---


class TenantProfileResponse(BaseModel):
    user: UserResponse
    profile: ProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)
