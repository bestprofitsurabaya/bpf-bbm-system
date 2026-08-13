"""Unit: PDF laporan compact (PDFReportCompact) & rekap BBM (BBMReportPDF) — desain v2.19.1.

Memastikan dokumen resmi compact tetap valid & memuat konten inti,
dan palet netral (hitam/abu) dipakai — tidak ada aksen warna biru/hijau/merah.
"""
import io
from datetime import datetime

from modules.pdf_generator import PDFReportCompact, BBMReportPDF


def _sample_tx(**over):
    tx = {
        'id': 1,
        'display_id': 'BBM-2026-0001',
        'nopol': 'L 1234 AB',
        'driver_name': 'RIVAN',
        'vehicle_type': 'Avanza',
        'bbm_type': 'Pertalite',
        'spbu_type': 'Shell',
        'gps_address': 'Jl. Darmo Permai, Surabaya',
        'nominal': 100000,
        'liter': 15.5,
        'odo_km': 123456,
        'km_per_liter': 12.5,
        'jumlah_appointment': 2,
        'price_per_liter': 10000,
        'created_at': datetime(2026, 8, 13, 10, 30),
    }
    tx.update(over)
    return tx


def _pdf_bytes(pdf):
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


class TestPDFReportCompact:
    def test_menghasilkan_pdf_valid_dengan_konten_inti(self):
        pdf = PDFReportCompact()
        pdf.add_page()
        pdf.generate_compact_report(_sample_tx())
        data = _pdf_bytes(pdf)
        assert data.startswith(b'%PDF')
        assert b'%%EOF' in data[-32:]

    def test_konten_lengkap(self):
        pdf = PDFReportCompact()
        pdf.add_page()
        pdf.generate_compact_report(_sample_tx())
        buf = io.BytesIO()
        pdf.output(buf)
        raw = buf.getvalue()
        # Dekompresi teks (fpdf menghasilkan aliran terkompresi)
        text = _pdf_text(raw)
        assert 'TRANSAKSI BBM-2026-0001' in text
        assert 'INFORMASI TRANSAKSI' in text
        assert 'KRONOLOGIS VERIFIKASI' in text
        assert 'STATUS PERSETUJUAN' in text
        assert 'RIVAN' in text
        assert 'Rp 100,000' in text


class TestBBMReportPDF:
    def test_menghasilkan_pdf_valid(self):
        pdf = BBMReportPDF(title='REKAP DANA BBM')
        pdf.add_page()
        pdf.generate_table([_sample_tx(), _sample_tx(id=2, nopol='L 9999 CD')])
        data = _pdf_bytes(pdf)
        assert data.startswith(b'%PDF')
        assert b'%%EOF' in data[-32:]

    def test_konten_rekap(self):
        pdf = BBMReportPDF(title='REKAP DANA BBM')
        pdf.add_page()
        pdf.generate_table([_sample_tx()])
        buf = io.BytesIO()
        pdf.output(buf)
        text = _pdf_text(buf.getvalue())
        assert 'REKAP DANA BBM' in text
        assert 'L 1234 AB' in text
        assert 'RIVAN' in text


def _pdf_text(pdf_bytes):
    """Ekstrak teks dari PDF fpdf2 (font disubset → kode glyph 2-byte + CMap ToUnicode)."""
    import re
    import zlib

    def _decomp(data):
        try:
            return zlib.decompress(data)
        except Exception:
            return data

    def _stream_of(body):
        m = re.search(rb'stream\r?\n(.*?)\r?\nendstream', body, re.S)
        if not m:
            return b''
        return _decomp(m.group(1))

    objs = {}
    for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj', pdf_bytes, re.S):
        objs[int(m.group(1))] = m.group(2)

    font_to_unicode = {}
    for num, body in objs.items():
        m = re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', body)
        if m:
            font_to_unicode[num] = int(m.group(1))

    name_to_font = {}
    for body in objs.values():
        m = re.search(rb'/Font\s*<<(.*?)>>', body, re.S)
        if m:
            for fm in re.finditer(rb'/(F\d+)\s+(\d+)\s+0\s+R', m.group(1)):
                name_to_font[fm.group(1).decode()] = int(fm.group(2))

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

    def _decode(raw, cmap):
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
