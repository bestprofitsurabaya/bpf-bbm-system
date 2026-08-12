"""Appointment System - Marketing & Chief Driver flows.

Alur bisnis:
  Marketing (mis. Icang dari Tim Yusie) mengisi appointment: nama calon nasabah,
  alamat, dan sesi (1 = 08.30 / 2 = 14.30).
  -> Chief Driver menugaskan driver berdasarkan alamat (area terdeteksi otomatis).
  -> Appointment selesai (completed) otomatis tersedia di form Log Perjalanan
     driver (trip PWA) untuk diisi rute & di-submit.
"""
from datetime import date, datetime

from flask import (redirect, request, jsonify, session, make_response)
from modules.config import get_db_connection
from modules.helpers import (role_required, log_activity_async,
                             generate_appointment_display_id,
                             validate_appointment_input, detect_area,
                             get_or_create_team, register_marketing_member,
                             get_team_members, session_driver_name,
                             resolve_driver_scope)
from modules.realtime import emit_event

# Hasil kunjungan yang dicatat driver / chief driver saat menandai selesai.
# Data ini menjadi sumber statistik konversi marketing.
VISIT_RESULTS = ('ditemui', 'prospek', 'gagal')
VISIT_RESULT_LABELS = {
    'ditemui': '😊 Ditemui',
    'prospek': '🤝 Prospek',
    'gagal': '❌ Gagal',
}


def _visit_result_label(value):
    return VISIT_RESULT_LABELS.get(value or '', value or '')


def _clean(row):
    """Normalisasi satu baris appointment DB -> dict JSON-safe."""
    if not row:
        return row
    row = dict(row)
    for k in ('appointment_date',):
        if row.get(k) is not None and not isinstance(row[k], str):
            row[k] = str(row[k])
    return row


def _current_user():
    return {
        'username': session.get('user_name', ''),
        'full_name': session.get('full_name', session.get('user_name', '')),
        'role': session.get('user_role', ''),
    }


def _user_team_name(username):
    """Ambil team_name dari tabel users (fallback '' jika gagal)."""
    try:
        conn = get_db_connection()
        if not conn:
            return ''
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT team_name FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        return (row or {}).get('team_name') or ''
    except Exception as e:
        print(f"[appointments] user team error: {e}")
        return ''


def _finalize_appointment_complete(appt_id, row, audit_action, actor_role, actor_name,
                                   notif_msg, driver_for_event=None,
                                   visit_result=None, visit_note=''):
    """Shared finalisasi appointment -> completed: UPDATE + audit + realtime + notif marketing.

    Dipakai oleh alur Chief Driver (tombol ✅) dan PWA driver (🏁 Selesai Dikunjungi)
    agar kedua alur tidak bisa drift. `row` = dict appointment hasil SELECT.
    `visit_result` (ditemui/prospek/gagal) & `visit_note` adalah hasil kunjungan
    yang dicatat untuk statistik konversi marketing.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE appointments SET status='completed', completed_at=NOW(), updated_at=NOW(), "
            "visit_result=%s, visit_note=%s "
            "WHERE id=%s AND status='assigned'",
            (visit_result, (visit_note or '')[:255], appt_id))
        conn.commit()
        log_activity_async(appt_id, audit_action, actor_role, actor_name,
                           new_data={'driver': row.get('driver_name')}, ip=request.remote_addr)
        cursor.close()
        conn.close()
        emit_event('appointment_update',
                   {'action': 'completed', 'id': appt_id, 'display_id': row['display_id'],
                    'driver': driver_for_event or row.get('driver_name'),
                    'date': str(row['appointment_date'])},
                   room='appointments_board')
        from modules.notifications import push_marketing_notification
        push_marketing_notification(
            row['marketing_username'], 'appointment', 'completed', notif_msg, row['display_id'])
    except Exception as e:
        print(f"[appointments] finalize complete error: {e}")


def _suggest_driver(cursor, target_date, sesi):
    """Driver aktif dengan beban paling ringan pada tanggal+sesi tersebut
    (untuk saran penugasan di halaman Chief Driver)."""
    cursor.execute(
        """SELECT d.name FROM drivers d
           LEFT JOIN (
               SELECT driver_name, COUNT(*) c FROM appointments
               WHERE appointment_date=%s AND sesi=%s AND status IN ('scheduled','assigned')
               GROUP BY driver_name
           ) a ON a.driver_name = d.name
           WHERE d.is_active=TRUE
           ORDER BY COALESCE(a.c,0) ASC, d.name ASC LIMIT 1""",
        (target_date, sesi))
    row = cursor.fetchone()
    return row['name'] if row else None


def register_appointment_routes(app):

    # ================================================================
    # PAGES
    # ================================================================
    @app.route('/marketing')
    @role_required(['marketing'])
    def marketing_page():
        # v2.5: halaman klasik dipensiunkan → SPA
        return redirect('/app/marketing')

    @app.route('/chief-driver')
    @role_required(['chief_driver', 'ga', 'admin'])
    def chief_driver_page():
        # v2.5: halaman klasik dipensiunkan → SPA
        return redirect('/app/chief-driver')

    # ================================================================
    # LIST APPOINTMENTS
    # ================================================================
    @app.route('/api/appointments')
    @role_required(['marketing', 'chief_driver', 'ga', 'admin'])
    def api_appointments():
        try:
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            sesi = request.args.get('sesi', '').strip()
            status = request.args.get('status', '').strip()
            team = request.args.get('team', '').strip()
            driver = request.args.get('driver', '').strip()
            marketing = request.args.get('marketing', '').strip()
            member = request.args.get('member', '').strip()

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)

            where = ["appointment_date = %s"]
            params = [target_date]
            if session.get('user_role') == 'marketing':
                where.append("marketing_username = %s")
                params.append(session.get('user_name'))
            else:
                if marketing:
                    where.append("marketing_username = %s")
                    params.append(marketing)
                if team:
                    where.append("team_name = %s")
                    params.append(team)
                if driver:
                    where.append("driver_name = %s")
                    params.append(driver)
            if member:
                where.append("marketing_member LIKE %s")
                params.append(f"%{member}%")
            if sesi in ('1', '2'):
                where.append("sesi = %s")
                params.append(sesi)
            if status in ('scheduled', 'assigned', 'completed', 'cancelled'):
                where.append("status = %s")
                params.append(status)

            cursor.execute(
                "SELECT * FROM appointments WHERE " + " AND ".join(where) +
                " ORDER BY sesi ASC, created_at ASC", params)
            rows = [_clean(r) for r in cursor.fetchall()]

            # Stats ringkas untuk tanggal tersebut (selalu untuk scope user + filter member)
            stats_where = ["appointment_date = %s"]
            stats_params = [target_date]
            if session.get('user_role') == 'marketing':
                stats_where.append("marketing_username = %s")
                stats_params.append(session.get('user_name'))
            if member:
                stats_where.append("marketing_member LIKE %s")
                stats_params.append(f"%{member}%")
            cursor.execute(
                "SELECT status, sesi, COUNT(*) c FROM appointments WHERE " +
                " AND ".join(stats_where) + " GROUP BY status, sesi", stats_params)
            stats = {'total': 0, 'sesi1': 0, 'sesi2': 0,
                     'scheduled': 0, 'assigned': 0, 'completed': 0, 'cancelled': 0}
            for s in cursor.fetchall():
                stats['total'] += s['c']
                if s['sesi'] == '1':
                    stats['sesi1'] += s['c']
                else:
                    stats['sesi2'] += s['c']
                stats[s['status']] = stats.get(s['status'], 0) + s['c']

            cursor.close(); conn.close()
            return jsonify({'data': rows, 'stats': stats})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # SUGGESTED DRIVERS (load balancing per sesi)
    # ================================================================
    @app.route('/api/appointments/suggestions')
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_appointment_suggestions():
        try:
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            result = {}
            for sesi in ('1', '2'):
                result[sesi] = _suggest_driver(cursor, target_date, sesi)
            cursor.close(); conn.close()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # CREATE (marketing; support multi-append dalam satu submit)
    # ================================================================
    @app.route('/api/appointments', methods=['POST'])
    @role_required(['marketing'])
    def api_create_appointments():
        try:
            data = request.get_json(silent=True) or {}
            items = data.get('appointments') if isinstance(data.get('appointments'), list) else [data]
            if not items:
                return jsonify({'status': 'error', 'msg': 'Tidak ada data appointment'}), 400
            if len(items) > 20:
                return jsonify({'status': 'error', 'msg': 'Maksimal 20 appointment per submit'}), 400

            user = _current_user()
            team_name = _user_team_name(user['username'])
            if team_name:
                get_or_create_team(team_name)

            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)

            created = []
            errors = []
            idx = 0
            for item in items:
                idx += 1
                valid, errs, norm = validate_appointment_input(item)
                if not valid:
                    errs['_index'] = idx
                    errors.append(errs)
                    continue
                try:
                    datetime.strptime(norm['appointment_date'], '%Y-%m-%d')
                except ValueError:
                    errs['appointment_date'] = 'Format tanggal harus YYYY-MM-DD'
                    errs['_index'] = idx
                    errors.append(errs)
                    continue
                area = detect_area(norm['alamat'])
                register_marketing_member(team_name, norm['marketing_member'])
                display_id = generate_appointment_display_id(conn)
                cursor.execute(
                    """INSERT INTO appointments
                       (display_id, marketing_username, marketing_name, marketing_member,
                        team_name, nasabah_name, nasabah_phone, alamat, area,
                        appointment_date, sesi, status, notes)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'scheduled',%s)""",
                    (display_id, user['username'], user['full_name'], norm['marketing_member'],
                     team_name, norm['nasabah_name'], norm['nasabah_phone'], norm['alamat'], area,
                     norm['appointment_date'], norm['sesi'], norm['notes']))
                created.append({
                    'id': cursor.lastrowid,
                    'display_id': display_id,
                    'area': area,
                    'sesi': norm['sesi'],
                    'appointment_date': norm['appointment_date'],
                })

            if created:
                conn.commit()
                log_activity_async(0, 'appointment_create', 'marketing', user['full_name'],
                                   new_data={'count': len(created), 'team': team_name},
                                   ip=request.remote_addr)
            cursor.close(); conn.close()

            if created:
                emit_event('appointment_update',
                           {'action': 'created', 'count': len(created),
                            'date': items[0].get('appointment_date', '')},
                           room='appointments_board')
                return jsonify({'status': 'success',
                                'msg': f'{len(created)} appointment berhasil dibuat!',
                                'created': created,
                                'errors': errors})
            return jsonify({'status': 'error', 'msg': 'Semua input tidak valid',
                            'created': [], 'errors': errors}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # EDIT (marketing: milik sendiri & masih scheduled)
    # ================================================================
    @app.route('/api/appointments/<int:appt_id>', methods=['PATCH'])
    @role_required(['marketing', 'chief_driver', 'ga', 'admin'])
    def api_update_appointment(appt_id):
        try:
            data = request.get_json(silent=True) or {}
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404

            user = _current_user()
            is_marketing = user['role'] == 'marketing'

            if is_marketing:
                # Marketing hanya boleh mengedit miliknya yang belum ditugaskan
                if row['marketing_username'] != user['username']:
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Bukan appointment Anda'}), 403
                if row['status'] != 'scheduled':
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Appointment sudah diproses, tidak bisa diedit'}), 409

                # Bangun data gabungan (existing + perubahan) lalu validasi ulang
                candidate = {k: (row[k] or '') for k in
                             ('nasabah_name', 'nasabah_phone', 'alamat', 'sesi',
                              'appointment_date', 'notes', 'marketing_member')}
                for field in ('nasabah_name', 'nasabah_phone', 'alamat', 'sesi',
                              'appointment_date', 'notes', 'marketing_member'):
                    if field in data:
                        candidate[field] = str(data[field]).strip()
                valid, errs, norm = validate_appointment_input(candidate)
                if not valid:
                    cursor.close(); conn.close()
                    msg = '; '.join(f'{k}: {v}' for k, v in errs.items())
                    return jsonify({'status': 'error', 'msg': msg}), 400

                fields = []
                params = []
                for field in ('nasabah_name', 'nasabah_phone', 'alamat', 'sesi',
                              'appointment_date', 'notes', 'marketing_member'):
                    if field in data:
                        fields.append(f"{field} = %s")
                        params.append(norm[field])
                if 'marketing_member' in data:
                    register_marketing_member(row['team_name'] or '', norm['marketing_member'])
                if 'alamat' in data:
                    fields.append("area = %s")
                    params.append(detect_area(norm['alamat']))
                if not fields:
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Tidak ada field yang diubah'}), 400
                params.append(appt_id)
                cursor.execute(
                    "UPDATE appointments SET " + ", ".join(fields) + ", updated_at=NOW() WHERE id=%s",
                    params)
                conn.commit()
                cursor.close(); conn.close()
                log_activity_async(appt_id, 'appointment_edit', 'marketing', user['full_name'],
                                   new_data={'fields': list(data.keys())}, ip=request.remote_addr)
                return jsonify({'status': 'success', 'msg': 'Appointment diperbarui'})
            else:
                # Chief driver / GA / Admin: boleh update catatan driver,
                # override area secara manual (perbaikan zona dari sistem), dan
                # mengisi/mengubah hasil kunjungan (mis. appointment selesai lewat
                # log perjalanan yang belum punya hasil konversi).
                updates = []
                params = []
                area_changed = None
                audit_action = 'appointment_edit'
                audit_data = {}
                if 'driver_note' in data:
                    updates.append("driver_note=%s")
                    params.append(str(data['driver_note']).strip()[:255])
                if 'area' in data:
                    area_changed = str(data['area']).strip()[:100]
                    if not area_changed:
                        cursor.close(); conn.close()
                        return jsonify({'status': 'error', 'msg': 'Area tidak boleh kosong'}), 400
                    updates.append("area=%s")
                    params.append(area_changed)
                    audit_action = 'appointment_area_edit'
                    audit_data['area'] = area_changed
                if 'visit_result' in data:
                    vr = str(data.get('visit_result') or '').strip().lower()
                    if vr and vr not in VISIT_RESULTS:
                        cursor.close(); conn.close()
                        return jsonify({'status': 'error', 'msg': 'Hasil kunjungan tidak valid'}), 400
                    updates.append("visit_result=%s")
                    params.append(vr or None)
                    audit_action = 'appointment_result_edit'
                    audit_data['visit_result'] = vr or ''
                if 'visit_note' in data:
                    updates.append("visit_note=%s")
                    params.append(str(data['visit_note']).strip()[:255])
                    audit_action = 'appointment_result_edit'
                    audit_data['visit_note'] = str(data['visit_note']).strip()[:255]
                if not updates:
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Tidak ada field yang diubah'}), 400
                params.append(appt_id)
                cursor.execute(
                    "UPDATE appointments SET " + ", ".join(updates) + ", updated_at=NOW() WHERE id=%s",
                    params)
                conn.commit()
                user = _current_user()
                log_activity_async(appt_id, audit_action, user['role'],
                                   user['full_name'], new_data=audit_data,
                                   ip=request.remote_addr)
                cursor.close(); conn.close()
                if area_changed:
                    emit_event('appointment_update',
                               {'action': 'area_changed', 'id': appt_id, 'area': area_changed,
                                'date': str(row['appointment_date'])},
                               room='appointments_board')
                if 'visit_result' in data or 'visit_note' in data:
                    emit_event('appointment_update',
                               {'action': 'result_changed', 'id': appt_id,
                                'display_id': row['display_id'],
                                'date': str(row['appointment_date'])},
                               room='appointments_board')
                return jsonify({'status': 'success', 'msg': 'Appointment diperbarui'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # ASSIGN DRIVER (chief driver)
    # ================================================================
    @app.route('/api/appointments/<int:appt_id>/assign', methods=['POST'])
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_assign_appointment(appt_id):
        try:
            data = request.get_json(silent=True) or {}
            driver_name = str(data.get('driver_name', '') or '').strip().upper()
            driver_note = str(data.get('driver_note', '') or '').strip()[:255]
            if not driver_name:
                return jsonify({'status': 'error', 'msg': 'Pilih driver terlebih dahulu'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name FROM drivers WHERE name=%s AND is_active=TRUE", (driver_name,))
            if not cursor.fetchone():
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': f'Driver {driver_name} tidak aktif/terdaftar'}), 400
            cursor.execute(
                "SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404
            if row['status'] not in ('scheduled', 'assigned'):
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment sudah selesai/dibatalkan'}), 409

            cursor.execute(
                "UPDATE appointments SET driver_name=%s, driver_note=%s, status='assigned', updated_at=NOW() WHERE id=%s",
                (driver_name, driver_note, appt_id))
            conn.commit()
            user = _current_user()
            log_activity_async(appt_id, 'appointment_assign', 'chief_driver', user['full_name'],
                               new_data={'driver': driver_name}, ip=request.remote_addr)
            cursor.close(); conn.close()

            # Realtime: board chief driver + notifikasi marketing + notifikasi driver
            emit_event('appointment_update',
                       {'action': 'assigned', 'id': appt_id, 'display_id': row['display_id'],
                        'driver': driver_name, 'date': str(row['appointment_date'])},
                       room='appointments_board')
            from modules.notifications import push_marketing_notification, push_driver_notification
            push_marketing_notification(
                row['marketing_username'], 'appointment', 'assigned',
                f'Driver {driver_name} ditugaskan ke appointment {row["display_id"]} '
                f'({row["nasabah_name"]})', row['display_id'])
            sesi_label = 'Sesi 1 (08.30)' if row['sesi'] == '1' else 'Sesi 2 (14.30)'
            push_driver_notification(
                driver_name, 'appointment', 'assigned',
                f'📅 Appointment baru ditugaskan: {row["nasabah_name"]} ({row["display_id"]}) '
                f'— {sesi_label}',
                row['display_id'])

            return jsonify({'status': 'success',
                            'msg': f'Driver {driver_name} ditugaskan ke {row["display_id"]}'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # UNASSIGN DRIVER (chief driver)
    # ================================================================
    @app.route('/api/appointments/<int:appt_id>/unassign', methods=['POST'])
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_unassign_appointment(appt_id):
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404
            if row['status'] != 'assigned':
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak dalam status ditugaskan'}), 409
            cursor.execute(
                "UPDATE appointments SET driver_name=NULL, driver_note='', status='scheduled', updated_at=NOW() WHERE id=%s",
                (appt_id,))
            conn.commit()
            user = _current_user()
            log_activity_async(appt_id, 'appointment_unassign', 'chief_driver', user['full_name'],
                               new_data={'driver_old': row['driver_name']}, ip=request.remote_addr)
            cursor.close(); conn.close()
            emit_event('appointment_update',
                       {'action': 'unassigned', 'id': appt_id, 'display_id': row['display_id'],
                        'date': str(row['appointment_date'])},
                       room='appointments_board')
            from modules.notifications import push_marketing_notification, push_driver_notification
            push_marketing_notification(
                row['marketing_username'], 'appointment', 'unassigned',
                f'Penugasan driver appointment {row["display_id"]} dibatalkan, menunggu driver baru',
                row['display_id'])
            if row['driver_name']:
                push_driver_notification(
                    row['driver_name'], 'appointment', 'unassigned',
                    f'Penugasan appointment {row["display_id"]} dibatalkan',
                    row['display_id'])
            return jsonify({'status': 'success', 'msg': 'Penugasan driver dibatalkan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # COMPLETE (chief driver) -> terintegrasi ke Log Perjalanan driver
    # ================================================================
    @app.route('/api/appointments/<int:appt_id>/complete', methods=['POST'])
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_complete_appointment(appt_id):
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404
            if row['status'] != 'assigned':
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Hanya appointment yang ditugaskan yang bisa diselesaikan'}), 409
            user = _current_user()
            # Hasil kunjungan opsional dari Chief Driver (jika driver belum mencatat)
            data = request.get_json(silent=True) or {}
            visit_result = str(data.get('result', '') or '').strip().lower()
            if visit_result and visit_result not in VISIT_RESULTS:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Hasil kunjungan tidak valid'}), 400
            visit_note = str(data.get('note', '') or '').strip()
            cursor.close(); conn.close()
            _finalize_appointment_complete(
                appt_id, row, 'appointment_complete', user['role'], user['full_name'],
                f'Appointment {row["display_id"]} ({row["nasabah_name"]}) selesai dikunjungi'
                + (f' — {_visit_result_label(visit_result)}' if visit_result else ''),
                visit_result=visit_result or None, visit_note=visit_note)
            return jsonify({'status': 'success',
                            'msg': f'{row["display_id"]} selesai — siap diintegrasikan ke Log Perjalanan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # DRIVER CONFIRM VISIT (PWA driver tanpa session) — '🏁 Selesai Dikunjungi'
    # Konfirmasi manual dari driver tanpa harus submit log perjalanan.
    # ================================================================
    @app.route('/api/appointments/driver-complete/<int:appt_id>', methods=['POST'])
    def api_driver_complete_appointment(appt_id):
        try:
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ?driver= ditutup)
            driver = resolve_driver_scope(request.form.get('driver') or request.args.get('driver') or '')
            if driver is None:
                return jsonify({'status': 'error', 'msg': 'Login driver wajib'}), 401
            if not driver:
                return jsonify({'status': 'error', 'msg': 'Parameter driver wajib'}), 400
            # Hasil kunjungan: ditemui / prospek / gagal (+ alasan opsional)
            visit_result = (request.form.get('result') or request.args.get('result') or '').strip().lower()
            if visit_result and visit_result not in VISIT_RESULTS:
                return jsonify({'status': 'error', 'msg': 'Hasil kunjungan tidak valid'}), 400
            visit_note = (request.form.get('note') or request.args.get('note') or '').strip()

            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404
            if row['status'] != 'assigned':
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment belum ditugaskan ke Anda atau sudah selesai'}), 409
            if (row['driver_name'] or '').upper() != driver:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment ini bukan milik Anda'}), 403

            cursor.close(); conn.close()
            _finalize_appointment_complete(
                appt_id, row, 'appointment_driver_complete', 'driver', driver,
                f'Driver {driver} selesai mengunjungi {row["nasabah_name"]} '
                f'({row["display_id"]})'
                + (f' — {_visit_result_label(visit_result)}' if visit_result else ''),
                driver_for_event=driver,
                visit_result=visit_result or None, visit_note=visit_note)
            return jsonify({'status': 'success',
                            'msg': f'{row["display_id"]} ditandai selesai dikunjungi'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # CANCEL
    # ================================================================
    @app.route('/api/appointments/<int:appt_id>/cancel', methods=['POST'])
    @role_required(['marketing', 'chief_driver', 'ga', 'admin'])
    def api_cancel_appointment(appt_id):
        try:
            data = request.get_json(silent=True) or {}
            reason = str(data.get('reason', '') or '').strip()[:200]
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appt_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Appointment tidak ditemukan'}), 404
            user = _current_user()
            if user['role'] == 'marketing':
                if row['marketing_username'] != user['username']:
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Bukan appointment Anda'}), 403
                if row['status'] not in ('scheduled',):
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Appointment sudah diproses, tidak bisa dibatalkan'}), 409
            else:
                if row['status'] in ('completed', 'cancelled'):
                    cursor.close(); conn.close()
                    return jsonify({'status': 'error', 'msg': 'Appointment sudah final'}), 409
            cursor.execute(
                "UPDATE appointments SET status='cancelled', updated_at=NOW() WHERE id=%s",
                (appt_id,))
            conn.commit()
            log_activity_async(appt_id, 'appointment_cancel', user['role'], user['full_name'],
                               new_data={'reason': reason}, ip=request.remote_addr)
            cursor.close(); conn.close()
            emit_event('appointment_update',
                       {'action': 'cancelled', 'id': appt_id, 'display_id': row['display_id'],
                        'date': str(row['appointment_date'])},
                       room='appointments_board')
            return jsonify({'status': 'success', 'msg': 'Appointment dibatalkan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # COMPLETED APPOINTMENTS UNTUK DRIVER (PWA Trip Form)
    # Public GET: dipakai halaman driver tanpa session.
    # ================================================================
    @app.route('/api/appointments/completed')
    def api_completed_appointments():
        try:
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ditutup)
            driver = resolve_driver_scope(request.args.get('driver', ''))
            if driver is None:
                return jsonify({'error': 'Login driver wajib'}), 401
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            if not driver:
                return jsonify({'error': 'Parameter driver wajib'}), 400
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            # Hanya field yang dibutuhkan form trip PWA (tanpa no. HP nasabah
            # yang bersifat sensitif — endpoint ini publik tanpa session).
            cursor.execute(
                """SELECT id, display_id, nasabah_name, alamat, area,
                          sesi, appointment_date, driver_name
                   FROM appointments
                   WHERE driver_name=%s AND appointment_date=%s AND status='completed'
                   ORDER BY sesi ASC, completed_at ASC""",
                (driver, target_date))
            rows = [_clean(r) for r in cursor.fetchall()]
            cursor.close(); conn.close()
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/appointments/driver-today')
    def api_driver_today_appointments():
        """Appointment hari ini milik satu driver (status assigned + completed).

        Dipakai PWA driver sebagai 'Jadwal Appointment Saya': driver perlu melihat
        data kunjungan (nama, alamat, no. HP) SEBELUM berangkat — bukan hanya
        setelah ditandai selesai. Endpoint publik seperti /completed (driver PWA
        tanpa session), scope dibatasi ke driver_name sendiri.
        Trade-off privasi: no. HP nasabah ikut dikembalikan karena dibutuhkan driver
        untuk menghubungi nasabah — konsisten dengan model akses PWA tanpa login.
        v2.4: sesi driver login dipaksa memakai identitas sendiri (anti IDOR).
        """
        try:
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ?driver= ditutup)
            driver = resolve_driver_scope(request.args.get('driver', ''))
            if driver is None:
                return jsonify({'error': 'Login driver wajib'}), 401
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            if not driver:
                return jsonify({'error': 'Parameter driver wajib'}), 400
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, display_id, nasabah_name, nasabah_phone, alamat, area,
                          sesi, appointment_date, status, driver_name, marketing_member,
                          visit_result, visit_note
                   FROM appointments
                   WHERE driver_name=%s AND appointment_date=%s
                     AND status IN ('assigned','completed')
                   ORDER BY sesi ASC, created_at ASC""",
                (driver, target_date))
            rows = [_clean(r) for r in cursor.fetchall()]
            cursor.close(); conn.close()
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/appointments/driver-summary')
    def api_driver_appointment_summary():
        """Ringkasan appointment untuk satu driver+date (dipakai PWA driver)."""
        try:
            # v2.5: tanpa sesi sama sekali → ditolak (jalur legacy ditutup)
            driver = resolve_driver_scope(request.args.get('driver', ''))
            if driver is None:
                return jsonify({'error': 'Login driver wajib'}), 401
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            if driver:
                cursor.execute(
                    """SELECT status, COUNT(*) c FROM appointments
                       WHERE driver_name=%s AND appointment_date=%s GROUP BY status""",
                    (driver, target_date))
            else:
                cursor.execute(
                    """SELECT status, COUNT(*) c FROM appointments
                       WHERE appointment_date=%s GROUP BY status""",
                    (target_date,))
            summary = {'total': 0, 'assigned': 0, 'completed': 0}
            for r in cursor.fetchall():
                summary['total'] += r['c']
                if r['status'] in summary:
                    summary[r['status']] += r['c']
            cursor.close(); conn.close()
            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # MEMBER SUMMARY (ringkasan per marketing anggota untuk board chief driver)
    # ================================================================
    @app.route('/api/appointments/member-summary')
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_member_summary():
        try:
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT marketing_member,
                          COUNT(*) AS total,
                          SUM(status='scheduled') AS scheduled,
                          SUM(status='assigned') AS assigned,
                          SUM(status='completed') AS completed,
                          SUM(status='cancelled') AS cancelled,
                          SUM(visit_result='ditemui') AS ditemui,
                          SUM(visit_result='prospek') AS prospek,
                          SUM(visit_result='gagal') AS gagal,
                          SUM(sesi='1') AS sesi1,
                          SUM(sesi='2') AS sesi2
                   FROM appointments
                   WHERE appointment_date=%s AND marketing_member<>''
                   GROUP BY marketing_member
                   ORDER BY total DESC, marketing_member ASC""",
                (target_date,))
            rows = []
            for r in cursor.fetchall():
                row = {'marketing_member': r['marketing_member']}
                for k in ('total', 'scheduled', 'assigned', 'completed', 'cancelled',
                          'ditemui', 'prospek', 'gagal', 'sesi1', 'sesi2'):
                    row[k] = int(r.get(k) or 0)
                rows.append(row)
            cursor.close(); conn.close()
            return jsonify({'date': target_date, 'members': rows})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # DETECT AREA (preview alamat -> zona)
    # ================================================================
    @app.route('/api/appointments/detect-area')
    def api_detect_area():
        alamat = request.args.get('alamat', '').strip()
        return jsonify({'area': detect_area(alamat)})

    # ================================================================
    # EXPORT EXCEL HARIAN (chief driver)
    # ================================================================
    @app.route('/api/appointments/export')
    @role_required(['chief_driver', 'ga', 'admin'])
    def api_export_appointments():
        try:
            target_date = request.args.get('date', '').strip() or date.today().isoformat()
            member = request.args.get('member', '').strip()
            conn = get_db_connection()
            if not conn:
                return "DB error", 500
            cursor = conn.cursor(dictionary=True)
            where = "appointment_date=%s"
            params = [target_date]
            if member:
                where += " AND marketing_member LIKE %s"
                params.append(f"%{member}%")
            cursor.execute(
                "SELECT * FROM appointments WHERE " + where + " ORDER BY sesi ASC, created_at ASC",
                params)
            rows = [_clean(r) for r in cursor.fetchall()]
            cursor.close(); conn.close()

            from modules.excel_generator import generate_appointment_report
            excel_bytes = generate_appointment_report(target_date, rows)
            response = make_response(excel_bytes)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = \
                f'attachment; filename=Appointment_{target_date}.xlsx'
            return response
        except Exception as e:
            return f"Error: {str(e)}", 500

    # ================================================================
    # NOTIFIKASI MARKETING (bell di halaman marketing)
    # ================================================================
    @app.route('/api/appointments/notifications')
    @role_required(['marketing'])
    def api_marketing_notifications():
        try:
            username = session.get('user_name', '').lower()
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, type, action, message, ref_id, is_read, created_at "
                "FROM notifications WHERE driver_name=%s ORDER BY id DESC LIMIT 50",
                (username,))
            rows = cursor.fetchall()
            cursor.close(); conn.close()
            for r in rows:
                r['created_at'] = str(r['created_at'])
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/appointments/notifications/read', methods=['POST'])
    @role_required(['marketing'])
    def api_marketing_notifications_read():
        try:
            username = session.get('user_name', '').lower()
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notifications SET is_read=1 WHERE driver_name=%s AND is_read=0",
                (username,))
            conn.commit()
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': 'Notifikasi dibaca'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # MARKETING MEMBERS (anggota tim yang memprospek)
    # ================================================================
    @app.route('/api/marketing/members')
    @role_required(['marketing', 'chief_driver', 'ga', 'admin'])
    def api_marketing_members():
        try:
            team = request.args.get('team', '').strip()
            if not team:
                if session.get('user_role') == 'marketing':
                    # Marketing: hanya anggota timnya sendiri (untuk saran input)
                    team = _user_team_name(session.get('user_name'))
                    members = get_team_members(team)
                else:
                    # Chief driver / GA / Admin: semua anggota lintas tim (untuk filter board)
                    conn = get_db_connection()
                    if not conn:
                        return jsonify({'error': 'DB error'}), 500
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT DISTINCT member_name FROM marketing_members "
                        "WHERE is_active=1 AND member_name<>'' ORDER BY member_name")
                    members = [r['member_name'] for r in cursor.fetchall()]
                    cursor.close(); conn.close()
            else:
                members = get_team_members(team)
            return jsonify({'members': members})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # MARKETING TEAMS
    # ================================================================
    @app.route('/api/teams')
    @role_required(['admin', 'ga', 'chief_driver'])
    def api_teams():
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT name, leader_name, is_active FROM marketing_teams ORDER BY name")
            rows = cursor.fetchall()
            cursor.close(); conn.close()
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/teams/sync', methods=['POST'])
    @role_required(['admin'])
    def api_team_sync():
        try:
            data = request.get_json(silent=True) or {}
            name = str(data.get('name', '') or '').strip()
            leader = str(data.get('leader_name', '') or '').strip()
            if not name:
                return jsonify({'status': 'error', 'msg': 'Nama tim wajib'}), 400
            get_or_create_team(name, leader)
            log_activity_async(0, 'team_sync', 'admin', 'Admin',
                               new_data={'team': name, 'leader': leader}, ip=request.remote_addr)
            return jsonify({'status': 'success', 'msg': f'Tim {name} disimpan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
