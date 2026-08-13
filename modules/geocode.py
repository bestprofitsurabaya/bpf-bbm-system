"""Geocoding alamat -> koordinat (lat/lng) via Nominatim/OpenStreetMap.

Gratis, tanpa API key. Dilengkapi cache DB (tabel geocode_cache) agar:
- tidak membebani server Nominatim (rate limit ±1 request/detik), dan
- alamat yang sama tidak di-query ulang berulang kali.

Ketahanan query (hasil E2E nyata):
  Alamat Indonesia sering memakai "Jl. ... No 12, Surabaya" yang TIDAK cocok
  dengan pencarian Nominatim. Modul ini mencoba beberapa varian query:
    1. alamat asli
    2. tanpa token jalan/nomor (jl., jalan, no., nomor, rt/rw)
    3. tanpa nomor rumah
  Hasil negatif di-cache dengan TTL 24 jam (agar alamat yang diperbaiki
  marketing bisa di-query ulang, tanpa membebani Nominatim tiap request).

Konfigurasi env:
  NOMINATIM_URL   (default https://nominatim.openstreetmap.org/search)
  NOMINATIM_EMAIL (opsional, disarankan OSM: identitas pemakai API)
  GEOCODE_ENABLED (default '1'; set '0' untuk menonaktifkan jaringan)
  GEOCODE_TIMEOUT (detik, default 6)
"""
import os
import re
import threading
import time
from datetime import datetime

import requests

NOMINATIM_URL = os.environ.get('NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search').strip()
NOMINATIM_EMAIL = os.environ.get('NOMINATIM_EMAIL', '').strip()
GEOCODE_ENABLED = os.environ.get('GEOCODE_ENABLED', '1').strip() not in ('0', 'false', 'no', '')
GEOCODE_TIMEOUT = float(os.environ.get('GEOCODE_TIMEOUT', '6'))
# Hasil "tidak ditemukan" hanya dihormati 24 jam, lalu di-query ulang.
NEGATIVE_TTL_SECONDS = 24 * 3600

# Penanda cache negatif (alamat pernah dicari tapi tidak ditemukan).
CACHE_NEGATIVE = '__NEGATIVE__'

# Rate limiter proses (thread-safe): 1 request / detik maksimal.
_last_request = 0.0
_rate_lock = threading.Lock()

# Token yang biasanya membuat query Nominatim gagal (Jl., Jalan, No., RT/RW).
_NOISE_RE = re.compile(
    r'\b(jl\.?|jalan|no\.?|nomor)\b|\brt\s*\d+\b|\brw\s*\d+\b', re.IGNORECASE)
_NUMBER_RE = re.compile(r'\b\d+\b')


def _squash(text):
    """Ratakan spasi & bersihkan spasi sebelum koma/titik."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+\.', '.', text)
    return text.strip(' ,-.')


def _clean_query(text):
    """Buang token jalan/nomor & ratakan spasi."""
    return _squash(_NOISE_RE.sub(' ', text))


def _query_variants(address):
    """Varian query yang dicoba berurutan (hingga 3)."""
    variants = [address]
    cleaned = _clean_query(address)
    if cleaned and cleaned != address:
        variants.append(cleaned)
        cleaned2 = _squash(_NUMBER_RE.sub(' ', cleaned))
        if cleaned2 and cleaned2 != cleaned and cleaned2 != address:
            variants.append(cleaned2)
    return variants[:3]


def _throttle():
    """Tunggu hingga minimal 1 detik sejak request Nominatim terakhir."""
    global _last_request
    with _rate_lock:
        elapsed = time.time() - _last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        _last_request = time.time()


def ensure_geocode_schema():
    """Buat tabel cache geocode + kolom found (idempotent; dipanggil saat startup)."""
    from modules.config import get_db_connection
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geocode_cache (
                address VARCHAR(500) NOT NULL PRIMARY KEY,
                lat DOUBLE NULL,
                lng DOUBLE NULL,
                display_name VARCHAR(500) DEFAULT '',
                found TINYINT(1) DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        # Upgrade DB lama (sebelum v2.15.1): kolom found
        try:
            cursor.execute("ALTER TABLE geocode_cache ADD COLUMN found TINYINT(1) DEFAULT 1")
        except Exception:
            pass  # sudah ada
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"[geocode] schema error: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _cache_get(address):
    """Baca cache.

    Return:
      (lat, lng)     -> cache positif
      CACHE_NEGATIVE -> cache negatif masih segar (< 24 jam)
      None           -> tidak ada cache / cache negatif basi (perlu query ulang)
    """
    from modules.config import get_db_connection
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT lat, lng, found, updated_at FROM geocode_cache WHERE address=%s", (address,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return None
        if row.get('found'):
            return (row['lat'], row['lng'])
        # Hasil negatif: hormati hanya jika masih segar
        updated = row.get('updated_at')
        if updated:
            try:
                age = (datetime.utcnow() - updated).total_seconds()
                if age > NEGATIVE_TTL_SECONDS:
                    return None
            except Exception:
                return CACHE_NEGATIVE
        return CACHE_NEGATIVE
    except Exception as e:
        print(f"[geocode] cache get error: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _cache_set(address, lat, lng, display_name=''):
    from modules.config import get_db_connection
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO geocode_cache (address, lat, lng, display_name, found) "
            "VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
            "lat=VALUES(lat), lng=VALUES(lng), display_name=VALUES(display_name), "
            "found=VALUES(found), updated_at=NOW()",
            (address, lat, lng, (display_name or '')[:500],
             1 if lat is not None and lng is not None else 0))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"[geocode] cache set error: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _geocode_once(query):
    """Satu query Nominatim. Return (lat, lng, display_name) atau (None, None, '')."""
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 0,
        'countrycodes': 'id',  # prioritas alamat Indonesia
    }
    headers = {'User-Agent': f'BPF-BBM-System/2.15 (Surabaya; {NOMINATIM_EMAIL or "ops@bestprofit.co.id"})'}
    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=headers,
                         timeout=GEOCODE_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data and isinstance(data, list) and data[0].get('lat') and data[0].get('lon'):
            return float(data[0]['lat']), float(data[0]['lon']), (data[0].get('display_name') or '')
        return None, None, ''
    except Exception as e:
        print(f"[geocode] Nominatim error untuk {query!r}: {e}")
        return None, None, ''


def _geocode_remote(address):
    """Query Nominatim dengan varian fallback (alamat asli -> disederhanakan)."""
    for query in _query_variants(address):
        _throttle()
        lat, lng, display = _geocode_once(query)
        if lat is not None:
            return lat, lng, display
    return None, None, ''


def geocode_address(address):
    """Resolusi alamat -> (lat, lng).

    - Cek cache DB dulu (positif; negatif segar langsung dipakai).
    - Bila GEOCODE_ENABLED=0, langsung None tanpa jaringan.
    - Return (lat, lng) atau (None, None).
    """
    address = (address or '').strip()
    if not address:
        return None, None
    if not GEOCODE_ENABLED:
        return None, None

    cached = _cache_get(address)
    if cached is not None:
        if cached == CACHE_NEGATIVE:
            return None, None
        return cached

    lat, lng, display = _geocode_remote(address)
    _cache_set(address, lat, lng, display)
    return lat, lng
