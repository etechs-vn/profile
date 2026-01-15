3. Tạo Profile và Trang cá nhân (Profile & Personal Page)
3.1. Mục tiêu
Thiết lập cho mỗi người dùng một hồ sơ dạng mạng xã hội, bao gồm:
Một trang thông tin cá nhân riêng đại diện cho định danh người dùng
Một trang mạng xã hội phục vụ tương tác (kết nối, đăng bài, bình luận)
Phân tách rõ ràng quy trình và cấu trúc trang dành cho học sinh và giáo viên
3.2. Nguyên tắc chung
Mỗi tài khoản sau khi đăng ký đều được hệ thống tự động tạo profile mặc định.
Mỗi người dùng chỉ có một trang cá nhân duy nhất trong hệ thống.
Trang cá nhân và toàn bộ nội dung liên quan được lưu trữ tại tầng dữ liệu riêng (Private Data).
Dữ liệu hiển thị công khai chỉ là dữ liệu được người dùng cho phép và dấu vết (hash) cần thiết cho mạng lưới.
Trang cá nhân tồn tại độc lập với trạng thái xác minh và chứng thực.
3.3. Cấu trúc Profile của người dùng
Profile của mỗi người dùng bao gồm hai thành phần chính:
3.3.1. Trang thông tin cá nhân (Personal Information Page) được liên kết với user ID
Trang này phản ánh định danh và vai trò của người dùng, bao gồm:
Thông tin cơ bản (họ tên, ảnh đại diện)
Trạng thái tài khoản (chưa xác minh, đã xác minh, đã chứng thực)
Vai trò hiển thị (sau khi xác minh): học sinh hoặc giáo viên
Thông tin học tập hoặc công tác
3.3.2. Trang mạng xã hội cá nhân (Social Interaction Page)
Trang này phục vụ cho các hoạt động tương tác, bao gồm:
Đăng bài viết
Bình luận
Kết nối bạn bè hoặc mối quan hệ học thuật
Hiển thị dòng thời gian hoạt động cá nhân
Trang mạng xã hội được gắn liền với profile nhưng có thể cấu hình quyền riêng tư riêng biệt.
3.4. Quy trình tự động tạo Profile sau khi đăng ký
Ngay sau khi người dùng hoàn tất đăng ký tài khoản, hệ thống tự động thực hiện:
Khởi tạo một profile mặc định cho người dùng.
Tạo trang thông tin cá nhân ban đầu với trạng thái:
Vai trò: chưa xác định
Trạng thái xác minh: chưa xác minh
Tạo trang mạng xã hội cá nhân với quyền tương tác cơ bản.
Liên kết profile với User ID và tài khoản hệ thống.
Lưu toàn bộ dữ liệu profile tại tầng dữ liệu riêng.
Người dùng có thể truy cập ngay trang cá nhân của mình sau khi đăng nhập lần đầu.
3.5. Quy trình hoàn thiện Profile cho học sinh
3.5.1. Điều kiện áp dụng
Áp dụng cho người dùng sau khi:
Đã đăng ký tài khoản
Đang hoặc đã xác minh với vai trò học sinh
3.5.2. Nội dung Profile học sinh
Profile học sinh bao gồm các thông tin:
Trường học
Lớp / khóa / niên khóa
Chuyên ngành (nếu có)
Thông tin học tập liên quan
3.5.3. Quy trình tạo và hoàn thiện
Người dùng bổ sung thông tin học sinh vào trang thông tin cá nhân.
Hệ thống ghi nhận vai trò là học sinh sau khi xác minh thành công.
Trang mạng xã hội cá nhân được cấu hình:
Cho phép kết nối với học sinh và giáo viên
Hiển thị nội dung phù hợp môi trường học đường (phát hiện những cmt spam, tiêu cực, rác,...vi phạm tiêu chuẩn cộng đồng)
Profile được cập nhật và lưu trữ tại kho dữ liệu riêng.
3.6. Quy trình hoàn thiện Profile cho giáo viên
3.6.1. Điều kiện áp dụng
Áp dụng cho người dùng sau khi:
Đã đăng ký tài khoản
Đang hoặc đã xác minh với vai trò giáo viên
3.6.2. Nội dung Profile giáo viên
Profile giáo viên bao gồm:
Đơn vị công tác
Bộ môn / lĩnh vực giảng dạy
Thông tin chuyên môn
Chức danh (nếu có)
3.6.3. Quy trình tạo và hoàn thiện
Người dùng bổ sung thông tin giáo viên vào trang thông tin cá nhân.
Hệ thống ghi nhận vai trò là giáo viên sau khi xác minh thành công
Trang mạng xã hội cá nhân được cấu hình:
Cho phép kết nối và tương tác với học sinh và giáo viên
Có thể mở các chức năng mở rộng (nhóm học tập, chia sẻ học liệu)
Profile được cập nhật và lưu trữ tại kho dữ liệu riêng.
3.7. Quyền riêng tư và hiển thị
Người dùng có quyền:


Cấu hình mức độ hiển thị trang cá nhân
Kiểm soát ai được xem thông tin và nội dung


Mặc định:


Trang cá nhân chỉ hiển thị thông tin cơ bản
Nội dung chi tiết do người dùng chủ động công khai


