from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.shared import User, Tenant
from app.schemas.shared import UserCreate, TenantCreate

class TenantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Tạo user mới trong shared database."""
        # Check exist
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email đã tồn tại")

        # Create
        new_user = User(email=user_data.email, name=user_data.name)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user(self, user_id: int) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User không tồn tại")
        return user
        
    async def get_all_users(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """Tạo tenant mới."""
        # Check exist
        result = await self.db.execute(select(Tenant).where(Tenant.tenant_id == tenant_data.tenant_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Tenant ID đã tồn tại")

        # Create
        new_tenant = Tenant(
            tenant_id=tenant_data.tenant_id,
            name=tenant_data.name,
            status=tenant_data.status,
            db_host=tenant_data.db_host,
            db_port=tenant_data.db_port,
            db_name=tenant_data.db_name,
            db_user=tenant_data.db_user,
            db_password=tenant_data.db_password,
            db_driver=tenant_data.db_driver,
        )
        self.db.add(new_tenant)
        await self.db.commit()
        await self.db.refresh(new_tenant)
        return new_tenant

    async def get_tenant(self, tenant_id: str) -> Tenant:
        result = await self.db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant không tồn tại")
        return tenant

    async def get_all_tenants(self):
        result = await self.db.execute(select(Tenant))
        return result.scalars().all()
