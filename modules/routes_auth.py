"""Auth Routes - Login & Logout (session-based, PIN user).

v2.5: Halaman login klasik dipensiunkan. Semua autentikasi memakai SPA
`/app/login` (JSON API `/api/auth/login` di routes_spa.py — sesi yang sama,
lengkap dengan rate-limit anti brute-force & CSRF). Endpoint lama `/login`
dan `/logout` hanya mengarahkan ke SPA agar bookmark lama tetap berfungsi.
"""
from flask import redirect, session
from modules.helpers import home_for_role


def register_auth_routes(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        # Sudah login? langsung ke halaman sesuai role di SPA
        if session.get('user_role'):
            return redirect(home_for_role(session.get('user_role')))
        return redirect('/app/login')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/app/login')
