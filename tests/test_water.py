"""
Unit Tests — Tanda Terima Pembelian Air Minum (v2.6)
BPF BBM System

- WaterReceiptPDF: dokumen PDF untuk status verified / rejected.
- _get_ttd_names: nama TTD Finance/GA dari system_config (mock DB).
- home_for_role('ob') → /app/water (halaman OB).

Jalankan:
    docker exec bbm_web python3 -m pytest tests/test_water.py -v
"""

import sys
import os
import re
import zlib
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, session
from modules.helpers import home_for_role, ROLE_HOME


def _pdf_text(pdf_bytes):
    """Ekstrak teks dari PDF fpdf2 (font disubset → kode glyph 2-byte + CMap ToUnicode).

    Tanpa dependensi eksternal (pypdf/PyPDF2 tidak tersedia di container):
    1. Parse objek PDF & referensi /ToUnicode per font.
    2. Bangun CMap glyph-code -> Unicode dari stream CMap (FlateDecode).
    3. Baca literal string di content stream, hormati escape backslash dan
       kurung, lalu decode pasangan 2-byte dengan CMap font aktif (/Fx ... Tf).
    """
    def _decomp(data):
        try:
            return zlib.decompress(data)
        except Exception:
            return data

    def _stream_of(body):
        """Ambil isi stream (...endstream) dari body objek & decompress (FlateDecode)."""
        m = re.search(rb'stream\r?\n(.*?)\r?\nendstream', body, re.S)
        if not m:
            return b''
        return _decomp(m.group(1))

    # 1. Objek PDF: nomor → isi
    objs = {}
    for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj', pdf_bytes, re.S):
        objs[int(m.group(1))] = m.group(2)

    # 2. Font object → objek ToUnicode
    font_to_unicode = {}
    for num, body in objs.items():
        m = re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', body)
        if m:
            font_to_unicode[num] = int(m.group(1))

    # 3. Nama resource (/F1, /F2, ...) → objek font
    name_to_font = {}
    for body in objs.values():
        m = re.search(rb'/Font\s*<<(.*?)>>', body, re.S)
        if m:
            for fm in re.finditer(rb'/(F\d+)\s+(\d+)\s+0\s+R', m.group(1)):
                name_to_font[fm.group(1).decode()] = int(fm.group(2))

    # 4. CMap per nama font
    cmaps = {}
    for name, font_num in name_to_font.items():
        touni = font_to_unicode.get(font_num)
        if touni is None or touni not in objs:
            continue
        body = _stream_of(objs[touni])
        cmap = {}
        for part in body.split(b'endbfchar'):
            if b'beginbfchar' not in part:
                continue
            section = part.split(b'beginbfchar', 1)[1]
            for bm in re.finditer(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', section):
                code = int(bm.group(1), 16)
                uni = bm.group(2)
                cmap[code] = ''.join(
                    chr(int(uni[i:i + 4], 16)) for i in range(0, len(uni), 4))
        cmaps[name] = cmap

    # 5. Baca teks dari content stream
    def _decode(raw, cmap):
        # Fallback: string teks polos (font non-subset) → ASCII langsung
        if all(0x20 <= b < 0x7F for b in raw) and b'\x00' not in raw:
            return raw.decode('latin-1')
        out = []
        k = 0
        while k + 1 < len(raw):
            code = (raw[k] << 8) | raw[k + 1]
            ch = cmap.get(code, '')
            if ch:
                out.append(ch)
            k += 2
        return ''.join(out)

    texts = []
    for body in objs.values():
        stream = _stream_of(body)
        if b'BT' not in stream or b'Tj' not in stream:
            continue
        font = 'F1'
        out = []
        i, n = 0, len(stream)
        while i < n:
            fm = re.match(rb'/(F\d+)\s+[\d.]+\s+Tf', stream[i:])
            if fm:
                font = fm.group(1).decode()
                i += fm.end()
                continue
            if stream[i] == 0x28:  # '('
                j = i + 1
                buf = bytearray()
                while j < n:
                    c = stream[j]
                    if c == 0x5C and j + 1 < n:  # escape \
                        buf.append(stream[j + 1])
                        j += 2
                        continue
                    if c == 0x29:  # ')'
                        break
                    buf.append(c)
                    j += 1
                out.append(_decode(bytes(buf), cmaps.get(font, {})))
                i = j + 1
            else:
                i += 1
        texts.append(''.join(out))
    return '\n'.join(texts)


app = Flask(__name__)
app.secret_key = 'test-secret'
app.config['UPLOAD_FOLDER'] = 'uploads'


def _sample_purchase(status='verified'):
    return {
        'id': 1,
        'display_id': 'WTR-20260812-0001',
        'ob_name': 'BUDI',
        'purchase_date': date(2026, 8, 12),
        'created_at': datetime(2026, 8, 12, 9, 30),
        'status': status,
        'remark': 'Barang diterima sesuai pesanan',
        'note': 'Galon ditukar 2 unit kosong',
        'rejection_reason': 'Foto sebelum & sesudah identik',
        'verified_by': 'RINA',
        'verified_at': datetime(2026, 8, 12, 10, 0),
        'foto_before': None,
        'foto_after': None,
    }


def _sample_items():
    return [
        {'drink_type': 'Galon', 'brand': 'AQUA', 'satuan': 'galon', 'quantity': 3},
        {'drink_type': 'Botol', 'brand': 'Le Minerale', 'satuan': 'dus', 'quantity': 2},
    ]


class TestWaterReceiptPDF:
    def test_generate_verified_menghasilkan_pdf(self):
        """PDF terverifikasi berisi tabel item, remark, note, dan nama TTD."""
        from modules.pdf_generator import WaterReceiptPDF
        pdf = WaterReceiptPDF()
        pdf.add_page()
        pdf.generate(_sample_purchase('verified'), _sample_items(),
                     ga_name='ANDI', finance_name='RINA')
        raw = pdf.output(dest='S')
        pdf_bytes = raw.encode('latin-1') if isinstance(raw, str) else bytes(raw)
        assert pdf_bytes[:4] == b'%PDF'
        text = _pdf_text(pdf_bytes)
        assert 'TANDA TERIMA SERAH TERIMA AIR MINUM' in text
        assert 'AQUA' in text
        assert 'Le Minerale' in text
        # Nama penandatangan
        assert 'RINA' in text
        assert 'ANDI' in text
        # Status verifikasi & remark
        assert 'TERVERIFIKASI' in text
        assert 'Barang diterima sesuai pesanan' in text

    def test_generate_rejected_menampilkan_alasan(self):
        """PDF berstatus ditolak menampilkan alasan penolakan."""
        from modules.pdf_generator import WaterReceiptPDF
        pdf = WaterReceiptPDF()
        pdf.add_page()
        pdf.generate(_sample_purchase('rejected'), _sample_items(),
                     ga_name='ANDI', finance_name='RINA')
        raw = pdf.output(dest='S')
        pdf_bytes = raw.encode('latin-1') if isinstance(raw, str) else bytes(raw)
        assert pdf_bytes[:4] == b'%PDF'
        text = _pdf_text(pdf_bytes)
        assert 'DITOLAK' in text
        assert 'Foto sebelum & sesudah identik' in text

    def test_generate_pending_menampilkan_menunggu(self):
        """PDF status pending menampilkan keterangan menunggu verifikasi."""
        from modules.pdf_generator import WaterReceiptPDF
        pdf = WaterReceiptPDF()
        pdf.add_page()
        pdf.generate(_sample_purchase('pending'), _sample_items())
        raw = pdf.output(dest='S')
        pdf_bytes = raw.encode('latin-1') if isinstance(raw, str) else bytes(raw)
        text = _pdf_text(pdf_bytes)
        assert 'Menunggu verifikasi Finance' in text


class TestGetTtdNames:
    def test_ttd_names_dari_system_config(self, monkeypatch):
        """Nama TTD diambil dari system_config (di-set admin di /app/settings)."""
        import modules.routes_water as rw

        class FakeCursor:
            def execute(self, q, params=None):
                self._rows = [
                    {'config_key': 'water_ga_name', 'config_value': 'Andi Prasetyo'},
                    {'config_key': 'water_finance_name', 'config_value': 'Rina Wijaya'},
                ]
            def fetchall(self):
                return self._rows
            def close(self):
                pass

        class FakeConn:
            def cursor(self, dictionary=True):
                return FakeCursor()
            def close(self):
                pass

        def fake_get_db_connection():
            return FakeConn()

        monkeypatch.setattr(rw, 'get_db_connection', fake_get_db_connection)
        ga, finance = rw._get_ttd_names()
        assert ga == 'Andi Prasetyo'
        assert finance == 'Rina Wijaya'

    def test_ttd_names_kosong_saat_tidak_diset(self, monkeypatch):
        """Tanpa konfigurasi → string kosong (PDF memakai default label)."""
        import modules.routes_water as rw

        class FakeCursor:
            def execute(self, q, params=None):
                self._rows = []
            def fetchall(self):
                return self._rows
            def close(self):
                pass

        class FakeConn:
            def cursor(self, dictionary=True):
                return FakeCursor()
            def close(self):
                pass

        monkeypatch.setattr(rw, 'get_db_connection', lambda: FakeConn())
        ga, finance = rw._get_ttd_names()
        assert ga == ''
        assert finance == ''


class TestHomeForRoleOB:
    def test_role_ob_memiliki_halaman_sendiri(self):
        """OB login → diarahkan ke SPA /app/water (bukan dashboard back-office)."""
        assert ROLE_HOME.get('ob') == '/app/water'
        assert home_for_role('ob') == '/app/water'

    def test_role_backoffice_tetap_dashboard(self):
        assert home_for_role('finance') == '/app/dashboard'
        assert home_for_role('ga') == '/app/dashboard'
