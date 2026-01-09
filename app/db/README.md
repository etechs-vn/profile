# Database Module - Multi-Tenant Architecture

Module này hỗ trợ kiến trúc multi-tenant với:
- **Shared Database**: Database chung chứa thông tin cơ bản
- **Tenant Databases**: Database riêng cho từng cá thể (SQLite)

## Cấu hình

Trong file `.env`:

```env
# Shared Database - Database chung
SHARED_DATABASE_URL=sqlite+aiosqlite:///./shared.db
# Hoặc PostgreSQL: postgresql+asyncpg://user:pass@localhost/shared

# Tenant Databases - Thư mục chứa các tenant database files
TENANT_DATABASE_DIR=./tenants

# Template cho tenant database filename (optional, default: tenant_{tenant_id}.db)
TENANT_DATABASE_TEMPLATE=tenant_{tenant_id}.db
```

## Kiến trúc

```
shared.db              # Database chung - thông tin cơ bản
tenants/
  ├── tenant_001.db   # Database riêng cho tenant 001
  ├── tenant_002.db   # Database riêng cho tenant 002
  └── tenant_003.db   # Database riêng cho tenant 003
```

## Sử dụng trong Routes

### 1. Shared Database (Database chung)

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_shared_db
from sqlalchemy import select

@app.get("/common/users")
async def get_common_users(db: AsyncSession = Depends(get_shared_db)):
    result = await db.execute(select(CommonUser))
    return result.scalars().all()
```

### 2. Tenant Database - Từ Path Parameter

```python
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_tenant_db_from_path
from sqlalchemy import select

@app.get("/tenants/{tenant_id}/data")
async def get_tenant_data(
    db: AsyncSession = Depends(get_tenant_db_from_path)
):
    result = await db.execute(select(TenantData))
    return result.scalars().all()
```

### 3. Tenant Database - Từ Query Parameter

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_tenant_db_from_query
from sqlalchemy import select

@app.get("/data")
async def get_data(db: AsyncSession = Depends(get_tenant_db_from_query)):
    result = await db.execute(select(TenantData))
    return result.scalars().all()
```

### 4. Tenant Database - Từ HTTP Header

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_tenant_db_from_header
from sqlalchemy import select

@app.get("/data")
async def get_data(db: AsyncSession = Depends(get_tenant_db_from_header)):
    result = await db.execute(select(TenantData))
    return result.scalars().all()
```

Client gửi request với header:
```
X-Tenant-ID: tenant_001
```

### 5. Tenant Database - Truyền tenant_id trực tiếp

```python
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_tenant_db
from sqlalchemy import select

@app.get("/tenants/{tenant_id}/data")
async def get_tenant_data(
    tenant_id: str = Path(...),
    db: AsyncSession = Depends(lambda: get_tenant_db(tenant_id))
):
    result = await db.execute(select(TenantData))
    return result.scalars().all()
```

### 6. Factory Function cho Tenant cụ thể

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_tenant_db_dependency

# Tạo dependency cho tenant cụ thể
get_tenant_001_db = get_tenant_db_dependency("tenant_001")

@app.get("/specific-tenant-data")
async def get_specific_data(db: AsyncSession = Depends(get_tenant_001_db)):
    result = await db.execute(select(TenantData))
    return result.scalars().all()
```

## Quản lý Database tại Runtime

### Lấy Shared Engine

```python
from app.db import db_manager

shared_engine = db_manager.get_shared_engine()
```

### Lấy Tenant Engine

```python
from app.db import db_manager

# Engine sẽ được tạo tự động nếu chưa có
tenant_engine = db_manager.get_tenant_engine("tenant_001")
```

### Liệt kê Tenants đã cache

```python
from app.db import db_manager

tenants = db_manager.list_tenants()
# ['tenant_001', 'tenant_002', 'tenant_003']
```

### Xóa Tenant Engine khỏi cache

```python
from app.db import db_manager

# Xóa khỏi cache (không dispose, sẽ dispose khi app shutdown)
db_manager.remove_tenant_engine("tenant_001")
```

## Models

### Shared Database Models

```python
from app.db.base import Base
from sqlalchemy import Column, Integer, String

class CommonUser(Base):
    __tablename__ = "common_users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
```

### Tenant Database Models

```python
from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class TenantData(Base):
    __tablename__ = "tenant_data"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String)  # Có thể lưu tenant_id trong data
    data = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Ví dụ hoàn chỉnh

```python
from fastapi import FastAPI, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_shared_db, get_tenant_db_from_path
from app.db.base import Base

app = FastAPI()

# Shared database route
@app.get("/common/users")
async def get_common_users(db: AsyncSession = Depends(get_shared_db)):
    result = await db.execute(select(CommonUser))
    return {"users": result.scalars().all()}

# Tenant database route
@app.get("/tenants/{tenant_id}/data")
async def get_tenant_data(
    db: AsyncSession = Depends(get_tenant_db_from_path)
):
    result = await db.execute(select(TenantData))
    return {"data": result.scalars().all()}

# Route sử dụng cả shared và tenant
@app.get("/tenants/{tenant_id}/profile")
async def get_tenant_profile(
    tenant_id: str = Path(...),
    shared_db: AsyncSession = Depends(get_shared_db),
    tenant_db: AsyncSession = Depends(get_tenant_db_from_path)
):
    # Lấy thông tin chung từ shared database
    common_info = await shared_db.execute(
        select(CommonUser).where(CommonUser.id == tenant_id)
    )
    
    # Lấy dữ liệu riêng từ tenant database
    tenant_data = await tenant_db.execute(select(TenantData))
    
    return {
        "common_info": common_info.scalar_one_or_none(),
        "tenant_data": tenant_data.scalars().all()
    }
```

## Lưu ý

- **Shared Database**: Được khởi tạo khi app start, tables được tạo tự động
- **Tenant Databases**: Được tạo tự động khi được sử dụng lần đầu
- **Caching**: Tenant engines được cache trong memory để tối ưu performance
- **Auto Cleanup**: Tất cả engines (shared + tenant) sẽ được dispose tự động khi app shutdown
- **SQLite**: Tenant databases sử dụng SQLite, mỗi tenant có file riêng
- **Path**: Tenant database files được lưu trong thư mục `TENANT_DATABASE_DIR`

## Backward Compatibility

Các functions cũ vẫn hoạt động:
- `get_db()` - Trả về shared database (default)
- `get_db_by_name()` - Chọn database theo tên
- `get_db_from_header()` - Chọn database qua header
