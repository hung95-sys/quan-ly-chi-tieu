import sqlite3
import sys
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, subtype FROM categories WHERE type='Chi'")
    rows = cursor.fetchall()
    print("Categories with type='Chi':")
    for row in rows:
        print(row)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
