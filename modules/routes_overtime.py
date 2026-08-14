"""Sistem Overtime (v2.22) — GA HR.

Dua modul overtime:
1. **Overtime DRIVER** — data berasal dari Google Sheet read-only (diisi Google
   Form lama). GA HR menekan tombol "Refresh" → server mengambil CSV/JSON dari
   URL sumber (system_config.overtime_driver_sheet_url) lalu upsert ke tabel
   `overtime_driver`. URL default = CSV export sheet (publik). Bila sheet
   private, GA HR mengganti URL dengan Google Apps Script Web App (jalankan
   sebagai pemilik akun → sheet tetap private, hasil JSON terbaca publik).
2. **Overtime OB & SECURITY** — data dimigrasi penuh dari sheet lama (546 baris)
   + form publik baru (tanpa login) dengan dropdown Posisi & Nama.

Role: `ga_hr` (halaman sendiri) & `admin`.
"""
import csv
import io
import time
import hashlib
import requests
from datetime import datetime, date

from flask import request, jsonify, make_response
from modules.config import get_db_connection
from modules.helpers import (role_required, log_activity_async,
                             generate_display_id)
from modules.overtime_helpers import (clean, map_headers, parse_date_mdy,
                                      parse_time_12h, parse_submitted_at,
                                      normalize_name, guess_position)
from modules.pdf_generator import OvertimeReportPDF

POSITIONS = ('OB', 'Security')

# Rate limit form publik: maks 10 submit / 10 menit per IP (anti spam).
_SUBMIT_MAX = 10
_SUBMIT_WINDOW = 600
_submit_log = {}


def _serialize(row):
    row = dict(row)
    for k, v in row.items():
        if isinstance(v, datetime):
            row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(v, date):
            row[k] = v.isoformat()
    return row


def _rate_ok(ip):
    now = time.time()
    ts = [t for t in _submit_log.get(ip, []) if now - t < _SUBMIT_WINDOW]
    if len(ts) >= _SUBMIT_MAX:
        _submit_log[ip] = ts
        return False
    ts.append(now)
    _submit_log[ip] = ts
    return True


def _current_user():
    return {
        'username': session_user('user_name', ''),
        'full_name': session_user('full_name', session_user('user_name', '')),
        'role': session_user('user_role', ''),
    }


def session_user(key, default=None):
    try:
        from flask import session
        return session.get(key, default)
    except Exception:
        return default


def _parse_date_filter(value, label):
    """YYYY-MM-DD -> date atau ValueError."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f'{label} harus format YYYY-MM-DD')


def _get_sheet_url(conn):
    """URL sumber sheet Driver dari system_config (dengan default)."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT config_value FROM system_config "
                   "WHERE config_key='overtime_driver_sheet_url'")
    row = cursor.fetchone()
    cursor.close()
    return (row['config_value'] if row and row.get('config_value') else '').strip()


def _set_refresh_meta(conn, summary):
    """Catat metadata refresh terakhir (waktu + ringkasan)."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO system_config (config_key, config_value) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE config_value=VALUES(config_value)",
        ('overtime_driver_last_refresh',
         f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {summary}"))
    conn.commit()
    cursor.close()


def _fetch_sheet_rows(url):
    """Ambil baris data dari URL sumber. Support CSV (export/gviz) & JSON
    (Google Apps Script Web App: {"rows": [{...}]}). Return list[dict]."""
    resp = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    resp.raise_for_status()
    text = resp.content.decode('utf-8-sig', errors='replace')
    stripped = text.lstrip()
    if stripped.startswith('{'):
        data = resp.json()
        rows = data.get('rows') or []
        if not rows:
            return []
        return [{str(k): (v if v is not None else '') for k, v in r.items()} for r in rows]
    # CSV
    reader = csv.DictReader(io.StringIO(text))
    return [{k: (v if v is not None else '') for k, v in r.items()} for r in reader]


def _upsert_driver_rows(conn, rows):
    """Upsert baris sheet ke overtime_driver (kunci: sheet_row = baris sheet)."""
    cursor = conn.cursor(dictionary=True)
    added = updated = skipped = 0
    if rows:
        headers = list(rows[0].keys())
        idx = map_headers(headers)
        for n, r in enumerate(rows):
            sheet_row = n + 2  # baris 1 = header di spreadsheet
            def g(field):
                i = idx.get(field)
                return clean(r[headers[i]]) if i is not None and i < len(headers) else ''
            nama = g('nama')
            if not nama:
                skipped += 1
                continue
            tanggal = parse_date_mdy(g('tanggal')) or (g('tanggal') or '')[:10]
            cursor.execute(
                """INSERT INTO overtime_driver
                   (sheet_row, submitted_at, email, nama, tanggal, waktu_mulai,
                    waktu_selesai, keterangan, foto_mulai, foto_selesai, notes)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE
                     submitted_at=VALUES(submitted_at), email=VALUES(email),
                     nama=VALUES(nama), tanggal=VALUES(tanggal),
                     waktu_mulai=VALUES(waktu_mulai), waktu_selesai=VALUES(waktu_selesai),
                     keterangan=VALUES(keterangan), foto_mulai=VALUES(foto_mulai),
                     foto_selesai=VALUES(foto_selesai), notes=VALUES(notes)""",
                (sheet_row,
                 parse_submitted_at(g('submitted_at')) or None,
                 g('email')[:150], nama[:150], tanggal or None,
                 (parse_time_12h(g('waktu_mulai')) or g('waktu_mulai'))[:20],
                 (parse_time_12h(g('waktu_selesai')) or g('waktu_selesai'))[:20],
                 g('keterangan')[:500], g('foto_mulai')[:600],
                 g('foto_selesai')[:600], g('notes')[:500]))
            # rowcount: 1 = insert baru, 2 = update baris lama (MySQL)
            if cursor.rowcount == 1:
                added += 1
            elif cursor.rowcount == 2:
                updated += 1
            else:
                skipped += 1
    conn.commit()
    cursor.close()
    return {'added': added, 'updated': updated, 'skipped': skipped, 'total_rows': len(rows)}


def register_overtime_routes(app):

    # ================================================================
    # FORM PUBLIK OB/SECURITY — meta (dropdown) & submit (tanpa login)
    # ================================================================
    @app.route('/api/overtime/form-meta')
    def api_overtime_form_meta():
        """Dropdown Posisi + Nama (dari data yang ada) + keterangan umum."""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT DISTINCT nama FROM overtime_ob_security "
                "WHERE nama<>'' ORDER BY nama")
            names = [r['nama'] for r in cursor.fetchall()]
            cursor.execute(
                "SELECT DISTINCT keterangan FROM overtime_ob_security "
                "WHERE keterangan<>'' ORDER BY keterangan LIMIT 100")
            keterangan = [r['keterangan'] for r in cursor.fetchall()]
            cursor.close(); conn.close()
            return jsonify({
                'positions': list(POSITIONS),
                'names': names,
                'keterangan': keterangan,
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/overtime', methods=['POST'])
    def api_overtime_submit():
        """Submit overtime OB/Security dari form publik (tanpa login)."""
        try:
            ip = request.remote_addr or '?'
            if not _rate_ok(ip):
                return jsonify({'status': 'error',
                                'msg': 'Terlalu banyak pengiriman dari perangkat ini. '
                                       'Coba lagi beberapa saat.'}), 429
            data = request.get_json(silent=True) or {}
            nama = clean(data.get('nama'))
            posisi = clean(data.get('posisi'))
            tanggal = clean(data.get('tanggal'))
            waktu_mulai = clean(data.get('waktu_mulai'))
            waktu_selesai = clean(data.get('waktu_selesai'))
            keterangan = clean(data.get('keterangan'))[:500]
            email = clean(data.get('email'))[:150]

            if not nama:
                return jsonify({'status': 'error', 'msg': 'Nama wajib diisi'}), 400
            if posisi not in POSITIONS:
                return jsonify({'status': 'error',
                                'msg': 'Posisi wajib dipilih (OB atau Security)'}), 400
            if not tanggal:
                return jsonify({'status': 'error', 'msg': 'Tanggal overtime wajib diisi'}), 400
            tanggal_iso = parse_date_mdy(tanggal) or tanggal
            if len(tanggal_iso) != 10:
                return jsonify({'status': 'error',
                                'msg': 'Tanggal harus format DD/MM/YYYY atau YYYY-MM-DD'}), 400
            if not waktu_mulai:
                return jsonify({'status': 'error', 'msg': 'Waktu mulai wajib diisi'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            display_id = generate_display_id('OTL', conn)
            source_uid = 'form-' + hashlib.md5(
                (display_id + nama + posisi).encode('utf-8')).hexdigest()[:24]
            cursor.execute(
                """INSERT INTO overtime_ob_security
                   (display_id, nama, posisi, tanggal, waktu_mulai, waktu_selesai,
                    keterangan, email, source, source_uid)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'form',%s)""",
                (display_id, nama, posisi, tanggal_iso,
                 (parse_time_12h(waktu_mulai) or waktu_mulai)[:20],
                 (parse_time_12h(waktu_selesai) or waktu_selesai or '')[:20],
                 keterangan, email, source_uid))
            conn.commit()
            log_activity_async(None, 'overtime_submit', 'public', nama,
                               new_data={'display_id': display_id, 'posisi': posisi},
                               ip=ip)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'display_id': display_id,
                            'msg': f'Overtime {posisi} tercatat! No. {display_id}'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # GA HR — daftar overtime DRIVER (hasil sinkronisasi sheet)
    # ================================================================
    @app.route('/api/overtime/driver')
    @role_required(['ga_hr', 'admin'])
    def api_overtime_driver_list():
        try:
            d_from = _parse_date_filter(request.args.get('date_from'), 'Tanggal dari')
            d_to = _parse_date_filter(request.args.get('date_to'), 'Tanggal sampai')
            search = clean(request.args.get('search'))
            nama = clean(request.args.get('nama'))
            where, params = [], []
            if d_from:
                where.append('tanggal >= %s'); params.append(d_from.isoformat())
            if d_to:
                where.append('tanggal <= %s'); params.append(d_to.isoformat())
            if search:
                like = f'%{search}%'
                where.append('(nama LIKE %s OR keterangan LIKE %s OR email LIKE %s)')
                params += [like] * 3
            if nama:
                where.append('nama LIKE %s'); params.append(f'%{nama}%')

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM overtime_driver"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY tanggal DESC, id DESC LIMIT 2000"
            cursor.execute(sql, params)
            rows = [_serialize(r) for r in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) c FROM overtime_driver")
            total = cursor.fetchone()['c']
            cursor.close(); conn.close()
            return jsonify({'data': rows, 'total': total})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # GA HR — refresh sinkronisasi sheet DRIVER
    # ================================================================
    @app.route('/api/overtime/driver/refresh', methods=['POST'])
    @role_required(['ga_hr', 'admin'])
    def api_overtime_driver_refresh():
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            url = _get_sheet_url(conn)
            if not url:
                cursor = conn.cursor(); cursor.close(); conn.close()
                return jsonify({'status': 'error',
                                'msg': 'URL sumber sheet belum diatur. Set di Pengaturan Sumber Data.'}), 400
            try:
                rows = _fetch_sheet_rows(url)
            except Exception as fe:
                cursor = conn.cursor(); cursor.close(); conn.close()
                return jsonify({
                    'status': 'error',
                    'msg': 'Gagal mengambil data dari Google Sheet. '
                           'Pastikan sheet di-share "Anyone with the link" ATAU '
                           'URL memakai Google Apps Script Web App (lihat petunjuk).',
                    'detail': str(fe)[:300],
                }), 502
            result = _upsert_driver_rows(conn, rows)
            summary = (f"{result['added']} baru, {result['updated']} diperbarui, "
                       f"{result['skipped']} dilewati (dari {result['total_rows']} baris)")
            _set_refresh_meta(conn, summary)
            user = _current_user()
            log_activity_async(None, 'overtime_driver_refresh', user['role'],
                               user['full_name'], new_data=result, ip=request.remote_addr)
            conn.close()
            return jsonify({'status': 'success', **result, 'summary': summary})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ================================================================
    # GA HR — daftar overtime OB/SECURITY (migrasi + form publik)
    # ================================================================
    @app.route('/api/overtime/ob-security')
    @role_required(['ga_hr', 'admin'])
    def api_overtime_ob_list():
        try:
            d_from = _parse_date_filter(request.args.get('date_from'), 'Tanggal dari')
            d_to = _parse_date_filter(request.args.get('date_to'), 'Tanggal sampai')
            search = clean(request.args.get('search'))
            posisi = clean(request.args.get('posisi'))
            nama = clean(request.args.get('nama'))
            where, params = [], []
            if d_from:
                where.append('tanggal >= %s'); params.append(d_from.isoformat())
            if d_to:
                where.append('tanggal <= %s'); params.append(d_to.isoformat())
            if search:
                like = f'%{search}%'
                where.append('(nama LIKE %s OR keterangan LIKE %s OR display_id LIKE %s)')
                params += [like] * 3
            if posisi in POSITIONS:
                where.append('posisi = %s'); params.append(posisi)
            if nama:
                where.append('nama LIKE %s'); params.append(f'%{nama}%')

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM overtime_ob_security"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY tanggal DESC, id DESC LIMIT 2000"
            cursor.execute(sql, params)
            rows = [_serialize(r) for r in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) c FROM overtime_ob_security")
            total = cursor.fetchone()['c']
            cursor.close(); conn.close()
            return jsonify({'data': rows, 'total': total})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # GA HR — laporan PDF resmi (Driver / OB-Security) + TTD GA HR
    # ================================================================
    @app.route('/api/overtime/report')
    @role_required(['ga_hr', 'admin'])
    def api_overtime_report():
        try:
            modul = str(request.args.get('modul', 'driver') or '').strip()
            if modul not in ('driver', 'ob'):
                return jsonify({'error': 'Modul harus driver atau ob'}), 400
            d_from = _parse_date_filter(request.args.get('date_from'), 'Tanggal dari')
            d_to = _parse_date_filter(request.args.get('date_to'), 'Tanggal sampai')
            if not d_to and d_from:
                d_to = d_from
            posisi = clean(request.args.get('posisi'))
            nama = clean(request.args.get('nama'))

            table = 'overtime_driver' if modul == 'driver' else 'overtime_ob_security'
            where, params = [], []
            if d_from:
                where.append('tanggal >= %s'); params.append(d_from.isoformat())
            if d_to:
                where.append('tanggal <= %s'); params.append(d_to.isoformat())
            if posisi in POSITIONS:
                where.append('posisi = %s'); params.append(posisi)
            if nama:
                where.append('nama LIKE %s'); params.append(f'%{nama}%')

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            sql = f'SELECT * FROM {table}'
            if where:
                sql += ' WHERE ' + ' AND '.join(where)
            sql += ' ORDER BY tanggal DESC, id DESC LIMIT 3000'
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close(); conn.close()

            date_label = f'{d_from or d_to} s/d {d_to}' if d_from else str(d_to or 'semua')
            filters = {}
            if posisi:
                filters['Posisi'] = posisi
            if nama:
                filters['Nama'] = nama
            user_info = _current_user()
            pdf = OvertimeReportPDF()
            pdf.generate(rows, modul=modul, date_label=date_label,
                         filters=filters, generated_by=user_info['full_name'])
            buf = io.BytesIO()
            pdf.output(buf)
            buf.seek(0)
            fname = f'Laporan_Overtime_{modul}_{(d_to or date.today()).isoformat()}.pdf'
            response = make_response(buf.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={fname}'
            return response
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # GA HR — ringkasan statistik kedua modul
    # ================================================================
    @app.route('/api/overtime/stats')
    @role_required(['ga_hr', 'admin'])
    def api_overtime_stats():
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) c FROM overtime_driver")
            driver_total = cursor.fetchone()['c']
            cursor.execute("SELECT posisi, COUNT(*) c FROM overtime_ob_security GROUP BY posisi")
            by_pos = {r['posisi']: r['c'] for r in cursor.fetchall()}
            cursor.execute("SELECT COUNT(*) c FROM overtime_ob_security")
            ob_total = cursor.fetchone()['c']
            cursor.execute("SELECT config_value FROM system_config "
                           "WHERE config_key='overtime_driver_last_refresh'")
            lr = cursor.fetchone()
            cursor.close(); conn.close()
            return jsonify({
                'driver': {'total': driver_total,
                           'last_refresh': (lr['config_value'] if lr else 'Belum pernah refresh')},
                'ob_security': {'total': ob_total, 'by_position': by_pos},
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ================================================================
    # GA HR — konfigurasi sumber data sheet Driver
    # ================================================================
    @app.route('/api/overtime/config')
    @role_required(['ga_hr', 'admin'])
    def api_overtime_config_get():
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT config_key, config_value FROM system_config "
                           "WHERE config_key LIKE 'overtime_driver_%'")
            cfg = {r['config_key']: r['config_value'] for r in cursor.fetchall()}
            cursor.close(); conn.close()
            return jsonify({
                'sheet_url': cfg.get('overtime_driver_sheet_url', ''),
                'last_refresh': cfg.get('overtime_driver_last_refresh', 'Belum pernah refresh'),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/overtime/config', methods=['PATCH'])
    @role_required(['ga_hr', 'admin'])
    def api_overtime_config_set():
        try:
            data = request.get_json(silent=True) or {}
            url = clean(data.get('sheet_url'))
            if not url:
                return jsonify({'status': 'error', 'msg': 'URL tidak boleh kosong'}), 400
            if not url.startswith('http://') and not url.startswith('https://'):
                return jsonify({'status': 'error', 'msg': 'URL harus diawali http(s)://'}), 400
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO system_config (config_key, config_value) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE config_value=VALUES(config_value)",
                ('overtime_driver_sheet_url', url[:600]))
            conn.commit()
            user = _current_user()
            log_activity_async(None, 'overtime_config', user['role'], user['full_name'],
                               new_data={'sheet_url': url[:120]}, ip=request.remote_addr)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': 'URL sumber data diperbarui'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500
