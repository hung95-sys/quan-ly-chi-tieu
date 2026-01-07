# 🌐 Ứng dụng Web Python với Flask

Ứng dụng web được xây dựng bằng Python và Flask, sử dụng cơ sở dữ liệu **SQLite** để lưu trữ và quản lý chi tiêu cá nhân.

## ✨ Tính năng

- ✅ **Hệ thống đăng nhập** - Xác thực người dùng an toàn từ Database
- ✅ **Trang quản trị** - Dashboard với thông tin người dùng và quản lý dữ liệu
- ✅ **Quản lý người dùng** - Hiển thị danh sách người dùng (cho admin)
- ✅ **Quản lý chi tiêu** - Thêm, sửa, xóa các khoản thu/chi
- ✅ **Báo cáo** - Biểu đồ thống kê trực quan
- ✅ **Data Management** - Import/Export dữ liệu qua file Excel

## 🚀 Cài đặt và Chạy (Local / Windows)

### 1. Clone Code

```bash
git clone https://github.com/hung95-sys/quan-ly-chi-tieu.git
cd quan-ly-chi-tieu
```

*Lưu ý: Dự án đã bao gồm file `database.db` chứa dữ liệu sẵn có.*

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python app.py
```

### 4. Mở trình duyệt

Truy cập: http://localhost:5000

---

## 🐧 Hướng dẫn Cài đặt trên Ubuntu (Production)

Dưới đây là hướng dẫn chi tiết để deploy ứng dụng lên server Ubuntu sử dụng **Gunicorn** và **Nginx**.

### 1. Cài đặt các gói cần thiết

Đăng nhập vào VPS/Server Ubuntu và chạy các lệnh sau:

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Python, pip, venv và Nginx
sudo apt install python3-pip python3-venv nginx git -y
```

### 2. Clone Code và Cài đặt môi trường

```bash
# Di chuyển đến thư mục web (ví dụ /var/www)
cd /var/www

# Clone source code
sudo git clone https://github.com/hung95-sys/quan-ly-chi-tieu.git
cd quan-ly-chi-tieu

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
pip install gunicorn  # Cài thêm gunicorn cho production
```

### 3. Cấu hình Systemd Service

Tạo file service để quản lý ứng dụng:

```bash
sudo nano /etc/systemd/system/quanlychitieu.service
```

Dán nội dung sau vào:

```ini
[Unit]
Description=Gunicorn instance to serve Quan Ly Chi Tieu
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/quan-ly-chi-tieu
Environment="PATH=/var/www/quan-ly-chi-tieu/venv/bin"
ExecStart=/var/www/quan-ly-chi-tieu/venv/bin/gunicorn --workers 3 --bind unix:quanlychitieu.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Lưu file (`Ctrl+O`, `Enter`) và thoát (`Ctrl+X`).

Khởi động service:

```bash
# Cấp quyền sở hữu thư mục cho user www-data
sudo chown -R www-data:www-data /var/www/quan-ly-chi-tieu

# Khởi động và enable service
sudo systemctl start quanlychitieu
sudo systemctl enable quanlychitieu
```

### 4. Cấu hình Nginx (Reverse Proxy)

Tạo file cấu hình Nginx:

```bash
sudo nano /etc/nginx/sites-available/quanlychitieu
```

Dán nội dung sau (thay `your_domain_or_ip` bằng IP hoặc tên miền của bạn):

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/quan-ly-chi-tieu/quanlychitieu.sock;
    }
}
```

Lưu và thoát. Sau đó kích hoạt cấu hình:

```bash
sudo ln -s /etc/nginx/sites-available/quanlychitieu /etc/nginx/sites-enabled
sudo nginx -t  # Kiểm tra lỗi cú pháp
sudo systemctl restart nginx
```

### 5. Cấp quyền ghi file Database (QUAN TRỌNG)

Vì ứng dụng sử dụng SQLite (`database.db`), bạn cần cấp quyền ghi tuyệt đối cho file này và thư mục chứa nó để ứng dụng có thể lưu dữ liệu:

```bash
# Cấp quyền cho file database
sudo chmod 664 /var/www/quan-ly-chi-tieu/database.db

# Cấp quyền cho thư mục chứa database
sudo chmod 775 /var/www/quan-ly-chi-tieu
sudo chown -R www-data:www-data /var/www/quan-ly-chi-tieu
```

---

## 📁 Cấu trúc thư mục

```
Hung/
├── app.py                 # File chính của ứng dụng Flask
├── requirements.txt       # Danh sách các package cần thiết
├── README.md             # File hướng dẫn
├── database.db           # Cơ sở dữ liệu SQLite (Chứa dữ liệu chính)
├── data/
│   └── export_all.xlsx   # File Excel (Dùng để backup/import)
├── templates/             # Giao diện HTML
└── static/                # CSS, JS, Images
```

## 🛠️ Công nghệ sử dụng

- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **Authentication**: Flask Session
- **Data Processing**: pandas, openpyxl
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## ⚠️ Lưu ý về Database

- File `database.db` chứa toàn bộ dữ liệu người dùng và giao dịch.
- Khi deploy, hãy đảm bảo file này được bảo mật.
- Nên thường xuyên backup dữ liệu bằng tính năng **Export Excel** trong trang quản trị.

Chúc bạn code vui vẻ! 🎉