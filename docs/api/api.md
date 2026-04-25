
## 1. Hệ thống Tài khoản (Authentication)

### 1.1. Đăng ký tài khoản
* **URL:** `/register`
* **Method:** `POST`
* **Định dạng Request:** `multipart/form-data`

| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `name` | String | Có | Họ và tên người dùng |
| `username` | String | Có | Tên đăng nhập |
| `password` | String | Có | Mật khẩu |
| `confirm` | String | Có | Xác nhận mật khẩu |
| `email` | String | Có | Địa chỉ email (Phải đúng định dạng) |
| `avatar` | File (Image)| Không | File ảnh đại diện (Tự động upload lên Cloudinary) |

### 1.2. Đăng nhập
* **URL:** `/login`
* **Method:** `POST`
* **Định dạng Request:** `application/x-www-form-urlencoded`

| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `username` | String | Có | Tên đăng nhập |
| `password` | String | Có | Mật khẩu |

---

## 2. Tương tác của Học viên (Student Actions)

### 2.1. Đăng ký Khóa học
* **URL:** `/dangky/<int:khoahoc_id>`
* **Method:** `POST`
* **Yêu cầu:** Đăng nhập (Login Required)
* **Kết quả:** Tạo bản ghi mới trong bảng `Enrollment` và redirect về trang chủ.

### 2.2. Ghi nhận tiến độ học (Tự động)
* **URL:** `/lesson_detail/<int:lesson_id>`
* **Method:** `GET`
* **Mô tả:** Khi học viên truy cập vào xem chi tiết bài học, hệ thống sẽ gọi hàm `dao.update_user_progress` ở dưới nền để ghi nhận tiến độ.

### 2.3. Nộp bài Quiz & Chấm điểm
* **URL:** `/quiz/lesson/<int:lesson_id>` hoặc `/quiz/<int:khoahoc_id>`
* **Method:** `POST`
* **Định dạng Request:** `application/x-www-form-urlencoded`
* **Mô tả:** Tên các input form được sinh tự động theo ID câu hỏi.

| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `q_{id}` | String | Không | Chứa ID của đáp án được chọn. Ví dụ: `q_101=2` (Câu hỏi 101 chọn đáp án 2) |

* **Luồng xử lý:** Hệ thống chấm điểm, nếu đạt `score >= 5` (thang điểm 10), hệ thống tự động cập nhật bảng `Progress`.

### 2.4. Cấp và tải Chứng chỉ (PDF)
* **URL:** `/certificate/<int:khoahoc_id>`
* **Method:** `GET` / `POST`
* **Mô tả:** Hệ thống kiểm tra tiến độ khóa học (`course_progress['percent'] == 100`). Nếu đủ 100%, render file PDF và trả về dạng file đính kèm (`as_attachment=True`) để tải xuống.

---

## 3. Chức năng của Giảng viên (Teacher Actions - CRUD)

Các tính năng thao tác dữ liệu dành cho quyền `TEACHER` và `ADMIN`. Tất cả đều yêu cầu đăng nhập.

### 3.1. Quản lý Khóa học (Courses)
* **Thêm Khóa học:** `POST /add_khoahoc` (Upload ảnh bìa lên Cloudinary)
* **Cập nhật:** `POST /update_khoahoc/<int:khoahoc_id>`
* **Xóa:** `POST /delete_khoahoc/<int:khoahoc_id>`

| Tên trường (Form) | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `khoahoc_name` | String | Tên khóa học |
| `capdo_id` | Integer | ID Cấp độ (Beginner, Intermediate...) |
| `khoahoc_hp` | Integer | Học phí |
| `khoahoc_text` | String | Mô tả khóa học |
| `ten_file` | File | Ảnh bìa khóa học |

### 3.2. Quản lý Bài giảng (Lessons)
* **Thêm Bài giảng:** `POST /add_lesson/<int:khoahoc_id>` (Hỗ trợ upload video lên Cloudinary)
* **Cập nhật:** `POST /update_lesson/<int:lesson_id>` (Hỗ trợ đổi/xóa video)
* **Xóa:** `POST /delete_lesson/<int:lesson_id>`

| Tên trường (Form) | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `lesson_name` | String | Tên/Tiêu đề bài học |
| `lesson_text` | String | Nội dung văn bản |
| `ten_file` | File | Video bài giảng (Resource type: video) |
| `delete_video` | Checkbox | Đánh dấu để xóa video hiện tại |

### 3.3. Quản lý Câu hỏi Quiz (Questions)
* **Thêm Câu hỏi:** `POST /add_question/<int:lesson_id>`
* **Cập nhật hàng loạt:** `POST /update_questions/<int:lesson_id>`
* **Xóa:** `POST /delete_question/<int:question_id>`

| Tên trường (Form) | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `content` | String | Nội dung câu hỏi |
| `a1`, `a2` | String | Nội dung 2 lựa chọn đáp án |
| `correct` | String | Value `1` hoặc `2` tương ứng với đáp án đúng |
