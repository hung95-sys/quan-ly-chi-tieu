import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE id=16")
    row = cursor.fetchone()
    if row:
        db_name = row[0]
        print(f"DB Name: {db_name}")
        print(f"DB Hex: {db_name.encode('utf-8').hex()}")
        
        target = 'Chi quỹ'
        print(f"Target Name: {target}")
        print(f"Target Hex: {target.encode('utf-8').hex()}")
        
        print(f"Match? {db_name == target}")
    else:
        print("Category 16 not found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
