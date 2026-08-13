"""Route Optimizer — penugasan rute appointment ke driver (VRPTW heuristic).

Algoritma: *greedy insertion berurutan waktu* + *load balancing*.

Konteks bisnis (masukan Marketing → Chief Driver):
  Marketing mencatat appointment dengan sesi (1 = 08.30 / 2 = 14.30) dan jam
  kunjungan bebas di dalam rentang sesi. Chief Driver ingin membagi appointment
  sehingga tiap driver mendapat rute yang "searah" (lokasi berdekatan) dan urut
  sesuai jam kunjungan — tujuannya meminimalkan jarak tempuh dan BBM.

Pendekatan (heuristic praktis untuk VRPTW skala kecil — puluhan kunjungan/hari):
  1. Setiap sesi dioptimalkan terpisah (jarak waktu antar sesi ±6 jam).
  2. Appointment diurutkan berdasarkan jam kunjungan (visit_time).
  3. Appointment yang SUDAH ditugaskan manual (fixed driver) menjadi "seed"
     rute driver-nya — override manual chief driver selalu dihormati.
  4. Untuk tiap appointment baru, pilih driver dengan biaya penyisipan terkecil:
         cost = jarak(last_visit, new) + LOAD_WEIGHT * jumlah_kunjungan_driver
     → rute cenderung searah secara geografis & beban antar driver merata.
  5. Urutan kunjungan per driver = urutan jam (tidak melanggar janji waktu),
     dengan cek kelayakan waktu perjalanan antar kunjungan (soft — jika semua
     driver tidak feasible, tetap dipilih yang biayanya paling kecil).

Modul murni (tanpa dependency DB/Flask) sehingga mudah diuji unit.
"""
import math

EARTH_RADIUS_KM = 6371.0

# Default asumsi operasional (bisa dioverride per pemanggilan).
DEFAULT_SPEED_KMH = 30.0      # kecepatan rata-rata dalam kota (Surabaya)
DEFAULT_KM_PER_LITER = 12.0   # konsumsi BBM kendaraan (km/liter)
DEFAULT_PRICE_PER_LITER = 10000.0  # harga BBM (rupiah/liter)
LOAD_WEIGHT = 1.5             # bobot beban (km-equivalent per kunjungan)


def haversine_km(lat1, lon1, lat2, lon2):
    """Jarak great-circle antara dua koordinat (km)."""
    try:
        lat1, lon1, lat2, lon2 = (float(v) for v in (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return None
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    if not (-90 <= lat1 <= 90 and -90 <= lat2 <= 90) or not (-180 <= lon1 <= 180 and -180 <= lon2 <= 180):
        return None
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def estimate_travel_minutes(distance_km, speed_kmh=DEFAULT_SPEED_KMH):
    """Estimasi waktu tempuh antar lokasi (menit)."""
    if distance_km is None or distance_km < 0:
        return 0
    if speed_kmh <= 0:
        return 0
    return (distance_km / speed_kmh) * 60.0


def time_to_minutes(value):
    """'HH:MM' -> menit sejak tengah malam; None bila tidak valid."""
    if not value:
        return None
    try:
        hh, mm = str(value).strip().split(':')[:2]
        return int(hh) * 60 + int(mm)
    except (ValueError, AttributeError):
        return None


def is_time_feasible(prev_time, next_time, travel_min):
    """True bila tiba di next_time masih memungkinkan (prev + travel <= next)."""
    p = time_to_minutes(prev_time)
    n = time_to_minutes(next_time)
    if p is None or n is None:
        return True  # tanpa jam, tidak ada batasan waktu
    return n >= p + travel_min


def _dist_between(a, b):
    """Jarak km antara dua dict berkoordinat; None bila koordinat hilang."""
    return haversine_km(a.get('lat'), a.get('lng'), b.get('lat'), b.get('lng'))


def _has_coords(point):
    try:
        return point.get('lat') is not None and point.get('lng') is not None
    except AttributeError:
        return False


def _total_route_km(route, depot):
    """Total jarak rute: depot -> v1 -> v2 -> ... -> vN (tanpa kembali ke depot)."""
    total = 0.0
    prev = depot
    for v in route:
        if _has_coords(prev) and _has_coords(v):
            d = _dist_between(prev, v)
            if d is not None:
                total += d
        prev = v
    return total


def estimate_bbm_liters(total_km, km_per_liter=DEFAULT_KM_PER_LITER):
    """Liter BBM yang dibutuhkan untuk menempuh total_km."""
    if total_km is None or total_km <= 0 or km_per_liter <= 0:
        return 0.0
    return total_km / km_per_liter


def estimate_bbm_cost(liters, price_per_liter=DEFAULT_PRICE_PER_LITER):
    """Perkiraan biaya BBM (rupiah)."""
    if liters <= 0 or price_per_liter <= 0:
        return 0
    return round(liters * price_per_liter)


def plan_routes(appointments, drivers, depot=None,
                km_per_liter=DEFAULT_KM_PER_LITER,
                price_per_liter=DEFAULT_PRICE_PER_LITER,
                speed_kmh=DEFAULT_SPEED_KMH,
                load_weight=LOAD_WEIGHT):
    """Bagi daftar appointment ke driver dengan rute searah & urut jam.

    Parameters
    ----------
    appointments : list[dict]
        Setiap item minimal berisi: 'id', 'sesi' ('1'/'2'), 'visit_time' ('HH:MM'),
        'lat'/'lng' (float atau None), 'driver' (str atau None = sudah ditugaskan).
        Field lain (display_id, nasabah_name, alamat, ...) diteruskan apa adanya
        ke output.
    drivers : list[str]
        Nama driver aktif yang tersedia untuk penugasan baru.
    depot : dict | None
        {'lat': ..., 'lng': ...} titik awal perjalanan (kantor). None = tanpa
        referensi awal (jarak antar kunjungan saja).

    Returns
    -------
    dict dengan kunci: 'drivers' (rute per driver), 'unassigned',
    'totals', 'meta'.
    """
    appointments = list(appointments or [])
    drivers = [str(d) for d in (drivers or []) if str(d).strip()]
    depot = dict(depot) if depot else None
    if depot is not None and not _has_coords(depot):
        depot = None

    # --- pisahkan per sesi, dan fixed (sudah ditugaskan) vs free ---
    by_session = {'1': [], '2': []}
    for a in appointments:
        by_session.setdefault(str(a.get('sesi', '1')), []).append(a)

    routes = {}  # driver -> list kunjungan (berurutan)
    for d in drivers:
        routes[d] = []

    unassigned = []

    for sesi_key in ('1', '2'):
        session_appts = by_session.get(sesi_key, [])

        def _sort_key(a):
            t = time_to_minutes(a.get('visit_time'))
            return (t if t is not None else 0, a.get('id') or 0)

        # Seed: appointment yang sudah ditugaskan manual — urut sesuai jam
        fixed = [a for a in session_appts if a.get('driver')]
        for a in sorted(fixed, key=_sort_key):
            dname = str(a.get('driver') or '').strip().upper()
            if dname and dname in routes:
                routes[dname].append(a)
            else:
                unassigned.append(_tag(a, 'driver_not_active'))

        # Free: diurutkan berdasarkan jam kunjungan (urutan waktu dunia nyata)
        free = sorted([a for a in session_appts if not a.get('driver')],
                      key=_sort_key)

        for a in free:
            if not _has_coords(a):
                unassigned.append(_tag(a, 'no_coordinates'))
                continue
            best = _pick_driver(a, routes, drivers, depot,
                                speed_kmh=speed_kmh, load_weight=load_weight)
            if best is None:
                unassigned.append(_tag(a, 'no_driver_available'))
                continue
            routes[best].append(a)

    # --- bangun output: rute per driver + estimasi jarak/BBM ---
    out_drivers = []
    total_km = 0.0
    for d in drivers:
        route = routes[d]
        if not route:
            continue
        km = _total_route_km(route, depot)
        total_km += km
        liters = estimate_bbm_liters(km, km_per_liter)
        visits = []
        for order, v in enumerate(route, start=1):
            item = dict(v)
            item['order'] = order
            visits.append(item)
        out_drivers.append({
            'driver': d,
            'visits': visits,
            'total_km': round(km, 1),
            'est_bbm_liter': round(liters, 2),
            'est_bbm_cost': estimate_bbm_cost(liters, price_per_liter),
        })

    out_drivers.sort(key=lambda r: r['driver'])

    total_liters = estimate_bbm_liters(total_km, km_per_liter)

    # Pembanding: berapa jarak/BBM kalau appointment dibagi tanpa optimasi
    baseline_km = _baseline_total_km(appointments, drivers, depot)
    baseline_liters = estimate_bbm_liters(baseline_km, km_per_liter)
    savings_km = max(baseline_km - total_km, 0.0)
    savings_liters = max(baseline_liters - total_liters, 0.0)
    savings_pct = (savings_km / baseline_km * 100.0) if baseline_km > 0 else 0.0

    return {
        'drivers': out_drivers,
        'unassigned': unassigned,
        'totals': {
            'appointments': len(appointments),
            'assigned': sum(len(r['visits']) for r in out_drivers),
            'unassigned': len(unassigned),
            'km': round(total_km, 1),
            'bbm_liter': round(total_liters, 2),
            'bbm_cost': estimate_bbm_cost(total_liters, price_per_liter),
            # Penghematan vs penugasan tanpa optimasi (round-robin)
            'baseline_km': round(baseline_km, 1),
            'baseline_bbm_liter': round(baseline_liters, 2),
            'savings_km': round(savings_km, 1),
            'savings_percent': round(savings_pct, 1),
            'savings_bbm_liter': round(savings_liters, 2),
            'savings_bbm_cost': max(estimate_bbm_cost(savings_liters, price_per_liter), 0),
        },
        'meta': {
            'depot': depot,
            'km_per_liter': km_per_liter,
            'price_per_liter': price_per_liter,
            'speed_kmh': speed_kmh,
            'load_weight': load_weight,
            'algorithm': 'greedy_time_ordered_insertion',
        },
    }


def _baseline_total_km(appointments, drivers, depot):
    """Total jarak baseline: penugasan TANPA optimasi geografis (round-robin).

    Dipakai sebagai pembanding — "berapa km kalau appointment cuma dibagi
    urut daftar saja". Appointment yang sudah ditugaskan manual tetap di
    drivernya (fixed); sisanya dibagi round-robin per sesi sesuai urutan jam.
    Appointment tanpa koordinat tidak berkontribusi jarak (sama seperti rute
    teroptimasi, sehingga perbandingan adil).
    """
    by_session = {'1': [], '2': []}
    for a in appointments:
        by_session.setdefault(str(a.get('sesi', '1')), []).append(a)

    routes = {d: [] for d in drivers}
    for sesi_key in ('1', '2'):
        appts = sorted(by_session.get(sesi_key, []),
                       key=lambda a: (time_to_minutes(a.get('visit_time')) or 0, a.get('id') or 0))
        for a in appts:
            if a.get('driver') and str(a['driver']).strip().upper() in routes:
                routes[str(a['driver']).strip().upper()].append(a)
        free = [a for a in appts if not a.get('driver') and _has_coords(a)]
        order = sorted(routes, key=lambda d: (len(routes[d]), d))
        if order:
            for i, a in enumerate(free):
                routes[order[i % len(order)]].append(a)

    return sum(_total_route_km(routes[d], depot) for d in drivers)


def _tag(a, reason):
    """Salin appointment + info alasan tidak ditugaskan."""
    item = dict(a)
    item['unassigned_reason'] = reason
    return item


def _pick_driver(a, routes, drivers, depot, speed_kmh=DEFAULT_SPEED_KMH,
                 load_weight=LOAD_WEIGHT):
    """Pilih driver terbaik untuk appointment `a`.

    Biaya penyisipan per driver:
        cost = jarak(last_visit -> a) + load_weight * jumlah kunjungan driver
    Prioritas: driver yang *feasible waktu* dengan cost terkecil; bila tidak ada
    yang feasible, ambil cost terkecil mutlak (soft time window). Tie-break:
    beban lebih ringan, lalu nama driver (deterministik).
    """
    best = None
    best_cost = None
    best_feasible = False
    a_time = a.get('visit_time')

    for d in drivers:
        route = routes[d]
        last = route[-1] if route else depot
        if last is None:
            # Tidak ada referensi awal & tanpa depot -> jarak antar kunjungan 0
            cost = load_weight * len(route)
            feasible = True
        else:
            d_km = _dist_between(last, a)
            if d_km is None:
                cost = load_weight * len(route)
                feasible = True
            else:
                travel = estimate_travel_minutes(d_km, speed_kmh)
                cost = d_km + load_weight * len(route)
                feasible = is_time_feasible(last.get('visit_time'), a_time, travel)

        # Tie-break: beban ringan dulu, lalu nama
        tie = (len(route), d)
        candidate = (feasible, cost, tie)
        cur = (best_feasible, best_cost, (len(routes[best]) if best else 0, best or ''))
        if best is None or _better(candidate, cur):
            best = d
            best_cost = cost
            best_feasible = feasible

    return best


def _better(cand, cur):
    """True bila kandidat lebih baik dari kandidat saat ini."""
    c_feas, c_cost, c_tie = cand
    cur_feas, cur_cost, cur_tie = cur
    if c_feas != cur_feas:
        return c_feas and not cur_feas  # feasible selalu menang atas tidak feasible
    if c_cost != cur_cost:
        return c_cost < cur_cost
    return c_tie < cur_tie
