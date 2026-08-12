#!/usr/bin/env python3
"""
BPF BBM System v1.0 - Main Application
PT. Bestprofit Surabaya
"""
import warnings, os
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
try:
    import eventlet
    eventlet.monkey_patch()
    socketio_async_mode = 'eventlet'
except Exception:
    eventlet = None
    socketio_async_mode = 'threading'

from flask_socketio import SocketIO
from flask import Flask, request, session, jsonify, redirect, url_for, flash
from datetime import timedelta
import os
import warnings
import secrets
warnings.filterwarnings('ignore')

# Init Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get('SECRET_KEY', 'bpf_bbm_secret_key_default_2026')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

# Session cookie hardening (ISO/IEC 27001 A.8.5 manajemen sesi)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
# Secure cookie: aktif saat HTTPS (produksi duckdns). Matikan hanya untuk dev http lokal.
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() in ('1', 'true', 'yes')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.environ.get('SESSION_HOURS', '12')))

# Init SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=socketio_async_mode, logger=False, engineio_logger=False)

# Attach realtime bus (driver notification rooms)
from modules.realtime import init_socketio
init_socketio(socketio)

# Init DB Pool
from modules.config import init_pool
init_pool()

# Ensure notifications table exists (safe on every startup)
from modules.notifications import ensure_notifications_table
ensure_notifications_table()

# Ensure appointment system tables/columns (safe on every startup)
from modules.appointments_schema import ensure_appointments_schema
ensure_appointments_schema()

# Register all route modules
from modules.routes_driver import register_driver_routes
from modules.routes_api_master import register_master_api
from modules.routes_api_transactions import register_transaction_api
from modules.routes_api_assignments import register_assignment_api
from modules.routes_admin import register_admin_routes
from modules.routes_reports import register_report_routes
from modules.routes_cash import register_cash_routes
from modules.routes_settings import register_settings_routes
from modules.routes_notifications import register_notification_routes
from modules.routes_auth import register_auth_routes
from modules.routes_appointments import register_appointment_routes
from modules.routes_water import register_water_routes
from modules.routes_spa import register_spa_routes

register_driver_routes(app, socketio)
register_auth_routes(app)
register_master_api(app)
register_transaction_api(app)
register_assignment_api(app)
register_cash_routes(app)
register_admin_routes(app)
register_report_routes(app)
register_settings_routes(app)
register_notification_routes(app)
register_appointment_routes(app)
register_water_routes(app)
register_spa_routes(app)

# ================================================================
# CSRF PROTECTION (berlaku untuk sesi admin yang login)
# Endpoint PWA driver (tanpa session) & socket.io dikecualikan.
# ================================================================
# v2.5: endpoint driver (submit-trip, cash request/submit-lpj/delete, driver-complete)
# kini WAJIB sesi login PIN — SPA driver mengirim X-CSRF-Token (api()/fetch), jadi
# tidak perlu lagi dikecualikan dari proteksi CSRF (defense-in-depth).
CSRF_EXEMPT_PREFIXES = (
    '/socket.io', '/api/assignments/confirm', '/api/get-feedback',
    '/api/vehicle-allowed-bbm', '/uploads/',
)

@app.context_processor
def inject_csrf_token():
    """Sediakan fungsi csrf_token() untuk dipakai di template (meta tag & hidden input)."""
    def _csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']
    return {'csrf_token': _csrf_token}

@app.before_request
def csrf_protect():
    if request.method not in ('POST', 'PUT', 'DELETE', 'PATCH'):
        return None
    # Hanya berlaku untuk sesi admin yang login; halaman login ikut dilindungi
    if not session.get('user_role') and request.path != '/login':
        return None
    for p in CSRF_EXEMPT_PREFIXES:
        if request.path.startswith(p):
            return None
    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
    if not token or not session.get('csrf_token') or token != session.get('csrf_token'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
            return jsonify({'status': 'error', 'msg': 'CSRF token tidak valid. Muat ulang halaman dan coba lagi.'}), 400
        flash('Sesi tidak valid. Silakan muat ulang halaman dan coba lagi.', 'error')
        ref = request.referrer or ''
        return redirect(ref if ref.startswith('/') else url_for('admin_dashboard'))
    return None

# Middleware
@app.after_request
def add_no_cache_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
