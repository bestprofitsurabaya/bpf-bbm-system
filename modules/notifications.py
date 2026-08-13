"""Driver notification store + real-time push.

Notifications are persisted so the PWA can catch up on anything the driver
missed while offline, and pushed live via SocketIO when a driver device is open.
"""
from datetime import datetime

from modules.config import get_db_connection
from modules.realtime import emit_driver


def ensure_notifications_table(conn=None):
    """CREATE TABLE IF NOT EXISTS - safe to run at every startup.

    conn opsional: bila diberikan, dipakai langsung (mis. untuk DB cabang)
    dan tidak ditutup di sini.
    """
    own = conn is None
    try:
        if conn is None:
            conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                driver_name VARCHAR(100) NOT NULL,
                type VARCHAR(20) NOT NULL,
                action VARCHAR(30) NOT NULL,
                message VARCHAR(255) NOT NULL,
                ref_id VARCHAR(60) DEFAULT NULL,
                is_read TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                KEY idx_driver_read (driver_name, is_read),
                KEY idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        # Prune read notifications older than 30 days
        try:
            cursor.execute("DELETE FROM notifications WHERE is_read=1 AND created_at < (NOW() - INTERVAL 30 DAY)")
            conn.commit()
        except Exception as pe:
            print(f"[notifications] prune error: {pe}")
        cursor.close()
        if own and conn:
            conn.close()
    except Exception as e:
        print(f"[notifications] ensure table error: {e}")


def push_driver_notification(driver_name, ntype, action, message, ref_id=None):
    """Persist a notification for a driver and push it live via SocketIO."""
    if not driver_name:
        return None
    driver = str(driver_name).strip().upper()
    notif_id = None
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (driver_name, type, action, message, ref_id, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (driver, ntype, action, str(message)[:255], ref_id, created),
            )
            conn.commit()
            notif_id = cursor.lastrowid
    except Exception as e:
        print(f"[notifications] push error: {e}")
    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if conn:
            try: conn.close()
            except Exception: pass

    emit_driver(driver, {
        'id': notif_id,
        'driver_name': driver,
        'type': ntype,
        'action': action,
        'message': str(message)[:255],
        'ref_id': ref_id,
        'created_at': created,
    })
    return notif_id


def push_marketing_notification(username, ntype, action, message, ref_id=None):
    """Persist + realtime-push notifikasi untuk user marketing (reuse tabel notifications).

    Emit ke room marketing_<username> sehingga halaman marketing menerima update langsung.
    """
    if not username:
        return None
    user = str(username).strip().lower()
    notif_id = None
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (driver_name, type, action, message, ref_id, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (user, ntype, action, str(message)[:255], ref_id, created),
            )
            conn.commit()
            notif_id = cursor.lastrowid
    except Exception as e:
        print(f"[notifications] push_marketing error: {e}")
    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if conn:
            try: conn.close()
            except Exception: pass

    from modules.realtime import emit_event
    emit_event('appointment_update', {
        'id': notif_id,
        'username': user,
        'type': ntype,
        'action': action,
        'message': str(message)[:255],
        'ref_id': ref_id,
        'created_at': created,
    }, room='marketing_' + user)
    return notif_id
