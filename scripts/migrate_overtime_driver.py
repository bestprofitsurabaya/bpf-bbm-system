"""Migrasi penuh data Overtime DRIVER dari Google Sheet ke BPF WorkHub.

Sumber: URL Google Apps Script Web App ({"rows":[...]}, untuk sheet PRIVATE
— cukup akun dengan akses view/read-only, TIDAK perlu akun pemilik) ATAU
URL/file CSV export sheet (gviz atau File > Unduh > CSV).

Pemakaian:
    python3 scripts/migrate_overtime_driver.py "https://script.google.com/macros/s/.../exec"
    python3 scripts/migrate_overtime_driver.py "https://.../gviz/tq?tqx=out:csv"
    python3 scripts/migrate_overtime_driver.py /path/ke/export.csv [--reset]

Perilaku:
  - Baca JSON Apps Script / CSV, petakan kolom secara toleran (overtime_helpers).
  - Tanggal & jam ISO UTC dikonversi ke WIB (+7 jam).
  - Idempoten: kunci = sheet_row (nomor baris sheet). Baris yang sama TIDAK
    digandakan — jalankan ulang kapan pun untuk sinkronisasi penuh.
  - Kolom lengkap (v2.22.1): no_kendaraan, broker, manager, doc_url.
  - Tanpa --reset: data lama tetap ada. Gunakan --reset hanya bila ingin
    mengosongkan tabel overtime_driver dulu.
"""
import csv
import io
import sys

sys.path.insert(0, '.')

from modules.config import get_db_connection  # noqa: E402
from modules.overtime_helpers import (clean, map_headers,  # noqa: E402
                                      normalize_driver_row)


def _fetch_rows(source):
    """source = URL (http/https) atau path file CSV. Return list[dict]."""
    if source.startswith('http://') or source.startswith('https://'):
        import requests
        resp = requests.get(source, timeout=60,
                            headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        text = resp.content.decode('utf-8-sig', errors='replace')
        stripped = text.lstrip()
        if stripped.startswith('{'):
            data = resp.json()
            rows = data.get('rows') or []
            if not rows:
                return []
            return [{str(k): (v if v is not None else '') for k, v in r.items()}
                    for r in rows]
    else:
        text = open(source, newline='', encoding='utf-8-sig').read()
    reader = csv.DictReader(io.StringIO(text))
    return [{k: (v if v is not None else '') for k, v in r.items()} for r in reader]


def main():
    if len(sys.argv) < 2:
        print('Pemakaian: python3 scripts/migrate_overtime_driver.py <url|file.csv> [--reset]')
        sys.exit(1)
    source = sys.argv[1]
    do_reset = '--reset' in sys.argv

    rows = _fetch_rows(source)
    print(f'📄 Sumber: {len(rows)} baris')

    conn = get_db_connection()
    if not conn:
        print('❌ DB tidak tersedia')
        sys.exit(1)
    cursor = conn.cursor(dictionary=True)

    if do_reset:
        cursor.execute('DELETE FROM overtime_driver')
        conn.commit()
        print('🧹 Tabel overtime_driver dikosongkan (reset).')

    inserted = updated = skipped = 0
    if rows:
        headers = list(rows[0].keys())
        idx = map_headers(headers)
        for n, r in enumerate(rows):
            row = normalize_driver_row(r, headers, idx, n)
            if not row:
                skipped += 1
                continue
            cursor.execute(
                """INSERT INTO overtime_driver
                   (sheet_row, submitted_at, email, nama, tanggal, waktu_mulai,
                    waktu_selesai, keterangan, foto_mulai, foto_selesai, notes,
                    no_kendaraan, broker, manager, doc_url)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE
                     submitted_at=VALUES(submitted_at), email=VALUES(email),
                     nama=VALUES(nama), tanggal=VALUES(tanggal),
                     waktu_mulai=VALUES(waktu_mulai), waktu_selesai=VALUES(waktu_selesai),
                     keterangan=VALUES(keterangan), foto_mulai=VALUES(foto_mulai),
                     foto_selesai=VALUES(foto_selesai), notes=VALUES(notes),
                     no_kendaraan=VALUES(no_kendaraan), broker=VALUES(broker),
                     manager=VALUES(manager), doc_url=VALUES(doc_url)""",
                (row['sheet_row'], row['submitted_at'], row['email'],
                 row['nama'], row['tanggal'], row['waktu_mulai'],
                 row['waktu_selesai'], row['keterangan'], row['foto_mulai'],
                 row['foto_selesai'], row['notes'], row['no_kendaraan'],
                 row['broker'], row['manager'], row['doc_url']))
            if cursor.rowcount == 1:
                inserted += 1
            elif cursor.rowcount == 2:
                updated += 1
            else:
                skipped += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f'✅ {inserted} baru, {updated} diperbarui (skipped: {skipped}).')

    # Ringkasan
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) c FROM overtime_driver")
    print(f'   Total di tabel: {cursor.fetchone()["c"]}')
    cursor.execute("SELECT MIN(tanggal) a, MAX(tanggal) b FROM overtime_driver")
    r = cursor.fetchone()
    print(f'   Rentang tanggal: {r["a"]} s/d {r["b"]}')
    cursor.close(); conn.close()


if __name__ == '__main__':
    main()
