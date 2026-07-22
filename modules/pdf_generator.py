"""PDF Generation Classes"""
import os
import re
from datetime import datetime
from fpdf import FPDF


class BPFBasePDF(FPDF):
    '''Base PDF with standard BPF letterhead'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register Unicode font
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        
        # Gunakan DejaVu Sans (Unicode support)
        dejavu_regular = os.path.join(font_dir, 'DejaVuSans.ttf')
        dejavu_bold = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
        dejavu_italic = os.path.join(font_dir, 'DejaVuSans-Oblique.ttf')
        
        if os.path.exists(dejavu_regular):
            self.add_font('DejaVu', '', dejavu_regular, uni=True)
            if os.path.exists(dejavu_bold):
                self.add_font('DejaVu', 'B', dejavu_bold, uni=True)
            # Italic: gunakan regular kalau oblique tidak ada
            italic_font = dejavu_italic if os.path.exists(dejavu_italic) else dejavu_regular
            self.add_font('DejaVu', 'I', italic_font, uni=True)
            self._use_unicode_font = True
        else:
            self._use_unicode_font = False
    
    def _font(self, style=''):
        '''Return font name based on availability'''
        if hasattr(self, '_use_unicode_font') and self._use_unicode_font:
            return 'DejaVu'
        return 'helvetica'
    
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
        self.set_font(self._font(), 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 6, 'PT BESTPROFIT FUTURES', align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font(self._font(), '', 8)
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
        self.set_font(self._font(), 'I', 6)
        self.set_text_color(148, 163, 184)
        self.cell(0, 4, f'BPF Fleet & BBM System v1.1 | Generated: {datetime.now().strftime("%d-%m-%Y %H:%M")} | Page {self.page_no()}/{{nb}}', align="C")
        self.set_text_color(0, 0, 0)
    

    def add_photo_grid_2x2(self, photos, upload_folder='uploads'):
        '''Add 4 photos in 2x2 grid with labels'''
        if not photos:
            self.set_font(self._font(), 'I', 8)
            self.cell(0, 5, '(Tidak ada foto)', align='C')
            return
        
        # Grid dimensions
        margin = self.l_margin
        page_w = self.w - self.l_margin - self.r_margin
        cell_w = page_w / 2 - 4  # 2 columns with gap
        cell_h = 65  # Fixed cell height
        gap = 4
        
        y_start = self.get_y()
        max_y = y_start
        
        for idx, photo in enumerate(photos):
            col = idx % 2
            row = idx // 2
            
            x = margin + col * (cell_w + gap)
            y = y_start + row * (cell_h + 12)  # +12 for label
            
            # Check page break
            if y + cell_h > self.h - 25:
                self.add_page()
                y_start = self.get_y()
                y = y_start
                max_y = y_start
                # Recalculate for new page
                col = idx % 2
                row = 0
                x = margin + col * (cell_w + gap)
                y = y_start
            
            # Draw border
            self.set_draw_color(200, 200, 200)
            self.set_line_width(0.3)
            self.rect(x, y, cell_w, cell_h)
            
            # Add photo
            if photo.get('path'):
                filepath = os.path.join(upload_folder, photo['path'])
                if os.path.exists(filepath):
                    try:
                        # Get image dimensions
                        from PIL import Image
                        with Image.open(filepath) as img:
                            img_w, img_h = img.size
                        
                        # Calculate fit
                        ratio = min(cell_w / img_w, cell_h / img_h)
                        new_w = img_w * ratio
                        new_h = img_h * ratio
                        
                        # Center in cell
                        img_x = x + (cell_w - new_w) / 2
                        img_y = y + (cell_h - new_h) / 2
                        
                        # Compress & resize
                        import io, base64
                        with Image.open(filepath) as img:
                            # Resize to max 800px wide
                            if img_w > 800:
                                ratio = 800 / img_w
                                img = img.resize((800, int(img_h * ratio)), Image.LANCZOS)
                            
                            # Convert to JPEG with compression
                            buffer = io.BytesIO()
                            img.convert('RGB').save(buffer, format='JPEG', quality=85, optimize=True)
                            buffer.seek(0)
                            
                            # Add to PDF
                            self.image(buffer, x=img_x, y=img_y, w=new_w, h=new_h)
                        
                        # Add zoom link
                        self.set_font(self._font(), '', 5)
                        self.set_text_color(37, 99, 235)
                        self.cell(cell_w, 3, '', border=0)
                    except Exception as e:
                        self.set_font(self._font(), 'I', 7)
                        self.set_text_color(148, 163, 184)
                        self.cell(cell_w, cell_h/2, '(Error)', align='C')
            
            # Label
            self.set_xy(x, y + cell_h + 1)
            self.set_font(self._font(), 'B', 6)
            self.set_text_color(71, 85, 105)
            self.cell(cell_w, 4, photo.get('label', ''), align='C')
            self.set_text_color(0, 0, 0)
            
            if y + cell_h > max_y:
                max_y = y + cell_h + 12
        
        self.set_y(max_y + 4)
    
    def get_photos_from_tx(self, tx):
        '''Extract photo list from transaction'''
        photos = []
        photo_fields = [
            ('foto_odo_sebelum', '📷 ODO Sebelum'),
            ('foto_nota_odo_sesudah', '📷 Nota + ODO'),
            ('foto_struk', '📷 Struk BBM'),
            ('foto_struk_dispenser', '📷 Dispenser'),
        ]
        for field, label in photo_fields:
            if tx.get(field):
                photos.append({'path': tx[field], 'label': label})
        return photos

    def section_title(self, title):
        self.set_font(self._font(), 'B', 9)
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, '  ' + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def info_row(self, label, value, x, y, w_label, w_value):
        self.set_xy(x, y)
        self.set_font(self._font(), '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(w_label, 5, label + ':', align="R")
        self.set_text_color(30, 41, 59)
        self.set_font(self._font(), 'B', 8)
        self.cell(w_value, 5, str(value) if value else '-')
        self.set_text_color(0, 0, 0)




    def resize_image(self, image_path, max_width=800):
        '''Resize image to max_width (maintain aspect ratio) using PIL'''
        try:
            from PIL import Image
            img = Image.open(image_path)
            w, h = img.size
            if w > max_width:
                ratio = max_width / w
                new_w = max_width
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                # Save to temp
                temp_path = image_path + '.resized.jpg'
                img.save(temp_path, 'JPEG', quality=85)
                return temp_path
        except:
            pass
        return image_path
    
    def fit_image_to_cell(self, image_path, x, y, cell_w, cell_h, label=''):
        '''Draw image fitting within cell, maintaining aspect ratio'''
        if not image_path or not os.path.exists(image_path):
            self.set_xy(x, y)
            self.set_font(self._font(), 'I', 7)
            self.set_text_color(148, 163, 184)
            self.cell(cell_w, cell_h, 'No image', border=1, align='C')
            self.set_text_color(0, 0, 0)
            return
        
        # Resize image
        img_path = self.resize_image(image_path)
        
        try:
            from PIL import Image
            img = Image.open(img_path)
            img_w, img_h = img.size
            
            # Calculate fit dimensions
            ratio_w = cell_w / img_w
            ratio_h = cell_h / img_h
            ratio = min(ratio_w, ratio_h)
            
            fit_w = img_w * ratio
            fit_h = img_h * ratio
            
            # Center in cell
            pos_x = x + (cell_w - fit_w) / 2
            pos_y = y + (cell_h - fit_h) / 2
            
            # Border
            self.set_draw_color(226, 232, 240)
            self.rect(x, y, cell_w, cell_h)
            
            # Image
            self.image(img_path, x=pos_x, y=pos_y, w=fit_w, h=fit_h)
            
            # Cleanup temp
            if img_path.endswith('.resized.jpg'):
                try:
                    os.remove(img_path)
                except:
                    pass
                    
        except:
            # Fallback: try direct insert
            self.set_draw_color(226, 232, 240)
            self.rect(x, y, cell_w, cell_h)
            try:
                self.image(image_path, x=x+2, y=y+2, w=cell_w-4, h=cell_h-4)
            except:
                pass
        
        # Label
        if label:
            self.set_xy(x, y + cell_h - 5)
            self.set_font(self._font(), '', 6)
            self.set_fill_color(15, 23, 42)
            self.set_text_color(255, 255, 255)
            self.cell(cell_w, 5, ' ' + label, fill=True)
            self.set_text_color(0, 0, 0)



    def _empty_cell(self, x, y, w, h, text=''):
        self.set_draw_color(226, 232, 240)
        self.rect(x, y, w, h)
        self.set_xy(x, y)
        self.set_font(self._font(), 'I', 7)
        self.set_text_color(148, 163, 184)
        self.cell(w, h, text, align='C')
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
        self.set_font(self._font(), 'B', 11)
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
            [('Appointment', f'{tx.get("jumlah_appointment", 0)}x'), ('KM/L', f'{tx.get("km_per_liter", 0):.1f}')],
            [('GPS', tx.get('gps_address', '-')[:80]), ('SPBU', tx.get('spbu_type', '-').replace('_', ' ').title())],
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
        self.set_font(self._font(), 'I', 6)
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
            
            self.set_font(self._font(), '', 7)
            self.set_text_color(51, 65, 85)
            
            y = self.get_y()
            col_w = (self.w - self.l_margin - self.r_margin) / 2
            
            # Left column
            self.set_xy(self.l_margin, y)
            self.set_font(self._font(), 'B', 7)
            self.cell(col_w, 5, 'Health Score: ' + str(health_score) + '/100', border=0)
            self.set_xy(self.l_margin, y+5)
            self.set_font(self._font(), '', 6)
            self.cell(col_w, 4, 'Rata-rata KM/L: ' + str(health_data['avg_kml'] if health_data else 'N/A'), border=0)
            
            if prev:
                self.set_xy(self.l_margin, y+9)
                odo_diff = tx['odo_km'] - prev['odo_km']
                self.set_font(self._font(), '', 6)
                self.cell(col_w, 4, f'ODO Sebelumnya: {prev["odo_km"]:,} km (selisih {odo_diff:+d} km)', border=0)
            
            # Right column
            self.set_xy(self.l_margin + col_w, y)
            self.set_font(self._font(), 'B', 7)
            self.cell(col_w, 5, 'Budget Bulanan', border=0)
            self.set_xy(self.l_margin + col_w, y+5)
            self.set_font(self._font(), '', 6)
            self.cell(col_w, 4, f'Rp {monthly["total"]:,.0f}' if monthly else 'N/A', border=0)
            
            if notes_row and notes_row['driver_notes']:
                self.set_xy(self.l_margin, y+14)
                self.set_font(self._font(), 'I', 6)
                self.set_text_color(217, 119, 6)
                self.cell(0, 4, 'Catatan GA: ' + notes_row['driver_notes'], border=0)
            
            self.set_text_color(51, 65, 85)
            self.ln(20)
        except:
            self.ln(5)
            self.set_font(self._font(), 'I', 6)
            self.cell(0, 4, 'Data cross-check tidak tersedia', border=0)
            self.ln(5)
        
        self.set_font(self._font(), '', 7)
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
            self.set_font(self._font(), 'B', 5)
            self.cell(bar_w, bar_h, label, border=0, fill=True, align='C')
            if who:
                self.set_xy(x, y + bar_h + 1)
                self.set_font(self._font(), '', 4)
                self.set_text_color(100, 116, 139)
                self.cell(bar_w, 3, who, align='C')
            x += bar_w + 4
        self.set_y(y + bar_h + 6)
        
        # Photos - Grid 2x2
        photos = self.get_photos_from_tx(tx)
        if photos:
            self.section_title('BUKTI VISUAL')
            self.add_photo_grid_2x2(photos, upload_folder)


class BBMReportPDF(BPFBasePDF):
    """Multi-transaction rekap PDF"""

    def header(self):
        super().header()
        self.set_font(self._font(), 'B', 11)
        self.set_text_color(37, 99, 235)
        self.cell(0, 6, self.clean_text(self.title), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def __init__(self, title="BBM VOUCHER PERIODE"):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font(self._font(), '', 10)
    
    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', str(text))
        return text.strip()
    

    def generate_table(self, data):
        if not data:
            self.set_font(self._font(), 'I', 12)
            self.cell(0, 10, "Tidak ada data", align="C")
            return

        self.set_font(self._font(), 'B', 7)
        headers = ['NO', 'TANGGAL', 'NO POLISI', 'DRIVER', 'AMOUNT', 'LITER', 'KM ISI BBM', 'KM/L', 'HEALTH']
        widths = [8, 24, 24, 34, 26, 16, 22, 16, 16]

        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, align='C', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln()

        self.set_font(self._font(), '', 7)
        fill = False
        for idx, tx in enumerate(data, 1):
            if fill:
                self.set_fill_color(241, 245, 249)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Health score
            health = 'N/A'
            try:
                kml = tx.get('km_per_liter', 0) or 0
                if float(kml) > 0:
                    health = str(min(100, int((float(kml) / 14) * 100)))
            except:
                pass
            
            self.cell(widths[0], 6, str(idx), border=1, align='C', fill=True)
            self.cell(widths[1], 6, tx['created_at'].strftime('%d/%m/%y %H:%M') if tx.get('created_at') else '-', border=1, align='C', fill=True)
            self.cell(widths[2], 6, self.clean_text(str(tx['nopol'])), border=1, align='C', fill=True)
            self.cell(widths[3], 6, self.clean_text(str(tx.get('driver_name', '-')).upper()), border=1, fill=True)
            self.cell(widths[4], 6, f"Rp {float(tx['nominal']):,.0f}" if tx.get('nominal') else 'Rp 0', border=1, align='R', fill=True)
            self.cell(widths[5], 6, f"{float(tx.get('liter', 0)):.1f}L", border=1, align='C', fill=True)
            self.cell(widths[6], 6, f"{int(tx.get('odo_km', 0)):,}", border=1, align='C', fill=True)
            self.cell(widths[7], 6, f"{float(tx.get('km_per_liter', 0)):.1f}" if tx.get('km_per_liter') else '-', border=1, align='C', fill=True)
            self.cell(widths[8], 6, health, border=1, align='C', fill=True)
            self.ln()
            fill = not fill
        
        self.ln(4)