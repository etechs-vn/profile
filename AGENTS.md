# AGENTS.md - Developer Guidelines for Profile API

**Project:** FastAPI Multi-Tenant Backend | **Python:** 3.13+ | **Package Manager:** uv
**Language:** Code in English | **Docstrings & Comments:** Vietnamese (Tiếng Việt)

---

## 1. Development Environment

### Setup & Run
```bash
# Install dependencies
uv sync

# Run development server (Hot Reload)
uv run uvicorn app.main:app --reload

# Database Migrations (Alembic)
uv run alembic upgrade head
```

### Verification Commands
**Always run these before requesting a review or finishing a task.**

```bash
# Format & Lint (Auto-fix)
uv run ruff check --fix . && uv run ruff format .

# Type Checking
# Note: Ensure mypy is installed (uv add --dev mypy) if this command fails
uv run mypy app/

# Run All Tests
uv run pytest

# Run Specific Test (Recommended for TDD)
# Syntax: uv run pytest path/to/file.py::function_name
uv run pytest tests/test_profile_service.py::test_create_profile
```

---

## 2. Code Style & Conventions

### Language Rules
- **Code:** Variables, functions, classes, and logs must be in **English**.
- **Documentation:** All docstrings and inline comments must be in **Vietnamese**.
  - **Exception:** Test files may use English docstrings, but consistency is preferred.
  ```python
  def get_user(user_id: int):
      """Lấy thông tin người dùng theo ID."""
      # Kiểm tra cache trước khi gọi DB
      pass
  ```

### Imports
Order is strict. Use `ruff format` to enforce, but manually:
1. **Standard Library:** `typing`, `datetime`, `uuid`
2. **Third-Party:** `fastapi`, `sqlalchemy`, `pydantic`
3. **Local Application:** Absolute imports only (`app.core...`)
   ```python
   from typing import Annotated
   
   from fastapi import Depends
   from sqlalchemy import select
   
   from app.api.deps import SharedDB
   from app.models.tenant import Profile
   ```

### Naming
- **Files/Vars/Funcs:** `snake_case` (`profile_service.py`, `user_id`)
- **Classes/Types:** `PascalCase` (`ProfileService`, `ProfileCreate`)
- **Constants:** `UPPER_SNAKE_CASE` (`MAX_RETRIES`)
- **Private:** `_underscore_prefix` (`_helper_function`)

### Typing (Python 3.13+)
- Use `|` for Union: `str | None` instead of `Optional[str]`.
- Use `list[str]` instead of `List[str]`.
- **Dependency Injection:** Use `Annotated` pattern in `app/api/deps.py`.
  ```python
  # Correct
  async def create(db: Annotated[AsyncSession, Depends(get_db)])
  ```

### Error Handling
- **Exceptions:** Raise `HTTPException` with Vietnamese `detail`.
  ```python
  raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
  ```
- **Logging:** Use standard logging or `structlog` (if available). Logs in English.

---

## 3. Architecture & Patterns

### Multi-Tenancy Strategy
- **Shared DB:** Stores `User`, `Tenant` metadata (`SharedBase`).
- **Tenant DB:** Stores isolated data like `Profile`, `Document` (`TenantBase`).
- **Resolution:** Tenant determined via URL path `/{tenant_id}/...` or Header `X-Tenant-ID`.
- **Testing:** Tests use `sqlite+aiosqlite:///:memory:` and file-based tenant DBs (managed by `conftest.py`).

### Service Layer Pattern
Business logic resides in `app/services/`, not endpoints. Services are injected via `Depends`.
```python
class ProfileService:
    def __init__(self, tenant_db: AsyncSession, shared_db: AsyncSession | None = None):
        self.tenant_db = tenant_db
        # ...

    async def create(self, data: ProfileCreate) -> Profile:
        # Logic here
        pass
```

### Database Operations (SQLAlchemy Async)
- **Always** `await` database calls.
- **Commit:** Explicitly `await db.commit()` after writes.
- **Refresh:** `await db.refresh(obj)` to populate DB-generated fields (IDs, timestamps).
- **Queries:** Use `await db.execute(select(Model)...)` then `.scalars().all()` or `.scalar_one_or_none()`.

### Pydantic V2
- Use `model_dump()` instead of `dict()`.
- Use `model_validate()` instead of `from_orm()`.
- Config: `model_config = ConfigDict(from_attributes=True)` (formerly `orm_mode`).

---

## 4. Testing Guidelines

- **Fixtures:** heavily used in `tests/conftest.py`.
- **`db_manager`**: Creates fresh schema per test.
- **`sample_tenant`**: Provides a ready-to-use tenant in Shared DB.
- **Mocking:** Avoid mocking DB sessions; use the provided `sqlite` fixtures which emulate the real DB structure.
- **Async Tests:** Use `@pytest.mark.asyncio`.

---

## 5. Critical Rules for Agents

1. **No Silent Failures:** Never use bare `try/except`. Log the error or raise `HTTPException`.
2. **Path Safety:** Always validate `tenant_id` before performing tenant-specific operations.
3. **Async Discipline:** Never use blocking I/O (like `time.sleep` or synchronous `requests`) in async routes.
4. **Secrets:** Never commit `.env` files or hardcode credentials.
5. **Modification:** When editing `AGENTS.md`, preserve these rules unless explicitly instructed to change logic.
6. **No Reverts:** Do not revert code changes unless explicitly requested by the user.
