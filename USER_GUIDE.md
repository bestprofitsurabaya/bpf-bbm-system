# 📖 Panduan Pengguna BPF BBM System v1.0

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
1. Buka Chrome di HP
2. Akses URL Driver
3. Klik menu ⋮ (pojok kanan atas)
4. Pilih **"Add to Home Screen"**
5. Aplikasi terpasang seperti app native
6. Buka dari icon di homescreen

---

## 2. Panduan Driver (PWA)

### 2.1 Tiga Tab Navigasi
- **⛽ BBM** — Form klaim BBM
- **🗺️ Trip** — Log perjalanan harian
- **📊 Rapor** — Cek performa kendaraan

### 2.2 Mengajukan Klaim BBM (Step-by-Step)

1. **Buka aplikasi** → tab ⛽ BBM
2. **Tunggu GPS** sampai kotak hijau: ✅ Lokasi Terdeteksi
3. **Pilih Nama Driver** dari dropdown:
   - Nopol & Kendaraan terisi otomatis
   - Pilih jenis BBM (PERTALITE/PERTAMAX) → harga otomatis
4. **Isi data transaksi:**
   - Nominal (Rp) → Volume (L) terhitung otomatis
   - Jumlah Appointment
   - Odometer (KM) — lihat di dashboard mobil
   - SPBU: Rekanan / Non-Rekanan
5. **Upload 3 Foto:**
   - Foto ODO (speedometer)
   - Foto ODO + Struk (bersebelahan)
   - Foto Struk (close-up)
   - Jika SPBU Non-Rekanan: + Foto Dispenser
   - Klik 📷 untuk kamera, 🖼️ untuk galeri
   - **Watermark otomatis** ditambahkan (GPS + Waktu + Perusahaan)
   - Lihat badge ✅ Watermarked
6. **Klik 📤 Kirim Laporan BBM**
7. **Popup sukses** muncul dengan ID Transaksi

### 2.3 Log Perjalanan (Step-by-Step)

1. Tab **🗺️ Trip**
2. **Pilih Nama Driver** → Nopol terisi otomatis
3. **Isi:** Tanggal, KM Awal, Jam Berangkat
4. **Klik + Tambah Rute** untuk setiap tujuan:
   - Isi lokasi manual, atau
   - **Klik 📍 GPS** → lokasi + jam + KM terisi otomatis
5. **Klik 📋 Kirim Log Perjalanan**

### 2.4 Mode Offline
- Jika sinyal hilang: 🟡 Offline — Data tersimpan lokal
- Counter antrean muncul di kanan atas
- Data otomatis terkirim saat sinyal kembali

### 2.5 Cek Performa Kendaraan
1. Tab **📊 Rapor**
2. Masukkan No. Polisi → **Cek**
3. Lihat: KM/L, Status (BOROS/CUKUP/BAIK/SANGAT BAIK), Saran AI

### 2.6 Konfirmasi Serah Terima Kendaraan
1. Saat GA assign kendaraan → notifikasi kuning muncul
2. Klik **✅ Konfirmasi Serah Terima**
3. Status berubah jadi hijau "Dikonfirmasi"

---

## 3. Panduan GA (General Affairs)

### 3.1 Dashboard Admin
Buka `/admin` — 4 tab:
- 🔴 **Antrean GA** — Klaim menunggu approval (berkedip jika ada)
- 💰 **Finance** — Siap dicairkan
- ✍️ **Driver TTD** — Menunggu tanda tangan
- 📦 **Arsip** — Selesai

### 3.2 Approve Klaim (Step-by-Step)

1. Tab **Antrean GA**
2. Lihat transaksi: foto, nominal, ODO, KM/L
3. Klik **🔍 Approve**
4. **Modal Cross-Check** muncul:
   - 🏥 Health Score kendaraan (0-100)
   - 📋 Detail transaksi + ODO sebelumnya
   - 🚩 Flags (ODO mundur, KM/L rendah, budget)
   - ✅ Rekomendasi: AMAN / PERLU PERHATIAN / INVESTIGASI
5. Klik **Lanjut Approve** → masukkan PIN → OK

### 3.3 Menolak Klaim
1. Klik **Tolak** pada transaksi
2. Masukkan PIN
3. Isi alasan penolakan
4. Klik **Tolak**

### 3.4 Manajemen Kendaraan (GA Assignments) — FITUR BARU

Buka `/ga/assignments`

#### A. Assign Kendaraan Kosong ke Driver
1. Lihat panel **➕ Assign Kendaraan Kosong** (kanan)
2. **Pilih Kendaraan** dari dropdown (nopol + tipe)
3. **Pilih Driver** dari dropdown
4. Isi Catatan (opsional)
5. Klik **➕ Assign Kendaraan**
6. Kendaraan muncul di tabel **Assignment Aktif**

#### B. Tukar Kendaraan Antar Driver
1. Lihat panel **🔄 Tukar Kendaraan** (kiri)
2. **Pilih Kendaraan** dari dropdown → Driver saat ini terisi otomatis
3. **Pilih Driver Baru** dari dropdown
4. **Pilih Kategori Alasan:**
   - 👤 Kendala Driver (sakit, cuti, dll)
   - 🚗 Kendala Kendaraan (rusak, servis, dll)
   - 🔄 Rotasi Biasa
   - 📝 Lainnya
5. **Isi Alasan Lengkap**
6. **Isi Nama GA**
7. Klik **🔄 Tukar Kendaraan**
8. Riwayat tercatat di tabel **📜 Riwayat Penukaran**

#### C. Lepas Kendaraan (Release)
1. Di tabel **Assignment Aktif**, klik **✕ Lepas**
2. Isi alasan di popup (contoh: "Masuk bengkel")
3. Klik OK
4. Kendaraan kembali ke pool "Assign Kosong"
5. Nopol driver dikembalikan ke nopol sebelumnya

### 3.5 Review Trip Log
1. Menu **🗺️ Trips**
2. Lihat log perjalanan driver
3. Verify atau Reject

---

## 4. Panduan Finance

### 4.1 Finance Review Panel (Step-by-Step)

1. Tab **💰 Finance**
2. Klik **🔍 Review** pada transaksi
3. **Split-screen muncul:**
   - **Kiri:** Semua foto (klik untuk zoom)
   - **Kanan:** Data transaksi lengkap + Budget usage
4. Tambah **Remark** jika perlu
5. Klik **💰 Keluarkan Dana** → PIN → OK

### 4.2 Edit ODO (Koreksi)
1. Klik **✏️** di samping ODO pada transaksi
2. Masukkan ODO baru
3. Isi alasan perubahan
4. Masukkan PIN Finance
5. Klik **Simpan Perubahan ODO**
6. Tercatat di Audit Log

### 4.3 Archive (Step-by-Step)
1. Tab **✍️ Driver TTD**
2. Pastikan driver sudah tanda tangan fisik
3. Klik **TTD & Arsip** → PIN → OK
4. Download **ZIP** untuk arsip digital (semua foto + info)

### 4.4 Rekapitulasi
1. Menu **📋 Rekap**
2. Default: 7 hari terakhir
3. Filter: tanggal, nopol, driver
4. **Cetak PDF** → klik Print
5. **Export ZIP** → download semua rapor driver

---

## 5. Panduan Admin

### 5.1 Settings — Akses
1. Buka **⚙️ Settings**
2. Masukkan **PIN Admin** (`123456`)
3. Halaman Settings terbuka

### 5.2 Driver Management

#### Lihat Daftar Driver
- Tabel: Driver | Nopol | Kendaraan | BBM | Status | Aksi

#### Aktifkan/Nonaktifkan Driver
- Klik tombol **Nonaktifkan** (merah) / **Aktifkan** (hijau)
- Konfirmasi popup → OK

#### Hapus Driver Permanen
- Klik tombol **🗑**
- Konfirmasi popup → OK

#### Tambah Driver Baru
1. Isi form **Tambah/Update Driver:**
   - Nama Driver (wajib)
   - No. Polisi (wajib)
   - Kendaraan (dropdown)
   - BBM (dropdown)
2. Klik **+ Simpan Driver**

### 5.3 Fleet Kendaraan — FITUR BARU

#### Lihat Semua Kendaraan
- Tabel: Nopol | Tipe | Brand | Kap (L) | BBM | Aktif | 🗑
- Nopol tampil sebagai tag monospace kuning

#### Tambah Kendaraan Baru (Tanpa Driver)
1. Isi form **➕ Tambah Kendaraan Baru:**
   - No. Polisi (wajib, contoh: L 1906 TF)
   - Tipe (contoh: AVANZA)
   - Brand (default: Toyota)
   - BBM Default (PERTALITE/PERTAMAX)
2. Klik **+ Tambah Kendaraan**
3. Kendaraan langsung tersedia di GA Assignments

### 5.4 User Management

#### Lihat Daftar User
- Tabel: Username | Nama | Role | Status | Login | Aksi

#### Aktifkan/Nonaktifkan User
- Klik tombol toggle (hijau/merah)

#### Reset PIN User
1. Klik tombol **🔑 PIN**
2. Popup muncul → isi PIN baru (6 digit)
3. Konfirmasi PIN
4. Klik **💾 Simpan PIN Baru**

#### Hapus User
- Klik tombol **🗑**

#### Tambah User Baru
1. Isi form **Tambah/Update User:**
   - Username
   - Nama Lengkap
   - Role (GA/Finance/Admin)
   - PIN (6 digit)
2. Klik **+ Simpan User**

### 5.5 Data Demo
- Klik **Aktifkan Data Demo** untuk menampilkan data dummy
- Data demo tidak muncul di dashboard utama
- Klik lagi untuk menonaktifkan

### 5.6 Import Excel
1. Klik **Unduh Template**
2. Isi data transaksi historis di Excel
3. Upload file .xlsx
4. Sistem otomatis mendaftarkan driver, kendaraan, BBM baru

### 5.7 Batas Konsumsi
- Atur Good/Warning/Min/Max KM/L per kombinasi Kendaraan+BBM
- Centang **Default** untuk menjadikan default

### 5.8 Multi-Fill Threshold
- Atur batas KM untuk deteksi top-up (default: 40 KM)
- Transaksi di bawah threshold → badge ⛽ TOP-UP

### 5.9 Backup Database
- Klik **Download Backup** untuk mengunduh file .sql

### 5.10 Audit Trail
1. Menu **📝 Audit Log**
2. Masukkan PIN Admin
3. Lihat semua aktivitas: create, approve, payout, archive, reject, swap, release, reset_pin, dll

---

## 6. FAQ

### Q: Watermark tidak muncul?
**A:** Pastikan GPS HP aktif. Watermark diproses otomatis setelah foto dipilih. Lihat badge status.

### Q: Kenapa KM/L = 0?
**A:** Transaksi pertama selalu 0. Transaksi berikutnya akan terhitung.

### Q: Lupa PIN?
**A:** Admin bisa mereset PIN user lain via Settings → 🔑 PIN.
Jika Admin lupa PIN, hubungi IT untuk reset via database.

### Q: Offline, data aman?
**A:** Ya, data disimpan di IndexedDB HP. Otomatis terkirim saat online. Lihat counter antrean.

### Q: Import Excel gagal?
**A:** Pastikan format tanggal: DD/MM/YYYY HH:MM. Format file: .xlsx.

### Q: Dropdown Tukar Kendaraan kosong?
**A:** Assign kendaraan dulu via "Assign Kosong". Dropdown hanya menampilkan kendaraan yang sedang aktif dipegang driver.

### Q: Bagaimana menambah kendaraan tanpa driver?
**A:** Settings → Fleet Kendaraan → isi form ➕ Tambah Kendaraan Baru → cukup isi nopol & tipe.

### Q: Kendaraan menganggur, apakah bisa digunakan?
**A:** Ya. Kendaraan tanpa driver muncul di GA Assignments → Assign Kosong. Bisa langsung di-assign ke driver manapun.

### Q: Apa perbedaan Tukar dan Lepas?
**A:** **Tukar** = ganti driver (kendaraan tetap aktif dengan driver baru). **Lepas** = kendaraan dikembalikan ke pool kosong (tidak ada driver).

---

## 📞 Kontak

**PT. Bestprofit Futures - Surabaya**  
BPF BBM System v1.0  
Developed & Maintained by **IT BPF Surabaya**

> **Catatan:** Semua perubahan di sistem tercatat di Audit Log. Setiap aksi memerlukan PIN sesuai role.
