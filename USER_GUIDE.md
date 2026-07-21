# 📖 Panduan Pengguna BPF Fleet & BBM System v1.1

**PT. Bestprofit Futures - Surabaya**

---

## Daftar Isi
1. [Akses Aplikasi](#1-akses-aplikasi)
2. [Panduan Driver (PWA)](#2-panduan-driver-pwa)
3. [Panduan GA (General Affairs)](#3-panduan-ga-general-affairs)
4. [Panduan Finance](#4-panduan-finance)
5. [Panduan Admin](#5-panduan-admin)
6. [FAQ](#6-faq)

---

## 1. Akses Aplikasi

### URL
| Pengguna | URL | Device |
|----------|-----|--------|
| Driver | `https://nasbpfsby.duckdns.org:5000/driver` | HP Android/iPhone |
| Admin/GA/Finance | `https://nasbpfsby.duckdns.org:5000/admin` | PC/Laptop |
| GA Assignments | `https://nasbpfsby.duckdns.org:5000/ga/assignments` | PC/Laptop |
| Analytics | `https://nasbpfsby.duckdns.org:5000/admin/analytics` | PC/Laptop |
| Settings | `https://nasbpfsby.duckdns.org:5000/admin/settings` | PC/Laptop |

### Default PIN
| Role | Username | PIN |
|------|----------|-----|
| Admin | `admin` | `123456` |
| GA Officer | `ga_officer` | `123456` |
| Finance Officer | `finance_officer` | `123456` |

### Install PWA di HP (Driver)
1. Buka Chrome di HP → akses URL Driver
2. Klik menu ⋮ → **"Add to Home Screen"**
3. Aplikasi terpasang seperti app native

---

## 2. Panduan Driver (PWA)

### 2.1 Tiga Tab Navigasi
- **⛽ BBM** — Form klaim BBM
- **🗺️ Trip** — Log perjalanan harian
- **📊 Rapor** — Cek performa kendaraan

### 2.2 Mengajukan Klaim BBM
1. Buka tab ⛽ BBM, tunggu GPS hijau ✅
2. **Pilih Nama Driver** dari dropdown
3. Nopol & Kendaraan terisi otomatis dari assignment GA
4. Pilih Jenis BBM → harga otomatis
5. Isi Nominal, Appointment, Odometer, SPBU
6. Upload 3 foto (📷 kamera atau 🖼️ galeri) → watermark otomatis
7. Klik **📤 Kirim Laporan BBM**

### 2.3 Log Perjalanan
1. Tab 🗺️ Trip → pilih driver → isi KM Awal, Jam
2. Klik **+ Tambah Rute** → isi atau klik 📍 GPS
3. Klik **📋 Kirim Log Perjalanan**

### 2.4 Mode Offline
- 🟡 Offline: data tersimpan lokal, auto-sync saat online

### 2.5 Cek Performa
- Tab 📊 Rapor → masukkan No. Polisi → Cek

---

## 3. Panduan GA (General Affairs)

### 3.1 Dashboard
Buka `/admin` — 4 tab: Antrean GA, Finance, Driver TTD, Arsip

### 3.2 Approve Klaim
1. Tab Antrean GA → klik **🔍 Approve**
2. Modal Cross-Check: Health Score, Flags, Budget
3. Klik **Lanjut Approve** → PIN → OK

### 3.3 Manajemen Kendaraan (GA Assignments)

Buka `/ga/assignments`

#### A. Assign Kendaraan Kosong
1. Pilih Kendaraan (nopol + tipe) dari dropdown
2. Pilih Driver dari dropdown
3. Klik **➕ Assign Kendaraan**

#### B. Tukar Kendaraan
1. Pilih Kendaraan (dropdown terisi dari assignment aktif)
2. Driver Saat Ini terisi otomatis
3. Pilih Driver Baru + Kategori Alasan + Alasan Lengkap
4. Klik **🔄 Tukar Kendaraan**

#### C. Lepas Kendaraan
1. Di tabel Assignment Aktif, klik **✕ Lepas**
2. Isi alasan → OK
3. Kendaraan kembali ke pool kosong

---

## 4. Panduan Finance

### 4.1 Finance Review
1. Tab Finance → klik **🔍 Review**
2. Split-screen: foto (kiri) + data (kanan)
3. Tambah remark → klik **💰 Keluarkan Dana** → PIN

### 4.2 Edit ODO
1. Klik ✏️ di samping ODO → isi ODO baru + alasan + PIN

### 4.3 Archive
1. Tab Driver TTD → pastikan TTD fisik
2. Klik **TTD & Arsip** → PIN → Download ZIP

---

## 5. Panduan Admin

### 5.1 Settings (PIN: 123456)

#### 👤 Driver Management
- **Tabel:** Driver | Status | Aksi
- **Tambah Driver:** Isi nama → klik + Tambah Driver
- **Nonaktifkan:** Klik toggle (tidak memengaruhi assignment)
- **Hapus:** Klik 🗑
- 💡 Assignment kendaraan dilakukan oleh GA

#### 🚗 Fleet Kendaraan
- **Tabel:** Nopol | Tipe | Brand | Kap | BBM | Driver | Aktif
- **Tambah Kendaraan:** Isi nopol, tipe → + Tambah Kendaraan
- Kolom Driver menampilkan driver aktif (read-only dari GA)

#### 👥 User Management
- **Tabel:** Username | Nama | Role | Status | Login | Aksi
- **Reset PIN:** Klik 🔑 PIN → isi PIN baru 6 digit → Simpan
- **Nonaktifkan/Hapus:** Toggle atau 🗑

#### 📊 Data Demo
- Klik Aktifkan/Nonaktifkan Data Demo

#### 📥 Import Excel
- Unduh Template → isi → Upload

#### ⛽ Multi-Fill Threshold
- Atur batas KM deteksi top-up (default: 40)

#### 📊 Batas Konsumsi
- Atur Good/Warning/Min/Max KM/L per kendaraan

#### 💾 Backup
- Klik Download Backup (.sql)

---

## 6. FAQ

**Q: Dropdown driver di PWA kosong?**
A: Pastikan driver sudah ditambahkan di Settings → Driver Management.

**Q: Nopol tidak muncul saat pilih driver?**
A: Driver belum di-assign kendaraan. GA harus assign dulu via GA Assignments.

**Q: Dropdown Tukar Kendaraan kosong?**
A: Belum ada assignment aktif. Assign kendaraan dulu via "Assign Kosong".

**Q: Beda Tukar dan Lepas?**
A: **Tukar** = ganti driver. **Lepas** = kendaraan kembali ke pool.

**Q: Nonaktifkan driver, kendaraannya gimana?**
A: Assignment tidak terpengaruh. GA yang mengatur pelepasan kendaraan.

**Q: Tambah kendaraan tanpa driver?**
A: Settings → Fleet Kendaraan → isi nopol + tipe → + Tambah.

---

## 📞 Kontak

**PT. Bestprofit Futures - Surabaya**  
BPF Fleet & BBM System v1.1  
Developed by **IT BPF Surabaya**
