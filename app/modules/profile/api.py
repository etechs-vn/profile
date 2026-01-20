from typing import List

from fastapi import APIRouter, Path, Query

from app.api.deps import (
    ProfileServiceHeaderDep,
    ProfileServicePathDep,
    ProfileServiceQueryDep,
)
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    StudentProfileUpdate,
    TeacherProfileUpdate,
    TenantProfileResponse,
)

router = APIRouter()


@router.post("/{tenant_id}/profiles", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    service: ProfileServicePathDep,
):
    return await service.create_profile(profile_data)


@router.get("/{tenant_id}/profiles", response_model=List[ProfileResponse])
async def get_profiles(
    service: ProfileServicePathDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    return await service.get_all_profiles(skip=skip, limit=limit)


@router.get("/{tenant_id}/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    service: ProfileServicePathDep,
    profile_id: int = Path(...),
):
    return await service.get_profile_by_id(profile_id)


@router.get("/{tenant_id}/profiles/slug/{slug}", response_model=ProfileResponse)
async def get_profile_by_slug(
    service: ProfileServicePathDep,
    slug: str = Path(...),
    viewer_id: int | None = Query(None),
):
    return await service.get_profile_by_slug(slug, viewer_user_id=viewer_id)


@router.get(
    "/{tenant_id}/profiles/user/{user_id}", response_model=TenantProfileResponse
)
async def get_profile_with_user(
    service: ProfileServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_profile_with_user(user_id)


@router.put(
    "/{tenant_id}/profiles/user/{user_id}/student", response_model=ProfileResponse
)
async def update_student_profile(
    student_data: StudentProfileUpdate,
    service: ProfileServicePathDep,
    user_id: int = Path(...),
):
    return await service.update_student_info(user_id, student_data)


@router.put(
    "/{tenant_id}/profiles/user/{user_id}/teacher", response_model=ProfileResponse
)
async def update_teacher_profile(
    teacher_data: TeacherProfileUpdate,
    service: ProfileServicePathDep,
    user_id: int = Path(...),
):
    return await service.update_teacher_info(user_id, teacher_data)


@router.patch("/{tenant_id}/profiles/user/{user_id}", response_model=ProfileResponse)
async def update_profile_general(
    update_data: ProfileUpdate,
    service: ProfileServicePathDep,
    user_id: int = Path(...),
):
    return await service.update_general_info(user_id, update_data)


# --- Other ---


@router.post("/profiles", response_model=ProfileResponse)
async def create_profile_from_query(
    profile_data: ProfileCreate,
    service: ProfileServiceQueryDep,
):
    return await service.create_profile(profile_data)


@router.get("/profiles/me", response_model=List[ProfileResponse])
async def get_my_profiles(
    service: ProfileServiceHeaderDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    return await service.get_all_profiles(skip=skip, limit=limit)
