"""
Routes cho authentication: login, logout, index
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from utils.db_utils import query_db
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            session['user_id'] = user['id'] # Store ID in session for easier access
            return redirect(url_for('main.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('auth.login'))
