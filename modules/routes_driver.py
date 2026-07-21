"""Driver & PWA routes"""
from flask import (render_template, request, redirect, url_for,
                   send_from_directory, jsonify, make_response, flash)
from modules.config import get_db_connection
from modules.helpers import (save_file, resolve_driver_form_context, validate_bbm_for_vehicle,
                             ensure_all_master_data, generate_display_id, log_activity_async)
from modules.engine import PerformanceAnalyzer
from datetime import datetime
import os

def register_driver_routes(app, socketio):
    
    @app.route('/')
    def index():
        return redirect(url_for('driver_form'))
    
    @app.route('/driver', methods=['GET', 'POST'])
    def driver_form():
        if request.method == 'POST':
            try:
                driver_name = request.form.get('driver_name', '').strip().upper()
                nopol = request.form.get('nopol', '').strip().upper()
                vehicle_type = request.form.get('vehicle_type', 'AVANZA')
                bbm_type = request.form.get('bbm_type', 'PERTALITE')
                nominal = float(request.form.get('nominal', 0))
                price_per_liter = float(request.form.get('price_per_liter', 10000))
                liter = nominal/price_per_liter if price_per_liter>0 else 0
                odo_km = int(request.form.get('odo_km', 0))
                jumlah_appointment = int(request.form.get('jumlah_appointment', 0) or 0)
                spbu_type = request.form.get('spbu_type', 'rekanan')
                gps_lat = request.form.get('gps_lat')
                gps_lon = request.form.get('gps_lon')
                gps_address = request.form.get('gps_address', '')

                conn = get_db_connection()
                if not conn:
                    flash('Database error!', 'error')
                    return render_template('driver.html')
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM drivers WHERE name=%s AND is_active=TRUE", (driver_name,))
                driver_data = cursor.fetchone()
                resolved = resolve_driver_form_context(driver_data, driver_name, nopol, vehicle_type, bbm_type)
                nopol = resolved['nopol']
                vehicle_type = resolved['vehicle_type']
                bbm_type = resolved['bbm_type']

                ensure_all_master_data(driver_name, nopol, vehicle_type, bbm_type, price_per_liter)
                
                validation = validate_bbm_for_vehicle(vehicle_type, bbm_type)
                if not validation['valid']:
                    flash(validation['error'], 'error')
                    cursor.close(); conn.close()
                    return render_template('driver.html')

                if not driver_name or not nopol or nominal<=0 or odo_km<=0:
                    flash('Semua field harus diisi!', 'error')
                    cursor.close(); conn.close()
                    return render_template('driver.html')

                upload_dir = app.config['UPLOAD_FOLDER']
                foto_odo_sebelum = save_file(request.files.get('foto_odo_sebelum'), 'ODO1', nopol, upload_dir)
                foto_nota_odo_sesudah = save_file(request.files.get('foto_nota_odo_sesudah'), 'ODO2', nopol, upload_dir)
                foto_struk = save_file(request.files.get('foto_struk'), 'STRUK', nopol, upload_dir)
                foto_struk_dispenser = save_file(request.files.get('foto_struk_dispenser'), 'DISP', nopol, upload_dir) if spbu_type=='non_rekanan' else None

                cursor.execute("SELECT odo_km FROM transactions WHERE nopol=%s ORDER BY created_at DESC LIMIT 1", (nopol,))
                previous = cursor.fetchone()
                km_per_liter = 0
                if previous and previous['odo_km']<odo_km and liter>0:
                    km_per_liter = (odo_km - previous['odo_km'])/liter

                analysis = PerformanceAnalyzer.analyze_performance(nopol, km_per_liter, conn, vehicle_type, bbm_type)
                display_id = generate_display_id('BPF', conn)
                
                cursor.execute("""
                    INSERT INTO transactions (display_id, driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                    odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                    status, ml_anomaly_flag, km_per_liter, gps_latitude, gps_longitude, gps_address, jumlah_appointment)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending',%s,%s,%s,%s,%s,%s)
                """, (display_id, driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                      odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                      analysis['is_anomaly'], km_per_liter, gps_lat, gps_lon, gps_address, jumlah_appointment))

                tx_id = cursor.lastrowid
                conn.commit()
                log_activity_async(tx_id, 'create', 'driver', driver_name, ip=request.remote_addr)
                cursor.close(); conn.close()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                    return jsonify({'status': 'success', 'transaction_id': tx_id, 'message': analysis['message']})
                flash(f'Klaim {display_id} berhasil! {analysis["message"]}', 'success')
                return redirect(url_for('driver_form'))
            except Exception as e:
                print(f"Driver error: {e}")
                import traceback; traceback.print_exc()
                flash(f'Error: {str(e)}', 'error')
                return render_template('driver.html')
        return render_template('driver.html')
    
    @app.route('/manifest.json')
    def serve_manifest():
        return send_from_directory(os.getcwd(), 'manifest.json')
    
    @app.route('/sw.js')
    def serve_sw():
        response = make_response(send_from_directory(os.getcwd(), 'sw.js'))
        response.headers['Content-Type'] = 'application/javascript'
        return response
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/submit-trip', methods=['POST'])
    def submit_trip():
        """Process multi-destination trip log submission"""
        try:
            driver_name = request.form.get('driver_name', '').strip().upper()
            nopol = request.form.get('nopol', '').strip().upper()
            trip_date = request.form.get('trip_date', datetime.now().strftime('%Y-%m-%d'))
            jam_berangkat = request.form.get('jam_keberangkatan', '')
            jam_tiba = request.form.get('jam_tiba', '')
            km_awal = int(request.form.get('km_awal', 0) or 0)
            km_akhir = int(request.form.get('km_akhir', 0) or 0)

            if not all([driver_name, nopol, jam_berangkat, km_awal > 0]):
                flash('Driver, Nopol, Jam Berangkat, dan KM Awal wajib diisi!', 'error')
                return redirect(url_for('driver_form'))

            conn = get_db_connection()
            cursor = conn.cursor()

            trip_display_id = generate_trip_display_id(conn)
            cursor.execute("""
                INSERT INTO trip_masters (display_id, driver_name, nopol, trip_date, jam_keberangkatan,
                                         jam_tiba, km_awal, km_akhir, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (trip_display_id, driver_name, nopol, trip_date, jam_berangkat, jam_tiba or None, km_awal, km_akhir or 0))
            trip_id = cursor.lastrowid

            lokasi_berangkat_list = request.form.getlist('lokasi_berangkat[]')
            pukul_berangkat_list = request.form.getlist('pukul_berangkat[]')
            km_berangkat_list = request.form.getlist('km_berangkat[]')
            lokasi_tujuan_list = request.form.getlist('lokasi_tujuan[]')
            pukul_tujuan_list = request.form.getlist('pukul_tujuan[]')
            km_tujuan_list = request.form.getlist('km_tujuan[]')

            detail_count = 0
            for i in range(len(lokasi_berangkat_list)):
                if lokasi_berangkat_list[i].strip() and lokasi_tujuan_list[i].strip():
                    cursor.execute("""
                        INSERT INTO trip_details (trip_master_id, no_urut, lokasi_berangkat,
                                                 pukul_berangkat, km_berangkat, lokasi_tujuan,
                                                 pukul_tujuan, km_tujuan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (trip_id, i+1, lokasi_berangkat_list[i], pukul_berangkat_list[i] or None,
                          int(km_berangkat_list[i] or 0), lokasi_tujuan_list[i],
                          pukul_tujuan_list[i] or None, int(km_tujuan_list[i] or 0)))
                    detail_count += 1

            conn.commit()
            log_activity_async(trip_id, 'trip_submit', 'driver', driver_name,
                              new_data={'details': detail_count}, ip=request.remote_addr)
            cursor.close(); conn.close()

            try:
                socketio.emit('new_trip_report', {
                    'id': trip_id, 'driver_name': driver_name, 'nopol': nopol,
                    'trip_date': trip_date, 'total_routes': detail_count, 'status': 'pending',
                    'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
                })
            except:
                pass

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'success', 'trip_id': trip_id, 'routes': detail_count})
            flash(f'Log perjalanan berhasil disubmit dengan {detail_count} rute!', 'success')
            return redirect(url_for('driver_form'))
        except Exception as e:
            print(f"Trip submit error: {e}")
            import traceback; traceback.print_exc()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('driver_form'))
    
    from modules.helpers import generate_trip_display_id
