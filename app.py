"""
Flask Application - Ứng dụng quản lý chi tiêu (Modular Version)

Cấu trúc đã được tách thành các modules:
- config.py: Cấu hình ứng dụng
- utils/: Utility functions
  - excel_utils.py: Xử lý đọc/ghi Excel
  - decorators.py: login_required, admin_required
- routes/: Route handlers (Blueprints)
  - auth.py: Login, Logout, Index
  - main.py: Dashboard, Chi tiêu, Admin
  - api_users.py: API quản lý users
  - api_expenses.py: API chi tiêu, calendar, reports
  - api_funds.py: API quỹ, fund links
  - api_categories.py: API danh mục
"""
from flask import Flask
import os
from config import Config

# Import blueprints
from routes import auth, main, api_users, api_expenses, api_funds, api_categories, api_data

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Đăng ký blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.register_blueprint(api_users.bp)
app.register_blueprint(api_expenses.bp)
app.register_blueprint(api_funds.bp)
app.register_blueprint(api_categories.bp)
app.register_blueprint(api_data.bp)


from utils.db_utils import init_db

if __name__ == '__main__':
    # Initialize DB
    if not os.path.exists('database.db'):
        init_db()
        
    app.run(debug=True, host='0.0.0.0', port=5000)
