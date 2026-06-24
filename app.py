from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import time
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_CONFIG = {
    'host': 'db', 
    'user': 'root',
    'password': 'password_db',
    'database': 'bpf_asset_system'
}

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            retries -= 1
            time.sleep(2)
    return None

def save_file(file_obj, prefix, nopol):
    if file_obj and file_obj.filename:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{nopol}_{timestamp_str}_{file_obj.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        return filename
    return None

def get_pending_count(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM bbm_transactions WHERE status='pending'")
    result = cursor.fetchone()
    cursor.close()
    return result['count'] if result else 0

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# =========================================
# PORTAL DRIVER
# =========================================
@app.route('/', methods=['GET', 'POST'])
def klaim_bbm_driver():
    if request.method == 'POST':
        nopol = request.form.get('nopol')
        nominal = request.form.get('nominal')
        spbu_type = request.form.get('spbu_type')
        
        foto_odo_sebelum = save_file(request.files.get('foto_odo_sebelum'), 'ODO1', nopol)
        foto_nota_odo_sesudah = save_file(request.files.get('foto_nota_odo_sesudah'), 'ODO2', nopol)
        foto_struk = save_file(request.files.get('foto_struk'), 'STRUK', nopol)
        
        foto_struk_dispenser = None
        if spbu_type == 'non_rekanan':
            foto_struk_dispenser = save_file(request.files.get('foto_struk_dispenser'), 'DISPENSER', nopol)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """INSERT INTO bbm_transactions 
                       (nopol, nominal, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')"""
            cursor.execute(query, (nopol, nominal, spbu_type, foto_odo_sebelum, foto_nota_odo_sesudah, foto_struk, foto_struk_dispenser))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('driver.html', success=True)
        except Exception as e:
            return f"Error Database: {str(e)}"

    return render_template('driver.html')

# =========================================
# PORTAL ADMIN (VERIFIKASI)
# =========================================
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    conn = get_db_connection()
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

        try:
            cursor = conn.cursor()
            query = """UPDATE bbm_transactions 
                       SET is_mypertamina_error=%s, kronologis_text=%s, foto_mypertamina_admin=%s, status='verified' 
                       WHERE id=%s"""
            cursor.execute(query, (is_error, kronologis, foto_mypertamina, tx_id))
            conn.commit()
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            return f"Error Database: {str(e)}"

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_transactions WHERE status='pending' ORDER BY created_at ASC")
    transactions = cursor.fetchall()
    cursor.close()
    
    pending_count = get_pending_count(conn)
    conn.close()

    return render_template('admin.html', transactions=transactions, pending_count=pending_count)

# =========================================
# DASHBOARD RIWAYAT & REPORTING
# =========================================
@app.route('/admin/riwayat')
def admin_riwayat():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bbm_transactions WHERE status='verified' ORDER BY created_at DESC")
    transactions = cursor.fetchall()
    cursor.close()
    
    pending_count = get_pending_count(conn)
    conn.close()
    
    return render_template('riwayat.html', transactions=transactions, pending_count=pending_count)

class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, "LAPORAN VERIFIKASI KLAIM BBM", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "B", 11)
        self.cell(0, 6, "PT. BESTPROFIT", new_x="LMARGIN", new_y="NEXT", align="C")
        self.line(10, 26, 200, 26)
        self.ln(5)

@app.route('/admin/report/<int:tx_id>')
def generate_report(tx_id):
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
    
    # 1. Teks Tabel Informasi (Compact)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    
    # Baris 1: ID & Tipe
    pdf.cell(30, 7, " ID / Tgl", border=1, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(65, 7, f" #{tx['id']} - {tx['created_at'].strftime('%d/%m/%Y')}", border=1)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 7, " Tipe SPBU", border=1, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(65, 7, f" {str(tx['spbu_type']).replace('_', ' ').title()}", border=1, new_x="LMARGIN", new_y="NEXT")

    # Baris 2: Nopol & Nominal
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 7, " Nopol", border=1, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(65, 7, f" {tx['nopol'].upper()}", border=1)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 7, " Nominal", border=1, fill=True)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(65, 7, f" Rp {tx['nominal']:,}", border=1, new_x="LMARGIN", new_y="NEXT")

    if tx['kronologis_text']:
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(0, 5, "Catatan Kronologis Sistem:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "I", 8)
        pdf.multi_cell(0, 4, tx['kronologis_text'], border=1)

    pdf.ln(4)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "LAMPIRAN BUKTI VISUAL (TERVERIFIKASI)", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    # 2. Grid System Gambar agar muat 1 Lembar A4
    def place_image_grid(pdf, title, filename, x, y, w, h):
        if filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                pdf.set_xy(x, y)
                pdf.set_font("helvetica", "B", 8)
                pdf.cell(w, 4, title, align="C")
                try:
                    pdf.image(filepath, x=x, y=y+4, w=w, h=h, keep_aspect_ratio=True)
                except Exception:
                    pass

    start_y = pdf.get_y()
    
    # Baris Gambar Atas: ODO (Lebar, Horizontal)
    place_image_grid(pdf, "1. ODO Sebelum Isi", tx['foto_odo_sebelum'], 10, start_y, 90, 60)
    place_image_grid(pdf, "2. Nota & ODO Sesudah Isi", tx['foto_nota_odo_sesudah'], 110, start_y, 90, 60)
    
    # Baris Gambar Bawah: Struk & Bukti MyPertamina (Tinggi, Vertikal)
    # Digeser Y nya sejauh 70mm dari gambar atas
    grid_y_bottom = start_y + 70 
    
    place_image_grid(pdf, "3. Struk Fisik", tx['foto_struk'], 10, grid_y_bottom, 60, 90)
    if tx['foto_struk_dispenser']:
        place_image_grid(pdf, "4. Struk di Dispenser", tx['foto_struk_dispenser'], 75, grid_y_bottom, 60, 90)
    if tx['foto_mypertamina_admin']:
        place_image_grid(pdf, "5. MyPertamina", tx['foto_mypertamina_admin'], 140, grid_y_bottom, 60, 90)

    pdf_filename = f"Report_BBM_{tx['nopol']}_{tx['id']}.pdf"
    pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf.output(pdf_filepath)

    return send_from_directory(app.config['UPLOAD_FOLDER'], pdf_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
