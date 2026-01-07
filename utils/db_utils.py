import sqlite3
import os
from config import config
from werkzeug.security import generate_password_hash

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(config.DATABASE_URI)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the required schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            role TEXT DEFAULT 'user',
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- 'Thu' or 'Chi'
            subtype TEXT DEFAULT 'normal', -- 'normal', 'fund'
            icon TEXT,
            UNIQUE(name, type, subtype)
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL, -- YYYY-MM-DD
            type TEXT NOT NULL, -- 'Thu' or 'Chi'
            category_id INTEGER,
            amount REAL NOT NULL,
            note TEXT,
            fund_purpose TEXT, -- For 'Thu quỹ'/'Chi quỹ'
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Create fund_links table (legacy - keeping for backward compatibility)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            user2_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (user1_id) REFERENCES users (id),
            FOREIGN KEY (user2_id) REFERENCES users (id),
            UNIQUE(user1_id, user2_id)
        )
    ''')
    
    # Create fund_groups table (new - replaces fund_links)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by INTEGER,
            created_at TEXT,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Create fund_group_members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            joined_at TEXT,
            FOREIGN KEY (group_id) REFERENCES fund_groups (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(group_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """Executes a query and returns the results."""
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Executes a modification query (INSERT, UPDATE, DELETE)."""
    conn = get_db_connection()
    try:
        cur = conn.execute(query, args)
        conn.commit()
        last_row_id = cur.lastrowid
        conn.close()
        return last_row_id
    except Exception as e:
        conn.close()
        raise e
