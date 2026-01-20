# Hướng dẫn Database Migration với Alembic

Tài liệu này hướng dẫn cách quản lý và chạy migration cho database trong dự án Profile API (Multi-tenant Architecture).

## 1. Tổng quan

Dự án sử dụng kiến trúc Multi-tenant với hai loại database tách biệt:
1.  **Shared Database (`shared`)**: Chứa các bảng dùng chung (User, Tenant mapping...). Metadata nằm trong `app.models.shared.SharedBase`.
2.  **Tenant Databases (`tenant`)**: Chứa dữ liệu riêng của từng khách hàng (Profile, Document...). Metadata nằm trong `app.models.tenant.TenantBase`.

Do đó, Alembic được cấu hình để quản lý hai luồng migration riêng biệt thông qua tham số `--name`.

## 2. Chuẩn bị

Đảm bảo bạn đã cài đặt đầy đủ dependencies:

```bash
uv sync
```

Kiểm tra cấu hình trong `alembic.ini`. Bạn sẽ thấy hai section `[shared]` và `[tenant]`.

## 3. Quy trình Migration

### A. Shared Database (User, Tenant...)

Áp dụng cho các thay đổi trong `app/models/shared.py`.

**1. Tạo Migration Script mới:**

Tự động tạo script dựa trên thay đổi trong code:

```bash
uv run alembic --name shared revision --autogenerate -m "mota_ngan_gon_thay_doi"
```

*Lưu ý: Script sẽ được tạo trong thư mục `migrations/shared/versions/`.*

**2. Chạy Migration (Upgrade):**

Cập nhật Shared Database lên phiên bản mới nhất:

```bash
uv run alembic --name shared upgrade head
```

### B. Tenant Databases (Profile, Document...)

Áp dụng cho các thay đổi trong `app/models/tenant.py`.

**1. Tạo Migration Script mới:**

> **Quan trọng:** Để tạo migration cho tenant, hệ thống cần kết nối đến ít nhất một tenant database đang tồn tại để so sánh schema.

Nếu bạn chưa có tenant nào, hãy tạo một tenant mẫu trước (qua API hoặc script seed). Sau đó chạy:

```bash
uv run alembic --name tenant revision --autogenerate -m "mota_thay_doi_tenant"
```

Nếu muốn chỉ định một tenant cụ thể để dùng làm mẫu so sánh (thay vì để hệ thống tự chọn):

```bash
uv run alembic --name tenant revision --autogenerate -m "mota" -x tenant_id=<tenant_id_mau>
```

*Lưu ý: Script sẽ được tạo trong thư mục `migrations/tenant/versions/`.*

**2. Chạy Migration (Upgrade):**

**Cách 1: Cập nhật TẤT CẢ Tenant (Khuyên dùng)**

Lệnh này sẽ lấy danh sách tenant từ Shared Database và lần lượt chạy migration cho từng tenant:

```bash
uv run alembic --name tenant upgrade head
```

**Cách 2: Cập nhật một Tenant cụ thể**

Dùng khi muốn test migration trên một tenant trước hoặc fix lỗi cho một tenant:

```bash
uv run alembic --name tenant upgrade head -x tenant_id=<target_tenant_id>
```

## 4. Các lệnh hữu ích khác

### Xem lịch sử migration

Xem lịch sử của Shared DB:
```bash
uv run alembic --name shared history
```

Xem lịch sử của Tenant DB (lưu ý tenant migration history giống nhau về mặt code, nhưng trạng thái áp dụng nằm trong từng DB):
```bash
uv run alembic --name tenant history
```

### Downgrade (Rollback)

Quay lại phiên bản trước đó (lùi 1 bước):

*   **Shared:**
    ```bash
    uv run alembic --name shared downgrade -1
    ```

*   **Tenant (Tất cả):**
    ```bash
    uv run alembic --name tenant downgrade -1
    ```

## 5. Lưu ý quan trọng

1.  **Review file migration:** Luôn luôn mở file migration (`.py`) vừa được tạo ra để kiểm tra xem Alembic có sinh đúng code không. Đôi khi `autogenerate` không phát hiện được việc đổi tên cột hoặc thay đổi kiểu dữ liệu phức tạp.
2.  **Async:** Dự án sử dụng `asyncpg` / `aiosqlite`. File `env.py` đã được cấu hình để chạy migration trong môi trường async. Không sửa đổi logic core trong `env.py` trừ khi bạn hiểu rõ về `asyncio` loop.
3.  **Lỗi "No tenants found":** Khi chạy lệnh `alembic --name tenant ...`, nếu gặp lỗi này nghĩa là Shared Database chưa có dữ liệu tenant nào. Bạn cần tạo ít nhất một tenant trong bảng `tenants` của Shared DB.

## 6. Cấu trúc thư mục

```
migrations/
├── shared/
│   ├── env.py          # Cấu hình môi trường cho Shared DB
│   └── versions/       # Các file revision của Shared
├── tenant/
│   ├── env.py          # Cấu hình môi trường cho Tenant DB (có logic loop qua các tenant)
│   └── versions/       # Các file revision của Tenant
└── script.py.mako      # Template mẫu
```
