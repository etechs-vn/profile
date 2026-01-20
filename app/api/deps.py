from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import (
    get_shared_db,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)
from app.services.profile_service import ProfileService

# Shared DB Dependency
SharedDB = Annotated[AsyncSession, Depends(get_shared_db)]

# Tenant DB Dependencies
TenantDBPath = Annotated[AsyncSession, Depends(get_tenant_db_from_path)]
TenantDBQuery = Annotated[AsyncSession, Depends(get_tenant_db_from_query)]
TenantDBHeader = Annotated[AsyncSession, Depends(get_tenant_db_from_header)]


# Service Dependencies
def get_profile_service_path(
    tenant_db: TenantDBPath,
    shared_db: SharedDB,
) -> ProfileService:
    return ProfileService(tenant_db, shared_db)


ProfileServicePathDep = Annotated[ProfileService, Depends(get_profile_service_path)]


def get_profile_service_query(
    tenant_db: TenantDBQuery,
    shared_db: SharedDB,
) -> ProfileService:
    return ProfileService(tenant_db, shared_db)


ProfileServiceQueryDep = Annotated[ProfileService, Depends(get_profile_service_query)]


def get_profile_service_header(
    tenant_db: TenantDBHeader,
    shared_db: SharedDB,
) -> ProfileService:
    return ProfileService(tenant_db, shared_db)


ProfileServiceHeaderDep = Annotated[ProfileService, Depends(get_profile_service_header)]
