"""
Routes chính: dashboard, chi_tieu, admin
"""
from flask import Blueprint, render_template, session
from datetime import datetime
from utils.decorators import login_required, admin_required
from utils.db_utils import query_db

bp = Blueprint('main', __name__)


@bp.route('/dashboard')
@login_required
def dashboard():
    """Trang dashboard với thống kê tài chính"""
    current_user = {
        'username': session.get('user'),
        'name': session.get('name'),
        'role': session.get('role')
    }
    
    user_id = session.get('user_id')
    if not user_id:
        # Should not happen due to login_required but good for safety
        return render_template('login.html')

    # Lấy tháng và năm hiện tại
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    summary = {
        'total_income': 0,
        'total_expense': 0,
        'balance': 0,
        'total_fund': 0
    }
    
    try:
        # 1. Calculate Personal Income and Expense for Current Month
        start_date = f"{current_year}-{current_month:02d}-01"
        if current_month == 12:
            end_date = f"{current_year+1}-01-01"
        else:
            end_date = f"{current_year}-{current_month+1:02d}-01"
            
        # Calculate Total Income (excluding 'Thu quỹ')
        sql_income = '''
            SELECT SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.date >= ? AND t.date < ? 
            AND t.type = 'Thu' AND (c.name != 'Thu quỹ' OR c.name IS NULL)
        '''
        res_income = query_db(sql_income, (user_id, start_date, end_date), one=True)
        summary['total_income'] = res_income['total'] if res_income and res_income['total'] else 0

        # Calculate Total Expense (excluding 'Chi quỹ', but including 'Thu quỹ' as it's money leaving personal account)
        # Note: 'Thu quỹ' transactions are type='Thu' but logically are personal expenses (transfer to fund).
        # However, the original code logic was:
        # if type == 'Thu' and cat == 'Thu quỹ': total_expense += amount
        # if type == 'Chi' and cat != 'Chi quỹ': total_expense += amount
        
        # Expense part 1: Normal expenses (Type 'Chi', not 'Chi quỹ')
        sql_expense_normal = '''
            SELECT SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.date >= ? AND t.date < ? 
            AND t.type = 'Chi' AND (c.name != 'Chi quỹ' OR c.name IS NULL)
        '''
        res_exp_normal = query_db(sql_expense_normal, (user_id, start_date, end_date), one=True)
        exp_normal = res_exp_normal['total'] if res_exp_normal and res_exp_normal['total'] else 0
        
        # Expense part 2: Fund contributions (Type 'Thu', cat 'Thu quỹ')
        sql_expense_fund = '''
            SELECT SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.date >= ? AND t.date < ? 
            AND t.type = 'Thu' AND c.name = 'Thu quỹ'
        '''
        res_exp_fund = query_db(sql_expense_fund, (user_id, start_date, end_date), one=True)
        exp_fund = res_exp_fund['total'] if res_exp_fund and res_exp_fund['total'] else 0
        
        summary['total_expense'] = exp_normal + exp_fund
                
        summary['balance'] = summary['total_income'] - summary['total_expense']
        
        # 2. Calculate Total Fund (All time, Fund Groups)
        linked_ids = {user_id}
        
        # Get all groups where current user is a member
        user_groups = query_db('''
            SELECT group_id FROM fund_group_members WHERE user_id = ?
        ''', (user_id,))
        
        if user_groups:
            # Get all members in those groups
            group_ids = [g['group_id'] for g in user_groups]
            placeholders_g = ','.join(['?'] * len(group_ids))
            members = query_db(f'''
                SELECT DISTINCT user_id FROM fund_group_members 
                WHERE group_id IN ({placeholders_g})
            ''', group_ids)
            
            for m in members:
                linked_ids.add(m['user_id'])
            
        placeholders = ','.join(['?'] * len(linked_ids))
        
        # Sum all 'Thu' with fund_purpose (Income to fund)
        sql_fund_in = f'''
            SELECT SUM(amount) as total FROM transactions 
            WHERE user_id IN ({placeholders}) AND type = 'Thu' AND fund_purpose IS NOT NULL AND fund_purpose != ''
        '''
        res_in = query_db(sql_fund_in, list(linked_ids), one=True)
        fund_in = res_in['total'] if res_in and res_in['total'] else 0
        
        # Sum all 'Chi' with fund_purpose (Expense from fund)
        sql_fund_out = f'''
            SELECT SUM(amount) as total FROM transactions 
            WHERE user_id IN ({placeholders}) AND type = 'Chi' AND fund_purpose IS NOT NULL AND fund_purpose != ''
        '''
        res_out = query_db(sql_fund_out, list(linked_ids), one=True)
        fund_out = res_out['total'] if res_out and res_out['total'] else 0
        
        summary['total_fund'] = fund_in - fund_out
        
    except Exception as e:
        print(f"Error calculating dashboard summary: {e}")
        import traceback
        traceback.print_exc()
    
    return render_template('dashboard.html', current_user=current_user, summary=summary)


@bp.route('/chi-tieu')
@login_required
def chi_tieu():
    """Trang nhập chi tiêu"""
    current_user = {
        'username': session.get('user'),
        'name': session.get('name'),
        'role': session.get('role')
    }
    return render_template('chi_tieu.html', current_user=current_user)


@bp.route('/admin')
@admin_required
def admin():
    current_user = {
        'username': session.get('user'),
        'name': session.get('name'),
        'role': session.get('role')
    }
    
    all_users = []
    if session.get('role') == 'admin':
        try:
            rows = query_db('SELECT id, username, name, role, active FROM users')
            for row in rows:
                all_users.append({
                    'id': row['id'],
                    'username': row['username'],
                    'name': row['name'],
                    'role': row['role'],
                    'active': bool(row['active'])
                })
        except Exception as e:
            print(f"Error loading users for admin: {e}")
            
    return render_template('admin.html', current_user=current_user, all_users=all_users)
