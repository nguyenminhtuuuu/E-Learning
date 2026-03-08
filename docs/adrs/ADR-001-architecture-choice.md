# ADR-001: Lựa chọn kiến trúc Layered

## Trạng thái

Accepted

## Bối cảnh

Chúng tôi cần lựa chọn kiến trúc phù hợp cho hệ thống học trực tuyến (E-Learning).
Hệ thống cho phép học viên đăng ký khóa học, xem video bài giảng, làm bài tập và theo dõi tiến độ học tập.

Dự án có quy mô nhỏ, nhóm phát triển gồm 2 người và thời gian thực hiện khoảng 8 tuần.
Do đó cần một kiến trúc đơn giản, dễ triển khai và dễ bảo trì.

## Quyết định

Sử dụng kiến trúc Layered 3 tầng:

* **Presentation Layer:** HTML, CSS, JavaScript (Web Application)
* **Business Logic Layer:** Python + Flask (Backend Application)
* **Data Layer:** MySQL Database

## Lý do

1. Kiến trúc Layered dễ hiểu và phù hợp với nhóm phát triển nhỏ.
2. Phân tách rõ ràng giữa giao diện người dùng, xử lý logic và lưu trữ dữ liệu.
3. Dễ bảo trì và mở rộng hệ thống trong tương lai.
4. Phù hợp với quy mô và thời gian phát triển của dự án.

## Hệ quả

### Tích cực

* Dễ phân chia công việc cho các thành viên theo từng layer.
* Hệ thống có cấu trúc rõ ràng và dễ bảo trì.
* Có thể dễ dàng thay đổi giao diện hoặc database mà ít ảnh hưởng đến các phần khác.

### Tiêu cực

* Một số chức năng đơn giản có thể phải đi qua nhiều layer, làm tăng độ phức tạp.
* Có thể làm giảm hiệu năng nếu hệ thống mở rộng lớn hơn.

## Ngày quyết định

07-03-2026
