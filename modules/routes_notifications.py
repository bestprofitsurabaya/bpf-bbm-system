"""API Routes - Driver Notifications"""
from flask import request, jsonify
from modules.config import get_db_connection
from modules.helpers import resolve_driver_scope


def register_notification_routes(app):

    @app.route('/api/notifications')
    def api_notifications():
        try:
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ?driver= ditutup)
            driver = resolve_driver_scope(request.args.get('driver', ''))
            if driver is None:
                return jsonify({'error': 'Login driver wajib'}), 401
            if not driver:
                return jsonify({'error': 'Parameter driver wajib'}), 400
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, driver_name, type, action, message, ref_id, is_read, created_at "
                "FROM notifications WHERE driver_name=%s "
                "ORDER BY created_at DESC, id DESC LIMIT 30",
                (driver,),
            )
            items = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS c FROM notifications WHERE driver_name=%s AND is_read=0",
                (driver,),
            )
            unread = cursor.fetchone()['c']
            cursor.close()
            conn.close()
            for it in items:
                if it.get('created_at') is not None:
                    it['created_at'] = str(it['created_at'])
            return jsonify({'notifications': items, 'unread': unread})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notifications/read', methods=['POST'])
    def api_notifications_read():
        try:
            data = request.get_json() or {}
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ditutup)
            driver = resolve_driver_scope(data.get('driver') or '')
            if driver is None:
                return jsonify({'status': 'error', 'msg': 'Login driver wajib'}), 401
            if not driver:
                return jsonify({'status': 'error', 'msg': 'driver wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notifications SET is_read=1 WHERE driver_name=%s AND is_read=0",
                (driver,),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
