# AGENTS.md - Developer Guidelines for Profile API

**Project:** FastAPI Multi-Tenant Backend  
**Python Version:** 3.13+  
**Architecture:** Database-per-Tenant with Shared Metadata DB  
**Language:** Code in English, Docstrings/Comments in Vietnamese

---

## 🚀 Build, Lint, and Test Commands

### Setup & Dependencies
```bash
# Install dependencies (using uv package manager)
uv sync

# Install dev dependencies (add these to pyproject.toml first)
uv add --dev pytest pytest-asyncio pytest-cov httpx ruff mypy
```

### Running the Application
```bash
# Development server with auto-reload
uv run uvicorn app.main:app --reload

# Production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# API Documentation URLs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Testing (when tests are added)
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_profile_service.py

# Run specific test function
uv run pytest tests/test_profile_service.py::test_create_profile

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run tests matching pattern
uv run pytest -k "profile"
```

### Linting & Formatting (configure these)
```bash
# Format code with Ruff
uv run ruff format .

# Lint code with Ruff
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Type checking with mypy
uv run mypy app/
```

### Manual API Testing
```bash
# Use Bruno API Client (located in bruno/ directory)
# See bruno/README.md for detailed usage
```

---

## 📁 Project Structure

```
app/
├── api/                      # API Layer
│   ├── deps.py              # Dependency injection (SharedDB, TenantDB)
│   └── v1/
│       ├── api.py           # Router aggregator
│       └── endpoints/       # Endpoint handlers
├── core/
│   └── config.py           # Settings (Pydantic BaseSettings)
├── db/
│   ├── base.py             # SharedBase & TenantBase declarative
│   ├── database_manager.py # Multi-tenant engine manager
│   └── session.py          # Session factories
├── models/                  # SQLAlchemy Models
│   ├── shared.py           # User, Tenant (SharedBase)
│   └── tenant.py           # Profile, SocialPost, Document (TenantBase)
├── schemas/                 # Pydantic Schemas (DTOs)
│   ├── shared.py
│   ├── profile.py
│   └── document.py
└── services/                # Business Logic Layer
    ├── profile_service.py
    ├── document_service.py
    └── tenant_service.py
```

---

## 🎨 Code Style Guidelines

### Import Order
```python
# 1. Standard library imports
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local imports (absolute paths, alphabetically)
from app.core.config import settings
from app.db.session import get_shared_db, get_tenant_db
from app.models.shared import User
from app.schemas.profile import ProfileCreate, ProfileResponse
```

### Naming Conventions
- **Files & Variables:** `snake_case` (e.g., `profile_service.py`, `user_id`)
- **Classes:** `PascalCase` (e.g., `ProfileService`, `User`, `ProfileCreate`)
- **Functions & Methods:** `snake_case` (e.g., `create_profile()`, `get_user_by_id()`)
- **Private Methods:** `_leading_underscore` (e.g., `_get_profile_by_user_id()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_LIMIT`)

### Type Hints
- ✅ **Always use type hints** for function parameters and return types
- Use modern Python 3.10+ syntax: `str | None` instead of `Optional[str]`
- Use `Annotated` for dependency injection types
```python
from typing import Annotated
from fastapi import Depends

SharedDB = Annotated[AsyncSession, Depends(get_shared_db)]
TenantDB = Annotated[AsyncSession, Depends(get_tenant_db)]

async def create_user(db: SharedDB, name: str) -> User:
    ...
```

### Async/Await Patterns
- **All database operations MUST be async**
- Use `async def` for all service methods that interact with database
- Always `await` async operations
```python
async def get_profile(self, profile_id: int) -> Profile | None:
    result = await self.tenant_db.execute(
        select(Profile).where(Profile.id == profile_id)
    )
    return result.scalar_one_or_none()
```

### Pydantic Schemas
- Inherit from `BaseModel` for all DTOs
- Use `from_attributes = True` in Config for ORM models
- Define separate schemas for Create, Update, and Response
```python
class ProfileBase(BaseModel):
    full_name: str
    phone: str | None = None

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

### SQLAlchemy Models
- Use `SharedBase` for shared database models (User, Tenant)
- Use `TenantBase` for tenant-specific models (Profile, Document)
- Always include `created_at` and `updated_at` timestamps
```python
from app.db.base import TenantBase
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class Profile(TenantBase):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🏗️ Architecture Patterns

### Multi-Tenant Strategy
1. **Shared Database:** Stores Users and Tenants metadata
2. **Tenant Database:** Each tenant has separate database for their data
3. **Routing:** Tenant ID passed via Path/Query/Header (`X-Tenant-ID`)

### Layered Architecture
```
FastAPI Endpoints → Services → SQLAlchemy Models → Database
```

### Service Pattern
```python
class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession | None = None):
        self.tenant_db = tenant_db
        self.shared_db = shared_db

    async def create_profile(self, data: ProfileCreate) -> Profile:
        # 1. Validation
        # 2. Business logic
        # 3. Database operations
        new_profile = Profile(**data.model_dump())
        self.tenant_db.add(new_profile)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)
        return new_profile
```

### Endpoint Pattern
```python
@router.post("/{tenant_id}/profiles", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    tenant_db: TenantDBPath,  # Injected via Depends
    shared_db: SharedDB,
    tenant_id: str = Path(..., description="ID của tenant"),
):
    service = ProfileService(tenant_db, shared_db)
    return await service.create_profile(profile_data)
```

---

## 🛡️ Error Handling

### HTTP Exceptions
```python
from fastapi import HTTPException, status

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Profile không tồn tại"
)

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User đã có profile"
)

# 500 Internal Server Error
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Lỗi khi tạo profile"
)
```

---

## 📝 Docstrings & Comments

- **Language:** Vietnamese for all docstrings and comments
- **Format:** Use triple quotes for docstrings
```python
def create_profile(self, data: ProfileCreate) -> Profile:
    """
    Tạo profile mới cho user.
    
    Args:
        data: Thông tin profile cần tạo
        
    Returns:
        Profile: Profile vừa được tạo
        
    Raises:
        HTTPException: Nếu user đã có profile hoặc user không tồn tại
    """
    ...
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
DEBUG=true
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_DB=shared_db
```

### Settings (app/core/config.py)
- Use Pydantic `BaseSettings` for configuration
- All settings loaded from environment variables

---

## ✅ Best Practices

1. **Always use dependency injection** for database sessions
2. **Commit after write operations:** `await db.commit()`
3. **Refresh after insert:** `await db.refresh(obj)` to get generated IDs
4. **Use transactions** for multi-step operations
5. **Validate tenant existence** before creating tenant-specific resources
6. **Use Path parameters** for tenant_id when it's the main resource identifier
7. **Close sessions properly** (handled by FastAPI Depends lifecycle)
8. **Log important operations** (especially in database_manager.py)
9. **Follow existing patterns** in similar endpoints/services

---

## 🚫 Common Pitfalls

1. ❌ Don't mix sync and async code
2. ❌ Don't forget to await async operations
3. ❌ Don't use SharedBase for tenant-specific models
4. ❌ Don't commit inside loops (batch operations instead)
5. ❌ Don't expose internal errors to API responses
6. ❌ Don't forget to add `from_attributes = True` for ORM response models

---

## 📚 Additional Resources

- **API Examples:** See `EXAMPLES.md` for curl and Python request examples
- **Business Logic:** See `quy-trinh.md` for profile creation workflows
- **Testing API:** See `bruno/README.md` for manual testing guide
- **Architecture:** See `GEMINI.md` for detailed project context
