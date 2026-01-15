from typing import List

from fastapi import APIRouter, Path, Query

from app.api.deps import SharedDB, TenantDBPath, TenantDBQuery, TenantDBHeader
from app.schemas.profile import (
    ProfileCreate, ProfileResponse, ProfileUpdate, 
    SocialPostCreate, SocialPostResponse,
    StudentProfileUpdate, TeacherProfileUpdate, TenantProfileResponse
)
from app.services.profile_service import ProfileService

router = APIRouter()

@router.post("/{tenant_id}/profiles", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    tenant_db: TenantDBPath,
    shared_db: SharedDB,
    tenant_id: str = Path(..., description="ID của tenant"),
):
    service = ProfileService(tenant_db, shared_db)
    return await service.create_profile(profile_data)


@router.get("/{tenant_id}/profiles", response_model=List[ProfileResponse])
async def get_profiles(
    tenant_db: TenantDBPath,
    tenant_id: str = Path(..., description="ID của tenant"),
):
    service = ProfileService(tenant_db)
    return await service.get_all_profiles()


@router.get("/{tenant_id}/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    profile_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.get_profile_by_id(profile_id)


@router.get("/{tenant_id}/profiles/user/{user_id}", response_model=TenantProfileResponse)
async def get_profile_with_user(
    tenant_db: TenantDBPath,
    shared_db: SharedDB,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db, shared_db)
    return await service.get_profile_with_user(user_id)


@router.put("/{tenant_id}/profiles/user/{user_id}/student", response_model=ProfileResponse)
async def update_student_profile(
    student_data: StudentProfileUpdate,
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.update_student_info(user_id, student_data)


@router.put("/{tenant_id}/profiles/user/{user_id}/teacher", response_model=ProfileResponse)
async def update_teacher_profile(
    teacher_data: TeacherProfileUpdate,
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.update_teacher_info(user_id, teacher_data)


@router.patch("/{tenant_id}/profiles/user/{user_id}", response_model=ProfileResponse)
async def update_profile_general(
    update_data: ProfileUpdate,
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.update_general_info(user_id, update_data)


@router.post("/{tenant_id}/profiles/user/{user_id}/posts", response_model=SocialPostResponse)
async def create_social_post(
    post_data: SocialPostCreate,
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.create_social_post(user_id, post_data)


@router.get("/{tenant_id}/profiles/user/{user_id}/posts", response_model=List[SocialPostResponse])
async def get_social_posts(
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    user_id: int = Path(...),
):
    service = ProfileService(tenant_db)
    return await service.get_social_posts(user_id)


@router.post("/profiles", response_model=ProfileResponse)
async def create_profile_from_query(
    profile_data: ProfileCreate,
    tenant_db: TenantDBQuery,
    shared_db: SharedDB,
    tenant_id: str = Query(..., description="ID của tenant"),
):
    service = ProfileService(tenant_db, shared_db)
    return await service.create_profile(profile_data)


@router.get("/profiles/me", response_model=List[ProfileResponse])
async def get_my_profiles(
    tenant_db: TenantDBHeader,
):
    service = ProfileService(tenant_db)
    return await service.get_all_profiles()
