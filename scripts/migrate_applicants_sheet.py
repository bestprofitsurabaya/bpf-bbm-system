"""Migrasi data pelamar kerja dari Google Sheet (CSV) ke database BPF WorkHub.

Sumber: https://docs.google.com/spreadsheets/d/1VIavwXGX1e9R6dbfkmLltEUo0QgpgDEalUPxD2SF8a0
(diekspor sebagai CSV: File > Unduh > CSV).

Pemakaian:
    python3 scripts/migrate_applicants_sheet.py /path/ke/export.csv [--reset]

Perilaku:
  - Selalu MENGOSONGKAN tabel applicants + applicant_attendance terlebih dahulu
    (--reset) sehingga DB hanya berisi data dari Google Sheet ini (permintaan
    "pastikan bersih, hanya ada data dari googlesheet tersebut").
  - Interview dianggap hadir otomatis (timestamp submit = waktu interview).
  - H1..H4 = TRUE -> catat kehadiran training hari bersangkutan dengan tanggal
    dari sheet; status mengikuti tahap terjauh.
  - Pulang = TRUE -> status 'resigned' dengan alasan (kolom Alasan; 'PULANG'
    bila kosong).
  - Kolom User kosong diisi '' (tetap tersimpan, tidak dipaksa pilih).
"""
import csv
import random
import string
import sys
from datetime import datetime

# Impor DB sesuai konfigurasi aplikasi
sys.path.insert(0, '.')
from modules.config import get_db_connection  # noqa: E402

VALID_STAGES = ('interview', 'training_1', 'training_2', 'training_3', 'training_4')
TRAINING_STAGES = ('training_1', 'training_2', 'training_3', 'training_4')


def parse_dt(date_str, time_str):
    """Gabung tanggal (M/D/YYYY) + jam (H:MM:SS) -> datetime."""
    date_str = (date_str or '').strip()
    time_str = (time_str or '').strip()
    if not date_str:
        return None
    try:
        if time_str:
            return datetime.strptime(f'{date_str} {time_str}', '%m/%d/%Y %H:%M:%S')
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        # Coba format alternatif
        try:
            return datetime.strptime(f'{date_str} {time_str}', '%m/%d/%Y %H:%M')
        except ValueError:
            print(f'  ⚠️ gagal parse tanggal {date_str!r} {time_str!r}')
            return None


def parse_date_only(date_str):
    """Tanggal M/D/YYYY -> date object."""
    date_str = (date_str or '').strip()
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        return None


def clean(s):
    """Trim + normalisasi spasi ganda (cth: 'TEAM  EDI 2' -> 'TEAM EDI 2')."""
    import re
    return re.sub(r'\s+', ' ', (s or '').strip())


def is_true(v):
    return str(v or '').strip().upper() == 'TRUE'


def gen_display_id(interview_at, idx):
    """PLM-YYYYMMDD-HHMMSS + 2 digit acak (unik per baris via idx)."""
    date_part = interview_at.strftime('%Y%m%d')
    time_part = interview_at.strftime('%H%M%S')
    rand = ''.join(random.choices(string.digits, k=2))
    return f'PLM-{date_part}-{time_part}{rand}-{idx % 100:02d}'


def main():
    if len(sys.argv) < 2:
        print('Pemakaian: python3 scripts/migrate_applicants_sheet.py <file.csv> [--reset]')
        sys.exit(1)
    csv_path = sys.argv[1]
    do_reset = '--reset' in sys.argv

    rows = list(csv.DictReader(open(csv_path, newline='', encoding='utf-8-sig')))
    print(f'📄 CSV: {len(rows)} baris dari {csv_path}')

    conn = get_db_connection()
    if not conn:
        print('❌ DB tidak tersedia')
        sys.exit(1)
    cursor = conn.cursor(dictionary=True)

    if do_reset:
        cursor.execute('DELETE FROM applicant_attendance')
        cursor.execute('DELETE FROM applicants')
        conn.commit()
        print('🧹 Tabel applicants + applicant_attendance dikosongkan (reset).')

    inserted = 0
    skipped = 0
    now = datetime.now()
    for idx, r in enumerate(rows):
        nama = clean(r.get('Nama Lengkap'))
        if not nama:
            skipped += 1
            continue
        interview_at = parse_dt(r.get('Tanggal Interview'), r.get('Jam'))
        if not interview_at:
            skipped += 1
            continue

        # Status awal: interview (hadir otomatis). Naik per tahap terjauh.
        status = 'interview'
        att = []  # (stage, attended_at, note)

        # Interview selalu dianggap hadir (timestamp submit).
        att.append(('interview', interview_at, 'Migrasi Google Sheet'))

        for i, stage in enumerate(TRAINING_STAGES, start=1):
            if is_true(r.get(f'H{i}')):
                d = parse_date_only(r.get(f'Tanggal H{i}'))
                attended = datetime.combine(d, interview_at.time()) if d else now
                att.append((stage, attended, 'Migrasi Google Sheet'))
                status = stage

        # Pulang (mengundurkan diri) -> status resigned + alasan
        if is_true(r.get('Pulang')):
            status = 'resigned'
            reason = clean(r.get('Alasan')) or 'PULANG'
        else:
            reason = ''

        display_id = gen_display_id(interview_at, idx)
        cursor.execute(
            """INSERT INTO applicants
               (display_id, nama_lengkap, pendidikan, no_hp, upline, user_field,
                posisi, interview_at, status, resign_reason, created_at, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (display_id, nama, clean(r.get('Pendidikan Terakhir'))[:100],
             clean(r.get('Nomor Telepon/HP'))[:30], clean(r.get('UPLINE'))[:100],
             clean(r.get('User'))[:100], clean(r.get('Posisi Yang Dilamar'))[:100],
             interview_at, status, reason, interview_at, interview_at))
        appt_id = cursor.lastrowid

        for stage, attended_at, note in att:
            cursor.execute(
                """INSERT INTO applicant_attendance
                   (applicant_id, stage, attended_at, marked_by, note)
                   VALUES (%s,%s,%s,%s,%s)""",
                (appt_id, stage, attended_at, 'System (migrasi)', note))
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f'✅ {inserted} pelamar dimigrasikan (skipped: {skipped}).')
    # Ringkasan status
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT status, COUNT(*) c FROM applicants GROUP BY status ORDER BY c DESC')
    for r in cursor.fetchall():
        print(f'   {r["status"]}: {r["c"]}')
    cursor.close(); conn.close()


if __name__ == '__main__':
    main()
