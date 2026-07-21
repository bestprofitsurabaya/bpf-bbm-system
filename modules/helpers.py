"""Helper functions for BPF BBM System"""
import os
import json
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

def generate_display_id(prefix='BPF', conn=None):
    """Generate professional display ID: BPF-YYYYMMDD-XXXX"""
    today = datetime.now().strftime('%Y%m%d')
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE DATE(created_at) = CURDATE()")
        count = cursor.fetchone()[0] + 1
        cursor.close()
    else:
        count = 1
    return f"{prefix}-{today}-{count:04d}"

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
