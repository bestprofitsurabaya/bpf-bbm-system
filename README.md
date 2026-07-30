# ⛽ BPF Fleet & BBM System v1.2

**Sistem Manajemen Armada, Klaim BBM, Kasbon & Log Perjalanan**  
**PT. Bestprofit Futures - Surabaya**

---

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, pengarsipan klaim BBM, **pengajuan kasbon dengan kode unik**, dan log perjalanan harian (logsheet) dengan workflow GA → Finance → Archive. Dilengkapi deteksi anomali Machine Learning, GPS tracking, **watermark foto otomatis**, PIN security, import Excel, audit trail, Chart.js visualization, **PWA offline-first**, dan **WebSocket real-time**.

---

## 🆕 Fitur Terbaru v1.2

### 💰 Modul Kasbon (Cash Request)
| Fitur | Deskripsi |
|-------|-----------|
| **Alur Lengkap** | DRAFT → GA → Finance → Handover → LPJ → Completed |
| **Kode Unik Harian** | Rp 100-2.000 (kelipatan 100), berubah setiap hari |
| **LPJ Offline-First** | Form BBM dengan nominal terkunci, IndexedDB queue |
| **Progress Bar** | Visual tracking status pengajuan |
| **Badge Kasbon** | Penanda kuning "💰 Kasbon" di dashboard |

### 🏗️ Modular Architecture
| Module | Fungsi |
|--------|--------|
| `routes_api_master.py` | Master data (vehicles, BBM, drivers, users) |
| `routes_api_transactions.py` | Transactions, cross-check, analytics |
| `routes_api_assignments.py` | Vehicle assignments, swap, release |
| `routes_cash.py` | Cash request, LPJ submission |

---

## 🚀 Fitur Utama

### 📱 Driver (PWA Offline-First)
| Fitur | Deskripsi |
|-------|-----------|
| **4-Tab Navigation** | ⛽ BBM, 💰 Kasbon, 🗺️ Trip, 📊 Rapor |
| **Offline-First** | IndexedDB + localStorage + auto-sync |
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

### ⚙️ Admin Settings
| Fitur | Deskripsi |
|-------|-----------|
| **Driver Management** | Toggle aktif/nonaktif + hapus (3 kolom) |
| **Fleet Kendaraan** | Tambah kendaraan mandiri (tanpa driver) |
| **User & PIN** | Reset PIN via popup 🔑 |
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
| Architecture | **Modular** (7 route modules + 3 API modules) |
| Real-Time | Flask-SocketIO + eventlet |
| Database | MariaDB 10.11 |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF + DejaVu Sans (Unicode) |
| Excel | openpyxl |
| Charts | Chart.js 4.4 |
| Frontend | HTML5 + CSS3 + Vanilla JS (4 JS modules) |
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

Halaman URL Aktor
Driver http://localhost:5001/driver Driver
Dashboard http://localhost:5001/admin GA & Finance
GA Assignments http://localhost:5001/ga/assignments GA
Rekap http://localhost:5001/admin/rekap Finance
Analytics http://localhost:5001/admin/analytics Manager
Trips http://localhost:5001/admin/trips GA
Audit Log http://localhost:5001/admin/logs Admin
Settings http://localhost:5001/admin/settings Admin

Default Credentials

Role Username PIN
Admin admin 123456
GA ga_officer 123456
Finance finance_officer 123456

---

📁 Project Structure

```
bpf-bbm-system/
├── app.py                          # Main entry point
├── modules/
│   ├── config.py                   # DB connection pool
│   ├── helpers.py                  # Utility functions
│   ├── engine.py                   # ML insights & rekap
│   ├── pdf_generator.py            # PDF classes (enterprise)
│   ├── excel_generator.py          # Excel export
│   ├── routes_driver.py            # Driver & PWA routes
│   ├── routes_admin.py             # Admin dashboard & workflow
│   ├── routes_reports.py           # Reports, rekap, analytics
│   ├── routes_settings.py          # Settings routes
│   ├── routes_cash.py              # Cash request & LPJ
│   ├── routes_api_master.py        # Master data API
│   ├── routes_api_transactions.py  # Transactions API
│   └── routes_api_assignments.py   # Assignments API
├── static/
│   ├── js/db.js                    # IndexedDB + cache
│   ├── js/sync.js                  # Background sync
│   └── js/drivers.js               # Driver data loader
├── templates/                      # 8 HTML templates
├── fonts/                          # DejaVu Sans (Unicode PDF)
├── docker-compose.yml
├── Dockerfile
├── README.md
└── USER_GUIDE.md
```

---

🔒 Security

Fitur Deskripsi
PIN 6-Digit GA/Finance/Admin
Watermark GPS + Timestamp di foto
Audit Trail 30+ action types
SQL Parameterized Anti injection
Anti-Cache no-store headers
PIN Gate Settings & Audit Log only

---

📊 Monitoring

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
```

---

📝 Changelog

v1.2 (Current)

· ✅ Modul Kasbon (Cash Request) dengan kode unik harian
· ✅ Modular API architecture (3 API modules)
· ✅ Display ID konsisten di semua tempat
· ✅ Transaction type: CLAIM vs CASH_LPJ
· ✅ UX: Progress bar, Dark mode, Skeleton loading, Swipe, Pull-to-refresh
· ✅ PDF: Grid foto 2×2, DejaVu Sans font, enterprise letterhead
· ✅ Professional USER_GUIDE with troubleshooting + glossary

v1.1

· ✅ GA Assignments (assign, swap, release)
· ✅ Driver toggle + delete + reset PIN
· ✅ Fleet kendaraan mandiri
· ✅ Unified navbar + footer
· ✅ Enterprise PDF with BPFBasePDF

v1.0

· ✅ PWA Offline-First
· ✅ Watermark otomatis
· ✅ Cross-Check Verifikasi
· ✅ Finance Review Panel
· ✅ Modular route architecture
· ✅ Chart.js analytics

---

👥 Roles

Role Akses Default PIN
Admin Settings, Audit Log, semua dashboard 123456
GA Officer Approve, reject, trip review, serah terima kendaraan, kasbon 123456
Finance Officer Payout, Archive, ZIP, Export, ODO Edit, kasbon 123456
Driver Submit BBM, Trip Log, Kasbon, Self-analytics -

---

📄 License

Internal use - PT. Bestprofit Futures Surabaya
Version 1.2 | July 2026
Developed & Maintained by IT BPF Surabaya
