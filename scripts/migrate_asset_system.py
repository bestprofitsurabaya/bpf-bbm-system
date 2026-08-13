"""Migrasi data bpf-asset-system (Streamlit/SQLite) ke BPF WorkHub (MySQL).

Sumber: ~/bpf-asset-system/data/bpf_ac_ai_system.db (DB real, bukan demo).
Yang dimigrasikan:
  - asset_ac          : 15 unit AC kantor (master)
  - vehicle_components: 12 komponen kendaraan + standar umur pakai
  - vehicle_assets    : 8 KENDARAAN ASLI KANTOR (dari tabel `vehicles`
                        WorkHub — Innova B 1126 DFC + 7 Avanza), bukan sample.
  - maintenance_logs / vehicle_service_logs : log lama TIDAK dimigrasikan
    (kosong di sumber) — mulai bersih; hanya master.

Pemakaian:
    python3 scripts/migrate_asset_system.py /path/ke/bpf_ac_ai_system.db [--reset]

--reset: kosongkan tabel aset dulu (default: INSERT IGNORE / tidak menimpa).
"""
import sys
from datetime import datetime

sys.path.insert(0, '.')
from modules.config import get_db_connection  # noqa: E402


def _clean(s):
    return (s or '').strip()


def _parse_date(s):
    s = _clean(s)
    if not s or s.lower() in ('none', 'null'):
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _num(v, default=0):
    try:
        return int(float(v or default))
    except (TypeError, ValueError):
        return default


def main():
    if len(sys.argv) < 2:
        print('Pemakaian: python3 scripts/migrate_asset_system.py <sqlite.db> [--reset]')
        sys.exit(1)
    db_path = sys.argv[1]
    do_reset = '--reset' in sys.argv

    import sqlite3
    src = sqlite3.connect(db_path)
    src.row_factory = sqlite3.Row

    conn = get_db_connection()
    if not conn:
        print('❌ DB MySQL tidak tersedia')
        sys.exit(1)
    cur = conn.cursor(dictionary=True)

    if do_reset:
        for t in ('maintenance_recommendations', 'vehicle_service_logs', 'asset_ac_logs',
                  'vehicle_assets', 'vehicle_components', 'asset_ac'):
            cur.execute(f'DELETE FROM {t}')
        conn.commit()
        print('🧹 Tabel aset dikosongkan (reset).')

    # ---------- 1. Master AC ----------
    ac_rows = src.execute('SELECT * FROM assets').fetchall()
    n_ac = 0
    for r in ac_rows:
        cur.execute(
            """INSERT IGNORE INTO asset_ac
               (asset_id, merk, tipe, kapasitas, lokasi, refrigerant,
                installation_date, warranty_until, last_maintenance, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (_clean(r['asset_id']), _clean(r['merk']), _clean(r['tipe']),
             _clean(r['kapasitas']), _clean(r['lokasi']), _clean(r['refrigerant']),
             _parse_date(r['installation_date']), _parse_date(r['warranty_until']),
             _parse_date(r['last_maintenance']), _clean(r['status']) or 'Aktif'))
        n_ac += cur.rowcount
    print(f'✅ AC dimigrasikan: {n_ac} (dari {len(ac_rows)})')

    # ---------- 2. Komponen kendaraan ----------
    comp_rows = src.execute('SELECT * FROM vehicle_components').fetchall()
    n_comp = 0
    for r in comp_rows:
        cur.execute(
            """INSERT IGNORE INTO vehicle_components
               (component_name, standard_life_km, standard_life_months, category,
                priority, estimated_cost, is_active, notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (_clean(r['component_name']), _num(r['standard_life_km']),
             _num(r['standard_life_months']), _clean(r['category']),
             _num(r['priority'], 1), float(r['estimated_cost'] or 0),
             1 if r['is_active'] else 0, _clean(r['notes'])))
        n_comp += cur.rowcount
    print(f'✅ Komponen kendaraan: {n_comp} (dari {len(comp_rows)})')

    # ---------- 3. Kendaraan ASLI kantor (dari tabel vehicles WorkHub) ----------
    cur.execute("""SELECT v.id, v.nopol, v.vehicle_type, v.brand
                   FROM vehicles v WHERE v.is_active=1 ORDER BY v.vehicle_type, v.nopol""")
    veh_rows = cur.fetchall()
    n_veh = 0
    for r in veh_rows:
        nopol = _clean(r['nopol'])
        if not nopol:
            continue
        cur.execute(
            """INSERT IGNORE INTO vehicle_assets
               (vehicle_id, nopol, vehicle_type, brand, status)
               VALUES (%s,%s,%s,%s,'Aktif')""",
            (r['id'], nopol, _clean(r['vehicle_type']), _clean(r['brand'])))
        n_veh += cur.rowcount
    print(f'✅ Kendaraan asli kantor: {n_veh} (dari {len(veh_rows)} aktif)')

    conn.commit()
    cur.close()
    conn.close()
    src.close()
    print('🎉 Migrasi aset selesai.')


if __name__ == '__main__':
    main()
