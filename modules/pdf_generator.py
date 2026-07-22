"""PDF Generation Classes - BPF Fleet & BBM System v1.1"""
import os
import re
import io
from datetime import datetime
from fpdf import FPDF

# ============================================================
# CONSTANTS
# ============================================================
COMPANY_NAME = 'PT BESTPROFIT FUTURES'
COMPANY_SUBTITLE = 'Fleet & BBM Management System | Surabaya'
SYSTEM_VERSION = 'BPF Fleet & BBM System v1.1'
LOGO_FILENAMES = ['icon-512.png', 'icon-192.png']
PHOTO_FIELDS = [
    ('foto_odo_sebelum', 'ODO Sebelum'),
    ('foto_nota_odo_sesudah', 'Nota + ODO'),
    ('foto_struk', 'Struk BBM'),
    ('foto_struk_dispenser', 'Dispenser'),
]
HEALTH_BENCHMARK = 14  # KM/L ideal
MAX_IMAGE_WIDTH = 800
JPEG_QUALITY = 85
GRID_CELL_HEIGHT = 60
GRID_GAP = 4

# ============================================================
# BASE PDF CLASS
# ============================================================
class BPFBasePDF(FPDF):
    """Base PDF with standard BPF letterhead and footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_fonts()

    # ---- Font Setup ----
    def _register_fonts(self):
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        regular = os.path.join(font_dir, 'DejaVuSans.ttf')
        bold = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
        italic = os.path.join(font_dir, 'DejaVuSans-Oblique.ttf')
        if os.path.exists(regular):
            self.add_font('DejaVu', '', regular, uni=True)
            self.add_font('DejaVu', 'B', bold if os.path.exists(bold) else regular, uni=True)
            self.add_font('DejaVu', 'I', italic if os.path.exists(italic) else regular, uni=True)
            self._use_unicode = True
        else:
            self._use_unicode = False

    def _font(self, style=''):
        return 'DejaVu' if getattr(self, '_use_unicode', False) else 'helvetica'

    # ---- Letterhead ----
    def header(self):
        logo = self._find_logo()
        if logo:
            try:
                self.image(logo, x=self.l_margin, y=5, w=13)
            except Exception:
                pass
        self.set_x(self.l_margin + 16)
        self.set_font(self._font(), 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 6, COMPANY_NAME, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font(self._font(), '', 8)
        self.set_text_color(71, 85, 105)
        self.cell(0, 4, COMPANY_SUBTITLE, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(37, 99, 235)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y() + 2, self.w - self.r_margin, self.get_y() + 2)
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
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.cell(0, 4, f'{SYSTEM_VERSION} | Generated: {now} | Page {self.page_no()}/{{nb}}', align="C")
        self.set_text_color(0, 0, 0)

    def _find_logo(self):
        for name in LOGO_FILENAMES:
            for base in ['static', os.path.join(os.path.dirname(__file__), '..', 'static')]:
                path = os.path.join(base, name)
                if os.path.exists(path):
                    return path
        return None

    # ---- UI Helpers ----
    def section_title(self, title):
        self.set_font(self._font(), 'B', 9)
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, '  ' + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def info_row(self, label, value, x, y, w_label=30, w_value=50):
        self.set_xy(x, y)
        self.set_font(self._font(), '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(w_label, 5, label + ':', align="R")
        self.set_text_color(30, 41, 59)
        self.set_font(self._font(), 'B', 8)
        self.cell(w_value, 5, str(value) if value is not None else '-')
        self.set_text_color(0, 0, 0)

    def _empty_cell(self, x, y, w, h, text=''):
        self.set_draw_color(226, 232, 240)
        self.rect(x, y, w, h)
        self.set_xy(x, y)
        self.set_font(self._font(), 'I', 7)
        self.set_text_color(148, 163, 184)
        self.cell(w, h, text, align='C')
        self.set_text_color(0, 0, 0)

    # ---- Photo Grid 2x2 ----
    def add_photo_grid(self, photos, upload_folder='uploads'):
        """Render up to 4 photos in a 2x2 grid with labels."""
        if not photos:
            self.set_font(self._font(), 'I', 8)
            self.cell(0, 5, '(Tidak ada foto)', align='C')
            return
        margin = self.l_margin
        page_w = self.w - self.l_margin - self.r_margin
        cell_w = page_w / 2 - GRID_GAP
        cell_h = GRID_CELL_HEIGHT
        y_start = self.get_y()
        max_y = y_start
        for idx, photo in enumerate(photos):
            col, row = idx % 2, idx // 2
            x = margin + col * (cell_w + GRID_GAP)
            y = y_start + row * (cell_h + 12)
            if y + cell_h > self.h - 25:
                self.add_page()
                y_start = self.get_y()
                y = y_start
                max_y = y_start
                col, row = idx % 2, 0
                x = margin + col * (cell_w + GRID_GAP)
            self.set_draw_color(200, 200, 200)
            self.set_line_width(0.3)
            self.rect(x, y, cell_w, cell_h)
            if photo.get('path'):
                filepath = os.path.join(upload_folder, photo['path'])
                if os.path.exists(filepath):
                    self._place_image(filepath, x, y, cell_w, cell_h)
            self.set_xy(x, y + cell_h + 1)
            self.set_font(self._font(), 'B', 6)
            self.set_text_color(71, 85, 105)
            self.cell(cell_w, 4, photo.get('label', ''), align='C')
            self.set_text_color(0, 0, 0)
            if y + cell_h > max_y:
                max_y = y + cell_h + 12
        self.set_y(max_y + 4)

    def _place_image(self, filepath, x, y, cell_w, cell_h):
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                img_w, img_h = img.size
            ratio = min(cell_w / img_w, cell_h / img_h)
            new_w, new_h = img_w * ratio, img_h * ratio
            img_x = x + (cell_w - new_w) / 2
            img_y = y + (cell_h - new_h) / 2
            with Image.open(filepath) as img:
                if img_w > MAX_IMAGE_WIDTH:
                    r = MAX_IMAGE_WIDTH / img_w
                    img = img.resize((MAX_IMAGE_WIDTH, int(img_h * r)), Image.LANCZOS)
                buf = io.BytesIO()
                img.convert('RGB').save(buf, format='JPEG', quality=JPEG_QUALITY, optimize=True)
                buf.seek(0)
                self.image(buf, x=img_x, y=img_y, w=new_w, h=new_h)
        except Exception:
            self.set_draw_color(226, 232, 240)
            self.rect(x, y, cell_w, cell_h)
            try:
                self.image(filepath, x=x + 2, y=y + 2, w=cell_w - 4, h=cell_h - 4)
            except Exception:
                pass

    @staticmethod
    def extract_photos(tx):
        return [{'path': tx[f], 'label': l} for f, l in PHOTO_FIELDS if tx.get(f)]

    @staticmethod
    def clean_text(text):
        if not text:
            return ''
        return re.sub(r'[^\x20-\x7E\n\r\t]', '', str(text)).strip()


# ============================================================
# SINGLE TRANSACTION REPORT
# ============================================================
class PDFReportCompact(BPFBasePDF):
    """Compact single-transaction PDF report with photo grid."""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=8)
        self.set_margins(8, 8, 8)

    def generate_compact_report(self, tx, upload_folder='uploads'):
        self._draw_transaction_header(tx)
        self._draw_info_grid(tx)
        self._draw_narrative(tx)
        self._draw_cross_check(tx)
        self._draw_approval_bar(tx)
        self._draw_photos(tx, upload_folder)

    # ---- Private Methods ----
    def _draw_transaction_header(self, tx):
        nopol = self.clean_text(str(tx.get('nopol', '-')).upper())
        display_id = tx.get('display_id', f'#{tx["id"]}')
        self.set_font(self._font(), 'B', 11)
        self.set_text_color(15, 23, 42)
        self.cell(0, 7, f'TRANSAKSI {display_id} | {nopol}', align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def _draw_info_grid(self, tx):
        self.section_title('INFORMASI TRANSAKSI')
        nopol = self.clean_text(str(tx.get('nopol', '-')).upper())
        driver = self.clean_text(str(tx.get('driver_name', '-')).upper())
        vehicle = self.clean_text(str(tx.get('vehicle_type', '-')))
        bbm = self.clean_text(str(tx.get('bbm_type', '-')))
        spbu = self.clean_text(str(tx.get('spbu_type', '-')).replace('_', ' ').title())
        gps = self.clean_text(str(tx.get('gps_address', '') or 'Tidak tersedia'))
        nominal = f'Rp {float(tx["nominal"]):,.0f}'
        liter = f'{float(tx["liter"]):.1f} L'
        odo = f'{int(tx["odo_km"]):,} km'
        kml = f'{float(tx.get("km_per_liter", 0)):.1f}'
        appt = f'{tx.get("jumlah_appointment", 0) or 0}x'
        price = f'Rp {float(tx.get("price_per_liter", 0)):,.0f}'
        rows = [
            [('ID', tx.get('display_id', f'#{tx["id"]}')), ('Tanggal', tx['created_at'].strftime('%d-%m-%Y %H:%M') if tx.get('created_at') else '-')],
            [('Nopol', nopol), ('Driver', driver)],
            [('Kendaraan', vehicle), ('BBM', bbm)],
            [('Nominal', nominal), ('Volume', liter)],
            [('Harga/L', price), ('ODO', odo)],
            [('KM/L', kml), ('Appointment', appt)],
            [('SPBU', spbu), ('GPS', gps[:60])],
        ]
        col1_x, col2_x = self.l_margin, self.w / 2 + 5
        y_start = self.get_y()
        for i, row in enumerate(rows):
            y = y_start + (i * 5.5)
            self.info_row(row[0][0], row[0][1], col1_x, y)
            self.info_row(row[1][0], row[1][1], col2_x, y)
        self.set_y(y_start + len(rows) * 5.5 + 2)

    def _draw_narrative(self, tx):
        self.section_title('KRONOLOGIS VERIFIKASI')
        nopol = self.clean_text(str(tx.get('nopol', '-')).upper())
        driver = self.clean_text(str(tx.get('driver_name', 'Driver')).upper())
        bbm = self.clean_text(str(tx.get('bbm_type', '-')))
        spbu = self.clean_text(str(tx.get('spbu_type', '-')).replace('_', ' ').title())
        gps = self.clean_text(str(tx.get('gps_address', '') or 'lokasi tidak terdeteksi'))
        tgl = tx['created_at'].strftime('%d %B %Y pukul %H:%M') if tx.get('created_at') else '-'
        narrative = (
            f'Pada hari {tgl}, {driver} selaku driver kendaraan {nopol} '
            f'melakukan pengisian {bbm} sebanyak {tx["liter"]} Liter '
            f'dengan total Rp {float(tx["nominal"]):,.0f} di SPBU {spbu}. '
            f'Pengisian dilakukan pada ODO {int(tx["odo_km"]):,} km. '
            f'Lokasi: {gps}. '
        )
        appt = tx.get('jumlah_appointment', 0) or 0
        if appt > 0:
            narrative += f'Driver memiliki {appt} janji temu. '
        ga = self.clean_text(str(tx.get('ga_approved_by') or tx.get('approved_by_user') or ''))
        fin = self.clean_text(str(tx.get('finance_payout_by') or tx.get('payout_by_user') or ''))
        arc = self.clean_text(str(tx.get('archived_by') or tx.get('archived_by_user') or ''))
        if ga: narrative += f'Disetujui GA: {ga}. '
        if fin: narrative += f'Dana dicairkan Finance: {fin}. '
        if arc: narrative += f'Diarsipkan: {arc}. '
        narrative += 'Klaim dinyatakan SAH sesuai prosedur PT. Bestprofit Surabaya.'
        self.set_font(self._font(), '', 7)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 4, narrative, align='J')
        self.ln(2)

    def _draw_cross_check(self, tx):
        self.section_title('CROSS-CHECK VERIFIKASI')
        try:
            from modules.config import get_db_connection
            conn = get_db_connection()
            if not conn:
                raise Exception('DB not available')
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT odo_km, created_at FROM transactions WHERE nopol=%s AND status='archived' AND id<%s ORDER BY id DESC LIMIT 1", (tx['nopol'], tx['id']))
            prev = cur.fetchone()
            cur.execute("SELECT ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml, COUNT(*) as cnt FROM transactions WHERE nopol=%s AND status='archived' AND km_per_liter>0", (tx['nopol'],))
            health = cur.fetchone()
            cur.execute("SELECT COALESCE(SUM(nominal),0) as total FROM transactions WHERE driver_name=%s AND MONTH(created_at)=MONTH(CURDATE())", (tx['driver_name'],))
            monthly = cur.fetchone()
            cur.execute("SELECT driver_notes FROM vehicle_assignments WHERE nopol=%s ORDER BY id DESC LIMIT 1", (tx['nopol'],))
            notes = cur.fetchone()
            cur.close(); conn.close()
            avg_kml = float(health['avg_kml']) if health and health['avg_kml'] else 10
            health_score = min(100, int((avg_kml / HEALTH_BENCHMARK) * 100))
            col_w = (self.w - self.l_margin - self.r_margin) / 2
            y = self.get_y()
            self.set_xy(self.l_margin, y)
            self.set_font(self._font(), 'B', 7)
            self.cell(col_w, 5, f'Health Score: {health_score}/100')
            self.set_xy(self.l_margin, y + 5)
            self.set_font(self._font(), '', 6)
            self.cell(col_w, 4, f'Rata-rata KM/L: {avg_kml:.1f} ({health["cnt"]} tx)' if health else 'N/A')
            if prev:
                odo_diff = int(tx['odo_km']) - int(prev['odo_km'])
                self.set_xy(self.l_margin, y + 9)
                self.set_font(self._font(), '', 6)
                self.cell(col_w, 4, f'ODO Sebelumnya: {int(prev["odo_km"]):,} km (selisih {odo_diff:+d} km)')
            self.set_xy(self.l_margin + col_w, y)
            self.set_font(self._font(), 'B', 7)
            self.cell(col_w, 5, 'Budget Bulanan')
            self.set_xy(self.l_margin + col_w, y + 5)
            self.set_font(self._font(), '', 6)
            self.cell(col_w, 4, f'Rp {float(monthly["total"]):,.0f}' if monthly else 'N/A')
            if notes and notes['driver_notes']:
                self.set_xy(self.l_margin, y + 14)
                self.set_font(self._font(), 'I', 6)
                self.set_text_color(217, 119, 6)
                self.cell(0, 4, 'Catatan GA: ' + notes['driver_notes'])
            self.set_text_color(51, 65, 85)
            self.ln(20)
        except Exception:
            self.ln(5)
            self.set_font(self._font(), 'I', 6)
            self.cell(0, 4, 'Data cross-check tidak tersedia', border=0)
            self.ln(5)

    def _draw_approval_bar(self, tx):
        self.section_title('STATUS PERSETUJUAN')
        ga = self.clean_text(str(tx.get('ga_approved_by') or tx.get('approved_by_user') or ''))
        fin = self.clean_text(str(tx.get('finance_payout_by') or tx.get('payout_by_user') or ''))
        arc = self.clean_text(str(tx.get('archived_by') or tx.get('archived_by_user') or ''))
        statuses = [
            ('GA APPROVAL', ga if ga else None),
            ('FINANCE PAYOUT', fin if fin else None),
            ('DRIVER TTD', 'Driver' if arc else None),
            ('ARCHIVED', arc if arc else None),
        ]
        bar_w = (self.w - self.l_margin - self.r_margin - 12) / 4
        x, y = self.l_margin, self.get_y() + 2
        for label, who in statuses:
            color = (34, 197, 94) if who else (226, 232, 240)
            text_color = (255, 255, 255) if who else (148, 163, 184)
            self.set_fill_color(*color)
            self.set_text_color(*text_color)
            self.set_xy(x, y)
            self.set_font(self._font(), 'B', 5)
            self.cell(bar_w, 4, label, fill=True, align='C')
            if who:
                self.set_xy(x, y + 5)
                self.set_font(self._font(), '', 4)
                self.set_text_color(100, 116, 139)
                self.cell(bar_w, 3, who, align='C')
            x += bar_w + 4
        self.set_y(y + 12)

    def _draw_photos(self, tx, upload_folder):
        photos = self.extract_photos(tx)
        if photos:
            self.section_title('BUKTI VISUAL')
            self.add_photo_grid(photos, upload_folder)


# ============================================================
# MULTI-TRANSACTION REKAP PDF
# ============================================================
class BBMReportPDF(BPFBasePDF):
    """Landscape multi-transaction recap PDF."""

    def __init__(self, title="REKAP DANA BBM"):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        super().header()
        self.set_font(self._font(), 'B', 11)
        self.set_text_color(37, 99, 235)
        self.cell(0, 6, self.clean_text(self.title), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def generate_table(self, data):
        if not data:
            self.set_font(self._font(), 'I', 12)
            self.cell(0, 10, "Tidak ada data", align="C")
            return
        headers = ['NO', 'TANGGAL', 'NO POLISI', 'DRIVER', 'AMOUNT', 'LITER', 'KM ISI BBM', 'KM/L', 'HEALTH']
        widths = [8, 24, 24, 34, 26, 16, 22, 16, 16]
        self.set_font(self._font(), 'B', 7)
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, align='C', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln()
        self.set_font(self._font(), '', 7)
        fill = False
        for idx, tx in enumerate(data, 1):
            self.set_fill_color(241, 245, 249) if fill else self.set_fill_color(255, 255, 255)
            health = 'N/A'
            try:
                kml = float(tx.get('km_per_liter', 0) or 0)
                if kml > 0:
                    health = str(min(100, int((kml / HEALTH_BENCHMARK) * 100)))
            except Exception:
                pass
            self.cell(widths[0], 6, str(idx), border=1, align='C', fill=True)
            self.cell(widths[1], 6, tx['created_at'].strftime('%d/%m/%y %H:%M') if tx.get('created_at') else '-', border=1, align='C', fill=True)
            self.cell(widths[2], 6, self.clean_text(str(tx['nopol'])), border=1, align='C', fill=True)
            self.cell(widths[3], 6, self.clean_text(str(tx.get('driver_name', '-')).upper()), border=1, fill=True)
            self.cell(widths[4], 6, f"Rp {float(tx['nominal']):,.0f}" if tx.get('nominal') else 'Rp 0', border=1, align='R', fill=True)
            self.cell(widths[5], 6, f"{float(tx.get('liter', 0)):.1f}L", border=1, align='C', fill=True)
            self.cell(widths[6], 6, f"{int(tx.get('odo_km', 0)):,}", border=1, align='C', fill=True)
            self.cell(widths[7], 6, f"{kml:.1f}" if tx.get('km_per_liter') else '-', border=1, align='C', fill=True)
            self.cell(widths[8], 6, health, border=1, align='C', fill=True)
            self.ln()
            fill = not fill
        self.ln(4)
