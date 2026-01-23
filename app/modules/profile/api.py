from typing import List

from fastapi import APIRouter, Path, Query

from app.api.deps import ProfileServicePathDep
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    EducationCreate,
    EducationResponse,
    IdentityDocumentCreate,
    IdentityDocumentResponse,
    UserInterestCreate,
    UserInterestResponse,
    StudentInfoCreate,
    StudentInfoResponse,
    TeacherInfoCreate,
    TeacherInfoResponse,
    VerificationRequest,
    VerificationResponse,
    PrivacySettingsUpdate,
    PrivacySettingsResponse,
)

router = APIRouter()


# --- Profile Management ---


@router.post("/{tenant_id}/users/{user_id}/profile", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    service: ProfileServicePathDep,
    user_id: int = Path(..., description="ID of the user in Shared DB"),
):
    """
    Create a new profile for a specific user.
    """
    return await service.create_profile(user_id, profile_data)


@router.get("/{tenant_id}/users/{user_id}/profile", response_model=ProfileResponse)
async def get_profile_by_user(
    service: ProfileServicePathDep,
    user_id: int = Path(...),
):
    """
    Get profile by User ID.
    """
    return await service.get_profile_by_user_id(user_id)


@router.get("/{tenant_id}/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    service: ProfileServicePathDep,
    profile_id: str = Path(..., description="UUID of the profile"),
):
    """
    Get profile by Profile ID (UUID).
    """
    return await service.get_profile_by_id(profile_id)


@router.put("/{tenant_id}/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    update_data: ProfileUpdate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """
    Update profile information.
    """
    return await service.update_profile(profile_id, update_data)


@router.get("/{tenant_id}/profiles", response_model=List[ProfileResponse])
async def get_all_profiles(
    service: ProfileServicePathDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List all profiles in the tenant.
    """
    return await service.get_all_profiles(skip=skip, limit=limit)


# --- Sub-resources (Education, Documents, Interests) ---


@router.post(
    "/{tenant_id}/profiles/{profile_id}/educations", response_model=EducationResponse
)
async def add_education(
    education_data: EducationCreate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    return await service.add_education(profile_id, education_data)


@router.post(
    "/{tenant_id}/profiles/{profile_id}/documents",
    response_model=IdentityDocumentResponse,
)
async def add_document(
    document_data: IdentityDocumentCreate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    return await service.add_identity_document(profile_id, document_data)


@router.post(
    "/{tenant_id}/profiles/{profile_id}/interests", response_model=UserInterestResponse
)
async def add_interest(
    interest_data: UserInterestCreate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    return await service.add_interest(profile_id, interest_data)


# --- Verification Workflow ---


@router.post(
    "/{tenant_id}/profiles/{profile_id}/student-info",
    response_model=StudentInfoResponse,
)
async def add_student_info(
    data: StudentInfoCreate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """Thêm thông tin học sinh vào profile."""
    return await service.add_student_info(profile_id, data)


@router.post(
    "/{tenant_id}/profiles/{profile_id}/teacher-info",
    response_model=TeacherInfoResponse,
)
async def add_teacher_info(
    data: TeacherInfoCreate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """Thêm thông tin giáo viên vào profile."""
    return await service.add_teacher_info(profile_id, data)


@router.post(
    "/{tenant_id}/profiles/{profile_id}/request-verification",
    response_model=VerificationResponse,
)
async def request_verification(
    data: VerificationRequest,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """Yêu cầu xác minh vai trò (học sinh hoặc giáo viên)."""
    profile = await service.request_verification(profile_id, data)
    return VerificationResponse(
        profile_id=profile.profile_id,
        verification_status=profile.verification_status,
        role=profile.role,
        message=f"Yêu cầu xác minh vai trò {data.role} đã được gửi. Trạng thái: {profile.verification_status}",
    )


# --- Privacy Settings ---


@router.get(
    "/{tenant_id}/profiles/{profile_id}/privacy",
    response_model=PrivacySettingsResponse,
)
async def get_privacy_settings(
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """Lấy cài đặt quyền riêng tư của profile."""
    return await service.get_privacy_settings(profile_id)


@router.put(
    "/{tenant_id}/profiles/{profile_id}/privacy",
    response_model=PrivacySettingsResponse,
)
async def update_privacy_settings(
    data: PrivacySettingsUpdate,
    service: ProfileServicePathDep,
    profile_id: str = Path(...),
):
    """Cập nhật cài đặt quyền riêng tư."""
    return await service.update_privacy_settings(profile_id, data)

