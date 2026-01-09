from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import (
    get_shared_db,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)
from app.models.shared import User
from app.models.tenant import Document, Profile

router = APIRouter(prefix="/tenants", tags=["Tenant Database"])


# Pydantic schemas
class ProfileCreate(BaseModel):
    user_id: int
    full_name: str
    phone: str | None = None
    address: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str | None
    address: str | None
    bio: str | None
    avatar_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    title: str
    content: str | None = None
    file_path: str | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str | None
    file_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TenantProfileResponse(BaseModel):
    """Response kết hợp thông tin từ shared và tenant database."""
    user: dict
    profile: ProfileResponse | None

    class Config:
        from_attributes = True


# ==================== Routes sử dụng Path Parameter ====================

@router.post("/{tenant_id}/profiles", response_model=ProfileResponse)
async def create_profile(
    tenant_id: str = Path(..., description="ID của tenant"),
    profile_data: ProfileCreate = ...,
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
    shared_db: AsyncSession = Depends(get_shared_db),
):
    """
    Tạo profile mới cho tenant.
    Sử dụng path parameter để xác định tenant database.
    """
    # Kiểm tra user có tồn tại trong shared database không
    result = await shared_db.execute(select(User).where(User.id == profile_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại trong shared database")

    # Kiểm tra profile đã tồn tại chưa
    result = await tenant_db.execute(
        select(Profile).where(Profile.user_id == profile_data.user_id)
    )
    existing_profile = result.scalar_one_or_none()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile đã tồn tại cho user này")

    # Tạo profile mới trong tenant database
    new_profile = Profile(
        user_id=profile_data.user_id,
        full_name=profile_data.full_name,
        phone=profile_data.phone,
        address=profile_data.address,
        bio=profile_data.bio,
        avatar_url=profile_data.avatar_url,
    )
    tenant_db.add(new_profile)
    await tenant_db.commit()
    await tenant_db.refresh(new_profile)

    return new_profile


@router.get("/{tenant_id}/profiles", response_model=List[ProfileResponse])
async def get_profiles(
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
):
    """Lấy danh sách tất cả profiles từ tenant database."""
    result = await tenant_db.execute(select(Profile))
    profiles = result.scalars().all()
    return profiles


@router.get("/{tenant_id}/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int = Path(...),
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
):
    """Lấy thông tin profile theo ID từ tenant database."""
    result = await tenant_db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile không tồn tại")
    return profile


@router.get("/{tenant_id}/profiles/user/{user_id}", response_model=TenantProfileResponse)
async def get_profile_with_user(
    user_id: int = Path(...),
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
    shared_db: AsyncSession = Depends(get_shared_db),
):
    """
    Lấy profile kết hợp với thông tin user từ shared database.
    Ví dụ về việc sử dụng cả shared và tenant database trong một route.
    """
    # Lấy user từ shared database
    result = await shared_db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # Lấy profile từ tenant database
    result = await tenant_db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()

    return TenantProfileResponse(
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
        profile=profile,
    )


# ==================== Routes sử dụng Query Parameter ====================

@router.post("/profiles", response_model=ProfileResponse)
async def create_profile_from_query(
    tenant_id: str = Query(..., description="ID của tenant"),
    profile_data: ProfileCreate = ...,
    tenant_db: AsyncSession = Depends(get_tenant_db_from_query),
    shared_db: AsyncSession = Depends(get_shared_db),
):
    """
    Tạo profile mới cho tenant.
    Sử dụng query parameter để xác định tenant database.
    """
    # Kiểm tra user có tồn tại trong shared database không
    result = await shared_db.execute(select(User).where(User.id == profile_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại trong shared database")

    # Tạo profile mới trong tenant database
    new_profile = Profile(
        user_id=profile_data.user_id,
        full_name=profile_data.full_name,
        phone=profile_data.phone,
        address=profile_data.address,
        bio=profile_data.bio,
        avatar_url=profile_data.avatar_url,
    )
    tenant_db.add(new_profile)
    await tenant_db.commit()
    await tenant_db.refresh(new_profile)

    return new_profile


# ==================== Routes sử dụng Header ====================

@router.get("/profiles/me", response_model=List[ProfileResponse])
async def get_my_profiles(
    tenant_db: AsyncSession = Depends(get_tenant_db_from_header),
):
    """
    Lấy danh sách profiles từ tenant database.
    Sử dụng header X-Tenant-ID để xác định tenant database.
    """
    result = await tenant_db.execute(select(Profile))
    profiles = result.scalars().all()
    return profiles


# ==================== Document Routes ====================

@router.post("/{tenant_id}/documents", response_model=DocumentResponse)
async def create_document(
    tenant_id: str = Path(...),
    document_data: DocumentCreate = ...,
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
):
    """Tạo document mới trong tenant database."""
    new_document = Document(
        title=document_data.title,
        content=document_data.content,
        file_path=document_data.file_path,
    )
    tenant_db.add(new_document)
    await tenant_db.commit()
    await tenant_db.refresh(new_document)

    return new_document


@router.get("/{tenant_id}/documents", response_model=List[DocumentResponse])
async def get_documents(
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
):
    """Lấy danh sách tất cả documents từ tenant database."""
    result = await tenant_db.execute(select(Document))
    documents = result.scalars().all()
    return documents


@router.get("/{tenant_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int = Path(...),
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path),
):
    """Lấy thông tin document theo ID từ tenant database."""
    result = await tenant_db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    return document
