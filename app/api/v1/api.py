from fastapi import APIRouter

from app.api.v1.endpoints import shared, profiles, documents, health, social

api_router = APIRouter()

# Health Check
api_router.include_router(health.router, prefix="/health", tags=["Health Check"])

# Shared Database Routes
api_router.include_router(shared.router, prefix="/shared", tags=["Shared Database"])

# Tenant Database Routes
# Lưu ý: Các router con đã có sẵn prefix /{tenant_id} hoặc không,
# nhưng chúng đều nằm trong nhóm chức năng "Tenant".
# Để giữ backward compatibility với cấu trúc cũ (/tenants/...), ta thêm prefix /tenants ở đây.
api_router.include_router(profiles.router, prefix="/tenants", tags=["Tenant Profiles"])

api_router.include_router(social.router, prefix="/tenants", tags=["Tenant Social"])

api_router.include_router(
    documents.router, prefix="/tenants", tags=["Tenant Documents"]
)
