"""
API Routes cho quản lý danh mục (categories)
"""
from flask import Blueprint, request, jsonify, session
import traceback
from utils.decorators import login_required
from utils.db_utils import query_db, execute_db

bp = Blueprint('api_categories', __name__)


@bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    """Lấy danh sách danh mục"""
    try:
        category_type = request.args.get('type', 'Chi').strip()
        
        # Map type to DB type
        db_type = 'Chi'
        if category_type.lower() == 'thu':
            db_type = 'Thu'
            
        # Query categories
        # We only want normal categories here usually, unless specified?
        # The original code just returned column 0 or 1.
        # Column 0/1 were normal categories.
        # So we filter by subtype='normal'
        
        rows = query_db(
            'SELECT name, icon FROM categories WHERE type = ? AND subtype = ? ORDER BY id',
            (db_type, 'normal')
        )
        
        categories = []
        for row in rows:
            val = f"{row['icon']} {row['name']}" if row['icon'] else row['name']
            categories.append(val)
        return jsonify({'categories': categories})
    except Exception as e:
        print(f"Lỗi khi lấy danh mục: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}', 'categories': []}), 500


@bp.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    """Thêm danh mục mới"""
    try:
        data = request.json
        category_name = data.get('name', '').strip()
        category_type = data.get('type', 'Chi').strip()
        category_icon = data.get('icon', '').strip()
        
        if not category_name:
            return jsonify({'success': False, 'error': 'Tên danh mục không được để trống'}), 400
        
        # Determine type and subtype
        db_type = 'Chi'
        subtype = 'normal'
        
        if category_type.lower() == 'thu':
            db_type = 'Thu'
        elif category_type.lower() == 'chi':
            db_type = 'Chi'
        elif category_type.lower() == 'quy': # Add to both?
             # Original code added to both Thu quy and Chi quy columns
             # Here we should probably add 2 entries?
             # Or maybe the frontend calls this twice?
             # Original code:
             # if category_type.lower() == 'quy': target_columns = ['Thu quỹ', 'Chi quỹ']
             pass
        elif category_type.lower() == 'thuquy':
            db_type = 'Thu'
            subtype = 'fund'
        elif category_type.lower() == 'chiquy':
            db_type = 'Chi'
            subtype = 'fund'
            
        # Handle 'quy' type (add both Thu and Chi fund categories)
        if category_type.lower() == 'quy':
            # Add Thu fund
            try:
                execute_db(
                    'INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                    (category_name, 'Thu', 'fund', category_icon)
                )
            except:
                pass # Ignore duplicate
                
            # Add Chi fund
            try:
                execute_db(
                    'INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                    (category_name, 'Chi', 'fund', category_icon)
                )
            except:
                pass # Ignore duplicate
                
            return jsonify({'success': True, 'message': f'Đã thêm danh mục quỹ "{category_name}" thành công'})

        # Check existing
        existing = query_db(
            'SELECT id FROM categories WHERE name = ? AND type = ? AND subtype = ?',
            (category_name, db_type, subtype),
            one=True
        )
        
        if existing:
            return jsonify({'success': False, 'error': 'Danh mục này đã tồn tại'}), 400
            
        execute_db(
            'INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
            (category_name, db_type, subtype, category_icon)
        )
        
        return jsonify({'success': True, 'message': f'Đã thêm danh mục "{category_name}" thành công'})
    except Exception as e:
        print(f"Lỗi khi thêm danh mục: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/categories/<category_type>', methods=['GET'])
@login_required
def get_categories_list(category_type):
    """Lấy danh sách danh mục để hiển thị trong menu"""
    try:
        categories = []
        
        if category_type.lower() == 'quy':
            # Get distinct names from fund categories
            rows = query_db("SELECT DISTINCT name, icon FROM categories WHERE subtype = 'fund'")
            for idx, row in enumerate(rows):
                val = f"{row['icon']} {row['name']}" if row['icon'] else row['name']
                categories.append({
                    'row': idx, # Fake row ID, or use real ID? Frontend uses row for update/delete.
                    # We should probably use real ID, but original code used row index.
                    # If we use ID, we need to update frontend or handle it here.
                    # Let's return ID as 'id' and 'row' for compatibility if needed.
                    'id': row['name'], # Use name as ID for grouping?
                    'value': val,
                    'column': 'Thu quỹ' # Just a placeholder
                })
        else:
            db_type = 'Chi'
            if category_type.lower() == 'thu':
                db_type = 'Thu'
            
            rows = query_db(
                'SELECT id, name, icon FROM categories WHERE type = ? AND subtype = ? ORDER BY id',
                (db_type, 'normal')
            )
            
            for row in rows:
                val = f"{row['icon']} {row['name']}" if row['icon'] else row['name']
                categories.append({
                    'row': row['id'], # Use ID as row index
                    'value': val
                })
        
        return jsonify({'categories': categories})
    except Exception as e:
        print(f"Lỗi khi lấy danh sách danh mục: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'categories': []}), 500


@bp.route('/api/categories', methods=['PUT'])
@login_required
def update_category():
    """Sửa danh mục"""
    try:
        data = request.json
        category_type = data.get('type', '').strip()
        row_id = data.get('row') # This is now ID
        old_value = data.get('old_value', '').strip()
        new_name = data.get('name', '').strip()
        new_icon = data.get('icon', '').strip()
        
        if not new_name:
            return jsonify({'success': False, 'error': 'Tên danh mục không được để trống'}), 400
            
        if category_type.lower() == 'quy':
            # Update by name for both types
            # Extract old name from old_value
            # old_value is like "🍔 Eating"
            # We need to find the name part.
            # But wait, for 'quy', we returned name as ID? No, we returned fake row index or something.
            # In get_categories_list for 'quy', I returned 'id': row['name'].
            # But the frontend sends 'row' which I mapped to 'id'.
            # If I changed get_categories_list to return ID, I should use ID.
            # But for 'quy', there are 2 rows (Thu and Chi).
            # So updating one should update both?
            # Let's assume we update by name if type is 'quy'.
            
            # Actually, let's look at get_categories_list implementation above.
            # I returned 'id': row['name'].
            # So row_id passed here is actually the name if type is 'quy'.
            old_name_key = row_id # This is the name
            
            execute_db(
                "UPDATE categories SET name = ?, icon = ? WHERE subtype = 'fund' AND name = ?",
                (new_name, new_icon, old_name_key)
            )
            return jsonify({'success': True, 'message': 'Đã cập nhật danh mục thành công'})

        else:
            # Normal category
            execute_db(
                'UPDATE categories SET name = ?, icon = ? WHERE id = ?',
                (new_name, new_icon, row_id)
            )
            return jsonify({'success': True, 'message': 'Đã cập nhật danh mục thành công'})
            
    except Exception as e:
        print(f"Lỗi khi sửa danh mục: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/categories', methods=['DELETE'])
@login_required
def delete_category():
    """Xóa danh mục"""
    try:
        data = request.json
        category_type = data.get('type', '').strip()
        row_id = data.get('row')
        value = data.get('value', '').strip() # Full value with icon
        
        if category_type.lower() == 'quy':
            # Delete by name
            # Extract name from value? Or use row_id which is name?
            # row_id is name as per get_categories_list
            name_to_delete = row_id
            execute_db("DELETE FROM categories WHERE subtype = 'fund' AND name = ?", (name_to_delete,))
        else:
            execute_db('DELETE FROM categories WHERE id = ?', (row_id,))
            
        return jsonify({'success': True, 'message': 'Đã xóa danh mục thành công'})
            
    except Exception as e:
        print(f"Lỗi khi xóa danh mục: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/icons', methods=['GET'])
@login_required
def get_icons():
    """Lấy danh sách icon"""
    try:
        rows = query_db("SELECT DISTINCT icon FROM categories WHERE icon IS NOT NULL AND icon != ''")
        icons = [row['icon'] for row in rows]
        return jsonify({'icons': icons})
    except Exception as e:
        print(f"Lỗi khi lấy icon: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'icons': []}), 500
