"""Migrasi penuh data Overtime OB & Security dari Google Sheet ke BPF WorkHub.

Sumber: https://docs.google.com/spreadsheets/d/1AsBq-rHssGmv5vHAzorrphZeNxchodkJQXz1wdBPoms
(diekspor sebagai CSV — File > Unduh > CSV, atau berikan URL gviz publik).

Pemakaian:
    python3 scripts/migrate_overtime_ob_security.py /path/ke/export.csv
    python3 scripts/migrate_overtime_ob_security.py "https://.../gviz/tq?tqx=out:csv"

Perilaku:
  - Baca CSV/URL, petakan kolom secara toleran (lihat overtime_helpers).
  - Nama dinormalisasi (typo: 'Edwin p' -> 'Edwin P', 'Faisool' -> 'Faisol').
  - Posisi ditebak dari nama (konfirmasi user 14/8/2026): Muhajir = Security,
    lainnya (Edwin P, Febri, Faisol) = OB.
  - Idempoten: source_uid = hash baris; baris yang sama TIDAK digandakan.
  - Tanpa --reset: data lama tetap ada. Gunakan --reset hanya bila ingin
    mengosongkan tabel overtime_ob_security dulu.
"""
import csv
import hashlib
import io
import sys
from datetime import datetime

sys.path.insert(0, '.')

from modules.config import get_db_connection  # noqa: E402
from modules.overtime_helpers import (clean, map_headers, parse_date_mdy,  # noqa: E402
                                      parse_time_12h, parse_submitted_at,
                                      normalize_name, guess_position)


def _fetch_rows(source):
    """source = path file CSV atau URL (http/https). Return list[dict]."""
    if source.startswith('http://') or source.startswith('https://'):
        import requests
        resp = requests.get(source, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        text = resp.content.decode('utf-8-sig', errors='replace')
    else:
        text = open(source, newline='', encoding='utf-8-sig').read()
    reader = csv.DictReader(io.StringIO(text))
    return [{k: (v if v is not None else '') for k, v in r.items()} for r in reader]


def _uid(r, idx):
    key = '|'.join(str(r.get(k) or '') for k in
                   ('Timestamp', 'Email Address', 'Nama Lengkap', 'Tanggal',
                    'Waktu Mulai Overtime', 'Waktu Selesai Overtime'))
    return hashlib.md5(f'{key}|{idx}'.encode('utf-8')).hexdigest()[:32]


def main():
    if len(sys.argv) < 2:
        print('Pemakaian: python3 scripts/migrate_overtime_ob_security.py <file.csv|url> [--reset]')
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
        cursor.execute('DELETE FROM overtime_ob_security')
        conn.commit()
        print('🧹 Tabel overtime_ob_security dikosongkan (reset).')

    inserted = 0
    skipped = 0
    if rows:
        headers = list(rows[0].keys())
        idx = map_headers(headers)
        for n, r in enumerate(rows):
            def g(field):
                i = idx.get(field)
                return clean(r[headers[i]]) if i is not None and i < len(headers) else ''
            nama = normalize_name(g('nama'))
            if not nama:
                skipped += 1
                continue
            tanggal = parse_date_mdy(g('tanggal')) or (g('tanggal') or '')[:10]
            if not tanggal or len(tanggal) != 10:
                skipped += 1
                continue
            posisi = guess_position(nama)
            cursor.execute(
                """INSERT IGNORE INTO overtime_ob_security
                   (display_id, nama, posisi, tanggal, waktu_mulai, waktu_selesai,
                    keterangan, foto_mulai, foto_selesai, email, source, source_uid)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'migrasi',%s)""",
                (f'OTL-MIGRASI-{n+1:05d}', nama, posisi, tanggal,
                 parse_time_12h(g('waktu_mulai')) or g('waktu_mulai'),
                 parse_time_12h(g('waktu_selesai')) or g('waktu_selesai'),
                 g('keterangan')[:500], g('foto_mulai')[:600],
                 g('foto_selesai')[:600], g('email')[:150], _uid(r, n)))
            if cursor.rowcount:
                inserted += 1
            else:
                skipped += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f'✅ {inserted} baris dimigrasikan (skipped: {skipped}).')

    # Ringkasan
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT posisi, COUNT(*) c FROM overtime_ob_security GROUP BY posisi")
    for r in cursor.fetchall():
        print(f'   {r["posisi"]}: {r["c"]}')
    cursor.execute("SELECT COUNT(*) c FROM overtime_ob_security")
    print(f'   Total: {cursor.fetchone()["c"]}')
    cursor.close(); conn.close()


if __name__ == '__main__':
    main()
