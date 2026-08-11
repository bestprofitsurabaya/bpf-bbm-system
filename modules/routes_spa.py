"""Routes for the Vue 3 SPA (v2.0).

- /api/auth/*  : JSON auth (session-based, CSRF-aware) untuk SPA.
- /api/trips*  : JSON endpoints log perjalanan (dipakai view SPA Trips).
- /app/*       : serve SPA bundle (static/app) dengan fallback ke index.html.
"""
import os
import secrets

from flask import jsonify, request, session, send_from_directory

from modules.helpers import role_required, log_activity_async, home_for_role, login_rate_check, login_fail, login_success
from modules.config import get_db_connection

SPA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'app')

# Asset ber-hash (Vite) bisa di-cache lama; index.html wajib no-cache.
_SPA_IMMUTABLE_HINTS = ('/assets/', '.js', '.css', '.svg', '.png', '.woff2', '.ico')


def _ensure_csrf():
    """Pastikan session punya csrf_token (untuk header X-CSRF-Token SPA)."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']


def _client_ip():
    return request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or request.remote_addr or '?'


def register_spa_routes(app):

    # ================================================================
    # AUTH (JSON) — sesi sama dengan login klasik
    # ================================================================
    @app.route('/api/auth/me')
    def api_auth_me():
        _ensure_csrf()
        if session.get('user_role'):
            return jsonify({
                'authenticated': True,
                'user': {
                    'role': session.get('user_role'),
                    'user_name': session.get('user_name'),
                    'full_name': session.get('full_name'),
                },
                'csrf_token': session.get('csrf_token'),
                'home': home_for_role(session.get('user_role')),
            })
        return jsonify({'authenticated': False, 'csrf_token': session.get('csrf_token')})

    @app.route('/api/auth/login', methods=['POST'])
    def api_auth_login():
        data = request.get_json(silent=True) or {}
        username = str(data.get('username', '')).strip()
        pin = str(data.get('pin', '')).strip()
        if not username or not pin:
            return jsonify({'status': 'error', 'msg': 'Username dan PIN wajib diisi'}), 400

        # Rate limit anti brute-force (ISO/IEC 27001 A.8.5) — sama dengan login klasik
        ip = _client_ip()
        allowed, retry_after = login_rate_check(ip)
        if not allowed:
            return jsonify({'status': 'error', 'msg': f'Terlalu banyak percobaan. Coba lagi dalam {retry_after // 60} menit.'}), 429

        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'msg': 'Database tidak tersedia'}), 500
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND pin=%s AND is_active=TRUE", (username, pin))
            user = cursor.fetchone()
            cursor.close(); conn.close()
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
        if not user:
            login_fail(ip)
            return jsonify({'status': 'error', 'msg': 'Username atau PIN salah'}), 401

        login_success(ip)
        session.clear()
        session['user_role'] = user['role']
        session['user_name'] = user['username']
        session['full_name'] = user['full_name']
        session.permanent = True
        csrf = _ensure_csrf()
        log_activity_async(None, 'login', 'user', user['username'], ip=request.remote_addr)
        return jsonify({
            'status': 'success',
            'user': {'role': user['role'], 'user_name': user['username'], 'full_name': user['full_name']},
            'csrf_token': csrf,
            'home': home_for_role(user['role']),
        })

    @app.route('/api/auth/logout', methods=['POST'])
    def api_auth_logout():
        session.clear()
        return jsonify({'status': 'success'})

    # ================================================================
    # TRIPS (JSON) — list + verify + reject
    # ================================================================
    @app.route('/api/trips')
    @role_required(['ga', 'finance', 'admin'])
    def api_trips_list():
        try:
            driver_filter = request.args.get('driver', '').strip()
            date_filter = request.args.get('date', '').strip()
            status_filter = request.args.get('status', '').strip()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            query = """SELECT tm.id, tm.display_id, tm.driver_name, tm.trip_date, tm.status,
                       tm.km_awal, tm.km_akhir, tm.verified_by, tm.verified_at,
                       (SELECT COUNT(*) FROM trip_details WHERE trip_master_id = tm.id) AS total_routes
                       FROM trip_masters tm WHERE 1=1"""
            params = []
            if driver_filter:
                query += " AND tm.driver_name LIKE %s"; params.append(f"%{driver_filter}%")
            if date_filter:
                query += " AND tm.trip_date = %s"; params.append(date_filter)
            if status_filter in ('pending', 'verified_ga', 'rejected'):
                query += " AND tm.status = %s"; params.append(status_filter)
            query += " ORDER BY tm.created_at DESC LIMIT 200"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify({'data': rows})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trips/verify/<int:trip_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def api_trip_verify(trip_id):
        try:
            # verified_by selalu dari session — jangan pernah percaya input klien (anti audit forgery)
            admin_name = (session.get('full_name') or session.get('user_name') or 'GA Officer').strip()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trip_masters SET status='verified_ga', verified_by=%s, verified_at=NOW() "
                "WHERE id=%s AND status='pending'",
                (admin_name, trip_id))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(trip_id, 'trip_verify', 'ga', admin_name, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'Trip #{trip_id} diverifikasi'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trips/reject/<int:trip_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def api_trip_reject(trip_id):
        try:
            data = request.get_json(silent=True) or {}
            reason = (data.get('reason') or 'Tidak valid').strip()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trip_masters SET status='rejected', rejection_reason=%s WHERE id=%s",
                (reason, trip_id))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(trip_id, 'trip_reject', 'ga', session.get('user_name', 'GA Officer'),
                               new_data={'reason': reason}, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'Trip #{trip_id} ditolak'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # QUEUE KERJA (JSON) — antrean approve GA / payout / archive / reject
    # Nama pelaku diambil dari session (anti audit-trail forgery),
    # bukan dari body/query seperti endpoint klasik.
    # ================================================================
    def _queue_actor():
        return (session.get('full_name') or session.get('user_name') or 'Admin').strip()

    @app.route('/api/queue')
    @role_required(['ga', 'finance', 'admin'])
    def api_queue():
        try:
            tab = request.args.get('tab', 'ga')
            if tab not in ('ga', 'finance', 'driver_confirm'):
                tab = 'ga'
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cols = "id, display_id, driver_name, nopol, vehicle_type, bbm_type, nominal, liter, odo_km, ml_anomaly_flag, created_at"
            if tab == 'finance':
                cursor.execute(f"SELECT {cols} FROM transactions WHERE status='verified_ga' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            elif tab == 'driver_confirm':
                cursor.execute(f"SELECT {cols} FROM transactions WHERE status='os_finance' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            else:
                cursor.execute(f"SELECT {cols} FROM transactions WHERE status IN ('pending','modified') AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            rows = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/queue/approve-ga/<int:tx_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def api_queue_approve_ga(tx_id):
        actor = _queue_actor()
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            # Transaksi ber-flag anomali ML wajib verifikasi penuh (foto bukti)
            # di antarmuka klasik — tidak boleh di-approve cepat dari SPA.
            cursor.execute("SELECT ml_anomaly_flag FROM transactions WHERE id=%s", (tx_id,))
            prow = cursor.fetchone()
            if prow and prow.get('ml_anomaly_flag'):
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} ber-flag anomali ML — wajib verifikasi penuh (foto bukti) di Dashboard Klasik.'}), 409
            cursor.execute("UPDATE transactions SET status='verified_ga', ga_approved_by=%s, ga_approved_at=NOW(), approved_by_user=%s WHERE id=%s AND status IN ('pending','modified')", (actor, actor, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        from modules.notifications import push_driver_notification
                        push_driver_notification(row[0], 'claim', 'approved', f'Klaim {row[1]} Anda disetujui GA', row[1])
                except Exception as ne:
                    print(f"[notify] approve error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
            log_activity_async(tx_id, 'ga_approve', 'ga', actor, ip=_client_ip())
            return jsonify({'status': 'success', 'msg': f'Klaim #{tx_id} disetujui GA!'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/queue/payout/<int:tx_id>', methods=['POST'])
    @role_required(['finance', 'admin'])
    def api_queue_payout(tx_id):
        actor = _queue_actor()
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='os_finance', finance_payout_by=%s, finance_payout_at=NOW(), payout_by_user=%s WHERE id=%s AND status='verified_ga'", (actor, actor, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        from modules.notifications import push_driver_notification
                        push_driver_notification(row[0], 'claim', 'paid', f'Dana klaim {row[1]} sudah dicairkan Finance', row[1])
                except Exception as ne:
                    print(f"[notify] payout error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
            log_activity_async(tx_id, 'finance_payout', 'finance', actor, ip=_client_ip())
            return jsonify({'status': 'success', 'msg': f'Dana #{tx_id} dicairkan!'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/queue/archive/<int:tx_id>', methods=['POST'])
    @role_required(['finance', 'admin'])
    def api_queue_archive(tx_id):
        actor = _queue_actor()
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='archived', archived_by=%s, archived_at=NOW(), archived_by_user=%s WHERE id=%s AND status='os_finance'", (actor, actor, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        from modules.notifications import push_driver_notification
                        push_driver_notification(row[0], 'claim', 'archived', f'Klaim {row[1]} selesai & diarsipkan', row[1])
                except Exception as ne:
                    print(f"[notify] archive error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
            log_activity_async(tx_id, 'archive', 'finance', actor, ip=_client_ip())
            return jsonify({'status': 'success', 'msg': f'Transaksi #{tx_id} diarsipkan!'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/queue/reject/<int:tx_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def api_queue_reject(tx_id):
        actor = _queue_actor()
        data = request.get_json(silent=True) or {}
        reason = str(data.get('reason') or 'Tanpa alasan').strip()[:500]
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
            tx = cursor.fetchone()
            cursor.execute("UPDATE transactions SET status='rejected', rejection_reason=%s WHERE id=%s AND status <> 'rejected'", (reason, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0 and tx:
                try:
                    from modules.notifications import push_driver_notification
                    push_driver_notification(tx['driver_name'], 'claim', 'rejected', f'Klaim {tx["display_id"]} ditolak: {reason}', tx['display_id'])
                except Exception as ne:
                    print(f"[notify] reject error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah ditolak.'}), 409
            log_activity_async(tx_id, 'reject', 'ga', actor, new_data={'reason': reason}, ip=_client_ip())
            return jsonify({'status': 'success', 'msg': f'Klaim #{tx_id} ditolak'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # SPA — serve bundle + fallback client routing
    # ================================================================
    @app.route('/app/')
    @app.route('/app/<path:path>')
    def spa_app(path=''):
        if not os.path.isfile(os.path.join(SPA_DIR, 'index.html')):
            return ("SPA belum di-build. Jalankan: bash scripts/build-spa.sh, "
                    "lalu rebuild container."), 503
        if path:
            full = os.path.join(SPA_DIR, path)
            if os.path.isfile(full):
                resp = send_from_directory(SPA_DIR, path)
                # Asset ber-hash (Vite) aman di-cache lama; app.py after_request
                # tidak menimpa header yang sudah di-set di sini.
                if any(hint in path for hint in _SPA_IMMUTABLE_HINTS):
                    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                return resp
        # index.html + fallback client-routing: selalu fresh (no-store dari after_request)
        return send_from_directory(SPA_DIR, 'index.html')
