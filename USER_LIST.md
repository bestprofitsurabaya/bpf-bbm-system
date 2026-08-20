# 📋 Daftar User — BPF WorkHub

> Dokumen ini dibuat berdasarkan analisis kode sumber (`init.sql`, `modules/`, `CHANGELOG.md`).
> Per **20 Agustus 2026**.

---

## 📌 Default Users (Seed Data)

Users berikut dibuat otomatis saat inisialisasi database (`init.sql`):

| # | Username | Full Name | Role | PIN Default | Keterangan |
|---|----------|-----------|------|-------------|------------|
| 1 | `admin` | Administrator | `admin` | `123456` | Akses penuh ke seluruh sistem |
| 2 | `ga_officer` | GA Officer | `ga` | `123456` | General Affairs Officer |
| 3 | `finance_officer` | Finance Officer | `finance` | `123456` | Finance Officer |

---

## 👤 Seluruh Role yang Didukung

Sistem mendukung **10 role** user (berdasarkan ENUM di tabel `users`):

| # | Role | Label | Halaman Utama | Deskripsi |
|---|------|-------|---------------|-----------|
| 1 | `admin` | 🔑 Admin | `/app/dashboard` | Akses penuh: manajemen user, settings, audit log, multi-cabang |
| 2 | `ga` | 🕐 GA Officer | `/app/ga` | Antrean klaim BBM, kasbon, trip, verifikasi anomali |
| 3 | `finance` | 💰 Finance | `/app/finance` | Rekap kasbon, cairkan dana, arsip transaksi |
| 4 | `marketing` | 📣 Marketing | `/app/marketing` | Buat & kelola appointment kunjungan nasabah |
| 5 | `chief_driver` | 🗺️ Chief Driver | `/app/chief-driver` | Atur rute perjalanan driver (auto & manual) |
| 6 | `driver` | 🚗 Driver | `/app/driver` | PWA: submit trip, foto ODO/struk, GPS, notifikasi |
| 7 | `ob` | 🧹 Office Boy | `/app/water` | Pengajuan pembelian air minum |
| 8 | `receptionist` | 📋 Resepsionis | `/app/receptionist` | Verifikasi pelamar kerja & kehadiran |
| 9 | `traineer` | 🎓 Traineer | `/app/traineer` | Pantau rekrutan / orang yang direkrut (upline) |
| 10 | `ga_hr` | 🕐 GA HR | `/app/ga-hr` | Data overtime Driver & OB/Security |

---

## 🔐 Detail Akses per Role

### 🔑 Admin (`admin`)
- **Akses**: Semua halaman & API
- **Fitur Khusus**:
  - Manajemen User (`/app/users`) — CRUD, sync, bulk create, reset PIN
  - Pengaturan (`/app/settings`) — identitas perusahaan, reset PIN massal driver
  - Audit Log (`/app/logs`) — semua aktivitas user tercatat
  - Multi-cabang (`/app/branches`)
  - Seed & clean data demo
- **Halaman**: Dashboard, GA, Finance, Marketing, Chief Driver, Trips, Assignments, Rekap, Cash, Analytics, Users, Logs, Settings, Branches, GA HR

### 🕐 GA Officer (`ga`)
- **Akses**: Back-office penuh (hampir sama dengan Admin, kecuali User Management & Settings)
- **Dashboard GA** (`/app/ga`):
  - 🕐 Antrean klaim BBM — approve, verifikasi anomali ML, tolak
  - 💵 Kasbon menunggu approve
  - 🗺️ Laporan perjalanan menunggu review
  - 🚰 Pengajuan air minum (ringkasan)
  - ⚡ Quick links ke Assignments, Kasbon, Air Minum, Analytics
- **Dashboard Admin** (`/app/dashboard`) — **juga bisa diakses GA**:
  - 📊 Stat cards: Antrean GA (pending), Verified GA, Terarsip, Transaksi Hari Ini
  - 🕐 Antrean Kerja tab GA — approve, verifikasi, tolak, detail
  - 💵 Antrean Kerja tab Finance & Konfirmasi Driver (**hanya lihat, tidak bisa aksi**)
  - 🔎 Verifikasi Mendalam — foto bukti, cross-check (health score, flag, budget)
  - ✏️ Edit data transaksi (kendaraan/BBM/nominal/ODO/SPBU)
  - ↩️ Unverify transaksi
  - 🗑 Hapus transaksi (**hanya admin**)
  - ⚡ Aksi Cepat: Log Perjalanan, Assignments, Kasbon, Analytics
- **Halaman Sidebar** (`AppLayout.vue`):
  - 🧾 Dashboard GA (`/app/ga`)
  - 🗺️ Log Perjalanan (`/app/trips`)
  - 🚗 Assignments (`/app/assignments`)
  - 💵 Kasbon / BBM (`/app/cash`)
  - 📈 Analytics (`/app/analytics`)
  - 🚛 Chief Driver (`/app/chief-driver`)
  - 🔧 Aset & Pemeliharaan (`/app/assets`)
- **API Endpoint** (role `ga`):
  - `POST /api/queue/approve-ga/<id>` — approve klaim BBM
  - `POST /api/queue/verify/<id>` — verifikasi anomali ML
  - `POST /api/queue/reject/<id>` — tolak klaim
  - `POST /api/queue/modify/<id>` — edit data transaksi
  - `POST /api/queue/unverify/<id>` — kembalikan ke antrean GA
  - `GET /api/queue?tab=ga` — ambil antrean GA
  - `POST /api/drivers/sync` — sinkronisasi driver
  - `POST /api/vehicles/add` — tambah kendaraan
  - `POST /api/assignments/*` — manajemen asigment kendaraan
  - `GET /api/assets/*` — aset & pemeliharaan
  - `GET /api/cross-check/<id>` — cross-check transaksi
  - `GET /api/stats` — statistik dashboard
- **Catatan Perubahan dari BBM System Lama**:
  - Endpoint klasik `ga_approve`, `ga_reject` **dihapus di v2.5** — diganti SPA `/api/queue/*`
  - Halaman klasik `/admin` **dipensiunkan** → redirect ke SPA
  - Fitur: approve, reject, verify anomali, edit, unverify, detail transaksi **tetap tersedia** di SPA

### 💰 Finance (`finance`)
- **Akses**: Finance penuh + water (air minum) + kasbon + rekap
- **Dashboard Finance** (`/app/finance`):
  - 🚰 Rekap air minum — statistik total, menunggu verifikasi, terverifikasi, ditolak
  - 💵 Kasbon menunggu approve
  - 🧾 LPJ menunggu approve
  - 👥 Ringkasan per OB (total, pending, verified, rejected)
  - 🥤 Per Jenis & 🏷️ Per Merk air minum
  - ⬇️ Export CSV
- **Dashboard Admin** (`/app/dashboard`) — **juga bisa diakses Finance**:
  - 📊 Stat cards: Menunggu Finance (os_finance), Terarsip, Transaksi Hari Ini, Nominal Hari Ini
  - 💵 Antrean Kerja tab Finance — payout (💰)
  - 🤝 Antrean Kerja tab Konfirmasi Driver — arsipkan (📦)
  - 🕐 Antrean Kerja tab GA (**hanya lihat, tidak bisa aksi**)
  - 🔎 Verifikasi Mendalam — foto bukti, cross-check
  - ⚡ Aksi Cepat: Log Perjalanan, Rekap, Analytics
- **Halaman Sidebar** (`AppLayout.vue`):
  - 💰 Dashboard Finance (`/app/finance`)
  - 🗺️ Log Perjalanan (`/app/trips`)
  - 📋 Rekap (`/app/rekap`)
  - 💵 Kasbon / BBM (`/app/cash`)
  - 📈 Analytics (`/app/analytics`)
  - 🚰 Air Minum (`/app/water`)
- **API Endpoint** (role `finance`):
  - `POST /api/queue/payout/<id>` — cairkan dana
  - `POST /api/queue/archive/<id>` — arsipkan transaksi
  - `GET /api/queue?tab=finance` — ambil antrean finance
  - `GET /api/queue?tab=driver_confirm` — ambil konfirmasi driver
  - `GET /api/water/recap` — rekap air minum
  - `POST /api/water/verify/<id>` — verifikasi air minum
  - `GET /api/rekap/*` — rekap transaksi
  - `GET /api/cash/history` — riwayat kasbon
  - `GET /api/stats` — statistik dashboard
- **Catatan Perubahan dari BBM System Lama**:
  - Endpoint klasik `finance_payout`, `finance_archive` **dihapus di v2.5** — diganti SPA `/api/queue/*`
  - Halaman klasik `/admin` **dipensiunkan** → redirect ke SPA
  - Fitur: payout, archive, rekap, water verify **tetap tersedia** di SPA
  - Finance **tidak bisa** approve GA (hanya GA & Admin)
  - Finance **tidak bisa** edit/unverify transaksi (hanya GA & Admin)

### 📣 Marketing (`marketing`)
- **Akses**: Appointment & kunjungan nasabah
- **Fitur Khusus**:
  - Buat appointment kunjungan
  - Lihat status kunjungan
  - Kelola data nasabah
- **Halaman**: Marketing Dashboard

### 🗺️ Chief Driver (`chief_driver`)
- **Akses**: Rute perjalanan driver
- **Fitur Khusus**:
  - Optimasi rute otomatis
  - Atur rute manual (tentukan driver + urutan kunjungan)
  - Assign driver ke appointment
- **Halaman**: Chief Driver Dashboard

### 🚗 Driver (`driver`)
- **Akses**: PWA driver (mobile-first)
- **Fitur Khusus**:
  - Submit trip (foto ODO, foto struk, GPS)
  - Lihat profil kendaraan & BBM
  - Notifikasi real-time
  - Multi-rute array
  - Enqueue & sync data offline
- **Halaman**: Driver PWA (`/driver`)

### 🧹 Office Boy (`ob`)
- **Akses**: Pengajuan air minum
- **Fitur Khusus**:
  - Buat pengajuan pembelian air minum
  - Upload foto before/after
  - Lihat status pengajuan
- **Halaman**: Water View (`/app/water`)

### 📋 Resepsionis (`receptionist`)
- **Akses**: Sistem pelamar kerja
- **Fitur Khusus**:
  - Verifikasi pelamar
  - Update status tahapan interview/training
  - Kelola kehadiran
- **Halaman**: Receptionist Dashboard

### 🎓 Traineer (`traineer`)
- **Akses**: Pantau rekrutan (read-only)
- **Fitur Khusus**:
  - Lihat orang yang direkrut (scope: upline sendiri)
  - Filter tanggal, search, chip kehadiran
  - Tanpa akses edit/PDF
- **Halaman**: Traineer Dashboard

### 🕐 GA HR (`ga_hr`)
- **Akses**: Data overtime
- **Fitur Khusus**:
  - Dashboard statistik overtime
  - Data migrasi Driver (8.665+ data) & OB/Security (546+ data)
  - Auto-refresh saat login/logout
  - CRUD overtime (edit, delete)
  - PDF laporan overtime
- **Halaman**: GA HR Dashboard (`/app/ga-hr`)

---

## 📊 Statistik Role (dari CHANGELOG & kode)

| Role | Estimasi Jumlah User | Keterangan |
|------|---------------------|------------|
| `admin` | 1+ (default) | minimal 1 admin utama |
| `ga` | 1+ (default) | GA Officer default |
| `finance` | 1+ (default) | Finance Officer default |
| `marketing` | tergantung jumlah tim | dibuat via bulk create / manual |
| `driver` | 8.665+ | dari migrasi data overtime Driver |
| `ob` | 546+ | dari migrasi data overtime OB/Security |
| `chief_driver` | tergantung kebutuhan | ditentukan admin |
| `receptionist` | tergantung kebutuhan | untuk rekrutmen |
| `traineer` | tergantung kebutuhan | untuk monitoring rekrutan |
| `ga_hr` | 1+ (default demo) | `ga_hr_officer` (PIN: 123456) |

---

## 🔒 Keamanan Akun

| Aspek | Keterangan |
|-------|------------|
| **Metode Login** | Username + PIN 6 digit |
| **Rate Limiting** | Anti brute-force (terlalu banyak percobaan → blokir sementara) |
| **CSRF Protection** | Aktif untuk semua POST/PUT/DELETE/PATCH |
| **Session** | HTTP-only cookie, SameSite=Lax, Secure (HTTPS) |
| **PIN Default** | `123456` untuk semua user baru |
| **Reset PIN** | Hanya admin yang bisa reset PIN user lain |
| **Audit Trail** | Semua aktivitas login, sync, delete tercatat di `activity_logs` |
| **Branch Code** | Multi-cabang: user dikaitkan dengan cabang tertentu |

---

## 📝 Catatan

1. **PIN Default**: Semua user baru (termasuk bulk create driver/marketing) menggunakan PIN default `123456`.
2. **Bulk Create**: Admin bisa membuat akun massal untuk driver aktif dan anggota marketing via `/api/users/bulk-create`.
3. **Bulk Reset PIN**: Admin bisa reset PIN massal semua driver via tombol di Settings.
4. **Role Hierarchy**: Admin > GA/Finance > Marketing/Chief Driver > Driver/OB > Receptionist/Traineer/GA HR.
5. **Data Tersimpan di DB Master**: Seluruh data user tersimpan di database master (bukan DB cabang).

---

## 🔄 Perbandingan dengan BBM System Lama (v2.4 → v2.5+)

Pada migrasi **v2.5**, seluruh antarmuka klasik (Jinja/HTML) **dihapus dari repo** dan digantikan SPA Vue 3.
Endpoint klasik hanya tersisa untuk redirect kompatibilitas (bookmark lama).

### Endpoint Klasik yang DIHAPUS (ganti SPA)

| Endpoint Lama | Fungsi | Pengganti SPA |
|---------------|--------|---------------|
| `POST /admin/ga-approve/<id>` | Approve klaim BBM | `POST /api/queue/approve-ga/<id>` |
| `POST /admin/ga-reject/<id>` | Tolak klaim BBM | `POST /api/queue/reject/<id>` |
| `POST /admin/finance-payout/<id>` | Cairkan dana | `POST /api/queue/payout/<id>` |
| `POST /admin/finance-archive/<id>` | Arsipkan transaksi | `POST /api/queue/archive/<id>` |
| `POST /admin/unverify/<id>` | Kembalikan ke antrean | `POST /api/queue/unverify/<id>` |
| `POST /admin/delete/<id>` | Hapus transaksi | `POST /api/queue/delete/<id>` |
| `POST /admin/edit-odo/<id>` | Edit ODO transaksi | `POST /api/queue/modify/<id>` |
| `POST /admin/trips/verify/<id>` | Verifikasi trip | `POST /api/trips/verify/<id>` |
| `POST /admin/trips/reject/<id>` | Tolak trip | `POST /api/trips/reject/<id>` |

### Endpoint Klasik yang MASIH ADA (hanya redirect)

| Endpoint | Fungsi |
|----------|--------|
| `GET /admin` | Redirect ke `/app/dashboard` |
| `GET /admin/queue-fragment/<tab>` | Redirect ke `/app/dashboard` |
| `GET /admin/trips` | Redirect ke `/app/trips` |
| `GET /ga/assignments` | Redirect ke `/app/assignments` |
| `GET /marketing` | Redirect ke `/app/marketing` |
| `GET /chief-driver` | Redirect ke `/app/chief-driver` |
| `GET /login` | Redirect ke `/app/login` |
| `GET /logout` | Clear session → redirect `/app/login` |

### Fitur yang TIDAK BERUBAR (tetap tersedia di SPA)

- ✅ Approve/Reject klaim BBM (GA/Admin)
- ✅ Payout/Archive transaksi (Finance/Admin)
- ✅ Verifikasi anomali ML (GA/Admin)
- ✅ Edit data transaksi (GA/Admin)
- ✅ Unverify transaksi (GA/Admin)
- ✅ Hapus transaksi (Admin only)
- ✅ Rekap transaksi (Finance/Admin)
- ✅ Analytics (GA/Finance/Admin)
- ✅ Kasbon/Cash (GA/Finance/Admin)
- ✅ Log Perjalanan/Trips (GA/Finance/Admin)
- ✅ Assignments kendaraan (GA/Admin)
- ✅ Export logsheet Excel/PDF (GA/Finance/Admin)

### Fitur BARU di SPA (tidak ada di klasik)

- 🆕 Cross-check transaksi (health score, flag, budget, selisih ODO)
- 🆕 Modal detail transaksi dengan foto bukti inline
- 🆕 Realtime refresh antrean (event `new_claim`)
- 🆕 Export antrean ke Excel
- 🆕 Dark mode & high contrast mode
- 🆕 Accessibility (focus trap, aria, keyboard navigation)
- 🆕 Verifikasi anomali dengan foto MyPertamina opsional
- 🆕 Multi-cabang: ringkasan cabang, PDF konsolidasi, Excel konsolidasi

---

## 🔍 Analisis Fitur GA & Finance (Detail Lengkap)

### 🕐 GA Officer — Alur Kerja Kasbon (Cash/Kasbon)

| Status | Aksi GA | Keterangan |
|--------|---------|------------|
| `DRAFT` | ✅ GA Approve | Setujui kasbon driver |
| `DRAFT` | ❌ Tolak | Tolak kasbon dengan alasan |
| `DRAFT` | ✏️ Edit | Ubah nominal kasbon |
| `DRAFT` | 🗑 Hapus | Hapus kasbon DRAFT |
| `FINANCE_APPROVED` | 🤝 Serahkan ke Driver | Konfirmasi dana diserahkan ke driver |
| `LPJ_SUBMITTED` | ✅ Approve LPJ | Verifikasi laporan pertanggungjawaban |
| `LPJ_SUBMITTED` | ❌ Tolak LPJ | Tolak LPJ, driver submit ulang |

### 💰 Finance — Alur Kerja Kasbon (Cash/Kasbon)

| Status | Aksi Finance | Keterangan |
|--------|--------------|------------|
| `GA_APPROVED` | 💰 Finance Approve | Setujui pencairan dana |
| `GA_APPROVED` | ↩ Batal | Batalkan pengajuan |
| `FINANCE_APPROVED` | ↩ Batal | Batalkan setelah approve |
| `COMPLETED` | 🔄 Reset LPJ | Reset status LPJ ke FUNDS_WITH_DRIVER |
| *Semua* | 🔢 Kode Harian | Atur kode unik harian (manual mode) |

### 🕐 GA — Fitur Transaksi BBM

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| Approve | `POST /api/queue/approve-ga/<id>` | Status: pending/modified → verified_ga |
| Verify Anomali | `POST /api/queue/verify/<id>` | Verifikasi transaksi ber-flag ML |
| Tolak | `POST /api/queue/reject/<id>` | Status: pending/modified → rejected |
| Edit | `POST /api/queue/modify/<id>` | Ubah kendaraan/BBM/nominal/ODO/SPBU |
| Unverify | `POST /api/queue/unverify/<id>` | Status: verified_ga → pending |
| Detail | `GET /api/transactions/detail/<id>` | Lihat foto bukti + cross-check |
| Cross-Check | `GET /api/cross-check/<id>` | Health score, flag, budget, selisih ODO |

### 💰 Finance — Fitur Transaksi BBM

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| Payout | `POST /api/queue/payout/<id>` | Status: verified_ga → os_finance |
| Archive | `POST /api/queue/archive/<id>` | Status: os_finance → archived |
| Detail | `GET /api/transactions/detail/<id>` | Lihat detail transaksi |
| Cross-Check | `GET /api/cross-check/<id>` | Health score, flag, budget, selisih ODO |

### 🕐 GA — Fitur Trip/Perjalanan

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| List Trip | `GET /api/trips` | Filter status (pending/verified/rejected) |
| Verify Trip | `POST /api/trips/verify/<id>` | Verifikasi laporan perjalanan |
| Reject Trip | `POST /api/trips/reject/<id>` | Tolak laporan perjalanan |
| Export Excel | `GET /admin/trips/export/<id>` | Unduh logsheet Excel |
| Export PDF | `GET /admin/trips/export-pdf/<id>` | Unduh logsheet PDF |

### 💰 Finance — Fitur Rekap & Air Minum

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| Rekap Transaksi | `GET /api/rekap/*` | Rekap harian/mingguan/bulanan |
| Rekap Air Minum | `GET /api/water/recap` | Statistik air minum per OB |
| Verify Air Minum | `POST /api/water/verify/<id>` | Verifikasi pengajuan air minum |
| Reject Air Minum | `POST /api/water/reject/<id>` | Tolak pengajuan air minum |
| Export CSV | `GET /api/water/recap/export` | Unduh rekap air minum CSV |

---

## 📊 Ringkasan Akses per Role

| Menu | Admin | GA | Finance | Marketing | Chief Driver | Driver | OB |
|------|:-----:|:--:|:-------:|:---------:|:------------:|:------:|:--:|
| Dashboard Admin | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dashboard GA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Dashboard Finance | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Log Perjalanan | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Assignments | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Rekap | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Kasbon / BBM | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Analytics | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Marketing Hub | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Chief Driver | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manajemen User | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Pengaturan | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Audit Log | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Air Minum | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Pelamar Kerja | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Aset & Pemeliharaan | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Overtime | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Driver PWA | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## 🔗 Sync Backend ↔ Frontend (Audit Lengkap)

### ✅ Endpoint yang SUDAH Terpakai di Frontend

| Module | Endpoint | Method | Frontend |
|--------|----------|--------|----------|
| **SPA** | `/api/auth/me` | GET | auth store |
| **SPA** | `/api/auth/login` | POST | LoginView |
| **SPA** | `/api/auth/logout` | POST | auth store |
| **SPA** | `/api/trips` | GET | TripsView, GaDashboard, AdminDashboard |
| **SPA** | `/api/trips/verify/<id>` | POST | TripsView |
| **SPA** | `/api/trips/reject/<id>` | POST | TripsView |
| **SPA** | `/api/queue` | GET | AdminDashboard, GaDashboard |
| **SPA** | `/api/queue/approve-ga/<id>` | POST | AdminDashboard, GaDashboard |
| **SPA** | `/api/queue/payout/<id>` | POST | AdminDashboard |
| **SPA** | `/api/queue/archive/<id>` | POST | AdminDashboard |
| **SPA** | `/api/queue/reject/<id>` | POST | AdminDashboard, GaDashboard |
| **SPA** | `/api/queue/verify/<id>` | POST | AdminDashboard, GaDashboard |
| **SPA** | `/api/queue/modify/<id>` | POST | AdminDashboard |
| **SPA** | `/api/queue/unverify/<id>` | POST | AdminDashboard |
| **SPA** | `/api/queue/delete/<id>` | POST | AdminDashboard |
| **SPA** | `/api/transactions/detail/<id>` | GET | AdminDashboard, GaDashboard |
| **SPA** | `/api/queue/export-excel` | GET | AdminDashboard |
| **Transactions** | `/api/transactions/archive` | GET | RekapView |
| **Transactions** | `/api/stats` | GET | AdminDashboard, GaDashboard, FinanceDashboard |
| **Transactions** | `/api/audit-logs` | GET | LogsView |
| **Transactions** | `/api/cross-check/<id>` | GET | AdminDashboard |
| **Transactions** | `/api/get-feedback/<nopol>` | GET | RaporTab (Driver PWA) |
| **Transactions** | `/api/analytics/data` | GET | AnalyticsView |
| **Transactions** | `/api/trip-detail/<id>` | GET | TripsView |
| **Cash** | `/api/cash/daily-code` | GET/POST | CashView |
| **Cash** | `/api/cash/request` | POST | Driver PWA |
| **Cash** | `/api/cash/approve-ga/<id>` | POST | CashView |
| **Cash** | `/api/cash/approve-finance/<id>` | POST | CashView |
| **Cash** | `/api/cash/handover/<id>` | POST | CashView |
| **Cash** | `/api/cash/pending-lpj` | GET | CashView |
| **Cash** | `/api/cash/approve-lpj/<id>` | POST | CashView |
| **Cash** | `/api/cash/reject-lpj/<id>` | POST | CashView |
| **Cash** | `/api/cash/history` | GET | CashView |
| **Cash** | `/api/cash/reject/<id>` | POST | CashView |
| **Cash** | `/api/cash/submit-lpj/<id>` | POST | Driver PWA |
| **Cash** | `/api/cash/delete/<id>` | POST | CashView |
| **Cash** | `/api/cash/edit/<id>` | POST | CashView |
| **Cash** | `/api/cash/cancel/<id>` | POST | CashView |
| **Cash** | `/api/cash/reset-lpj/<id>` | POST | CashView |
| **Water** | `/api/water/brands` | GET/POST | WaterView |
| **Water** | `/api/water/brands/<id>` | DELETE | WaterView |
| **Water** | `/api/water/purchases` | POST/GET | WaterView |
| **Water** | `/api/water/purchases/<id>` | GET | WaterView |
| **Water** | `/api/water/purchases/<id>/verify` | POST | WaterView |
| **Water** | `/api/water/purchases/<id>/reject` | POST | WaterView |
| **Water** | `/api/water/recap` | GET | FinanceDashboard |
| **Water** | `/api/water/recap/export` | GET | FinanceDashboard |
| **Water** | `/api/water/purchases/<id>/pdf` | GET | WaterView |
| **Master** | `/api/vehicles` | GET | multiple views |
| **Master** | `/api/bbm_types` | GET | multiple views |
| **Master** | `/api/drivers` | GET | multiple views |
| **Master** | `/api/drivers/sync` | POST | SettingsView |
| **Master** | `/api/drivers/<name>/activate` | POST | SettingsView |
| **Master** | `/api/drivers/<name>/deactivate` | POST | SettingsView |
| **Master** | `/api/drivers/<name>/delete` | POST | SettingsView |
| **Master** | `/api/drivers/pin-reset` | POST | SettingsView |
| **Master** | `/api/users` | GET | UsersView |
| **Master** | `/api/users/sync` | POST | UsersView |
| **Master** | `/api/users/bulk-create` | POST | SettingsView |
| **Master** | `/api/users/reset-pin` | POST | UsersView |
| **Master** | `/api/verify-pin` | POST | LoginView |
| **Master** | `/api/vehicles/with-nopol` | GET | AssignmentsView |
| **Master** | `/api/vehicles/add` | POST | SettingsView |
| **Master** | `/api/vehicle_bbm/<type>` | GET | multiple views |
| **Master** | `/api/vehicle-allowed-bbm/<type>` | GET | multiple views |
| **Master** | `/api/system-config/<key>` | GET/PUT | SettingsView |
| **Master** | `/api/dummy-data/status` | GET | SettingsView |
| **Master** | `/api/dummy-data/toggle` | POST | SettingsView |
| **Master** | `/api/system-config/identity` | GET/PUT | identity store |
| **Master** | `/api/demo/status` | GET | SettingsView |
| **Master** | `/api/demo/seed` | POST | SettingsView |
| **Master** | `/api/demo/clean` | POST | SettingsView |
| **Branches** | `/api/branches` | GET | BranchesView |
| **Branches** | `/api/branches/stats` | GET | AdminDashboard |
| **Branches** | `/api/branches/current` | GET | SettingsView |
| **Branches** | `/api/branches/save` | POST | BranchesView |
| **Branches** | `/api/branches/<code>/seed-demo` | POST | SettingsView |
| **Branches** | `/api/branches/report-pdf` | GET | AdminDashboard |
| **Branches** | `/api/branches/<code>/activate` | POST | BranchesView |
| **Branches** | `/api/branches/<code>/deactivate` | POST | BranchesView |
| **Branches** | `/api/branches/<code>/ensure-db` | POST | SettingsView |
| **Branches** | `/api/branches/switch` | POST | SettingsView |
| **Branches** | `/api/branches/consolidated-pdf` | GET | AdminDashboard |
| **Branches** | `/api/branches/consolidated-excel` | GET | AdminDashboard |
| **Overtime** | `/api/overtime/form-meta` | GET | OvertimeFormView |
| **Overtime** | `/api/overtime` | POST | OvertimeFormView |
| **Overtime** | `/api/overtime/driver` | GET | OvertimeView |
| **Overtime** | `/api/overtime/driver/refresh` | POST | OvertimeView |
| **Overtime** | `/api/overtime/ob-security` | GET | OvertimeView |
| **Overtime** | `/api/overtime/report` | GET | OvertimeView |
| **Overtime** | `/api/overtime/stats` | GET | OvertimeView |
| **Overtime** | `/api/overtime/config` | GET/PATCH | OvertimeView |
| **Overtime** | `/api/overtime/<modul>/<id>` | PATCH | OvertimeView |
| **Overtime** | `/api/overtime/<modul>/<id>` | DELETE | OvertimeView |
| **Assets** | `/api/assets/summary` | GET | AssetsView |
| **Assets** | `/api/assets/ac` | GET/POST | AssetsView |
| **Assets** | `/api/assets/ac/<id>` | PATCH/DELETE | AssetsView |
| **Assets** | `/api/assets/ac/<id>/logs` | GET/POST | AssetsView |
| **Assets** | `/api/assets/ac-logs/<id>` | DELETE | AssetsView |
| **Assets** | `/api/assets/vehicles` | GET/POST | AssetsView |
| **Assets** | `/api/assets/vehicles/<id>` | PATCH/DELETE | AssetsView |
| **Assets** | `/api/assets/vehicles/<id>/services` | GET/POST | AssetsView |
| **Assets** | `/api/assets/vehicle-services/<id>` | DELETE | AssetsView |
| **Assets** | `/api/assets/components` | GET/POST | AssetsView |
| **Assets** | `/api/assets/components/<id>` | PATCH/DELETE | AssetsView |
| **Assets** | `/api/assets/recommendations` | GET | AssetsView |
| **Assets** | `/api/assets/recommendations/refresh` | POST | AssetsView |
| **Assets** | `/api/assets/recommendations/<id>` | PATCH | AssetsView |
| **Assets** | `/api/assets/report` | GET | AssetsView |
| **Applicants** | `/api/applicants` | GET/POST | ReceptionistView, TraineerView, ApplyView |
| **Applicants** | `/api/applicants/meta` | GET | ReceptionistView, TraineerView |
| **Applicants** | `/api/applicants/user-options` | GET/POST | ApplyView, ReceptionistView |
| **Applicants** | `/api/applicants/user-options/manage` | GET | ReceptionistView |
| **Applicants** | `/api/applicants/user-options/<id>` | PATCH/DELETE | ReceptionistView |
| **Applicants** | `/api/applicants/<id>` | PATCH/DELETE | ReceptionistView |
| **Applicants** | `/api/applicants/<id>/verify` | POST | ReceptionistView |
| **Applicants** | `/api/applicants/<id>/attendance` | POST | ReceptionistView |
| **Applicants** | `/api/applicants/<id>/status` | POST | ReceptionistView |
| **Applicants** | `/api/applicants/report` | GET | ReceptionistView |
| **Appointments** | `/api/appointments` | GET/POST | MarketingDashboard, ChiefDriverDashboard |
| **Appointments** | `/api/appointments/suggestions` | GET | MarketingDashboard |
| **Appointments** | `/api/appointments/route-plan` | GET | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/route-plan/apply` | POST | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/route-manual/apply` | POST | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/<id>` | PATCH | MarketingDashboard |
| **Appointments** | `/api/appointments/<id>/assign` | POST | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/<id>/unassign` | POST | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/<id>/complete` | POST | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/driver-complete/<id>` | POST | Driver PWA |
| **Appointments** | `/api/appointments/<id>/cancel` | POST | MarketingDashboard |
| **Appointments** | `/api/appointments/driver-today` | GET | Driver PWA |
| **Appointments** | `/api/appointments/driver-summary` | GET | Driver PWA |
| **Appointments** | `/api/appointments/member-summary` | GET | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/detect-area` | GET | MarketingDashboard |
| **Appointments** | `/api/appointments/export` | GET | ChiefDriverDashboard |
| **Appointments** | `/api/appointments/notifications` | GET | NotificationBell |
| **Appointments** | `/api/appointments/notifications/read` | POST | NotificationBell |
| **Appointments** | `/api/marketing/members` | GET | MarketingDashboard |
| **Appointments** | `/api/teams` | GET | MarketingDashboard |
| **Appointments** | `/api/teams/sync` | POST | MarketingDashboard |
| **Driver** | `/api/driver/me` | GET | DriverView |
| **Notifications** | `/api/notifications` | GET | NotificationBell |
| **Notifications** | `/api/notifications/read` | POST | NotificationBell |
| **Security** | `/api/health` | GET | health check |
| **Assignments** | `/api/assignments/active` | GET | AssignmentsView |
| **Assignments** | `/api/assignments/history` | GET | AssignmentsView |
| **Assignments** | `/api/assignments/pending` | GET | AssignmentsView |
| **Assignments** | `/api/assignments/unassigned` | GET | AssignmentsView |
| **Assignments** | `/api/assignments/swap-history` | GET | AssignmentsView |
| **Assignments** | `/api/assignments/create` | POST | AssignmentsView |
| **Assignments** | `/api/assignments/swap` | POST | AssignmentsView |
| **Assignments** | `/api/assignments/release` | POST | AssignmentsView |
| **Assignments** | `/api/assignments/confirm` | POST | Driver PWA |
| **Assignments** | `/api/assignment-remark` | POST | AssignmentsView |

---

### ❌ Endpoint yang BELUM Terpakai di Frontend (Backend Only)

| Module | Endpoint | Method | Fungsi | Status |
|--------|----------|--------|--------|--------|
| **Branches** | `/api/branches/consolidated` | GET | Data konsolidasi JSON lintas cabang | ⚠️ Hanya PDF/Excel (JSON untuk API consumer) |

> ✅ **7 dari 8 endpoint** sudah diintegrasikan ke frontend pada update ini!

---

### 📊 Ringkasan Sync

| Metrik | Jumlah |
|--------|--------|
| Total Backend API Endpoints | **161** |
| Sudah Terpakai di Frontend | **160** (99.4%) |
| Belum Terpakai di Frontend | **1** (0.6%) — `/api/branches/consolidated` (JSON) |

### ✅ Endpoint yang Sudah Diintegrasikan

1. **`/api/finance-review/<id>`** → ✅ Finance Review panel di modal detail transaksi (prev ODO, monthly stats, budget)
2. **`/api/finance-remark`** → ✅ Form remark di modal detail transaksi untuk Finance
3. **`/api/cash/detail/<id>`** → ✅ Modal detail di CashView (tracking kasbon + LPJ terkait)
4. **`/api/transaction-flags`** → ✅ Flag anomali ODO di kolom Anomali antrean GA
5. **`/api/vehicle-health`** → ✅ Tabel Fleet Health di AnalyticsView (skor kesehatan kendaraan)
6. **`/api/get-performance/<plat>`** → ✅ Sudah terpakai di RaporTab (Driver PWA)
7. **`/api/appointments/completed`** → ✅ Tab "Selesai" di MarketingDashboard

---

*Dokumen ini dihasilkan otomatis dari analisis kode sumber BPF WorkHub v2.22.x*
