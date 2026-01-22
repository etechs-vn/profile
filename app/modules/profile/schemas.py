from datetime import date, datetime

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
    created_at: datetime
    updated_at: datetime

    # Optional: Include related data
    educations: list[EducationResponse] = []
    identity_documents: list[IdentityDocumentResponse] = []
    user_interests: list[UserInterestResponse] = []

    model_config = ConfigDict(from_attributes=True)
