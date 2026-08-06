"""Auth Routes - Login & Logout (session-based, PIN user)"""
from flask import render_template, request, redirect, url_for, session, flash
from modules.config import get_db_connection
from urllib.parse import urlparse


def register_auth_routes(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        # Sudah login? langsung ke dashboard
        if session.get('user_role'):
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            pin = request.form.get('pin', '').strip()
            nxt_arg = request.args.get('next', '').strip()
            # Pertahankan next agar tidak hilang saat login gagal (url_for menangani encoding)
            login_retry = url_for('login_page', next=nxt_arg) if nxt_arg else url_for('login_page')

            if not username or not pin:
                flash('Username dan PIN wajib diisi.', 'error')
                return redirect(login_retry)

            try:
                conn = get_db_connection()
                if not conn:
                    flash('Database tidak tersedia.', 'error')
                    return redirect(login_retry)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username=%s AND pin=%s AND is_active=TRUE", (username, pin))
                user = cursor.fetchone()
                cursor.close(); conn.close()
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(login_retry)

            if user:
                session.clear()
                session['user_role'] = user['role']
                session['user_name'] = user['username']
                session['full_name'] = user['full_name']
                session.permanent = True
                nxt = request.args.get('next', '').strip()
                # Hanya izinkan redirect internal (cegah open redirect)
                parsed = urlparse(nxt)
                if nxt and nxt.startswith('/') and not nxt.startswith('//') and not parsed.netloc:
                    return redirect(nxt)
                return redirect(url_for('admin_dashboard'))

            flash('Username atau PIN salah.', 'error')
            return redirect(login_retry)

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login_page'))
