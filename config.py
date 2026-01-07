"""
Cấu hình ứng dụng Flask
"""
import os

class Config:
    """Lớp cấu hình chính cho ứng dụng"""
    
    # Secret key cho session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
    # Đường dẫn đến file Excel (Backup)
    EXCEL_FILE = 'data/export_all.xlsx'
    
    # Đường dẫn đến SQLite DB
    DATABASE_URI = 'database.db'
    
    # Cấu hình retry cho file locking
    MAX_RETRY_ATTEMPTS = 5
    RETRY_DELAY_SECONDS = 0.5


# Singleton config object
config = Config()
