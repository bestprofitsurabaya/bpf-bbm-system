# 📋 Changelog — BPF WorkHub v1.0

Riwayat perubahan penting pada BPF WorkHub. Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/ID/1.0.0/) dan versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

## 📋 Daftar Isi

- [Versi Terbaru](#versi-terbaru)
- [Riwayat Lengkap](#riwayat-lengkap)

---

## Versi Terbaru

### [1.0.0] - 2026-08-20

Versi stabil pertama dengan fitur lengkap: 10 role, 243 pytest, 82 Vitest, 10 video walkthrough.

**Fitur Utama:**
- Klaim BBM, kasbon, log perjalanan
- Sistem appointment dengan rute otomatis
- Pembelian air minum dengan verifikasi Finance
- Sistem pelamar kerja (form → Receptionist → Traineer)
- Aset & pemeliharaan (AC + kendaraan)
- Overtime Driver & OB/Security
- Multi-cabang dengan isolasi data
- PWA offline-first untuk driver
- Notifikasi real-time via WebSocket
- Backup DB otomatis

**Keamanan:**
- Login PIN + session-based
- CSRF protection
- Role-based access (10 role)
- Audit trail lengkap
- Security headers (CSP, X-Frame-Options, dll)

**Testing:**
- 243 pytest (backend)
- 82 Vitest (frontend)
- Browser verification via Puppeteer
- CI/CD via GitHub Actions

---

## Riwayat Lengkap

### v2.22.2 (2026-08-20)
- **Integrasi Backend → Frontend**: Finance Review, Finance Remark, Transaction Flags, Fleet Health, Cash Detail, Completed Appointments
- **User List**: dokumentasi lengkap 10 role + audit sync backend ↔ frontend (160/161 endpoint terpakai, 99.4%)

### v2.22.1 (2026-08-18)
- **Migrasi Overtime Driver**: 8.665 baris dari Google Sheet via Apps Script Web App
- **Solusi sheet PRIVATE**: tanpa akses pemilik, cukup akun yang punya akses view
- **Parser ISO UTC → WIB**: konversi otomatis +7 jam
- **Auto-refresh saat login/logout**: debounce 30 detik anti-spam
- **Notifikasi data overtime baru**: bell 🔔 realtime
- **Edit & hapus data overtime**: modal edit + konfirmasi hapus
- **Testing**: 243 pytest + 82 Vitest

### v2.22.0 (2026-08-14)
- **Role baru GA HR** dengan halaman sendiri `/app/ga-hr`
- **Overtime Driver**: sinkronisasi Google Sheet, URL sumber data bisa diatur
- **Overtime OB/Security**: 546 baris dimigrasikan + form publik tanpa login
- **Keamanan**: endpoint khusus role ga_hr & admin, rate-limit form publik
- **PDF Overtime**: laporan resmi berlogo BPF + TTD GA HR

### v2.21.0 (2026-08-13)
- **Security headers lengkap**: CSP ketat, X-Frame-Options, Referrer-Policy
- **Rate limit terpusat**: anti brute-force login
- **Backup DB otomatis**: mysqldump semua database tiap 03:00 WIB
- **Laporan konsolidasi lintas cabang**: PDF + Excel dari semua DB cabang
- **UI/UX**: LoadingState, EmptyState, ErrorState, pagination, export Excel

### v2.20.x (2026-08-13)
- **Multi-cabang**: setiap cabang punya database sendiri (isolasi data penuh)
- **Ringkasan cabang di dashboard Admin**
- **Audit log bertanda cabang**
- **Filter cabang di Audit Log**
- **PDF ringkasan per cabang**

### v2.19.x (2026-08-13)
- **Nama akun driver dirapikan**: username huruf kecil
- **Data demo dikelola Admin**: buat & bersihkan dari Settings
- **Identitas perusahaan dinamis**: bisa diubah Admin
- **PDF generator compact**: palet monokrom, resmi
- **Debugging menyeluruh**: tab driver, notifikasi, error server

### v2.18.0 (2026-08-13)
- **Aset & Pemeliharaan**: migrasi dari Streamlit ke WorkHub
- **15 unit AC** + **8 kendaraan** + **12 komponen**
- **Health score otomatis 0–100**
- **Rekomendasi maintenance berbasis aturan**
- **PDF resmi berlogo BPF**

### v2.17.0 (2026-08-13)
- **Migrasi data Google Sheet**: 914 riwayat pelamar
- **Dropdown User diatur Receptionist**: kelola opsi form pelamar

### v2.16.x (2026-08-13)
- **Ganti nama aplikasi**: dari "BPF Fleet & BBM System" → **BPF WorkHub**
- **Sistem Pelamar Kerja**: form publik → Receptionist → Traineer
- **Laporan PDF resmi per tahap**

### v2.15.x (2026-08-13)
- **Rute canggih**: jam kunjungan, geocoding, optimasi rute otomatis
- **Estimasi penghematan BBM**: angka persentase efisiensi
- **Backfill koordinat data lama**

### v2.14.x (2026-08-12)
- **Gladi resik otomatis**: 20/20 cek per peran
- **Video walkthrough**: 8 mp4 + walkthrough-all
- **Fix kritis**: koneksi DB bocor + font self-host

### v2.13.0 (2026-08-12)
- **Paket presentasi lengkap**: PPTX editabel, PDF, slide deck interaktif
- **Data demo**: 70 transaksi riwayat

### v2.12.x (2026-08-12)
- **Chrome host berfungsi**: verifikasi UI via Puppeteer
- **Slide deck interaktif**: 12 slide dengan navigasi keyboard

### v2.11.0 (2026-08-12)
- **Aksesibilitas**: dialog, kontras, keyboard navigation
- **Mode Kontras Tinggi 🔆**

### v2.10.0 (2026-08-12)
- **SPA Vue 3**: migrasi penuh dari server-rendered
- **Dashboard per role**: Admin, GA, Finance, Marketing, Chief Driver

### v2.0.0 (2026-08-11)
- **SPA Vue 3 + Vite**: antarmuka baru
- **Auth JSON**: `/api/auth/me`, `/api/auth/login`, `/api/auth/logout`
- **Kontrol akses berlapis**: server + SPA + sidebar

### v1.2.0 (2026-08-10)
- **Sistem Appointment**: Marketing → Chief Driver → Driver
- **Integrasi Log Perjalanan**: appointment → trip otomatis
- **Login redirect per-role**

### v1.1.0 (2026-08-09)
- **Autentikasi PIN**: login/logout session-based
- **CSRF protection**: token di semua form
- **Notifikasi driver real-time**: WebSocket per-driver room
- **Dark mode**: toggle 🌙/☀️ di semua halaman

### v1.0.0 (2026-08-08)
- **Rilis pertama**: sistem BBM, kasbon, log perjalanan
- **Driver PWA**: submit BBM, kasbon, trip
- **GA/Finance**: verifikasi & pencairan
- **Admin**: manajemen user, settings, audit log

---

## 📊 Statistik Pengujian

| Versi | Pytest | Vitest | Browser | Total |
|-------|--------|--------|---------|-------|
| v1.0.0 | 29 | — | — | 29 |
| v1.1.0 | 48 | 12 | — | 60 |
| v1.2.0 | 66 | 29 | — | 95 |
| v2.0.0 | 77 | 39 | — | 116 |
| v2.10.0 | 87 | 47 | — | 134 |
| v2.15.0 | 131 | 67 | 8 | 206 |
| v2.18.0 | 160 | 82 | 8 | 250 |
| v2.20.0 | 194 | 82 | 16 | 292 |
| v2.22.0 | 243 | 82 | 16 | 341 |
| **v1.0.0 (final)** | **243** | **82** | **16** | **341** |

---

## 📞 Kontak

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

*BPF WorkHub v1.0 · Changelog*
