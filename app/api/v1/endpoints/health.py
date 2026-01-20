from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import TenantDBPath, SharedDB

router = APIRouter()


@router.get("/{tenant_id}/db-check", response_model=dict[str, Any])
async def check_tenant_db(
    tenant_id: str,
    tenant_db: TenantDBPath,
    shared_db: SharedDB,
) -> Any:
    """
    Kiểm tra kết nối tới Tenant Database và Shared Database.
    Endpoint này chứng minh DatabaseManager hoạt động đúng.
    """
    results = {
        "tenant_id": tenant_id,
        "shared_db_status": "unknown",
        "tenant_db_status": "unknown",
        "tenant_db_info": {},
    }

    # 1. Check Shared DB
    try:
        await shared_db.execute(text("SELECT 1"))
        results["shared_db_status"] = "connected"
    except Exception as e:
        results["shared_db_status"] = f"error: {str(e)}"

    # 2. Check Tenant DB
    try:
        # Lấy tên file DB hoặc DB Name để verify
        # Với SQLite, ta có thể check pragma database_list, với Postgres là current_database()
        # Dùng hàm chung chung
        await tenant_db.execute(text("SELECT 1"))
        results["tenant_db_status"] = "connected"

        # Thử lấy thông tin chi tiết hơn nếu có thể (tùy thuộc driver)
        # Đây chỉ là demo
    except Exception as e:
        results["tenant_db_status"] = f"error: {str(e)}"

    return results
