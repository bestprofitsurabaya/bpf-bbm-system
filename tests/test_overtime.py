"""Sistem Overtime (v2.22) — GA HR: Driver (sinkronisasi Google Sheet)
+ OB/Security (migrasi penuh & form publik).

Jalankan:
    docker exec bbm_web python3 -m pytest tests/test_overtime.py -v
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.overtime_helpers import (clean, norm_key, map_headers,
                                      parse_date_mdy, parse_time_12h,
                                      parse_submitted_at, normalize_name,
                                      guess_position)
from modules.helpers import home_for_role, ROLE_HOME


# ============================================================
# Parser kolom Google Sheet
# ============================================================
class TestHeaderMapping:
    """Header form Google Form asli (sheet OB/Security) dipetakan benar."""

    def test_headers_ob_security(self):
        m = map_headers([
            'Timestamp', 'Email Address', 'Nama Lengkap', 'Tanggal',
            'Waktu Mulai Overtime', 'Waktu Selesai Overtime', 'Keterangan',
            'Upload Foto Mulai OT menggunakan Timestamp. ',
            'Upload Foto Selesai OT menggunakan Timestamp. ',
        ])
        assert m['submitted_at'] == 0
        assert m['email'] == 1
        assert m['nama'] == 2
        assert m['tanggal'] == 3
        assert m['waktu_mulai'] == 4
        assert m['waktu_selesai'] == 5
        assert m['keterangan'] == 6
        assert m['foto_mulai'] == 7
        assert m['foto_selesai'] == 8

    def test_headers_sederhana(self):
        m = map_headers(['Nama', 'Tanggal', 'Mulai', 'Selesai', 'Catatan'])
        assert m['nama'] == 0 and m['tanggal'] == 1
        assert m['waktu_mulai'] == 2 and m['waktu_selesai'] == 3
        assert m['keterangan'] == 4

    def test_header_tidak_dikenal_diabaikan(self):
        m = map_headers(['Score', 'Foo Bar', 'Nama Lengkap'])
        assert m['nama'] == 2
        assert 'score' not in m


class TestDateParsing:
    def test_parse_date_mdy(self):
        assert parse_date_mdy('1/5/2026') == '2026-01-05'
        assert parse_date_mdy('12/25/2026') == '2026-12-25'
        assert parse_date_mdy('1/5/2026 20:32:44') == '2026-01-05'
        assert parse_date_mdy('') is None
        assert parse_date_mdy('abc') is None

    def test_parse_time_12h(self):
        assert parse_time_12h('6:29:00 PM') == '18:29'
        assert parse_time_12h('8:32:00 PM') == '20:32'
        assert parse_time_12h('6:30:00 AM') == '06:30'
        assert parse_time_12h('12:00:00 PM') == '12:00'
        assert parse_time_12h('12:30:00 AM') == '00:30'
        assert parse_time_12h('') is None
        assert parse_time_12h('n/a') is None

    def test_parse_submitted_at(self):
        assert parse_submitted_at('1/5/2026 20:32:44') == '2026-01-05 20:32:44'
        assert parse_submitted_at('') is None


# ============================================================
# Normalisasi nama & posisi (data sheet lama banyak typo)
# ============================================================
class TestNormalizeName:
    def test_nama_baku(self):
        assert normalize_name('Edwin P') == 'Edwin P'
        assert normalize_name('Muhajir') == 'Muhajir'

    def test_typo_dibakukan(self):
        assert normalize_name('Edwin p') == 'Edwin P'
        assert normalize_name('Febru') == 'Febri'
        assert normalize_name('Febrj') == 'Febri'
        assert normalize_name('Faissol') == 'Faisol'
        assert normalize_name('Faisool') == 'Faisol'
        assert normalize_name('Fasol') == 'Faisol'

    def test_kosong(self):
        assert normalize_name('') == ''
        assert normalize_name('  ') == ''


class TestGuessPosition:
    def test_muhajir_security(self):
        assert guess_position('Muhajir') == 'Security'
        assert guess_position('muhajir') == 'Security'

    def test_sisanya_ob(self):
        assert guess_position('Edwin P') == 'OB'
        assert guess_position('Febri') == 'OB'
        assert guess_position('Faisol') == 'OB'


# ============================================================
# Role GA HR — halaman sendiri
# ============================================================
class TestGaHrRole:
    def test_home_for_role(self):
        assert ROLE_HOME['ga_hr'] == '/app/ga-hr'
        assert home_for_role('ga_hr') == '/app/ga-hr'


# ============================================================
# Fetch sumber sheet: CSV publik & JSON Apps Script Web App
# ============================================================
class TestFetchSheetRows:
    def _fake_get(self, body, url='https://example.test/x', is_json=False):
        import modules.routes_overtime as ro

        class FakeResp:
            def __init__(self):
                self.content = body.encode('utf-8-sig')
                self._json = is_json
            def raise_for_status(self):
                pass
            def json(self):
                import json as _j
                return _j.loads(body)

        def fake_get(url_, timeout=30, headers=None):
            assert url_ == url
            return FakeResp()

        import modules.routes_overtime as ro
        ro.requests.get = fake_get
        return ro

    def test_fetch_csv(self):
        ro = self._fake_get(
            '"Timestamp","Nama Lengkap","Tanggal","Waktu Mulai Overtime","Waktu Selesai Overtime"\n'
            '"1/5/2026 20:32:44","Muhajir","1/5/2026","6:29:00 PM","8:32:00 PM"\n')
        rows = ro._fetch_sheet_rows('https://example.test/x')
        assert len(rows) == 1
        assert rows[0]['Nama Lengkap'] == 'Muhajir'

    def test_fetch_json_apps_script(self):
        ro = self._fake_get(
            '{"rows": [{"Nama Lengkap": "Edwin P", "Tanggal": "1/5/2026", "Waktu Mulai Overtime": "6:00:00 PM"}]}',
            is_json=True)
        rows = ro._fetch_sheet_rows('https://example.test/x')
        assert len(rows) == 1
        assert rows[0]['Nama Lengkap'] == 'Edwin P'

    def test_fetch_kosong(self):
        ro = self._fake_get('{"rows": []}', is_json=True)
        assert ro._fetch_sheet_rows('https://example.test/x') == []


# ============================================================
# Logika migrasi sheet lama (unit — tanpa DB)
# ============================================================
class TestMigrationLogic:
    def _load(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'migrate_ot', os.path.join(os.path.dirname(__file__), '..',
                                       'scripts', 'migrate_overtime_ob_security.py'))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_uid_berbeda_per_baris(self):
        m = self._load()
        r1 = {'Timestamp': '1/5/2026 20:32:44', 'Nama Lengkap': 'Muhajir'}
        r2 = {'Timestamp': '1/6/2026 22:01:18', 'Nama Lengkap': 'Muhajir'}
        assert m._uid(r1, 0) != m._uid(r2, 1)

    def test_uid_sama_untuk_baris_identik(self):
        m = self._load()
        r = {'Timestamp': '1/5/2026 20:32:44', 'Nama Lengkap': 'Muhajir'}
        assert m._uid(r, 0) == m._uid(dict(r), 0)


class TestClean:
    def test_normalisasi_spasi(self):
        assert clean('  Edwin   P  ') == 'Edwin P'
        assert clean('') == ''


# ============================================================
# Laporan PDF Overtime (berlogo, TTD GA HR)
# ============================================================
class TestOvertimePDF:
    def _mk_pdf(self, rows, modul='driver'):
        import io
        from modules.pdf_generator import OvertimeReportPDF
        pdf = OvertimeReportPDF()
        pdf.generate(rows, modul=modul, date_label='2026-08-01 s/d 2026-08-14',
                     filters={'Posisi': 'OB'}, generated_by='GA HR Officer')
        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    def test_generate_empty_rows(self):
        from tests.test_water import _pdf_text
        data = self._mk_pdf([])
        assert data.startswith(b'%PDF')
        assert b'%%EOF' in data[-32:]
        assert 'LAPORAN OVERTIME' in _pdf_text(data)

    def test_generate_driver(self):
        from tests.test_water import _pdf_text
        rows = [{
            'tanggal': date(2026, 8, 13), 'nama': 'Andi Driver',
            'waktu_mulai': '18:00', 'waktu_selesai': '21:00',
            'keterangan': 'OT malam', 'email': 'andi@mail.com',
        }]
        data = self._mk_pdf(rows, 'driver')
        txt = _pdf_text(data)
        assert 'LAPORAN OVERTIME' in txt
        assert 'ANDI DRIVER' in txt.upper() or 'Andi' in txt
        assert 'OT MALAM' in txt.upper() or 'OT malam' in txt
        assert 'GA HR' in txt.upper()

    def test_generate_ob_security(self):
        from tests.test_water import _pdf_text
        rows = [{
            'tanggal': date(2026, 8, 13), 'nama': 'Muhajir',
            'posisi': 'Security', 'waktu_mulai': '18:30', 'waktu_selesai': '22:00',
            'keterangan': 'Keamanan kantor',
        }]
        data = self._mk_pdf(rows, 'ob')
        txt = _pdf_text(data)
        assert 'OB & SECURITY' in txt.upper() or 'Overtime OB' in txt
        assert 'SECURITY' in txt.upper()
        assert 'MUHAJIR' in txt.upper()
