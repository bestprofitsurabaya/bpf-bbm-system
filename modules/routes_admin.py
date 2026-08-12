import os
"""Admin Dashboard & Workflow Routes"""
from flask import (request, redirect, url_for, flash, jsonify, make_response)
from modules.config import get_db_connection
from modules.helpers import log_activity_async, role_required
from modules.notifications import push_driver_notification

def register_admin_routes(app):

    @app.route('/admin', methods=['GET', 'POST'])
    @role_required(['ga', 'finance', 'admin'])
    def admin_dashboard():
        # v2.5: halaman klasik dipensiunkan — seluruh alur memakai SPA /app/dashboard
        # (API pengganti: /api/queue/*, /api/transactions/*, /api/cash/*, /api/trips*).
        return redirect('/app/dashboard')

    @app.route('/admin/queue-fragment/<tab>')
    @role_required(['ga', 'finance', 'admin'])
    def queue_fragment(tab):
        """Fragment tab klasik — dipensiunkan (SPA memakai /api/queue)."""
        return redirect('/app/dashboard')

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
        # v2.5: halaman klasik dipensiunkan — review trip memakai SPA /app/trips
        # (API pengganti: /api/trips, /api/trips/verify, /api/trips/reject).
        return redirect('/app/trips')

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
        # v2.5: halaman klasik dipensiunkan — penugasan memakai SPA /app/assignments
        # (API pengganti: /api/appointments/*).
        return redirect('/app/assignments')
