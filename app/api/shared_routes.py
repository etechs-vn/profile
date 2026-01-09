from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_shared_db
from app.models.shared import Tenant, User

router = APIRouter(prefix="/shared", tags=["Shared Database"])


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    status: str = "active"


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# User routes
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_shared_db),
):
    """Tạo user mới trong shared database."""
    # Kiểm tra email đã tồn tại chưa
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    # Tạo user mới
    new_user = User(email=user_data.email, name=user_data.name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_shared_db)):
    """Lấy danh sách tất cả users từ shared database."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_shared_db)):
    """Lấy thông tin user theo ID từ shared database."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return user


# Tenant routes
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_shared_db),
):
    """Tạo tenant mới trong shared database."""
    # Kiểm tra tenant_id đã tồn tại chưa
    result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_data.tenant_id)
    )
    existing_tenant = result.scalar_one_or_none()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant ID đã tồn tại")

    # Tạo tenant mới
    new_tenant = Tenant(
        tenant_id=tenant_data.tenant_id,
        name=tenant_data.name,
        status=tenant_data.status,
    )
    db.add(new_tenant)
    await db.commit()
    await db.refresh(new_tenant)

    return new_tenant


@router.get("/tenants", response_model=List[TenantResponse])
async def get_tenants(db: AsyncSession = Depends(get_shared_db)):
    """Lấy danh sách tất cả tenants từ shared database."""
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()
    return tenants


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_shared_db)):
    """Lấy thông tin tenant theo tenant_id từ shared database."""
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant không tồn tại")
    return tenant
