# 📋 Daftar User & Role — BPF WorkHub v1.0

Dokumen ini menjelaskan semua role yang didukung sistem, siapa yang memakainya, dan apa yang bisa dilakukan masing-masing.

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

## 📋 Daftar Isi

1. [Akun Default (Seed Data)](#1-akun-default-seed-data)
2. [10 Role yang Didukung](#2-10-role-yang-didukung)
3. [Detail Akses per Role](#3-detail-akses-per-role)
4. [Ringkasan Akses](#4-ringkasan-akses)
5. [Keamanan Akun](#5-keamanan-akun)
6. [Catatan Penting](#6-catatan-penting)

---

## 1. Akun Default (Seed Data)

Akun berikut dibuat otomatis saat inisialisasi database:

| # | Username | Nama Lengkap | Role | PIN | Keterangan |
|---|----------|--------------|------|-----|------------|
| 1 | `admin` | Administrator | `admin` | `123456` | Akses penuh ke seluruh sistem |
| 2 | `ga_officer` | GA Officer | `ga` | `123456` | General Affairs Officer |
| 3 | `finance_officer` | Finance Officer | `finance` | `123456` | Finance Officer |

> ⚠️ **Segera ganti PIN bawaan** setelah login pertama kali.

---

## 2. 10 Role yang Didukung

Sistem mendukung 10 role pengguna:

| # | Role | Label | Halaman Utama | Keterangan |
|---|------|-------|---------------|------------|
| 1 | `admin` | 🔑 Admin | `/app/dashboard` | Akses penuh: manajemen user, settings, audit log, multi-cabang |
| 2 | `ga` | 🧾 GA Officer | `/app/ga` | Antrean klaim BBM, kasbon, trip, verifikasi anomali |
| 3 | `finance` | 💰 Finance | `/app/finance` | Rekap kasbon, cairkan dana, arsip transaksi |
| 4 | `marketing` | 📣 Marketing | `/app/marketing` | Buat & kelola appointment kunjungan nasabah |
| 5 | `chief_driver` | 🚛 Chief Driver | `/app/chief-driver` | Atur rute perjalanan driver (auto & manual) |
| 6 | `driver` | 🚗 Driver | `/app/driver` | PWA: submit trip, foto ODO/struk, GPS, notifikasi |
| 7 | `ob` | 🧹 OB | `/app/water` | Pengajuan pembelian air minum |
| 8 | `receptionist` | 🪪 Receptionist | `/app/receptionist` | Verifikasi pelamar kerja & kehadiran |
| 9 | `traineer` | 🎯 Traineer | `/app/traineer` | Pantau rekrutan (read-only) |
| 10 | `ga_hr` | ⏰ GA HR | `/app/ga-hr` | Data overtime Driver & OB/Security |

---

## 3. Detail Akses per Role

### 🔑 Admin (`admin`)

**Akses:** Semua halaman & API

**Fitur Khusus:**
- Manajemen User (`/app/users`) — CRUD, sync, bulk create, reset PIN
- Pengaturan (`/app/settings`) — identitas perusahaan, reset PIN massal driver
- Audit Log (`/app/logs`) — semua aktivitas user tercatat
- Multi-cabang (`/app/branches`)
- Seed & clean data demo

**Halaman Sidebar:**
- 📊 Dashboard Admin
- 🧾 Dashboard GA
- 💰 Dashboard Finance
- 🗺️ Log Perjalanan
- 🚗 Assignments
- 📋 Rekap
- 💵 Kasbon / BBM
- 📈 Analytics
- 🚛 Chief Driver
- 👥 Manajemen User
- ⚙️ Pengaturan
- 📝 Audit Log
- 🚰 Air Minum
- 🪪 Pelamar Kerja
- 🔧 Aset & Pemeliharaan
- ⏰ GA HR

---

### 🧾 GA Officer (`ga`)

**Akses:** Back-office penuh (hampir sama dengan Admin, kecuali User Management & Settings)

**Dashboard GA** (`/app/ga`):
- 🕐 Antrean klaim BBM — approve, verifikasi anomali ML, tolak
- 💵 Kasbon menunggu approve
- 🗺️ Laporan perjalanan menunggu review
- 🚰 Pengajuan air minum (ringkasan)
- ⚡ Quick links ke Assignments, Kasbon, Air Minum, Analytics

**Dashboard Admin** (`/app/dashboard`) — juga bisa diakses GA:
- 📊 Stat cards: Antrean GA (pending), Verified GA, Terarsip, Transaksi Hari Ini
- 🕐 Antrean Kerja tab GA — approve, verifikasi, tolak, detail
- 🔎 Verifikasi Mendalam — foto bukti, cross-check (health score, flag, budget)
- ✏️ Edit data transaksi (kendaraan/BBM/nominal/ODO/SPBU)
- ↩️ Unverify transaksi
- 🗑 Hapus transaksi (hanya admin)
- ⚡ Aksi Cepat: Log Perjalanan, Assignments, Kasbon, Analytics

**Halaman Sidebar:**
- 🧾 Dashboard GA
- 🗺️ Log Perjalanan
- 🚗 Assignments
- 💵 Kasbon / BBM
- 📈 Analytics
- 🚛 Chief Driver
- 🔧 Aset & Pemeliharaan

**API Endpoint:**
- `POST /api/queue/approve-ga/<id>` — approve klaim BBM
- `POST /api/queue/verify/<id>` — verifikasi anomali ML
- `POST /api/queue/reject/<id>` — tolak klaim
- `POST /api/queue/modify/<id>` — edit data transaksi
- `POST /api/queue/unverify/<id>` — kembalikan ke antrean GA
- `GET /api/queue?tab=ga` — ambil antrean GA
- `POST /api/drivers/sync` — sinkronisasi driver
- `POST /api/vehicles/add` — tambah kendaraan
- `POST /api/assignments/*` — manajemen assignment kendaraan
- `GET /api/assets/*` — aset & pemeliharaan
- `GET /api/cross-check/<id>` — cross-check transaksi
- `GET /api/stats` — statistik dashboard

---

### 💰 Finance (`finance`)

**Akses:** Finance penuh + water (air minum) + kasbon + rekap

**Dashboard Finance** (`/app/finance`):
- 🚰 Rekap air minum — statistik total, menunggu verifikasi, terverifikasi, ditolak
- 💵 Kasbon menunggu approve
- 🧾 LPJ menunggu approve
- 👥 Ringkasan per OB (total, pending, verified, rejected)
- 🥤 Per Jenis & 🏷️ Per Merk air minum
- ⬇️ Export CSV

**Dashboard Admin** (`/app/dashboard`) — juga bisa diakses Finance:
- 📊 Stat cards: Menunggu Finance (os_finance), Terarsip, Transaksi Hari Ini, Nominal Hari Ini
- 💵 Antrean Kerja tab Finance — payout (💰)
- 🤝 Antrean Kerja tab Konfirmasi Driver — arsipkan (📦)
- 🔎 Verifikasi Mendalam — foto bukti, cross-check
- ⚡ Aksi Cepat: Log Perjalanan, Rekap, Analytics

**Halaman Sidebar:**
- 💰 Dashboard Finance
- 🗺️ Log Perjalanan
- 📋 Rekap
- 💵 Kasbon / BBM
- 📈 Analytics
- 🚰 Air Minum

**API Endpoint:**
- `POST /api/queue/payout/<id>` — cairkan dana
- `POST /api/queue/archive/<id>` — arsipkan transaksi
- `GET /api/queue?tab=finance` — ambil antrean finance
- `GET /api/queue?tab=driver_confirm` — ambil konfirmasi driver
- `GET /api/water/recap` — rekap air minum
- `POST /api/water/verify/<id>` — verifikasi air minum
- `GET /api/rekap/*` — rekap transaksi
- `GET /api/cash/history` — riwayat kasbon
- `GET /api/stats` — statistik dashboard

---

### 📣 Marketing (`marketing`)

**Akses:** Appointment & kunjungan nasabah

**Fitur Khusus:**
- Buat appointment kunjungan
- Lihat status kunjungan
- Kelola data nasabah

**Halaman:** Marketing Hub (`/app/marketing`)

---

### 🚛 Chief Driver (`chief_driver`)

**Akses:** Rute perjalanan driver

**Fitur Khusus:**
- Optimasi rute otomatis
- Atur rute manual (tentukan driver + urutan kunjungan)
- Assign driver ke appointment

**Halaman:** Chief Driver Dashboard (`/app/chief-driver`)

---

### 🚗 Driver (`driver`)

**Akses:** PWA driver (mobile-first)

**Fitur Khusus:**
- Submit trip (foto ODO, foto struk, GPS)
- Lihat profil kendaraan & BBM
- Notifikasi real-time
- Multi-rute array
- Enqueue & sync data offline

**Halaman:** Driver PWA (`/app/driver`)

**Tab:**
- ⛽ BBM — klaim pembelian BBM
- 💰 Kasbon — ajukan uang muka
- 🗺️ Trip — log perjalanan
- 📊 Rapor — performa kendaraan

---

### 🧹 OB (`ob`)

**Akses:** Pengajuan air minum

**Fitur Khusus:**
- Buat pengajuan pembelian air minum
- Upload foto before/after
- Lihat status pengajuan

**Halaman:** Air Minum (`/app/water`)

---

### 🪪 Receptionist (`receptionist`)

**Akses:** Sistem pelamar kerja

**Fitur Khusus:**
- Verifikasi pelamar
- Update status tahapan interview/training
- Kelola kehadiran
- Kelola dropdown User

**Halaman:** Receptionist Dashboard (`/app/receptionist`)

---

### 🎯 Traineer (`traineer`)

**Akses:** Pantau rekrutan (read-only)

**Fitur Khusus:**
- Lihat orang yang direkrut (scope: upline sendiri)
- Filter tanggal, search, chip kehadiran
- Tanpa akses edit/PDF

**Halaman:** Traineer Dashboard (`/app/traineer`)

---

### ⏰ GA HR (`ga_hr`)

**Akses:** Data overtime

**Fitur Khusus:**
- Dashboard statistik overtime
- Data migrasi Driver (8.665+ data) & OB/Security (546+ data)
- Auto-refresh saat login/logout
- CRUD overtime (edit, delete)
- PDF laporan overtime

**Halaman:** GA HR Dashboard (`/app/ga-hr`)

---

## 4. Ringkasan Akses

| Menu | Admin | GA | Finance | Marketing | Chief Driver | Driver | OB |
|------|:-----:|:--:|:-------:|:---------:|:------------:|:------:|:--:|
| Dashboard Admin | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dashboard GA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Dashboard Finance | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Log Perjalanan | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Assignments | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Rekap | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Kasbon / BBM | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Analytics | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Marketing Hub | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Chief Driver | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manajemen User | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Pengaturan | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Audit Log | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Air Minum | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Pelamar Kerja | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Aset & Pemeliharaan | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| GA HR (Overtime) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 5. Keamanan Akun

| Aspek | Keterangan |
|-------|------------|
| Metode Login | Username + PIN 6 digit |
| Rate Limiting | Anti brute-force (terlalu banyak percobaan → blokir sementara) |
| CSRF Protection | Aktif untuk semua POST/PUT/DELETE/PATCH |
| Session | HTTP-only cookie, SameSite=Lax, Secure (HTTPS) |
| PIN Default | `123456` untuk semua user baru |
| Reset PIN | Hanya admin yang bisa reset PIN user lain |
| Audit Trail | Semua aktivitas login, sync, delete tercatat di `activity_logs` |
| Branch Code | Multi-cabang: user dikaitkan dengan cabang tertentu |

---

## 6. Catatan Penting

1. **PIN Default**: Semua user baru (termasuk bulk create driver/marketing) menggunakan PIN default `123456`.
2. **Bulk Create**: Admin bisa membuat akun massal untuk driver aktif dan anggota marketing via `/api/users/bulk-create`.
3. **Bulk Reset PIN**: Admin bisa reset PIN massal semua driver via tombol di Settings.
4. **Role Hierarchy**: Admin > GA/Finance > Marketing/Chief Driver > Driver/OB > Receptionist/Traineer/GA HR.
5. **Data Tersimpan di DB Master**: Seluruh data user tersimpan di database master (bukan DB cabang).

---

## 🔄 Endpoint Klasik yang Dipensiunkan (v2.5)

Pada migrasi v2.5, seluruh antarmuka klasik (Jinja/HTML) dihapus dari repo dan digantikan SPA Vue 3. Endpoint klasik hanya tersisa untuk redirect kompatibilitas.

### Endpoint yang MASIH ADA (hanya redirect)

| Endpoint | Fungsi |
|----------|--------|
| `GET /admin` | Redirect ke `/app/dashboard` |
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

## 📞 Kontak

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

*BPF WorkHub v1.0 · Daftar User & Role*
