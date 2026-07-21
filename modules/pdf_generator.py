"""PDF Generation Classes"""
import os
import re
from datetime import datetime
from fpdf import FPDF


class BPFBasePDF(FPDF):
    '''Base PDF with standard BPF letterhead'''
    
    def _get_logo_path(self):
        '''Cari logo di beberapa kemungkinan path'''
        paths = [
            os.path.join('static', 'icon-512.png'),
            os.path.join(os.path.dirname(__file__), '..', 'static', 'icon-512.png'),
            os.path.join(os.path.dirname(__file__), '..', 'static', 'icon-192.png'),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None
    
    def header(self):
        logo_path = self._get_logo_path()
        if logo_path:
            try:
                self.image(logo_path, x=self.l_margin, y=5, w=13)
            except:
                pass
        
        self.set_x(self.l_margin + 16)
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 6, 'PT BESTPROFIT FUTURES', align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', '', 8)
        self.set_text_color(71, 85, 105)
        self.cell(0, 4, 'Fleet & BBM Management System | Surabaya', align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Divider
        self.set_draw_color(37, 99, 235)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y()+2, self.w - self.r_margin, self.get_y()+2)
        self.ln(6)
        self.set_text_color(0, 0, 0)
    
    def footer(self):
        self.set_y(-16)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-13)
        self.set_font('helvetica', 'I', 6)
        self.set_text_color(148, 163, 184)
        self.cell(0, 4, f'BPF Fleet & BBM System v1.1 | Generated: {datetime.now().strftime("%d-%m-%Y %H:%M")} | Page {self.page_no()}/{{nb}}', align="C")
        self.set_text_color(0, 0, 0)
    
    def section_title(self, title):
        self.set_font('helvetica', 'B', 9)
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, '  ' + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def info_row(self, label, value, x, y, w_label, w_value):
        self.set_xy(x, y)
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(w_label, 5, label + ':', align="R")
        self.set_text_color(30, 41, 59)
        self.set_font('helvetica', 'B', 8)
        self.cell(w_value, 5, str(value) if value else '-')
        self.set_text_color(0, 0, 0)



class PDFReportCompact(BPFBasePDF):
    """Single transaction PDF report"""
    
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=8)
        self.set_margins(8, 8, 8)
    
    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', str(text))
        return text.strip()
    




    def generate_compact_report(self, tx, upload_folder='uploads'):
        """Generate complete single-page report"""
        # Header
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(15, 23, 42)
        nopol_text = self.clean_text(str(tx.get('nopol', '-')).upper())
        self.cell(0, 7, f'TRANSAKSI {tx.get("display_id", "#"+str(tx["id"]))} | {nopol_text}', align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        # Info Grid
        self.section_title('INFORMASI TRANSAKSI')
        col1_x = self.l_margin
        col2_x = self.w / 2 + 5
        row_h = 5.5
        label_w = 30
        value_w = 50
        
        rows = [
            [('ID', tx.get('display_id', f'#{tx["id"]}')), ('Tanggal', tx['created_at'].strftime('%d-%m-%Y %H:%M') if tx.get('created_at') else '-')],
            [('Nopol', nopol_text), ('Driver', self.clean_text(str(tx.get('driver_name', '-')).upper()))],
            [('Kendaraan', self.clean_text(str(tx.get('vehicle_type', '-')))), ('BBM', self.clean_text(str(tx.get('bbm_type', '-'))))],
            [('Nominal', f'Rp {tx["nominal"]:,.0f}'), ('Volume', f'{tx["liter"]} L')],
            [('Harga/L', f'Rp {tx.get("price_per_liter", 0):,.0f}'), ('ODO', f'{tx["odo_km"]:,} km')],
            [('SPBU', self.clean_text(str(tx.get('spbu_type', '-')).replace('_', ' ').title())), ('Appt', f'{tx.get("jumlah_appointment", 0)}x')],
        ]
        
        y_start = self.get_y()
        for i, row in enumerate(rows):
            y_pos = y_start + (i * row_h)
            self.info_row(row[0][0], row[0][1], col1_x, y_pos, label_w, value_w)
            self.info_row(row[1][0], row[1][1], col2_x, y_pos, label_w, value_w)
        self.set_y(y_start + len(rows) * row_h + 2)
        
        # Location
        gps_addr = self.clean_text(str(tx.get('gps_address', '') or 'Tidak tersedia'))
        self.set_font('helvetica', 'I', 6)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, f'Lokasi: {gps_addr[:120]}', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        # Narrative
        self.section_title('KRONOLOGIS VERIFIKASI')
        driver_name = self.clean_text(str(tx.get('driver_name', 'Driver')).upper())
        tgl = tx['created_at'].strftime('%d %B %Y pukul %H:%M') if tx.get('created_at') else '-'
        narrative = (
            f'Pada hari {tgl}, Bapak/Ibu {driver_name} selaku driver kendaraan {nopol_text} '
            f'melakukan pengisian {self.clean_text(str(tx.get("bbm_type", "-")))} sebanyak {tx["liter"]} Liter '
            f'dengan total Rp {tx["nominal"]:,.0f} di SPBU {self.clean_text(str(tx.get("spbu_type", "-")).replace("_", " ").title())}. '
            f'Pengisian dilakukan pada ODO {tx["odo_km"]:,} km. '
            f'Lokasi terdeteksi di {gps_addr}. '
        )
        
        appt = tx.get('jumlah_appointment', 0) or 0
        if appt > 0:
            narrative += f'Driver memiliki {appt} janji temu pada hari yang sama. '
        
        ga_by = self.clean_text(str(tx.get('ga_approved_by', '') or tx.get('approved_by_user', '') or '-'))
        if ga_by != '-':
            narrative += f'Klaim disetujui GA ({ga_by}). '
        
        fin_by = self.clean_text(str(tx.get('finance_payout_by', '') or tx.get('payout_by_user', '') or '-'))
        if fin_by != '-':
            narrative += f'Dana dicairkan Finance ({fin_by}). '
        
        arc_by = self.clean_text(str(tx.get('archived_by', '') or tx.get('archived_by_user', '') or '-'))
        if arc_by != '-':
            narrative += f'Dokumen diarsipkan ({arc_by}). '
        
        narrative += 'Klaim dinyatakan SAH sesuai prosedur PT. Bestprofit Surabaya.'
        
        # ===== CROSS-CHECK SUMMARY (Fitur #1) =====
        self.section_title('CROSS-CHECK VERIFIKASI')
        
        # Fetch health data
        try:
            import mysql.connector
            conn_check = mysql.connector.connect(
                host=os.environ.get('DB_HOST', 'db'),
                user=os.environ.get('DB_USER', 'bpf_user'),
                password=os.environ.get('DB_PASSWORD', 'bpf_pass'),
                database=os.environ.get('DB_NAME', 'bpf_asset_system')
            )
            cur = conn_check.cursor(dictionary=True)
            
            # Previous ODO
            cur.execute("SELECT odo_km, created_at FROM transactions WHERE nopol=%s AND status='archived' AND id<%s ORDER BY id DESC LIMIT 1", (tx['nopol'], tx['id']))
            prev = cur.fetchone()
            
            # Avg KM/L
            cur.execute("SELECT ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg FROM transactions WHERE nopol=%s AND status='archived' AND km_per_liter>0", (tx['nopol'],))
            avg = cur.fetchone()
            
            # Monthly budget
            cur.execute("SELECT COALESCE(SUM(nominal),0) as total FROM transactions WHERE driver_name=%s AND MONTH(created_at)=MONTH(CURDATE())", (tx['driver_name'],))
            monthly = cur.fetchone()
            
            # Health score
            cur.execute("SELECT ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml, COUNT(*) as cnt FROM transactions WHERE nopol=%s AND status='archived' AND km_per_liter>0", (tx['nopol'],))
            health_data = cur.fetchone()
            health_score = min(100, int(((health_data['avg_kml'] or 10) / 14) * 100)) if health_data else 50
            
            # Driver notes
            cur.execute("SELECT driver_notes FROM vehicle_assignments WHERE nopol=%s ORDER BY id DESC LIMIT 1", (tx['nopol'],))
            notes_row = cur.fetchone()
            
            cur.close()
            conn_check.close()
            
            self.set_font('helvetica', '', 7)
            self.set_text_color(51, 65, 85)
            
            y = self.get_y()
            col_w = (self.w - self.l_margin - self.r_margin) / 2
            
            # Left column
            self.set_xy(self.l_margin, y)
            self.set_font('helvetica', 'B', 7)
            self.cell(col_w, 5, 'Health Score: ' + str(health_score) + '/100', border=0)
            self.set_xy(self.l_margin, y+5)
            self.set_font('helvetica', '', 6)
            self.cell(col_w, 4, 'Rata-rata KM/L: ' + str(health_data['avg_kml'] if health_data else 'N/A'), border=0)
            
            if prev:
                self.set_xy(self.l_margin, y+9)
                odo_diff = tx['odo_km'] - prev['odo_km']
                self.set_font('helvetica', '', 6)
                self.cell(col_w, 4, f'ODO Sebelumnya: {prev["odo_km"]:,} km (selisih {odo_diff:+d} km)', border=0)
            
            # Right column
            self.set_xy(self.l_margin + col_w, y)
            self.set_font('helvetica', 'B', 7)
            self.cell(col_w, 5, 'Budget Bulanan', border=0)
            self.set_xy(self.l_margin + col_w, y+5)
            self.set_font('helvetica', '', 6)
            self.cell(col_w, 4, f'Rp {monthly["total"]:,.0f}' if monthly else 'N/A', border=0)
            
            if notes_row and notes_row['driver_notes']:
                self.set_xy(self.l_margin, y+14)
                self.set_font('helvetica', 'I', 6)
                self.set_text_color(217, 119, 6)
                self.cell(0, 4, 'Catatan GA: ' + notes_row['driver_notes'], border=0)
            
            self.set_text_color(51, 65, 85)
            self.ln(20)
        except:
            self.ln(5)
            self.set_font('helvetica', 'I', 6)
            self.cell(0, 4, 'Data cross-check tidak tersedia', border=0)
            self.ln(5)
        
        # ===== CROSS-CHECK SUMMARY (Fitur #1) =====
        self.section_title('CROSS-CHECK VERIFIKASI')
        
        # Fetch health data
        try:
            import mysql.connector
            conn_check = mysql.connector.connect(
                host=os.environ.get('DB_HOST', 'db'),
                user=os.environ.get('DB_USER', 'bpf_user'),
                password=os.environ.get('DB_PASSWORD', 'bpf_pass'),
                database=os.environ.get('DB_NAME', 'bpf_asset_system')
            )
            cur = conn_check.cursor(dictionary=True)
            
            # Previous ODO
            cur.execute("SELECT odo_km, created_at FROM transactions WHERE nopol=%s AND status='archived' AND id<%s ORDER BY id DESC LIMIT 1", (tx['nopol'], tx['id']))
            prev = cur.fetchone()
            
            # Avg KM/L
            cur.execute("SELECT ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg FROM transactions WHERE nopol=%s AND status='archived' AND km_per_liter>0", (tx['nopol'],))
            avg = cur.fetchone()
            
            # Monthly budget
            cur.execute("SELECT COALESCE(SUM(nominal),0) as total FROM transactions WHERE driver_name=%s AND MONTH(created_at)=MONTH(CURDATE())", (tx['driver_name'],))
            monthly = cur.fetchone()
            
            # Health score
            cur.execute("SELECT ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml, COUNT(*) as cnt FROM transactions WHERE nopol=%s AND status='archived' AND km_per_liter>0", (tx['nopol'],))
            health_data = cur.fetchone()
            health_score = min(100, int(((health_data['avg_kml'] or 10) / 14) * 100)) if health_data else 50
            
            # Driver notes
            cur.execute("SELECT driver_notes FROM vehicle_assignments WHERE nopol=%s ORDER BY id DESC LIMIT 1", (tx['nopol'],))
            notes_row = cur.fetchone()
            
            cur.close()
            conn_check.close()
            
            self.set_font('helvetica', '', 7)
            self.set_text_color(51, 65, 85)
            
            y = self.get_y()
            col_w = (self.w - self.l_margin - self.r_margin) / 2
            
            # Left column
            self.set_xy(self.l_margin, y)
            self.set_font('helvetica', 'B', 7)
            self.cell(col_w, 5, 'Health Score: ' + str(health_score) + '/100', border=0)
            self.set_xy(self.l_margin, y+5)
            self.set_font('helvetica', '', 6)
            self.cell(col_w, 4, 'Rata-rata KM/L: ' + str(health_data['avg_kml'] if health_data else 'N/A'), border=0)
            
            if prev:
                self.set_xy(self.l_margin, y+9)
                odo_diff = tx['odo_km'] - prev['odo_km']
                self.set_font('helvetica', '', 6)
                self.cell(col_w, 4, f'ODO Sebelumnya: {prev["odo_km"]:,} km (selisih {odo_diff:+d} km)', border=0)
            
            # Right column
            self.set_xy(self.l_margin + col_w, y)
            self.set_font('helvetica', 'B', 7)
            self.cell(col_w, 5, 'Budget Bulanan', border=0)
            self.set_xy(self.l_margin + col_w, y+5)
            self.set_font('helvetica', '', 6)
            self.cell(col_w, 4, f'Rp {monthly["total"]:,.0f}' if monthly else 'N/A', border=0)
            
            if notes_row and notes_row['driver_notes']:
                self.set_xy(self.l_margin, y+14)
                self.set_font('helvetica', 'I', 6)
                self.set_text_color(217, 119, 6)
                self.cell(0, 4, 'Catatan GA: ' + notes_row['driver_notes'], border=0)
            
            self.set_text_color(51, 65, 85)
            self.ln(20)
        except:
            self.ln(5)
            self.set_font('helvetica', 'I', 6)
            self.cell(0, 4, 'Data cross-check tidak tersedia', border=0)
            self.ln(5)
        
        self.set_font('helvetica', '', 7)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 4, narrative, align='J')
        self.ln(2)
        
        # Status Bar
        self.section_title('STATUS PERSETUJUAN')
        statuses = [
            ('GA APPROVAL', ga_by if ga_by != '-' else None),
            ('FINANCE PAYOUT', fin_by if fin_by != '-' else None),
            ('DRIVER TTD', 'Driver' if arc_by != '-' else None),
            ('ARCHIVED', arc_by if arc_by != '-' else None),
        ]
        bar_w = (self.w - self.l_margin - self.r_margin - 12) / 4
        bar_h = 4
        x = self.l_margin
        y = self.get_y() + 2
        for label, who in statuses:
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
                self.cell(bar_w, 3, who, align='C')
            x += bar_w + 4
        self.set_y(y + bar_h + 6)
        
        # Photos
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
            img_w, img_h, gap = 55, 42, 3
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
                        filepath = os.path.join(upload_folder, path)
                        if os.path.exists(filepath):
                            self.image(filepath, x=x+2, y=y+4, w=img_w-4, h=img_h-6)
                    except:
                        pass
                    x += img_w + gap
                self.set_y(y + img_h + 10)


class BBMReportPDF(BPFBasePDF):
    """Multi-transaction rekap PDF"""

    def header(self):
        super().header()
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(37, 99, 235)
        self.cell(0, 6, self.clean_text(self.title), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def __init__(self, title="BBM VOUCHER PERIODE"):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font('helvetica', '', 10)
    
    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', str(text))
        return text.strip()
    

    def generate_table(self, data):
        if not data:
            self.set_font('helvetica', 'I', 12)
            self.cell(0, 10, "Tidak ada data", align="C")
            return
        
        self.set_font('helvetica', 'B', 7)
        headers = ['NO', 'TANGGAL', 'NO POLISI', 'AMOUNT', 'KM ISI BBM', 
                   'KM AWAL', 'KM AKHIR', 'TOTAL KM', 'RATA-RATA KM', 'HEALTH', 'DRIVER', 'LITER']
        widths = [8, 22, 24, 24, 20, 20, 20, 16, 18, 14, 34, 14]
        
        self.set_fill_color(200, 200, 200)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('helvetica', '', 7)
        fill = False
        for idx, tx in enumerate(data, 1):
            self.set_fill_color(240 if fill else 255)
            jam = tx['created_at'].strftime('%H:%M') if tx.get('created_at') else '-'
            self.cell(widths[0], 6, str(idx), border=1, align='C', fill=True)
            self.cell(widths[1], 6, tx['created_at'].strftime('%d %b %Y') if tx.get('created_at') else '-', border=1, align='C', fill=True)
            self.cell(widths[2], 6, self.clean_text(str(tx['nopol'])), border=1, align='C', fill=True)
            self.cell(widths[3], 6, f"Rp {tx['nominal']:,.0f}" if tx.get('nominal') else 'Rp 0', border=1, align='R', fill=True)
            self.cell(widths[4], 6, f"{tx['odo_km']:,}" if tx.get('odo_km') else '0', border=1, align='C', fill=True)
            self.cell(widths[5], 6, f"{tx.get('km_awal', 0):,}", border=1, align='C', fill=True)
            self.cell(widths[6], 6, f"{tx.get('km_akhir', 0):,}", border=1, align='C', fill=True)
            self.cell(widths[7], 6, f"{tx.get('total_km', 0):,}", border=1, align='C', fill=True)
            self.cell(widths[8], 6, f"{tx.get('rata_rata', 0):.2f}", border=1, align='C', fill=True)
            # Health score placeholder replaced
            self.cell(widths[9], 6, f"{tx.get('rata_rata', 0):.2f}", border=1, align='C', fill=True)
            self.cell(widths[10], 6, self.clean_text(str(tx['driver_name']).upper() if tx.get('driver_name') else '-'), border=1, fill=True)
            # Health score
            health = 'N/A'
            try:
                if tx.get('km_per_liter') and tx['km_per_liter'] > 0:
                    health = str(min(100, int((tx['km_per_liter'] / 14) * 100)))
            except:
                pass
            self.cell(widths[9], 6, health, border=1, align='C', fill=True)
            self.cell(widths[10], 6, self.clean_text(str(tx['driver_name']).upper() if tx.get('driver_name') else '-'), border=1, fill=True)
            # Health score
            health = 'N/A'
            try:
                if tx.get('km_per_liter') and tx['km_per_liter'] > 0:
                    health = str(min(100, int((tx['km_per_liter'] / 14) * 100)))
            except:
                pass
            self.cell(widths[9], 6, health, border=1, align='C', fill=True)
            self.cell(widths[10], 6, self.clean_text(str(tx['driver_name']).upper() if tx.get('driver_name') else '-'), border=1, fill=True)
            self.cell(widths[11], 6, str(tx.get('liter', 0)), border=1, align='C', fill=True)
            self.ln()
            fill = not fill
