from typing import Annotated

from fastapi import Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import (
    get_shared_db,
    get_tenant_db_from_header,
    get_tenant_db_from_path,
    get_tenant_db_from_query,
)

# Shared DB Dependency
SharedDB = Annotated[AsyncSession, Depends(get_shared_db)]

# Tenant DB Dependencies
TenantDBPath = Annotated[AsyncSession, Depends(get_tenant_db_from_path)]
TenantDBQuery = Annotated[AsyncSession, Depends(get_tenant_db_from_query)]
TenantDBHeader = Annotated[AsyncSession, Depends(get_tenant_db_from_header)]
