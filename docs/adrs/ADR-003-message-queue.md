# ADR-003: Sử dụng Message Queue với RabbitMQ

## Trạng thái
Accepted

## Bối cảnh
Chúng tôi cần xem xét việc sử dụng Message Queue để xử lý các tác vụ bất đồng bộ trong hệ thống học trực tuyến (E-Learning).  
Một số chức năng như gửi email xác nhận khi học viên đăng ký khóa học hoặc gửi thông báo có thể mất nhiều thời gian xử lý nếu thực hiện trực tiếp trong luồng xử lý chính của hệ thống. Điều này có thể làm tăng thời gian phản hồi khi người dùng thực hiện thao tác.

## Quyết định
Sử dụng RabbitMQ làm Message Queue để xử lý các tác vụ bất đồng bộ trong hệ thống.

## Lý do
1. RabbitMQ hỗ trợ xử lý các tác vụ bất đồng bộ hiệu quả.
2. Giúp tách biệt việc xử lý các tác vụ nền khỏi luồng xử lý chính của hệ thống.
3. Phù hợp để xử lý các tác vụ như gửi email, thông báo hoặc các công việc tốn thời gian.
4. Có nhiều thư viện hỗ trợ tích hợp với Python và Flask.

## Hệ quả
- Tích cực:
  - Giảm thời gian phản hồi của hệ thống vì các tác vụ tốn thời gian được xử lý bất đồng bộ.
  - Hệ thống có khả năng mở rộng tốt hơn khi số lượng tác vụ nền tăng lên.
  - Tách biệt rõ ràng giữa xử lý chính của hệ thống và các tác vụ nền.

- Tiêu cực:
  - Tăng độ phức tạp của hệ thống do cần triển khai thêm RabbitMQ và worker xử lý message.
  - Cần quản lý và theo dõi queue để đảm bảo các message được xử lý đầy đủ.

## Ngày quyết định
2026-08-03