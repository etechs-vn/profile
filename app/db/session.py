from typing import Annotated

from fastapi import Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.database_manager import db_manager


def get_session_factory(db_name: str | None = None):
    """
    Lấy session factory cho database cụ thể.

    Args:
        db_name: Tên database. Nếu None, sử dụng default database.

    Returns:
        async_sessionmaker instance
    """
    engine = db_manager.get_engine(db_name)
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# Shared database session factory
shared_session_factory = async_sessionmaker(
    db_manager.get_shared_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Default session factory (sử dụng shared database)
default_async_session = shared_session_factory

# Backward compatibility: engine và async_session
engine = db_manager.default_engine
async_session = default_async_session


# Dependency function để inject AsyncSession vào FastAPI routes (default database)
async def get_db() -> AsyncSession:
    """
    Dependency function để lấy database session từ default database.
    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db

    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        return result.scalars().all()
    """
    async with default_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency function để chọn database động qua query parameter
async def get_db_by_name(
    db_name: str | None = None,
) -> AsyncSession:
    """
    Dependency function để lấy database session từ database cụ thể.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends, Query
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db_by_name

    @app.get("/users")
    async def get_users(
        db_name: str = Query("default", description="Tên database"),
        db: AsyncSession = Depends(get_db_by_name)
    ):
        result = await db.execute(select(User))
        return result.scalars().all()

    Hoặc sử dụng Header:

    @app.get("/users")
    async def get_users(
        x_db_name: Annotated[str | None, Header()] = None,
        db: AsyncSession = Depends(get_db_by_name)
    ):
        ...
    """
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency function với Header để chọn database
async def get_db_from_header(
    x_db_name: Annotated[str | None, Header(description="Tên database")] = None,
) -> AsyncSession:
    """
    Dependency function để lấy database session từ HTTP header 'X-DB-Name'.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db_from_header

    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db_from_header)):
        result = await db.execute(select(User))
        return result.scalars().all()

    Client gửi request với header: X-DB-Name: secondary
    """
    session_factory = get_session_factory(x_db_name)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Factory function để tạo dependency cho database cụ thể
def get_db_dependency(db_name: str):
    """
    Factory function để tạo dependency function cho database cụ thể.

    Sử dụng:

    from app.db.session import get_db_dependency

    get_secondary_db = get_db_dependency("secondary")

    @app.get("/analytics")
    async def get_analytics(db: AsyncSession = Depends(get_secondary_db)):
        ...
    """

    async def _get_db() -> AsyncSession:
        session_factory = get_session_factory(db_name)
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    return _get_db


# ==================== Shared Database Dependencies ====================


async def get_shared_db() -> AsyncSession:
    """
    Dependency function để lấy session từ shared database (database chung).

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_shared_db

    @app.get("/common-data")
    async def get_common_data(db: AsyncSession = Depends(get_shared_db)):
        result = await db.execute(select(CommonModel))
        return result.scalars().all()
    """
    async with shared_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==================== Tenant Database Dependencies ====================


def get_tenant_session_factory(tenant_id: str):
    """
    Lấy session factory cho tenant database cụ thể.

    Args:
        tenant_id: ID của tenant/cá thể

    Returns:
        async_sessionmaker instance
    """
    engine = db_manager.get_tenant_engine(tenant_id)
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_tenant_db(tenant_id: str) -> AsyncSession:
    """
    Dependency function để lấy session từ tenant database.
    Tự động tạo tables nếu chưa có.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends, Path
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_tenant_db

    @app.get("/tenants/{tenant_id}/data")
    async def get_tenant_data(
        tenant_id: str = Path(...),
        db: AsyncSession = Depends(get_tenant_db)
    ):
        result = await db.execute(select(TenantModel))
        return result.scalars().all()
    """
    # Đảm bảo tables đã được tạo cho tenant database
    await db_manager.ensure_tenant_tables(tenant_id)
    
    session_factory = get_tenant_session_factory(tenant_id)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tenant_db_from_path(
    tenant_id: Annotated[str, Path(description="ID của tenant/cá thể")],
) -> AsyncSession:
    """
    Dependency function để lấy tenant database session từ path parameter.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_tenant_db_from_path

    @app.get("/tenants/{tenant_id}/data")
    async def get_tenant_data(db: AsyncSession = Depends(get_tenant_db_from_path)):
        result = await db.execute(select(TenantModel))
        return result.scalars().all()
    """
    # Đảm bảo tables đã được tạo cho tenant database
    await db_manager.ensure_tenant_tables(tenant_id)
    
    session_factory = get_tenant_session_factory(tenant_id)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tenant_db_from_query(
    tenant_id: Annotated[str, Query(description="ID của tenant/cá thể")],
) -> AsyncSession:
    """
    Dependency function để lấy tenant database session từ query parameter.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_tenant_db_from_query

    @app.get("/data")
    async def get_data(db: AsyncSession = Depends(get_tenant_db_from_query)):
        result = await db.execute(select(TenantModel))
        return result.scalars().all()
    """
    # Đảm bảo tables đã được tạo cho tenant database
    await db_manager.ensure_tenant_tables(tenant_id)
    
    session_factory = get_tenant_session_factory(tenant_id)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tenant_db_from_header(
    x_tenant_id: Annotated[str, Header(description="ID của tenant/cá thể")],
) -> AsyncSession:
    """
    Dependency function để lấy tenant database session từ HTTP header 'X-Tenant-ID'.

    Sử dụng trong FastAPI routes như:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_tenant_db_from_header

    @app.get("/data")
    async def get_data(db: AsyncSession = Depends(get_tenant_db_from_header)):
        result = await db.execute(select(TenantModel))
        return result.scalars().all()

    Client gửi request với header: X-Tenant-ID: tenant_123
    """
    # Đảm bảo tables đã được tạo cho tenant database
    await db_manager.ensure_tenant_tables(x_tenant_id)
    
    session_factory = get_tenant_session_factory(x_tenant_id)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Factory function để tạo dependency cho tenant cụ thể
def get_tenant_db_dependency(tenant_id: str):
    """
    Factory function để tạo dependency function cho tenant cụ thể.
    Tự động tạo tables nếu chưa có.

    Sử dụng:

    from app.db.session import get_tenant_db_dependency

    get_tenant_123_db = get_tenant_db_dependency("tenant_123")

    @app.get("/specific-tenant-data")
    async def get_specific_data(db: AsyncSession = Depends(get_tenant_123_db)):
        ...
    """

    async def _get_db() -> AsyncSession:
        # Đảm bảo tables đã được tạo cho tenant database
        await db_manager.ensure_tenant_tables(tenant_id)
        
        session_factory = get_tenant_session_factory(tenant_id)
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    return _get_db
