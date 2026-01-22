import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.modules.auth.models import User, Tenant
from app.modules.auth.schemas import UserCreate, TenantCreate
from app.db.database_manager import db_manager

logger = logging.getLogger(__name__)


class TenantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Tạo user mới trong shared database."""
        # Check exist (Pre-check)
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email đã tồn tại")

        # Validate tenant_id nếu được cung cấp
        if user_data.tenant_id:
            tenant_result = await self.db.execute(
                select(Tenant).where(Tenant.tenant_id == user_data.tenant_id)
            )
            if not tenant_result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Tenant không tồn tại")

        try:
            # Create
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                full_name=user_data.full_name,
                slug=user_data.slug,
                avatar_url=user_data.avatar_url,
                tenant_id=user_data.tenant_id,
            )
            self.db.add(new_user)
            # Use flush instead of commit to let dependency handle transaction
            # flush ensures id is populated
            await self.db.flush()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError as e:
            logger.error(f"IntegrityError creating user: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Email đã tồn tại (Integrity Error)"
            )
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo user")

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
        result = await self.db.execute(
            select(Tenant).where(Tenant.tenant_id == tenant_data.tenant_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Tenant ID đã tồn tại")

        try:
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
            await self.db.flush()
            await self.db.refresh(new_tenant)

            # Provision Database & Tables immediately
            # Note: This is separate from shared_db transaction
            await db_manager.ensure_tenant_tables(new_tenant.tenant_id)

            return new_tenant
        except IntegrityError as e:
            logger.error(f"IntegrityError creating tenant: {e}")
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Tenant ID đã tồn tại")
        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            # If provisioning failed, we might want to rollback the tenant creation?
            # Since we only flushed, rollback is possible.
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi tạo tenant: {str(e)}")

    async def get_tenant(self, tenant_id: str) -> Tenant:
        result = await self.db.execute(
            select(Tenant).where(Tenant.tenant_id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant không tồn tại")
        return tenant

    async def get_all_tenants(self):
        result = await self.db.execute(select(Tenant))
        return result.scalars().all()
