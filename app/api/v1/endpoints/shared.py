from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import SharedDB
from app.schemas.shared import UserCreate, UserResponse, TenantCreate, TenantResponse
from app.services.tenant_service import TenantService

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: SharedDB,
):
    """Tạo user mới trong shared database."""
    service = TenantService(db)
    return await service.create_user(user_data)


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: SharedDB):
    """Lấy danh sách tất cả users từ shared database."""
    service = TenantService(db)
    return await service.get_all_users()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SharedDB):
    """Lấy thông tin user theo ID từ shared database."""
    service = TenantService(db)
    return await service.get_user(user_id)


# Tenant routes
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: SharedDB,
):
    """
    Tạo tenant mới trong shared database.
    Có thể cung cấp thông tin database riêng (Isolated Strategy).
    """
    service = TenantService(db)
    return await service.create_tenant(tenant_data)


@router.get("/tenants", response_model=List[TenantResponse])
async def get_tenants(db: SharedDB):
    """Lấy danh sách tất cả tenants từ shared database."""
    service = TenantService(db)
    return await service.get_all_tenants()


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, db: SharedDB):
    """Lấy thông tin tenant theo tenant_id từ shared database."""
    service = TenantService(db)
    return await service.get_tenant(tenant_id)