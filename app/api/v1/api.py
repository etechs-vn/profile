from fastapi import APIRouter

from app.modules.document import api as documents_api
from app.modules.profile import api as profiles_api
from app.modules.social import api as social_api
from app.modules.system import api as system_api
from app.modules.tenant import api as tenant_api
from app.modules.wallet import api as wallet_api

api_router = APIRouter()

# Health Check
api_router.include_router(system_api.router, prefix="/health", tags=["Health Check"])

# Shared Database Routes
api_router.include_router(tenant_api.router, prefix="/shared", tags=["Shared Database"])

# Tenant Database Routes
api_router.include_router(
    profiles_api.router, prefix="/tenants", tags=["Tenant Profiles"]
)

api_router.include_router(social_api.router, prefix="/tenants", tags=["Tenant Social"])

api_router.include_router(
    documents_api.router, prefix="/tenants", tags=["Tenant Documents"]
)

api_router.include_router(wallet_api.router, prefix="/tenants", tags=["Tenant Wallet"])
