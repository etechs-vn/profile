# Ví dụ sử dụng Multi-Tenant API

File này chứa các ví dụ về cách sử dụng API với shared database và tenant databases.

## Khởi động server

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

## 1. Shared Database - Quản lý Users và Tenants

### Tạo User mới

```bash
curl -X POST "http://localhost:8000/shared/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "name": "Nguyễn Văn A"
  }'
```

### Lấy danh sách Users

```bash
curl "http://localhost:8000/shared/users"
```

### Tạo Tenant mới

```bash
curl -X POST "http://localhost:8000/shared/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "name": "Công ty ABC",
    "status": "active"
  }'
```

### Lấy danh sách Tenants

```bash
curl "http://localhost:8000/shared/tenants"
```

## 2. Tenant Database - Sử dụng Path Parameter

### Tạo Profile cho tenant_001

```bash
curl -X POST "http://localhost:8000/tenants/tenant_001/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "address": "123 Đường ABC, Quận 1, TP.HCM",
    "bio": "Đây là bio của user",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

### Lấy danh sách Profiles của tenant_001

```bash
curl "http://localhost:8000/tenants/tenant_001/profiles"
```

### Lấy Profile kết hợp với User info

```bash
curl "http://localhost:8000/tenants/tenant_001/profiles/user/1"
```

### Tạo Document cho tenant_001

```bash
curl -X POST "http://localhost:8000/tenants/tenant_001/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tài liệu quan trọng",
    "content": "Nội dung tài liệu...",
    "file_path": "/documents/important.pdf"
  }'
```

### Lấy danh sách Documents của tenant_001

```bash
curl "http://localhost:8000/tenants/tenant_001/documents"
```

## 3. Tenant Database - Sử dụng Query Parameter

### Tạo Profile với query parameter

```bash
curl -X POST "http://localhost:8000/tenants/profiles?tenant_id=tenant_001" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789"
  }'
```

## 4. Tenant Database - Sử dụng HTTP Header

### Lấy Profiles với header X-Tenant-ID

```bash
curl "http://localhost:8000/tenants/profiles/me" \
  -H "X-Tenant-ID: tenant_001"
```

## 5. Ví dụ với nhiều Tenants

### Tạo dữ liệu cho tenant_002

```bash
# Tạo tenant_002
curl -X POST "http://localhost:8000/shared/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_002",
    "name": "Công ty XYZ",
    "status": "active"
  }'

# Tạo profile cho tenant_002
curl -X POST "http://localhost:8000/tenants/tenant_002/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "full_name": "Nguyễn Văn A (Tenant 2)",
    "phone": "0987654321"
  }'
```

Mỗi tenant có database riêng, nên dữ liệu của tenant_001 và tenant_002 hoàn toàn độc lập.

## 6. Sử dụng với Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Tạo user trong shared database
user_response = requests.post(
    f"{BASE_URL}/shared/users",
    json={
        "email": "user1@example.com",
        "name": "Nguyễn Văn A"
    }
)
user = user_response.json()
print(f"Created user: {user}")

# 2. Tạo tenant trong shared database
tenant_response = requests.post(
    f"{BASE_URL}/shared/tenants",
    json={
        "tenant_id": "tenant_001",
        "name": "Công ty ABC",
        "status": "active"
    }
)
tenant = tenant_response.json()
print(f"Created tenant: {tenant}")

# 3. Tạo profile trong tenant database
profile_response = requests.post(
    f"{BASE_URL}/tenants/tenant_001/profiles",
    json={
        "user_id": user["id"],
        "full_name": "Nguyễn Văn A",
        "phone": "0123456789",
        "address": "123 Đường ABC",
        "bio": "Đây là bio"
    }
)
profile = profile_response.json()
print(f"Created profile: {profile}")

# 4. Lấy profile kết hợp với user info
combined_response = requests.get(
    f"{BASE_URL}/tenants/tenant_001/profiles/user/{user['id']}"
)
combined = combined_response.json()
print(f"Combined data: {combined}")

# 5. Sử dụng header để lấy profiles
headers = {"X-Tenant-ID": "tenant_001"}
profiles_response = requests.get(
    f"{BASE_URL}/tenants/profiles/me",
    headers=headers
)
profiles = profiles_response.json()
print(f"Profiles: {profiles}")
```

## 7. Kiểm tra Database Files

Sau khi chạy các ví dụ trên, bạn sẽ thấy:

```
shared.db              # Shared database
tenants/
  ├── tenant_001.db   # Database riêng cho tenant_001
  └── tenant_002.db   # Database riêng cho tenant_002
```

## 8. Truy cập API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Lưu ý

1. **Shared Database**: Tất cả tenants đều truy cập cùng một shared database để lấy thông tin chung (users, tenants list, etc.)

2. **Tenant Databases**: Mỗi tenant có database riêng biệt, dữ liệu hoàn toàn độc lập:
   - `tenant_001` có profile riêng
   - `tenant_002` có profile riêng
   - Không thể truy cập dữ liệu của tenant khác

3. **Auto Creation**: Tenant database files được tạo tự động khi được sử dụng lần đầu tiên.

4. **Path vs Query vs Header**: 
   - Path parameter: `/tenants/{tenant_id}/profiles` - Rõ ràng, RESTful
   - Query parameter: `/tenants/profiles?tenant_id=xxx` - Linh hoạt
   - Header: `X-Tenant-ID: xxx` - Phù hợp cho authentication middleware
