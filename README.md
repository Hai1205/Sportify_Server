## Tổng quan

Sportify là ứng dụng web nghe nhạc trực tuyến mô phỏng theo Spotify, với đầy đủ tính năng phát nhạc, quản lý bài hát, tương tác xã hội và nhiều tính năng khác.

- 🎵 Phát nhạc với đầy đủ điều khiển (play, pause, next, previous)
- 🎧 Hiển thị bài hát đang phát với thông tin chi tiết
- 📚 Trình duyệt bài hát và album
- 🎤 Trang chi tiết bài hát với lời và thông tin
- 💿 Trang chi tiết album với danh sách bài hát
- 🔍 Tìm kiếm bài hát, album và nghệ sĩ
- ❤️ Thích bài hát và album
- 👤 Hồ sơ người dùng và nghệ sĩ
- 🔐 Hệ thống xác thực đầy đủ
- 💬 Chat trực tiếp giữa người dùng
- 📱 Giao diện responsive


## Công nghệ sử dụng
- Django: Framework web chính, quản lý toàn bộ ứng dụng backend.
- Django REST Framework (DRF): Xây dựng các API RESTful.
- Django Channels: Hỗ trợ WebSocket và các tính năng real-time (chat).
- Daphne: ASGI server để chạy ứng dụng Django với Channels.
- JWT (JSON Web Token): Xác thực người dùng (qua rest_framework_simplejwt).
- MySQL/PostgreSQL/SQLite: Hỗ trợ nhiều loại cơ sở dữ liệu (có thể cấu hình trong .env và settings.py).
- AWS S3: Lưu trữ file tĩnh (qua các service như AwsS3Service).
- Django Email Backend: Gửi email xác thực, thông báo.

## Cài đặt

Yêu cầu tiên quyết
- Python 3.8 trở lên (khuyến nghị 3.10+)
- pip hoặc pipenv
- MySQL (hoặc có thể cấu hình lại để dùng SQLite/PostgreSQL)

Các bước cài đặt
1. Clone repository và truy cập thư mục frontend
```bash
git clone https://github.com/haole2k4/Sportify-Server.git
cd Sportify-Server
```
2. Tạo và kích hoạt môi trường ảo
Sử dụng venv:

```bash 
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. Chỉnh sửa file .env để thiết lập các biến môi trường cần thiết:

```bash
SECRET_KEY=
CLIENT_PORT_3000=http://localhost:3000
AWS_S3_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

4. Tạo database

```bash
CREATE DATABASE sportify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Chạy migrate và tạo admin

```bash
python manage.py migrate
python manage.py createsuperuser
```

7. Khởi động backend:
```bash
python manage.py runserver
```

8. Chạy với WebSocket (ASGI):
mở một cửa sổ khác chạy venv và thực hiện lệnh sau:
```bash
daphne -p 8001 Sportify_Server.asgi:application
```

## Giấy phép

<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #1DB954;">
  <p><strong>MIT License</strong></p>
  <p>Copyright (c) 2025 Spotify Clone Team</p>
  
  <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
  
  <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
  
  <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>
</div>

## Thành viên
| Mã số sinh viên | Họ và tên         | 
|-----------------|-------------------|
| 3122410095      | Nguyễn Hoàng Hải  |
| 3122410096      | Lê Chí Hào        |
