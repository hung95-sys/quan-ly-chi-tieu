#!/bin/bash

# Script cài đặt tự động Quản Lý Chi Tiêu trên Ubuntu
# Usage: sudo bash install.sh

# Dừng script nếu có lỗi
set -e

REPO_URL="https://github.com/hung95-sys/quan-ly-chi-tieu.git"
APP_DIR="/var/www/quan-ly-chi-tieu"
USER="www-data"

# Màu sắc cho đẹp
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Bắt đầu cài đặt Quản Lý Chi Tiêu...${NC}"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}❌ Vui lòng chạy bằng quyền root (sudo)${NC}"
  exit 1
fi

# 1. Cài đặt dependencies
echo -e "${YELLOW}📦 [1/6] Đang cập nhật và cài đặt các gói cần thiết...${NC}"
apt update -qq
apt install -y python3-pip python3-venv nginx git -qq

# 2. Setup thư mục và source code
echo -e "${YELLOW}📂 [2/6] Đang cấu hình mã nguồn...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "   Thư mục đã tồn tại, đang cập nhật code..."
    cd $APP_DIR
    git pull
else
    echo "   Clone source code từ GitHub..."
    mkdir -p /var/www
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# 3. Setup Python Environment
echo -e "${YELLOW}🐍 [3/6] Đang cài đặt môi trường Python...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. Setup Systemd
echo -e "${YELLOW}⚙️ [4/6] Đang cấu hình Systemd Service...${NC}"
cat > /etc/systemd/system/quanlychitieu.service <<EOF
[Unit]
Description=Gunicorn instance to serve Quan Ly Chi Tieu
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:quanlychitieu.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

# 5. Setup Nginx
echo -e "${YELLOW}🌐 [5/6] Đang cấu hình Nginx...${NC}"

# Hỏi tên miền (nếu chạy interactive)
DOMAIN_NAME="_"
if [ -t 0 ]; then
    read -p "Nhập tên miền hoặc IP của server (Enter để dùng mặc định): " INPUT_DOMAIN
    if [ ! -z "$INPUT_DOMAIN" ]; then
        DOMAIN_NAME=$INPUT_DOMAIN
    fi
fi

cat > /etc/nginx/sites-available/quanlychitieu <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/quanlychitieu.sock;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/quanlychitieu /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 6. Phân quyền
echo -e "${YELLOW}🔒 [6/6] Đang thiết lập quyền hạn...${NC}"
chown -R $USER:$USER $APP_DIR
chmod -R 775 $APP_DIR
# Cấp quyền ghi đặc biệt cho database nếu tồn tại
if [ -f "$APP_DIR/database.db" ]; then
    chmod 664 "$APP_DIR/database.db"
fi

# Khởi động service
echo -e "${GREEN}🚀 Khởi động ứng dụng...${NC}"
systemctl daemon-reload
systemctl start quanlychitieu
systemctl enable quanlychitieu
systemctl restart quanlychitieu

echo -e "${GREEN}✅ CÀI ĐẶT HOÀN TẤT!${NC}"
echo -e "Truy cập tại: http://$DOMAIN_NAME"
