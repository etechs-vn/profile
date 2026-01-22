# Đánh Giá Thiết Kế Database Cá Thể (Profile & Social)

Tài liệu này đánh giá cấu trúc cơ sở dữ liệu dựa trên đặc tả `bangmota-cathe.md` và implementation SQLAlchemy ORM tương ứng.

## 1. Tổng Quan
Thiết kế hướng tới mô hình **Multi-tenant** (cơ sở dữ liệu riêng cho từng cá thể/tổ chức) hoặc **Distributed System**, tách biệt rõ ràng giữa thông tin định danh (Profile), tài chính (Wallet) và tương tác xã hội (Social).

*   **Kiểu ID:** Sử dụng `char` (String) cho toàn bộ Khóa chính (PK) thay vì Integer tự tăng.
*   **Phong cách:** Modular, chia thành các nhóm chức năng rõ ràng.

---

## 2. Phân Tích Chi Tiết

### 2.1. Module Profile (Hồ sơ & Định danh)
**Cấu trúc:** `profile`, `education`, `identity_documents`, `user_interests`.

*   **Ưu điểm:**
    *   **Lịch sử dữ liệu:** Trường `valid_from` và `valid_to` trong bảng `profile` cho thấy thiết kế hỗ trợ lưu trữ lịch sử thay đổi (SCD - Slowly Changing Dimension Type 2). Điều này rất tốt cho việc truy vết thông tin người dùng theo thời gian.
    *   **ID phi tập trung:** Việc sử dụng `char` (String) cho `profile_id` giúp dễ dàng sharding (phân mảnh) database hoặc migration dữ liệu mà không bị xung đột ID như kiểu số nguyên.
*   **Hạn chế:**
    *   **Thiếu liên kết Authentication:** Không thấy bảng `User` hoặc trường liên kết đến hệ thống đăng nhập (Auth). Giả định việc mapping giữa Account và Profile được xử lý ở tầng Gateway hoặc Shared DB.
    *   **Dữ liệu JSON:** Các thông tin phức tạp (metadata) đang lưu dạng tham chiếu `metadata_id` text. Điều này linh hoạt nhưng sẽ khó query/filter trực tiếp nếu không có bảng metadata đi kèm.

### 2.2. Module Wallet (Ví & Tài sản số)
**Cấu trúc:** `wallets`, `wallet_assets`, `wallet_transactions`, `asset_rates_to_credit`.

*   **Ưu điểm:**
    *   **Thiết kế linh hoạt:** Hỗ trợ đa dạng loại tài sản (`asset_type`) thay vì fix cứng cột tiền tệ.
    *   **Audit tốt:** Bảng `wallet_transactions` ghi lại lịch sử giao dịch chi tiết (direction, ref_type, ref_id) giúp đối soát dễ dàng.
*   **Rủi ro:**
    *   **Dư thừa dữ liệu (Redundancy):** Bảng `wallets` lưu số dư tổng (`ets`) và `wallet_assets` lưu số lượng (`amount`), trong khi `wallet_transactions` cũng lưu lịch sử biến động.
    *   **Rủi ro bất đồng bộ:** Nếu logic ứng dụng không chuẩn (quên update bảng tổng khi insert transaction), số dư sẽ bị sai lệch. Cần đảm bảo tính toàn vẹn (ACID) cực cao ở tầng Application hoặc Database Triggers.

### 2.3. Module Social (Mạng xã hội)
**Cấu trúc:** `posts`, `comments`, `groups`, `messages`, `polls`...

*   **Vấn đề Nghiêm Trọng (Critical Issue):**
    *   **Mất liên kết chủ sở hữu (Ownership):** Bảng `posts` và `comments` trong đặc tả **không có** `profile_id`.
        *   *Hệ quả:* Không thể biết ai là người tạo ra bài viết hay bình luận đó nếu chỉ nhìn vào bảng `posts`/`comments`.
        *   *Giả định hiện tại:* Việc liên kết có thể đang dựa vào bảng trung gian hoặc bảng log, nhưng đây là thiết kế **Anti-pattern** đối với mô hình quan hệ (Relational DB). Việc query "Lấy tất cả bài viết của user A" sẽ cực kỳ tốn kém và phức tạp.
    *   **Bảng `comment_post` gây khó hiểu:** Bảng này chứa `post_id`, `comment_id`, `profile_id`. Nếu đây là bảng để liên kết comment vào post, thì việc tách rời làm tăng độ phức tạp join bảng không cần thiết.

*   **Ưu điểm:**
    *   **Tương tác đa hình:** `post_interactions` và `comment_interactions` tách biệt, dễ mở rộng thêm các loại action mới (ngoài like/share) mà không cần sửa cấu trúc bảng chính.
    *   **Messaging:** Thiết kế `messages` gộp chung cá nhân và nhóm (dùng `msg_scope`) là cách tiếp cận gọn gàng, giảm số lượng bảng.

---

## 3. Đánh Giá Chung

| Tiêu chí | Điểm | Nhận xét |
| :--- | :---: | :--- |
| **Tính mở rộng (Scalability)** | 8/10 | Sử dụng String ID tốt cho phân tán. Thiết kế tách module rõ ràng. |
| **Tính toàn vẹn (Integrity)** | 6/10 | Thiếu FK quan trọng trong module Social (`posts`, `comments`). Rủi ro dữ liệu ví bị lệch. |
| **Hiệu năng (Performance)** | 7/10 | Tốt cho ghi (Write), nhưng Query (Read) module Social sẽ chậm do phải Join nhiều bảng trung gian. |
| **Tính linh hoạt (Flexibility)** | 9/10 | Hỗ trợ metadata, đa loại tài sản, đa loại giấy tờ tùy thân. |

---

## 4. Đề Xuất Cải Thiện (Recommendations)

Để đảm bảo hệ thống vận hành ổn định và chuẩn hóa, đề xuất điều chỉnh các điểm sau:

1.  **Sửa lỗi thiết kế Social (Quan trọng nhất):**
    *   Thêm cột `profile_id` (FK) vào bảng `posts` và `comments`. Bài viết/bình luận phải luôn thuộc về một người dùng cụ thể.
    *   Bảng `comment_post` nên được xem xét lại. Thông thường `comments` nên có `post_id` trực tiếp.

2.  **Ràng buộc Ví điện tử:**
    *   Cân nhắc bỏ lưu trữ số dư cứng trong `wallets` nếu không cần hiệu năng đọc cực cao, thay vào đó tính toán từ `wallet_transactions`.
    *   Hoặc: Dùng Database Trigger để tự động cập nhật số dư khi có Transaction mới để tránh lỗi logic code.

3.  **Chuẩn hóa Metadata:**
    *   Nếu `metadata_id` trỏ đến một kho NoSQL (như MongoDB) hoặc bảng JSONB, cần ghi rõ cơ chế liên kết để đội phát triển nắm được.

4.  **Đặt tên:**
    *   Cột `ets` trong bảng `wallets` nên đặt tên rõ nghĩa hơn (ví dụ: `credit_balance` hoặc `primary_balance`) nếu nó là đơn vị tiền tệ chính.

---
*Người đánh giá: AI Assistant - Dựa trên phiên bản đặc tả ngày 22/01/2026.*
