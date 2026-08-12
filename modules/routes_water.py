"""Air Minum Routes (v2.6) — Tanda Terima Pembelian Air Minum.

Alur:
1. Finance (atau admin) menyediakan master merk per tipe (gelas/botol/galon).
2. OB mengajukan pembelian: tanggal + item (tipe, merk, satuan, kuantitas) +
   foto timestamp "sebelum diisi" & "sesudah diisi".
3. Finance memverifikasi: approve (remark + note) atau tolak (alasan).
4. Pengajuan terverifikasi -> PDF tanda terima TTD Finance (menyerahkan)
   & GA (menerima); nama TTD di-set admin via system_config.
"""
from flask import request, jsonify, make_response, session
from modules.config import get_db_connection
from modules.helpers import (role_required, log_activity_async, save_file,
                             generate_display_id, client_ip)

WATER_ROLES = ['ob', 'finance', 'admin']          # pengguna air minum
WATER_FINANCE_ROLES = ['finance', 'admin']        # kelola master + verifikasi
VALID_SATUAN = {'pcs', 'dus', 'karton', 'botol', 'gelas', 'galon', 'unit'}


def _session_name():
    return (session.get('full_name') or session.get('user_name') or '').strip()


def _get_ttd_names():
    """Nama TTD dari system_config (di-set admin di /app/settings)."""
    ga = finance = ''
    try:
        conn = get_db_connection()
        if not conn:
            return ga, finance
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT config_key, config_value FROM system_config "
                    "WHERE config_key IN ('water_ga_name','water_finance_name')")
        for row in cur.fetchall():
            if row['config_key'] == 'water_ga_name':
                ga = (row['config_value'] or '').strip()
            elif row['config_key'] == 'water_finance_name':
                finance = (row['config_value'] or '').strip()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[water] get_ttd_names: {e}")
    return ga, finance


def _purchase_row(cur, p):
    """Perkaya satu baris pengajuan dengan rincian item (list)."""
    p = dict(p)
    cur.execute("SELECT drink_type, brand, satuan, quantity "
                "FROM water_purchase_items WHERE purchase_id=%s ORDER BY id", (p['id'],))
    p['items'] = cur.fetchall()
    p['status_label'] = {'pending': 'Menunggu Verifikasi', 'verified': 'Terverifikasi',
                         'rejected': 'Ditolak'}.get(p['status'], p['status'])
    return p


def register_water_routes(app):

    # ============================================================
    # MASTER DATA — tipe & merk (dikelola Finance)
    # ============================================================
    @app.route('/api/water/brands')
    @role_required(WATER_ROLES)
    def api_water_brands():
        """Tipe + merk aktif untuk dropdown OB. Grouped per tipe."""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, name FROM water_drink_types "
                        "WHERE is_active=1 ORDER BY FIELD(name,'Gelas','Botol','Galon'), name")
            types = cur.fetchall()
            cur.execute("""SELECT b.id, b.type_id, t.name AS drink_type, b.brand
                           FROM water_drink_brands b
                           JOIN water_drink_types t ON t.id=b.type_id
                           WHERE b.is_active=1 ORDER BY t.name, b.brand""")
            brands = cur.fetchall()
            cur.close(); conn.close()
            for t in types:
                t['brands'] = [b for b in brands if b['type_id'] == t['id']]
            return jsonify({'types': types, 'brands': brands})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/water/brands', methods=['POST'])
    @role_required(WATER_FINANCE_ROLES)
    def api_water_brand_add():
        try:
            data = request.get_json(silent=True) or {}
            type_id = data.get('type_id')
            brand = str(data.get('brand', '') or '').strip()
            if not type_id or not brand:
                return jsonify({'status': 'error', 'msg': 'Tipe dan merk wajib diisi'}), 400
            if len(brand) > 100:
                return jsonify({'status': 'error', 'msg': 'Merk maksimal 100 karakter'}), 400
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cur = conn.cursor()
            cur.execute("INSERT INTO water_drink_brands (type_id, brand) VALUES (%s,%s) "
                        "ON DUPLICATE KEY UPDATE is_active=1, updated_at=NOW()",
                        (int(type_id), brand))
            new_id = cur.lastrowid  # baca SEBELUM commit (reliabel di MySQL/MariaDB)
            conn.commit()
            cur.close(); conn.close()
            log_activity_async(0, 'water_brand_add', session.get('user_role', ''),
                               _session_name() or 'Finance', new_data={'type_id': type_id, 'brand': brand},
                               ip=client_ip())
            return jsonify({'status': 'success', 'msg': f'Merk {brand} disimpan', 'id': new_id})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/water/brands/<int:brand_id>', methods=['DELETE'])
    @role_required(WATER_FINANCE_ROLES)
    def api_water_brand_delete(brand_id):
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cur = conn.cursor()
            cur.execute("UPDATE water_drink_brands SET is_active=0 WHERE id=%s", (brand_id,))
            affected = cur.rowcount
            conn.commit(); cur.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': 'Merk tidak ditemukan'}), 404
            log_activity_async(0, 'water_brand_delete', session.get('user_role', ''),
                               _session_name() or 'Finance', new_data={'brand_id': brand_id},
                               ip=client_ip())
            return jsonify({'status': 'success', 'msg': 'Merk dinonaktifkan'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ============================================================
    # PENGAJUAN — diisi OB
    # ============================================================
    @app.route('/api/water/purchases', methods=['POST'])
    @role_required(['ob', 'admin'])
    def api_water_purchase_create():
        """Buat pengajuan (multipart): tanggal, items JSON, foto before & after."""
        try:
            ob_name = _session_name() or 'OB'
            tanggal = (request.form.get('purchase_date') or '').strip()
            items_raw = request.form.get('items') or '[]'
            import json as _json
            items = _json.loads(items_raw)
            if not isinstance(items, list) or not items:
                return jsonify({'status': 'error', 'msg': 'Minimal satu item wajib diisi'}), 400
            if not tanggal:
                return jsonify({'status': 'error', 'msg': 'Tanggal pembelian wajib diisi'}), 400
            if len(items) > 20:
                return jsonify({'status': 'error', 'msg': 'Maksimal 20 item per pengajuan'}), 400
            normalized = []
            for it in items:
                tipe = str(it.get('drink_type', '') or '').strip()
                brand = str(it.get('brand', '') or '').strip()
                satuan = str(it.get('satuan', 'pcs') or 'pcs').strip().lower()
                try:
                    qty = int(it.get('quantity', 0) or 0)
                except (TypeError, ValueError):
                    return jsonify({'status': 'error', 'msg': 'Kuantitas item harus berupa angka'}), 400
                if not tipe or not brand:
                    return jsonify({'status': 'error', 'msg': 'Setiap item wajib: jenis dan merk'}), 400
                if qty <= 0 or qty > 99999:
                    return jsonify({'status': 'error', 'msg': 'Kuantitas item harus 1–99.999'}), 400
                if satuan not in VALID_SATUAN:
                    satuan = 'pcs'
                normalized.append({'drink_type': tipe, 'brand': brand, 'satuan': satuan, 'quantity': qty})

            foto_before = save_file(request.files.get('foto_before'), 'WTR_BEFORE', ob_name, app.config['UPLOAD_FOLDER'])
            foto_after = save_file(request.files.get('foto_after'), 'WTR_AFTER', ob_name, app.config['UPLOAD_FOLDER'])
            if not foto_before or not foto_after:
                return jsonify({'status': 'error', 'msg': 'Foto "sebelum diisi" dan "sesudah diisi" wajib diunggah (JPG/PNG)'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cur = conn.cursor()
            display_id = generate_display_id('WTR', conn)
            cur.execute("""INSERT INTO water_purchases
                           (display_id, ob_name, purchase_date, status, foto_before, foto_after)
                           VALUES (%s,%s,%s,'pending',%s,%s)""",
                        (display_id, ob_name, tanggal, foto_before, foto_after))
            purchase_id = cur.lastrowid
            for it in normalized:
                cur.execute("""INSERT INTO water_purchase_items
                               (purchase_id, drink_type, brand, satuan, quantity)
                               VALUES (%s,%s,%s,%s,%s)""",
                            (purchase_id, it['drink_type'], it['brand'], it['satuan'], it['quantity']))
            conn.commit(); cur.close(); conn.close()
            log_activity_async(0, 'water_purchase_create', session.get('user_role', ''),
                               ob_name, new_data={'display_id': display_id, 'items': normalized},
                               ip=client_ip())
            return jsonify({'status': 'success', 'msg': f'Pengajuan {display_id} dikirim ke Finance',
                            'display_id': display_id, 'id': purchase_id})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/water/purchases')
    @role_required(WATER_ROLES)
    def api_water_purchases():
        """Daftar pengajuan. OB: hanya miliknya; Finance/admin: semua."""
        try:
            role = session.get('user_role', '')
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cur = conn.cursor(dictionary=True)
            if role == 'ob':
                cur.execute("""SELECT * FROM water_purchases WHERE ob_name=%s
                               ORDER BY id DESC LIMIT 200""", (_session_name(),))
            else:
                cur.execute("SELECT * FROM water_purchases ORDER BY id DESC LIMIT 500")
            rows = cur.fetchall()
            # Batch load item (hindari N+1): satu query untuk semua purchase_id
            if rows:
                ids = [r['id'] for r in rows]
                fmt = ','.join(['%s'] * len(ids))
                cur.execute(
                    "SELECT purchase_id, drink_type, brand, satuan, quantity "
                    f"FROM water_purchase_items WHERE purchase_id IN ({fmt}) ORDER BY id",
                    tuple(ids))
                items_by_purchase = {}
                for it in cur.fetchall():
                    items_by_purchase.setdefault(it['purchase_id'], []).append(it)
                for r in rows:
                    r['items'] = items_by_purchase.get(r['id'], [])
                    r['status_label'] = {'pending': 'Menunggu Verifikasi',
                                         'verified': 'Terverifikasi',
                                         'rejected': 'Ditolak'}.get(r['status'], r['status'])
            cur.close(); conn.close()
            return jsonify(rows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/water/purchases/<int:purchase_id>')
    @role_required(WATER_ROLES)
    def api_water_purchase_detail(purchase_id):
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'DB error'}), 500
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM water_purchases WHERE id=%s", (purchase_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return jsonify({'error': 'Pengajuan tidak ditemukan'}), 404
            role = session.get('user_role', '')
            if role == 'ob' and row['ob_name'] != _session_name():
                cur.close(); conn.close()
                return jsonify({'error': 'Akses ditolak'}), 403
            result = _purchase_row(cur, row)
            cur.close(); conn.close()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ============================================================
    # VERIFIKASI — oleh Finance
    # ============================================================
    @app.route('/api/water/purchases/<int:purchase_id>/verify', methods=['POST'])
    @role_required(WATER_FINANCE_ROLES)
    def api_water_purchase_verify(purchase_id):
        try:
            data = request.get_json(silent=True) or {}
            remark = str(data.get('remark', '') or '').strip()
            note = str(data.get('note', '') or '').strip()
            if not remark:
                return jsonify({'status': 'error', 'msg': 'Remark verifikasi wajib diisi'}), 400
            who = _session_name() or 'Finance'
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cur = conn.cursor()
            cur.execute("""UPDATE water_purchases
                           SET status='verified', remark=%s, note=%s, verified_by=%s, verified_at=NOW(),
                               rejection_reason=''
                           WHERE id=%s AND status='pending'""",
                        (remark[:500], note[:2000], who, purchase_id))
            affected = cur.rowcount
            conn.commit(); cur.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': 'Pengajuan tidak ditemukan atau sudah diproses'}), 404
            log_activity_async(0, 'water_purchase_verify', 'finance', who,
                               new_data={'purchase_id': purchase_id, 'remark': remark, 'note': note},
                               ip=client_ip())
            return jsonify({'status': 'success', 'msg': 'Pengajuan terverifikasi'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/api/water/purchases/<int:purchase_id>/reject', methods=['POST'])
    @role_required(WATER_FINANCE_ROLES)
    def api_water_purchase_reject(purchase_id):
        try:
            data = request.get_json(silent=True) or {}
            reason = str(data.get('reason', '') or '').strip()
            if not reason:
                return jsonify({'status': 'error', 'msg': 'Alasan penolakan wajib diisi'}), 400
            who = _session_name() or 'Finance'
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'msg': 'DB error'}), 500
            cur = conn.cursor()
            cur.execute("""UPDATE water_purchases
                           SET status='rejected', rejection_reason=%s, verified_by=%s, verified_at=NOW(),
                               remark='', note=''
                           WHERE id=%s AND status='pending'""",
                        (reason[:500], who, purchase_id))
            affected = cur.rowcount
            conn.commit(); cur.close(); conn.close()
            if affected == 0:
                return jsonify({'status': 'error', 'msg': 'Pengajuan tidak ditemukan atau sudah diproses'}), 404
            log_activity_async(0, 'water_purchase_reject', 'finance', who,
                               new_data={'purchase_id': purchase_id, 'reason': reason},
                               ip=client_ip())
            return jsonify({'status': 'success', 'msg': 'Pengajuan ditolak'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    # ============================================================
    # PDF TANDA TERIMA
    # ============================================================
    @app.route('/api/water/purchases/<int:purchase_id>/pdf')
    @role_required(WATER_ROLES)
    def api_water_purchase_pdf(purchase_id):
        try:
            conn = get_db_connection()
            if not conn:
                return make_response('DB error', 500)
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM water_purchases WHERE id=%s", (purchase_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return make_response('Pengajuan tidak ditemukan', 404)
            role = session.get('user_role', '')
            if role == 'ob' and row['ob_name'] != _session_name():
                cur.close(); conn.close()
                return make_response('Akses ditolak', 403)
            cur.execute("SELECT drink_type, brand, satuan, quantity "
                        "FROM water_purchase_items WHERE purchase_id=%s ORDER BY id", (purchase_id,))
            items = cur.fetchall()
            cur.close(); conn.close()

            ga_name, finance_name = _get_ttd_names()
            from modules.pdf_generator import WaterReceiptPDF
            pdf = WaterReceiptPDF()
            pdf.add_page()
            pdf.generate(row, items, ga_name=ga_name, finance_name=finance_name)
            pdf_raw = pdf.output(dest='S')
            pdf_bytes = pdf_raw.encode('latin-1') if isinstance(pdf_raw, str) else bytes(pdf_raw)
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            fname = f'TandaTerima_AirMinum_{row.get("display_id", purchase_id)}.pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={fname}'
            log_activity_async(0, 'water_purchase_pdf', role, _session_name(),
                               new_data={'display_id': row.get('display_id')}, ip=client_ip())
            return response
        except Exception as e:
            return make_response(f'Error: {str(e)}', 500)
