from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import SharedBase


class User(SharedBase):
    """
    Model cho shared database - Thông tin người dùng chung.
    Lưu trong shared database.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]

    # Global Identity Fields
    full_name: Mapped[str | None] = mapped_column(nullable=True)
    slug: Mapped[str | None] = mapped_column(unique=True, index=True, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Tenant(SharedBase):
    """
    Model cho shared database - Thông tin tenant/cá thể.
    Lưu trong shared database để quản lý các tenant.
    """

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(default="active")

    # Database Connection Info (Cho phép Tenant nằm ở server khác)
    # Nếu db_host là NULL -> Dùng Default Strategy (config.py)
    db_host: Mapped[str | None] = mapped_column(nullable=True)
    db_port: Mapped[int | None] = mapped_column(nullable=True)
    db_name: Mapped[str | None] = mapped_column(nullable=True)
    db_user: Mapped[str | None] = mapped_column(nullable=True)
    db_password: Mapped[str | None] = mapped_column(nullable=True)
    db_driver: Mapped[str | None] = mapped_column(
        default="postgresql+asyncpg"
    )  # hoặc sqlite+aiosqlite

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
