# Hướng dẫn Toàn diện SQLAlchemy ORM 2.0 (AsyncIO)

Hướng dẫn này bao gồm các pattern thường dùng nhất trong SQLAlchemy 2.0 với phong cách AsyncIO, được tối ưu cho FastAPI và PostgreSQL (`asyncpg`).

## 1. Cài đặt

```bash
uv add sqlalchemy[asyncio] asyncpg
```

## 2. Định nghĩa Model (Typed Mapping)

SQLAlchemy 2.0 sử dụng `Mapped[]` và `mapped_column()` để định nghĩa model với type hints chính xác.

`app/models/example.py`
```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, String, func, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(200), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    # Relationship: 1 User - N Posts
    posts: Mapped[List["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[Optional[str]] = mapped_column(Text)
    views: Mapped[int] = mapped_column(Integer, default=0)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

## 3. Cấu hình Session

`app/db/session.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Lưu ý: Dùng postgresql+asyncpg://
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # BẮT BUỘC cho Async
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## 4. Truy vấn dữ liệu (Select)

### 4.1. Basic Select
Lấy nhiều dòng hoặc 1 dòng.

```python
from sqlalchemy import select

async def get_all_users(db: AsyncSession):
    # Lấy tất cả (List[User])
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int):
    # Lấy 1 dòng theo Primary Key (nhanh nhất)
    return await db.get(User, user_id)

async def get_one_user(db: AsyncSession, username: str):
    # Lấy 1 dòng theo điều kiện
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() # Trả về None nếu không tìm thấy
```

### 4.2. Filtering (Điều kiện lọc)
Các toán tử so sánh phổ biến.

```python
from sqlalchemy import or_, and_, not_

async def filter_users(db: AsyncSession):
    stmt = select(User).where(
        # Bằng: ==
        (User.is_active == True) &
        
        # Khác: !=
        (User.username != "admin") &
        
        # Chứa chuỗi (LIKE / ILIKE - không phân biệt hoa thường)
        User.email.ilike("%@gmail.com") &
        
        # Trong danh sách (IN)
        User.id.in_([1, 2, 3]) &
        
        # Lớn hơn / Nhỏ hơn
        (User.created_at >= datetime(2023, 1, 1))
    )
    
    # OR condition
    stmt_or = select(User).where(
        or_(
            User.username == "teemo",
            User.email == "teemo@lol.com"
        )
    )
```

### 4.3. Ordering & Layout (Sắp xếp & Phân trang)

```python
async def get_posts_paginated(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = (
        select(Post)
        .where(Post.views > 100)
        # Sắp xếp giảm dần (desc) và tăng dần (asc)
        .order_by(Post.views.desc(), Post.id.asc())
        # Offset & Limit
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### 4.4. Aggregation (Gộp nhóm - Count, Sum, Max)

```python
from sqlalchemy import func

async def get_user_stats(db: AsyncSession):
    stmt = select(
        func.count(User.id).label("total_users"),
        func.max(User.created_at).label("latest_user")
    )
    result = await db.execute(stmt)
    # Kết quả trả về Row object (như tuple có tên)
    row = result.one()
    return {"total": row.total_users, "latest": row.latest_user}

async def group_by_example(db: AsyncSession):
    # Đếm số bài post của mỗi user
    stmt = (
        select(Post.user_id, func.count(Post.id))
        .group_by(Post.user_id)
        .having(func.count(Post.id) > 5) # Chỉ lấy user có > 5 bài
    )
```

### 4.5. Relationships Joining (Quan trọng cho Async)
Trong AsyncIO, bạn không thể truy cập relationship (ví dụ `user.posts`) nếu chưa load nó query (Lazy loading sẽ gây lỗi).

**Chiến lược 1: `selectinload` (Khuyên dùng cho quan hệ 1-N)**
Phát sinh 2 câu query riêng biệt: 1 câu lấy User, 1 câu lấy Posts theo list User ID. Nhanh và hiệu quả.

```python
from sqlalchemy.orm import selectinload

async def get_users_with_posts(db: AsyncSession):
    stmt = (
        select(User)
        .options(selectinload(User.posts)) # Eager load posts
    )
    result = await db.execute(stmt)
    for user in result.scalars():
        print(user.posts) # OK, không bị lỗi
```

**Chiến lược 2: `joinedload` (Khuyên dùng cho quan hệ N-1)**
Sử dụng SQL INNER JOIN / LEFT JOIN. Tốt khi load cha từ con (vd: load User từ Post).

```python
from sqlalchemy.orm import joinedload

async def get_posts_with_author(db: AsyncSession):
    stmt = (
        select(Post)
        .options(joinedload(Post.author)) # Join bảng User
    )
```

## 5. Thêm / Sửa / Xóa (CUD Ops)

### 5.1. Insert (Thêm mới)

```python
async def create_new_user(db: AsyncSession):
    user = User(username="yasuo", email="hasagi@lol.com")
    db.add(user)
    
    await db.commit()
    await db.refresh(user) # Lấy lại ID và default values từ DB
    return user
```

### 5.2. Update (Cập nhật)

**Style 1: ORM Update (Load -> Change -> Commit)**
Dùng khi cần logic validate phức tạp trên object.

```python
async def update_user_bio(db: AsyncSession, user_id: int, bio: str):
    user = await db.get(User, user_id)
    if not user:
        return None
        
    user.bio = bio # Tracking changes tự động
    await db.commit() # Chỉ update các cột thay đổi
    return user
```

**Style 2: Bulk Update (Nhanh, không cần load)**
Dùng khi update nhiều dòng hoặc update đơn giản.

```python
from sqlalchemy import update

async def increment_views(db: AsyncSession, post_id: int):
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(views=Post.views + 1) # Expression SQL
        .execution_options(synchronize_session=False) 
    )
    await db.execute(stmt)
    await db.commit()
```

### 5.3. Delete (Xóa)

```python
from sqlalchemy import delete

async def delete_inactive_users(db: AsyncSession):
    stmt = delete(User).where(User.is_active == False)
    await db.execute(stmt)
    await db.commit()
```

### 5.4. Upsert (PostgreSQL only)
Insert nếu chưa có, Update nếu đã trùng Key.

```python
from sqlalchemy.dialects.postgresql import insert

async def upsert_user(db: AsyncSession, user_id: int, name: str):
    stmt = insert(User).values(id=user_id, username=name)
    
    # Nếu trùng User ID thì update username
    stmt = stmt.on_conflict_do_update(
        index_elements=[User.id],
        set_=dict(username=name)
    )
    
    await db.execute(stmt)
    await db.commit()
```

## 6. Advanced Topics

### 6.1. Raw SQL (SQL thuần)
Khi query quá phức tạp hoặc cần tối ưu đặc biệt.

```python
from sqlalchemy import text

async def raw_sql_example(db: AsyncSession):
    # Dùng params (:id) để chống SQL Injection
    stmt = text("SELECT * FROM users WHERE id = :id")
    result = await db.execute(stmt, {"id": 1})
    
    # Kết quả trả về mappings (dict-like)
    return result.mappings().all()
```

### 6.2. Streaming (Dữ liệu lớn)
Xử lý dữ liệu khổng lồ mà không load hết vào RAM.

```python
async def process_large_dataset(db: AsyncSession):
    stmt = select(User).execution_options(yield_per=100) # Fetch từng 100 dòng
    
    result = await db.stream(stmt)
    
    # Async Iterator
    async for partition in result.partitions(100):
        for row in partition:
            user = row[0]
            # Xử lý user...
```

### 6.3. Nested Transactions (Savepoint)
Dùng khi muốn rollback một phần logic mà không rollback toàn bộ request.

```python
async def complex_transaction(db: AsyncSession):
    async with db.begin(): # Transaction chính
        db.add(user1)
        
        # Tạo savepoint
        async with db.begin_nested(): 
            db.add(user2)
            # Nếu đoạn này lỗi, chỉ user2 bị rollback, user1 vẫn giữ
```

## 7. Các lưu ý "Sống còn"

1.  **Luôn dùng `await`**: Mọi method `execute`, `commit`, `refresh`, `get` đều là async.
2.  **MissingGreenlet Error**: Lỗi này xuất hiện khi bạn cố truy cập relationship chưa load (vd `print(user.posts)`) bên ngoài session context hoặc chưa dùng `selectinload`.
3.  **Returning**: Các lệnh `insert/update/delete` mặc định không trả về dữ liệu. Nếu muốn lấy dữ liệu sau khi sửa/xóa, dùng `.returning(User)` (chỉ hỗ trợ tốt trên PostgreSQL).
    ```python
    stmt = delete(User).where(User.id == 1).returning(User)
    res = await db.execute(stmt)
    deleted_user = res.scalar_one()
    ```
4.  **Pydantic Integration**: Khi return model ra API:
    ```python
    class UserResponse(BaseModel):
        id: int
        username: str
        class Config:
            from_attributes = True # Quan trọng
    ```
