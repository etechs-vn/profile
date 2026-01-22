# Đặc tả bảng dữ liệu (bảng mô tả)

## profile
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| profile_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| user_id | int |  | FK → users.id (Shared DB) |  | Liên kết với user trong Shared DB |  |
| nickname | char |  |  |  | Bí danh |  |
| valid_from | datetime |  |  |  | Thông tin có hiệu lực từ |  |
| valid_to | datetime |  |  |  | Thông tin hết hiệu lực từ |  |
| dob | date |  |  |  | Ngày sinh |  |
| gender | boolean |  |  |  | 1: Nam, 0: Nữ |  |
| address | text |  |  |  | Địa chỉ |  |
| avatar_url | text |  |  |  | Ảnh đại diện trên object storage |  |
| bio | text |  |  |  | Giới thiệu ngắn |  |
| metadata_id | text |  |  |  | Mô tả thêm |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## education
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| education_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết với profile |  |
| education_level | varchar |  |  |  | Cấp học (cấp 1/2/3/đại học...) |  |
| institution_name | text |  |  |  | Tên trường/cơ sở đào tạo |  |
| start_date | datetime |  |  |  | Thời gian bắt đầu |  |
| end_date | datetime |  |  | end_date IS NULL OR start_date IS NULL OR end_date >= start_date | Thời gian kết thúc |  |
| is_current | boolean |  |  |  | 1 đang học, 0 nghỉ |  |
| credential_type | varchar |  |  |  | Bằng cấp/chứng chỉ |  |
| credential_title | text |  |  |  | Ví dụ: bằng THPT, cử nhân, B2/B1/IELTS/MOS |  |
| issuing_organization | text |  |  |  | Đơn vị cấp |  |
| credential_ref | text |  |  |  | Số hiệu bằng/mã tra cứu |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## identity_documents
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| identity_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết với profile |  |
| document_type | text |  |  |  | Loại giấy tờ (CCCD/thẻ học sinh/bảo hiểm...) |  |
| document_number | text |  |  |  | Số giấy tờ |  |
| issued_date | datetime |  |  |  | Ngày cấp |  |
| expiry_date | datetime |  |  |  | Ngày hết hạn |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## wallets
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| wallet_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết với profile |  |
| ets | numeric | (16,2) |  |  | Số dư credit |  |
| metadata_id | text |  |  |  | Mô tả ví |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## wallet_assets
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| asset_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| wallet_id | char |  | FK → wallets.wallet_id |  | Liên kết với ví |  |
| asset_type | text |  |  |  | Coin/token/huy hiệu/thành tích/chứng nhận loại |  |
| asset_code | text |  |  |  | Mã |  |
| amount | numeric | (16,2) |  |  | Số lượng |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## asset_rates_to_credit
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| rate_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| from_asset_type | text |  |  |  | Quy đổi từ loại nào (coin/credit/token/huy hiệu/thành tích) |  |
| rate_to_ets | numeric | (16,2) |  |  | 1 đơn vị from = rate ets |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## wallet_transactions
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| tx_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| wallet_id | char |  | FK → wallets.wallet_id |  | Liên kết với ví |  |
| asset_type | text |  |  |  | Loại tài sản số |  |
| direction | smallint |  |  |  | 1 = cộng, -1 = trừ |  |
| amount | numeric | (16,2) |  |  | Số lượng thay đổi |  |
| ref_type | text |  |  |  | Chứng thực/post/comment/... |  |
| ref_id | text |  |  |  | ID tham chiếu |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## user_interests
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| interest_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết với profile |  |
| interest_text | text |  |  |  | Sở thích user nhập |  |
| normalized_text | text |  |  |  | Chuẩn hóa sở thích |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## interest_canonical
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| canonical_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| name | text |  |  |  | Tên chuẩn hiển thị |  |
| slug | char |  |  |  | Mã chuẩn |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## interest_mapping
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| interest_id | char |  | PK, unique |  | FK user nhập sở thích |  |
| canonical_id | char |  | FK → interest_canonical.canonical_id |  | FK map về sở thích chuẩn |  |
| confidence | numeric | (6,2) |  |  | Độ tin cậy |  |
| mapped_by | text |  |  |  | Map bởi admin/auto |  |
| mapped_at | datetime |  |  |  | Thời điểm map |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## posts
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| post_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| content | text |  |  |  | Nội dung post |  |
| file_url | text |  |  |  | Đính kèm multimedia |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## comment_post
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| comment_post_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| post_id | char |  | FK → posts.post_id |  | Liên kết post |  |
| comment_id | char |  | FK → comments.comment_id |  | Liên kết comment |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết profile |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## comments
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| comment_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| content | text |  |  |  | Nội dung comment |  |
| file_url | text |  |  |  | Đính kèm multimedia |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
| updated_at | datetime |  |  |  | Ngày cập nhật |  |

## post_interactions
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| interaction_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| post_id | char |  | FK → posts.post_id |  | Liên kết post |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết profile |  |
| action | text |  |  |  | Like/share |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## comment_interactions
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| interaction_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| comment_id | char |  | FK → comments.comment_id |  | Liên kết comment |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết profile |  |
| action | text |  |  |  | Like/share |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## groups
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| group_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết profile |  |
| role | boolean |  |  |  | 0 thành viên, 1 nhóm trưởng |  |
| joined_at | datetime |  |  |  | Ngày tham gia |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## messages
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| message_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| msg_scope | smallint |  |  |  | 0 tin nhắn cá nhân, 1 tin nhắn nhóm |  |
| group_id | char |  | FK nếu msg_scope = 1 |  | Thuộc nhóm nào |  |
| receiver_id | char |  | FK nếu msg_scope = 0 |  | Cá nhân nào |  |
| content | text |  |  |  | Nội dung tin nhắn |  |
| file_url | text |  |  |  | Link multimedia |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## user_actions
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| action_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết với profile |  |
| action_type | text |  |  |  | Nhắn tin, tham gia nhóm... |  |
| object_type | text |  |  |  | Tin nhắn/group |  |
| object_id | char |  |  |  | ID đối tượng |  |
| group_id | char |  |  |  | User tương tác nhóm nào |  |
| msg_scope | smallint |  |  |  | User tương tác tin nhắn nào |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## polls
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| poll_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| group_id | char |  | FK → groups.group_id |  | Bình chọn của nhóm |  |
| profile_id | char |  | FK → profile.profile_id |  | Liên kết profile |  |
| title | text |  |  |  | Tiêu đề hộp bình chọn |  |
| is_closed | boolean |  |  |  | Đóng/mở bình chọn |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |

## poll_options
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| option_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| poll_id | char |  | FK → polls.poll_id |  | Thuộc hộp bình chọn nào |  |
| option_text | text |  |  |  | Nội dung bình chọn |  |

## poll_votes
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| poll_vote_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| option_id | char |  | FK → poll_options.option_id |  | Option được chọn |  |
| created_at | datetime |  |  |  | Ngày bình chọn |  |

## appointments
| Thuộc tính | Kiểu | Kích thước | Khóa | Ràng buộc | Mô tả | Ghi chú |
|---|---|---|---|---|---|---|
| appointment_id | char |  | PK, unique |  | Mã được tạo qua hệ thống |  |
| group_id | char |  | FK → groups.group_id |  | Nhắc hẹn của nhóm nào |  |
| title | text |  |  |  | Tiêu đề nhắc hẹn |  |
| start_time | datetime |  |  |  | Thời gian bắt đầu |  |
| end_time | datetime |  |  |  | Thời gian kết thúc |  |
| note | text |  |  |  | Ghi chú |  |
| remind_enabled | boolean |  |  |  | Bật/tắt nhắc hẹn |  |
| remind_before_minutes | int |  |  |  | Nhắc trước bao nhiêu phút |  |
| metadata_id | text |  |  |  | Mô tả |  |
| created_at | datetime |  |  |  | Ngày tạo |  |
