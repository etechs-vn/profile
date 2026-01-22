# API Endpoints - Profile API

## Project Overview
- **Project:** FastAPI Multi-Tenant Backend
- **Python:** 3.13+
- **Framework:** FastAPI, SQLAlchemy Async, Pydantic V2
- **Architecture:** Shared DB + Tenant DBs (Multi-Tenancy)

---

## Tổng quan thống kê

| Module | API Endpoints | Status |
|--------|--------------|--------|
| System | 1 | ✅ Hoàn thành |
| Tenant | 6 | ✅ Hoàn thành |
| Profile | 8 | ✅ Hoàn thành |
| Social | 19 | ✅ Hoàn thành |
| Wallet | 9 | ✅ Hoàn thành |
| Document | 3 | ✅ Hoàn thành |
| **TỔNG CỘNG** | **46** | **✅ Hoàn thành** |

---

## 1. System Module

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{tenant_id}/db-check` | Kiểm tra kết nối Tenant & Shared DB |

---

## 2. Tenant Module (Shared Database)

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shared/users` | Tạo user mới |
| GET | `/shared/users` | Lấy danh sách tất cả users |
| GET | `/shared/users/{user_id}` | Lấy thông tin user theo ID |

### Tenants
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shared/tenants` | Tạo tenant mới + provision database |
| GET | `/shared/tenants` | Lấy danh sách tất cả tenants |
| GET | `/shared/tenants/{tenant_id}` | Lấy thông tin tenant theo ID |

---

## 3. Profile Module

### Main Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/profile` | Tạo profile mới |
| GET | `/tenants/{tenant_id}/users/{user_id}/profile` | Lấy profile theo user_id |
| GET | `/tenants/{tenant_id}/profiles/{profile_id}` | Lấy profile theo profile_id (UUID) |
| PUT | `/tenants/{tenant_id}/profiles/{profile_id}` | Cập nhật profile |
| GET | `/tenants/{tenant_id}/profiles` | Lấy danh sách profiles (có pagination) |

### Sub-resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/profiles/{profile_id}/educations` | Thêm học vấn |
| POST | `/tenants/{tenant_id}/profiles/{profile_id}/documents` | Thêm giấy tờ tùy thân |
| POST | `/tenants/{tenant_id}/profiles/{profile_id}/interests` | Thêm sở thích |

---

## 4. Social Module

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/posts` | Tạo bài viết |
| GET | `/tenants/{tenant_id}/users/{user_id}/social/feed` | Lấy feed (timeline) |
| GET | `/tenants/{tenant_id}/social/posts/{post_id}` | Lấy chi tiết bài viết |
| DELETE | `/tenants/{tenant_id}/users/{user_id}/social/posts/{post_id}` | Xóa bài viết |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/posts/{post_id}/comments` | Bình luận bài viết |
| GET | `/tenants/{tenant_id}/social/posts/{post_id}/comments` | Lấy danh sách comments |

### Interactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/posts/{post_id}/like` | Like bài viết |

### Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/groups` | Tạo nhóm |
| GET | `/tenants/{tenant_id}/users/{user_id}/social/groups` | Lấy danh sách nhóm của user |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/messages` | Gửi tin nhắn (private hoặc group) |

### Polls
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/groups/{group_id}/polls` | Tạo bình chọn trong nhóm |
| GET | `/tenants/{tenant_id}/social/groups/{group_id}/polls` | Lấy danh sách polls của nhóm |
| GET | `/tenants/{tenant_id}/social/polls/{poll_id}` | Lấy chi tiết poll |
| POST | `/tenants/{tenant_id}/users/{user_id}/social/polls/{poll_id}/vote` | Bình chọn |
| POST | `/tenants/{tenant_id}/users/{user_id}/social/polls/{poll_id}/close` | Đóng bình chọn |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/social/groups/{group_id}/appointments` | Tạo cuộc hẹn |
| GET | `/tenants/{tenant_id}/social/groups/{group_id}/appointments` | Lấy danh sách appointments của nhóm |
| GET | `/tenants/{tenant_id}/social/appointments/{appointment_id}` | Lấy chi tiết appointment |
| PUT | `/tenants/{tenant_id}/users/{user_id}/social/appointments/{appointment_id}` | Cập nhật cuộc hẹn |
| DELETE | `/tenants/{tenant_id}/users/{user_id}/social/appointments/{appointment_id}` | Xóa cuộc hẹn |

---

## 5. Wallet Module

### Main Wallet
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/users/{user_id}/wallet` | Tạo ví mới |
| GET | `/tenants/{tenant_id}/users/{user_id}/wallet` | Lấy thông tin ví |
| POST | `/tenants/{tenant_id}/users/{user_id}/wallet/topup` | Nạp tiền vào ví |
| POST | `/tenants/{tenant_id}/users/{user_id}/wallet/transfer` | Chuyển tiền sang profile khác |

### Assets & Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tenants/{tenant_id}/users/{user_id}/wallet/assets` | Lấy danh sách tài sản |
| POST | `/tenants/{tenant_id}/users/{user_id}/wallet/assets` | Thêm tài sản vào ví |
| GET | `/tenants/{tenant_id}/users/{user_id}/wallet/transactions` | Lấy lịch sử giao dịch |

### Exchange Rates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tenants/{tenant_id}/wallet/rates` | Lấy danh sách tỷ lệ quy đổi |
| POST | `/tenants/{tenant_id}/wallet/rates` | Tạo tỷ lệ quy đổi mới |

---

## 6. Document Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants/{tenant_id}/documents` | Tạo document mới |
| GET | `/tenants/{tenant_id}/documents` | Lấy danh sách documents |
| GET | `/tenants/{tenant_id}/documents/{document_id}` | Lấy document theo ID |

---

## Các đặc điểm chính

- ✅ **Multi-tenancy**: Mỗi tenant có database riêng
- ✅ **Async/Await**: SQLAlchemy Async cho tất cả DB operations
- ✅ **Service Layer Pattern**: Tách biệt business logic
- ✅ **Dependency Injection**: Clean DI pattern
- ✅ **Pydantic V2**: Validation & serialization
- ✅ **Database Manager**: Dynamic provisioning + LRU cache
- ✅ **OpenAPI Documentation**: Tự động生成 từ FastAPI

---

*Last updated: January 22, 2026*
