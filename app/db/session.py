from typing import Annotated

from fastapi import Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.database_manager import db_manager


# ==================== Shared Database ====================

shared_session_factory = async_sessionmaker(
    db_manager.get_shared_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_shared_db() -> AsyncSession:
    """Dependency lấy session từ shared database."""
    async with shared_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==================== Tenant Database Helper ====================

async def _yield_tenant_session(tenant_id: str):
    """Internal helper để tạo và yield tenant session."""
    # Đảm bảo tables tồn tại (chỉ chạy 1 lần/tenant)
    await db_manager.ensure_tenant_tables(tenant_id)
    
    # get_tenant_engine giờ là async function
    engine = await db_manager.get_tenant_engine(tenant_id)
    
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==================== Tenant Dependencies ====================

async def get_tenant_db_from_path(
    tenant_id: Annotated[str, Path(description="ID của tenant")],
) -> AsyncSession:
    """Lấy tenant DB session từ path param {tenant_id}."""
    async for session in _yield_tenant_session(tenant_id):
        yield session


async def get_tenant_db_from_query(
    tenant_id: Annotated[str, Query(description="ID của tenant")],
) -> AsyncSession:
    """Lấy tenant DB session từ query param ?tenant_id=..."""
    async for session in _yield_tenant_session(tenant_id):
        yield session


async def get_tenant_db_from_header(
    x_tenant_id: Annotated[str, Header(description="ID của tenant")],
) -> AsyncSession:
    """Lấy tenant DB session từ header X-Tenant-ID."""
    async for session in _yield_tenant_session(x_tenant_id):
        yield session


def get_tenant_db_dependency(tenant_id: str):
    """Factory tạo dependency cố định cho một tenant cụ thể."""
    async def _get_db() -> AsyncSession:
        async for session in _yield_tenant_session(tenant_id):
            yield session
    return _get_db
