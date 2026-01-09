# Bruno API Collection - Profile API

Collection này chứa các API requests để test Profile API với kiến trúc Multi-Tenant.

## Cài đặt Bruno

1. Tải Bruno từ: https://www.usebruno.com/
2. Cài đặt và mở Bruno
3. Mở collection: File → Open Collection → Chọn thư mục `bruno`

## Cấu trúc Collection

```
bruno/
├── bruno.json              # Collection config
├── environments/           # Environment variables
│   ├── local.bru          # Local development environment
│   └── production.bru     # Production environment
├── Shared Database/         # Shared database endpoints
│   ├── Get Root.bru
│   ├── Users/
│   │   ├── Create User.bru
│   │   ├── Get All Users.bru
│   │   └── Get User By ID.bru
│   └── Tenants/
│       ├── Create Tenant.bru
│       ├── Get All Tenants.bru
│       └── Get Tenant By ID.bru
└── Tenant Database/        # Tenant database endpoints
    ├── Profiles/
    │   ├── Create Profile (Path).bru
    │   ├── Get All Profiles (Path).bru
    │   ├── Get Profile By ID (Path).bru
    │   ├── Get Profile With User (Path).bru
    │   ├── Create Profile (Query).bru
    │   └── Get Profiles (Header).bru
    └── Documents/
        ├── Create Document.bru
        ├── Get All Documents.bru
        └── Get Document By ID.bru
```

## Environment Variables

Bruno sử dụng thư mục `environments/` để lưu các biến môi trường. Mỗi file `.bru` trong thư mục này đại diện cho một environment.

### Cách chọn Environment trong Bruno:

1. Mở Bruno và load collection
2. Ở góc trên bên phải, click vào dropdown "No Environment"
3. Chọn environment bạn muốn sử dụng (ví dụ: "local")

### Các Environments có sẵn:

- **local** (`environments/local.bru`): 
  - `base_url`: http://localhost:8000
  - `tenant_id`: tenant_001
  - `user_id`: 1
  - `profile_id`: 1
  - `document_id`: 1

- **production** (`environments/production.bru`):
  - `base_url`: https://api.example.com
  - Các biến khác tương tự local

### Chỉnh sửa Environment Variables:

1. **Trong Bruno GUI**: 
   - Click vào environment selector → Configure
   - Chọn environment → Add/Edit variables

2. **Trong file**:
   - Mở file `.bru` trong thư mục `environments/`
   - Chỉnh sửa trực tiếp và save
   - Bruno sẽ tự động reload

## Cách sử dụng

### 1. Khởi động API Server

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

### 2. Test Flow đề xuất

#### Bước 1: Tạo dữ liệu trong Shared Database

1. **Create User** - Tạo user mới
   - Endpoint: `POST /shared/users`
   - Lưu `id` từ response để dùng cho các request sau

2. **Create Tenant** - Tạo tenant mới
   - Endpoint: `POST /shared/tenants`
   - Lưu `tenant_id` từ response

#### Bước 2: Tạo dữ liệu trong Tenant Database

1. **Create Profile (Path)** - Tạo profile cho tenant
   - Endpoint: `POST /tenants/{tenant_id}/profiles`
   - Sử dụng `user_id` từ bước 1
   - Lưu `id` từ response

2. **Create Document** - Tạo document cho tenant
   - Endpoint: `POST /tenants/{tenant_id}/documents`

#### Bước 3: Test các cách truy cập khác nhau

1. **Get Profiles (Header)** - Lấy profiles qua header
   - Endpoint: `GET /tenants/profiles/me`
   - Header: `X-Tenant-ID: tenant_001`

2. **Create Profile (Query)** - Tạo profile qua query parameter
   - Endpoint: `POST /tenants/profiles?tenant_id=tenant_001`

## Các loại Endpoints

### Shared Database Endpoints

- **Users**: Quản lý users chung
- **Tenants**: Quản lý tenants

### Tenant Database Endpoints

Có 3 cách truy cập tenant database:

1. **Path Parameter**: `/tenants/{tenant_id}/...`
   - Rõ ràng, RESTful
   - Ví dụ: `GET /tenants/tenant_001/profiles`

2. **Query Parameter**: `/tenants/...?tenant_id=xxx`
   - Linh hoạt
   - Ví dụ: `POST /tenants/profiles?tenant_id=tenant_001`

3. **HTTP Header**: Header `X-Tenant-ID`
   - Phù hợp cho authentication middleware
   - Ví dụ: `GET /tenants/profiles/me` với header `X-Tenant-ID: tenant_001`

## Tests

Mỗi request đều có tests để validate response:
- Status code validation
- Response structure validation
- Data validation

Bạn có thể chạy tests trong Bruno để kiểm tra response.

## Lưu ý

1. **Chọn Environment**: Đảm bảo đã chọn đúng environment (local/production) trước khi chạy requests
2. **Thứ tự thực hiện**: Nên tạo User và Tenant trước khi tạo Profile
3. **Tenant ID**: Đảm bảo `tenant_id` trong environment khớp với tenant đã tạo
4. **User ID**: Đảm bảo `user_id` trong environment khớp với user đã tạo
5. **Auto Creation**: Tenant database và tables sẽ được tạo tự động khi sử dụng lần đầu

## Troubleshooting

### Lỗi "no such table"
- Tenant database chưa được sử dụng lần đầu
- Tables sẽ được tạo tự động khi request đầu tiên được gửi

### Lỗi "User không tồn tại"
- Đảm bảo đã tạo user trong shared database trước
- Kiểm tra `user_id` trong environment đang sử dụng

### Lỗi "Tenant không tồn tại"
- Đảm bảo đã tạo tenant trong shared database trước
- Kiểm tra `tenant_id` trong environment đang sử dụng

### Environment variables không được load
- Đảm bảo đã chọn environment trong Bruno (dropdown ở góc trên bên phải)
- Kiểm tra file `.bru` trong thư mục `environments/` có đúng format không
- Format đúng: `vars { key: value }`
- Reload collection nếu cần: File → Reload Collection
