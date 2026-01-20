from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import (
    get_shared_db,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)
from app.modules.profile.service import ProfileService
from app.modules.social.service import ConnectionService, SocialService

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


# Connection Service
def get_connection_service_path(
    tenant_db: TenantDBPath,
) -> ConnectionService:
    return ConnectionService(tenant_db)


ConnectionServicePathDep = Annotated[
    ConnectionService, Depends(get_connection_service_path)
]


# Social Service
def get_social_service_path(
    tenant_db: TenantDBPath,
) -> SocialService:
    return SocialService(tenant_db)


SocialServicePathDep = Annotated[SocialService, Depends(get_social_service_path)]
