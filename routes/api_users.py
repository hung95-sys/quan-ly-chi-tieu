"""
API Routes cho quản lý users
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import traceback
from utils.decorators import login_required, admin_required
from utils.db_utils import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('api_users', __name__)


@bp.route('/api/time')
def get_time():
    return jsonify({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': 'Chào mừng đến với web Python!'
    })


@bp.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        'received': data,
        'message': 'Dữ liệu đã được nhận thành công!'
    })


@bp.route('/api/users', methods=['GET'])
@login_required
def get_all_users():
    """Lấy danh sách tất cả users"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        users_rows = query_db('SELECT * FROM users')
        users = []
        for row in users_rows:
            users.append({
                'username': row['username'],
                'name': row['name'],
                'role': row['role'],
                'active': bool(row['active'])
            })
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/users', methods=['POST'])
@admin_required
def add_user():
    """Thêm user mới"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    role = data.get('role', 'user').strip()
    active = data.get('active', True)
    
    if not username or not password:
        return jsonify({'error': 'Tên đăng nhập và mật khẩu không được để trống'}), 400
    
    try:
        # Check existing
        existing = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
        if existing:
            return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400
        
        hashed_password = generate_password_hash(password)
        user_name = name if name else username
        
        execute_db(
            'INSERT INTO users (username, password, name, role, active) VALUES (?, ?, ?, ?, ?)',
            (username, hashed_password, user_name, role, active)
        )
        
        return jsonify({'success': True, 'message': f'Thêm tài khoản "{username}" thành công!'})
    except Exception as e:
        print(f"Exception in add_user: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/users/<username>', methods=['PUT'])
@admin_required
def update_user(username):
    """Sửa thông tin user"""
    data = request.get_json()
    new_username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    role = data.get('role', 'user').strip()
    active = data.get('active', True)
    
    if not new_username:
        return jsonify({'error': 'Tên đăng nhập không được để trống'}), 400
    
    try:
        user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        if not user:
            return jsonify({'error': 'Không tìm thấy tài khoản'}), 404
        
        user_id = user['id']
        
        # Check if new username exists (if changed)
        if new_username != username:
            existing = query_db('SELECT id FROM users WHERE username = ?', (new_username,), one=True)
            if existing:
                return jsonify({'error': 'Tên đăng nhập mới đã tồn tại'}), 400
        
        new_name = name if name else new_username
        
        if password:
            hashed_password = generate_password_hash(password)
            execute_db(
                'UPDATE users SET username=?, password=?, name=?, role=?, active=? WHERE id=?',
                (new_username, hashed_password, new_name, role, active, user_id)
            )
        else:
            execute_db(
                'UPDATE users SET username=?, name=?, role=?, active=? WHERE id=?',
                (new_username, new_name, role, active, user_id)
            )
            
        # Update session if current user
        if session.get('user') == username:
            session['user'] = new_username
            session['name'] = new_name
            session['role'] = role
            
        return jsonify({'success': True, 'message': 'Cập nhật tài khoản thành công!'})
        
    except Exception as e:
        print(f"Exception in update_user: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/users/<username>', methods=['DELETE'])
@admin_required
def delete_user(username):
    """Xóa user"""
    if session.get('user') == username:
        return jsonify({'error': 'Không thể xóa tài khoản của chính bạn'}), 400
        
    try:
        user = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
        if not user:
            return jsonify({'error': 'Không tìm thấy tài khoản'}), 404
            
        # Delete related data first (optional, or rely on cascade if configured, but sqlite default is off)
        # We should probably keep transactions but maybe nullify user_id or just delete them?
        # For now, let's delete the user. Transactions will be orphaned or we can delete them.
        # Let's delete transactions for clean up.
        execute_db('DELETE FROM transactions WHERE user_id = ?', (user['id'],))
        execute_db('DELETE FROM fund_links WHERE user1_id = ? OR user2_id = ?', (user['id'], user['id']))
        execute_db('DELETE FROM fund_group_members WHERE user_id = ?', (user['id'],))
        execute_db('DELETE FROM users WHERE id = ?', (user['id'],))
        
        return jsonify({'success': True, 'message': 'Xóa tài khoản thành công!'})
    except Exception as e:
        print(f"Exception in delete_user: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Đổi mật khẩu"""
    data = request.get_json()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not current_password or not new_password or not confirm_password:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'Mật khẩu mới và xác nhận không khớp'}), 400
    
    username = session.get('user')
    
    try:
        user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        if not user or not check_password_hash(user['password'], current_password):
            return jsonify({'error': 'Mật khẩu hiện tại không đúng'}), 400
            
        hashed_new_password = generate_password_hash(new_password)
        execute_db('UPDATE users SET password = ? WHERE id = ?', (hashed_new_password, user['id']))
        
        return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công!'})
    except Exception as e:
        print(f"Exception in change_password: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500
