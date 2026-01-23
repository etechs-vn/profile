# Bảng mô tả cá thể

Quy ước các bảng dữ liệu và thuộc tính cho hệ thống hồ sơ (profile) và các thực thể liên quan.

## Profile

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| profile_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh hồ sơ | – |
| nickname | char | – | – | – | Bí danh | – |
| valid_from | datetime | – | – | – | Thông tin hiệu lực từ ngày | – |
| valid_to | datetime | – | – | – | Thông tin hết hiệu lực từ ngày | – |
| dob | date | – | – | – | Ngày sinh | – |
| gender | boolean | – | – | 1 = Nam, 0 = Nữ | Giới tính | – |
| address | text | – | – | – | Địa chỉ | – |
| avatar_url | text | – | – | – | Ảnh đại diện (object storage) | – |
| bio | text | – | – | – | Giới thiệu ngắn | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Education

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| education_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh học vấn | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| education_level | varchar | – | – | Cấp 1/2/3/ĐH… | Cấp học | – |
| institution_name | text | – | – | – | Tên trường/cơ sở | – |
| start_date | datetime | – | – | – | Bắt đầu | – |
| end_date | datetime | – | end_date IS NULL OR start_date IS NULL OR end_date >= start_date | – | Kết thúc | – |
| is_current | boolean | – | – | 1 = đang học, 0 = nghỉ | Trạng thái | – |
| credential_type | varchar | – | – | – | Bằng cấp/chứng chỉ | – |
| credential_title | text | – | – | – | Tên bằng (THPT/cử nhân/B2/IELTS/MOS…) | – |
| issuing_organization | text | – | – | – | Đơn vị cấp | – |
| credential_ref | text | – | – | – | Số hiệu/mã tra cứu | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Identity Documents

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| identity_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh giấy tờ | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| document_type | text | – | – | – | Loại giấy tờ (CCCD/thẻ HS/BHXH/…) | – |
| document_number | text | – | – | – | Số giấy tờ | – |
| issued_date | datetime | – | – | – | Ngày cấp | – |
| expiry_date | datetime | – | – | – | Ngày hết hạn | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Wallets

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| wallets_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh ví | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| ETS | numeric | (16,2) | – | – | Số dư credit | – |
| metadata_id | text | – | – | – | Mô tả ví | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Wallet Assets

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| asset_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh tài sản | – |
| wallet_id | char | – | FK → wallets | – | Liên kết ví | – |
| asset_type | text | – | – | Coin/token/huy hiệu/thành tích/chứng nhận | Loại tài sản số | – |
| asset_code | text | – | – | – | Mã tài sản | – |
| amount | numeric | (16,2) | – | – | Số lượng | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Asset Rates To Credit

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| rate_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh quy đổi | – |
| from_asset_type | text | – | – | Quy đổi từ loại nào (coin/credit/token/huy hiệu/thành tích) | Loại nguồn | – |
| rate_to_ets | numeric | (16,2) | – | 1 from = rate ETS | Tỷ lệ quy đổi | – |
| metadata_id | text | – | – | – | Mô tả | – |
| effective_from | datetime | – | – | – | Bắt đầu áp dụng | – |
| effective_to | datetime | – | – | – | Kết thúc áp dụng, NULL = đang áp dụng | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Wallet Transactions

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| tx_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh giao dịch | – |
| wallet_id | char | – | FK → wallets | – | Liên kết ví | – |
| asset_type | text | – | – | Loại tài sản số | – | – |
| direction | smallint | – | – | 1 = cộng, -1 = trừ | Hướng giao dịch | – |
| amount | numeric | (16,2) | – | – | Số lượng thay đổi | – |
| ref_type | text | – | – | Chứng thực/post/comment/... | Kiểu tham chiếu | – |
| ref_id | text | – | – | – | ID tham chiếu | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## User Interests

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| interest_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh sở thích | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| interest_text | text | – | – | – | Sở thích user nhập | – |
| normalized_text | text | – | – | – | Chuẩn hóa sở thích nhập | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Interest Canonical

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| canonical_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh chuẩn | – |
| name | text | – | – | – | Tên chuẩn | – |
| slug | char | – | – | – | Mã chuẩn | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Interest Mapping

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| interest_id | char | – | FK → user_interests | – | FK sở thích user nhập | – |
| canonical_id | char | – | FK → interest_canonical | – | FK sở thích chuẩn | – |
| confidence | numeric | (6,2) | – | – | Độ tin cậy | – |
| mapped_by | text | – | – | admin/auto | Map bởi ai | – |
| mapped_at | datetime | – | – | – | Thời điểm map | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Posts

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| post_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh post | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| content | text | – | – | – | Nội dung post | – |
| file_url | text | – | – | – | Tệp đính kèm multimedia | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Comment Post (liên kết post/comment)

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| post_id | char | – | FK → posts | – | Liên kết post | – |
| comment_id | char | – | FK → comments | – | Liên kết comment | – |
| profile_id | char | – | FK → profile | – | Ai comment | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Comments

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| comment_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh comment | – |
| profile_id | char | – | FK → profile | – | Liên kết profile | – |
| content | text | – | – | – | Nội dung comment | – |
| file_url | text | – | – | – | Tệp đính kèm multimedia | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |
| updated_at | datetime | – | – | – | Ngày cập nhật | – |

## Post Interactions

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| interaction_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh tương tác post | – |
| post_id | char | – | FK → posts | – | Liên kết post | – |
| profile_id | char | – | FK → profile | – | Ai tương tác | – |
| action | text | – | – | like/share | Loại tương tác | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## Comment Interactions

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| interaction_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh tương tác comment | – |
| comment_id | char | – | FK → comments | – | Liên kết comment | – |
| profile_id | char | – | FK → profile | – | Ai tương tác | – |
| action | text | – | – | like/share | Loại tương tác | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## Group Membership

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| group_id | char | – | FK → group (global) | – | Nhóm liên kết | – |
| profile_id | char | – | FK → profile | – | Thành viên | – |
| role | boolean | – | – | 0 = thành viên, 1 = nhóm trưởng | Vai trò | – |
| joined_at | datetime | – | – | – | Ngày tham gia | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## Messages

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| message_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh tin nhắn | – |
| msg_scope | smallint | – | – | 0 = cá nhân, 1 = nhóm | Phạm vi | – |
| group_id | char | – | FK nếu là tin nhắn nhóm | – | Nhóm | – |
| receiver_id | char | – | FK nếu là cá nhân | – | Người nhận | – |
| content | text | – | – | – | Nội dung | – |
| file_url | text | – | – | – | Multimedia | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## User Actions

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| action_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh hành động | – |
| profile_id | char | – | FK → profile | – | Ai thực hiện | – |
| action_type | text | – | – | Nhắn tin, tham gia nhóm… | Loại hành động | – |
| object_type | text | – | – | Tin nhắn/group | Đối tượng | – |
| object_id | char | – | – | – | ID đối tượng | – |
| group_id | char | – | – | – | Nhóm tương tác | – |
| msg_scope | smallint | – | – | – | Phạm vi tin nhắn | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## Polls

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| poll_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh poll | – |
| group_id | char | – | FK | – | Poll của nhóm nào | – |
| profile_id | char | – | FK → profile | – | Người tạo | – |
| title | text | – | – | – | Tiêu đề poll | – |
| is_closed | boolean | – | – | – | Trạng thái đóng/mở | – |
| metadata_id | text | – | – | – | Mô tả | – |
| created_at | datetime | – | – | – | Ngày tạo | – |

## Poll Options

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| option_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh option | – |
| poll_id | char | – | FK → polls | – | Thuộc poll nào | – |
| option_text | text | – | – | – | Nội dung lựa chọn | – |

## Poll Votes

| Thuộc tính | Kiểu | Kích thước | Ràng buộc | Quy ước | Mô tả | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| poll_vote_id | char | – | PK, unique | Mã sinh bởi hệ thống | Định danh vote | – |
| option_id | char | – | FK → poll_options | – | Option được chọn | – |
| created_at | datetime | – | – | – | Ngày bình chọn | – |
