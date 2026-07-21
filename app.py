#!/usr/bin/env python3
"""
BPF BBM System v1.0 - Main Application
PT. Bestprofit Surabaya
"""
try:
    import eventlet
    eventlet.monkey_patch()
    socketio_async_mode = 'eventlet'
except Exception:
    eventlet = None
    socketio_async_mode = 'threading'

from flask_socketio import SocketIO
from flask import Flask, request
import os
import warnings
warnings.filterwarnings('ignore')

# Init Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get('SECRET_KEY', 'bpf_bbm_secret_key_default_2026')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

# Init SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=socketio_async_mode, logger=False, engineio_logger=False)

# Init DB Pool
from modules.config import init_pool
init_pool()

# Register all route modules
from modules.routes_driver import register_driver_routes
from modules.routes_api import register_api_routes
from modules.routes_admin import register_admin_routes
from modules.routes_reports import register_report_routes
from modules.routes_settings import register_settings_routes

register_driver_routes(app, socketio)
register_api_routes(app)
register_admin_routes(app)
register_report_routes(app)
register_settings_routes(app)

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
