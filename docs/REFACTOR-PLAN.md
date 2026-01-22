# Kế hoạch refactoring User-Profile linkage

## Vấn đề
- Spec hiện tại (`bangmota-cathe.md`) KHÔNG có `user_id` trong bảng `profile`
- Nhưng thực tế: User (Shared DB) → tạo Tenant DB → Profile thuộc về User đó
- Cần cơ chế link giữa User (global) và Profile (tenant)

## Giải pháp đề xuất

### Option A: Thêm `user_id` vào Profile (Khuyên nghị)
- Thêm cột `user_id` (FK → shared.users.id) vào bảng `profile`
- Mỗi user chỉ có 1 profile duy nhất per tenant
- Endpoint: `/{tenant_id}/users/{user_id}/...`

**Ưu điểm:**
- Rõ ràng quan hệ 1-1
- Dễ truy cập profile qua user_id

**Nhược điểm:**
- Cần cập nhật spec

### Option B: Thêm `email` vào Profile
- Thêm cột `email` (varchar) vào bảng `profile`
- Link bằng cách so sánh email với user.email

**Ưu điểm:**
- Không phụ thuộc FK xuyên database

**Nhược điểm:**
- Email có thể thay đổi
- Không có ràng buộc DB

### Option C: Bổ sung table `user_profile_mapping` (Trung gian)
- Table có: `id`, `user_id`, `tenant_id`, `profile_id`
- Profile trong tenant KHÔNG có user_id/email
- Mapping nằm ở Shared DB

**Ưu điểm:**
- Giữ nguyên spec Profile
- Flexible mapping (1 user → N profiles)

**Nhược điểm:**
- Thêm join table
- Phải query mapping trước

## Đề xuất cuối cùng: **Option A**

### Lý do:
1. Đơn giản, rõ ràng
2. Pattern `/{tenant_id}/users/{user_id}/...` phù hợp
3. Code hiện tại đã implement sẵn, chỉ cần:
   - Cập nhật spec
   - Cập nhật migration (đã có field, chỉ cần xác nhận)
   - Bỏ comment "tạm thời" trong code

### Steps:
1. Cập nhật spec `bangmota-cathe.md`: Thêm `user_id` vào profile
2. Xác nhận model `Profile` đã có `user_id` field
3. Xác nhận migrations đã create field
4. Document kiến trúc rõ ràng hơn
