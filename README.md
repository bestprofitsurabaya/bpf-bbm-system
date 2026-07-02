# ⛽ BPF BBM System

**Sistem Manajemen Klaim BBM PT. Bestprofit Surabaya**

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, dan pengarsipan klaim BBM dengan workflow GA → Finance → Archive.

---

## 🚀 Fitur Utama

### 📱 Driver
- **Form input klaim** dengan auto-fill data kendaraan
- **GPS auto-detection** dengan alamat administratif + SPBU terdekat
- **Watermark otomatis** pada foto (tanggal, jam, lokasi)
- **Kompresi gambar client-side** untuk upload cepat
- **PWA Support** - Install di homescreen smartphone

### 👨‍💼 GA (General Affairs)
- **Dashboard tab view** - Antrean GA / Finance / Driver TTD / Arsip
- **PIN Security** - Verifikasi 6-digit sebelum approve
- **Preview foto** & dokumen sebelum persetujuan
- **Reject dengan alasan** - Transaksi ditolak + catatan

### 💰 Finance
- **Disburse dana** - Konfirmasi pencairan dengan PIN
- **Archive** - Konfirmasi tanda tangan driver + arsip
- **Download ZIP** - Semua bukti dalam 1 file arsip
- **PDF Report** - Laporan profesional 1 halaman

### 📊 Analytics & Rekap
- **Rekapitulasi transaksi** - Filter tanggal, nopol, driver
- **Performa kendaraan** - KM/L, appointment, status
- **Statistik harian** - 30 hari terakhir
- **Export PDF** - Laporan dengan tanda tangan

### ⚙️ Admin Settings
- **Manajemen Driver-Kendaraan** - Mapping driver ke nopol
- **Manajemen User & PIN** - GA, Finance, Admin
- **Kendaraan & BBM** - CRUD tipe kendaraan & jenis BBM
- **Batas konsumsi** - Good/Warning/Min/Max per kendaraan
- **PIN Gate** - Settings hanya bisa diakses dengan PIN Admin

---

## 🔄 Workflow

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│ DRIVER  │────▶│   GA    │────▶│ FINANCE  │────▶│ DRIVER  │────▶│ ARCHIVE │
│ Submit  │     │ Approve │     │ Payout   │     │ TTD OS  │     │  ZIP    │
│ pending │     │verified │     │os_finance│     │archived │     │ download│
└─────────┘     └─────────┘     └──────────┘     └─────────┘     └─────────┘
```

| Step | Aktor | Action | Status |
|------|-------|--------|--------|
| 1 | Driver | Submit klaim via PWA | `pending` |
| 2 | **GA** | Verifikasi + Approve (PIN) | `verified_ga` |
| 3 | **Finance** | Cairkan dana (PIN) | `os_finance` |
| 4 | Driver | Tanda tangan OS (fisik) | - |
| 5 | **Finance** | Archive + Download ZIP (PIN) | `archived` |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Database | MariaDB 10.11 |
| Web Server | Gunicorn (4 workers, 2 threads) |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF (custom layout) |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| PWA | Service Worker + Manifest |
| Container | Docker + Docker Compose |
| Reverse Proxy | Nginx (optional) |

---

## 📦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
cd bpf-bbm-system

# Start services
docker compose up -d

# Initialize database (first time only)
docker exec -i bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system < init.sql

# Access application
# Driver:  http://localhost:5001/driver
# Admin:   http://localhost:5001/admin
```

### Default Credentials

| Role | Username | PIN |
|------|----------|-----|
| Admin | `admin` | `123456` |
| GA Officer | `ga_officer` | `123456` |
| Finance Officer | `finance_officer` | `123456` |

> ⚠️ **Ganti PIN default segera** di Settings → Manajemen User & PIN

---

## 📁 Project Structure

```
bpf-bbm-system/
├── app.py                  # Main Flask application
├── init.sql                # Database schema
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Multi-container orchestration
├── manifest.json           # PWA manifest
├── sw.js                   # Service Worker
├── README.md               # This file
├── templates/
│   ├── admin.html          # Dashboard tab view
│   ├── driver.html         # Driver claim form
│   ├── rekap.html          # Rekapitulasi
│   ├── analytics.html      # Performance analytics
│   ├── settings.html       # Admin settings
│   └── assignments.html    # Driver assignments (legacy)
├── static/
│   ├── icon-192.png        # PWA icon 192x192
│   └── icon-512.png        # PWA icon 512x512
└── uploads/                # Uploaded photos (mounted volume)
```

---

## 🔌 API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vehicles` | List active vehicles |
| GET | `/api/bbm_types` | List active BBM types |
| GET | `/api/drivers` | List active driver assignments |
| GET | `/api/vehicle_bbm/<type>` | BBM allowed for vehicle |
| POST | `/api/verify-pin` | Verify user PIN |

### Driver
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/driver` | Submit claim form |

### GA
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ga/approve/<id>` | Approve transaction (GA) |

### Finance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/finance/payout/<id>` | Confirm payout |
| GET | `/finance/archive/<id>` | Archive transaction |
| GET | `/finance/download-archive/<id>` | Download ZIP bundle |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/admin` | Dashboard |
| POST | `/admin/reject/<id>` | Reject transaction |
| GET | `/admin/rekap` | Rekapitulasi |
| GET | `/admin/rekap/pdf` | Export PDF rekap |
| GET | `/admin/analytics` | Performance analytics |
| GET/POST | `/admin/settings` | System settings |
| GET | `/admin/report/<id>` | Single transaction PDF |
| GET | `/admin/unverify/<id>` | Return to pending |
| GET | `/admin/delete/<id>` | Delete transaction |
| GET | `/uploads/<filename>` | Serve uploaded file |

---

## 🗄 Database Schema

### `transactions`
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| driver_name | VARCHAR | Driver name |
| nopol | VARCHAR | License plate |
| vehicle_type | VARCHAR | Vehicle type |
| bbm_type | VARCHAR | Fuel type |
| nominal | DECIMAL | Amount (Rp) |
| liter | DECIMAL | Volume (L) |
| price_per_liter | DECIMAL | Price per liter |
| odo_km | INT | Odometer reading |
| jumlah_appointment | INT | Marketing appointments |
| km_per_liter | DECIMAL | Fuel efficiency |
| status | ENUM | pending, verified_ga, os_finance, archived, rejected, modified |
| gps_latitude | DECIMAL | GPS coordinate |
| gps_longitude | DECIMAL | GPS coordinate |
| gps_address | TEXT | Reverse geocoded address |
| ga_approved_by | VARCHAR | GA approver name |
| ga_approved_at | DATETIME | GA approval timestamp |
| finance_payout_by | VARCHAR | Finance officer name |
| finance_payout_at | DATETIME | Payout timestamp |
| archived_by | VARCHAR | Archiver name |
| archived_at | DATETIME | Archive timestamp |
| created_at | TIMESTAMP | Record creation |
| updated_at | TIMESTAMP | Last update |

### `drivers`
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| name | VARCHAR | Driver name (unique) |
| nopol | VARCHAR | Assigned vehicle |
| vehicle_type | VARCHAR | Vehicle type |
| bbm_type | VARCHAR | Default BBM |
| is_active | TINYINT | Active status |

### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| username | VARCHAR | Login username |
| full_name | VARCHAR | Display name |
| role | ENUM | admin, ga, finance |
| pin | VARCHAR | 6-digit PIN |
| is_active | TINYINT | Active status |
| last_login | DATETIME | Last login time |

---

## 🔒 Security Features

- **PIN Authentication** - Required for GA approval, Finance payout, and Archive
- **Settings PIN Gate** - Admin-only access to system configuration
- **Audit Trail** - Every action logged with user + timestamp
- **Watermark** - GPS location + timestamp embedded in photos
- **Status Workflow** - Linear progression prevents unauthorized skips
- **SQL Injection Prevention** - Parameterized queries throughout
- **File Upload Validation** - Image type checking + compression

---

## 🐳 Docker Deployment

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f web

# Restart
docker compose restart web

# Stop
docker compose down

# Complete rebuild
docker compose down
docker rmi bpf-bbm-system-web
docker compose build --no-cache web
docker compose up -d
```

### Port Mapping
| Service | Host | Container |
|---------|------|-----------|
| Web App | `5001` | `5000` |
| MariaDB | `3307` | `3306` |

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | `db` | Database host |
| DB_USER | `bpf_user` | Database user |
| DB_PASSWORD | `bpf_pass` | Database password |
| DB_NAME | `bpf_asset_system` | Database name |
| DB_POOL_SIZE | `15` | Connection pool size |
| SECRET_KEY | *(auto)* | Flask secret key |
| FLASK_DEBUG | `0` | Debug mode |

---

## 📊 Monitoring & Maintenance

```bash
# Check transaction status distribution
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT status, COUNT(*) FROM transactions GROUP BY status;"

# View recent transactions
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT id, nopol, driver_name, status, created_at FROM transactions ORDER BY id DESC LIMIT 10;"

# Check user logins
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT username, role, last_login FROM users;"

# Check driver assignments
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT name, nopol, vehicle_type, bbm_type, is_active FROM drivers;"
```

---

## 🎨 UI Theme

- **Primary**: Blue-600 (#2563eb)
- **Font**: Inter (Google Fonts)
- **Design**: Clean corporate, high contrast
- **Responsive**: Desktop + Mobile
- **PWA**: Installable, offline-capable

---

## 📝 Changelog

### v3.0 (July 2026)
- ✅ GA → Finance → Archive workflow
- ✅ PIN security system (6-digit)
- ✅ Driver-vehicle master data + auto-fill
- ✅ GPS administrative location + SPBU finder
- ✅ Auto-watermark on photos
- ✅ Professional PDF report (narrow margin, humanistic narrative)
- ✅ User management (CRUD + role-based)
- ✅ Settings PIN gate
- ✅ Modern UI theme (Inter font, blue palette)
- ✅ Analytics with appointment tracking
- ✅ ZIP archive download

### v2.0 (June 2026)
- ✅ PWA support
- ✅ Image compression
- ✅ ML anomaly detection
- ✅ Daily summary

### v1.0 (Initial)
- ✅ Basic claim submission
- ✅ Photo upload
- ✅ PDF report

---

## 👥 User Roles

| Role | Access | Default PIN |
|------|--------|-------------|
| **Admin** | Settings, all dashboards, user management | `123456` |
| **GA Officer** | Approve claims (Antrean GA tab) | `123456` |
| **Finance Officer** | Payout, Archive, Download ZIP | `123456` |
| **Driver** | Submit claims only | - |

---

## 📞 Support

**PT. Bestprofit Surabaya**  
Sistem Klaim BBM Internal  
Version: 3.0 | Last Updated: July 2026

---

## 📄 License

Internal use only - PT. Bestprofit Surabaya
EOF

echo "✓ README.md updated"
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ README.md Updated - Comprehensive Documentation            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
```

---

## 📋 **README Baru Mencakup:**

| Section | Content |
|---------|---------|
| 🚀 Fitur Utama | Per-role (Driver, GA, Finance, Analytics, Settings) |
| 🔄 Workflow | Diagram + tabel step-by-step |
| 🛠 Tech Stack | Semua teknologi yang digunakan |
| 📦 Quick Start | Clone → Docker up → Akses |
| 🔑 Default Credentials | Admin, GA, Finance PIN |
| 📁 Project Structure | Tree folder lengkap |
| 🔌 API Endpoints | Semua endpoint + method + deskripsi |
| 🗄 Database Schema | Tabel penting + kolom |
| 🔒 Security | PIN, audit trail, watermark, SQL injection |
| 🐳 Docker | Deploy, restart, rebuild commands |
| 📊 Monitoring | Query maintenance harian |
| 🎨 UI Theme | Warna + font |
| 📝 Changelog | v1.0 → v2.0 → v3.0 |
| 👥 User Roles | Tabel peran + akses + default PIN |
