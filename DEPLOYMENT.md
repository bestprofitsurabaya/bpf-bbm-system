# 🚀 Panduan Deployment — BPF Fleet & BBM System v1.1

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
| `SECRET_KEY` | `bpf_bbm_super_secret_...` | **WAJIB GANTI di produksi** — dipakai untuk session & CSRF token. Ganti dengan nilai acak panjang. |
| `FLASK_DEBUG` | `0` | Jangan aktifkan di produksi |
| `TZ` | `Asia/Jakarta` | Zona waktu |

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

Saat ini produksi diakses via `https://nasbpfsby.duckdns.org:5000` (port langsung). Untuk setup yang lebih rapi (port 443 standar), pasang nginx sebagai reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name nasbpfsby.duckdns.org;

    # SSL cert (Let's Encrypt / internal CA)
    ssl_certificate     /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;

    location / {
        proxy_pass http://127.0.0.1:5001;      # bbm_web di host
        proxy_http_version 1.1;

        # ★ PENTING untuk WebSocket / SocketIO (notifikasi real-time)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 86400;               # koneksi WebSocket panjang
    }
}
```

> ⚠️ **Setelah memakai reverse proxy + HTTPS**, update URL di `USER_GUIDE.md` dan pastikan `manifest.json` menggunakan URL HTTPS (PWA menuntut origin secure).

---

## 9. Troubleshooting Deployment

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| `bbm_web` restart loop | `db` belum healthy / kredensial salah | Cek `docker compose ps`; tunggu healthcheck; pastikan `DB_PASSWORD` sesuai |
| **500** pada semua halaman admin | `SECRET_KEY` berubah / session korup | Hapus cookie session di browser, login ulang |
| Notifikasi driver tidak real-time | Proxy tidak forward header Upgrade | Aktifkan `proxy_set_header Upgrade/Connection` (lihat §8) |
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

## 🧾 Checklist Sebelum Go-Live

- [ ] `SECRET_KEY` diganti dengan nilai acak (jangan default)
- [ ] PIN bawaan semua akun sudah diganti
- [ ] Reverse proxy meneruskan header WebSocket (`Upgrade`/`Connection`)
- [ ] Backup otomatis terkonfigurasi (DB + uploads)
- [ ] HTTPS aktif (PWA wajib secure origin)
- [ ] Smoke test: `/login` 200, `/driver` 200, login admin sukses
- [ ] Test suite: `docker exec bbm_web python3 -m pytest tests/ -q` → semua PASS

---

**PT. Bestprofit Futures — Surabaya**  
BPF Fleet & BBM System v1.1 · Dikembangkan oleh **Tim IT BPF Surabaya**
