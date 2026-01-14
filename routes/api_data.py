"""
API Routes cho quản lý dữ liệu (Export/Import)
"""
from flask import Blueprint, request, send_file, jsonify, session
import pandas as pd
import io
from datetime import datetime
import traceback
from utils.decorators import admin_required
from utils.db_utils import query_db

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
    """Import dữ liệu từ file Excel (Full Restore)"""
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
        
        from werkzeug.security import generate_password_hash
        
        # --- 0. CLEAR EXISTING TRANSACTIONS (Replace Mode) ---
        query_db('DELETE FROM transactions')
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
                    
                    existing = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
                    if existing:
                        users_cache[username] = existing['id']
                    else:
                        password_hash = generate_password_hash('123456')
                        query_db('INSERT INTO users (username, password, name, role, active) VALUES (?, ?, ?, ?, ?)',
                                (username, password_hash, name, role, active))
                        new_user = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
                        users_cache[username] = new_user['id']
                        count_users += 1
                except Exception as e:
                    errors.append(f"Lỗi User {row.get('username')}: {e}")
            success_msg.append(f"Đã thêm {count_users} users mới.")
        
        # Reload cache to include existing users
        all_users = query_db('SELECT id, username FROM users')
        for u in all_users:
            users_cache[u['username']] = u['id']

        # --- 1.5 Restore Categories (New) ---
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
                    
                    existing = query_db('SELECT id FROM categories WHERE name = ?', (name,), one=True)
                    if existing:
                        categories_cache[name] = existing['id']
                        # Optional: Update icon/type if needed? For now, skip to preserve existing.
                    else:
                        query_db('INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                                (name, cat_type, subtype, icon))
                        new_cat = query_db('SELECT id FROM categories WHERE name = ?', (name,), one=True)
                        categories_cache[name] = new_cat['id']
                        count_cats += 1
                except Exception as e:
                    errors.append(f"Lỗi Category {row.get('name')}: {e}")
            success_msg.append(f"Đã đồng bộ {count_cats} danh mục mới.")
        
        # Reload cache to include all categories (including pre-existing ones)
        all_cats = query_db('SELECT id, name FROM categories')
        for c in all_cats:
            categories_cache[c['name']] = c['id']

        # --- 2. Restore Fund Groups ---
        groups_cache = {} # name -> id
        if 'FundGroups' in xls.sheet_names:
            df_groups = pd.read_excel(xls, 'FundGroups')
            count_groups = 0
            for _, row in df_groups.iterrows():
                try:
                    name = str(row['name']).strip()
                    created_by_user = str(row['created_by']).strip()
                    creator_id = users_cache.get(created_by_user, 1) # Default to admin (id 1) if not found
                    
                    existing = query_db('SELECT id FROM fund_groups WHERE name = ?', (name,), one=True)
                    if existing:
                        groups_cache[name] = existing['id']
                    else:
                        query_db('INSERT INTO fund_groups (name, created_by) VALUES (?, ?)', (name, creator_id))
                        new_group = query_db('SELECT id FROM fund_groups WHERE name = ?', (name,), one=True)
                        groups_cache[name] = new_group['id']
                        count_groups += 1
                except Exception as e:
                    errors.append(f"Lỗi Group {row.get('name')}: {e}")
            success_msg.append(f"Đã thêm {count_groups} nhóm quỹ mới.")
            
        # Reload cache
        all_groups = query_db('SELECT id, name FROM fund_groups')
        for g in all_groups:
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
                        existing = query_db('SELECT id FROM fund_group_members WHERE group_id = ? AND user_id = ?', (gid, uid), one=True)
                        if not existing:
                            query_db('INSERT INTO fund_group_members (group_id, user_id) VALUES (?, ?)', (gid, uid))
                            count_members += 1
                except Exception as e:
                    errors.append(f"Lỗi Member {row.get('user_username')}: {e}")
            success_msg.append(f"Đã khôi phục {count_members} thành viên nhóm.")

        # --- 4. Restore Transactions ---
        sheet_trans = 'Transactions' if 'Transactions' in xls.sheet_names else (xls.sheet_names[0] if xls.sheet_names else None)
        if sheet_trans:
            df = pd.read_excel(xls, sheet_trans)
            
            # Cache categories (already loaded in step 1.5, but just in case)
            if not categories_cache:
                all_cats = query_db('SELECT id, name FROM categories')
                for c in all_cats:
                    categories_cache[c['name']] = c['id']
                
            count_trans = 0
            for index, row in df.iterrows():
                try:
                    # Resolve User
                    # Support both 'Username' (new format) and 'Người dùng' (old format/name)
                    user_id = None
                    if 'Username' in row and pd.notna(row['Username']):
                        user_id = users_cache.get(str(row['Username']).strip())
                    
                    if not user_id and 'Người dùng' in row:
                        # Fallback to name lookup (less reliable)
                        u_name = str(row['Người dùng']).strip()
                        # Try to find user by name
                        u = query_db('SELECT id FROM users WHERE name = ?', (u_name,), one=True)
                        if u: user_id = u['id']
                        
                    if not user_id:
                        # Create temp user if absolutely necessary, or skip?
                        # Let's create based on name if provided
                        if 'Người dùng' in row:
                             u_name = str(row['Người dùng']).strip()
                             username = u_name.lower().replace(' ', '') + f"_{int(datetime.now().timestamp())}"
                             password_hash = generate_password_hash('123456')
                             query_db('INSERT INTO users (username, password, name, role, active) VALUES (?, ?, ?, ?, ?)',
                                     (username, password_hash, u_name, 'user', 1))
                             new_u = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
                             user_id = new_u['id']
                             users_cache[username] = user_id
                    
                    if not user_id: continue # Skip if no user found
                    
                    # Resolve Category
                    cat_name = str(row['Danh mục']).strip()
                    cat_id = categories_cache.get(cat_name)
                    if not cat_id:
                        cat_type = row['Loại'] if 'Loại' in row else 'Chi'
                        query_db('INSERT INTO categories (name, type, icon) VALUES (?, ?, ?)', (cat_name, cat_type, '📝'))
                        new_cat = query_db('SELECT id FROM categories WHERE name = ?', (cat_name,), one=True)
                        cat_id = new_cat['id']
                        categories_cache[cat_name] = cat_id
                        
                    # Normalize date to YYYY-MM-DD format (no time)
                    date_val = pd.to_datetime(row['Ngày']).strftime('%Y-%m-%d')
                    amount = float(row['Số tiền'])
                    note = str(row['Ghi chú']) if 'Ghi chú' in row and pd.notna(row['Ghi chú']) else ''
                    fund_purpose = str(row['Mục đích quỹ']) if 'Mục đích quỹ' in row and pd.notna(row['Mục đích quỹ']) else None
                    trans_type = row['Loại']
                    
                    # Ensure Fund Category exists if fund_purpose is set
                    if fund_purpose:
                        fund_purpose = fund_purpose.strip()
                        # Check if this fund purpose exists in categories (as subtype='fund')
                        # We use a separate cache or query directly because funds are distinct from normal categories
                        existing_fund = query_db("SELECT id FROM categories WHERE name = ? AND subtype = 'fund'", (fund_purpose,), one=True)
                        if not existing_fund:
                            # Create it
                            # We create 2 entries (Thu and Chi) or just one? 
                            # The system seems to use name+subtype='fund' to identify funds. 
                            # Let's create one with type='Chi' (default) and one 'Thu' to be safe?
                            # Actually api_funds.py selects DISTINCT name. So one is enough.
                            # But to be clean, let's create one.
                            query_db("INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)", 
                                    (fund_purpose, 'Chi', 'fund', '💰'))
                            # Also create Thu version? Some logic might depend on it.
                            query_db("INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)", 
                                    (fund_purpose, 'Thu', 'fund', '💰'))
                    
                    query_db('''
                        INSERT INTO transactions (user_id, category_id, amount, date, type, note, fund_purpose)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, cat_id, amount, date_val, trans_type, note, fund_purpose))
                    count_trans += 1
                    
                except Exception as row_err:
                    errors.append(f"Lỗi Giao dịch dòng {index}: {str(row_err)}")
            
            success_msg.append(f"Đã import {count_trans} giao dịch.")
                
        return jsonify({
            'success': True,
            'message': '\\n'.join(success_msg),
            'errors': errors
        })

    except Exception as e:
        print(f"Lỗi khi import excel: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
