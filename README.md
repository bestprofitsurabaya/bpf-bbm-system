# ⛽ BPF Fleet & BBM System v1.2

**Sistem Manajemen Armada, Klaim BBM, Kasbon, Log Perjalanan & Appointment**  
**PT. Bestprofit Futures - Surabaya**

---

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, pengarsipan klaim BBM, **pengajuan kasbon dengan kode unik**, dan log perjalanan harian (logsheet) dengan workflow GA → Finance → Archive. Dilengkapi **sistem appointment canggih** (Marketing → Chief Driver → Log Perjalanan), deteksi anomali Machine Learning, GPS tracking, **watermark foto otomatis**, PIN security, **session-based login & role-based access**, **CSRF protection**, **notifikasi real-time**, import Excel, audit trail, Chart.js visualization, **PWA offline-first**, dan **WebSocket real-time**.

---

## 🆕 Fitur Terbaru v1.2 — Sistem Appointment

### 📣 Marketing Hub (`/marketing`)
| Fitur | Deskripsi |
|-------|-----------|
| **Login Role Marketing** | User marketing (mis. Icang dari Tim Yusie) login PIN → langsung ke halaman inputnya |
| **Form Multi-Input** | Input 2+ appointment sekaligus: nama calon nasabah, no. HP, alamat, catatan |
| **Nama Marketing Anggota** | 1 akun (manager) bisa input untuk banyak anggota — wajib cantumkan **siapa yang memprospek**; nama auto-register jadi daftar saran |
| **Sesi Perjalanan** | 🌅 Sesi 1 (08.30) / 🌆 Sesi 2 (14.30) — menentukan slot kunjungan |
| **Deteksi Area Otomatis** | Sistem mengenali zona alamat (Darmo, Rungkut, Sidoarjo, dsb.) |
| **Notifikasi Real-Time** | Marketing tahu saat driver ditugaskan / appointment selesai |

### 🚛 Chief Driver Command Center (`/chief-driver`)
| Fitur | Deskripsi |
|-------|-----------|
| **Board Belum Ditugaskan** | Per sesi + **saran driver otomatis** (load-balancing beban sesi) |
| **Tugas Per Driver** | Jadwal lengkap per driver: ✅ Selesai, 🔄 Ganti, ↩️ Batal Tugas, ✕ Batal Appt |
| **🌍 Ubah Area Manual** | Chief Driver bisa **override area** hasil deteksi otomatis (tombol 🌍 di kartu) |
| **Rekap Excel Harian** | Unduh laporan appointment per tanggal (openpyxl, termasuk nama marketing anggota) |
| **Board Real-Time** | Perubahan langsung tampil (Socket.IO) |

### 🔗 Integrasi Log Perjalanan
| Fitur | Deskripsi |
|-------|-----------|
| **Auto-Integrasi** | Appointment selesai → otomatis muncul di form Trip driver pada tanggal sama |
| **Muat Sekali Klik** | "📥 Muat Semua ke Rute" mengisi rute dari alamat nasabah + jam sesi |
| **Audit Jejak** | `trip_details.appointment_id` + badge "📅 APP-xxxx" di Trip Review |

---

## 🆕 Fitur Terbaru v1.1

### 🔐 Autentikasi & Keamanan (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Login / Logout** | Halaman `/login` (username + PIN), session cookie, tombol Keluar di semua halaman |
| **Role-Based Access** | 66 endpoint dilindungi `@role_required` (admin/ga/finance) — halaman di-redirect, API JSON 401/403 |
| **CSRF Protection** | Token CSRF di semua form + header `X-CSRF-Token` otomatis oleh fetch wrapper |
| **Anti Open-Redirect** | Parameter `next` pada login disanitasi & di-URL-encode |
| **GET → POST** | Semua aksi state-changing kini POST-only (approve, payout, archive, unverify, delete, trips verify) |

### 🔔 Notifikasi Driver Real-Time (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Push Live** | Driver menerima notifikasi via WebSocket saat transaksi/kasbon-nya diproses di dashboard admin |
| **Offline Catch-Up** | Notifikasi tersimpan di DB — langsung terlihat saat driver kembali online |
| **Badge Belum Dibaca** | Jumlah notifikasi unread di PWA driver |
| **API Notifikasi** | `GET /api/notifications?driver=...` + `POST /api/notifications/read` |

### 👥 Manajemen Pengguna (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Halaman /admin/users** | Kelola akun pengguna (admin-only): tambah, update role, aktif/nonaktif |
| **Reset PIN** | Atur ulang PIN 6 digit pengguna |

### 🌙 Dark Mode (Baru)
- Toggle 🌙/☀️ di navbar **semua halaman admin** (dashboard, analytics, rekap, settings, logs, trips, GA assignments, users, login)
- Tersimpan di `localStorage` — konsisten antar halaman, tanpa flash saat load

### 🖥️ Dashboard Admin UX (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **SPA Tab Switching** | Ganti tab antrean tanpa reload (fragment HTML + history API) |
| **Sticky Context Bar** | Ringkasan "Hari Ini" selalu terlihat saat scroll |
| **Skeleton Loading** | Kartu shimmer saat berpindah tab |
| **Bulk Action GA** | "✅ Tandai Semua Dicek" — approve massal dengan konfirmasi PIN |
| **Shortcut Keyboard** | Tekan `1`–`5` untuk berpindah tab |
| **Arsip Cerdas** | Filter search/tanggal/BBM, default 7 hari terakhir, tombol "Muat Lebih Banyak" |

---

## 🚀 Fitur Utama

### 📱 Driver (PWA Offline-First)
| Fitur | Deskripsi |
|-------|-----------|
| **4-Tab Navigation** | ⛽ BBM, 💰 Kasbon, 🗺️ Trip, 📊 Rapor |
| **Offline-First** | IndexedDB + localStorage + auto-sync |
| **Notifikasi Real-Time** | 🔔 Info status transaksi & kasbon langsung di HP |
| **Watermark Otomatis** | GPS + Waktu + Nama Perusahaan di setiap foto |
| **One-Click GPS** | 📍 Lokasi + jam + KM terisi otomatis |
| **Swipe Gesture** | Geser kiri/kanan pindah tab |
| **Dark Mode** | Toggle 🌙/☀️, tersimpan di localStorage |
| **Pull-to-Refresh** | Tarik ke bawah untuk refresh data |

### 👨‍💼 GA (General Affairs)
| Fitur | Deskripsi |
|-------|-----------|
| **GA Assignments** | Assign, Tukar, Lepas kendaraan dengan audit trail |
| **Cross-Check Verifikasi** | Health Score + Flags + Budget sebelum approve |
| **Trip Review** | Popup detail rute + Print + PDF + Excel |
| **Progress Bar Kasbon** | Visual tracking per pengajuan |
| **Auto-Refresh Antrean** | Antrean baru tampil otomatis (polling 30 detik) |

### 💰 Finance
| Fitur | Deskripsi |
|-------|-----------|
| **Finance Review Panel** | Split-screen foto + data + remark |
| **ODO Edit** | Koreksi ODO dengan PIN + alasan |
| **Archive + ZIP** | Download semua bukti dalam 1 file |
| **PDF Report** | Kop surat profesional + Grid foto 2×2 |

### 📊 Analytics & Rekap
| Fitur | Deskripsi |
|-------|-----------|
| **3-Tab Analytics** | Finance, GA, Fleet + Cash chart |
| **Filter Tipe Transaksi** | Klaim Biasa vs Kasbon |
| **Display ID Konsisten** | Sama di semua tempat (Driver, Admin, Rekap) |
| **Dark-Aware Charts** | Warna chart menyesuaikan tema |

### ⚙️ Admin Settings
| Fitur | Deskripsi |
|-------|-----------|
| **Driver Management** | Toggle aktif/nonaktif + hapus (3 kolom) |
| **Fleet Kendaraan** | Tambah kendaraan mandiri (tanpa driver) |
| **User & PIN** | Reset PIN via popup 🔑 + halaman Users terpisah |
| **Multi-Fill Threshold** | Deteksi top-up BBM |

---

## 🔄 Workflow

```

DRIVER → GA Approve → Finance Payout → Driver TTD → Archive ZIP
│          │              │               │            │
└─ pending └─ verified_ga └─ os_finance   └─ archived └─ download

```

### Alur Kasbon
```

Driver 💰→ GA ✅→ Finance 💰→ GA 🤝→ Driver ⛽→ LPJ 📋→ ✅ Selesai

```

### Alur Appointment (v1.2)
```

Marketing 📣 → Chief Driver 🚛 → Driver 🗺️ → GA ✅
   │              │                │            │
   └─ input       └─ bagi driver    └─ log       └─ review trip
      nasabah +      (saran          perjalanan
      alamat +        otomatis       auto-terisi
      sesi 08.30/     per sesi/      dari alamat
      14.30 +         area +         nasabah
      nama            area bisa
      marketing       diubah manual
      anggota         🌍)

```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Architecture | **Modular** (11 route modules + service layer) |
| Auth | Session-based (PIN users) + role_required + CSRF |
| Real-Time | Flask-SocketIO + eventlet + per-driver rooms |
| Database | MariaDB 10.11 |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF + DejaVu Sans (Unicode) |
| Excel | openpyxl |
| Charts | Chart.js 4.4 |
| Frontend | HTML5 + CSS3 + Vanilla JS (13 JS modules + 11 CSS) |
| PWA | Service Worker + IndexedDB + localStorage |
| Container | Docker + Docker Compose |
| Font | Inter (Google Fonts) + DejaVu Sans |

---

## 📦 Quick Start

```bash
git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
cd bpf-bbm-system
docker compose up -d
```

Access

### 🌐 Akses Online (Domain DuckDNS)

Aplikasi diakses publik melalui **domain permanen** `nasbpfsby.duckdns.org` (HTTPS via nginx reverse proxy):

| Halaman | URL Online |
|---------|------------|
| **Login (semua role)** | `https://nasbpfsby.duckdns.org:5000/login` |
| **📣 Marketing Hub** | `https://nasbpfsby.duckdns.org:5000/marketing` |
| **🚛 Chief Driver** | `https://nasbpfsby.duckdns.org:5000/chief-driver` |
| **📱 Driver PWA** | `https://nasbpfsby.duckdns.org:5000/driver` |
| Dashboard Admin | `https://nasbpfsby.duckdns.org:5000/admin` |
| GA Assignments | `https://nasbpfsby.duckdns.org:5000/ga/assignments` |
| Trips | `https://nasbpfsby.duckdns.org:5000/admin/trips` |
| Users | `https://nasbpfsby.duckdns.org:5000/admin/users` |

> ✅ **URL permanen (DuckDNS)** — tidak berubah saat server di-restart. WebSocket/notifikasi real-time aktif (nginx meneruskan header Upgrade).
> ⚠️ **Akses cadangan opsional:** Cloudflare Tunnel *quick tunnel* (URL acak `*.trycloudflare.com`) bisa diaktifkan kembali di `docker-compose.yml` — lihat `DEPLOYMENT.md` §11.

### 🖥️ Akses Lokal (Development)

| Halaman | URL | Aktor |
|---------|-----|-------|
| Login | http://localhost:5001/login | Semua |
| Driver | http://localhost:5001/driver | Driver (tanpa login) |
| **Marketing Hub** | http://localhost:5001/marketing | Marketing |
| **Chief Driver** | http://localhost:5001/chief-driver | Chief Driver, GA |
| Dashboard | http://localhost:5001/admin | GA, Finance, Admin |
| GA Assignments | http://localhost:5001/ga/assignments | GA |
| Rekap | http://localhost:5001/admin/rekap | Finance, Admin |
| Analytics | http://localhost:5001/admin/analytics | Manager, Admin |
| Trips | http://localhost:5001/admin/trips | GA, Admin |
| Users | http://localhost:5001/admin/users | Admin |
| Audit Log | http://localhost:5001/admin/logs | Admin |
| Settings | http://localhost:5001/admin/settings | Admin |

> ⚠️ **Semua halaman admin kini memerlukan login.** Driver PWA tetap terbuka tanpa login.

Default Credentials

| Role | Username | PIN |
|------|----------|-----|
| Admin | admin | 123456 |
| GA | ga_officer | 123456 |
| Finance | finance_officer | 123456 |
| Marketing (buat via Users) | mis. icang | 123456 (set via Users) |
| Chief Driver (buat via Users) | mis. chief_driver | 123456 (set via Users) |

---

## 📁 Project Structure

```
bpf-bbm-system/
├── app.py                          # Main entry point (auth, CSRF, SocketIO)
├── init.sql                        # Schema + data awal (termasuk tabel notifications)
├── modules/
│   ├── config.py                   # DB connection pool
│   ├── helpers.py                  # Utils + role_required decorator
│   ├── engine.py                   # ML insights & rekap
│   ├── pdf_generator.py            # PDF classes (enterprise)
│   ├── excel_generator.py          # Excel export
│   ├── realtime.py                 # SocketIO bus + per-driver rooms
│   ├── notifications.py            # Store & push notifikasi driver/marketing
│   ├── appointments_schema.py      # Migrasi tabel appointments (startup)
│   ├── routes_auth.py              # Login / logout (session, redirect per-role)
│   ├── routes_appointments.py      # Marketing & Chief Driver (halaman + API)
│   ├── routes_driver.py            # Driver & PWA routes
│   ├── routes_admin.py             # Admin dashboard & workflow
│   ├── routes_reports.py           # Reports, rekap, analytics
│   ├── routes_settings.py          # Settings + /admin/users
│   ├── routes_cash.py              # Cash request & LPJ
│   ├── routes_notifications.py     # Notifikasi API
│   ├── routes_api_master.py        # Master data API
│   ├── routes_api_transactions.py  # Transactions API
│   └── routes_api_assignments.py   # Assignments API
├── static/
│   ├── js/
│   │   ├── theme.js                # Dark mode + fetch 401/CSRF wrapper
│   │   ├── admin-ui.js             # Toast/dialog/PIN shared (dashboard)
│   │   ├── admin-tabs.js           # SPA tab switching + load-more arsip
│   │   ├── admin-dashboard.js      # Dashboard actions
│   │   ├── admin-cash.js           # Kasbon admin actions
│   │   ├── admin.js                # Legacy admin helpers
│   │   ├── notifications.js        # Notifikasi driver PWA
│   │   ├── driver.js               # Driver PWA logic
│   │   ├── db.js                   # IndexedDB + cache
│   │   ├── sync.js                 # Background sync
│   │   └── drivers.js              # Driver data loader
│   └── css/                        # 1 file per halaman (base.css + admin/driver/analytics/...)
├── templates/                      # 14 HTML templates (+ _tab_content fragment)
├── scripts/
│   ├── tunnel-check.sh             # Periksa status URL public (online/offline)
│   ├── tunnel-url.sh               # Tampilkan URL public aktif
│   └── release.sh                  # Buat GitHub Release dari CHANGELOG
├── fonts/                          # DejaVu Sans (Unicode PDF)
├── docker-compose.yml              # Service cloudflared (opsional — nonaktif, URL via DuckDNS)
├── Dockerfile
├── README.md
├── DEPLOYMENT.md
└── USER_GUIDE.md
```

---

## 🔒 Security

| Fitur | Deskripsi |
|-------|-----------|
| **Session Login** | `/login` username+PIN, session cookie, logout |
| **Role-Based Access** | `@role_required` di 66 halaman/API (admin/ga/finance) |
| **CSRF Protection** | Token di form + header, exempt untuk endpoint driver PWA |
| **Anti Open-Redirect** | Validasi parameter `next` |
| **GET → POST** | Semua aksi state-changing wajib POST |
| PIN 6-Digit | GA/Finance/Admin (verifikasi ganda di aksi penting) |
| Watermark | GPS + Timestamp di foto |
| Audit Trail | 30+ action types |
| SQL Parameterized | Anti injection |
| Anti-Cache | no-store headers |

---

## 📊 Monitoring

```bash
# Status transaksi
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT status, COUNT(*) FROM transactions GROUP BY status;"

# Audit log
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT created_at, user_name, action FROM activity_logs ORDER BY id DESC LIMIT 20;"

# Cash requests
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT display_id, driver_name, total_amount, status FROM fuel_cash_requests ORDER BY id DESC;"

# Notifikasi driver
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT driver_name, type, message, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 20;"

# Appointment harian
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT appointment_date, sesi, status, COUNT(*) FROM appointments GROUP BY appointment_date, sesi, status ORDER BY appointment_date DESC LIMIT 20;"
```

---

## 📋 Changelog v1.2

- ✅ **Sistem Appointment**: tabel `appointments` + `marketing_teams` + `marketing_members`, role `marketing` & `chief_driver`, migrasi otomatis saat startup (`appointments_schema.py`)
- ✅ **Halaman Marketing Hub** `/marketing`: form multi-input, **nama marketing anggota (wajib, ada saran otomatis)**, sesi 08.30/14.30, deteksi area alamat otomatis, notifikasi real-time
- ✅ **Halaman Chief Driver** `/chief-driver`: board penugasan per sesi & per driver, saran driver load-balancing, **override area manual 🌍**, export Excel harian, board real-time
- ✅ **Integrasi Log Perjalanan**: appointment selesai → auto-terisi di form Trip driver + jejak `appointment_id` di Trip Review
- ✅ **Login redirect per-role**: marketing → `/marketing`, chief_driver → `/chief-driver`
- ✅ **User management**: role Marketing + Chief Driver + field Tim Marketing (auto-register `marketing_teams`)
- ✅ **Tests**: 48+ test PASS + smoke test end-to-end

## 📋 Changelog v1.1

- ✅ **Auth**: login/logout session-based + role_required (66 endpoint)
- ✅ **CSRF protection** di semua POST state-changing (exempt driver PWA)
- ✅ **Konversi GET → POST** untuk semua aksi admin state-changing
- ✅ **Notifikasi driver real-time** (SocketIO per-driver room + offline catch-up)
- ✅ **Halaman User Management** `/admin/users`
- ✅ **Dark mode** di semua halaman admin + login (localStorage, tanpa flash)
- ✅ **Dashboard UX**: SPA tab tanpa reload, sticky context bar, skeleton, bulk approve GA, shortcut keyboard 1–5, count-up
- ✅ **Arsip cerdas**: filter + default 7 hari + tombol "Muat Lebih Banyak"
- ✅ **Refactor modular JS** (12 modul) + CSS per halaman
- ✅ **Tests**: 29+ test PASS (workflow kasbon, driver context, excel generator)

---

## 👥 Roles

| Role | Akses | Default PIN |
|------|-------|-------------|
| Admin | Settings, Users, Audit Log, semua dashboard | 123456 |
| GA Officer | Approve, reject, trip review, serah terima kendaraan, kasbon, chief driver board | 123456 |
| Finance Officer | Payout, Archive, ZIP, Export, ODO Edit, kasbon | 123456 |
| Chief Driver | Command center penugasan driver appointment | 123456 |
| Marketing | Input & kelola appointment prospek nasabah (1 akun bisa untuk banyak anggota tim) | 123456 |
| Driver | Submit BBM, Trip Log, Kasbon, Self-analytics, notifikasi (tanpa login) | - |

---

## 📄 License

Internal use - PT. Bestprofit Futures Surabaya  
Version 1.2 | August 2026  
Developed & Maintained by IT BPF Surabaya
