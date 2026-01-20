# AGENTS.md - Developer Guidelines for Profile API

**Project:** FastAPI Multi-Tenant Backend | **Python:** 3.13+ | **Package Manager:** uv  
**Language:** Code in English, Docstrings/Comments in Vietnamese

---

## Quick Commands

```bash
# Setup
uv sync

# Development server
uv run uvicorn app.main:app --reload

# Linting & Formatting
uv run ruff format .              # Format code
uv run ruff check .               # Lint code
uv run ruff check --fix .         # Auto-fix issues
uv run mypy app/                  # Type checking

# Testing
uv run pytest                                              # All tests
uv run pytest tests/test_profile_service.py                # Single file
uv run pytest tests/test_profile_service.py::test_create   # Single test
uv run pytest -k "profile"                                 # Pattern match
uv run pytest --cov=app --cov-report=html                  # With coverage
```

---

## Project Structure

```
app/
├── api/
│   ├── deps.py              # DI types: SharedDB, TenantDBPath, TenantDBQuery
│   └── v1/endpoints/        # Endpoint handlers
├── core/config.py           # Settings (Pydantic BaseSettings)
├── db/
│   ├── base.py              # SharedBase & TenantBase declarative bases
│   ├── database_manager.py  # Multi-tenant engine manager
│   └── session.py           # Session factories
├── models/
│   ├── shared.py            # User, Tenant (SharedBase)
│   └── tenant.py            # Profile, SocialPost, Document (TenantBase)
├── schemas/                 # Pydantic DTOs (Create, Update, Response)
└── services/                # Business logic layer
```

---

## Code Style

### Import Order
```python
# 1. Standard library
from datetime import datetime
from typing import Annotated

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local (absolute paths, alphabetically)
from app.api.deps import SharedDB, TenantDBPath
from app.models.tenant import Profile
from app.schemas.profile import ProfileCreate
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Files & Variables | `snake_case` | `profile_service.py`, `user_id` |
| Classes | `PascalCase` | `ProfileService`, `ProfileCreate` |
| Functions/Methods | `snake_case` | `create_profile()` |
| Private Methods | `_underscore` | `_get_profile_by_user_id()` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES` |

### Type Hints
- **Always required** for function parameters and return types
- Use modern syntax: `str | None` (not `Optional[str]`)
- Use `Annotated` for dependency injection:
```python
SharedDB = Annotated[AsyncSession, Depends(get_shared_db)]
TenantDBPath = Annotated[AsyncSession, Depends(get_tenant_db_from_path)]
```

### Async/Await
- **All database operations MUST be async**
- Always `await` async operations
```python
async def get_profile(self, profile_id: int) -> Profile | None:
    result = await self.tenant_db.execute(
        select(Profile).where(Profile.id == profile_id)
    )
    return result.scalar_one_or_none()
```

---

## Architecture Patterns

### Multi-Tenant Strategy
- **SharedBase:** User, Tenant (metadata in shared_db)
- **TenantBase:** Profile, Document (data in tenant-specific db)
- **Routing:** Tenant ID via Path (`/{tenant_id}/`) or Header (`X-Tenant-ID`)

### Service Pattern
```python
class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession | None = None):
        self.tenant_db = tenant_db
        self.shared_db = shared_db

    async def create_profile(self, data: ProfileCreate) -> Profile:
        new_profile = Profile(**data.model_dump())
        self.tenant_db.add(new_profile)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_profile)  # Get generated ID
        return new_profile
```

### Endpoint Pattern
```python
@router.post("/{tenant_id}/profiles", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    tenant_db: TenantDBPath,
    shared_db: SharedDB,
    tenant_id: str = Path(...),
):
    service = ProfileService(tenant_db, shared_db)
    return await service.create_profile(profile_data)
```

---

## Error Handling

```python
from fastapi import HTTPException, status

raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile khong ton tai")
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User da co profile")
```

---

## Pydantic Schemas

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
        from_attributes = True  # Required for ORM models
```

---

## Critical Rules

1. **Always use dependency injection** for database sessions (`SharedDB`, `TenantDBPath`)
2. **Commit after writes:** `await db.commit()`
3. **Refresh after insert:** `await db.refresh(obj)` to get generated IDs
4. **Use SharedBase** for shared models, **TenantBase** for tenant models
5. **Validate tenant existence** before creating tenant-specific resources
6. **Use `from_attributes = True`** in Pydantic response models

## Common Pitfalls

- Don't mix sync and async code
- Don't forget to `await` async operations
- Don't commit inside loops (batch instead)
- Don't use `SharedBase` for tenant-specific models
- Don't expose internal errors to API responses
