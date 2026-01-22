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
