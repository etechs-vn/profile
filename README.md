# Profile Service (Multi-Tenant)

## Setup

```bash
uv sync
```

## Database Migrations (Alembic)

Dự án sử dụng Alembic để quản lý migrations cho cả Shared DB và Tenant DBs.

### Shared Database

1. **Tạo migration mới:**
   ```bash
   PYTHONPATH=. uv run alembic -c alembic.ini -n shared revision --autogenerate -m "description"
   ```

2. **Apply migrations:**
   ```bash
   PYTHONPATH=. uv run alembic -c alembic.ini -n shared upgrade head
   ```

### Tenant Databases

1. **Tạo migration mới:**
   Chỉ định `tenant_id` của một tenant mẫu để generate script.
   ```bash
   PYTHONPATH=. uv run alembic -c alembic.ini -n tenant -x tenant_id=dev_tenant revision --autogenerate -m "description"
   ```

2. **Apply cho MỘT tenant:**
   ```bash
   PYTHONPATH=. uv run alembic -c alembic.ini -n tenant -x tenant_id=dev_tenant upgrade head
   ```

3. **Apply cho TẤT CẢ tenants:**
   ```bash
   PYTHONPATH=. uv run alembic -c alembic.ini -n tenant upgrade head
   ```

### Development Tools

- Tạo dữ liệu mẫu (Shared DB + 1 Tenant):
  ```bash
  uv run python scripts/init_dev_data.py
  ```
