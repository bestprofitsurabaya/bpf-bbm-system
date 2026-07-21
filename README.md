# ⛽ BPF BBM System v1.0

**Sistem Manajemen Klaim BBM & Log Perjalanan PT. Bestprofit Futures - Surabaya**

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, pengarsipan klaim BBM, dan log perjalanan harian (logsheet) dengan workflow GA → Finance → Archive. Dilengkapi deteksi anomali Machine Learning, GPS tracking, **watermark foto otomatis**, PIN security, import Excel, audit trail, Chart.js visualization, **PWA offline-first**, dan **WebSocket real-time**.

---

## 🚀 Fitur Utama

### 📱 Driver (PWA Offline-First)
| Fitur | Deskripsi |
|-------|-----------|
| **Bottom Navigation** | 3-tab: ⛽ BBM, 🗺️ Trip, 📊 Rapor |
| **Offline-First** | IndexedDB storage + auto-sync saat online |
| Auto-fill Form | Pilih nama → Nopol & Kendaraan otomatis terisi |
| Multi-BBM Flexible | Dropdown BBM menampilkan semua jenis yang diizinkan |
| GPS Auto-Detect | Alamat administratif lengkap + SPBU terdekat |
| **Watermark Otomatis** | GPS + Waktu + Nama Perusahaan di setiap foto |
| **Watermark Preview** | Driver bisa review watermark sebelum submit |
| One-Click GPS Trip | Klik 📍 → lokasi + jam + KM terisi otomatis |
| Self-Analytics | Cek performa kendaraan + AI coaching insight |
| PWA Installable | Install di homescreen, auto-update |

### 👨‍💼 GA (General Affairs)
| Fitur | Deskripsi |
|-------|-----------|
| Tab View Dashboard | Antrean GA / Finance / Driver TTD / Arsip |
| PIN Security 6-Digit | Verifikasi wajib sebelum approve |
| **Real-Time WebSocket** | Notifikasi instan saat driver submit |
| High-Contrast Pulse | Kartu Pending berkedip merah jika ada antrean |
| Preview Foto | Lihat bukti + watermark sebelum persetujuan |
| Reject + Alasan | Tolak transaksi dengan catatan |

### 💰 Finance
| Fitur | Deskripsi |
|-------|-----------|
| Total Payout Summary | Ringkasan nominal yang harus dicairkan |
| Disburse Dana | Konfirmasi pencairan dengan PIN |
| Archive + ZIP | Download semua bukti dalam 1 file ZIP |
| PDF Report | Laporan profesional 1 halaman + Kop Surat |
| Cetak Rapor Massal | ZIP bundle PDF per driver |

### 📊 Analytics & Rekap
| Fitur | Deskripsi |
|-------|-----------|
| Rekapitulasi | Default 7 hari, pagination 75/halaman |
| Grouped Columns | Waktu+Driver, Armada+BBM, ODO+Jarak |
| Color-coded KM/L | Hijau (≥11), Kuning (9-11), Merah (≤9) |
| ⛽ TOP-UP Badge | Indikator transaksi multifill |
| Bar Chart | Peringkat efisiensi kendaraan |
| Line Chart | Tren konsumsi BBM harian |
| Dynamic PDF | Title & filename dinamis + Kop Surat |

### ⚙️ Admin Settings
| Fitur | Deskripsi |
|-------|-----------|
| **Smart Master Data** | Auto-register driver/kendaraan/BBM baru |
| Soft Deletion | is_active flag (tidak hard delete) |
| User & PIN | Kelola GA, Finance, Admin + PIN 6-digit |
| Multi-BBM Config | Satu kendaraan bisa beberapa jenis BBM |
| Multifill Threshold | Atur batas KM deteksi top-up |
| PIN Gate | Settings & Audit Log hanya Admin |
| Backup Database | Download SQL dump |
| Dummy Data Toggle | Data demo on/off |
| Import Excel | Auto-register + validasi |

### 🔒 Audit Trail
| Fitur | Deskripsi |
|-------|-----------|
| Complete Coverage | 15+ action types: create, approve, payout, archive, reject, unverify, delete, settings_save, backup_download, excel_import, dummy_toggle, driver_sync, user_sync, template_download, trip_submit, trip_verify, trip_reject |
| PIN Protected | Halaman log hanya Admin |
| Real-time | Setiap action tercatat otomatis |

---

## 🔄 Workflow

```
DRIVER → GA Approve → Finance Payout → Driver TTD → Archive ZIP
  │          │              │               │            │
  └─ pending └─ verified_ga └─ os_finance   └─ archived └─ download
```

| Step | Aktor | Action | Status | PIN |
|------|-------|--------|--------|-----|
| 1 | Driver | Submit klaim via PWA | `pending` | - |
| 2 | **GA** | Verifikasi + Approve | `verified_ga` | ✅ |
| 3 | **Finance** | Cairkan dana | `os_finance` | ✅ |
| 4 | Driver | Tanda tangan OS (fisik) | - | - |
| 5 | **Finance** | Archive + Download ZIP | `archived` | ✅ |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Real-Time | Flask-SocketIO + eventlet |
| Database | MariaDB 10.11 |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF (custom layout + logo) |
| Excel | openpyxl (template + import) |
| Charts | Chart.js 4.4 |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| PWA | Service Worker v4 + IndexedDB |
| Offline | IndexedDB (BPF_Driver_DB) |
| Container | Docker + Docker Compose |
| Font | Inter (Google Fonts) |
| GPS | Nominatim (OpenStreetMap) |

---

## 📦 Quick Start

```bash
git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
cd bpf-bbm-system
docker compose up -d
```

### Access
| Halaman | URL | Aktor |
|---------|-----|-------|
| Driver | `http://localhost:5001/driver` | Driver |
| Dashboard | `http://localhost:5001/admin` | GA & Finance |
| Rekap | `http://localhost:5001/admin/rekap` | Finance |
| Analytics | `http://localhost:5001/admin/analytics` | Manager |
| Trips | `http://localhost:5001/admin/trips` | GA |
| Audit Log | `http://localhost:5001/admin/logs` | Admin |
| Settings | `http://localhost:5001/admin/settings` | Admin |

### Default Credentials

| Role | Username | PIN |
|------|----------|-----|
| Admin | `admin` | `123456` |
| GA Officer | `ga_officer` | `123456` |
| Finance Officer | `finance_officer` | `123456` |

---

## 📁 Project Structure

```
bpf-bbm-system/
├── app.py                  # Main Flask routes
├── modules/
│   ├── config.py           # DB connection pool
│   ├── engine.py           # ML, insights, rekap
│   ├── pdf_generator.py    # PDF classes + Kop Surat
│   └── excel_generator.py  # Trip logsheet export
├── templates/
│   ├── base.html           # Global layout + Socket.io
│   ├── admin.html          # Dashboard + WebSocket
│   ├── driver.html         # PWA Offline-First
│   ├── rekap.html          # Rekapitulasi
│   ├── analytics.html      # Analytics + Chart.js
│   ├── settings.html       # Settings + PIN gate
│   ├── trips_review.html   # Trip log review
│   └── logs.html           # Audit trail
├── static/
│   ├── icon-192.png        # Favicon + PWA icon
│   └── icon-512.png        # PWA icon + Kop Surat
├── init.sql                # Database schema
├── docker-compose.yml      # Multi-container
├── Dockerfile              # Container build
├── requirements.txt        # Python dependencies
├── sw.js                   # Service Worker v4
├── manifest.json           # PWA manifest
├── README.md               # Documentation
└── USER_GUIDE.md           # User guide per role
```

---

## 🔒 Security

| Fitur | Deskripsi |
|-------|-----------|
| PIN 6-Digit | GA/Finance/Admin |
| Watermark | GPS + Timestamp di foto |
| Audit Trail | 15+ action types |
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

# Backup
# http://NAS_IP:5001/admin/settings → Download Backup
```

---

## 🎨 UI Theme

| Element | Value |
|---------|-------|
| Primary | `#2563eb` (Blue-600) |
| Font | Inter |
| Cards | White + shadow + border |
| Tables | Grouped columns, zebra-stripe |
| Charts | Chart.js (bar + line) |
| PWA | Bottom nav, offline-first |

---

## 👥 Roles

| Role | Akses | Default PIN |
|------|-------|-------------|
| **Admin** | Settings, Audit Log, semua dashboard | `123456` |
| **GA Officer** | Approve, reject, trip review | `123456` |
| **Finance Officer** | Payout, Archive, ZIP, Export | `123456` |
| **Driver** | Submit BBM, Trip Log, Self-analytics | - |

---

## 📝 Changelog v1.0

- ✅ PWA Bottom Navigation (BBM | Trip | Rapor)
- ✅ Offline-First (IndexedDB + auto-sync)
- ✅ Watermark otomatis (GPS + Waktu + Perusahaan)
- ✅ Watermark preview sebelum submit
- ✅ One-Click GPS fill (lokasi + jam + KM)
- ✅ WebSocket real-time Admin dashboard
- ✅ Smart Master Data Engine (auto-register)
- ✅ Soft deletion drivers
- ✅ GA → Finance → Archive workflow
- ✅ PIN security 6-digit
- ✅ Audit trail (15+ action types)
- ✅ Chart.js visualization
- ✅ Multifill detection + TOP-UP badge
- ✅ Dynamic PDF + Kop Surat logo
- ✅ Excel import + auto-register
- ✅ Favicon + Kop Surat di semua dokumen
- ✅ Modular architecture
- ✅ PWA installable + auto-update

---

## 📄 License

Internal use - PT. Bestprofit Futures Surabaya  
Version 1.0 | July 2026  
Developed & Maintained by **IT BPF Surabaya**
