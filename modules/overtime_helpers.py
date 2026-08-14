"""Helper parsing data Google Sheet untuk sistem Overtime (v2.22).

Dipakai bersama oleh:
- modules/routes_overtime.py  (refresh sinkronisasi + form publik OB/Security)
- scripts/migrate_overtime_ob_security.py (migrasi penuh data lama)

Fokus: memetakan kolom Google Sheet (header bebas, sering berganti ejaan)
ke field database secara toleran, plus parsing tanggal (M/D/YYYY) & jam
(12 jam: "6:29:00 PM") seperti format response Google Form.
"""
import re
from datetime import datetime

# ============================================================
# Normalisasi teks
# ============================================================
def clean(s):
    """Trim + normalisasi spasi ganda + whitespace aneh."""
    return re.sub(r'\s+', ' ', (s or '').strip())


def norm_key(s):
    """Normalisasi untuk pencocokan header/nama: huruf kecil, tanpa aksen/spasi."""
    s = clean(s).lower()
    s = s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    s = s.replace('ä', 'a').replace('ö', 'o').replace('ü', 'u')
    return re.sub(r'[^a-z0-9]', '', s)


# ============================================================
# Pemetaan header sheet -> field DB (toleran ejaan)
# Setiap field punya daftar kata kunci (sudah di-norm_key).
# ============================================================
HEADER_MAP = {
    'submitted_at': ['timestamp', 'submittedat', 'tanggalwaktupengiriman', 'waktupengiriman'],
    'email': ['emailaddress', 'email', 'alamatemail'],
    'nama': ['namalengkap', 'nama', 'name', 'namakaryawan', 'karyawan', 'namapegawai'],
    'tanggal': ['tanggal', 'date', 'tanggalovertime', 'haritanggal'],
    'waktu_mulai': ['waktumulaiovertime', 'waktumulai', 'mulai', 'starttime', 'jamawal', 'jammulai', 'waktuawal'],
    'waktu_selesai': ['waktuselesaiovertime', 'waktuselesai', 'selesai', 'endtime', 'jamakhir', 'jamselesai', 'waktuakhir'],
    'keterangan': ['keterangan', 'notes', 'note', 'catatan', 'deskripsi', 'shift', 'uraian'],
    'foto_mulai': ['uploadfotomulaiot', 'fotomulai', 'uploadfotomulai', 'fotoawal'],
    'foto_selesai': ['uploadfotoselesaiot', 'fotoselesai', 'uploadfotoselesai', 'fotoakhir'],
    'posisi': ['posisi', 'jabatan', 'bagian', 'divisi'],
}


def map_headers(headers):
    """Petakan daftar header sheet ke {field: index}. Header tak dikenal diabaikan.

    Strategi two-pass:
      1. Pencocokan PERSIS (key == keyword) — header pendek standar.
      2. Header panjang/berisik (cth 'Upload Foto Mulai OT menggunakan
         Timestamp. ') dicocokkan dengan KEYWORD TERPANJANG yang merupakan
         substring key — paling spesifik, paling aman dari false-positive.

    >>> m = map_headers(['Timestamp', 'Email Address', 'Nama Lengkap', 'Tanggal',
    ...                  'Waktu Mulai Overtime', 'Waktu Selesai Overtime', 'Keterangan',
    ...                  'Upload Foto Mulai OT menggunakan Timestamp. ',
    ...                  'Upload Foto Selesai OT menggunakan Timestamp. '])
    >>> m['nama'] == 2 and m['tanggal'] == 3 and m['waktu_mulai'] == 4
    True
    >>> m['waktu_selesai'] == 5 and m['foto_mulai'] == 7 and m['foto_selesai'] == 8
    True
    """
    keys = [norm_key(h) for h in headers]
    out = {}
    # Pass 1: persis
    for idx, key in enumerate(keys):
        for field, kws in HEADER_MAP.items():
            if field in out:
                continue
            if key in kws:
                out[field] = idx
                break
    # Pass 2: keyword terpanjang yang menjadi substring key
    for idx, key in enumerate(keys):
        if not key:
            continue
        best_field, best_len = None, -1
        for field, kws in HEADER_MAP.items():
            if field in out:
                continue
            for kw in kws:
                if kw and kw in key and len(kw) > best_len:
                    best_field, best_len = field, len(kw)
        if best_field is not None:
            out[best_field] = idx
    return out


# ============================================================
# Parsing tanggal & jam (format Google Form)
# ============================================================
def parse_date_mdy(value):
    """Tanggal 'M/D/YYYY' -> 'YYYY-MM-DD' atau None. Toleran 'M/D/YYYY HH:MM:SS'."""
    s = clean(value)
    if not s:
        return None
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if not m:
        return None
    try:
        return datetime(int(m.group(3)), int(m.group(1)), int(m.group(2))).date().isoformat()
    except ValueError:
        return None


def parse_time_12h(value):
    """Jam '6:29:00 PM' -> '18:29' atau '06:29'. Return string HH:MM 24 jam / None."""
    s = clean(value)
    if not s:
        return None
    m = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AP]M)?$', s, re.I)
    if not m:
        return None
    hh, mm = int(m.group(1)), int(m.group(2))
    ampm = (m.group(4) or '').upper()
    if ampm == 'PM' and hh < 12:
        hh += 12
    elif ampm == 'AM' and hh == 12:
        hh = 0
    if mm > 59:
        return None
    return f'{hh:02d}:{mm:02d}'


def parse_submitted_at(value):
    """Timestamp submit '1/5/2026 20:32:44' -> 'YYYY-MM-DD HH:MM:SS' / None."""
    s = clean(value)
    if not s:
        return None
    for fmt in ('%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
    return None


# ============================================================
# Normalisasi nama karyawan (typo dari input manual Google Form)
# ============================================================
# Peta ejaan salah -> ejaan baku. Kunci di-norm_key.
NAME_CANONICAL = {
    'edwinp': 'Edwin P',
    'muhajir': 'Muhajir',
    'febri': 'Febri',
    'febru': 'Febri',
    'febrj': 'Febri',
    'faisol': 'Faisol',
    'faissol': 'Faisol',
    'faisool': 'Faisol',
    'faiso l': 'Faisol',
    'fasol': 'Faisol',
    'faisok': 'Faisol',
    'fausol': 'Faisol',
    'faisl': 'Faisol',
    'faiisl': 'Faisol',
    'faisoll': 'Faisol',
}


def normalize_name(value):
    """Bakukan ejaan nama; kembalikan versi bersih bila tidak dikenal."""
    s = clean(value)
    if not s:
        return ''
    return NAME_CANONICAL.get(norm_key(s), s)


# ============================================================
# Posisi (OB / Security) — pemetaan nama dari data sheet lama.
# Konfirmasi pengguna (14/8/2026): Muhajir = Security, sisanya OB.
# ============================================================
SECURITY_NAMES = {'muhajir'}


def guess_position(nama):
    """Tebak posisi dari nama. 'Security' untuk daftar keamanan, default 'OB'."""
    return 'Security' if norm_key(nama) in SECURITY_NAMES else 'OB'
