# ⛽ BPF Fleet & BBM System v1.1

**Sistem Manajemen Armada, Klaim BBM, Kasbon & Log Perjalanan**  
**PT. Bestprofit Futures - Surabaya**

---

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, pengarsipan klaim BBM, **pengajuan kasbon dengan kode unik**, dan log perjalanan harian (logsheet) dengan workflow GA → Finance → Archive. Dilengkapi deteksi anomali Machine Learning, GPS tracking, **watermark foto otomatis**, PIN security, **session-based login & role-based access**, **CSRF protection**, **notifikasi driver real-time**, import Excel, audit trail, Chart.js visualization, **PWA offline-first**, dan **WebSocket real-time**.

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

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Architecture | **Modular** (10 route modules + service layer) |
| Auth | Session-based (PIN users) + role_required + CSRF |
| Real-Time | Flask-SocketIO + eventlet + per-driver rooms |
| Database | MariaDB 10.11 |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF + DejaVu Sans (Unicode) |
| Excel | openpyxl |
| Charts | Chart.js 4.4 |
| Frontend | HTML5 + CSS3 + Vanilla JS (12 JS modules + 9 CSS) |
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

### 🌐 Akses Online (Cloudflare Tunnel)

Aplikasi dapat diakses publik tanpa port forwarding via Cloudflare Tunnel:

| Halaman | URL Online |
|---------|------------|
| **Login admin** | `https://miles-attribute-insulin-fraction.trycloudflare.com/login` |
| **Driver PWA** | `https://miles-attribute-insulin-fraction.trycloudflare.com/driver` |
| Dashboard | `https://miles-attribute-insulin-fraction.trycloudflare.com/admin` |

> ⚠️ **Catatan:** Ini *quick tunnel* — URL acak dan dapat **berubah saat container `cloudflared` di-restart**.
> Gunakan `bash scripts/tunnel-check.sh` untuk melihat & memeriksa URL yang sedang aktif,
> atau `bash scripts/tunnel-url.sh` untuk menampilkan URL saja.
> Untuk URL permanen: named tunnel + domain sendiri (lihat `DEPLOYMENT.md` §11).

### 🖥️ Akses Lokal (Development)

| Halaman | URL | Aktor |
|---------|-----|-------|
| Login | http://localhost:5001/login | Semua |
| Driver | http://localhost:5001/driver | Driver (tanpa login) |
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
│   ├── notifications.py            # Store & push notifikasi driver
│   ├── routes_auth.py              # Login / logout (session)
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
├── templates/                      # 12 HTML templates (+ _tab_content fragment)
├── scripts/
│   ├── tunnel-check.sh             # Periksa status URL public (online/offline)
│   ├── tunnel-url.sh               # Tampilkan URL public aktif
│   └── release.sh                  # Buat GitHub Release dari CHANGELOG
├── fonts/                          # DejaVu Sans (Unicode PDF)
├── docker-compose.yml              # Termasuk service cloudflared (tunnel)
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
```

---

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
| GA Officer | Approve, reject, trip review, serah terima kendaraan, kasbon | 123456 |
| Finance Officer | Payout, Archive, ZIP, Export, ODO Edit, kasbon | 123456 |
| Driver | Submit BBM, Trip Log, Kasbon, Self-analytics, notifikasi (tanpa login) | - |

---

## 📄 License

Internal use - PT. Bestprofit Futures Surabaya  
Version 1.1 | August 2026  
Developed & Maintained by IT BPF Surabaya
