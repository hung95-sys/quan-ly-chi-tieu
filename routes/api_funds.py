"""
API Routes cho quản lý quỹ (funds) và fund groups
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import traceback
from utils.decorators import login_required, admin_required
from utils.db_utils import query_db, execute_db

bp = Blueprint('api_funds', __name__)


@bp.route('/api/fund_summary', methods=['GET'])
@login_required
def get_fund_summary():
    """Lấy tổng hợp quỹ theo mục đích cho các user trong cùng nhóm quỹ"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not found'}), 401
            
        # Get all users in same fund groups as current user
        linked_ids = {user_id}
        
        # Get all groups where current user is a member
        user_groups = query_db('''
            SELECT group_id FROM fund_group_members WHERE user_id = ?
        ''', (user_id,))
        
        if user_groups:
            # Get all members in those groups
            group_ids = [g['group_id'] for g in user_groups]
            placeholders = ','.join(['?'] * len(group_ids))
            members = query_db(f'''
                SELECT DISTINCT user_id FROM fund_group_members 
                WHERE group_id IN ({placeholders})
            ''', group_ids)
            
            for m in members:
                linked_ids.add(m['user_id'])
            
        # Get names for these users
        placeholders = ','.join(['?'] * len(linked_ids))
        users_info = query_db(f'SELECT id, name, username FROM users WHERE id IN ({placeholders})', list(linked_ids))
        user_map = {u['id']: (u['name'] if u['name'] else u['username']) for u in users_info}
        
        # 2. Get all fund purposes (categories with subtype='fund')
        purposes_rows = query_db("SELECT DISTINCT name, icon FROM categories WHERE subtype = 'fund'")
        purposes = []
        for row in purposes_rows:
            purposes.append({'name': row['name'], 'icon': row['icon']})
            
        if not purposes:
            purposes = [{'name': 'Tiết kiệm', 'icon': '💰'}]
            
        # 3. Calculate totals
        result = []
        for purpose in purposes:
            p_name = purpose['name']
            row_data = {'purpose': p_name, 'icon': purpose['icon'], 'users': {}, 'total': 0}
            
            for uid in linked_ids:
                u_name = user_map.get(uid, f'User {uid}') # Safe lookup
                
                # Sum Thu
                thu = query_db('''
                    SELECT SUM(amount) as total FROM transactions 
                    WHERE user_id = ? AND type = 'Thu' AND fund_purpose = ?
                ''', (uid, p_name), one=True)
                thu_amount = thu['total'] if thu and thu['total'] else 0
                
                # Sum Chi
                chi = query_db('''
                    SELECT SUM(amount) as total FROM transactions 
                    WHERE user_id = ? AND type = 'Chi' AND fund_purpose = ?
                ''', (uid, p_name), one=True)
                chi_amount = chi['total'] if chi and chi['total'] else 0
                
                amount = thu_amount - chi_amount
                row_data['users'][u_name] = amount
                row_data['total'] += amount
                
            if row_data['total'] > 0 or any(val > 0 for val in row_data['users'].values()):
                result.append(row_data)
                
        return jsonify({
            'purposes': result,
            'linked_users': [user_map.get(uid, f'User {uid}') for uid in linked_ids] # Safe lookup
        })
        
    except Exception as e:
        print(f"Lỗi khi lấy fund summary: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'purposes': []}), 500


@bp.route('/api/quy_purposes', methods=['GET'])
@login_required
def get_quy_purposes():
    """Lấy danh sách tất cả mục đích quỹ"""
    try:
        rows = query_db("SELECT DISTINCT name, icon FROM categories WHERE subtype = 'fund'")
        purposes = [{'name': r['name'], 'icon': r['icon']} for r in rows]
        return jsonify({'purposes': purposes})
    except Exception as e:
        print(f"Lỗi khi lấy mục đích quỹ: {e}")
        return jsonify({'error': str(e), 'purposes': []}), 500


@bp.route('/api/quy_purposes_thu', methods=['GET'])
@login_required
def get_quy_purposes_thu():
    """Lấy danh sách mục đích quỹ Thu"""
    try:
        rows = query_db("SELECT name, icon FROM categories WHERE subtype = 'fund' AND type = 'Thu'")
        purposes = [{'name': r['name'], 'icon': r['icon']} for r in rows]
        return jsonify({'purposes': purposes})
    except Exception as e:
        print(f"Lỗi khi lấy mục đích quỹ Thu: {e}")
        return jsonify({'error': str(e), 'purposes': []}), 500


@bp.route('/api/quy_purposes_chi', methods=['GET'])
@login_required
def get_quy_purposes_chi():
    """Lấy danh sách mục đích quỹ Chi"""
    try:
        rows = query_db("SELECT name, icon FROM categories WHERE subtype = 'fund' AND type = 'Chi'")
        purposes = [{'name': r['name'], 'icon': r['icon']} for r in rows]
        return jsonify({'purposes': purposes})
    except Exception as e:
        print(f"Lỗi khi lấy mục đích quỹ Chi: {e}")
        return jsonify({'error': str(e), 'purposes': []}), 500


# ============================================
# FUND GROUPS API (New - replaces fund_links)
# ============================================

@bp.route('/api/fund_groups', methods=['GET'])
@login_required
def get_fund_groups():
    """Lấy danh sách tất cả nhóm quỹ mà user tham gia"""
    try:
        user_id = session.get('user_id')
        
        # Get all groups where user is a member
        groups = query_db('''
            SELECT fg.id, fg.name, fg.created_at, fg.created_by,
                   u.name as creator_name, u.username as creator_username
            FROM fund_groups fg
            JOIN fund_group_members fgm ON fg.id = fgm.group_id
            JOIN users u ON fg.created_by = u.id
            WHERE fgm.user_id = ?
            ORDER BY fg.created_at DESC
        ''', (user_id,))
        
        result = []
        for g in groups:
            # Get member count
            members = query_db('''
                SELECT COUNT(*) as count FROM fund_group_members WHERE group_id = ?
            ''', (g['id'],), one=True)
            
            result.append({
                'id': g['id'],
                'name': g['name'],
                'created_at': g['created_at'],
                'created_by': g['creator_name'] or g['creator_username'],
                'member_count': members['count'] if members else 0,
                'is_owner': g['created_by'] == user_id
            })
            
        return jsonify({'groups': result})
    except Exception as e:
        print(f"Lỗi khi lấy fund groups: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'groups': []}), 500


@bp.route('/api/fund_groups', methods=['POST'])
@admin_required
def create_fund_group():
    """Tạo nhóm quỹ mới"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        member_ids = data.get('member_ids', [])
        
        if not name:
            return jsonify({'error': 'Vui lòng nhập tên nhóm'}), 400
            
        user_id = session.get('user_id')
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create group
        group_id = execute_db(
            'INSERT INTO fund_groups (name, created_by, created_at) VALUES (?, ?, ?)',
            (name, user_id, created_at)
        )
        
        # Add creator as member
        execute_db(
            'INSERT INTO fund_group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)',
            (group_id, user_id, created_at)
        )
        
        # Add other members
        for mid in member_ids:
            if mid != user_id:
                try:
                    execute_db(
                        'INSERT INTO fund_group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)',
                        (group_id, mid, created_at)
                    )
                except:
                    pass  # Ignore duplicates
                    
        return jsonify({'success': True, 'message': 'Tạo nhóm quỹ thành công', 'group_id': group_id})
        
    except Exception as e:
        print(f"Lỗi khi tạo fund group: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/fund_groups/<int:group_id>', methods=['PUT'])
@admin_required
def update_fund_group(group_id):
    """Cập nhật thông tin nhóm quỹ"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Vui lòng nhập tên nhóm'}), 400
            
        execute_db('UPDATE fund_groups SET name = ? WHERE id = ?', (name, group_id))
        return jsonify({'success': True, 'message': 'Cập nhật nhóm quỹ thành công'})
        
    except Exception as e:
        print(f"Lỗi khi cập nhật fund group: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/fund_groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_fund_group(group_id):
    """Xóa nhóm quỹ"""
    try:
        # Delete members first (due to foreign key)
        execute_db('DELETE FROM fund_group_members WHERE group_id = ?', (group_id,))
        execute_db('DELETE FROM fund_groups WHERE id = ?', (group_id,))
        return jsonify({'success': True, 'message': 'Xóa nhóm quỹ thành công'})
    except Exception as e:
        print(f"Lỗi khi xóa fund group: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/fund_groups/<int:group_id>/members', methods=['GET'])
@login_required
def get_group_members(group_id):
    """Lấy danh sách thành viên của nhóm"""
    try:
        members = query_db('''
            SELECT u.id, u.username, u.name
            FROM fund_group_members fgm
            JOIN users u ON fgm.user_id = u.id
            WHERE fgm.group_id = ?
        ''', (group_id,))
        
        result = [{'id': m['id'], 'name': m['name'] or m['username']} for m in members]
        return jsonify({'members': result})
        
    except Exception as e:
        print(f"Lỗi khi lấy group members: {e}")
        return jsonify({'error': str(e), 'members': []}), 500


@bp.route('/api/fund_groups/<int:group_id>/members', methods=['POST'])
@admin_required
def add_group_member(group_id):
    """Thêm thành viên vào nhóm"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Vui lòng chọn người dùng'}), 400
            
        # Check if already member
        existing = query_db(
            'SELECT id FROM fund_group_members WHERE group_id = ? AND user_id = ?',
            (group_id, user_id), one=True
        )
        
        if existing:
            return jsonify({'error': 'Người dùng đã là thành viên của nhóm'}), 400
            
        joined_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execute_db(
            'INSERT INTO fund_group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)',
            (group_id, user_id, joined_at)
        )
        
        return jsonify({'success': True, 'message': 'Thêm thành viên thành công'})
        
    except Exception as e:
        print(f"Lỗi khi thêm group member: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/fund_groups/<int:group_id>/members/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_group_member(group_id, user_id):
    """Xóa thành viên khỏi nhóm"""
    try:
        execute_db(
            'DELETE FROM fund_group_members WHERE group_id = ? AND user_id = ?',
            (group_id, user_id)
        )
        return jsonify({'success': True, 'message': 'Xóa thành viên thành công'})
    except Exception as e:
        print(f"Lỗi khi xóa group member: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/fund_groups/all', methods=['GET'])
@admin_required
def get_all_fund_groups():
    """Admin: Lấy tất cả nhóm quỹ"""
    try:
        groups = query_db('''
            SELECT fg.id, fg.name, fg.created_at, fg.created_by,
                   u.name as creator_name, u.username as creator_username
            FROM fund_groups fg
            JOIN users u ON fg.created_by = u.id
            ORDER BY fg.created_at DESC
        ''')
        
        result = []
        for g in groups:
            # Get members
            members = query_db('''
                SELECT u.id, u.name, u.username
                FROM fund_group_members fgm
                JOIN users u ON fgm.user_id = u.id
                WHERE fgm.group_id = ?
            ''', (g['id'],))
            
            result.append({
                'id': g['id'],
                'name': g['name'],
                'created_at': g['created_at'],
                'created_by': g['creator_name'] or g['creator_username'],
                'members': [{'id': m['id'], 'name': m['name'] or m['username']} for m in members]
            })
            
        return jsonify({'groups': result})
    except Exception as e:
        print(f"Lỗi khi lấy all fund groups: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'groups': []}), 500

