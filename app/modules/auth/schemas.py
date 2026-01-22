from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    full_name: str | None = None
    slug: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    full_name: str | None = None
    slug: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    status: str = "active"

    # Custom Database Info (Optional)
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_driver: str | None = None


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    status: str
    db_host: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
