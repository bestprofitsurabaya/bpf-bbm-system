from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, make_response, flash
import os
import time
import json
import requests
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error, pooling
from fpdf import FPDF
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
import threading
from concurrent.futures import ThreadPoolExecutor
import io
warnings.filterwarnings('ignore')

app = Flask(__name__)
# Set limit upload 16MB untuk mengakomodasi resolusi kamera iPhone 13
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Membatasi total worker thread di produksi guna mencegah memori leak / exhaustion
production_pool_executor = ThreadPoolExecutor(max_workers=20)
app.secret_key = os.environ.get('SECRET_KEY', 'bpf_bbm_secret_key_production_default_2026')
UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ============================================================
# DATABASE POOLING
# ============================================================
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'bpf_user'),
    'password': os.environ.get('DB_PASSWORD', 'bpf_pass'),
    'database': os.environ.get('DB_NAME', 'bpf_asset_system'),
    'pool_name': 'bbm_pool',
    'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
    'pool_reset_session': True,
    'autocommit': False,
    'connect_timeout': 60,
    'use_pure': True
}

# Inisialisasi Real Enterprise Connection Pool Terpusat
try:
    db_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
    print("✔ Real MySQLConnectionPool berhasil diinisialisasi secara global.")
except Error as e:
    print(f"❌ Gagal menginisialisasi MySQL Connection Pool: {e}")
    db_pool = None

def get_db_connection():
    # Mengambil koneksi aktif yang sudah ready dari pool manajemen
    if db_pool:
        try:
            return db_pool.get_connection()
        except Error as pool_err:
            print(f"⚠ Pool exhausted atau mengalami kendala: {pool_err}. Melakukan fallback ke koneksi langsung.")
    
    # Mekanisme pertahanan berlapis: Fallback koneksi non-pool jika terjadi kontensi tinggi
    max_retries = 5
    retry_delay = 1
    fallback_config = {k: v for k, v in DB_CONFIG.items() if k not in ['pool_name', 'pool_size']}
    for attempt in range(max_retries):
        try:
            return mysql.connector.connect(**fallback_config)
        except Error as e:
            if attempt == max_retries - 1:
                print(f"Database connection total failure: {e}")
                raise
            time.sleep(retry_delay)
    return None

def save_file(file_obj, prefix, nopol):
    if file_obj and file_obj.filename:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{nopol}_{timestamp_str}_{file_obj.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        return filename
    return None

# ============================================================
# PWA ROUTES
# ============================================================
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    response = make_response(send_from_directory(os.getcwd(), 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response

# ============================================================
# API ROUTES
# ============================================================
@app.route('/api/vehicles')
def api_vehicles():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database error'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT vehicle_type, brand, fuel_capacity, description FROM vehicles WHERE is_active = TRUE ORDER BY vehicle_type")
        vehicles = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(vehicles)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bbm_types')
def api_bbm_types():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database error'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, price_per_liter, octane_rating FROM bbm_types WHERE is_active = TRUE ORDER BY name")
        bbm_types = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bbm_types)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/driver-assignments', methods=['GET'])
def api_driver_assignments():
    """Return list of active driver-vehicle assignments"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database error'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT da.*, bt.price_per_liter 
            FROM driver_assignments da
            LEFT JOIN bbm_types bt ON da.bbm_type = bt.name
            WHERE da.is_active = TRUE 
            ORDER BY da.driver_name
        """)
        assignments = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(assignments)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicle_bbm/<vehicle_type>')
def api_vehicle_bbm(vehicle_type):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database error'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT vba.bbm_type, vba.min_km_per_liter, vba.max_km_per_liter, 
                   vba.warning_km_per_liter, vba.good_km_per_liter, vba.is_default,
                   bt.price_per_liter
            FROM vehicle_bbm_allowed vba
            JOIN bbm_types bt ON vba.bbm_type = bt.name
            WHERE vba.vehicle_type = %s AND bt.is_active = TRUE
            ORDER BY vba.is_default DESC, vba.bbm_type
        """, (vehicle_type,))
        bbm_allowed = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bbm_allowed)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# API - DRIVERS LIST (untuk auto-fill form)
# ============================================================
@app.route('/api/drivers')
def api_drivers():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database error'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT name, nopol, vehicle_type, bbm_type 
            FROM drivers 
            WHERE is_active = TRUE 
            ORDER BY name
        """)
        drivers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(drivers)
    except Exception as e:
        print(f"API Drivers error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# VALIDATION ENGINE
# ============================================================
def validate_bbm_for_vehicle(vehicle_type, bbm_type):
    try:
        conn = get_db_connection()
        if not conn:
            return {'valid': False, 'error': 'Database error'}
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM vehicle_bbm_allowed 
            WHERE vehicle_type = %s AND bbm_type = %s
        """, (vehicle_type, bbm_type))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'valid': True,
                'limits': {
                    'min': result['min_km_per_liter'],
                    'max': result['max_km_per_liter'],
                    'warning': result['warning_km_per_liter'],
                    'good': result['good_km_per_liter']
                }
            }
        return {'valid': False, 'error': f'BBM {bbm_type} tidak tersedia untuk {vehicle_type}'}
    except Exception as e:
        print(f"Validation Error: {e}")
        return {'valid': False, 'error': str(e)}

# ============================================================
# LOG ACTIVITY (ASYNC)
# ============================================================
def log_activity_async(transaction_id, action, user_type, user_name, old_data=None, new_data=None, ip=None, ua=None):
    def _log():
        try:
            conn = get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs 
                (transaction_id, action, user_type, user_name, old_data, new_data, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (transaction_id, action, user_type, user_name, 
                  json.dumps(old_data) if old_data else None,
                  json.dumps(new_data) if new_data else None,
                  ip, ua))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Log error: {e}")
    
    # Mendelegasikan penulisan log ke antrean executor produksi yang terkontrol
    production_pool_executor.submit(_log)

# ============================================================
# DAILY SUMMARY UPDATE (ASYNC)
# ============================================================
def update_daily_summary_async(transaction_data):
    def _update():
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            summary_date = datetime.now().date()
            vehicle_type = transaction_data.get('vehicle_type')
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, total_transactions, total_liter, total_nominal, total_odo_km
                FROM daily_summary 
                WHERE summary_date = %s AND vehicle_type = %s
            """, (summary_date, vehicle_type))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE daily_summary 
                    SET total_transactions = total_transactions + 1,
                        total_liter = total_liter + %s,
                        total_nominal = total_nominal + %s,
                        total_odo_km = total_odo_km + %s,
                        avg_km_per_liter = (avg_km_per_liter * total_transactions + %s) / (total_transactions + 1)
                    WHERE id = %s
                """, (transaction_data.get('liter', 0), 
                      transaction_data.get('nominal', 0),
                      transaction_data.get('odo_km', 0),
                      transaction_data.get('km_per_liter', 0),
                      existing[0]))
            else:
                cursor.execute("""
                    INSERT INTO daily_summary 
                    (summary_date, vehicle_type, total_transactions, total_liter, total_nominal, 
                     total_odo_km, avg_km_per_liter)
                    VALUES (%s, %s, 1, %s, %s, %s, %s, %s, %s, %s)
                """, (summary_date, vehicle_type,
                      transaction_data.get('liter', 0),
                      transaction_data.get('nominal', 0),
                      transaction_data.get('odo_km', 0),
                      transaction_data.get('km_per_liter', 0)))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Daily summary error: {e}")
    
    # Mendelegasikan rekap ringkasan harian ke pool executor
    production_pool_executor.submit(_update)

# ============================================================
# ML PERFORMANCE ANALYZER
# ============================================================
class PerformanceAnalyzer:
    @staticmethod
    def analyze_performance(nopol, current_efficiency, conn, vehicle_type, bbm_type):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT warning_km_per_liter, good_km_per_liter, min_km_per_liter, max_km_per_liter
                FROM vehicle_bbm_allowed 
                WHERE vehicle_type = %s AND bbm_type = %s
            """, (vehicle_type, bbm_type))
            limit = cursor.fetchone()
            cursor.close()
            
            if not limit:
                warning = 10.5
                good = 12.5
                min_km = 5.0
                max_km = 18.0
            else:
                warning = float(limit['warning_km_per_liter'])
                good = float(limit['good_km_per_liter'])
                min_km = float(limit['min_km_per_liter'])
                max_km = float(limit['max_km_per_liter'])
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT km_per_liter FROM transactions 
                WHERE nopol = %s AND km_per_liter > 0 AND status = 'verified' 
                ORDER BY created_at DESC LIMIT 15
            """, (nopol,))
            history = cursor.fetchall()
            cursor.close()
            
            if current_efficiency <= 0:
                return {
                    'is_anomaly': False,
                    'status': 'PERLU DATA',
                    'category': 'info',
                    'message': 'Belum ada data yang cukup untuk analisis'
                }
            
            is_anomaly = False
            status = 'BAIK'
            category = 'success'
            message = f'Performa {vehicle_type} - {bbm_type} normal'
            
            if current_efficiency < warning:
                status = 'PERLU PEMERIKSAAN (Boros)'
                category = 'danger'
                message = f'Efisiensi {current_efficiency:.1f} KM/L < standar minimal {warning} KM/L'
                is_anomaly = True
            elif current_efficiency > max_km:
                status = 'PERLU PEMERIKSAAN (Data Tidak Normal)'
                category = 'warning'
                message = f'Efisiensi {current_efficiency:.1f} KM/L di atas maksimal'
                is_anomaly = True
            elif current_efficiency < good:
                status = 'CUKUP'
                category = 'warning'
                message = f'Efisiensi {current_efficiency:.1f} KM/L, perlu pemantauan'
            
            if len(history) >= 5:
                efficiency_data = [row['km_per_liter'] for row in history] + [current_efficiency]
                if len(efficiency_data) >= 6:
                    try:
                        X = np.array(efficiency_data).reshape(-1, 1)
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        iso_forest = IsolationForest(contamination=0.15, random_state=42, n_jobs=-1, n_estimators=50)
                        predictions = iso_forest.fit_predict(X_scaled)
                        
                        if predictions[-1] == -1:
                            is_anomaly = True
                            status = 'ANOMALI DETEKSI ML'
                            category = 'danger'
                            message = 'ML mendeteksi anomali pada data ini'
                    except Exception as e:
                        print(f"ML Error: {e}")
            
            return {
                'is_anomaly': is_anomaly,
                'status': status,
                'category': category,
                'message': message,
                'vehicle_type': vehicle_type,
                'bbm_type': bbm_type,
                'current_efficiency': current_efficiency
            }
        except Exception as e:
            print(f"Performance analysis error: {e}")
            return {
                'is_anomaly': False,
                'status': 'ERROR',
                'category': 'error',
                'message': str(e)
            }


@app.route('/api/get-performance/<plat_nomor>', methods=['GET'])
def get_performance(plat_nomor):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Ambil data performa 30 hari terakhir
        cursor.execute('''
            SELECT km_per_liter, jumlah_appointment 
            FROM transactions 
            WHERE nopol=%s AND status IN ('archived', 'os_finance', 'verified_ga') AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        ''', (plat_nomor,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        if not data:
            return jsonify({"nopol": plat_nomor, "status": "BELUM CUKUP DATA", "avg_kml": 0, "total_appointment": 0})

        avg_kml = sum([d['km_per_liter'] for d in data if d['km_per_liter']]) / len(data)
        total_apt = sum([d['jumlah_appointment'] for d in data if d['jumlah_appointment']])
        
        performa = "BAIK (Efisien)" if avg_kml >= 10.0 else "BOROS (Perlu Pengecekan)"
        
        return jsonify({
            "nopol": plat_nomor,
            "status": performa,
            "avg_kml": round(avg_kml, 2),
            "total_appointment": total_apt,
            "count": len(data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# REKAP DATA ENGINE
# ============================================================
def get_rekap_data(start_date=None, end_date=None, nopol=None, driver=None):
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT t.*, d.vehicle_type as master_vehicle, d.bbm_type as master_bbm
            FROM transactions t
            LEFT JOIN drivers d ON t.driver_name = d.name
            WHERE t.status IN ('archived', 'os_finance', 'verified_ga')
        """
        params = []
        
        if start_date:
            query += " AND DATE(t.created_at) >= %s"
            params.append(start_date)
        if end_date:
            query += " AND DATE(t.created_at) <= %s"
            params.append(end_date)
        if nopol:
            query += " AND t.nopol LIKE %s"
            params.append(f"%{nopol}%")
        if driver:
            query += " AND t.driver_name LIKE %s"
            params.append(f"%{driver}%")
        
        query += " ORDER BY t.nopol ASC, t.created_at ASC"
        
        cursor.execute(query, params)
        all_tx = cursor.fetchall()
        cursor.close()
        conn.close()
        
        nopol_history = {}
        for tx in all_tx:
            curr_nopol = tx['nopol']
            curr_odo = tx['odo_km']
            
            km_awal = nopol_history.get(curr_nopol, curr_odo)
            total_km = curr_odo - km_awal if curr_odo >= km_awal else 0
            rata_rata = (total_km / tx['liter']) if tx['liter'] > 0 else 0
            
            tx['km_awal'] = km_awal
            tx['km_akhir'] = curr_odo
            tx['total_km'] = total_km
            tx['rata_rata'] = rata_rata
            
            nopol_history[curr_nopol] = curr_odo
        
        return list(reversed(all_tx))
    except Exception as e:
        print(f"Rekap data error: {e}")
        return []

# ============================================================
# PDF GENERATOR - UNICODE FIX (TANPA EMOJI)
# ============================================================

class PDFReportCompact(FPDF):
    """PDF Report - Professional single page, narrow margins, humanistic"""
    
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=8)
        self.set_margins(8, 8, 8)
    
    def clean_text(self, text):
        if not text:
            return ""
        import re
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', str(text))
        return text.strip()
    
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(30, 64, 175)
        self.cell(0, 7, 'LAPORAN VERIFIKASI KLAIM BBM', align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(71, 85, 105)
        self.cell(0, 5, 'PT. BESTPROFIT SURABAYA', align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y()+1, self.w - self.r_margin, self.get_y()+1)
        self.ln(4)
    
    def footer(self):
        self.set_y(-8)
        self.set_font('helvetica', 'I', 5)
        self.set_text_color(148, 163, 184)
        self.cell(0, 3, f'Generated: {datetime.now().strftime("%d-%m-%Y %H:%M")} | Page {self.page_no()}', align="C")
    
    def section_title(self, title):
        self.set_font('helvetica', 'B', 9)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(30, 64, 175)
        self.cell(0, 6, '  ' + title, border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(203, 213, 225)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
    
    def info_row(self, label, value, x, y, w_label, w_value):
        self.set_xy(x, y)
        self.set_font('helvetica', 'B', 7)
        self.set_text_color(71, 85, 105)
        self.cell(w_label, 5, label, border=0)
        self.set_font('helvetica', '', 7)
        self.set_text_color(15, 23, 42)
        self.cell(w_value, 5, str(value), border=0)
    
    def generate_compact_report(self, tx):
        # ===== TRANSACTION HEADER =====
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(15, 23, 42)
        nopol_text = self.clean_text(str(tx.get('nopol', '-')).upper())
        self.cell(0, 7, f'TRANSAKSI #{tx["id"]} - {nopol_text}', align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        # ===== INFO GRID (2 columns) =====
        self.section_title('INFORMASI TRANSAKSI')
        
        col1_x = self.l_margin
        col2_x = self.w / 2 + 5
        row_h = 5.5
        label_w = 30
        value_w = 50
        
        rows = [
            [('ID Transaksi', f'#{tx["id"]}'), ('Tanggal', tx['created_at'].strftime('%d-%m-%Y %H:%M') if tx.get('created_at') else '-')],
            [('Nopol', nopol_text), ('Driver', self.clean_text(str(tx.get('driver_name', '-')).upper()))],
            [('Kendaraan', self.clean_text(str(tx.get('vehicle_type', '-')))), ('Jenis BBM', self.clean_text(str(tx.get('bbm_type', '-'))))],
            [('Nominal', f'Rp {tx["nominal"]:,.0f}'), ('Volume', f'{tx["liter"]} Liter')],
            [('Harga/Liter', f'Rp {tx.get("price_per_liter", 0):,.0f}'), ('ODO KM', f'{tx["odo_km"]:,} km')],
            [('SPBU', self.clean_text(str(tx.get('spbu_type', '-')).replace('_', ' ').title())), ('Appointment', f'{tx.get("jumlah_appointment", 0)}x')],
        ]
        
        y_start = self.get_y()
        for i, row in enumerate(rows):
            y_pos = y_start + (i * row_h)
            self.info_row(row[0][0], row[0][1], col1_x, y_pos, label_w, value_w)
            self.info_row(row[1][0], row[1][1], col2_x, y_pos, label_w, value_w)
        
        self.set_y(y_start + len(rows) * row_h + 2)
        
        # ===== LOCATION =====
        gps_addr = self.clean_text(str(tx.get('gps_address', '') or 'Tidak tersedia'))
        self.set_font('helvetica', 'I', 6)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, f'Lokasi: {gps_addr[:120]}', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        # ===== KRONOLOGIS (Humanistic Narrative) =====
        self.section_title('KRONOLOGIS VERIFIKASI')
        
        driver_name = self.clean_text(str(tx.get('driver_name', 'Driver')).upper())
        nopol_short = nopol_text
        tgl = tx['created_at'].strftime('%d %B %Y pukul %H:%M') if tx.get('created_at') else '-'
        nominal_str = f'Rp {tx["nominal"]:,.0f}'
        liter_str = f'{tx["liter"]} Liter'
        odo_str = f'{tx["odo_km"]:,} km'
        spbu_str = self.clean_text(str(tx.get('spbu_type', '-')).replace('_', ' ').title())
        bbm_str = self.clean_text(str(tx.get('bbm_type', '-')))
        appt = tx.get('jumlah_appointment', 0) or 0
        gps_str = self.clean_text(str(tx.get('gps_address', '') or 'lokasi terdeteksi'))
        
        # Build narrative
        narrative = (
            f'Pada hari {tgl}, Bapak/Ibu {driver_name} selaku driver kendaraan {nopol_short} '
            f'melakukan pengisian bahan bakar {bbm_str} sebanyak {liter_str} dengan total biaya sebesar {nominal_str} '
            f'di SPBU {spbu_str}. Pengisian dilakukan pada saat odometer kendaraan menunjukkan angka {odo_str}. '
        )
        
        if appt > 0:
            narrative += (
                f'Pada hari yang sama, driver memiliki {appt} janji temu (appointment) marketing yang harus dipenuhi. '
            )
        
        narrative += (
            f'Lokasi pengisian terdeteksi di {gps_str}. '
        )
        
        # GA/Finance info
        ga_by = self.clean_text(str(tx.get('ga_approved_by', '') or tx.get('approved_by_user', '') or '-'))
        ga_at = tx.get('ga_approved_at')
        fin_by = self.clean_text(str(tx.get('finance_payout_by', '') or tx.get('payout_by_user', '') or '-'))
        fin_at = tx.get('finance_payout_at')
        arc_by = self.clean_text(str(tx.get('archived_by', '') or tx.get('archived_by_user', '') or '-'))
        arc_at = tx.get('archived_at')
        
        if ga_by != '-':
            narrative += f'Klaim ini telah diverifikasi dan disetujui oleh GA ({ga_by})'
            if ga_at: narrative += f' pada {ga_at.strftime("%d %B %Y %H:%M")}'
            narrative += '. '
        
        if fin_by != '-':
            narrative += f'Dana telah dicairkan oleh Finance ({fin_by})'
            if fin_at: narrative += f' pada {fin_at.strftime("%d %B %Y %H:%M")}'
            narrative += '. '
        
        if arc_by != '-':
            narrative += f'Dokumen telah ditandatangani oleh Driver dan diarsipkan oleh Finance ({arc_by})'
            if arc_at: narrative += f' pada {arc_at.strftime("%d %B %Y %H:%M")}'
            narrative += '. '
        
        narrative += (
            f'Seluruh bukti berupa foto ODO, struk, dan dokumen pendukung telah dilampirkan dan diverifikasi. '
            f'Klaim BBM ini dinyatakan SAH dan telah melalui seluruh tahapan persetujuan sesuai prosedur yang berlaku '
            f'di PT. Bestprofit Surabaya.'
        )
        
        self.set_font('helvetica', '', 7)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 4, narrative, align='J')
        self.ln(2)
        
        # ===== WORKFLOW STATUS BAR =====
        self.section_title('STATUS PERSETUJUAN')
        
        statuses = [
            ('GA APPROVAL', ga_by if ga_by != '-' else None, ga_at),
            ('FINANCE PAYOUT', fin_by if fin_by != '-' else None, fin_at),
            ('DRIVER TTD', 'Driver' if arc_by != '-' else None, None),
            ('ARCHIVED', arc_by if arc_by != '-' else None, arc_at),
        ]
        
        bar_w = (self.w - self.l_margin - self.r_margin - 12) / 4
        bar_h = 4
        x = self.l_margin
        y = self.get_y() + 2
        
        for i, (label, who, when) in enumerate(statuses):
            if who:
                self.set_fill_color(34, 197, 94)
                self.set_text_color(255, 255, 255)
            else:
                self.set_fill_color(226, 232, 240)
                self.set_text_color(148, 163, 184)
            
            self.set_xy(x, y)
            self.set_font('helvetica', 'B', 5)
            self.cell(bar_w, bar_h, label, border=0, fill=True, align='C')
            
            if who:
                self.set_xy(x, y + bar_h + 1)
                self.set_font('helvetica', '', 4)
                self.set_text_color(100, 116, 139)
                self.cell(bar_w, 3, f'{who}', align='C')
            
            x += bar_w + 4
        
        self.set_y(y + bar_h + 6)
        
        # ===== PHOTOS =====
        photos = [
            ('ODO Sebelum', tx.get('foto_odo_sebelum')),
            ('ODO + Nota', tx.get('foto_nota_odo_sesudah')),
            ('Struk BBM', tx.get('foto_struk')),
            ('Dispenser', tx.get('foto_struk_dispenser')),
            ('MyPertamina', tx.get('foto_mypertamina_admin')),
        ]
        
        existing = [(l, p) for l, p in photos if p]
        
        if existing:
            self.section_title('BUKTI VISUAL')
            
            img_w = 55
            img_h = 42
            gap = 3
            
            for i in range(0, len(existing), 3):
                row = existing[i:i+3]
                x = self.l_margin
                y = self.get_y()
                
                if y > 245:
                    self.add_page()
                    y = self.get_y()
                
                for label, path in row:
                    self.set_xy(x, y)
                    self.set_fill_color(248, 250, 252)
                    self.set_draw_color(203, 213, 225)
                    self.rect(x, y, img_w, img_h + 8)
                    
                    self.set_font('helvetica', 'B', 5)
                    self.set_xy(x + 1, y + 1)
                    self.cell(img_w - 2, 3, self.clean_text(label), align='C')
                    
                    try:
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], path)
                        if os.path.exists(filepath):
                            self.image(filepath, x=x+2, y=y+4, w=img_w-4, h=img_h-6)
                    except:
                        self.set_font('helvetica', 'I', 6)
                        self.set_xy(x+2, y+15)
                        self.cell(img_w-4, 5, '[File tidak tersedia]', align='C')
                    
                    x += img_w + gap
                
                self.set_y(y + img_h + 10)
        else:
            self.ln(3)
            self.set_font('helvetica', 'I', 7)
            self.set_text_color(148, 163, 184)
            self.cell(0, 5, 'Tidak ada foto bukti dilampirkan.', align='C')

class BBMReportPDF(FPDF):
    """PDF Rekap - dengan tanda tangan dan ukuran proporsional"""
    
    def __init__(self, title="BBM VOUCHER PERIODE"):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font('helvetica', '', 10)
    
    def clean_text(self, text):
        """Hapus karakter yang tidak didukung"""
        if not text:
            return ""
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        return text.strip()
    
    def header(self):
        self.set_font('helvetica', 'B', 14)
        clean_title = self.clean_text(self.title)
        self.cell(0, 10, clean_title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
    
    def generate_table(self, data):
        if not data:
            self.set_font('helvetica', 'I', 12)
            self.cell(0, 10, "Tidak ada data untuk ditampilkan", align="C")
            return
        
        self.set_font('helvetica', 'B', 7)
        headers = ['NO', 'TANGGAL', 'NO POLISI', 'AMOUNT', 'KM ISI BBM', 
                   'KM AWAL', 'KM AKHIR', 'TOTAL KM', 'JAM', 'RATA-RATA KM', 'DRIVER', 'LITER']
        widths = [8, 22, 26, 26, 22, 22, 22, 18, 15, 22, 38, 16]
        
        self.set_fill_color(200, 200, 200)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('helvetica', '', 7)
        fill = False
        for idx, tx in enumerate(data, 1):
            if fill:
                self.set_fill_color(240, 240, 240)
            else:
                self.set_fill_color(255, 255, 255)
            
            jam = tx['created_at'].strftime('%H:%M') if tx.get('created_at') else '-'
            
            self.cell(widths[0], 6, str(idx), border=1, align='C', fill=fill)
            self.cell(widths[1], 6, tx['created_at'].strftime('%d %b %Y') if tx.get('created_at') else '-', border=1, align='C', fill=fill)
            self.cell(widths[2], 6, self.clean_text(str(tx['nopol'])), border=1, align='C', fill=fill)
            self.cell(widths[3], 6, f"Rp {tx['nominal']:,.0f}" if tx.get('nominal') else 'Rp 0', border=1, align='R', fill=fill)
            self.cell(widths[4], 6, f"{tx['odo_km']:,}" if tx.get('odo_km') else '0', border=1, align='C', fill=fill)
            self.cell(widths[5], 6, f"{tx.get('km_awal', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[6], 6, f"{tx.get('km_akhir', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[7], 6, f"{tx.get('total_km', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[8], 6, jam, border=1, align='C', fill=fill)
            self.cell(widths[9], 6, f"{tx.get('rata_rata', 0):.2f}", border=1, align='C', fill=fill)
            self.cell(widths[10], 6, self.clean_text(str(tx['driver_name']).upper() if tx.get('driver_name') else '-'), border=1, fill=fill)
            self.cell(widths[11], 6, str(tx.get('liter', 0)), border=1, align='C', fill=fill)
            self.ln()
            fill = not fill

# ============================================================
# ROUTES - DRIVER
# ============================================================
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
            liter = nominal / price_per_liter if price_per_liter > 0 else 0
            odo_km = int(request.form.get('odo_km', 0))
            jumlah_appointment = int(request.form.get('jumlah_appointment', 0) or 0)
            spbu_type = request.form.get('spbu_type', 'rekanan')
            gps_lat = request.form.get('gps_lat')
            gps_lon = request.form.get('gps_lon')
            gps_address = request.form.get('gps_address', '')
            
            # Validasi: ambil data driver dari database
            conn = get_db_connection()
            if not conn:
                flash('Database error!', 'error')
                return render_template('driver.html')
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM drivers WHERE name = %s AND is_active = TRUE", (driver_name,))
            driver_data = cursor.fetchone()
            
            if driver_data:
                # Override dengan data master
                nopol = driver_data['nopol']
                vehicle_type = driver_data['vehicle_type']
                bbm_type = driver_data['bbm_type']
            
            # Validasi BBM untuk kendaraan
            validation = validate_bbm_for_vehicle(vehicle_type, bbm_type)
            if not validation['valid']:
                flash('BBM ' + bbm_type + ' tidak tersedia untuk ' + vehicle_type, 'error')
                cursor.close()
                conn.close()
                return render_template('driver.html')
            
            if not driver_name or not nopol or nominal <= 0 or odo_km <= 0:
                flash('Semua field harus diisi dengan benar!', 'error')
                cursor.close()
                conn.close()
                return render_template('driver.html')
            
            foto_odo_sebelum = save_file(request.files.get('foto_odo_sebelum'), 'ODO1', nopol)
            foto_nota_odo_sesudah = save_file(request.files.get('foto_nota_odo_sesudah'), 'ODO2', nopol)
            foto_struk = save_file(request.files.get('foto_struk'), 'STRUK', nopol)
            foto_struk_dispenser = save_file(request.files.get('foto_struk_dispenser'), 'DISP', nopol) if spbu_type == 'non_rekanan' else None
            
            cursor.execute("""
                SELECT odo_km FROM transactions 
                WHERE nopol = %s AND status = 'verified_ga' 
                ORDER BY created_at DESC LIMIT 1
            """, (nopol,))
            previous = cursor.fetchone()
            
            km_per_liter = 0
            if previous and previous['odo_km'] < odo_km and liter > 0:
                km_per_liter = (odo_km - previous['odo_km']) / liter
            
            analysis = PerformanceAnalyzer.analyze_performance(
                nopol, km_per_liter, conn, vehicle_type, bbm_type
            )
            
            cursor.execute("""
                INSERT INTO transactions 
                (driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                 odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                 status, ml_anomaly_flag, km_per_liter, gps_latitude, gps_longitude, gps_address, jumlah_appointment) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s, %s, %s, %s)
            """, (driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                  odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                  analysis['is_anomaly'], km_per_liter, gps_lat, gps_lon, gps_address, jumlah_appointment))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            
            log_activity_async(transaction_id, 'create', 'driver', driver_name, 
                              ip=request.remote_addr, ua=request.headers.get('User-Agent'))
            
            cursor.close()
            conn.close()
            
            flash('Klaim #' + str(transaction_id) + ' berhasil! ' + analysis['message'], 'success')
            return redirect(url_for('driver_form'))
            
        except Exception as e:
            print(f"Driver form error: {e}")
            import traceback
            traceback.print_exc()
            flash('Error: ' + str(e), 'error')
            return render_template('driver.html')
    
    return render_template('driver.html')

# ============================================================
# ROUTES - ADMIN VERIFICATION
# ============================================================
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        try:
            action = request.form.get('action', 'verify')
            tx_id = request.form.get('tx_id')
            nopol = request.form.get('nopol', '')
            nominal = request.form.get('nominal', 0)
            
            if action == 'verify':
                is_error = request.form.get('mypertamina_error') == 'on'
                foto_mypertamina = save_file(request.files.get('foto_mypertamina'), 'ADMIN_MYPTM', nopol)
                kronologis = None

                if is_error:
                    waktu_sekarang = datetime.now().strftime("%d-%m-%Y %H:%M")
                    kronologis = (f"KRONOLOGIS OTOMATIS: Pada {waktu_sekarang}, diverifikasi bahwa klaim BBM kendaraan {nopol} "
                                  f"senilai Rp {nominal} sah. Mutasi di MyPertamina tidak muncul/error.")

                conn = get_db_connection()
                if not conn:
                    flash('Database error!', 'error')
                    return redirect(url_for('admin_dashboard'))
                
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE transactions 
                    SET is_mypertamina_error=%s, kronologis_text=%s, foto_mypertamina_admin=%s, status='verified',
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=%s
                """, (is_error, kronologis, foto_mypertamina, tx_id))
                conn.commit()
                
                cursor.execute("SELECT vehicle_type, liter, nominal, odo_km, km_per_liter FROM transactions WHERE id=%s", (tx_id,))
                tx_data = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if tx_data:
                    update_daily_summary_async({
                        'vehicle_type': tx_data[0],
                        'liter': tx_data[1],
                        'nominal': tx_data[2],
                        'odo_km': tx_data[3],
                        'km_per_liter': tx_data[4] or 0
                    })
                
                log_activity_async(int(tx_id), 'verify', 'admin', 'Admin', 
                                  ip=request.remote_addr, ua=request.headers.get('User-Agent'))
                
                flash('✅ Klaim berhasil diverifikasi!', 'success')
                
            elif action == 'modify':
                new_vehicle = request.form.get('edit_vehicle')
                new_bbm = request.form.get('edit_bbm')
                new_nominal = request.form.get('edit_nominal')
                new_odo = request.form.get('edit_odo')
                new_spbu = request.form.get('edit_spbu')
                modification_note = request.form.get('modification_note', '')
                
                conn = get_db_connection()
                if not conn:
                    flash('Database error!', 'error')
                    return redirect(url_for('admin_dashboard'))
                
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("SELECT * FROM transactions WHERE id=%s", (tx_id,))
                old_data = cursor.fetchone()
                
                cursor.execute("""
                    UPDATE transactions 
                    SET vehicle_type = %s, bbm_type = %s, nominal = %s, 
                        odo_km = %s, spbu_type = %s, status = 'modified',
                        modified_by = 'Admin', modification_note = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_vehicle, new_bbm, new_nominal, new_odo, new_spbu, modification_note, tx_id))
                conn.commit()
                cursor.close()
                conn.close()
                
                log_activity_async(int(tx_id), 'modify', 'admin', 'Admin', 
                                  old_data=old_data, 
                                  new_data={'vehicle_type': new_vehicle, 'bbm_type': new_bbm, 
                                           'nominal': new_nominal, 'odo_km': new_odo},
                                  ip=request.remote_addr, ua=request.headers.get('User-Agent'))
                
                flash('✅ Data transaksi berhasil dimodifikasi! Silakan verifikasi ulang.', 'success')

            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            print(f"Admin POST error: {e}")
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))

    try:
        conn = get_db_connection()
        if not conn:
            return "Database tidak tersedia", 500
        
        cursor = conn.cursor(dictionary=True)
        tab = request.args.get('tab', 'ga_queue')
        if tab == 'finance':
            cursor.execute("SELECT * FROM transactions WHERE status = 'verified_ga' ORDER BY created_at ASC")
        elif tab == 'driver_confirm':
            cursor.execute("SELECT * FROM transactions WHERE status = 'os_finance' ORDER BY created_at ASC")
        elif tab == 'archive':
            cursor.execute("SELECT * FROM transactions WHERE status = 'archived' ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM transactions WHERE status IN ('pending', 'modified') ORDER BY created_at ASC")
        pending_txs = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        total = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as pending FROM transactions WHERE status IN ('pending', 'modified')")
        pending_count = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as verified_ga FROM transactions WHERE status = 'verified_ga'")
        verified_ga = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as os_finance FROM transactions WHERE status = 'os_finance'")
        os_finance = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as archived FROM transactions WHERE status = 'archived'")
        archived = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as anomaly FROM transactions WHERE ml_anomaly_flag = TRUE")
        anomaly = cursor.fetchone()
        
        cursor.execute("SELECT vehicle_type FROM vehicles WHERE is_active = TRUE")
        vehicles = cursor.fetchall()
        
        cursor.execute("SELECT name FROM bbm_types WHERE is_active = TRUE")
        bbm_types = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        stats = {
            'total': total['total'] if total else 0,
            'pending': pending_count['pending'] if pending_count else 0,
            'verified_ga': verified_ga['verified_ga'] if verified_ga else 0,
            'os_finance': os_finance['os_finance'] if os_finance else 0,
            'archived': archived['archived'] if archived else 0,
            'anomaly': anomaly['anomaly'] if anomaly else 0,
            'tab': tab
        }
        
        return render_template('admin.html', 
                             transactions=pending_txs, 
                             stats=stats,
                             vehicles=vehicles,
                             bbm_types=bbm_types)
    except Exception as e:
        print(f"Admin GET error: {e}")
        return f"Error loading admin dashboard: {str(e)}", 500

# ============================================================
# ROUTES - RIWAYAT & REPORT (TANPA TANDA TANGAN)
# ============================================================
@app.route('/admin/riwayat')
def admin_riwayat():
    return redirect(url_for('admin_rekap'))

@app.route('/admin/report/<int:tx_id>')
def generate_report(tx_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE id=%s", (tx_id,))
        tx = cursor.fetchone()

        if not tx:
            return "Data tidak ditemukan", 404

        cursor.execute("UPDATE transactions SET is_reported=TRUE WHERE id=%s", (tx_id,))
        conn.commit()
        cursor.close()
        conn.close()

        pdf = PDFReportCompact()
        pdf.add_page()
        pdf.generate_compact_report(tx)

        pdf_filename = f"Report_BBM_{tx['nopol']}_{tx['id']}.pdf"
        pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf_out = pdf.output(dest='S')
        pdf_bytes = pdf_out.encode('latin-1') if isinstance(pdf_out, str) else bytes(pdf_out)
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=' + str(pdf_filename)
        return response
    except Exception as e:
        print(f"PDF Error: {e}")
        return f"Error generating PDF: {str(e)}", 500

# ============================================================
# ROUTES - REKAP (DENGAN TANDA TANGAN & FIX DOWNLOAD)
# ============================================================
@app.route('/admin/rekap')
def admin_rekap():
    try:
        filters = {
            'start_date': request.args.get('start_date', ''),
            'end_date': request.args.get('end_date', ''),
            'nopol': request.args.get('nopol', ''),
            'driver': request.args.get('driver', '')
        }
        
        txs = get_rekap_data(
            start_date=filters['start_date'] if filters['start_date'] else None,
            end_date=filters['end_date'] if filters['end_date'] else None,
            nopol=filters['nopol'] if filters['nopol'] else None,
            driver=filters['driver'] if filters['driver'] else None
        )
        
        return render_template('rekap.html', transactions=txs, filters=filters)
    except Exception as e:
        print(f"Rekap error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/admin/rekap/pdf')
def rekap_pdf():
    try:
        filters = {
            'start_date': request.args.get('start_date', ''),
            'end_date': request.args.get('end_date', ''),
            'nopol': request.args.get('nopol', ''),
            'driver': request.args.get('driver', '')
        }
        
        data = get_rekap_data(
            start_date=filters['start_date'] if filters['start_date'] else None,
            end_date=filters['end_date'] if filters['end_date'] else None,
            nopol=filters['nopol'] if filters['nopol'] else None,
            driver=filters['driver'] if filters['driver'] else None
        )
        
        if not data:
            flash('Tidak ada data untuk periode yang dipilih', 'warning')
            return redirect(url_for('admin_rekap'))
        
        title = "BBM VOUCHER PERIODE"
        if filters['start_date'] or filters['end_date']:
            start = filters['start_date'] or 'AWAL'
            end = filters['end_date'] or 'AKHIR'
            title += f" {start} - {end}"
        
        pdf = BBMReportPDF(title=title)
        pdf.add_page()
        pdf.generate_table(data)
        
        # ===== TANDA TANGAN =====
        pdf.ln(8)
        pdf.set_font('helvetica', '', 10)
        
        # Tanda tangan
        pdf.cell(130, 5, "")
        pdf.cell(60, 5, "Dibuat Oleh,", align="C")
        pdf.cell(60, 5, "Disetujui Oleh,", align="C", ln=True)
        pdf.ln(18)
        pdf.cell(130, 5, "")
        pdf.cell(60, 5, "( Finance )", align="C")
        pdf.cell(60, 5, "( Branch Manager )", align="C")
        
        # ===== GENERATE PDF =====
        is_download = request.args.get('dl') == '1'
        
        # Gunakan output dengan buffer untuk memastikan file lengkap
        pdf_output = pdf.output(dest='S')
        
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Length'] = len(pdf_output)
        
        if is_download:
            response.headers['Content-Disposition'] = 'attachment; filename=Rekap_BBM.pdf'
        else:
            response.headers['Content-Disposition'] = 'inline; filename=Rekap_BBM.pdf'
        
        return response
        
    except Exception as e:
        print(f"PDF Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error generating PDF: {str(e)}", 500

# ============================================================
# ROUTES - ANALYTICS
# ============================================================
@app.route('/admin/analytics')
def admin_analytics():
    try:
        conn = get_db_connection()
        if not conn:
            return "Database error", 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT t.nopol, t.vehicle_type, t.bbm_type,
                   AVG(t.km_per_liter) as avg_km_per_liter,
                   COUNT(*) as total_transactions,
                   MAX(t.created_at) as last_transaction,
                   MIN(t.created_at) as first_transaction,
                   vba.good_km_per_liter, vba.warning_km_per_liter
            FROM transactions t
            JOIN vehicle_bbm_allowed vba ON t.vehicle_type = vba.vehicle_type AND t.bbm_type = vba.bbm_type
            WHERE t.status IN ('archived', 'os_finance', 'verified_ga')
            GROUP BY t.nopol, t.vehicle_type, t.bbm_type, vba.good_km_per_liter, vba.warning_km_per_liter
            HAVING COUNT(*) >= 1
            ORDER BY avg_km_per_liter DESC
        """)
        vehicle_performance = cursor.fetchall()
        
        if not vehicle_performance:
            cursor.execute("""
                SELECT t.nopol, t.vehicle_type, t.bbm_type,
                       AVG(t.km_per_liter) as avg_km_per_liter,
                       COUNT(*) as total_transactions,
                       MAX(t.created_at) as last_transaction,
                       MIN(t.created_at) as first_transaction,
                       vba.good_km_per_liter, vba.warning_km_per_liter
                FROM transactions t
                JOIN vehicle_bbm_allowed vba ON t.vehicle_type = vba.vehicle_type AND t.bbm_type = vba.bbm_type
                WHERE t.status IN ('archived', 'os_finance', 'verified_ga')
                GROUP BY t.nopol, t.vehicle_type, t.bbm_type, vba.good_km_per_liter, vba.warning_km_per_liter
                ORDER BY avg_km_per_liter DESC
            """)
            vehicle_performance = cursor.fetchall()
        
        cursor.execute("""
            SELECT DATE(created_at) as date, 
                   AVG(km_per_liter) as avg_efficiency,
                   COUNT(*) as transactions
            FROM transactions 
            WHERE status IN ('archived', 'os_finance', 'verified_ga')
            GROUP BY DATE(created_at)
            ORDER BY date DESC LIMIT 30
        """)
        daily_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('analytics.html', 
                             vehicle_performance=vehicle_performance,
                             daily_stats=daily_stats)
    except Exception as e:
        print(f"Analytics error: {e}")
        return f"Error: {str(e)}", 500

# ============================================================
# ROUTES - SETTINGS
# ============================================================
@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database error!', 'error')
                return redirect(url_for('admin_settings'))
            
            cursor = conn.cursor()
            
            # Vehicles
            vehicle_ids = request.form.getlist('vehicle_id[]')
            vehicle_names = request.form.getlist('vehicle_name[]')
            vehicle_brands = request.form.getlist('vehicle_brand[]')
            vehicle_capacities = request.form.getlist('vehicle_capacity[]')
            vehicle_active = request.form.getlist('vehicle_active[]')
            
            for i in range(len(vehicle_ids)):
                if vehicle_ids[i]:
                    active = 1 if str(i) in vehicle_active else 0
                    cursor.execute("""
                        UPDATE vehicles 
                        SET vehicle_type = %s, brand = %s, fuel_capacity = %s, is_active = %s
                        WHERE id = %s
                    """, (vehicle_names[i], vehicle_brands[i], vehicle_capacities[i], active, vehicle_ids[i]))
            
            new_vehicles = request.form.getlist('new_vehicle_name[]')
            new_brands = request.form.getlist('new_vehicle_brand[]')
            new_capacities = request.form.getlist('new_vehicle_capacity[]')
            
            for i in range(len(new_vehicles)):
                if new_vehicles[i]:
                    cursor.execute("""
                        INSERT INTO vehicles (vehicle_type, brand, fuel_capacity, is_active) 
                        VALUES (%s, %s, %s, 1)
                    """, (new_vehicles[i], new_brands[i] if i < len(new_brands) else 'Toyota', 
                          new_capacities[i] if i < len(new_capacities) else 45))
            
            # BBM Types
            bbm_ids = request.form.getlist('bbm_id[]')
            bbm_names = request.form.getlist('bbm_name[]')
            bbm_prices = request.form.getlist('bbm_price[]')
            bbm_active = request.form.getlist('bbm_active[]')
            
            for i in range(len(bbm_ids)):
                if bbm_ids[i]:
                    active = 1 if str(i) in bbm_active else 0
                    cursor.execute("""
                        UPDATE bbm_types 
                        SET name = %s, price_per_liter = %s, is_active = %s 
                        WHERE id = %s
                    """, (bbm_names[i], bbm_prices[i], active, bbm_ids[i]))
            
            new_bbm_names = request.form.getlist('new_bbm_name[]')
            new_bbm_prices = request.form.getlist('new_bbm_price[]')
            
            for i in range(len(new_bbm_names)):
                if new_bbm_names[i] and new_bbm_prices[i]:
                    cursor.execute("""
                        INSERT INTO bbm_types (name, price_per_liter, is_active) 
                        VALUES (%s, %s, 1)
                    """, (new_bbm_names[i], new_bbm_prices[i]))
            
            # Vehicle-BBM Limits
            limit_ids = request.form.getlist('limit_id[]')
            limit_vehicles = request.form.getlist('limit_vehicle[]')
            limit_bbm = request.form.getlist('limit_bbm[]')
            limit_good = request.form.getlist('limit_good[]')
            limit_warning = request.form.getlist('limit_warning[]')
            limit_min = request.form.getlist('limit_min[]')
            limit_max = request.form.getlist('limit_max[]')
            limit_default = request.form.getlist('limit_default[]')
            
            for i in range(len(limit_ids)):
                if limit_ids[i]:
                    is_default = 1 if str(i) in limit_default else 0
                    cursor.execute("""
                        UPDATE vehicle_bbm_allowed 
                        SET good_km_per_liter = %s, warning_km_per_liter = %s,
                            min_km_per_liter = %s, max_km_per_liter = %s,
                            is_default = %s
                        WHERE id = %s
                    """, (limit_good[i], limit_warning[i], limit_min[i], limit_max[i], 
                          is_default, limit_ids[i]))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('✅ Settings berhasil diperbarui!', 'success')
        except Exception as e:
            print(f"Settings error: {e}")
            flash(f'Error: {str(e)}', 'error')
    
    try:
        conn = get_db_connection()
        if not conn:
            return "Database error", 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicles ORDER BY vehicle_type")
        vehicles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM bbm_types ORDER BY name")
        bbm_types = cursor.fetchall()
        
        cursor.execute("""
            SELECT vba.*, bt.price_per_liter 
            FROM vehicle_bbm_allowed vba
            JOIN bbm_types bt ON vba.bbm_type = bt.name
            ORDER BY vba.vehicle_type, vba.bbm_type
        """)
        vehicle_limits = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('settings.html', 
                             vehicles=vehicles,
                             bbm_types=bbm_types,
                             vehicle_limits=vehicle_limits)
    except Exception as e:
        print(f"Settings GET error: {e}")
        return f"Error: {str(e)}", 500

# ============================================================
# ROUTES - UNVERIFY & DELETE
# ============================================================
@app.route('/admin/unverify/<int:tx_id>')
def unverify_tx(tx_id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status = 'pending' WHERE id = %s", (tx_id,))
            conn.commit()
            log_activity_async(tx_id, 'unverify', 'admin', 'Admin', ip=request.remote_addr)
            cursor.close()
            conn.close()
            flash('✅ Transaksi dikembalikan ke Pending', 'success')
    except Exception as e:
        print(f"Unverify error: {e}")
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin_rekap'))

@app.route('/admin/delete/<int:tx_id>')
def delete_tx(tx_id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = %s", (tx_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash('🗑️ Transaksi berhasil dihapus', 'warning')
    except Exception as e:
        print(f"Delete error: {e}")
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin_rekap'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/api/get-feedback/<nopol>', methods=['GET'])
def get_vehicle_feedback(nopol):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT odo_km, liter, km_per_liter, jumlah_appointment, created_at "
            "FROM transactions "
            "WHERE nopol=%s AND status IN ('archived', 'os_finance', 'verified_ga') "
            "ORDER BY created_at DESC LIMIT 10",
            (nopol,)
        )
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        if not data:
            return jsonify({
                "status": "info",
                "nopol": nopol,
                "msg": f"Belum ada data untuk analisis kendaraan {nopol}."
            })

        km_values = [d['km_per_liter'] for d in data if d['km_per_liter'] and d['km_per_liter'] > 0]
        if not km_values:
            return jsonify({
                "status": "info",
                "nopol": nopol,
                "msg": f"Data KM/liter untuk {nopol} belum lengkap."
            })

        avg_kpl = sum(km_values) / len(km_values)
        total_apt = sum([d.get('jumlah_appointment', 0) or 0 for d in data])

        if avg_kpl >= 12:
            performa = "SANGAT BAIK"
        elif avg_kpl >= 10:
            performa = "BAIK"
        elif avg_kpl >= 8:
            performa = "CUKUP"
        else:
            performa = "BOROS"

        return jsonify({
            "status": "success",
            "nopol": nopol,
            "avg_km_per_liter": round(avg_kpl, 2),
            "total_data": len(km_values),
            "total_appointment": total_apt,
            "performa": performa,
            "msg": f"Performa {nopol}: {performa} (Rata-rata {avg_kpl:.2f} KM/L)"
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500




# ============================================================
# ROUTES - GA APPROVAL
# ============================================================
@app.route('/ga/approve/<int:tx_id>')
def ga_approve(tx_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database error!', 'error')
            return redirect(url_for('admin_dashboard'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE id = %s AND status IN ('pending', 'modified')", (tx_id,))
        tx = cursor.fetchone()
        
        if not tx:
            flash('Transaksi tidak ditemukan atau sudah diproses!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        
        admin_name = request.args.get('admin', 'GA Officer')
        
        cursor.execute(
            "UPDATE transactions SET status = 'verified_ga', ga_approved_by = %s, ga_approved_at = NOW(), approved_by_user = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (admin_name, admin_name, tx_id)
        )
        conn.commit()
        
        log_activity_async(tx_id, 'ga_approve', 'ga', admin_name, ip=request.remote_addr, ua=request.headers.get('User-Agent'))
        
        cursor.close()
        conn.close()
        
        flash('Klaim #' + str(tx_id) + ' (' + tx['nopol'] + ') disetujui oleh GA! Siap diajukan ke Finance.', 'success')
    except Exception as e:
        print(f"GA Approve error: {e}")
        flash('Error: ' + str(e), 'error')
    
    return redirect(url_for('admin_dashboard', tab='ga_queue'))


# ============================================================
# ROUTES - FINANCE PAYOUT
# ============================================================
@app.route('/finance/payout/<int:tx_id>')
def finance_payout(tx_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database error!', 'error')
            return redirect(url_for('admin_dashboard'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE id = %s AND status = 'verified_ga'", (tx_id,))
        tx = cursor.fetchone()
        
        if not tx:
            flash('Transaksi tidak ditemukan atau belum disetujui GA!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        
        admin_name = request.args.get('admin', 'Finance Officer')
        
        cursor.execute(
            "UPDATE transactions SET status = 'os_finance', finance_payout_by = %s, finance_payout_at = NOW(), payout_by_user = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (admin_name, admin_name, tx_id)
        )
        conn.commit()
        
        log_activity_async(tx_id, 'finance_payout', 'finance', admin_name, ip=request.remote_addr, ua=request.headers.get('User-Agent'))
        
        cursor.close()
        conn.close()
        
        flash('Dana klaim #' + str(tx_id) + ' (' + tx['nopol'] + ') sudah dikeluarkan! Menunggu tanda tangan Driver.', 'success')
    except Exception as e:
        print(f"Finance Payout error: {e}")
        flash('Error: ' + str(e), 'error')
    
    return redirect(url_for('admin_dashboard', tab='finance'))


# ============================================================
# ROUTES - FINANCE ARCHIVE (Driver sudah TTD)
# ============================================================
@app.route('/finance/archive/<int:tx_id>')
def finance_archive(tx_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database error!', 'error')
            return redirect(url_for('admin_dashboard'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE id = %s AND status = 'os_finance'", (tx_id,))
        tx = cursor.fetchone()
        
        if not tx:
            flash('Transaksi tidak ditemukan atau belum dalam status OS!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        
        admin_name = request.args.get('admin', 'Finance Officer')
        
        cursor.execute(
            "UPDATE transactions SET status = 'archived', archived_by = %s, archived_at = NOW(), archived_by_user = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (admin_name, admin_name, tx_id)
        )
        conn.commit()
        
        log_activity_async(tx_id, 'archive', 'finance', admin_name, ip=request.remote_addr, ua=request.headers.get('User-Agent'))
        
        cursor.close()
        conn.close()
        
        flash('Klaim #' + str(tx_id) + ' (' + tx['nopol'] + ') sudah diarsipkan!', 'success')
    except Exception as e:
        print(f"Archive error: {e}")
        flash('Error: ' + str(e), 'error')
    
    return redirect(url_for('admin_dashboard', tab='driver_confirm'))


# ============================================================
# ROUTES - REJECT
# ============================================================
@app.route('/admin/reject/<int:tx_id>', methods=['POST'])
def reject_tx(tx_id):
    try:
        reason = request.form.get('rejection_reason', 'Tidak ada alasan')
        rejected_by = request.form.get('rejected_by', 'Admin')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET status = 'rejected', rejection_reason = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (reason, tx_id)
            )
            conn.commit()
            
            log_activity_async(tx_id, 'reject', 'admin', rejected_by, new_data={'reason': reason}, ip=request.remote_addr, ua=request.headers.get('User-Agent'))
            
            cursor.close()
            conn.close()
            flash('Transaksi ditolak: ' + reason, 'warning')
    except Exception as e:
        print(f"Reject error: {e}")
        flash('Error: ' + str(e), 'error')
    
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ROUTES - DOWNLOAD ARCHIVE BUNDLE (ZIP)
# ============================================================
@app.route('/finance/download-archive/<int:tx_id>')
def download_archive(tx_id):
    try:
        import zipfile
        from io import BytesIO
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
        tx = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not tx:
            return "Transaksi tidak ditemukan", 404
        
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            foto_fields = [
                ('foto_odo_sebelum', '01_ODO_Sebelum'),
                ('foto_nota_odo_sesudah', '02_ODO_Nota'),
                ('foto_struk', '03_Struk_BBM'),
                ('foto_struk_dispenser', '04_Struk_Dispenser'),
                ('foto_mypertamina_admin', '05_MyPertamina'),
            ]
            
            files_added = 0
            for field, label in foto_fields:
                filename = tx.get(field)
                if filename:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(filepath):
                        ext = os.path.splitext(filename)[1]
                        zf.write(filepath, label + '_' + str(tx['nopol']) + ext)
                        files_added += 1
            
            info_text = "ARSIP KLAIM BBM #" + str(tx['id']) + "\n"
            info_text += "===============================\n"
            info_text += "Nopol: " + str(tx['nopol']) + "\n"
            info_text += "Driver: " + str(tx['driver_name']) + "\n"
            info_text += "Kendaraan: " + str(tx['vehicle_type']) + "\n"
            info_text += "BBM: " + str(tx.get('bbm_type', '-')) + "\n"
            info_text += "Nominal: Rp " + '{:,.0f}'.format(tx['nominal']) + "\n"
            info_text += "Liter: " + str(tx['liter']) + " L\n"
            info_text += "ODO: " + str(tx['odo_km']) + " km\n"
            info_text += "SPBU: " + str(tx.get('spbu_type', '-')) + "\n"
            info_text += "Tanggal: " + str(tx['created_at']) + "\n"
            info_text += "GA Approved: " + str(tx.get('ga_approved_by', '-')) + "\n"
            info_text += "Finance Payout: " + str(tx.get('finance_payout_by', '-')) + "\n"
            info_text += "Archived: " + str(tx.get('archived_by', '-')) + "\n"
            
            zf.writestr('INFO_Transaksi_' + str(tx['nopol']) + '_' + str(tx['id']) + '.txt', info_text)
            files_added += 1
            
            if files_added == 0:
                return "Tidak ada file bukti untuk diarsipkan", 404
        
        memory_file.seek(0)
        
        response = make_response(memory_file.read())
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; filename=Archive_BBM_' + str(tx['nopol']) + '_' + str(tx['id']) + '.zip'
        return response
        
    except Exception as e:
        print(f"Download archive error: {e}")
        import traceback
        traceback.print_exc()
        return "Error: " + str(e), 500



# ============================================================
# ROUTES - DRIVER ASSIGNMENTS MANAGEMENT
# ============================================================
@app.route('/admin/assignments', methods=['GET', 'POST'])
def admin_assignments():
    if request.method == 'POST':
        try:
            action = request.form.get('action', 'add')
            conn = get_db_connection()
            if not conn:
                flash('Database error!', 'error')
                return redirect(url_for('admin_assignments'))
            
            cursor = conn.cursor()
            
            if action == 'add':
                driver_name = request.form.get('driver_name', '').strip().upper()
                nopol = request.form.get('nopol', '').strip().upper()
                vehicle_type = request.form.get('vehicle_type', 'AVANZA')
                bbm_type = request.form.get('bbm_type', 'PERTALITE')
                
                if driver_name and nopol:
                    cursor.execute("""
                        INSERT INTO driver_assignments (driver_name, nopol, vehicle_type, bbm_type)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE vehicle_type=%s, bbm_type=%s, is_active=TRUE
                    """, (driver_name, nopol, vehicle_type, bbm_type, vehicle_type, bbm_type))
                    conn.commit()
                    flash('Assignment berhasil ditambahkan!', 'success')
            
            elif action == 'toggle':
                assign_id = request.form.get('assign_id')
                is_active = request.form.get('is_active') == '1'
                cursor.execute("UPDATE driver_assignments SET is_active = %s WHERE id = %s", (is_active, assign_id))
                conn.commit()
                flash('Status assignment diubah!', 'success')
            
            elif action == 'delete':
                assign_id = request.form.get('assign_id')
                cursor.execute("DELETE FROM driver_assignments WHERE id = %s", (assign_id,))
                conn.commit()
                flash('Assignment dihapus!', 'warning')
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Assignments error: {e}")
            flash('Error: ' + str(e), 'error')
        
        return redirect(url_for('admin_assignments'))
    
    # GET
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM driver_assignments ORDER BY is_active DESC, driver_name")
        assignments = cursor.fetchall()
        
        cursor.execute("SELECT vehicle_type FROM vehicles WHERE is_active = TRUE")
        vehicles = cursor.fetchall()
        
        cursor.execute("SELECT name FROM bbm_types WHERE is_active = TRUE")
        bbm_types = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('assignments.html', assignments=assignments, vehicles=vehicles, bbm_types=bbm_types)
    except Exception as e:
        print(f"Assignments GET error: {e}")
        return f"Error: {str(e)}", 500



# ============================================================
# API - SYNC DRIVER DATA
# ============================================================
@app.route('/api/drivers/sync', methods=['POST'])
def sync_driver():
    try:
        data = request.get_json()
        driver_name = data.get('driver_name', '').strip().upper()
        nopol = data.get('nopol', '').strip().upper()
        vehicle_type = data.get('vehicle_type', 'AVANZA')
        bbm_type = data.get('bbm_type', 'PERTALITE')
        
        if not driver_name or not nopol:
            return jsonify({'status': 'error', 'msg': 'Driver name and nopol required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO drivers (name, nopol, vehicle_type, bbm_type)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                nopol = VALUES(nopol),
                vehicle_type = VALUES(vehicle_type),
                bbm_type = VALUES(bbm_type),
                is_active = TRUE
        """, (driver_name, nopol, vehicle_type, bbm_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'msg': 'Driver ' + driver_name + ' synced'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/drivers/<driver_name>/deactivate', methods=['POST'])
def deactivate_driver(driver_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE drivers SET is_active = FALSE WHERE name = %s", (driver_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'msg': 'Driver ' + driver_name + ' deactivated'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500



# ============================================================
# API - VERIFY PIN (untuk GA/Finance approval)
# ============================================================
@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        pin = data.get('pin', '').strip()
        
        if not username or not pin:
            return jsonify({'status': 'error', 'msg': 'Username dan PIN wajib diisi'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND pin = %s AND is_active = TRUE", (username, pin))
        user = cursor.fetchone()
        
        if user:
            # Update last_login
            cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'success',
                'user': {'username': user['username'], 'full_name': user['full_name'], 'role': user['role']}
            })
        else:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'msg': 'PIN salah atau user tidak aktif'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

# ============================================================
# API - MANAGE USERS (untuk Settings)
# ============================================================
@app.route('/api/users', methods=['GET'])
def api_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, full_name, role, is_active, last_login FROM users ORDER BY role, username")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/sync', methods=['POST'])
def sync_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        full_name = data.get('full_name', '').strip()
        role = data.get('role', 'ga')
        pin = data.get('pin', '123456')
        is_active = data.get('is_active', True)
        
        if not username or not full_name:
            return jsonify({'status': 'error', 'msg': 'Username dan nama lengkap wajib'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, full_name, role, pin, is_active)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                full_name = VALUES(full_name),
                role = VALUES(role),
                pin = VALUES(pin),
                is_active = VALUES(is_active)
        """, (username, full_name, role, pin, is_active))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'msg': 'User ' + username + ' saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

