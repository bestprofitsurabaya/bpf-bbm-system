"""API Routes"""
from flask import request, jsonify
from modules.config import get_db_connection
from modules.helpers import log_activity_async, safe_float
from modules.engine import generate_human_insight, PerformanceAnalyzer
from datetime import datetime, timedelta

def register_api_routes(app):
    @app.route('/api/transactions/archive')
    def api_archive_transactions():
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 50, type=int)
            search = request.args.get('search', '').strip()
            start_date = request.args.get('start_date', '')
            end_date = request.args.get('end_date', '')
            bbm_type = request.args.get('bbm_type', '')
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            where = ["status = 'archived'"]
            params = []
            if not start_date: where.append("created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
            if start_date: where.append("DATE(created_at) >= %s"); params.append(start_date)
            if end_date: where.append("DATE(created_at) <= %s"); params.append(end_date)
            if search: where.append("(nopol LIKE %s OR driver_name LIKE %s)"); params.extend([f"%{search}%", f"%{search}%"])
            if bbm_type: where.append("bbm_type = %s"); params.append(bbm_type)
            wc = " AND ".join(where)
            cursor.execute(f"SELECT COUNT(*) as total FROM transactions WHERE {wc}", params)
            total = cursor.fetchone()['total']
            cursor.execute(f"SELECT COALESCE(SUM(nominal),0) as total_nominal FROM transactions WHERE {wc}", params)
            s = cursor.fetchone()
            cursor.execute(f"SELECT * FROM transactions WHERE {wc} ORDER BY created_at DESC LIMIT %s OFFSET %s", params + [limit, (page-1)*limit])
            data = cursor.fetchall()
            for row in data:
                for k in ['nominal','liter','price_per_liter','odo_km','km_per_liter']:
                    if row.get(k) is not None: row[k] = float(row[k])
            cursor.close(); conn.close()
            return jsonify({'data': data, 'total': total, 'page': page, 'limit': limit, 'total_pages': max(1,(total+limit-1)//limit), 'summary': {'total_nominal': float(s['total_nominal'])}})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    
    @app.route('/api/vehicles')
    def api_vehicles():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT vehicle_type, brand, fuel_capacity FROM vehicles WHERE is_active=TRUE ORDER BY vehicle_type")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/bbm_types')
    def api_bbm_types():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, price_per_liter FROM bbm_types WHERE is_active=TRUE ORDER BY name")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/drivers')
    def api_drivers():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, nopol, vehicle_type, bbm_type, is_active FROM drivers ORDER BY name")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vehicle_bbm/<vehicle_type>')
    def api_vehicle_bbm(vehicle_type):
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT vba.bbm_type, vba.min_km_per_liter, vba.max_km_per_liter,
                       vba.warning_km_per_liter, vba.good_km_per_liter, vba.is_default, bt.price_per_liter
                FROM vehicle_bbm_allowed vba JOIN bbm_types bt ON vba.bbm_type=bt.name
                WHERE vba.vehicle_type=%s AND bt.is_active=TRUE ORDER BY vba.is_default DESC
            """, (vehicle_type,))
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vehicle-allowed-bbm/<vehicle_type>')
    def api_vehicle_allowed_bbm(vehicle_type):
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT vba.bbm_type, bt.price_per_liter, vba.is_default FROM vehicle_bbm_allowed vba
                JOIN bbm_types bt ON vba.bbm_type=bt.name
                WHERE vba.vehicle_type=%s AND bt.is_active=TRUE ORDER BY vba.is_default DESC
            """, (vehicle_type,))
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/verify-pin', methods=['POST'])
    def verify_pin():
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            pin = data.get('pin', '').strip()
            if not username or not pin:
                return jsonify({'status': 'error', 'msg': 'Username dan PIN wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND pin=%s AND is_active=TRUE", (username, pin))
            user = cursor.fetchone()
            if user:
                cursor.execute("UPDATE users SET last_login=NOW() WHERE id=%s", (user['id'],))
                conn.commit()
                cursor.close(); conn.close()
                return jsonify({'status': 'success', 'user': {'username': user['username'], 'full_name': user['full_name'], 'role': user['role']}})
            cursor.close(); conn.close()
            return jsonify({'status': 'error', 'msg': 'PIN salah'}), 401
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/users')
    def api_users():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, full_name, role, is_active, last_login FROM users ORDER BY role, username")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/users/sync', methods=['POST'])
    def sync_user():
        try:
            data = request.get_json()
            u = data.get('username', '').strip()
            f = data.get('full_name', '').strip()
            r = data.get('role', 'ga')
            p = data.get('pin', '123456')
            a = data.get('is_active', True)
            if not u or not f:
                return jsonify({'status': 'error', 'msg': 'Username dan nama wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, full_name, role, pin, is_active) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), role=VALUES(role), pin=VALUES(pin), is_active=VALUES(is_active)", (u, f, r, p, a))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(0, 'user_sync', 'admin', 'Admin', new_data={'username': u, 'role': r}, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'User {u} saved'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/drivers/sync', methods=['POST'])
    def sync_driver():
        try:
            data = request.get_json()
            n = data.get('driver_name', '').strip().upper()
            p = data.get('nopol', '').strip().upper()
            v = data.get('vehicle_type', 'AVANZA')
            b = data.get('bbm_type', 'PERTALITE')
            if not n:
                return jsonify({'status': 'error', 'msg': 'Nama driver wajib'}), 400
            if not p:
                p = n
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO drivers (name, nopol, vehicle_type, bbm_type) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE nopol=VALUES(nopol), vehicle_type=VALUES(vehicle_type), bbm_type=VALUES(bbm_type), is_active=TRUE", (n, p, v, b))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(0, 'driver_sync', 'admin', 'Admin', new_data={'driver': n, 'nopol': p}, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'Driver {n} synced'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/drivers/<driver_name>/activate', methods=['POST'])
    def activate_driver(driver_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET is_active = TRUE WHERE name = %s", (driver_name,))
            conn.commit()
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': f'Driver {driver_name} activated'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/drivers/<driver_name>/deactivate', methods=['POST'])
    def deactivate_driver(driver_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET is_active=FALSE WHERE name=%s", (driver_name,))
            conn.commit()
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': f'Driver {driver_name} deactivated'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/drivers/<driver_name>/delete', methods=['POST', 'DELETE'])
    def delete_driver(driver_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drivers WHERE name = %s", (driver_name,))
            conn.commit()
            affected = cursor.rowcount
            cursor.close(); conn.close()
            if affected > 0:
                return jsonify({'status': 'success', 'msg': f'Driver {driver_name} dihapus'})
            else:
                return jsonify({'status': 'error', 'msg': 'Driver tidak ditemukan'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/system-config/<config_key>')
    def api_system_config(config_key):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT config_value FROM system_config WHERE config_key=%s", (config_key,))
            row = cursor.fetchone()
            cursor.close(); conn.close()
            return jsonify({'key': config_key, 'value': row['config_value'] if row else None})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/dummy-data/status')
    def dummy_data_status():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT config_value FROM system_config WHERE config_key='dummy_data_enabled'")
            row = cursor.fetchone()
            cursor.close(); conn.close()
            return jsonify({'enabled': row['config_value'] == 'true' if row else False})
        except Exception as e:
            return jsonify({'enabled': False, 'error': str(e)})

    @app.route('/api/dummy-data/toggle', methods=['POST'])
    def toggle_dummy_data():
        try:
            data = request.get_json()
            enable = data.get('enable', False)
            conn = get_db_connection()
            cursor = conn.cursor()
            if enable:
                cursor.execute("""
                    INSERT IGNORE INTO transactions (driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter, odo_km, spbu_type, status, km_per_liter, jumlah_appointment, is_dummy, gps_address, kronologis_text) VALUES
                    ('AKHAD','L 1413 CBI','AVANZA','PERTALITE',200000,20.00,10000,12936,'rekanan','archived',12.50,3,1,'Jl. Raya Darmo 45, Surabaya','Operasional marketing'),
                    ('AHMAT','B 2628 SRP','INNOVA','PERTAMAX',270000,20.00,13500,71126,'rekanan','archived',10.20,5,1,'Jl. Ahmad Yani 120, Surabaya','Kunjungan client'),
                    ('BUDI','L 1234 ABC','AVANZA','PERTALITE',150000,15.00,10000,45230,'non_rekanan','verified_ga',11.00,2,1,'Jl. Gubeng 78, Surabaya','Darurat non-rekanan'),
                    ('CANDRA','B 5678 DEF','INNOVA','PERTAMAX',300000,22.22,13500,89200,'rekanan','os_finance',9.50,4,1,'Jl. Sungkono 200, Surabaya','Mingguan')
                """)
            else:
                cursor.execute("DELETE FROM transactions WHERE is_dummy=1")
            cursor.execute("INSERT INTO system_config (config_key, config_value) VALUES ('dummy_data_enabled',%s) ON DUPLICATE KEY UPDATE config_value=VALUES(config_value)", ('true' if enable else 'false',))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(0, 'dummy_toggle', 'admin', 'Admin', new_data={'enabled': enable}, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'Dummy data {"enabled" if enable else "disabled"}'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/get-performance/<plat_nomor>')
    def get_performance(plat_nomor):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT km_per_liter, jumlah_appointment FROM transactions WHERE nopol=%s AND status IN ('verified','archived','os_finance','verified_ga','rejected') AND km_per_liter>0 AND created_at>=DATE_SUB(NOW(), INTERVAL 1 MONTH)", (plat_nomor,))
            data = cursor.fetchall()
            cursor.close(); conn.close()
            if not data:
                return jsonify({"nopol": plat_nomor, "status": "BELUM CUKUP DATA", "avg_kml": 0, "total_appointment": 0})
            avg_kml = sum([d['km_per_liter'] for d in data if d['km_per_liter']]) / len(data)
            total_apt = sum([d['jumlah_appointment'] for d in data if d['jumlah_appointment']])
            return jsonify({"nopol": plat_nomor, "status": "BAIK" if avg_kml>=10 else "BOROS", "avg_kml": round(avg_kml,2), "total_appointment": total_apt, "count": len(data)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/get-feedback/<nopol>')
    def get_vehicle_feedback(nopol):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT odo_km, liter, km_per_liter, jumlah_appointment, created_at FROM transactions WHERE nopol=%s AND status IN ('verified','archived','os_finance','verified_ga','rejected') AND km_per_liter>0 ORDER BY created_at DESC LIMIT 10", (nopol,))
            data = cursor.fetchall()
            cursor.close(); conn.close()
            if not data:
                return jsonify({"status": "info", "nopol": nopol, "msg": f"Belum ada data untuk {nopol}."})
            km_values = [d['km_per_liter'] for d in data if d['km_per_liter'] and d['km_per_liter']>0]
            if not km_values:
                return jsonify({"status": "info", "nopol": nopol, "msg": f"Data KM/L untuk {nopol} belum lengkap."})
            avg_kpl = sum(km_values)/len(km_values)
            total_apt = sum([d.get('jumlah_appointment',0) or 0 for d in data])
            performa = "SANGAT BAIK" if avg_kpl>=12 else ("BAIK" if avg_kpl>=10 else ("CUKUP" if avg_kpl>=8 else "BOROS"))
            msg = generate_human_insight(performa, avg_kpl, 12.0, total_apt, len(km_values))
            return jsonify({"status": "success", "nopol": nopol, "avg_km_per_liter": round(avg_kpl,2), "total_data": len(km_values), "total_appointment": total_apt, "performa": performa, "msg": msg})
        except Exception as e:
            return jsonify({"status": "error", "msg": str(e)}), 500

    @app.route('/api/stats')
    def api_stats():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as c FROM transactions"); total = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status IN ('pending','modified')"); pending = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='verified_ga'"); vga = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='os_finance'"); osf = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='archived'"); arc = cursor.fetchone()['c']
            cursor.close(); conn.close()
            return jsonify({'total': total, 'pending': pending, 'verified_ga': vga, 'os_finance': osf, 'archived': arc})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/audit-logs')
    def api_audit_logs():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, transaction_id, action, user_type, user_name, created_at, ip_address FROM activity_logs ORDER BY created_at DESC LIMIT 500")
            logs = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(logs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cross-check/<int:tx_id>')
    def api_cross_check(tx_id):
        log_activity_async(tx_id, 'cross_check_view', 'ga', 'GA Officer',
                          new_data={'action': 'view_cross_check'}, ip=request.remote_addr, ua=request.headers.get('User-Agent'))
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                cursor.close(); conn.close()
                return jsonify({'error': 'Transaction not found'}), 404
            
            cursor.execute("""
                SELECT odo_km, km_per_liter, created_at FROM transactions 
                WHERE nopol = %s AND status = 'archived' AND id < %s 
                ORDER BY id DESC LIMIT 1
            """, (tx['nopol'], tx_id))
            prev = cursor.fetchone()
            
            cursor.execute("""
                SELECT ROUND(AVG(NULLIF(km_per_liter,0)), 2) as avg_kml, COUNT(*) as tx_count
                FROM transactions WHERE nopol = %s AND status = 'archived' AND km_per_liter > 0 
                AND created_at >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            """, (tx['nopol'],))
            avg_data = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) as total_tx, COALESCE(SUM(nominal),0) as total_nominal
                FROM transactions WHERE driver_name = %s AND status = 'archived' 
                AND MONTH(created_at) = MONTH(CURDATE())
            """, (tx['driver_name'],))
            monthly = cursor.fetchone()
            
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'monthly_budget'")
            budget_row = cursor.fetchone()
            budget = float(budget_row['config_value']) if budget_row else 3000000
            
            cursor.execute("""
                SELECT id, odo_km, km_per_liter, nominal, created_at 
                FROM transactions WHERE nopol = %s AND status = 'archived' AND id < %s
                ORDER BY id DESC LIMIT 3
            """, (tx['nopol'], tx_id))
            last3 = cursor.fetchall()
            
            avg_kml = float(avg_data['avg_kml']) if avg_data and avg_data['avg_kml'] else 10.0
            health_score = min(100, max(0, int((avg_kml / 14) * 100)))
            
            flags = []
            odo_diff = float(tx['odo_km']) - float(prev['odo_km']) if prev else 0.0
            
            if odo_diff < 0:
                flags.append({'level': 'danger', 'msg': '⚠️ ODO MUNDUR! ODO sebelumnya lebih tinggi'})
            elif odo_diff == 0:
                flags.append({'level': 'warning', 'msg': '⚠️ ODO tidak berubah dari transaksi sebelumnya'})
            elif odo_diff < 30:
                flags.append({'level': 'warning', 'msg': f'⚠️ Jarak tempuh hanya {odo_diff} km (kemungkinan top-up)'})
            
            current_kml = float(tx['km_per_liter']) if tx['km_per_liter'] and float(tx['km_per_liter']) > 0 else None
            if current_kml and avg_data and avg_data['avg_kml']:
                if current_kml < float(avg_data['avg_kml']) * 0.7:
                    flags.append({'level': 'warning', 'msg': f'⚠️ KM/L ({current_kml}) jauh di bawah rata-rata 3 bulan ({avg_data["avg_kml"]})'})
                elif current_kml > float(avg_data['avg_kml']) * 1.5:
                    flags.append({'level': 'warning', 'msg': f'⚠️ KM/L ({current_kml}) jauh di atas rata-rata 3 bulan ({avg_data["avg_kml"]})'})
            
            budget_usage = (float(monthly['total_nominal']) / budget * 100) if budget > 0 else 0
            if budget_usage > 80:
                flags.append({'level': 'warning', 'msg': f'⚠️ Budget bulan ini sudah {budget_usage:.0f}%'})
            elif budget_usage > 100:
                flags.append({'level': 'danger', 'msg': f'🔴 Budget bulan ini SUDAH HABIS! ({budget_usage:.0f}%)'})
            
            has_danger = any(f['level'] == 'danger' for f in flags)
            has_warning = any(f['level'] == 'warning' for f in flags)
            overall = 'danger' if has_danger else ('warning' if has_warning else 'success')
            
            cursor.close(); conn.close()
            
            return jsonify({
                'current': {
                    'id': tx['id'], 'nopol': tx['nopol'], 'driver_name': tx['driver_name'],
                    'odo_km': float(tx['odo_km']), 'nominal': float(tx['nominal']), 'liter': float(tx['liter']),
                    'km_per_liter': float(tx['km_per_liter']) if tx['km_per_liter'] else 0, 'jumlah_appointment': tx.get('jumlah_appointment', 0)
                },
                'previous_odo': {'odo_km': prev['odo_km'], 'km_per_liter': prev['km_per_liter'], 'date': str(prev['created_at'])} if prev else None,
                'odo_diff': odo_diff if prev else 0,
                'avg_3months': {'avg_kml': avg_data['avg_kml'], 'tx_count': avg_data['tx_count']} if avg_data else None,
                'monthly': {'total_tx': monthly['total_tx'], 'total_nominal': float(monthly['total_nominal'])},
                'budget': budget,
                'budget_usage_percent': round(budget_usage, 1),
                'health_score': health_score,
                'last_3': [{'odo': l['odo_km'], 'kml': l['km_per_liter'], 'nominal': float(l['nominal'])} for l in last3],
                'flags': flags,
                'overall': overall,
                'recommendation': '✅ AMAN untuk diapprove' if overall == 'success' else ('⚠️ PERLU PERHATIAN' if overall == 'warning' else '🔴 PERLU INVESTIGASI!')
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/transaction-flags')
    def api_transaction_flags():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nopol, driver_name, odo_km, km_per_liter, nominal, jumlah_appointment FROM transactions WHERE status IN ('pending','modified') ORDER BY created_at ASC")
            txs = cursor.fetchall()
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'monthly_budget'")
            budget_row = cursor.fetchone()
            budget = float(budget_row['config_value']) if budget_row else 3000000
            result = {}
            for tx in txs:
                flags = []
                cursor.execute("SELECT odo_km FROM transactions WHERE nopol = %s AND status = 'archived' AND id < %s ORDER BY id DESC LIMIT 1", (tx['nopol'], tx['id']))
                prev = cursor.fetchone()
                if prev:
                    odo_diff = float(tx['odo_km']) - float(prev['odo_km'])
                    if odo_diff < 0: flags.append({'level': 'danger', 'msg': 'ODO mundur'})
                    elif odo_diff == 0: flags.append({'level': 'warning', 'msg': 'ODO tidak berubah'})
                    elif odo_diff < 30: flags.append({'level': 'warning', 'msg': f'Top-up ({odo_diff} km)'})
                result[str(tx['id'])] = {'flags': flags, 'overall': 'danger' if any(f['level']=='danger' for f in flags) else ('warning' if any(f['level']=='warning' for f in flags) else 'success')}
            cursor.close(); conn.close()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vehicle-health')
    def api_vehicle_health():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.nopol, t.vehicle_type, COUNT(t.id) as total_tx,
                       ROUND(AVG(NULLIF(t.km_per_liter,0)), 2) as avg_kml,
                       MAX(t.created_at) as last_activity,
                       SUM(t.nominal) as total_nominal,
                       COALESCE(SUM(t.jumlah_appointment),0) as total_appt,
                       (SELECT va.driver_name FROM vehicle_assignments va WHERE va.nopol = t.nopol AND va.is_current = 1 ORDER BY va.id DESC LIMIT 1) as current_driver,
                       (SELECT va.driver_notes FROM vehicle_assignments va WHERE va.nopol = t.nopol ORDER BY va.id DESC LIMIT 1) as latest_notes
                FROM transactions t WHERE t.status = 'archived'
                GROUP BY t.nopol, t.vehicle_type ORDER BY avg_kml DESC
            """)
            units = cursor.fetchall()
            for unit in units:
                kml = unit['avg_kml'] if unit['avg_kml'] else 10
                tx_count = unit['total_tx']
                kml_score = min(100, (kml / 14) * 60)
                days_since = 30
                if unit['last_activity']:
                    days_since = (datetime.now() - unit['last_activity']).days
                activity_score = max(0, 20 - min(20, days_since))
                tx_score = min(20, tx_count * 2)
                health = min(100, int(kml_score + activity_score + tx_score))
                unit['health_score'] = health
                unit['status'] = 'good' if health >= 70 else ('warning' if health >= 40 else 'danger')
            cursor.close(); conn.close()
            return jsonify({
                'units': units,
                'total_active_units': len(units),
                'avg_fleet_health': round(sum(u['health_score'] for u in units) / len(units)) if units else 0
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/assignment-remark', methods=['POST'])
    def api_assignment_remark():
        try:
            data = request.get_json()
            nopol = data.get('nopol', '').strip()
            remark = data.get('remark', '').strip()
            driver_name = data.get('driver_name', '').strip()
            if not nopol or not remark:
                return jsonify({'status': 'error', 'msg': 'Nopol dan remark wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM vehicle_assignments WHERE nopol = %s AND is_current = 1 ORDER BY id DESC LIMIT 1", (nopol,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE vehicle_assignments SET driver_notes = %s WHERE id = %s", (remark, existing[0]))
            else:
                cursor.execute("""
                    INSERT INTO vehicle_assignments (driver_name, nopol, vehicle_type, bbm_type, assigned_date, is_current, driver_notes)
                    SELECT name, nopol, vehicle_type, bbm_type, CURDATE(), 1, %s FROM drivers WHERE nopol = %s AND is_active = 1 LIMIT 1
                """, (remark, nopol))
            conn.commit()
            log_activity_async(0, 'ga_remark', 'ga', driver_name or 'GA Officer', new_data={'nopol': nopol, 'remark': remark}, ip=request.remote_addr)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': 'Remark berhasil disimpan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/finance-review/<int:tx_id>')
    def api_finance_review(tx_id):
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                cursor.close(); conn.close()
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT odo_km, created_at FROM transactions WHERE nopol = %s AND status = 'archived' AND id < %s ORDER BY id DESC LIMIT 1", (tx['nopol'], tx_id))
            prev = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) as total_tx, COALESCE(SUM(nominal),0) as total_nominal FROM transactions WHERE driver_name = %s AND MONTH(created_at) = MONTH(CURDATE())", (tx['driver_name'],))
            monthly = cursor.fetchone()
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'monthly_budget'")
            budget_row = cursor.fetchone()
            budget = float(budget_row['config_value']) if budget_row else 3000000
            photos = []
            for field, label in [('foto_odo_sebelum','ODO Sebelum'),('foto_nota_odo_sesudah','ODO + Nota'),('foto_struk','Struk BBM'),('foto_struk_dispenser','Dispenser')]:
                if tx.get(field):
                    photos.append({'label': label, 'url': '/uploads/' + tx[field], 'field': field})
            cursor.close(); conn.close()
            return jsonify({
                'transaction': {
                    'id': tx['id'], 'nopol': tx['nopol'], 'driver_name': tx['driver_name'],
                    'vehicle_type': tx['vehicle_type'], 'bbm_type': tx['bbm_type'],
                    'nominal': float(tx['nominal']), 'liter': float(tx['liter']),
                    'price_per_liter': float(tx['price_per_liter']),
                    'odo_km': float(tx['odo_km']), 'km_per_liter': float(tx['km_per_liter']) if tx['km_per_liter'] else 0,
                    'jumlah_appointment': tx.get('jumlah_appointment', 0),
                    'spbu_type': tx['spbu_type'], 'gps_address': tx.get('gps_address', ''),
                    'created_at': str(tx['created_at']), 'status': tx['status']
                },
                'previous_odo': {'odo_km': prev['odo_km'], 'date': str(prev['created_at'])} if prev else None,
                'monthly': {'total_tx': monthly['total_tx'], 'total_nominal': float(monthly['total_nominal'])},
                'budget': budget,
                'photos': photos
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/finance-remark', methods=['POST'])
    def api_finance_remark():
        try:
            data = request.get_json()
            tx_id = data.get('tx_id')
            remark = data.get('remark', '').strip()
            username = data.get('username', 'Finance Officer')
            if not tx_id or not remark:
                return jsonify({'status': 'error', 'msg': 'ID transaksi dan remark wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions SET transaction_notes = CONCAT(COALESCE(transaction_notes,''), '\n[', NOW(), '] ', %s, ': ', %s)
                WHERE id = %s
            """, (username, remark, tx_id))
            conn.commit()
            log_activity_async(tx_id, 'finance_remark', 'finance', username, new_data={'remark': remark}, ip=request.remote_addr)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': 'Remark berhasil disimpan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/assignments/create', methods=['POST'])
    def api_create_assignment():
        try:
            data = request.get_json()
            driver_name = data.get('driver_name', '').strip().upper()
            nopol = data.get('nopol', '').strip().upper()
            vehicle_type = data.get('vehicle_type', '').strip()
            bbm_type = data.get('bbm_type', 'PERTALITE').strip()
            notes = data.get('notes', '').strip()
            if not driver_name or not nopol:
                return jsonify({'status': 'error', 'msg': 'Driver dan Nopol wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE vehicle_assignments SET is_current = 0, unassigned_date = CURDATE() WHERE nopol = %s AND is_current = 1", (nopol,))
            cursor.execute("""
                INSERT INTO vehicle_assignments (driver_name, nopol, vehicle_type, bbm_type, assigned_date, is_current, driver_notes)
                VALUES (%s, %s, %s, %s, CURDATE(), 1, %s)
            """, (driver_name, nopol, vehicle_type, bbm_type, notes))
            cursor.execute("""
                INSERT INTO drivers (name, nopol, vehicle_type, bbm_type, is_active)
                VALUES (%s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE nopol = VALUES(nopol), vehicle_type = VALUES(vehicle_type), bbm_type = VALUES(bbm_type), is_active = 1
            """, (driver_name, nopol, vehicle_type, bbm_type))
            conn.commit()
            log_activity_async(0, 'ga_assign_vehicle', 'ga', 'GA Officer', new_data={'driver': driver_name, 'nopol': nopol}, ip=request.remote_addr)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': f'{driver_name} ditugaskan ke {nopol} ({vehicle_type})'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
    @app.route('/api/trip-detail/<int:trip_id>')
    def api_trip_detail(trip_id):
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM trip_masters WHERE id = %s", (trip_id,))
            master = cursor.fetchone()
            if not master:
                cursor.close(); conn.close()
                return jsonify({'error': 'Trip not found'}), 404
            cursor.execute("SELECT * FROM trip_details WHERE trip_master_id = %s ORDER BY no_urut", (trip_id,))
            details = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify({'master': master, 'details': details})
        except Exception as e:
            return jsonify({'error': str(e)}), 500



    @app.route('/api/assignments/history')
    def api_assignment_history():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT va.*, DATEDIFF(COALESCE(va.unassigned_date, CURDATE()), va.assigned_date) as duration_days
                FROM vehicle_assignments va ORDER BY va.id DESC LIMIT 100
            """)
            history = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(history)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    @app.route('/api/assignments/active')
    def api_active_assignments():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vehicle_assignments WHERE is_current = 1 ORDER BY assigned_date DESC")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    @app.route('/api/assignments/swap-history')
    def api_swap_history():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM assignment_swaps ORDER BY created_at DESC LIMIT 100")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    @app.route('/api/assignments/unassigned')
    def api_unassigned_vehicles():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT v.nopol, v.vehicle_type, COALESCE(v.bbm_default, 'PERTALITE') as bbm_type
                FROM vehicles v
                WHERE v.is_active = 1 AND v.nopol IS NOT NULL AND v.nopol != ''
                AND v.nopol NOT IN (
                    SELECT va.nopol FROM vehicle_assignments va WHERE va.is_current = 1
                )
                ORDER BY v.nopol
            ''')
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    @app.route('/api/assignments/swap', methods=['POST'])
    def api_swap_assignment():
        try:
            data = request.get_json()
            nopol = data.get('nopol', '').strip()
            new_driver = data.get('new_driver', '').strip()
            category = data.get('category', 'other').strip()
            reason = data.get('reason', '').strip()
            ga_name = data.get('ga_name', 'GA Officer').strip()
            
            if not all([nopol, new_driver, category, reason, ga_name]):
                return jsonify({'status': 'error', 'msg': 'Semua field wajib diisi'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Cari assignment aktif
            cursor.execute("SELECT * FROM vehicle_assignments WHERE nopol = %s AND is_current = 1 ORDER BY id DESC LIMIT 1", (nopol,))
            old = cursor.fetchone()
            old_driver = old['driver_name'] if old else None
            vehicle_type = old['vehicle_type'] if old else 'AVANZA'
            bbm_type = old['bbm_type'] if old else 'PERTALITE'
            
            # Nonaktifkan assignment lama
            if old:
                cursor.execute("UPDATE vehicle_assignments SET is_current = 0, unassigned_date = CURDATE() WHERE id = %s", (old['id'],))
            
            # Buat assignment baru
            cursor.execute("INSERT INTO vehicle_assignments (driver_name, nopol, vehicle_type, bbm_type, assigned_date, is_current, driver_notes) VALUES (%s, %s, %s, %s, CURDATE(), 1, %s)", (new_driver, nopol, vehicle_type, bbm_type, reason))
            
            # Update driver table
            cursor.execute("UPDATE drivers SET nopol = %s, vehicle_type = %s, bbm_type = %s WHERE name = %s", (nopol, vehicle_type, bbm_type, new_driver))
            if old_driver:
                cursor.execute("UPDATE drivers SET nopol = '' WHERE name = %s AND nopol = %s", (old_driver, nopol))
            
            # Log swap
            cursor.execute("INSERT INTO assignment_swaps (nopol, old_driver, new_driver, category, reason, ga_name) VALUES (%s, %s, %s, %s, %s, %s)", (nopol, old_driver, new_driver, category, reason, ga_name))
            
            conn.commit()
            log_activity_async(0, 'ga_swap_vehicle', 'ga', ga_name, new_data={'nopol': nopol, 'old_driver': old_driver, 'new_driver': new_driver, 'category': category, 'reason': reason})
            cursor.close(); conn.close()
            
            return jsonify({'status': 'success', 'msg': nopol + ' berhasil ditukar: ' + (old_driver or '-') + ' → ' + new_driver})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
    @app.route('/api/assignments/release', methods=['POST'])
    def api_release_assignment():
        try:
            data = request.get_json()
            nopol = data.get('nopol', '').strip()
            reason = data.get('reason', '').strip()
            ga_name = data.get('ga_name', 'GA Officer').strip()
            
            if not nopol or not reason:
                return jsonify({'status': 'error', 'msg': 'Nopol dan alasan wajib'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM vehicle_assignments WHERE nopol = %s AND is_current = 1 ORDER BY id DESC LIMIT 1", (nopol,))
            assignment = cursor.fetchone()
            
            if not assignment:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Tidak ada assignment aktif untuk ' + nopol}), 404
            
            cursor.execute("UPDATE vehicle_assignments SET is_current = 0, unassigned_date = CURDATE(), cancel_reason = %s, cancelled_by = %s WHERE id = %s", (reason, ga_name, assignment['id']))
            cursor.execute("INSERT INTO assignment_swaps (nopol, old_driver, new_driver, category, reason, ga_name) VALUES (%s, %s, %s, %s, %s, %s)", (nopol, assignment['driver_name'], '- (Dilepas)', 'vehicle_issue', reason, ga_name))
            
            # Kembalikan nopol asli driver (dari assignment sebelumnya)
            cursor.execute("SELECT nopol FROM vehicle_assignments WHERE driver_name = %s AND id < %s ORDER BY id DESC LIMIT 1", (assignment['driver_name'], assignment['id']))
            prev = cursor.fetchone()
            if prev and prev['nopol']:
                cursor.execute("UPDATE drivers SET nopol = %s WHERE name = %s", (prev['nopol'], assignment['driver_name']))
            else:
                cursor.execute("UPDATE drivers SET nopol = '' WHERE name = %s", (assignment['driver_name'],))
            
            conn.commit()
            
            try:
                log_activity_async(0, 'ga_release_vehicle', 'ga', ga_name, new_data={'nopol': nopol, 'driver': assignment['driver_name'], 'reason': reason})
            except:
                pass
            
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': nopol + ' dilepas dari ' + assignment['driver_name']})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500






    @app.route('/api/assignments/pending')
    def api_pending_assignments():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vehicle_assignments WHERE is_current = 1 AND confirmed_by_driver = 0 ORDER BY assigned_date DESC")
            pending = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(pending)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/assignments/confirm', methods=['POST'])
    def api_confirm_assignment():
        try:
            data = request.get_json()
            driver_name = data.get('driver_name', '').strip().upper()
            nopol = data.get('nopol', '').strip().upper()
            if not driver_name or not nopol:
                return jsonify({'status': 'error', 'msg': 'Data tidak lengkap'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehicle_assignments SET confirmed_by_driver = 1, confirmed_at = NOW()
                WHERE driver_name = %s AND nopol = %s AND is_current = 1 AND confirmed_by_driver = 0
                ORDER BY id DESC LIMIT 1
            """, (driver_name, nopol))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                log_activity_async(0, 'driver_confirm_assignment', 'driver', driver_name, new_data={'nopol': nopol}, ip=request.remote_addr)
            cursor.close(); conn.close()
            if affected > 0:
                return jsonify({'status': 'success', 'msg': f'Konfirmasi serah terima {nopol} berhasil! ✅'})
            else:
                return jsonify({'status': 'error', 'msg': 'Tidak ada assignment pending'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/analytics/data')
    def api_analytics_data():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT COALESCE(SUM(nominal),0) as total_month, COUNT(*) as total_tx,
                       ROUND(COALESCE(SUM(nominal),0) / GREATEST(DATEDIFF(CURDATE(), DATE_SUB(CURDATE(), INTERVAL 1 MONTH)), 1)) as avg_per_day,
                       ROUND(COALESCE(AVG(nominal),0)) as avg_per_tx
                FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
            """)
            fin = cursor.fetchone()
            
            cursor.execute("""
                SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(nominal) as total
                FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY month ORDER BY month
            """)
            monthly = cursor.fetchall()
            
            cursor.execute("""
                SELECT driver_name, nopol, SUM(nominal) as total, COUNT(*) as tx_count
                FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                GROUP BY driver_name, nopol ORDER BY total DESC LIMIT 5
            """)
            top_drivers = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as c FROM drivers WHERE is_active=1")
            total_drivers = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)")
            total_claims = cursor.fetchone()['c']
            
            # Frekuensi klaim per driver
            cursor.execute('''
                SELECT driver_name, COUNT(*) as c FROM transactions WHERE status='archived'
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) GROUP BY driver_name ORDER BY c DESC
            ''')
            freq = cursor.fetchall()
            
            # Appointment vs Klaim
            cursor.execute('''
                SELECT driver_name, COALESCE(SUM(jumlah_appointment),0) as appt, COUNT(*) as klaim
                FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                GROUP BY driver_name ORDER BY klaim DESC
            ''')
            appt_data = cursor.fetchall()
            
            # Top driver (paling sering klaim)
            cursor.execute('''SELECT driver_name, COUNT(*) as c FROM transactions WHERE status='archived'
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                GROUP BY driver_name ORDER BY c DESC LIMIT 1''')
            top_driver_row = cursor.fetchone()
            
            # Total appointment
            cursor.execute("SELECT COALESCE(SUM(jumlah_appointment),0) as c FROM transactions WHERE status='archived' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)")
            total_appt = cursor.fetchone()['c']
            
            cursor.execute("""
                SELECT nopol, ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml, COUNT(*) as tx_count
                FROM transactions WHERE status='archived' AND km_per_liter > 0
                GROUP BY nopol ORDER BY avg_kml DESC
            """)
            eff = cursor.fetchall()
            
            # Anomaly count
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE ml_anomaly_flag=1 AND status='archived'")
            anomaly = cursor.fetchone()['c']
            
            # Service alerts (KM/L < 9)
            cursor.execute('''
                SELECT nopol, ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml, COUNT(*) as tx_count
                FROM transactions WHERE status='archived' AND km_per_liter > 0
                GROUP BY nopol HAVING avg_kml < 9 ORDER BY avg_kml
            ''')
            service = cursor.fetchall()
            
            cursor.close(); conn.close()
            
            return jsonify({
                'finance': {
                    'total_month': float(fin['total_month']), 'total_tx': fin['total_tx'],
                    'avg_per_day': float(fin['avg_per_day']), 'avg_per_tx': float(fin['avg_per_tx']),
                    'monthly_labels': [m['month'] for m in monthly],
                    'monthly_amounts': [float(m['total']) for m in monthly],
                    'top_drivers': [{'driver_name': t['driver_name'], 'nopol': t['nopol'], 'total': float(t['total']), 'tx_count': t['tx_count']} for t in top_drivers]
                },
                'ga': {'total_drivers': total_drivers, 'total_claims': total_claims, 'total_appt': int(total_appt) if 'total_appt' in dir() else 0, 'top_driver': top_driver_row['driver_name'] if top_driver_row else '-', 'freq_labels': [f['driver_name'] for f in freq], 'freq_values': [f['c'] for f in freq], 'appt_vs_claim': [{'driver_name': a['driver_name'], 'appt': int(a['appt']), 'klaim': a['klaim']} for a in appt_data]},
                'fleet': {
                    'best_vehicle': eff[0]['nopol'] + ' (' + str(eff[0]['avg_kml']) + ' KM/L)' if eff else '-',
                    'worst_vehicle': eff[-1]['nopol'] + ' (' + str(eff[-1]['avg_kml']) + ' KM/L)' if eff else '-',
                    'avg_kml': round(sum([float(e['avg_kml']) for e in eff]) / len(eff), 1) if eff else 0,
                    'anomaly_count': anomaly,
                    'eff_labels': [e['nopol'] for e in eff],
                    'eff_values': [float(e['avg_kml']) if e['avg_kml'] else 0 for e in eff],
                    'service_alerts': [{'nopol': s['nopol'], 'avg_kml': float(s['avg_kml']), 'tx_count': s['tx_count']} for s in service]
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vehicles/with-nopol')
    def api_vehicles_with_nopol():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nopol, vehicle_type, bbm_default FROM vehicles WHERE is_active=1 AND nopol IS NOT NULL AND nopol != '' ORDER BY nopol")
            data = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vehicles/add', methods=['POST'])
    def api_add_vehicle():
        try:
            data = request.get_json()
            nopol = data.get('nopol', '').strip().upper()
            vehicle_type = data.get('vehicle_type', 'AVANZA').strip().upper()
            brand = data.get('brand', 'Toyota').strip()
            bbm_default = data.get('bbm_default', 'PERTALITE').strip().upper()
            if not nopol:
                return jsonify({'status': 'error', 'msg': 'No. Polisi wajib'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vehicles (vehicle_type, nopol, brand, fuel_capacity, bbm_default, is_active) VALUES (%s, %s, %s, 45, %s, 1) ON DUPLICATE KEY UPDATE vehicle_type=VALUES(vehicle_type), brand=VALUES(brand), bbm_default=VALUES(bbm_default), is_active=1", (vehicle_type, nopol, brand, bbm_default))
            conn.commit()
            cursor.close(); conn.close()
            log_activity_async(0, 'vehicle_add', 'admin', 'Admin', new_data={'nopol': nopol, 'type': vehicle_type})
            return jsonify({'status': 'success', 'msg': f'Kendaraan {nopol} ({vehicle_type}) ditambahkan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
