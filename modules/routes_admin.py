import os
"""Admin Dashboard & Workflow Routes"""
from flask import (render_template, request, redirect, url_for, flash, jsonify, make_response)
from modules.config import get_db_connection
from modules.helpers import log_activity_async, save_file, generate_display_id, generate_trip_display_id, role_required
from modules.notifications import push_driver_notification
from datetime import datetime, timedelta

def register_admin_routes(app):
    def cleanup_transaction_files(self, tx_data, upload_folder='uploads'):
        """Hapus file foto transaksi dari folder uploads."""
        file_fields = [
            'foto_odo_sebelum', 'foto_nota_odo_sesudah',
            'foto_struk', 'foto_struk_dispenser', 'foto_mypertamina_admin'
        ]
        deleted = []
        for field in file_fields:
            filename = tx_data.get(field) if isinstance(tx_data, dict) else None
            if filename and filename.strip():
                fpath = os.path.join(upload_folder, filename)
                try:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                        deleted.append(filename)
                except Exception as e:
                    print(f"Cleanup error {filename}: {e}")
        return deleted


    def _queue_txs(cursor, tab):
        """Ambil daftar transaksi sesuai tab (dipakai admin_dashboard & queue-fragment).
        Tab archive menghormati params URL (search/start_date/end_date/bbm_type/page) agar
        konsisten dengan /api/transactions/archive dan filter loadArchive() (default 7 hari)."""
        if tab == 'finance':
            cursor.execute("SELECT * FROM transactions WHERE status='verified_ga' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
        elif tab == 'driver_confirm':
            cursor.execute("SELECT * FROM transactions WHERE status='os_finance' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
        elif tab == 'archive':
            where = ["status='archived'", "(is_dummy=0 OR is_dummy IS NULL)"]
            params = []
            search = request.args.get('search', '').strip()
            sd = request.args.get('start_date', '').strip()
            ed = request.args.get('end_date', '').strip()
            bb = request.args.get('bbm_type', '').strip()
            if not sd:
                where.append("created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
            if sd:
                where.append("DATE(created_at) >= %s"); params.append(sd)
            if ed:
                where.append("DATE(created_at) <= %s"); params.append(ed)
            if search:
                where.append("(nopol LIKE %s OR driver_name LIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            if bb:
                where.append("bbm_type = %s"); params.append(bb)
            page = max(1, request.args.get('page', 1, type=int) or 1)
            limit = 50
            query = "SELECT * FROM transactions WHERE " + " AND ".join(where) + " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            cursor.execute(query, params + [limit, (page - 1) * limit])
        else:
            cursor.execute("SELECT * FROM transactions WHERE status IN ('pending','modified') AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
        return cursor.fetchall()

    @app.route('/admin', methods=['GET', 'POST'])
    @role_required(['ga', 'finance', 'admin'])
    def admin_dashboard():
        if request.method == 'POST':
            try:
                action = request.form.get('action', 'verify')
                tx_id = request.form.get('tx_id')
                if action == 'verify':
                    conn = get_db_connection()
                    if not conn:
                        flash('DB error!', 'error')
                        return redirect(url_for('admin_dashboard'))
                    cursor = conn.cursor()
                    is_error = request.form.get('mypertamina_error') == 'on'
                    upload_dir = app.config['UPLOAD_FOLDER']
                    foto_mypertamina = save_file(request.files.get('foto_mypertamina'), 'ADMIN_MYPTM', request.form.get('nopol', ''), upload_dir)
                    cursor.execute("UPDATE transactions SET is_mypertamina_error=%s, foto_mypertamina_admin=%s, status='verified_ga', updated_at=CURRENT_TIMESTAMP WHERE id=%s", (is_error, foto_mypertamina, tx_id))
                    conn.commit()
                    cursor.close(); conn.close()
                    log_activity_async(int(tx_id), 'verify', 'admin', 'Admin', ip=request.remote_addr)
                    flash('✅ Klaim diverifikasi!', 'success')
                elif action == 'modify':
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE transactions SET vehicle_type=%s, bbm_type=%s, nominal=%s, odo_km=%s, spbu_type=%s, status='modified', updated_at=CURRENT_TIMESTAMP WHERE id=%s",
                        (request.form.get('edit_vehicle'), request.form.get('edit_bbm'), request.form.get('edit_nominal'),
                         request.form.get('edit_odo'), request.form.get('edit_spbu'), tx_id))
                    conn.commit()
                    cursor.close(); conn.close()
                    log_activity_async(int(tx_id), 'modify', 'admin', 'Admin', ip=request.remote_addr)
                    flash('✅ Data dimodifikasi!', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('admin_dashboard'))

        try:
            conn = get_db_connection()
            if not conn: return "DB tidak tersedia", 500
            cursor = conn.cursor(dictionary=True)
            tab = request.args.get('tab', 'ga_queue')
            if tab not in ('ga_queue', 'finance', 'driver_confirm', 'archive', 'cash'):
                tab = 'ga_queue'
            txs = _queue_txs(cursor, tab) if tab != 'cash' else []

            cursor.execute("SELECT COUNT(*) as c FROM transactions"); total = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status IN ('pending','modified')"); pending = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='verified_ga'"); vga = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='os_finance'"); osf = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='archived'"); arc = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE ml_anomaly_flag=TRUE"); anom = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM fuel_cash_requests WHERE status IN ('DRAFT','GA_APPROVED','FINANCE_APPROVED')")
            cash_pending = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM fuel_cash_requests WHERE status = 'FUNDS_WITH_DRIVER'")
            cash_with_driver = cursor.fetchone()['c']
            cursor.execute("SELECT vehicle_type FROM vehicles WHERE is_active=TRUE"); vehicles = cursor.fetchall()
            cursor.execute("SELECT name FROM bbm_types WHERE is_active=TRUE"); bbm_types = cursor.fetchall()
            cursor.close(); conn.close()

            return render_template('admin.html', transactions=txs, tab=tab,
                                  stats={'total': total, 'pending': pending, 'verified_ga': vga, 'os_finance': osf, 'archived': arc, 'anomaly': anom, 'cash_pending': cash_pending if 'cash_pending' in dir() else 0, 'cash_with_driver': cash_with_driver if 'cash_with_driver' in dir() else 0, 'tab': tab},
                                  vehicles=vehicles, bbm_types=bbm_types)
        except Exception as e:
            return f"Error: {str(e)}", 500

    @app.route('/admin/queue-fragment/<tab>')
    @role_required(['ga', 'finance', 'admin'])
    def queue_fragment(tab):
        """Fragment HTML konten tab untuk SPA switch tanpa reload (render Jinja sama persis)."""
        try:
            if tab not in ('ga_queue', 'finance', 'driver_confirm', 'archive', 'cash'):
                tab = 'ga_queue'
            conn = get_db_connection()
            if not conn:
                return "DB tidak tersedia", 500
            cursor = conn.cursor(dictionary=True)
            txs = _queue_txs(cursor, tab) if tab != 'cash' else []
            cursor.close(); conn.close()
            response = make_response(render_template('_tab_content.html', transactions=txs, tab=tab))
            response.headers['Cache-Control'] = 'no-store'
            return response
        except Exception as e:
            return f"Error: {str(e)}", 500

    @app.route('/ga/approve/<int:tx_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def ga_approve(tx_id):
        is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        admin_name = request.args.get('admin', 'GA Officer')
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='verified_ga', ga_approved_by=%s, ga_approved_at=NOW(), approved_by_user=%s WHERE id=%s AND status IN ('pending','modified')", (admin_name, admin_name, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        push_driver_notification(row[0], 'claim', 'approved', f'Klaim {row[1]} Anda disetujui GA', row[1])
                except Exception as ne:
                    print(f"[notify] approve error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                if is_xhr:
                    return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
                flash('Transaksi tidak ditemukan atau sudah diproses!', 'error')
                return redirect(url_for('admin_dashboard', tab='ga_queue'))
            log_activity_async(tx_id, 'ga_approve', 'ga', admin_name, ip=request.remote_addr)
            if is_xhr:
                return jsonify({'status': 'success', 'msg': f'Klaim #{tx_id} disetujui GA!'})
            flash(f'Klaim #{tx_id} disetujui GA!', 'success')
        except Exception as e:
            if is_xhr:
                return jsonify({'status': 'error', 'msg': str(e)}), 500
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='ga_queue'))

    @app.route('/finance/payout/<int:tx_id>', methods=['POST'])
    @role_required(['finance', 'admin'])
    def finance_payout(tx_id):
        is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        admin_name = request.args.get('admin', 'Finance Officer')
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='os_finance', finance_payout_by=%s, finance_payout_at=NOW(), payout_by_user=%s WHERE id=%s AND status='verified_ga'", (admin_name, admin_name, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        push_driver_notification(row[0], 'claim', 'paid', f'Dana klaim {row[1]} sudah dicairkan Finance', row[1])
                except Exception as ne:
                    print(f"[notify] payout error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                if is_xhr:
                    return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
                flash('Transaksi tidak ditemukan atau sudah diproses!', 'error')
                return redirect(url_for('admin_dashboard', tab='finance'))
            log_activity_async(tx_id, 'finance_payout', 'finance', admin_name, ip=request.remote_addr)
            if is_xhr:
                return jsonify({'status': 'success', 'msg': f'Dana #{tx_id} dicairkan!'})
            flash(f'Dana #{tx_id} dicairkan!', 'success')
        except Exception as e:
            if is_xhr:
                return jsonify({'status': 'error', 'msg': str(e)}), 500
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='finance'))

    @app.route('/finance/archive/<int:tx_id>', methods=['POST'])
    @role_required(['finance', 'admin'])
    def finance_archive(tx_id):
        is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        admin_name = request.args.get('admin', 'Finance Officer')
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='archived', archived_by=%s, archived_at=NOW(), archived_by_user=%s WHERE id=%s AND status='os_finance'", (admin_name, admin_name, tx_id))
            affected = cursor.rowcount
            conn.commit()
            if affected > 0:
                try:
                    cursor.execute("SELECT driver_name, display_id FROM transactions WHERE id=%s", (tx_id,))
                    row = cursor.fetchone()
                    if row:
                        push_driver_notification(row[0], 'claim', 'archived', f'Klaim {row[1]} selesai & diarsipkan', row[1])
                except Exception as ne:
                    print(f"[notify] archive error: {ne}")
            cursor.close(); conn.close()
            if affected == 0:
                if is_xhr:
                    return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah diproses.'}), 409
                flash('Transaksi tidak ditemukan atau sudah diproses!', 'error')
                return redirect(url_for('admin_dashboard', tab='driver_confirm'))
            log_activity_async(tx_id, 'archive', 'finance', admin_name, ip=request.remote_addr)
            if is_xhr:
                return jsonify({'status': 'success', 'msg': f'Transaksi #{tx_id} diarsipkan!'})
            flash(f'Klaim #{tx_id} diarsipkan!', 'success')
        except Exception as e:
            if is_xhr:
                return jsonify({'status': 'error', 'msg': str(e)}), 500
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='driver_confirm'))

    @app.route('/admin/reject/<int:tx_id>', methods=['POST'])
    @role_required(['ga', 'finance', 'admin'])
    def reject_tx(tx_id):
        is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            reason = request.form.get('rejection_reason', 'Tanpa alasan')
            rejected_by = request.form.get('rejected_by', 'Admin')
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Cek apakah ini LPJ kasbon
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
            tx = cursor.fetchone()

            # Reject transaksi (guard: jangan reject ulang yang sudah ditolak)
            cursor.execute("UPDATE transactions SET status='rejected', rejection_reason=%s WHERE id=%s AND status <> 'rejected'", (reason, tx_id))
            affected = cursor.rowcount

            if affected == 0:
                conn.commit()
                cursor.close(); conn.close()
                if is_xhr:
                    return jsonify({'status': 'error', 'msg': f'Transaksi #{tx_id} tidak ditemukan atau sudah ditolak.'}), 409
                flash('Transaksi tidak ditemukan atau sudah ditolak!', 'error')
                return redirect(url_for('admin_dashboard'))

            # Jika LPJ kasbon, kembalikan cash request ke FUNDS_WITH_DRIVER
            if tx and tx.get('transaction_type') == 'CASH_LPJ':
                cursor.execute("UPDATE fuel_cash_requests SET status = 'FUNDS_WITH_DRIVER', lpj_transaction_id = NULL, lpj_submitted_at = NULL WHERE lpj_transaction_id = %s", (tx_id,))

            # Hapus file fisik dari uploads
            upload_dir = app.config.get("UPLOAD_FOLDER", "uploads")
            try:
                for fname in [tx.get("foto_odo_sebelum"), tx.get("foto_nota_odo_sesudah"), tx.get("foto_struk"), tx.get("foto_struk_dispenser")]:
                    if fname:
                        fpath = os.path.join(upload_dir, fname)
                        if os.path.exists(fpath):
                            os.remove(fpath)
            except Exception as e:
                print(f"Cleanup error: {e}")
            conn.commit()
            log_activity_async(tx_id, 'reject', 'admin', rejected_by, new_data={'reason': reason, 'type': tx.get('transaction_type') if tx else 'CLAIM'}, ip=request.remote_addr)
            if tx:
                try:
                    push_driver_notification(tx['driver_name'], 'claim', 'rejected', f'Klaim {tx["display_id"]} ditolak: {reason}', tx['display_id'])
                except Exception as ne:
                    print(f"[notify] reject error: {ne}")
            cursor.close(); conn.close()
            if is_xhr:
                return jsonify({'status': 'success', 'msg': f'Transaksi #{tx_id} ditolak'})
            flash(f'Transaksi ditolak: {reason}', 'warning')
        except Exception as e:
            if is_xhr:
                return jsonify({'status': 'error', 'msg': str(e)}), 500
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/unverify/<int:tx_id>', methods=['POST'])
    @role_required(['admin'])
    def unverify_tx(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='pending' WHERE id=%s", (tx_id,))
            conn.commit()
            log_activity_async(tx_id, 'unverify', 'admin', 'Admin', ip=request.remote_addr)
            cursor.close(); conn.close()
            flash('✅ Transaksi dikembalikan ke Pending', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_rekap'))

    @app.route('/admin/delete/<int:tx_id>', methods=['POST'])
    @role_required(['admin'])
    def delete_tx(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Cek apakah ini LPJ kasbon
            cursor.execute("SELECT id FROM fuel_cash_requests WHERE lpj_transaction_id = %s", (tx_id,))
            cash_req = cursor.fetchone()
            if cash_req:
                # Reset cash request ke FUNDS_WITH_DRIVER (LPJ batal)
                cursor.execute("UPDATE fuel_cash_requests SET lpj_transaction_id = NULL, status = 'FUNDS_WITH_DRIVER', lpj_submitted_at = NULL WHERE lpj_transaction_id = %s", (tx_id,))
            # Hapus transaksi
            cursor.execute("DELETE FROM transactions WHERE id=%s", (tx_id,))
            upload_dir = app.config.get("UPLOAD_FOLDER", "uploads")
            try:
                for fname in [tx.get("foto_odo_sebelum"), tx.get("foto_nota_odo_sesudah"), tx.get("foto_struk"), tx.get("foto_struk_dispenser")]:
                    if fname:
                        fpath = os.path.join(upload_dir, fname)
                        if os.path.exists(fpath):
                            os.remove(fpath)
            except Exception as e:
                print(f"Cleanup error: {e}")
            conn.commit()
            if cash_req:
                log_activity_async(tx_id, 'delete_lpj', 'admin', 'Admin', new_data={'cash_id': cash_req[0], 'action': 'lpj_deleted_cash_reset'}, ip=request.remote_addr)
            else:
                log_activity_async(tx_id, 'delete', 'admin', 'Admin', ip=request.remote_addr)
            cursor.close(); conn.close()
            flash('🗑️ Transaksi dihapus' + (' (Kasbon dikembalikan ke status Dana di Driver)' if cash_req else ''), 'warning')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_rekap'))

    @app.route('/admin/edit-odo/<int:tx_id>', methods=['POST'])
    @role_required(['finance', 'admin'])
    def edit_odo(tx_id):
        try:
            data = request.get_json()
            pin = data.get('pin', '')
            username = data.get('username', 'finance_officer')
            new_odo = int(data.get('new_odo', 0))
            remark = data.get('remark', '').strip()
            if not pin or len(pin) != 6:
                return jsonify({'status': 'error', 'msg': 'PIN 6-digit wajib diisi'}), 400
            if new_odo <= 0:
                return jsonify({'status': 'error', 'msg': 'ODO baru tidak valid'}), 400
            if not remark:
                return jsonify({'status': 'error', 'msg': 'Remark/alasan wajib diisi'}), 400
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND pin = %s AND is_active = TRUE", (username, pin))
            user = cursor.fetchone()
            if not user or user['role'] not in ['finance', 'admin']:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'PIN salah atau tidak memiliki akses'}), 401
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                cursor.close(); conn.close()
                return jsonify({'status': 'error', 'msg': 'Transaksi tidak ditemukan'}), 404
            old_odo = tx['odo_km']
            cursor.execute("UPDATE transactions SET odo_km = %s, modification_note = %s, modified_by = %s, updated_at = NOW() WHERE id = %s", (new_odo, remark, user['full_name'], tx_id))
            conn.commit()
            log_activity_async(tx_id, 'finance_edit_odo', 'finance', user['full_name'],
                              old_data={'odo_km': old_odo}, new_data={'odo_km': new_odo, 'remark': remark}, ip=request.remote_addr)
            cursor.close(); conn.close()
            return jsonify({'status': 'success', 'msg': f'ODO berhasil diubah dari {old_odo:,} ke {new_odo:,} km'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': str(e)}), 500

    @app.route('/admin/trips')
    @role_required(['ga', 'finance', 'admin'])
    def admin_trips():
        try:
            driver_filter = request.args.get('driver', '').strip()
            date_filter = request.args.get('date', '').strip()
            status_filter = request.args.get('status', 'pending')
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = """SELECT tm.*, (SELECT COUNT(*) FROM trip_details WHERE trip_master_id = tm.id) as total_routes
                       FROM trip_masters tm WHERE 1=1"""
            params = []
            if driver_filter:
                query += " AND tm.driver_name LIKE %s"; params.append(f"%{driver_filter}%")
            if date_filter:
                query += " AND tm.trip_date = %s"; params.append(date_filter)
            if status_filter in ['pending', 'verified_ga', 'rejected']:
                query += " AND tm.status = %s"; params.append(status_filter)
            query += " ORDER BY tm.created_at DESC LIMIT 100"
            cursor.execute(query, params)
            trips = cursor.fetchall()
            cursor.close(); conn.close()
            return render_template('trips_review.html', trips=trips,
                                 filters={'driver': driver_filter, 'date': date_filter, 'status': status_filter})
        except Exception as e:
            return f"Error: {str(e)}", 500

    @app.route('/admin/trips/verify/<int:trip_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def verify_trip(trip_id):
        try:
            admin_name = request.args.get('admin', 'GA Officer')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE trip_masters SET status='verified_ga', verified_by=%s, verified_at=NOW() WHERE id=%s AND status='pending'", (admin_name, trip_id))
            conn.commit()
            log_activity_async(trip_id, 'trip_verify', 'ga', admin_name, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Trip #{trip_id} diverifikasi!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_trips'))

    @app.route('/admin/trips/reject/<int:trip_id>', methods=['POST'])
    @role_required(['ga', 'admin'])
    def reject_trip(trip_id):
        try:
            reason = request.form.get('reason', 'Tidak valid')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE trip_masters SET status='rejected', rejection_reason=%s WHERE id=%s", (reason, trip_id))
            conn.commit()
            log_activity_async(trip_id, 'trip_reject', 'ga', 'GA Officer', new_data={'reason': reason}, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Trip #{trip_id} ditolak: {reason}', 'warning')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_trips'))

    @app.route('/admin/trips/export/<int:trip_id>')
    @role_required(['ga', 'finance', 'admin'])
    def export_trip_excel(trip_id):
        from modules.excel_generator import generate_trip_logsheet
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM trip_masters WHERE id=%s", (trip_id,))
            master = cursor.fetchone()
            if not master:
                cursor.close(); conn.close()
                return "Trip not found", 404
            cursor.execute("SELECT * FROM trip_details WHERE trip_master_id=%s ORDER BY no_urut", (trip_id,))
            details = cursor.fetchall()
            cursor.close(); conn.close()
            excel_bytes = generate_trip_logsheet(master, details)
            response = make_response(excel_bytes)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=Logsheet_{master["nopol"]}_{master["trip_date"]}.xlsx'
            return response
        except Exception as e:
            return f"Error: {str(e)}", 500
    @app.route('/admin/trips/export-pdf/<int:trip_id>')
    @role_required(['ga', 'finance', 'admin'])
    def export_trip_pdf(trip_id):
        try:
            from modules.pdf_generator import BPFBasePDF
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM trip_masters WHERE id=%s", (trip_id,))
            master = cursor.fetchone()
            if not master:
                cursor.close(); conn.close()
                return "Trip not found", 404
            cursor.execute("SELECT * FROM trip_details WHERE trip_master_id=%s ORDER BY no_urut", (trip_id,))
            details = cursor.fetchall()
            cursor.close(); conn.close()

            pdf = BPFBasePDF()
            pdf.add_page()
            pdf.set_font(pdf._font(), 'B', 12)
            pdf.cell(0, 8, f'LOG PERJALANAN #{master["display_id"]}', align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

            # Info header
            pdf.set_font(pdf._font(), '', 8)
            info = [
                ('Driver', master['driver_name']),
                ('Nopol', master['nopol']),
                ('Tanggal', str(master['trip_date'])),
                ('Jam Berangkat', master['jam_keberangkatan'] or '-'),
                ('Jam Tiba', master['jam_tiba'] or '-'),
                ('KM Awal', str(master['km_awal'])),
                ('KM Akhir', str(master['km_akhir'] or 0)),
                ('Status', master['status']),
            ]
            for label, value in info:
                pdf.set_font(pdf._font(), 'B', 8)
                pdf.cell(35, 5, label)
                pdf.set_font(pdf._font(), '', 8)
                pdf.cell(0, 5, ': ' + str(value), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

            # Rute
            pdf.set_font(pdf._font(), 'B', 9)
            pdf.cell(0, 6, 'RUTE PERJALANAN', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            headers = ['NO', 'LOKASI BERANGKAT', 'PUKUL', 'KM', 'LOKASI TUJUAN', 'PUKUL', 'KM']
            widths = [8, 40, 18, 14, 40, 18, 14]
            pdf.set_fill_color(37, 99, 235)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font(pdf._font(), 'B', 7)
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 6, h, border=1, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln()

            pdf.set_font(pdf._font(), '', 7)
            for i, d in enumerate(details, 1):
                pdf.cell(widths[0], 5, str(i), border=1, align='C')
                pdf.cell(widths[1], 5, pdf.clean_text(str(d['lokasi_berangkat'])[:30]), border=1)
                pdf.cell(widths[2], 5, str(d['pukul_berangkat'] or '-'), border=1, align='C')
                pdf.cell(widths[3], 5, str(d['km_berangkat']), border=1, align='C')
                pdf.cell(widths[4], 5, pdf.clean_text(str(d['lokasi_tujuan'])[:30]), border=1)
                pdf.cell(widths[5], 5, str(d['pukul_tujuan'] or '-'), border=1, align='C')
                pdf.cell(widths[6], 5, str(d['km_tujuan']), border=1, align='C')
                pdf.ln()

            pdf_raw = pdf.output(dest='S')
            pdf_bytes = pdf_raw.encode('latin-1') if isinstance(pdf_raw, str) else bytes(pdf_raw)
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=BPF_Logsheet_' + str(master.get('display_id', master['id'])) + '_' + str(master['nopol']) + '_' + str(master['trip_date']) + '.pdf'
            log_activity_async(trip_id, 'trip_export_pdf', 'ga', 'GA Officer', ip=request.remote_addr)
            return response
        except Exception as e:
            return f"Error: {str(e)}", 500


    @app.route('/ga/assignments')
    @role_required(['ga', 'finance', 'admin'])
    def ga_assignments():
        return render_template('ga_assignments.html')
