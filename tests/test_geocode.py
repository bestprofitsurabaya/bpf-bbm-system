"""Unit Tests untuk perbaikan v2.15.1:
- Fallback query geocoding (alamat Indonesia dengan 'Jl./No' sering gagal di Nominatim)
- Format visit_time 'HH:MM' dari nilai TIME DB (timedelta / string)

Jalankan:
    python3 -m pytest tests/test_geocode.py -v
"""

import sys
import os
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.geocode import _query_variants
from modules.routes_appointments import _fmt_visit_time


# ================================================================
# TEST 1: Varian query geocoding
# ================================================================
class TestQueryVariants:
    def test_buang_jl_dan_no(self):
        v = _query_variants('Jl. Rungkut Industri Raya No 12, Surabaya')
        assert v[0] == 'Jl. Rungkut Industri Raya No 12, Surabaya'
        assert 'Rungkut Industri Raya 12, Surabaya' in v, v

    def test_buang_nomor_rumah(self):
        v = _query_variants('Jl. Lakarsantri 45, Surabaya')
        assert 'Lakarsantri 45, Surabaya' in v, v
        assert 'Lakarsantri, Surabaya' in v, v

    def test_alamat_bersih_tidak_diubah(self):
        v = _query_variants('Rungkut Menanggal, Surabaya')
        assert v == ['Rungkut Menanggal, Surabaya']

    def test_maksimal_tiga_varian(self):
        assert len(_query_variants('Jl. Rungkut Industri Raya No 12, Surabaya')) <= 3

    def test_buang_rt_rw(self):
        v = _query_variants('Jl. A No 1 RT 02 RW 03, Surabaya')
        assert any('rt 02' not in x.lower() and 'rw 03' not in x.lower() for x in v[1:]), v


# ================================================================
# TEST 2: Format visit_time dari nilai DB
# ================================================================
class TestFmtVisitTime:
    def test_timedelta_satu_digit_jam(self):
        # Bug nyata: str(timedelta(hours=9)) = '9:00:00' -> [:5] jadi '9:00:'
        assert _fmt_visit_time(timedelta(hours=9)) == '09:00'
        assert _fmt_visit_time(timedelta(hours=14, minutes=30)) == '14:30'

    def test_string_db(self):
        assert _fmt_visit_time('09:30:00') == '09:30'
        assert _fmt_visit_time('9:30:00') == '09:30'
        assert _fmt_visit_time('08:00') == '08:00'

    def test_none_dan_aneh(self):
        assert _fmt_visit_time(None) is None
        assert _fmt_visit_time('') == ''


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])
