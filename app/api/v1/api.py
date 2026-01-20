from fastapi import APIRouter

from app.modules.document import api as documents_api
from app.modules.profile import api as profiles_api
from app.modules.social import api as social_api
from app.modules.system import api as system_api
from app.modules.tenant import api as tenant_api

api_router = APIRouter()

# Health Check
api_router.include_router(system_api.router, prefix="/health", tags=["Health Check"])

# Shared Database Routes
api_router.include_router(tenant_api.router, prefix="/shared", tags=["Shared Database"])

# Tenant Database Routes
# Lưu ý: Các router con đã có sẵn prefix /{tenant_id} hoặc không,
# nhưng chúng đều nằm trong nhóm chức năng "Tenant".
# Để giữ backward compatibility với cấu trúc cũ (/tenants/...), ta thêm prefix /tenants ở đây.
api_router.include_router(
    profiles_api.router, prefix="/tenants", tags=["Tenant Profiles"]
)

api_router.include_router(social_api.router, prefix="/tenants", tags=["Tenant Social"])

api_router.include_router(
    documents_api.router, prefix="/tenants", tags=["Tenant Documents"]
)
