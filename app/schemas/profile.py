from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# --- Sub-schemas ---

class StudentInfo(BaseModel):
    school: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class")
    major: Optional[str] = None
    academic_year: Optional[str] = None

    class Config:
        populate_by_name = True

class TeacherInfo(BaseModel):
    work_unit: Optional[str] = None
    subject: Optional[str] = None
    specialty: Optional[str] = None
    title: Optional[str] = None

class PrivacySettings(BaseModel):
    visibility: str = "public"  # public, private, connections
    show_contact: bool = False
    allow_interaction: bool = True

# --- Main Schemas ---

class ProfileBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "unspecified"
    verification_status: str = "unverified"
    student_info: Optional[StudentInfo] = None
    teacher_info: Optional[TeacherInfo] = None
    privacy_settings: Optional[PrivacySettings] = Field(default_factory=lambda: PrivacySettings())

class ProfileCreate(BaseModel):
    user_id: int
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    privacy_settings: Optional[PrivacySettings] = None

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

    class Config:
        from_attributes = True

# --- Social Post Schemas ---

class SocialPostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = None
    privacy: str = "public"

class SocialPostResponse(BaseModel):
    id: int
    profile_id: int
    content: str
    media_urls: Optional[List[str]] = None
    privacy: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Combined Response ---

class TenantProfileResponse(BaseModel):
    user: Dict[str, Any]
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True
