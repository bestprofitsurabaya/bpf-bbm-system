# ? BPF BBM System v1.0

**Sistem Manajemen Klaim BBM PT. Bestprofit Surabaya**

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, dan pengarsipan klaim BBM dengan workflow GA ? Finance ? Archive. Dilengkapi dengan deteksi anomali Machine Learning, GPS tracking, watermark foto otomatis, dan PIN security.

---

## ?? Fitur Utama

### ?? Driver (PWA)
| Fitur | Deskripsi |
|-------|-----------|
| Auto-fill Form | Pilih nama ? Nopol, Kendaraan, BBM otomatis terisi |
| GPS Auto-Detect | Alamat administratif lengkap + SPBU terdekat |
| Watermark Otomatis | Tanggal, jam, dan lokasi tertanam di setiap foto |
| Kompresi Client-Side | Foto dikecilkan sebelum upload (hemat bandwidth) |
| Self-Analytics | Cek performa kendaraan sendiri via input nopol |
| PWA Installable | Install di homescreen smartphone |

### ????? GA (General Affairs)
| Fitur | Deskripsi |
|-------|-----------|
| Tab View Dashboard | Antrean GA / Finance / Driver TTD / Arsip |
| PIN Security 6-Digit | Verifikasi sebelum approve |
| Preview Foto | Lihat bukti sebelum persetujuan |
| Reject + Alasan | Tolak transaksi dengan catatan |
| Workflow Indicator | Progress bar GA ? Finance ? TTD ? Arsip |

### ?? Finance
| Fitur | Deskripsi |
|-------|-----------|
| Disburse Dana | Konfirmasi pencairan dengan PIN |
| Archive | Konfirmasi tanda tangan driver |
| Download ZIP | Semua bukti + info transaksi dalam 1 file |
| PDF Report | Laporan profesional 1 halaman per transaksi |

### ?? Analytics & Rekap
| Fitur | Deskripsi |
|-------|-----------|
| Rekapitulasi | Filter tanggal, nopol, driver |
| Performa Kendaraan | KM/L, appointment, status ML |
| Statistik Harian | 30 hari terakhir |
| Cetak Rapor Massal | ZIP bundle berisi PDF per driver |
| Human Insight Engine | Narasi saran berkendara berbasis AI |
| Export PDF | Laporan dengan tanda tangan |

### ?? Admin Settings
| Fitur | Deskripsi |
|-------|-----------|
| Driver-Kendaraan | Mapping driver ke nopol + BBM |
| User & PIN | Kelola GA, Finance, Admin + PIN |
| Kendaraan & BBM | CRUD tipe kendaraan & jenis BBM |
| Batas Konsumsi | Good/Warning/Min/Max per kendaraan |
| PIN Gate | Settings hanya bisa diakses dengan PIN Admin |
| Backup Database | Download SQL dump |
| Dummy Data Toggle | Data demo on/off |

---

## ?? Workflow

```
+---------+     +---------+     +----------+     +---------+     +---------+
¦ DRIVER  ¦----?¦   GA    ¦----?¦ FINANCE  ¦----?¦ DRIVER  ¦----?¦ ARCHIVE ¦
¦ Submit  ¦     ¦ Approve ¦     ¦ Payout   ¦     ¦ TTD OS  ¦     ¦  ZIP    ¦
¦ pending ¦     ¦verified ¦     ¦os_finance¦     ¦archived ¦     ¦ download¦
+---------+     +---------+     +----------+     +---------+     +---------+
```

| Step | Aktor | Action | Status |
|------|-------|--------|--------|
| 1 | Driver | Submit klaim via PWA | `pending` |
| 2 | **GA** | Verifikasi + Approve (PIN) | `verified_ga` |
| 3 | **Finance** | Cairkan dana (PIN) | `os_finance` |
| 4 | Driver | Tanda tangan OS (fisik) | - |
| 5 | **Finance** | Archive + Download ZIP (PIN) | `archived` |

---

## ?? Tech Stack

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
| Font | Inter (Google Fonts) |

---

## ?? Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

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
| Settings | `http://localhost:5001/admin/settings` | Admin |

### Default Credentials

| Role | Username | PIN |
|------|----------|-----|
| Admin | `admin` | `123456` |
| GA Officer | `ga_officer` | `123456` |
| Finance Officer | `finance_officer` | `123456` |

> ?? **Ganti PIN default segera** di Settings ? Manajemen User & PIN

---

## ?? Project Structure

```
bpf-bbm-system/
+-- app.py                  # Main Flask application
+-- init.sql                # Database schema + seed data
+-- requirements.txt        # Python dependencies
+-- Dockerfile              # Container build
+-- docker-compose.yml      # Multi-container orchestration
+-- manifest.json           # PWA manifest
+-- sw.js                   # Service Worker
+-- README.md               # Documentation
+-- templates/
¦   +-- admin.html          # Dashboard with tab view + PIN modal
¦   +-- driver.html         # Driver claim form + auto-fill + GPS
¦   +-- rekap.html          # Rekapitulasi with filters
¦   +-- analytics.html      # Performance analytics + export modal
¦   +-- settings.html       # Admin settings + PIN gate
+-- static/
¦   +-- icon-192.png        # PWA icon 192x192
¦   +-- icon-512.png        # PWA icon 512x512
+-- uploads/                # Uploaded photos (mounted volume)
```

---

## ?? API Endpoints

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
| GET | `/api/get-feedback/<nopol>` | Self-analytics rapor |

### GA
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ga/approve/<id>` | Approve transaction (PIN required) |

### Finance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/finance/payout/<id>` | Confirm payout |
| GET | `/finance/archive/<id>` | Archive transaction |
| GET | `/finance/download-archive/<id>` | Download ZIP bundle |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/admin` | Dashboard with tab view |
| POST | `/admin/reject/<id>` | Reject transaction |
| GET | `/admin/rekap` | Rekapitulasi |
| GET | `/admin/rekap/pdf` | Export PDF rekap |
| GET | `/admin/analytics` | Performance analytics |
| POST | `/admin/analytics/export` | Export ZIP rapor massal |
| GET/POST | `/admin/settings` | System settings |
| GET | `/admin/report/<id>` | Single transaction PDF |
| GET | `/admin/backup` | Download database backup |
| GET | `/admin/unverify/<id>` | Return to pending |
| GET | `/admin/delete/<id>` | Delete transaction |
| POST | `/api/dummy-data/toggle` | Toggle demo data |
| GET | `/uploads/<filename>` | Serve uploaded file |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List users |
| POST | `/api/users/sync` | Create/update user |
| POST | `/api/drivers/sync` | Sync driver assignment |
| POST | `/api/drivers/<name>/deactivate` | Deactivate driver |

---

## ?? Database Schema

### `transactions`
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| driver_name | VARCHAR(100) | Driver name |
| nopol | VARCHAR(20) | License plate |
| vehicle_type | VARCHAR(50) | Vehicle type |
| bbm_type | VARCHAR(50) | Fuel type |
| nominal | DECIMAL(15,2) | Amount (Rp) |
| liter | DECIMAL(10,2) | Volume (L) |
| price_per_liter | DECIMAL(10,2) | Price per liter |
| odo_km | INT | Odometer reading |
| jumlah_appointment | INT | Marketing appointments |
| km_per_liter | DECIMAL(10,2) | Fuel efficiency |
| status | ENUM | pending, verified_ga, os_finance, archived, rejected, modified |
| gps_latitude | DECIMAL(10,8) | GPS coordinate |
| gps_longitude | DECIMAL(11,8) | GPS coordinate |
| gps_address | TEXT | Reverse geocoded address |
| is_dummy | TINYINT(1) | Dummy data flag |
| ga_approved_by | VARCHAR(100) | GA approver |
| ga_approved_at | DATETIME | GA timestamp |
| finance_payout_by | VARCHAR(100) | Finance officer |
| finance_payout_at | DATETIME | Payout timestamp |
| archived_by | VARCHAR(100) | Archiver |
| archived_at | DATETIME | Archive timestamp |

### `drivers`
| Column | Type | Description |
|--------|------|-------------|
| name | VARCHAR(100) | Driver name (unique) |
| nopol | VARCHAR(20) | Assigned vehicle |
| vehicle_type | VARCHAR(50) | Vehicle type |
| bbm_type | VARCHAR(50) | Default BBM |
| is_active | TINYINT(1) | Active status |

### `users`
| Column | Type | Description |
|--------|------|-------------|
| username | VARCHAR(50) | Login username |
| full_name | VARCHAR(100) | Display name |
| role | ENUM | admin, ga, finance |
| pin | VARCHAR(255) | 6-digit PIN |
| is_active | TINYINT(1) | Active status |
| last_login | DATETIME | Last login timestamp |

---

## ?? Security Features

| Fitur | Deskripsi |
|-------|-----------|
| PIN Authentication | 6-digit PIN untuk GA/Finance/Admin |
| Settings PIN Gate | Admin-only access |
| Audit Trail | Setiap action dicatat (user + timestamp) |
| Watermark | GPS + timestamp di foto |
| Workflow Linear | Tidak bisa skip tahapan |
| SQL Parameterized | Anti SQL injection |
| File Validation | Hanya terima gambar |
| Dummy Data Isolation | Data demo tidak muncul di dashboard |

---

## ?? Docker Deployment

```bash
# Start
docker compose up -d

# Build + Start
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

## ?? Monitoring & Maintenance

```bash
# Check transaction distribution
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT status, COUNT(*) FROM transactions GROUP BY status;"

# View recent transactions
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT id, nopol, driver_name, km_per_liter, status, created_at FROM transactions ORDER BY id DESC LIMIT 10;"

# Check user logins
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT username, role, last_login FROM users;"

# Check driver assignments
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT name, nopol, vehicle_type, bbm_type, is_active FROM drivers;"

# Check km_per_liter statistics
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT COUNT(*) as total, SUM(CASE WHEN km_per_liter>0 THEN 1 ELSE 0 END) as has_kml, ROUND(AVG(NULLIF(km_per_liter,0)),2) as avg_kml FROM transactions WHERE status IN ('verified_ga','os_finance','archived');"

# Backup database (via Settings page)
# http://NAS_IP:5001/admin/settings ? Download Backup (.sql)
```

---

## ?? UI Theme

| Element | Value |
|---------|-------|
| Primary Color | `#2563eb` (Blue-600) |
| Font | Inter (Google Fonts) |
| Design | Clean corporate, high contrast |
| Responsive | Desktop + Mobile |
| PWA | Installable, offline-capable |

---

## ?? User Roles

| Role | Access | Default PIN |
|------|--------|-------------|
| **Admin** | Settings, all dashboards, user management, backup | `123456` |
| **GA Officer** | Approve claims (Antrean GA tab) | `123456` |
| **Finance Officer** | Payout, Archive, Download ZIP, Export Rapor | `123456` |
| **Driver** | Submit claims, self-analytics | - |

---

## ?? Changelog

### v1.0 (July 2026) - Stable Release
- ? GA ? Finance ? Archive workflow
- ? PIN security system (6-digit)
- ? Driver-vehicle master data + auto-fill
- ? GPS administrative location + SPBU finder
- ? Auto-watermark on photos (date, time, location)
- ? Professional PDF report (narrow margin, humanistic narrative)
- ? User management (CRUD + role-based)
- ? Settings PIN gate (admin only)
- ? Modern UI theme (Inter font, blue palette)
- ? Analytics with appointment tracking
- ? Human Insight Engine (AI-driven coaching)
- ? ZIP archive download (all evidence)
- ? Rapor massal export (per driver PDF)
- ? Dummy data toggle (demo mode)
- ? Database backup (download SQL)
- ? PWA support (installable)
- ? Image compression (client-side)
- ? ML anomaly detection (Isolation Forest)
- ? Audit trail (activity logs)
- ? Connection pooling (MySQLConnectionPool)
- ? SQL injection prevention (parameterized queries)
- ? km_per_liter auto-calculation (NULLIF + previous ODO tracking)
- ? Responsive design (mobile + desktop)

---

## ?? License

Internal use - PT. Bestprofit Surabaya  
Version 1.0 | July 2026