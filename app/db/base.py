from sqlalchemy.orm import DeclarativeBase


class SharedBase(DeclarativeBase):
    """
    Base class cho tất cả SQLAlchemy models thuộc **shared database**.
    Các model dùng chung (users, tenants, ...) nên kế thừa từ class này.

    Ví dụ:
        from app.db.base import SharedBase
        from sqlalchemy import Column, Integer, String

        class User(SharedBase):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)
    """

    pass


class TenantBase(DeclarativeBase):
    """
    Base class cho tất cả SQLAlchemy models thuộc **tenant databases**.
    Mỗi tenant database sẽ chứa schema riêng dựa trên TenantBase.

    Ví dụ:
        from app.db.base import TenantBase
        from sqlalchemy import Column, Integer, String

        class Profile(TenantBase):
            __tablename__ = "profiles"
            id = Column(Integer, primary_key=True)
            name = Column(String)
    """

    pass


# Backward compatibility:
# - Giữ tên Base để không phải sửa quá nhiều import cũ.
# - Mặc định ánh xạ Base -> SharedBase (shared database).
Base = SharedBase
