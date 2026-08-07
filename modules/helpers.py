"""Helper functions for BPF BBM System"""
import os
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

production_pool_executor = ThreadPoolExecutor(max_workers=20)

def safe_float(val, default=0.0):
    """Convert Decimal/None/str to float safely"""
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default

def resolve_driver_form_context(driver_data, driver_name, nopol, vehicle_type, bbm_type):
    """Resolve the final driver context for claim submission using master data when available."""
    resolved_nopol = nopol
    resolved_vehicle_type = vehicle_type
    resolved_bbm_type = bbm_type
    if driver_data:
        resolved_nopol = driver_data.get('nopol') or resolved_nopol
        resolved_vehicle_type = driver_data.get('vehicle_type') or resolved_vehicle_type
        resolved_bbm_type = driver_data.get('bbm_type') or resolved_bbm_type
    return {
        'driver_name': driver_name,
        'nopol': resolved_nopol,
        'vehicle_type': resolved_vehicle_type,
        'bbm_type': resolved_bbm_type,
    }

_generated_display_ids = set()
_display_id_lock = threading.Lock()


def generate_display_id(prefix='BPF', conn=None):
    """Generate unique display ID: BPF-YYYYMMDD-HHMMSSXX (timestamp + random).

    Uniqueness dijaga via dedupe in-memory thread-safe + double-check di DB
    bila koneksi tersedia.
    """
    import random, string
    now = datetime.now()
    date_part = now.strftime('%Y%m%d')
    time_part = now.strftime('%H%M%S')

    def _candidate():
        random_part = ''.join(random.choices(string.digits, k=2))
        return f"{prefix}-{date_part}-{time_part}{random_part}"

    unique_id = _candidate()
    guard = 0
    with _display_id_lock:
        while unique_id in _generated_display_ids:
            unique_id = _candidate()
            guard += 1
            if guard > 500:
                break
        _generated_display_ids.add(unique_id)

    # Double-check uniqueness in DB (rare collision lintas-restart)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE display_id = %s", (unique_id,))
            exists = cursor.fetchone()[0]
            cursor.close()
            if exists > 0:
                with _display_id_lock:
                    unique_id = _candidate()
                    _generated_display_ids.add(unique_id)
        except Exception:
            pass

    return unique_id

def generate_trip_display_id(conn=None):
    """Generate trip display ID: TRIP-YYYYMMDD-XXXX"""
    return generate_display_id('TRIP', conn)

def save_file(file_obj, prefix, nopol, upload_folder):
    """Save uploaded file with timestamp prefix"""
    if file_obj and file_obj.filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{nopol}_{ts}_{file_obj.filename}"
        filepath = os.path.join(upload_folder, filename)
        file_obj.save(filepath)
        return filename
    return None

def log_activity_async(tx_id, action, user_type, user_name, old_data=None, new_data=None, ip=None, ua=None):
    """Log activity asynchronously"""
    from modules.config import get_db_connection
    def _log():
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs (transaction_id, action, user_type, user_name, old_data, new_data, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tx_id, action, user_type, user_name,
                  json.dumps(old_data) if old_data else None,
                  json.dumps(new_data) if new_data else None, ip, ua))
            conn.commit()
            cursor.close(); conn.close()
        except Exception as e:
            print(f"Log error: {e}")
    production_pool_executor.submit(_log)

def validate_bbm_for_vehicle(vehicle_type, bbm_type):
    """Validate BBM type for vehicle"""
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn: return {'valid': False, 'error': 'DB error'}
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicle_bbm_allowed WHERE vehicle_type=%s AND bbm_type=%s", (vehicle_type, bbm_type))
        result = cursor.fetchone()
        cursor.close(); conn.close()
        if result:
            return {'valid': True, 'limits': {
                'min': result['min_km_per_liter'], 'max': result['max_km_per_liter'],
                'warning': result['warning_km_per_liter'], 'good': result['good_km_per_liter']
            }}
        return {'valid': False, 'error': f'BBM {bbm_type} tidak tersedia untuk {vehicle_type}'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def get_or_create_driver(driver_name, nopol, vehicle_type, bbm_type='PERTALITE'):
    """Auto-discover or create driver profile"""
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, is_active FROM drivers WHERE name = %s", (driver_name,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE drivers SET nopol = %s, vehicle_type = %s, bbm_type = %s, is_active = TRUE
                WHERE name = %s
            """, (nopol, vehicle_type, bbm_type, driver_name))
        else:
            cursor.execute("""
                INSERT INTO drivers (name, nopol, vehicle_type, bbm_type, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (driver_name, nopol, vehicle_type, bbm_type))
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception as e:
        print(f"get_or_create_driver error: {e}")
        return False

def get_or_create_vehicle(vehicle_type, brand='TOYOTA', capacity=45):
    """Auto-discover or create vehicle type"""
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM vehicles WHERE vehicle_type = %s", (vehicle_type,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO vehicles (vehicle_type, brand, fuel_capacity, is_active)
                VALUES (%s, %s, %s, TRUE)
            """, (vehicle_type, brand, capacity))
            conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception as e:
        print(f"get_or_create_vehicle error: {e}")
        return False

def get_or_create_bbm(bbm_type, price_per_liter=10000):
    """Auto-discover or create BBM type"""
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM bbm_types WHERE name = %s", (bbm_type,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO bbm_types (name, price_per_liter, is_active)
                VALUES (%s, %s, TRUE)
            """, (bbm_type, price_per_liter))
            conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception as e:
        print(f"get_or_create_bbm error: {e}")
        return False

def get_or_create_vehicle_bbm_allowed(vehicle_type, bbm_type):
    """Auto-discover or create vehicle-BBM allowed relation"""
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id FROM vehicle_bbm_allowed WHERE vehicle_type = %s AND bbm_type = %s
        """, (vehicle_type, bbm_type))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO vehicle_bbm_allowed 
                (vehicle_type, bbm_type, min_km_per_liter, max_km_per_liter, warning_km_per_liter, good_km_per_liter, is_default)
                VALUES (%s, %s, 5.0, 20.0, 10.0, 12.5, FALSE)
            """, (vehicle_type, bbm_type))
            conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception as e:
        print(f"get_or_create_vehicle_bbm_allowed error: {e}")
        return False

def ensure_all_master_data(driver_name, nopol, vehicle_type, bbm_type, price_per_liter=10000):
    """One-call to ensure all master data exists"""
    get_or_create_vehicle(vehicle_type)
    get_or_create_bbm(bbm_type, price_per_liter)
    get_or_create_vehicle_bbm_allowed(vehicle_type, bbm_type)
    get_or_create_driver(driver_name, nopol, vehicle_type, bbm_type)
    return True
# ============================================================
# TAMBAHKAN INI DI AKHIR FILE helpers.py
# (Sebelum baris terakhir, setelah fungsi ensure_all_master_data)
# ============================================================

# --- AUTH DECORATORS ---
from functools import wraps
from flask import request, jsonify, session, g, redirect, url_for, flash

def _auth_denied_response():
    """Respons saat belum login: halaman -> redirect ke login, API/SPA -> JSON 401."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'msg': 'Akses ditolak. Silakan login terlebih dahulu.'}), 401
    next_url = request.full_path if request.query_string else request.path
    return redirect(url_for('login_page', next=next_url))

def _auth_forbidden_response():
    """Respons saat role tidak sesuai: halaman -> flash + redirect, API/SPA -> JSON 403."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'msg': 'Role tidak diizinkan untuk aksi ini.'}), 403
    flash('Anda tidak memiliki akses ke halaman ini.', 'error')
    return redirect(url_for('admin_dashboard'))

def role_required(allowed_roles):
    """
    Decorator: Hanya izinkan user dengan role tertentu.
    Bekerja dengan session-based auth (login PIN).
    
    Usage:
        @app.route('/admin/settings')
        @role_required(['admin'])
        def settings():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Cek session dulu
            user_role = session.get('user_role')
            user_name = session.get('user_name')

            if not user_role:
                return _auth_denied_response()

            if user_role not in allowed_roles:
                return _auth_forbidden_response()

            # Simpan ke g untuk dipakai di view
            g.user_role = user_role
            g.user_name = user_name

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Shortcut decorator: hanya admin."""
    return role_required(['admin'])(f)


def ga_or_admin_required(f):
    """Shortcut decorator: GA atau admin."""
    return role_required(['ga', 'admin'])(f)


def finance_or_admin_required(f):
    """Shortcut decorator: Finance atau admin."""
    return role_required(['finance', 'admin'])(f)


# ============================================================
# APPOINTMENT SYSTEM HELPERS
# ============================================================

# Sesi perjalanan appointment. Sesi 1 = 08.30, Sesi 2 = 14.30.
SESI_INFO = {
    '1': {'label': 'Sesi 1', 'time': '08:30', 'display': '08.30', 'icon': '🌅'},
    '2': {'label': 'Sesi 2', 'time': '14:30', 'display': '14.30', 'icon': '🌆'},
}
VALID_SESI = ('1', '2')
APPOINTMENT_STATUSES = ('scheduled', 'assigned', 'completed', 'cancelled')


def sesi_info(sesi):
    """Return dict sesi (label, waktu mulai, display) atau None jika tidak valid."""
    return SESI_INFO.get(str(sesi))


def sesi_time(sesi):
    """Jam mulai sesi sebagai string HH:MM ('08:30' / '14:30')."""
    info = SESI_INFO.get(str(sesi))
    return info['time'] if info else None


# Pemetaan kata kunci area -> zona (digunakan untuk membantu Chief Driver
# membagi driver berdasarkan wilayah, dan preview otomatis untuk marketing).
AREA_KEYWORDS = [
    ('Surabaya Pusat', ['surabaya pusat', 'pasar atom', 'tunjungan', 'genteng', 'gubeng', 'tegalsari', 'sawahan', 'simokerto', 'bubutan', 'krejongan', 'gemblongan']),
    ('Surabaya Barat', ['surabaya barat', 'darmo', 'darmo permai', 'darmo park', 'wiyung', 'karang pilang', 'lakarsantri', 'benowo', 'pakal', 'tandes', 'sukomanunggal', 'asemrowo']),
    ('Surabaya Utara', ['surabaya utara', 'kenjeran', 'bulak', 'semampir', 'pabean cantian', 'krembangan', 'perak', 'tanjung perak']),
    ('Surabaya Timur', ['surabaya timur', 'rungkut', 'gunung anyar', 'mulyorejo', 'sukolilo', 'tambaksari', 'tenggilis', 'gayungan', 'wonocolo', 'medokan']),
    ('Surabaya Selatan', ['surabaya selatan', 'wonokromo', 'jambangan', 'wonokusumo', 'karang gayam', 'pucang', 'siwalankerto', 'ketintang']),
    ('Sidoarjo', ['sidoarjo', 'gedangan', 'taman', 'waru', 'sedati', 'buduran', 'candi', 'tanggulangin', 'porong', 'jabon', 'krian', 'balongbendo', 'wonoayu', 'tarik', 'prambon', 'tulangan']),
    ('Gresik', ['gresik', 'kebomas', 'manyar', 'bunder', 'driyorejo', 'menganti', 'cerme']),
    ('Mojokerto', ['mojokerto', 'puri', 'sooko', 'jetis', 'gedeg', 'dawarblandong']),
    ('Pasuruan', ['pasuruan', 'pandaan', 'gempol', 'bangil', 'beji']),
    ('Lamongan', ['lamongan', 'kembangbahu', 'sugio', 'turi', 'paciran']),
]


def detect_area(alamat):
    """Deteksi zona wilayah dari teks alamat (Surabaya & sekitarnya).

    Return nama area ('Surabaya Timur', 'Sidoarjo', ...) atau 'Lainnya'.
    """
    if not alamat:
        return 'Lainnya'
    text = str(alamat).lower()
    for area, keywords in AREA_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return area
    return 'Lainnya'


def generate_appointment_display_id(conn=None):
    """Generate display ID appointment: APP-YYYYMMDD-HHMMSSXX"""
    return generate_display_id('APP', conn)


def get_or_create_team(name, leader_name=''):
    """Pastikan tim marketing ada di marketing_teams; return nama tim."""
    name = (name or '').strip()
    if not name:
        return ''
    from modules.config import get_db_connection
    try:
        conn = get_db_connection()
        if not conn:
            return name
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO marketing_teams (name, leader_name, is_active) VALUES (%s, %s, 1) "
            "ON DUPLICATE KEY UPDATE is_active=1",
            (name, leader_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"get_or_create_team error: {e}")
    return name


def validate_appointment_input(item):
    """Validasi satu item input appointment.

    Return (is_valid, errors_dict, normalized_dict).
    """
    errors = {}
    nasabah = str(item.get('nasabah_name', '') or '').strip()
    alamat = str(item.get('alamat', '') or '').strip()
    sesi = str(item.get('sesi', '') or '').strip()
    tanggal = str(item.get('appointment_date', '') or item.get('date', '') or '').strip()
    phone = str(item.get('nasabah_phone', '') or '').strip()
    notes = str(item.get('notes', '') or '').strip()

    if not nasabah:
        errors['nasabah_name'] = 'Nama calon nasabah wajib diisi'
    if not alamat:
        errors['alamat'] = 'Alamat wajib diisi'
    elif len(alamat) > 500:
        errors['alamat'] = 'Alamat maksimal 500 karakter'
    if sesi not in VALID_SESI:
        errors['sesi'] = 'Pilih sesi (1 = 08.30 atau 2 = 14.30)'
    if not tanggal:
        errors['appointment_date'] = 'Tanggal appointment wajib diisi'
    if len(nasabah) > 150:
        errors['nasabah_name'] = 'Nama maksimal 150 karakter'
    if len(phone) > 30:
        errors['nasabah_phone'] = 'No. HP maksimal 30 karakter'

    normalized = {
        'nasabah_name': nasabah,
        'nasabah_phone': phone,
        'alamat': alamat,
        'sesi': sesi,
        'appointment_date': tanggal,
        'notes': notes[:500],
    }
    return (not errors, errors, normalized)
