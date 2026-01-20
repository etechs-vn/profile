import logging
from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from app.modules.auth.models import Tenant

logger = logging.getLogger(__name__)


class TenantConfigProvider:
    """
    Chịu trách nhiệm truy vấn cấu hình Tenant từ Shared Database.
    """

    def __init__(self, shared_engine: AsyncEngine):
        self.shared_engine = shared_engine

    async def get_config(self, tenant_id: str) -> RowMapping | None:
        """
        Lấy thông tin cấu hình kết nối DB của tenant.
        """
        try:
            async with self.shared_engine.connect() as conn:
                result = await conn.execute(
                    select(
                        Tenant.db_host,
                        Tenant.db_port,
                        Tenant.db_name,
                        Tenant.db_user,
                        Tenant.db_password,
                        Tenant.db_driver,
                    ).where(Tenant.tenant_id == tenant_id)
                )
                return result.mappings().one_or_none()
        except Exception as e:
            logger.error(f"Error fetching tenant config for {tenant_id}: {e}")
            return None
