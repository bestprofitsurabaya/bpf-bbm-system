# 🚀 Panduan Deployment — BPF Fleet & BBM System v2.0

**PT. Bestprofit Futures — Surabaya** · Dokumen untuk Tim IT

---

## 📋 Daftar Isi

1. [Arsitektur & Port](#1-arsitektur--port)
2. [Prasyarat](#2-prasyarat)
3. [Instalasi Pertama (Fresh Install)](#3-instalasi-pertama-fresh-install)
4. [Variabel Lingkungan](#4-variabel-lingkungan)
5. [Update ke Versi Baru](#5-update-ke-versi-baru)
6. [Backup & Restore](#6-backup--restore)
7. [Monitoring & Log](#7-monitoring--log)
8. [Reverse Proxy & HTTPS](#8-reverse-proxy--https)
9. [Troubleshooting Deployment](#9-troubleshooting-deployment)
10. [Daftar Endpoint Utama](#10-daftar-endpoint-utama)
11. [Cloudflare Tunnel (Akses Cadangan Opsional)](#11-cloudflare-tunnel-akses-cadangan-opsional)
12. [SPA Vue 3 (v2.0) — Build & Deploy](#12-spa-vue-3-v20--build--deploy)

---

## 1. Arsitektur & Port

```
Internet / VPN
      │
      ▼
  Reverse Proxy (nginx / duckdns:5000)     ← HTTPS public
      │
      ▼
┌──────────────┐        ┌──────────────────┐
│  bbm_web     │◄──────►│  bbm_mariadb     │
│  Flask :5000 │  DB    │  MariaDB :3306   │
│  :5001 (dev) │        │  :3307 (host)    │
└──────────────┘        └──────────────────┘
   │  ┌───────────────┐
   └──│  bbm_db_data  │  ← volume persist DB
      │  uploads/     │  ← volume foto & bukti
      └───────────────┘
```

| Container | Nama | Port Host | Port Kontainer | Fungsi |
|-----------|------|-----------|----------------|--------|
| Web (Flask + SocketIO) | `bbm_web` | `5001` (dev) / `5000` (prod via proxy) | `5000` | Aplikasi |
| Database | `bbm_mariadb` | `3307` | `3306` | MariaDB 10.11 |

> **Catatan SocketIO:** WebSocket membutuhkan koneksi *long-lived*. Jika memakai reverse proxy, wajib aktifkan header **Upgrade/Connection** (`proxy_set_header Upgrade $http_upgrade;`). Tanpa itu, notifikasi real-time driver tidak akan jalan (halaman tetap normal, tapi push live gagal).

---

## 2. Prasyarat

- Docker Engine 20.10+ dan Docker Compose v2 (`docker compose`).
- Ruang disk cukup untuk volume DB + `uploads/` (foto watermark bisa besar).
- Zona waktu server: `Asia/Jakarta` (sudah di-set di compose & Dockerfile).
- Git untuk menarik kode terbaru.

```bash
docker --version && docker compose version
```

---

## 3. Instalasi Pertama (Fresh Install)

```bash
# 1. Clone repo
git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
cd bpf-bbm-system

# 2. (Opsional tapi disarankan) ganti SECRET_KEY di docker-compose.yml
#    sebelum pertama kali build!

# 3. Build & jalankan
docker compose up -d --build

# 4. Verifikasi
docker compose ps                 # kedua container "Up" dan "healthy"
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:5001/login   # → 200
```

Database **dibuat otomatis** pada first run dari `init.sql` (berisi schema + data awal + tabel `notifications`). Kredensial awal:

| Role | Username | PIN |
|------|----------|-----|
| Admin | `admin` | `123456` |
| GA | `ga_officer` | `123456` |
| Finance | `finance_officer` | `123456` |

> ⚠️ **Segera ganti PIN bawaan** setelah login pertama.

---

## 4. Variabel Lingkungan

Semua env di-set di `docker-compose.yml` (tidak perlu file `.env` terpisah, tapi bisa juga dipakai).

| Variabel | Default (compose) | Keterangan |
|----------|-------------------|------------|
| `DB_HOST` | `db` | Host MariaDB (nama service compose) |
| `DB_USER` | `bpf_user` | User DB |
| `DB_PASSWORD` | `bpf_pass` | Password DB |
| `DB_NAME` | `bpf_asset_system` | Nama database |
| `DB_POOL_SIZE` | `15` | Ukuran pool koneksi |
| `REDIS_URL` | `redis://redis:6379/0` | Backing store rate limit (login & verify-pin). Jika kosong / Redis mati, aplikasi **otomatis fallback ke memori proses** — tidak perlu ubah kode. Service `redis` (redis:7-alpine) sudah ada di docker-compose. |
| `SECRET_KEY` | `bpf_bbm_super_secret_...` | **WAJIB GANTI di produksi** — dipakai untuk session & CSRF token. Ganti dengan nilai acak panjang. |
| `FLASK_DEBUG` | `0` | Jangan aktifkan di produksi |
| `TZ` | `Asia/Jakarta` | Zona waktu |
| `SESSION_HOURS` | `12` | Masa berlaku sesi login (jam) — kebijakan sesi ISO/IEC 27001 A.8.5 |
| `SESSION_COOKIE_SECURE` | `true` | Cookie sesi hanya lewat HTTPS. Set `false` hanya untuk dev http lokal |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Proteksi CSRF tingkat cookie (jangan ubah tanpa alasan) |

**Cara generate SECRET_KEY aman:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

> 🔴 Jika `SECRET_KEY` diubah setelah produksi berjalan, **semua session login akan ter-logout** (aman, hanya perlu login ulang).

---

## 5. Update ke Versi Baru

```bash
cd bpf-bbm-system

# 1. Backup dulu (lihat bagian 6)
# 2. Tarik kode terbaru
git pull origin main

# 3. Lihat apa yang berubah (bila ada migrasi DB di release note)
git log --oneline -10

# 4. Rebuild & restart
docker compose up -d --build

# 5. Cek kesehatan
docker compose ps
docker logs bbm_web --tail 50 | grep -iE 'error|traceback' || echo 'bersih'

# 6. Smoke test cepat
curl -s -o /dev/null -w 'login: %{http_code}\n'  http://localhost:5001/login
curl -s -o /dev/null -w 'driver: %{http_code}\n'  http://localhost:5001/driver
```

> 💡 **Migrasi schema:** tabel `notifications` dibuat otomatis saat startup (`ensure_notifications_table`), jadi update v1.0 → v1.1 **tidak perlu migrasi manual**. Untuk perubahan schema lain di masa depan, Tim IT akan menyertakan file SQL di release note.

**Update frontend / PWA:** service worker memakai `CACHE_NAME` ber-version; saat update, versi asset di-bump sehingga perangkat driver otomatis mengambil versi baru.

---

## 6. Backup & Restore

### 6.1 Backup Database (otomatis via mysqldump)

```bash
# Di dalam container web (mysqldump sudah terinstall)
docker exec bbm_web sh -c 'mysqldump -h db -u bpf_user -pbpf_pass bpf_asset_system \
  --single-transaction --routines --triggers' > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 6.2 Backup Uploads (foto & bukti)

```bash
tar czf uploads_$(date +%Y%m%d).tar.gz uploads/
```

### 6.3 Restore

```bash
# Stop web dulu agar tidak ada koneksi aktif
docker compose stop web

# Restore DB (dari file backup.sql)
cat backup.sql | docker exec -i bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system

# Restore uploads
tar xzf uploads_YYYYMMDD.tar.gz -C .

# Start lagi
docker compose start web
```

> 💡 **Jadwalkan backup otomatis** via cron di server host:
> ```
> 30 1 * * * cd /opt/bpf-bbm-system && docker exec bbm_web sh -c 'mysqldump -h db -u bpf_user -pbpf_pass bpf_asset_system --single-transaction' > /backups/bbm_$(date +\%Y\%m\%d).sql && find /backups -name 'bbm_*.sql' -mtime +30 -delete
> ```

---

## 7. Monitoring & Log

### 7.1 Kesehatan Container

```bash
docker compose ps                      # status container
docker inspect --format='{{.State.Health.Status}}' bbm_mariadb
```

### 7.2 Log Aplikasi

```bash
docker logs -f bbm_web                # live tail
docker logs bbm_web --since 1h        # 1 jam terakhir
```

### 7.3 Query Monitoring Penting

```bash
# Status transaksi
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT status, COUNT(*) FROM transactions GROUP BY status;"

# Kasbon berjalan
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT display_id, driver_name, total_amount, status FROM fuel_cash_requests ORDER BY id DESC LIMIT 20;"

# Notifikasi driver (sudah dibaca / belum)
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT driver_name, type, message, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 20;"

# Audit trail
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT created_at, user_name, action FROM activity_logs ORDER BY id DESC LIMIT 20;"
```

### 7.4 Healthcheck Endpoint

```bash
curl -s -o /dev/null -w 'login: %{http_code}\n' http://localhost:5001/login
curl -s -o /dev/null -w 'driver PWA: %{http_code}\n' http://localhost:5001/driver
```

---

## 8. Reverse Proxy & HTTPS

Produksi saat ini diakses via **`https://nasbpfsby.duckdns.org:5000`** — **nginx reverse proxy** (container `nextcloud_nginx`, config bind-mount di `/home/it-ef/hybrid_nextcloud/nginx/conf.d/bbm_system.conf`) meneruskan ke `bbm_web:5000` di jaringan `nextcloud_net`.

```nginx
server {
    listen 5000 ssl;
    server_name nasbpfsby.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/nasbpfsby.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nasbpfsby.duckdns.org/privkey.pem;

    resolver 127.0.0.11 valid=30s;

    location / {
        set $upstream_bbm http://bbm_web:5000;
        proxy_pass $upstream_bbm;

        # ★ PENTING untuk WebSocket / Socket.IO (notifikasi real-time driver).
        # Tanpa ini upgrade wss:// ditolak server (HTTP 400) & log bbm_web
        # menampilkan "Invalid transport for session <sid>".
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> ✅ **Verifikasi WebSocket:** `curl -sk -i --http1.1 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: x' 'https://nasbpfsby.duckdns.org:5000/socket.io/?EIO=4&transport=websocket&sid=<sid>'` → harus `101 Switching Protocols`.

---

## 9. Troubleshooting Deployment

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| `bbm_web` restart loop | `db` belum healthy / kredensial salah | Cek `docker compose ps`; tunggu healthcheck; pastikan `DB_PASSWORD` sesuai |
| **500** pada semua halaman admin | `SECRET_KEY` berubah / session korup | Hapus cookie session di browser, login ulang |
| Notifikasi driver tidak real-time / console `wss://... failed` / log `Invalid transport for session <sid>` | Proxy (nginx) tidak meneruskan header Upgrade WebSocket | Tambahkan `proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` + `proxy_buffering off` di `location /` (lihat §8) |
| Login selalu gagal | User nonaktif / PIN salah | Cek via `docker exec bbm_mariadb mysql ... -e "SELECT username,is_active FROM users;"` |
| Halaman lambat setelah deploy | Service worker versi lama | Hard refresh; versi asset baru otomatis terambil |
| Port 5001 bentrok | Aplikasi lain memakai port | Ubah `ports: "XXXX:5000"` di docker-compose.yml |
| Data tidak tersimpan setelah restart | Volume hilang | Jangan hapus `bbm_db_data`; `docker compose down` tanpa `-v` aman |

---

## 10. Daftar Endpoint Utama

### Halaman (Web)
| Method | Path | Auth | Fungsi |
|--------|------|------|--------|
| GET | `/login` | Publik | Login admin |
| GET | `/logout` | Session | Logout |
| GET | `/driver` | Publik | PWA Driver (tanpa login) |
| GET | `/admin` | admin/ga/finance | Dashboard admin |
| GET | `/ga/assignments` | admin/ga | Penugasan kendaraan |
| GET | `/admin/rekap` | admin/finance | Rekapitulasi |
| GET | `/admin/analytics` | admin/ga/finance | Analytics |
| GET | `/admin/trips` | admin/ga | Trip review |
| GET | `/admin/users` | **admin** | Manajemen pengguna |
| GET | `/admin/settings` | admin/ga/finance | Pengaturan (PIN gate) |
| GET | `/admin/logs` | admin | Audit log |
| GET | `/admin/queue-fragment/<tab>` | Session | Fragment SPA tab dashboard |

### API Penting
| Method | Path | Auth | Fungsi |
|--------|------|------|--------|
| GET | `/api/stats` | Session | Statistik dashboard |
| GET | `/api/notifications?driver=...` | Publik | Notifikasi driver |
| POST | `/api/notifications/read` | Publik | Tandai notifikasi dibaca |
| POST | `/api/cash/request` | Publik (driver) | Ajukan kasbon |
| POST | `/api/cash/submit-lpj/<id>` | Publik (driver) | Kirim LPJ |
| GET | `/api/cash/history` | Publik (driver) | Riwayat kasbon |
| POST | `/api/cash/approve-ga/<id>` | ga/admin | Approve kasbon GA |
| POST | `/api/cash/approve-finance/<id>` | finance/admin | Cairkan kasbon |
| POST | `/api/users/sync` | **admin** | Tambah/update user |
| POST | `/api/users/reset-pin` | **admin** | Reset PIN user |
| POST | `/api/verify-pin` | Publik | Verifikasi PIN (verifikasi ganda) |
| POST | `/api/assignments/create` | ga/admin | Assign kendaraan |
| POST | `/api/drivers/sync` | admin | Tambah driver |

> **Aturan auth:** endpoint driver PWA (`/driver`, `/api/cash/*` request/history/submit-lpj, `/api/assignments/confirm`, dsb.) **tidak butuh login** dan di-exempt dari CSRF. Endpoint admin butuh session + CSRF token.

---

## 11. Cloudflare Tunnel (Akses Cadangan Opsional) 🌐

> ⚠️ **Nonaktif sejak v1.2.3** — produksi memakai **DuckDNS + nginx** (`https://nasbpfsby.duckdns.org:5000`). Service `cloudflared` di `docker-compose.yml` sengaja di-comment agar tidak boros resource; aktifkan kembali hanya jika butuh akses cadangan tanpa port forwarding.

Aplikasi bisa diakses publik tanpa membuka port di router/gateway, memakai **Cloudflare Tunnel** (`cloudflared`) yang berjalan sebagai container Docker.

### 11.1 Quick Tunnel (Uji Coba — Nonaktif, Aktifkan Kembali Bila Perlu)

Service `cloudflared` sudah ada di `docker-compose.yml`:

```yaml
cloudflared:
  image: cloudflare/cloudflared:latest
  container_name: bbm_cloudflared
  command: tunnel --no-autoupdate --url http://web:5000
  depends_on:
    - web
  restart: unless-stopped
  networks:
    - default
```

- Jalankan: `docker compose up -d cloudflared`
- Lihat URL: `bash scripts/tunnel-url.sh` (atau `docker logs bbm_cloudflared`)

**Karakteristik quick tunnel:**
- ✅ HTTPS otomatis (sertifikat Cloudflare) — PWA berfungsi penuh
- ✅ WebSocket didukung (notifikasi real-time driver jalan)
- ⚠️ URL acak (`https://xxx.trycloudflare.com`) dan **berubah setiap restart** — hanya untuk uji coba

### 11.2 Named Tunnel + Domain (Produksi — URL Permanen)

Untuk URL yang stabil, buat named tunnel:

1. **Dashboard Cloudflare** → Zero Trust → **Networks → Tunnels → Create a tunnel** → pilih type **Cloudflared**.
2. Salin **Tunnel Token** (`eyJ...`).
3. Ubah command di `docker-compose.yml`:
   ```yaml
   command: tunnel --no-autoupdate run --token eyJ....(tempel token).
   ```
4. Di dashboard tunnel, tambahkan **Public Hostname**:
   - Subdomain: `bpf` · Domain: `perusahaan.com`
   - Service: `http://web:5000`
5. Pastikan domain sudah di-manage Cloudflare (nameserver Cloudflare).
6. Restart: `docker compose up -d cloudflared`

**Catatan penting:**
- SocketIO memakai `io()` relatif → otomatis mengikuti host, jadi **tidak perlu ubah kode** saat pindah URL.
- Tidak ada domain hardcoded di codebase (terverifikasi).
- URL baru cukup dibagikan; PWA akan menyesuaikan saat dimuat dari origin baru.

---

## 12. SPA Vue 3 (v2.0) — Build & Deploy 🎨

Mulai v2.0, antarmuka admin/back-office adalah **Single Page App Vue 3** yang di-build dengan **Vite** dan disajikan Flask dari `/app/*`.

### 12.1 Alur Build (otomatis di Dockerfile multi-stage)

```
Stage 1 (node:20-alpine): cd frontend && npm install && npm run build → dist/
Stage 2 (python:3.11-slim): Flask + dependensi; dist disalin ke /app/static/app/
```

> 🔴 **PENTING (bind-mount `./static`):** `docker-compose.yml` me-mount `./static:/app/static`, sehingga hasil `COPY --from=frontend-build` **tertimpa** oleh folder host. Artinya **setelah pull kode baru**, jalankan sekali:
> ```bash
> bash scripts/build-spa.sh     # build SPA + salin ke static/app/
> docker compose up -d --build
> ```
> `static/app/` tidak ikut di-commit (ada di `.gitignore`) — selalu dihasilkan oleh script ini. Jika `GET /app/` mengembalikan `SPA belum di-build`, itu tanda `static/app/` belum dibuat di host.

Build lokal (untuk develop/validasi):
```bash
cd frontend
npm install
npm run dev        # dev server :5173, proxy /api → localhost:5001
npm run build      # hasil di frontend/dist
```

### 12.2 PWA, Notifikasi & CI/CD (v2.1)

- **PWA SPA**: `/app/manifest.webmanifest` + `/app/sw.js` (scope `/app/`) ikut ter-build dari `frontend/public/`. SW SPA: app-shell di-cache saat install, navigasi network-first dengan fallback offline ke `index.html`, asset ber-hash cache-first.
- **Service worker driver** (`sw.js`) kini **hanya** membersihkan cache miliknya sendiri (prefix `bpf-bbm-*`) — tidak lagi menghapus cache SPA (`bpf-spa-*`) saat versi baru rilis.
- **Notifikasi real-time SPA**: GA/Finance/Admin menerima event `new_claim` & `new_trip_report` (broadcast); Marketing & Chief Driver join room `appointments_board` untuk `appointment_update`. Tidak ada konfigurasi tambahan — WebSocket yang sama (lihat §8).
- **CI/CD**: `.github/workflows/ci.yml` menjalankan build + `npm test` (Vitest) untuk frontend dan `pytest tests/` untuk backend di setiap push ke `main`/PR. Test backend murni unit (tanpa DB).

### 12.3 Endpoint Auth & Trips (baru)

| Method | Path | Fungsi |
|--------|------|--------|
| GET | `/api/auth/me` | Status sesi + role + CSRF token (untuk SPA) |
| POST | `/api/auth/login` | Login JSON (username + PIN) → role + home |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/trips` | List log perjalanan (filter driver/date/status) |
| POST | `/api/trips/verify/<id>` | Verify trip (ga/admin) |
| POST | `/api/trips/reject/<id>` | Reject trip + alasan (ga/admin) |
| GET | `/app/*` | SPA (fallback index.html utk client routing) |

### 12.3 Akses per Role (ISO/IEC 27001)

Setelah login, redirect mengikuti role: marketing → `/app/marketing`, chief_driver → `/app/chief-driver`,
selainnya → `/app/dashboard`. Server tetap menegakkan `role_required` di semua route; SPA menegakkan
ulang di sisi klien (guard router + menu terfilter). Lihat `SECURITY.md` untuk pemetaan kontrol lengkap
(ISO/IEC 27001:2022, ISO 9241-11, ISO 9001).

### 12.4 Halaman Back-Office Lengkap (v2.2)

- `/app/analytics` — konsumsi `/api/analytics/data` (`{finance, ga, cash, fleet}`) dengan 8+ kartu statistik + 3 grafik Chart.js + tabel Top 5 driver. Grafik digambar via `nextTick` setelah render.
- `/app/rekap` — tombol **Preview PDF** (`/admin/rekap/pdf?start_date&end_date`, tab baru) & **Download PDF** (`&dl=1` → `Content-Disposition: attachment`).
- `/app/logs` — filter aksi & peran dilakukan klien-side pada `/api/audit-logs`.
- `/app/settings` — tambah driver (`POST /api/drivers/sync`), hapus driver (`POST /api/drivers/<nama>/delete`, admin), tambah kendaraan (`POST /api/vehicles/add`).
- `/app/users` — nonaktifkan/aktifkan & hapus user via `POST /api/users/sync` (`is_active`), seperti perilaku klasik.
- Semua halaman sudah ada route+guard role di SPA; tidak ada migrasi DB tambahan.

---

### 12.5 Hardening Keamanan (v2.2.3)

- **`SECRET_KEY` wajib dari `.env`** (gitignored): `docker compose` membaca `.env` di direktori project untuk `SECRET_KEY=${SECRET_KEY:?}`. Tanpa file `.env`, container **menolak start** — buat dengan: `printf 'SECRET_KEY=%s\n' "$(python3 -c 'import secrets; print("bpf_bbm_" + secrets.token_hex(24))')" > .env && chmod 600 .env`.
- Mengganti SECRET_KEY akan **meng-invalidasi semua sesi** (semua user login ulang) — lakukan saat jendela maintenance.
- **Upload bukti** kini dibatasi ekstensi aman (png/jpg/jpeg/webp/gif/pdf) + `secure_filename` + header `nosniff` — file berbahaya otomatis ditolak.
- **`/api/verify-pin`** rate limit per-IP (8 gagal/5 menit → lockout 10 menit) — anti brute-force PIN.

---

## 🧾 Checklist Sebelum Go-Live

- [ ] `SECRET_KEY` ada di `.env` lokal (gitignored) — bukan hardcoded di repo
- [ ] PIN bawaan semua akun sudah diganti
- [ ] Reverse proxy meneruskan header WebSocket (`Upgrade`/`Connection`)
- [ ] Backup otomatis terkonfigurasi (DB + uploads)
- [ ] HTTPS aktif (PWA wajib secure origin)
- [ ] Smoke test: `/login` 200, `/driver` 200, `/app/` 200 (SPA), login admin sukses
- [ ] SPA: `bash scripts/build-spa.sh` sudah dijalankan setelah pull (bind-mount `./static`)
- [ ] Test suite: `docker exec bbm_web python3 -m pytest tests/ -q` → semua PASS
- [ ] Frontend: `cd frontend && npm test` → 12 PASS (CI otomatis di GitHub Actions)

---

**PT. Bestprofit Futures — Surabaya**  
BPF Fleet & BBM System v2.0 · Dikembangkan oleh **Tim IT BPF Surabaya**
