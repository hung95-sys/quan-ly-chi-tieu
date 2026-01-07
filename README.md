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

Cách nhanh nhất để cài đặt là sử dụng script tự động (đã bao gồm cài đặt Python, Nginx, Systemd và phân quyền):

```bash
sudo bash <(curl -s https://raw.githubusercontent.com/hung95-sys/quan-ly-chi-tieu/main/install.sh)
```

Sau khi chạy xong, website sẽ hoạt động ngay lập tức!

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