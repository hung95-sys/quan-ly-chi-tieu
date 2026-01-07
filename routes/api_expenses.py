"""
API Routes cho quản lý chi tiêu (expenses), calendar, reports
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import traceback
from utils.decorators import login_required
from utils.db_utils import query_db, execute_db

bp = Blueprint('api_expenses', __name__)


@bp.route('/api/calendar', methods=['GET'])
@login_required
def get_calendar_data():
    """API lấy dữ liệu lịch cho calendar view"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not found'}), 401
        
    transactions_by_date = {}
    daily_totals = {}
    monthly_summary = {'thu': 0, 'chi': 0, 'tong': 0}
    
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    try:
        # Build query
        sql = '''
            SELECT t.id, t.date, t.type, t.amount, t.note, t.fund_purpose, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        '''
        params = [user_id]
        
        if month is not None and year is not None:
            # Filter by month/year
            # SQLite date is text YYYY-MM-DD
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
                
            sql += " AND t.date >= ? AND t.date < ?"
            params.extend([start_date, end_date])
            
        # Get fund icons map
        fund_rows = query_db("SELECT name, icon FROM categories WHERE subtype = 'fund'")
        fund_icons = {row['name']: row['icon'] for row in fund_rows}
            
        rows = query_db(sql, params)
        
        for row in rows:
            try:
                date_str = row['date'] # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
                # Try to parse with multiple formats
                try:
                    ngay = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    try:
                        ngay = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Try ISO format with T
                        ngay = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                date_key = ngay.strftime('%d/%m/%Y')
                day_name = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'][ngay.weekday()]
                
                if date_key not in transactions_by_date:
                    transactions_by_date[date_key] = {
                        'date': date_key,
                        'day_name': day_name,
                        'transactions': []
                    }
                    daily_totals[date_key] = {'thu': 0, 'chi': 0}
                
                loai = row['type'].lower()
                so_tien = row['amount']
                danh_muc = row['category_name']
                icon = row['category_icon']
                
                # Handle fund icon
                fund_purpose = row['fund_purpose']
                quy_display = fund_purpose or ''
                
                if fund_purpose and fund_purpose in fund_icons:
                    icon_char = fund_icons[fund_purpose]
                    if icon_char:
                        quy_display = f"{icon_char} {fund_purpose}"

                if icon:
                    danh_muc = f"{icon} {danh_muc}"
                
                transaction = {
                    'row_id': row['id'],  # Use DB ID as row_id
                    'loai': loai,
                    'danh_muc': danh_muc,
                    'so_tien': so_tien,
                    'ghi_chu': row['note'] or '',
                    'quy': quy_display,
                    'ngay': date_key
                }
                transactions_by_date[date_key]['transactions'].append(transaction)
                
                # Calculate totals
                cat_name_only = row['category_name']
                
                if loai == 'thu':
                    if cat_name_only != 'Thu quỹ':
                        daily_totals[date_key]['thu'] += so_tien
                        monthly_summary['thu'] += so_tien
                    else:
                        daily_totals[date_key]['chi'] += so_tien
                        monthly_summary['chi'] += so_tien
                elif loai == 'chi':
                    if cat_name_only != 'Chi quỹ':
                        daily_totals[date_key]['chi'] += so_tien
                        monthly_summary['chi'] += so_tien
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
                
        monthly_summary['tong'] = monthly_summary['thu'] - monthly_summary['chi']
        
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu lịch: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    sorted_dates = sorted(transactions_by_date.keys(), key=lambda x: datetime.strptime(x, '%d/%m/%Y'), reverse=True)
    sorted_transactions = [transactions_by_date[date] for date in sorted_dates]
    
    return jsonify({
        'transactions_by_date': sorted_transactions,
        'daily_totals': daily_totals,
        'monthly_summary': monthly_summary
    })


@bp.route('/api/user_yearly_report', methods=['GET'])
@login_required
def get_yearly_report():
    """API trả về báo cáo theo năm"""
    try:
        years = int(request.args.get('years', 5))
        user_id = session.get('user_id')
        
        current_year = datetime.now().year
        start_year = current_year - years + 1
        
        sql = '''
            SELECT strftime('%Y', date) as year, type, amount, fund_purpose
            FROM transactions
            WHERE user_id = ? AND strftime('%Y', date) >= ?
        '''
        rows = query_db(sql, (user_id, str(start_year)))
        
        report_data = {} # year -> {income, expense, fund}
        for y in range(start_year, current_year + 1):
            report_data[y] = {'year': y, 'income': 0, 'expense': 0, 'fund': 0}
            
        for row in rows:
            y = int(row['year'])
            if y in report_data:
                amount = row['amount']
                if row['type'] == 'Thu':
                    report_data[y]['income'] += amount
                elif row['type'] == 'Chi':
                    report_data[y]['expense'] += amount
                    
                if row['fund_purpose']:
                    report_data[y]['fund'] += amount
                    
        result = [report_data[y] for y in sorted(report_data.keys())]
        return jsonify({'years': result})
        
    except Exception as e:
        print(f"Lỗi khi lấy báo cáo năm: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/user_monthly_report', methods=['GET'])
@login_required
def get_monthly_report():
    """API trả về báo cáo theo tháng trong năm hiện tại"""
    try:
        user_id = session.get('user_id')
        current_year = datetime.now().year
        
        sql = '''
            SELECT strftime('%m', date) as month, type, amount, fund_purpose
            FROM transactions
            WHERE user_id = ? AND strftime('%Y', date) = ?
        '''
        rows = query_db(sql, (user_id, str(current_year)))
        
        months_data = {m: {'month': m, 'income': 0, 'expense': 0, 'fund': 0} for m in range(1, 13)}
        
        for row in rows:
            m = int(row['month'])
            amount = row['amount']
            if row['type'] == 'Thu':
                months_data[m]['income'] += amount
            elif row['type'] == 'Chi':
                months_data[m]['expense'] += amount
                
            if row['fund_purpose']:
                months_data[m]['fund'] += amount
                
        result = [months_data[m] for m in range(1, 13)]
        return jsonify({'months': result})
        
    except Exception as e:
        print(f"Lỗi khi lấy báo cáo tháng: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/user_daily_report', methods=['GET'])
@login_required
def get_daily_report():
    """API trả về báo cáo theo ngày trong tháng hiện tại"""
    try:
        user_id = session.get('user_id')
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Get number of days in current month
        import calendar
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        
        sql = '''
            SELECT strftime('%d', date) as day, type, amount, fund_purpose
            FROM transactions
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        '''
        rows = query_db(sql, (user_id, str(current_year), str(current_month).zfill(2)))
        
        days_data = {d: {'day': d, 'income': 0, 'expense': 0, 'fund': 0} for d in range(1, days_in_month + 1)}
        
        for row in rows:
            d = int(row['day'])
            amount = row['amount']
            if row['type'] == 'Thu':
                days_data[d]['income'] += amount
            elif row['type'] == 'Chi':
                days_data[d]['expense'] += amount
                
            if row['fund_purpose']:
                days_data[d]['fund'] += amount
                
        result = [days_data[d] for d in range(1, days_in_month + 1)]
        return jsonify({'days': result, 'month': current_month, 'year': current_year})
        
    except Exception as e:
        print(f"Lỗi khi lấy báo cáo ngày: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/user_category_breakdown', methods=['GET'])
@login_required
def get_category_breakdown():
    """API trả về phân bổ chi tiêu theo danh mục trong tháng hiện tại"""
    try:
        user_id = session.get('user_id')
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        sql = '''
            SELECT c.name as category_name, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'Chi' 
                AND strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
            GROUP BY c.name
            ORDER BY total DESC
        '''
        rows = query_db(sql, (user_id, str(current_year), str(current_month).zfill(2)))
        
        categories = []
        for row in rows:
            categories.append({
                'name': row['category_name'],
                'amount': row['total']
            })
                
        return jsonify({
            'categories': categories, 
            'month': current_month, 
            'year': current_year
        })
        
    except Exception as e:
        print(f"Lỗi khi lấy phân bổ danh mục: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/expenses', methods=['POST'])
@login_required
def add_expense():
    """Thêm chi tiêu mới"""
    data = request.get_json()
    
    ngay = data.get('ngay', '') # DD/MM/YYYY
    loai = data.get('loai', 'Chi')
    danh_muc_full = data.get('danh_muc', '') # Icon + Name
    so_tien = data.get('so_tien', 0)
    ghi_chu = data.get('ghi_chu', '')
    quy = data.get('quy', '')
    
    if not ngay or not danh_muc_full or so_tien <= 0:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
    
    user_id = session.get('user_id')
    
    try:
        # Parse date
        try:
            date_obj = datetime.strptime(ngay, '%d/%m/%Y')
            date_str = date_obj.strftime('%Y-%m-%d')
        except:
            return jsonify({'error': 'Định dạng ngày không hợp lệ'}), 400
            
        # Parse category
        import re
        match = re.search(r'[A-Za-zÀ-ỹ]', danh_muc_full)
        if match:
            cat_name = danh_muc_full[match.start():].strip()
        else:
            cat_name = danh_muc_full
            
        # Find category ID
        cat = query_db('SELECT id FROM categories WHERE name = ? AND type = ?', (cat_name, loai), one=True)
        if not cat:
            # Create if not exists
            icon = ''
            if match and match.start() > 0:
                icon = danh_muc_full[:match.start()].strip()
                
            execute_db(
                'INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                (cat_name, loai, 'normal', icon)
            )
            cat = query_db('SELECT id FROM categories WHERE name = ? AND type = ?', (cat_name, loai), one=True)
        
        cat_id = cat['id']
        
        execute_db(
            '''INSERT INTO transactions 
               (user_id, date, type, category_id, amount, note, fund_purpose) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, date_str, loai, cat_id, float(so_tien), ghi_chu, quy)
        )
        
        return jsonify({'success': True, 'message': 'Thêm chi tiêu thành công!'})
        
    except Exception as e:
        print(f"Lỗi khi thêm chi tiêu: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/expenses/<int:row_id>', methods=['PUT'])
@login_required
def update_expense(row_id):
    """Sửa giao dịch"""
    data = request.get_json()
    
    ngay = data.get('ngay', '')
    loai = data.get('loai', '')
    danh_muc_full = data.get('danh_muc', '')
    so_tien = data.get('so_tien', 0)
    ghi_chu = data.get('ghi_chu', '')
    quy = data.get('quy', '')
    
    if not ngay or not danh_muc_full:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
        
    user_id = session.get('user_id')
    
    try:
        # Parse date
        date_obj = datetime.strptime(ngay, '%d/%m/%Y')
        date_str = date_obj.strftime('%Y-%m-%d')
        
        # Parse category
        import re
        match = re.search(r'[A-Za-zÀ-ỹ]', danh_muc_full)
        if match:
            cat_name = danh_muc_full[match.start():].strip()
        else:
            cat_name = danh_muc_full
            
        cat = query_db('SELECT id FROM categories WHERE name = ? AND type = ?', (cat_name, loai), one=True)
        if not cat:
             # Create if not exists
            icon = ''
            if match and match.start() > 0:
                icon = danh_muc_full[:match.start()].strip()
            execute_db(
                'INSERT INTO categories (name, type, subtype, icon) VALUES (?, ?, ?, ?)',
                (cat_name, loai, 'normal', icon)
            )
            cat = query_db('SELECT id FROM categories WHERE name = ? AND type = ?', (cat_name, loai), one=True)
            
        cat_id = cat['id']
        
        # Update
        # Verify ownership
        trans = query_db('SELECT id FROM transactions WHERE id = ? AND user_id = ?', (row_id, user_id), one=True)
        if not trans:
            return jsonify({'error': 'Không tìm thấy giao dịch'}), 404
            
        execute_db(
            '''UPDATE transactions 
               SET date=?, type=?, category_id=?, amount=?, note=?, fund_purpose=?
               WHERE id=?''',
            (date_str, loai, cat_id, float(so_tien), ghi_chu, quy, row_id)
        )
        
        return jsonify({'success': True, 'message': 'Sửa giao dịch thành công!'})
        
    except Exception as e:
        print(f"Lỗi khi sửa chi tiêu: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@bp.route('/api/expenses/<int:row_id>', methods=['DELETE'])
@login_required
def delete_expense(row_id):
    """Xóa giao dịch"""
    user_id = session.get('user_id')
    
    try:
        # Verify ownership
        trans = query_db('SELECT id FROM transactions WHERE id = ? AND user_id = ?', (row_id, user_id), one=True)
        if not trans:
            return jsonify({'error': 'Không tìm thấy giao dịch'}), 404
            
        execute_db('DELETE FROM transactions WHERE id = ?', (row_id,))
        
        return jsonify({'success': True, 'message': 'Xóa giao dịch thành công!'})
        
    except Exception as e:
        print(f"Lỗi khi xóa chi tiêu: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500
