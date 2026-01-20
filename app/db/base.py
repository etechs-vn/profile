from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TimestampMixin:
    """
    Mixin cung cấp các trường created_at và updated_at tự động.
    Sử dụng timezone-naive datetime (UTC) để tương thích tốt với PostgreSQL Timestamp.
    """

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class SharedBase(DeclarativeBase, TimestampMixin):
    """
    Base class cho tất cả SQLAlchemy models thuộc **shared database**.
    Các model dùng chung (users, tenants, ...) nên kế thừa từ class này.
    """

    pass


class TenantBase(DeclarativeBase, TimestampMixin):
    """
    Base class cho tất cả SQLAlchemy models thuộc **tenant databases**.
    Mỗi tenant database sẽ chứa schema riêng dựa trên TenantBase.
    """

    pass


# Backward compatibility:
# - Giữ tên Base để không phải sửa quá nhiều import cũ.
# - Mặc định ánh xạ Base -> SharedBase (shared database).
Base = SharedBase
