"""Unit Tests untuk Route Optimizer (v2.15) — penugasan rute appointment ke driver.
Algoritma: greedy insertion urut-jam + load balancing (modules/route_optimizer.py).

Jalankan:
    python3 -m pytest tests/test_route_optimizer.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.route_optimizer import (
    haversine_km,
    estimate_travel_minutes,
    time_to_minutes,
    is_time_feasible,
    estimate_bbm_liters,
    estimate_bbm_cost,
    plan_routes,
)

# Koordinat realistis Surabaya & sekitarnya (derajat)
DEPOT = {'lat': -7.2566, 'lng': 112.7424}   # Tunjungan / pusat kota
RUNGKUT_1 = {'lat': -7.3227, 'lng': 112.7772}  # Rungkut (timur)
RUNGKUT_2 = {'lat': -7.3180, 'lng': 112.7850}  # Rungkut Menanggal (timur)
WIYUNG_1 = {'lat': -7.3060, 'lng': 112.6780}   # Wiyung (barat daya)
WIYUNG_2 = {'lat': -7.2900, 'lng': 112.6700}   # Lakarsantri (barat daya)


def appt(aid, point, sesi='1', visit_time='09:00', driver=None, **extra):
    """Helper membuat dict appointment untuk plan_routes."""
    a = {'id': aid, 'sesi': sesi, 'visit_time': visit_time, 'driver': driver,
         'lat': point.get('lat'), 'lng': point.get('lng'),
         'display_id': 'APP-%s' % aid, 'nasabah_name': 'Nasabah %s' % aid}
    a.update(extra)
    return a


# ================================================================
# TEST 1: Haversine & waktu tempuh
# ================================================================
class TestDistance:
    def test_jarak_tunjungan_rungkut(self):
        km = haversine_km(DEPOT['lat'], DEPOT['lng'], RUNGKUT_1['lat'], RUNGKUT_1['lng'])
        assert 5 < km < 15, 'Jarak Tunjungan-Rungkut wajar: %s km' % km

    def test_jarak_nol(self):
        assert haversine_km(-7.2, 112.7, -7.2, 112.7) == 0.0

    def test_koordinat_tidak_valid(self):
        assert haversine_km(None, 112.7, -7.2, 112.7) is None
        assert haversine_km(-7.2, 999, -7.2, 112.7) is None

    def test_waktu_tempuh(self):
        # 30 km dengan kecepatan 30 km/jam = 60 menit
        assert estimate_travel_minutes(30, 30) == 60.0
        assert estimate_travel_minutes(0) == 0.0
        assert estimate_travel_minutes(10, 0) == 0.0


# ================================================================
# TEST 2: Waktu (time window)
# ================================================================
class TestTimeWindow:
    def test_parse(self):
        assert time_to_minutes('08:30') == 510
        assert time_to_minutes('14:30') == 870
        assert time_to_minutes('') is None
        assert time_to_minutes('abc') is None

    def test_feasible(self):
        # 08:30 + 15 menit perjalanan -> tiba 08:45, kunjungan 08:45 feasible
        assert is_time_feasible('08:30', '08:45', 15) is True
        assert is_time_feasible('08:30', '08:40', 15) is False
        # tanpa jam -> selalu feasible
        assert is_time_feasible(None, '09:00', 60) is True
        assert is_time_feasible('09:00', None, 60) is True


# ================================================================
# TEST 3: BBM estimate
# ================================================================
class TestBBM:
    def test_liter(self):
        assert estimate_bbm_liters(120, 12) == 10.0
        assert estimate_bbm_liters(0, 12) == 0.0

    def test_biaya(self):
        assert estimate_bbm_cost(10, 10000) == 100000


# ================================================================
# TEST 4: Pembagian rute searah (klaster geografis)
# ================================================================
class TestPlanRoutes:
    def test_dua_klaster_dua_driver(self):
        """Klaster timur & barat -> tiap driver mendapat satu klaster (searah)."""
        appointments = [
            appt(1, RUNGKUT_1, '1', '09:00'),
            appt(2, RUNGKUT_2, '1', '09:30'),
            appt(3, WIYUNG_1, '1', '10:00'),
            appt(4, WIYUNG_2, '1', '10:30'),
        ]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        assert len(plan['drivers']) == 2
        by_id = {}
        for d in plan['drivers']:
            assert len(d['visits']) == 2
            for v in d['visits']:
                by_id[v['id']] = d['driver']
        # Rungkut berpasangan, Wiyung berpasangan (bukan campur)
        assert by_id[1] == by_id[2]
        assert by_id[3] == by_id[4]
        assert by_id[1] != by_id[3]
        assert plan['totals']['assigned'] == 4
        assert plan['totals']['unassigned'] == 0

    def test_urutan_kunjungan_mengikuti_jam(self):
        appointments = [
            appt(1, RUNGKUT_1, '1', '10:00'),
            appt(2, WIYUNG_1, '1', '08:30'),
            appt(3, RUNGKUT_2, '1', '09:15'),
        ]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        for d in plan['drivers']:
            times = [time_to_minutes(v['visit_time']) for v in d['visits']]
            assert times == sorted(times), 'Urutan kunjungan harus sesuai jam'

    def test_penugasan_manual_tetap_dihormati(self):
        """Appointment yang sudah ditugaskan (fixed) tidak dipindahkan."""
        appointments = [
            appt(1, RUNGKUT_1, '1', '09:00', driver='BETA'),
            appt(2, RUNGKUT_2, '1', '09:30'),
            appt(3, WIYUNG_1, '1', '10:00'),
        ]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        for d in plan['drivers']:
            ids = [v['id'] for v in d['visits']]
            if 1 in ids:
                assert d['driver'] == 'BETA', 'Penugasan manual tidak boleh diubah'

    def test_beban_merata_klaster_tunggal(self):
        """Banyak appointment di lokasi sama -> beban terbagi rata (load balance)."""
        appointments = [appt(i, RUNGKUT_1, '1', '09:%02d' % i)
                        for i in range(1, 6)]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        sizes = sorted(len(d['visits']) for d in plan['drivers'])
        assert sizes[-1] - sizes[0] <= 1, 'Beban tidak merata: %s' % sizes

    def test_tanpa_koordinat_jadi_unassigned(self):
        appointments = [
            appt(1, RUNGKUT_1, '1', '09:00'),
            {'id': 2, 'sesi': '1', 'visit_time': '09:30', 'driver': None,
             'lat': None, 'lng': None, 'display_id': 'APP-2', 'nasabah_name': 'Tanpa Koordinat'},
        ]
        plan = plan_routes(appointments, ['ALFA'], depot=DEPOT)
        assert plan['totals']['assigned'] == 1
        assert plan['totals']['unassigned'] == 1
        assert plan['unassigned'][0]['unassigned_reason'] == 'no_coordinates'

    def test_tanpa_driver_tidak_error(self):
        plan = plan_routes([appt(1, RUNGKUT_1, '1', '09:00')], [], depot=DEPOT)
        assert plan['totals']['unassigned'] == 1

    def test_total_jarak_termasuk_ke_kantor(self):
        """Rute 1 kunjungan -> total km = jarak depot -> kunjungan."""
        plan = plan_routes([appt(1, {'lat': 0, 'lng': 1}, '1', '09:00')],
                           ['ALFA'], depot={'lat': 0, 'lng': 0})
        assert 110 < plan['totals']['km'] < 113  # ~111 km (1 derajat lintang)

    def test_konsistensi_area_antar_sesi(self):
        """Sesi dioptimalkan per sesi, tapi driver yang sama bisa cover area yang
        sama di sesi 1 dan sesi 2 (jarak waktu ±6 jam) — efisien & wajar."""
        appointments = [
            appt(1, RUNGKUT_1, '1', '09:00'),
            appt(2, WIYUNG_1, '1', '09:30'),
            appt(3, RUNGKUT_2, '2', '14:30'),
            appt(4, WIYUNG_2, '2', '15:00'),
        ]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        assert plan['totals']['assigned'] == 4
        by_id = {v['id']: d['driver'] for d in plan['drivers'] for v in d['visits']}
        # Driver Rungkut (sesi 1) tetap menangani Rungkut di sesi 2
        assert by_id[1] == by_id[3]
        assert by_id[2] == by_id[4]
        assert by_id[1] != by_id[2]

    def test_output_meta(self):
        plan = plan_routes([appt(1, RUNGKUT_1)], ['ALFA'], depot=DEPOT)
        assert plan['meta']['algorithm'] == 'greedy_time_ordered_insertion'
        assert plan['totals']['km'] > 0
        assert plan['drivers'][0]['est_bbm_cost'] > 0

    def test_penghematan_vs_baseline(self):
        """Rute otomatis (klaster searah) lebih hemat daripada round-robin biasa."""
        appointments = [
            appt(1, RUNGKUT_1, '1', '09:00'),
            appt(2, RUNGKUT_2, '1', '09:30'),
            appt(3, WIYUNG_1, '1', '10:00'),
            appt(4, WIYUNG_2, '1', '10:30'),
        ]
        plan = plan_routes(appointments, ['ALFA', 'BETA'], depot=DEPOT)
        assert plan['totals']['baseline_km'] > plan['totals']['km']
        assert plan['totals']['savings_percent'] > 0
        assert plan['totals']['savings_km'] > 0
        assert plan['totals']['savings_bbm_liter'] > 0
        assert plan['totals']['savings_bbm_cost'] > 0

    def test_tanpa_penghematan_satu_driver(self):
        """Satu driver: rute otomatis = baseline (tidak ada penghematan)."""
        plan = plan_routes(
            [appt(1, RUNGKUT_1, '1', '09:00'), appt(2, WIYUNG_1, '1', '10:00')],
            ['ALFA'], depot=DEPOT)
        assert plan['totals']['baseline_km'] == plan['totals']['km']
        assert plan['totals']['savings_percent'] == 0.0
        assert plan['totals']['savings_bbm_liter'] == 0.0


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])
