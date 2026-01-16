"""
API Routes cho quản lý dữ liệu (Export/Import)
"""
from flask import Blueprint, request, send_file, jsonify, session
import pandas as pd
import io
from datetime import datetime
import traceback
from utils.decorators import admin_required
from utils.db_utils import query_db, get_db_connection
import sqlite3

bp = Blueprint('api_data', __name__)

@bp.route('/api/export/excel', methods=['GET'])
@admin_required
def export_excel():
    """Xuất toàn bộ dữ liệu (Giao dịch, Users, Groups) ra Excel"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. Transactions
            sql_trans = '''
                SELECT 
                    t.date as "Ngày",
                    u.username as "Username",
                    u.name as "Người dùng",
                    c.name as "Danh mục",
                    t.type as "Loại",
                    t.amount as "Số tiền",
                    t.note as "Ghi chú",
                    t.fund_purpose as "Mục đích quỹ"
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN categories c ON t.category_id = c.id
                ORDER BY t.date DESC
            '''
            # Use query_db to get rows, then convert to DataFrame
            rows_trans = query_db(sql_trans)
            df_trans = pd.DataFrame([dict(row) for row in rows_trans])
            df_trans.to_excel(writer, index=False, sheet_name='Transactions')
            
            # 1.5 Categories (New)
            sql_cats = 'SELECT name, type, subtype, icon FROM categories'
            rows_cats = query_db(sql_cats)
            df_cats = pd.DataFrame([dict(row) for row in rows_cats])
            df_cats.to_excel(writer, index=False, sheet_name='Categories')
            
            # 2. Users
            sql_users = 'SELECT username, name, role, active FROM users'
            rows_users = query_db(sql_users)
            df_users = pd.DataFrame([dict(row) for row in rows_users])
            df_users.to_excel(writer, index=False, sheet_name='Users')
            
            # 3. Fund Groups
            sql_groups = '''
                SELECT g.name, u.username as created_by 
                FROM fund_groups g 
                LEFT JOIN users u ON g.created_by = u.id
            '''
            rows_groups = query_db(sql_groups)
            df_groups = pd.DataFrame([dict(row) for row in rows_groups])
            df_groups.to_excel(writer, index=False, sheet_name='FundGroups')
            
            # 4. Group Members
            sql_members = '''
                SELECT g.name as group_name, u.username as user_username
                FROM fund_group_members m
                JOIN fund_groups g ON m.group_id = g.id
                JOIN users u ON m.user_id = u.id
            '''
            rows_members = query_db(sql_members)
            df_members = pd.DataFrame([dict(row) for row in rows_members])
            df_members.to_excel(writer, index=False, sheet_name='GroupMembers')
            
            # Auto-adjust column width for all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(writer.book[sheet_name].columns):
                    max_len = 0
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_len:
                                max_len = len(str(cell.value))
                        except:
                            pass
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_len + 2, 50)
                
        output.seek(0)
        filename = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Lỗi khi export excel: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@bp.route('/api/import/excel', methods=['POST'])
@admin_required
def import_excel():
    """Import dữ liệu từ file Excel (Full Restore) - Optimized for Speed"""
    conn = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được gửi lên'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Chưa chọn file'}), 400
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Chỉ hỗ trợ file Excel (.xlsx, .xls)'}), 400

        # Read Excel (all sheets)
        try:
            xls = pd.ExcelFile(file)
        except Exception as e:
            return jsonify({'error': f'Không thể đọc file Excel: {str(e)}'}), 400
            
        success_msg = []
        errors = []
        
        # --- START TRANSACTION ---
        conn = get_db_connection()
        # Turn off auto-commit behavior if any (SQLite default is usually fine but explicit commit is better)
        
        # --- 0. CLEAR EXISTING TRANSACTIONS (Replace Mode) ---
        conn.execute('DELETE FROM transactions')
        success_msg.append("Đã xóa dữ liệu giao dịch cũ.")
        
        # --- 1. Restore Users ---
        users_cache = {} # username -> id
        if 'Users' in xls.sheet_names:
            df_users = pd.read_excel(xls, 'Users')
            count_users = 0
            for _, row in df_users.iterrows():
                try:
                    username = str(row['username']).strip()
                    name = str(row['name']).strip()
                    role = str(row['role']).strip()
                    active = int(row['active'])
                    
                    cur = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
                    existing = cur.fetchone()
                    
                    if existing:
                        users_cache[username] = existing['id']
                    else:
                        password_hash = generate_password_hash('123456')
                        conn.execute('INSERT INTO users (username, password, name, role, active) VALUES (?, ?, ?, ?, ?)',
                                (username, password_hash, name, role, active))
                        cur = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
                        new_user = cur.fetchone()
                        users_cache[username] = new_user['id']
                        count_users += 1
                except Exception as e:
                    errors.append(f"Lỗi User {row.get('username')}: {e}")
            success_msg.append(f"Đã thêm {count_users} users mới.")
        
        # Reload cache
        cur = conn.execute('SELECT id, username FROM users')
        for u in cur.fetchall():
            users_cache[u['username']] = u['id']

        # --- 1.5 Restore Categories ---
        categories_cache = {} # name -> id
        if 'Categories' in xls.sheet_names:
            df_cats = pd.read_excel(xls, 'Categories')
            count_cats = 0
            for _, row in df_cats.iterrows():
                try:
                    name = str(row['name']).strip()
                    cat_type = str(row['type']).strip()
                    subtype = str(row['subtype']).strip() if 'subtype' in row and pd.notna(row['subtype']) else 'default'
                    icon = str(row['icon']).strip() if 'icon' in row and pd.notna(row['icon']) else '📝'
                    
                    cur = conn.execute('SELECT id FROM categories WHERE name = ?', (name,))
                    existing = cur.fetchone()
                    
                    if existing:
                        categories_cache[name] = existing['id']
                        # Update existing
                        try:
                            conn.execute('UPDATE categories SET type = ?, subtype = ?, icon = ? WHERE id = ?',
                                    (cat_type, subtype, icon, existing['id']))
                        except sqlite3.IntegrityError:
                            pass # Ignore UNIQUE constraint on update
                    else:
                        try:
                            conn.execute('INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                                    (name, cat_type, subtype, icon))
                            cur = conn.execute('SELECT id FROM categories WHERE name = ?', (name,))
                            new_cat = cur.fetchone()
                            if new_cat:
                                categories_cache[name] = new_cat['id']
                                count_cats += 1
                        except sqlite3.IntegrityError:
                             # Retry fetch if race condition/duplicate
                            cur = conn.execute('SELECT id FROM categories WHERE name = ?', (name,))
                            existing_retry = cur.fetchone()
                            if existing_retry:
                                categories_cache[name] = existing_retry['id']

                except Exception as e:
                    errors.append(f"Lỗi Category {row.get('name')}: {e}")
            success_msg.append(f"Đã đồng bộ {count_cats} danh mục mới.")
        
        # Reload cache
        cur = conn.execute('SELECT id, name FROM categories')
        for c in cur.fetchall():
            categories_cache[c['name']] = c['id']

        # --- 2. Restore Fund Groups ---
        groups_cache = {} 
        if 'FundGroups' in xls.sheet_names:
            df_groups = pd.read_excel(xls, 'FundGroups')
            count_groups = 0
            for _, row in df_groups.iterrows():
                try:
                    name = str(row['name']).strip()
                    created_by_user = str(row['created_by']).strip()
                    creator_id = users_cache.get(created_by_user, 1)
                    
                    cur = conn.execute('SELECT id FROM fund_groups WHERE name = ?', (name,))
                    existing = cur.fetchone()
                    if existing:
                        groups_cache[name] = existing['id']
                    else:
                        conn.execute('INSERT INTO fund_groups (name, created_by) VALUES (?, ?)', (name, creator_id))
                        cur = conn.execute('SELECT id FROM fund_groups WHERE name = ?', (name,))
                        new_group = cur.fetchone()
                        groups_cache[name] = new_group['id']
                        count_groups += 1
                except Exception as e:
                    errors.append(f"Lỗi Group {row.get('name')}: {e}")
            success_msg.append(f"Đã thêm {count_groups} nhóm quỹ mới.")
            
        # Reload cache
        cur = conn.execute('SELECT id, name FROM fund_groups')
        for g in cur.fetchall():
            groups_cache[g['name']] = g['id']

        # --- 3. Restore Group Members ---
        if 'GroupMembers' in xls.sheet_names:
            df_members = pd.read_excel(xls, 'GroupMembers')
            count_members = 0
            for _, row in df_members.iterrows():
                try:
                    group_name = str(row['group_name']).strip()
                    user_username = str(row['user_username']).strip()
                    
                    gid = groups_cache.get(group_name)
                    uid = users_cache.get(user_username)
                    
                    if gid and uid:
                        cur = conn.execute('SELECT id FROM fund_group_members WHERE group_id = ? AND user_id = ?', (gid, uid))
                        existing = cur.fetchone()
                        if not existing:
                            conn.execute('INSERT INTO fund_group_members (group_id, user_id) VALUES (?, ?)', (gid, uid))
                            count_members += 1
                except Exception as e:
                    errors.append(f"Lỗi Member {row.get('user_username')}: {e}")
            success_msg.append(f"Đã khôi phục {count_members} thành viên nhóm.")

        # --- 4. Restore Transactions ---
        sheet_trans = 'Transactions' if 'Transactions' in xls.sheet_names else (xls.sheet_names[0] if xls.sheet_names else None)
        if sheet_trans:
            df = pd.read_excel(xls, sheet_trans)
            
            # Ensure categories cache is populated
            if not categories_cache:
                cur = conn.execute('SELECT id, name FROM categories')
                for c in cur.fetchall():
                    categories_cache[c['name']] = c['id']
                
            count_trans = 0
            # Prepare batch insert data
            trans_to_insert = []
            
            for index, row in df.iterrows():
                try:
                    # Resolve User
                    user_id = None
                    if 'Username' in row and pd.notna(row['Username']):
                        user_id = users_cache.get(str(row['Username']).strip())
                    
                    if not user_id and 'Người dùng' in row:
                        u_name = str(row['Người dùng']).strip()
                        cur = conn.execute('SELECT id FROM users WHERE name = ?', (u_name,))
                        u = cur.fetchone()
                        if u: user_id = u['id']
                        
                    if not user_id:
                         # Create user on fly?
                        if 'Người dùng' in row:
                             u_name = str(row['Người dùng']).strip()
                             username = u_name.lower().replace(' ', '') + f"_{int(datetime.now().timestamp())}_{index}"
                             password_hash = generate_password_hash('123456')
                             conn.execute('INSERT INTO users (username, password, name, role, active) VALUES (?, ?, ?, ?, ?)',
                                     (username, password_hash, u_name, 'user', 1))
                             cur = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
                             new_u = cur.fetchone()
                             user_id = new_u['id']
                             users_cache[username] = user_id
                    
                    if not user_id: continue 
                    
                    # Resolve Category
                    cat_name = str(row['Danh mục']).strip()
                    cat_id = categories_cache.get(cat_name)
                    if not cat_id:
                        cat_type = row['Loại'] if 'Loại' in row else 'Chi'
                        conn.execute('INSERT INTO categories (name, type, icon) VALUES (?, ?, ?)', (cat_name, cat_type, '📝'))
                        cur = conn.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
                        new_cat = cur.fetchone()
                        cat_id = new_cat['id']
                        categories_cache[cat_name] = cat_id
                        
                    # Normalize date
                    date_val = pd.to_datetime(row['Ngày']).strftime('%Y-%m-%d')
                    amount = float(row['Số tiền'])
                    note = str(row['Ghi chú']) if 'Ghi chú' in row and pd.notna(row['Ghi chú']) else ''
                    fund_purpose = str(row['Mục đích quỹ']) if 'Mục đích quỹ' in row and pd.notna(row['Mục đích quỹ']) else None
                    trans_type = row['Loại']
                    
                    # Fund purpose check
                    if fund_purpose:
                        fund_purpose = fund_purpose.strip()
                        cur = conn.execute("SELECT id FROM categories WHERE name = ? AND subtype = 'fund'", (fund_purpose,))
                        existing_fund = cur.fetchone()
                        if not existing_fund:
                            conn.execute("INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)", 
                                        (fund_purpose, 'Chi', 'fund', '💰'))
                    
                    # Add to batch
                    trans_to_insert.append((user_id, date_val, trans_type, cat_id, amount, note, fund_purpose))
                    count_trans += 1
                    
                except Exception as e:
                    errors.append(f"Lỗi dòng {index + 2}: {e}")
            
            # Execute batch insert
            if trans_to_insert:
                conn.executemany('''
                    INSERT INTO transactions (user_id, date, type, category_id, amount, note, fund_purpose)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', trans_to_insert)
                
            success_msg.append(f"Đã import {count_trans} giao dịch.")

        # --- COMMIT TRANSACTION ---
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '\n'.join(success_msg),
            'errors': errors
        })
        
    except Exception as e:
        if conn: conn.rollback()
        print(f"Lỗi khi import excel: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
    finally:
        if conn: conn.close()
