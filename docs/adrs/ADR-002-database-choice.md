# ADR-002: Lựa chọn hệ quản trị cơ sở dữ liệu MySQL

## Trạng thái
Accepted

## Bối cảnh
Hệ thống E-Learning cần một hệ quản trị cơ sở dữ liệu để lưu trữ thông tin người dùng, khóa học, bài giảng video, bài kiểm tra và kết quả học tập.  
Hệ thống được xây dựng bằng Python và Flask nên cần một cơ sở dữ liệu dễ tích hợp, dễ triển khai và phù hợp với quy mô của dự án.

## Quyết định
Sử dụng MySQL làm hệ quản trị cơ sở dữ liệu chính của hệ thống.  
MySQL sẽ được sử dụng cùng với các thư viện kết nối như SQLAlchemy hoặc MySQL Connector để thao tác dữ liệu từ ứng dụng Flask.

## Lý do
1. MySQL là hệ quản trị cơ sở dữ liệu quan hệ phổ biến và ổn định.
2. Dễ dàng tích hợp với Python, Flask và các thư viện ORM như SQLAlchemy.
3. Hiệu năng tốt cho các ứng dụng web quy mô nhỏ đến trung bình.
4. Có nhiều tài liệu và cộng đồng hỗ trợ.

## Hệ quả
- Tích cực:
  - MySQL phổ biến, dễ học và có nhiều tài liệu hỗ trợ.
  - Tích hợp tốt với Flask và các thư viện ORM.
  - Hiệu năng ổn định cho hệ thống E-Learning.
  - Dễ cài đặt, quản lý và triển khai.

- Tiêu cực:
  - Khi hệ thống mở rộng lớn, việc mở rộng và phân tán dữ liệu có thể phức tạp.
  - Một số tính năng nâng cao có thể hạn chế so với một số hệ quản trị cơ sở dữ liệu khác.

## Ngày quyết định
2026-08-03