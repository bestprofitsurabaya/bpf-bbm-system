from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, make_response, flash
import os
import time
import json
import requests
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from fpdf import FPDF
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'bpf_bbm_secret_key_2026'
UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

DB_CONFIG = {
    'host': 'db',
    'user': 'root',
    'password': 'password_db',
    'database': 'bpf_asset_system'
}

# ============================================================
# VEHICLE SPECIFICATIONS (Default)
# ============================================================
VEHICLE_SPECS = {
    'AVANZA': {
        'fuel_capacity': 45,
        'efficiency_min': 5.0,
        'efficiency_max': 18.0,
        'efficiency_avg': 12,
        'efficiency_good': 12.5,
        'efficiency_warning': 10.5,
    },
    'INNOVA': {
        'fuel_capacity': 55,
        'efficiency_min': 4.0,
        'efficiency_max': 16.0,
        'efficiency_avg': 10,
        'efficiency_good': 10.5,
        'efficiency_warning': 8.5,
    }
}

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
# DATABASE FUNCTIONS
# ============================================================
def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error:
            retries -= 1
            time.sleep(3)
    return None

def save_file(file_obj, prefix, nopol):
    if file_obj and file_obj.filename:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{nopol}_{timestamp_str}_{file_obj.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        return filename
    return None

def get_bbm_types():
    """Ambil daftar jenis BBM dari database"""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_types WHERE is_active = TRUE ORDER BY name")
    types = cursor.fetchall()
    cursor.close()
    conn.close()
    return types

def get_vehicle_limit(vehicle_type, bbm_type):
    """Ambil batas konsumsi per kendaraan dan jenis BBM"""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM vehicle_fuel_limits 
        WHERE vehicle_type = %s AND bbm_type = %s
    """, (vehicle_type, bbm_type))
    limit = cursor.fetchone()
    cursor.close()
    conn.close()
    return limit

def get_all_vehicle_limits():
    """Ambil semua batas konsumsi"""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicle_fuel_limits ORDER BY vehicle_type, bbm_type")
    limits = cursor.fetchall()
    cursor.close()
    conn.close()
    return limits

def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=18&addressdetails=1"
        response = requests.get(url, headers={'User-Agent': 'BPF-BBM-System'}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'address' in data:
                addr = data['address']
                parts = []
                for key in ['road', 'village', 'town', 'city', 'county', 'state', 'country']:
                    if key in addr:
                        parts.append(addr[key])
                return ', '.join(parts) if parts else data.get('display_name', '')
    except:
        pass
    return f"{lat}, {lon}"

# ============================================================
# MACHINE LEARNING ANALYZER
# ============================================================
class ToyotaPerformanceAnalyzer:
    @staticmethod
    def analyze_performance(nopol, current_efficiency, conn, vehicle_type='AVANZA', bbm_type='PERTALITE'):
        # Ambil limit dari database
        limit = get_vehicle_limit(vehicle_type, bbm_type)
        if not limit:
            # Fallback ke default
            specs = VEHICLE_SPECS.get(vehicle_type, VEHICLE_SPECS['AVANZA'])
            good = specs['efficiency_good']
            warning = specs['efficiency_warning']
        else:
            good = float(limit['good_km_per_liter'])
            warning = float(limit['warning_km_per_liter'])
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT km_per_liter, liter, odo_km 
            FROM bbm_transactions 
            WHERE nopol = %s AND km_per_liter > 0 AND status = 'verified' 
            ORDER BY created_at DESC LIMIT 20
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
        elif current_efficiency > 18.0:
            status = 'PERLU PEMERIKSAAN (Data Tidak Normal)'
            category = 'warning'
            message = f'Efisiensi {current_efficiency:.1f} KM/L di atas maksimal'
            is_anomaly = True
        elif current_efficiency < good:
            status = 'CUKUP'
            category = 'warning'
            message = f'Efisiensi {current_efficiency:.1f} KM/L, perlu pemantauan'
        
        if len(history) >= 3:
            efficiency_data = [row['km_per_liter'] for row in history] + [current_efficiency]
            if len(efficiency_data) >= 4:
                X = np.array(efficiency_data).reshape(-1, 1)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                iso_forest = IsolationForest(contamination=0.15, random_state=42)
                predictions = iso_forest.fit_predict(X_scaled)
                
                if predictions[-1] == -1:
                    is_anomaly = True
                    status = 'ANOMALI DETEKSI ML'
                    category = 'danger'
                    message = 'ML mendeteksi anomali pada data ini'
        
        return {
            'is_anomaly': is_anomaly,
            'status': status,
            'category': category,
            'message': message,
            'vehicle_type': vehicle_type,
            'bbm_type': bbm_type,
            'current_efficiency': current_efficiency
        }

# ============================================================
# REKAP DATA ENGINE
# ============================================================
def get_rekap_data(start_date=None, end_date=None, nopol=None, driver=None):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT * FROM bbm_transactions 
        WHERE status = 'verified'
    """
    params = []
    
    if start_date:
        query += " AND DATE(created_at) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(created_at) <= %s"
        params.append(end_date)
    if nopol:
        query += " AND nopol LIKE %s"
        params.append(f"%{nopol}%")
    if driver:
        query += " AND driver_name LIKE %s"
        params.append(f"%{driver}%")
    
    query += " ORDER BY nopol ASC, created_at ASC"
    
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

# ============================================================
# PDF GENERATOR - FIXED
# ============================================================
class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "LAPORAN VERIFIKASI KLAIM BBM", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "PT. BESTPROFIT SURABAYA", new_x="LMARGIN", new_y="NEXT", align="C")
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Halaman {self.page_no()}", align="C")

class BBMReportPDF(FPDF):
    def __init__(self, title="BBM VOUCHER PERIODE"):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font('helvetica', '', 10)
    
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, self.title, align="C", new_x="LMARGIN", new_y="NEXT")
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
            self.cell(widths[2], 6, str(tx['nopol']), border=1, align='C', fill=fill)
            self.cell(widths[3], 6, f"Rp {tx['nominal']:,.0f}" if tx.get('nominal') else 'Rp 0', border=1, align='R', fill=fill)
            self.cell(widths[4], 6, f"{tx['odo_km']:,}" if tx.get('odo_km') else '0', border=1, align='C', fill=fill)
            self.cell(widths[5], 6, f"{tx.get('km_awal', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[6], 6, f"{tx.get('km_akhir', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[7], 6, f"{tx.get('total_km', 0):,}", border=1, align='C', fill=fill)
            self.cell(widths[8], 6, jam, border=1, align='C', fill=fill)
            self.cell(widths[9], 6, f"{tx.get('rata_rata', 0):.2f}", border=1, align='C', fill=fill)
            self.cell(widths[10], 6, str(tx['driver_name']).upper() if tx.get('driver_name') else '-', border=1, fill=fill)
            self.cell(widths[11], 6, str(tx.get('liter', 0)), border=1, align='C', fill=fill)
            self.ln()
            fill = not fill

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return redirect(url_for('driver_form'))

@app.route('/driver', methods=['GET', 'POST'])
def driver_form():
    bbm_types = get_bbm_types()
    
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
            spbu_type = request.form.get('spbu_type', 'rekanan')
            gps_lat = request.form.get('gps_lat')
            gps_lon = request.form.get('gps_lon')
            gps_address = request.form.get('gps_address', '')
            
            if not driver_name or not nopol or nominal <= 0 or odo_km <= 0:
                flash('Semua field harus diisi dengan benar!', 'error')
                return render_template('driver.html', bbm_types=bbm_types)
            
            foto_odo_sebelum = save_file(request.files.get('foto_odo_sebelum'), 'ODO1', nopol)
            foto_nota_odo_sesudah = save_file(request.files.get('foto_nota_odo_sesudah'), 'ODO2', nopol)
            foto_struk = save_file(request.files.get('foto_struk'), 'STRUK', nopol)
            foto_struk_dispenser = save_file(request.files.get('foto_struk_dispenser'), 'DISP', nopol) if spbu_type == 'non_rekanan' else None
            
            conn = get_db_connection()
            if not conn:
                flash('Database error!', 'error')
                return render_template('driver.html', bbm_types=bbm_types)
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT odo_km FROM bbm_transactions 
                WHERE nopol = %s AND status = 'verified' 
                ORDER BY created_at DESC LIMIT 1
            """, (nopol,))
            previous = cursor.fetchone()
            
            km_per_liter = 0
            if previous and previous['odo_km'] < odo_km and liter > 0:
                km_per_liter = (odo_km - previous['odo_km']) / liter
            
            analysis = ToyotaPerformanceAnalyzer.analyze_performance(
                nopol, km_per_liter, conn, vehicle_type, bbm_type
            )
            
            cursor.execute("""
                INSERT INTO bbm_transactions 
                (driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                 odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                 status, ml_anomaly_flag, km_per_liter, gps_latitude, gps_longitude, gps_address) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s, %s, %s)
            """, (driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter,
                  odo_km, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser,
                  analysis['is_anomaly'], km_per_liter, gps_lat, gps_lon, gps_address))
            
            conn.commit()
            conn.close()
            
            if analysis['is_anomaly']:
                flash(f"⚠️ {analysis['status']}: {analysis['message']}", 'warning')
            else:
                flash(f"✅ Klaim berhasil dikirim! {analysis['message']}", 'success')
            
            return redirect(url_for('driver_form'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('driver.html', bbm_types=bbm_types)
    
    return render_template('driver.html', bbm_types=bbm_types)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        tx_id = request.form.get('tx_id')
        nopol = request.form.get('nopol')
        nominal = request.form.get('nominal')
        is_error = request.form.get('mypertamina_error') == 'on'
        
        foto_mypertamina = save_file(request.files.get('foto_mypertamina'), 'ADMIN_MYPTM', nopol)
        kronologis = None

        if is_error:
            waktu_sekarang = datetime.now().strftime("%d-%m-%Y %H:%M")
            kronologis = (f"KRONOLOGIS OTOMATIS: Pada {waktu_sekarang}, diverifikasi bahwa klaim BBM kendaraan {nopol} "
                          f"senilai Rp {nominal} sah. Mutasi di MyPertamina tidak muncul/error. "
                          f"Verifikasi dilakukan berdasarkan bukti foto ODO dan Struk fisik.")

        conn = get_db_connection()
        if not conn:
            flash('Database error!', 'error')
            return redirect(url_for('admin_dashboard'))
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bbm_transactions 
            SET is_mypertamina_error=%s, kronologis_text=%s, foto_mypertamina_admin=%s, status='verified' 
            WHERE id=%s
        """, (is_error, kronologis, foto_mypertamina, tx_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('✅ Klaim berhasil diverifikasi!', 'success')
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    if not conn:
        return "Database tidak tersedia", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_transactions WHERE status='pending' ORDER BY created_at ASC")
    pending_txs = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total FROM bbm_transactions")
    total = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as verified FROM bbm_transactions WHERE status = 'verified'")
    verified = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as anomaly FROM bbm_transactions WHERE ml_anomaly_flag = TRUE")
    anomaly = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    stats = {
        'total': total['total'] if total else 0,
        'pending': len(pending_txs),
        'verified': verified['verified'] if verified else 0,
        'anomaly': anomaly['anomaly'] if anomaly else 0
    }
    
    return render_template('admin.html', transactions=pending_txs, stats=stats)

@app.route('/admin/riwayat')
def admin_riwayat():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_transactions WHERE status='verified' ORDER BY created_at DESC")
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('riwayat.html', transactions=transactions)

@app.route('/admin/report/<int:tx_id>')
def generate_report(tx_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bbm_transactions WHERE id=%s", (tx_id,))
        tx = cursor.fetchone()

        if not tx:
            return "Data tidak ditemukan", 404

        cursor.execute("UPDATE bbm_transactions SET is_reported=TRUE WHERE id=%s", (tx_id,))
        conn.commit()
        cursor.close()
        conn.close()

        pdf = PDFReport()
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        
        # Informasi Dasar
        items = [
            ("ID Transaksi", f"#{tx['id']}"),
            ("Tanggal Input", str(tx['created_at'])),
            ("Nopol Kendaraan", tx['nopol'].upper()),
            ("Driver", tx['driver_name']),
            ("Nominal Klaim", f"Rp {tx['nominal']:,}"),
            ("Volume", f"{tx['liter']} Liter"),
            ("Jenis BBM", tx.get('bbm_type', 'PERTALITE')),
            ("Harga/Liter", f"Rp {tx.get('price_per_liter', 10000):,}"),
            ("ODO KM", str(tx['odo_km'])),
            ("Tipe SPBU", str(tx['spbu_type']).replace('_', ' ').title()),
            ("GPS Lokasi", tx.get('gps_address', '') or f"{tx.get('gps_latitude', '')}, {tx.get('gps_longitude', '')}")
        ]
        
        for label, value in items:
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(50, 8, f" {label}", border=1, fill=True)
            pdf.set_font("helvetica", "", 11)
            pdf.cell(0, 8, f" {value}", border=1, new_x="LMARGIN", new_y="NEXT")

        if tx.get('kronologis_text'):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 8, "Catatan Kronologis:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "I", 10)
            pdf.multi_cell(0, 6, tx['kronologis_text'], border=1)

        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "LAMPIRAN BUKTI VISUAL", new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        def add_image_to_pdf(title, filename):
            if filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    if pdf.get_y() > 220:
                        pdf.add_page()
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
                    try:
                        pdf.image(filepath, w=100)
                    except:
                        pdf.cell(0, 6, "[Gambar tidak dapat ditampilkan]", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(5)

        add_image_to_pdf("1. Foto ODO Sebelum Isi:", tx.get('foto_odo_sebelum'))
        add_image_to_pdf("2. Foto Nota & ODO Sesudah Isi:", tx.get('foto_nota_odo_sesudah'))
        add_image_to_pdf("3. Foto Struk Fisik:", tx.get('foto_struk'))
        add_image_to_pdf("4. Foto Dispenser:", tx.get('foto_struk_dispenser'))
        add_image_to_pdf("5. Screenshot MyPertamina:", tx.get('foto_mypertamina_admin'))

        pdf_filename = f"Report_BBM_{tx['nopol']}_{tx['id']}.pdf"
        pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf.output(pdf_filepath)

        return send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            pdf_filename, 
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"PDF Error: {e}")
        return f"Error generating PDF: {str(e)}", 500

@app.route('/admin/rekap')
def admin_rekap():
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
        
        title = "BBM VOUCHER PERIODE"
        if filters['start_date'] or filters['end_date']:
            start = filters['start_date'] or 'AWAL'
            end = filters['end_date'] or 'AKHIR'
            title += f" {start} - {end}"
        
        pdf = BBMReportPDF(title=title)
        pdf.add_page()
        pdf.generate_table(data)
        
        pdf.ln(8)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(130, 5, "")
        pdf.cell(60, 5, "Dibuat Oleh,", align="C")
        pdf.cell(60, 5, "Disetujui Oleh,", align="C", ln=True)
        pdf.ln(15)
        pdf.cell(130, 5, "")
        pdf.cell(60, 5, "( Finance )", align="C")
        pdf.cell(60, 5, "( Branch Manager )", align="C")
        
        is_download = request.args.get('dl') == '1'
        
        response = make_response(pdf.output(dest='S'))
        response.headers['Content-Type'] = 'application/pdf'
        if is_download:
            response.headers['Content-Disposition'] = 'attachment; filename=Rekap_BBM.pdf'
        else:
            response.headers['Content-Disposition'] = 'inline; filename=Rekap_BBM.pdf'
        return response
        
    except Exception as e:
        print(f"PDF Error: {e}")
        return f"Error generating PDF: {str(e)}", 500

@app.route('/admin/analytics')
def admin_analytics():
    conn = get_db_connection()
    if not conn:
        return "Database error", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Ambil semua kendaraan yang sudah memiliki minimal 2 transaksi verified
    cursor.execute("""
        SELECT nopol, vehicle_type, bbm_type,
               AVG(km_per_liter) as avg_km_per_liter,
               COUNT(*) as total_transactions,
               MAX(created_at) as last_transaction,
               MIN(created_at) as first_transaction
        FROM bbm_transactions 
        WHERE status = 'verified' AND km_per_liter > 0
        GROUP BY nopol, vehicle_type, bbm_type
        HAVING COUNT(*) >= 2
        ORDER BY avg_km_per_liter DESC
    """)
    vehicle_performance = cursor.fetchall()
    
    # Jika tidak ada data dengan minimal 2 transaksi, ambil semua yang verified
    if not vehicle_performance:
        cursor.execute("""
            SELECT nopol, vehicle_type, bbm_type,
                   AVG(km_per_liter) as avg_km_per_liter,
                   COUNT(*) as total_transactions,
                   MAX(created_at) as last_transaction,
                   MIN(created_at) as first_transaction
            FROM bbm_transactions 
            WHERE status = 'verified' AND km_per_liter > 0
            GROUP BY nopol, vehicle_type, bbm_type
            ORDER BY avg_km_per_liter DESC
        """)
        vehicle_performance = cursor.fetchall()
    
    # Daily stats
    cursor.execute("""
        SELECT DATE(created_at) as date, 
               AVG(km_per_liter) as avg_efficiency,
               COUNT(*) as transactions
        FROM bbm_transactions 
        WHERE status = 'verified' AND km_per_liter > 0
        GROUP BY DATE(created_at)
        ORDER BY date DESC LIMIT 30
    """)
    daily_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('analytics.html', 
                         vehicle_performance=vehicle_performance,
                         daily_stats=daily_stats)

@app.route('/admin/unverify/<int:tx_id>')
def unverify_tx(tx_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bbm_transactions SET status = 'pending' WHERE id = %s", (tx_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('✅ Transaksi dikembalikan ke Pending', 'success')
    return redirect(url_for('admin_rekap'))

@app.route('/admin/delete/<int:tx_id>')
def delete_tx(tx_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bbm_transactions WHERE id = %s", (tx_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('🗑️ Transaksi berhasil dihapus', 'warning')
    return redirect(url_for('admin_rekap'))

# ============================================================
# ADMIN SETTINGS - MULTI BBM
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
            
            # Update BBM Types
            bbm_ids = request.form.getlist('bbm_id[]')
            bbm_names = request.form.getlist('bbm_name[]')
            bbm_prices = request.form.getlist('bbm_price[]')
            bbm_active = request.form.getlist('bbm_active[]')
            
            # Update existing
            for i in range(len(bbm_ids)):
                if bbm_ids[i]:
                    active = 1 if str(i) in bbm_active else 0
                    cursor.execute("""
                        UPDATE bbm_types 
                        SET name = %s, price_per_liter = %s, is_active = %s 
                        WHERE id = %s
                    """, (bbm_names[i], bbm_prices[i], active, bbm_ids[i]))
            
            # Add new
            new_names = request.form.getlist('new_bbm_name[]')
            new_prices = request.form.getlist('new_bbm_price[]')
            for i in range(len(new_names)):
                if new_names[i] and new_prices[i]:
                    cursor.execute("""
                        INSERT INTO bbm_types (name, price_per_liter, is_active) 
                        VALUES (%s, %s, 1)
                        ON DUPLICATE KEY UPDATE price_per_liter = %s, is_active = 1
                    """, (new_names[i], new_prices[i], new_prices[i]))
            
            # Update Vehicle Fuel Limits
            limit_ids = request.form.getlist('limit_id[]')
            limit_vehicles = request.form.getlist('limit_vehicle[]')
            limit_bbm = request.form.getlist('limit_bbm[]')
            limit_good = request.form.getlist('limit_good[]')
            limit_warning = request.form.getlist('limit_warning[]')
            limit_min = request.form.getlist('limit_min[]')
            limit_max = request.form.getlist('limit_max[]')
            
            for i in range(len(limit_ids)):
                if limit_ids[i]:
                    cursor.execute("""
                        UPDATE vehicle_fuel_limits 
                        SET good_km_per_liter = %s, warning_km_per_liter = %s,
                            min_km_per_liter = %s, max_km_per_liter = %s
                        WHERE id = %s
                    """, (limit_good[i], limit_warning[i], limit_min[i], limit_max[i], limit_ids[i]))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('✅ Settings berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # Get data for display
    conn = get_db_connection()
    if not conn:
        return "Database error", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_types ORDER BY name")
    bbm_types = cursor.fetchall()
    
    cursor.execute("SELECT * FROM vehicle_fuel_limits ORDER BY vehicle_type, bbm_type")
    vehicle_limits = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT vehicle_type FROM vehicle_fuel_limits")
    vehicle_types = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('settings.html', 
                         bbm_types=bbm_types,
                         vehicle_limits=vehicle_limits,
                         vehicle_types=vehicle_types)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
