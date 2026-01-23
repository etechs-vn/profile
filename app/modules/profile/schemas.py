from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# --- Education Schemas ---
class EducationBase(BaseModel):
    education_level: str | None = None
    institution_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool | None = None
    credential_type: str | None = None
    credential_title: str | None = None
    issuing_organization: str | None = None
    credential_ref: str | None = None
    metadata_id: str | None = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    education_id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Identity Document Schemas ---
class IdentityDocumentBase(BaseModel):
    document_type: str | None = None
    document_number: str | None = None
    issued_date: datetime | None = None
    expiry_date: datetime | None = None
    metadata_id: str | None = None


class IdentityDocumentCreate(IdentityDocumentBase):
    pass


class IdentityDocumentResponse(IdentityDocumentBase):
    identity_id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- User Interest Schemas ---
class UserInterestBase(BaseModel):
    interest_text: str | None = None
    normalized_text: str | None = None
    metadata_id: str | None = None


class UserInterestCreate(UserInterestBase):
    pass


class UserInterestResponse(UserInterestBase):
    interest_id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Profile Schemas ---
class ProfileBase(BaseModel):
    nickname: str | None = None
    dob: date | None = None
    gender: bool | None = None  # True: Male, False: Female
    address: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    metadata_id: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    dob: date | None = None
    gender: bool | None = None
    address: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    metadata_id: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class ProfileResponse(ProfileBase):
    profile_id: str
    verification_status: str = "unverified"
    role: str | None = None
    created_at: datetime
    updated_at: datetime

    # Optional: Include related data
    educations: list[EducationResponse] = []
    identity_documents: list[IdentityDocumentResponse] = []
    user_interests: list[UserInterestResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Profile Provisioning Schemas (Internal API) ---
class ProfileProvision(BaseModel):
    """Internal API - Auth Service gọi để provision profile."""

    user_id: int
    nickname: str | None = None
    avatar_url: str | None = None


class ProfileProvisionResponse(BaseModel):
    profile_id: str
    wallet_id: str
    verification_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Student Info Schemas ---
class StudentInfoBase(BaseModel):
    school_name: str
    grade: str | None = None
    school_year: str | None = None
    major: str | None = None
    metadata_id: str | None = None


class StudentInfoCreate(StudentInfoBase):
    pass


class StudentInfoResponse(StudentInfoBase):
    id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Teacher Info Schemas ---
class TeacherInfoBase(BaseModel):
    institution_name: str
    subject: str | None = None
    title: str | None = None
    metadata_id: str | None = None


class TeacherInfoCreate(TeacherInfoBase):
    pass


class TeacherInfoResponse(TeacherInfoBase):
    id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Verification Schemas ---
class VerificationRequest(BaseModel):
    role: Literal["student", "teacher"]


class VerificationResponse(BaseModel):
    profile_id: str
    verification_status: str
    role: str
    message: str

    model_config = ConfigDict(from_attributes=True)


# --- Privacy Settings Schemas ---
class PrivacySettingsBase(BaseModel):
    profile_visibility: Literal["public", "friends", "private"] = "public"
    posts_visibility: Literal["public", "friends", "private"] = "public"
    education_visibility: Literal["public", "friends", "private"] = "friends"
    contact_visibility: Literal["public", "friends", "private"] = "private"
    allow_messages_from: Literal["everyone", "friends", "none"] = "friends"
    allow_friend_requests: bool = True


class PrivacySettingsUpdate(PrivacySettingsBase):
    pass


class PrivacySettingsResponse(PrivacySettingsBase):
    id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

