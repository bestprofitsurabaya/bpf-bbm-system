"""Settings Routes (v2.5 — halaman klasik dipensiunkan → redirect SPA).

Manajemen user & master data kini memakai SPA:
- /app/users      → API /api/users, /api/users/sync, /api/users/reset-pin
- /app/settings   → API /api/drivers, /api/vehicles, /api/bbm_types, /api/system-config
Endpoint lama hanya mengarahkan agar bookmark tetap berfungsi.
"""
from flask import redirect
from modules.helpers import role_required

def register_settings_routes(app):

    @app.route('/admin/users')
    @role_required(['admin'])
    def admin_users_page():
        """Halaman manajemen user (admin-only) — kelola akun & reset PIN."""
        return redirect('/app/users')

    @app.route('/admin/settings', methods=['GET', 'POST'])
    @role_required(['ga', 'finance', 'admin'])
    def admin_settings():
        return redirect('/app/settings')
