"""Admin Dashboard & Workflow Routes"""
from flask import (render_template, request, redirect, url_for, flash, jsonify)
from modules.config import get_db_connection
from modules.helpers import log_activity_async, save_file, generate_display_id, generate_trip_display_id
from datetime import datetime, timedelta

def register_admin_routes(app):
    
    @app.route('/admin', methods=['GET', 'POST'])
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
            if tab == 'finance':
                cursor.execute("SELECT * FROM transactions WHERE status='verified_ga' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            elif tab == 'driver_confirm':
                cursor.execute("SELECT * FROM transactions WHERE status='os_finance' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            elif tab == 'archive':
                cursor.execute("SELECT * FROM transactions WHERE status='archived' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM transactions WHERE status IN ('pending','modified') AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at ASC")
            txs = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as c FROM transactions"); total = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status IN ('pending','modified')"); pending = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='verified_ga'"); vga = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='os_finance'"); osf = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='archived'"); arc = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE ml_anomaly_flag=TRUE"); anom = cursor.fetchone()['c']
            cursor.execute("SELECT vehicle_type FROM vehicles WHERE is_active=TRUE"); vehicles = cursor.fetchall()
            cursor.execute("SELECT name FROM bbm_types WHERE is_active=TRUE"); bbm_types = cursor.fetchall()
            cursor.close(); conn.close()

            return render_template('admin.html', transactions=txs,
                                  stats={'total': total, 'pending': pending, 'verified_ga': vga, 'os_finance': osf, 'archived': arc, 'anomaly': anom, 'tab': tab},
                                  vehicles=vehicles, bbm_types=bbm_types)
        except Exception as e:
            return f"Error: {str(e)}", 500
    
    @app.route('/ga/approve/<int:tx_id>')
    def ga_approve(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE id=%s AND status IN ('pending','modified')", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                flash('Transaksi tidak ditemukan!', 'error')
                cursor.close(); conn.close()
                return redirect(url_for('admin_dashboard'))
            admin_name = request.args.get('admin', 'GA Officer')
            cursor.execute("UPDATE transactions SET status='verified_ga', ga_approved_by=%s, ga_approved_at=NOW(), approved_by_user=%s WHERE id=%s", (admin_name, admin_name, tx_id))
            conn.commit()
            log_activity_async(tx_id, 'ga_approve', 'ga', admin_name, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Klaim #{tx_id} disetujui GA!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='ga_queue'))
    
    @app.route('/finance/payout/<int:tx_id>')
    def finance_payout(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE id=%s AND status='verified_ga'", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                flash('Transaksi tidak ditemukan!', 'error')
                cursor.close(); conn.close()
                return redirect(url_for('admin_dashboard'))
            admin_name = request.args.get('admin', 'Finance Officer')
            cursor.execute("UPDATE transactions SET status='os_finance', finance_payout_by=%s, finance_payout_at=NOW(), payout_by_user=%s WHERE id=%s", (admin_name, admin_name, tx_id))
            conn.commit()
            log_activity_async(tx_id, 'finance_payout', 'finance', admin_name, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Dana #{tx_id} dicairkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='finance'))
    
    @app.route('/finance/archive/<int:tx_id>')
    def finance_archive(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE id=%s AND status='os_finance'", (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                flash('Transaksi tidak ditemukan!', 'error')
                cursor.close(); conn.close()
                return redirect(url_for('admin_dashboard'))
            admin_name = request.args.get('admin', 'Finance Officer')
            cursor.execute("UPDATE transactions SET status='archived', archived_by=%s, archived_at=NOW(), archived_by_user=%s WHERE id=%s", (admin_name, admin_name, tx_id))
            conn.commit()
            log_activity_async(tx_id, 'archive', 'finance', admin_name, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Klaim #{tx_id} diarsipkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard', tab='driver_confirm'))
    
    @app.route('/admin/reject/<int:tx_id>', methods=['POST'])
    def reject_tx(tx_id):
        try:
            reason = request.form.get('rejection_reason', 'Tanpa alasan')
            rejected_by = request.form.get('rejected_by', 'Admin')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status='rejected', rejection_reason=%s WHERE id=%s", (reason, tx_id))
            conn.commit()
            log_activity_async(tx_id, 'reject', 'admin', rejected_by, new_data={'reason': reason}, ip=request.remote_addr)
            cursor.close(); conn.close()
            flash(f'Transaksi ditolak: {reason}', 'warning')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/unverify/<int:tx_id>')
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
    
    @app.route('/admin/delete/<int:tx_id>')
    def delete_tx(tx_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id=%s", (tx_id,))
            conn.commit()
            log_activity_async(tx_id, 'delete', 'admin', 'Admin', ip=request.remote_addr)
            cursor.close(); conn.close()
            flash('🗑️ Transaksi dihapus', 'warning')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_rekap'))
    
    @app.route('/admin/edit-odo/<int:tx_id>', methods=['POST'])
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
    
    @app.route('/admin/trips/verify/<int:trip_id>')
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

    @app.route('/ga/assignments')
    def ga_assignments():
        return render_template('ga_assignments.html')
