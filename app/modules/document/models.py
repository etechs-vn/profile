from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TenantBase


class Document(TenantBase):
    """
    Model cho tenant database - Tài liệu riêng của từng tenant.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(nullable=True)
