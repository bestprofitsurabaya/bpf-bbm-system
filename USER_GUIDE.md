# 📖 Panduan Pengguna BPF BBM System v1.0

**PT. Bestprofit Futures - Surabaya**

---

## Daftar Isi
1. [Akses Aplikasi](#1-akses-aplikasi)
2. [Panduan Driver](#2-panduan-driver)
3. [Panduan GA](#3-panduan-ga)
4. [Panduan Finance](#4-panduan-finance)
5. [Panduan Admin](#5-panduan-admin)
6. [FAQ](#6-faq)

---

## 1. Akses Aplikasi

### URL
| Pengguna | URL |
|----------|-----|
| Driver (HP) | `https://nasbpfsby.duckdns.org:5000/driver` |
| Admin/GA/Finance (PC) | `https://nasbpfsby.duckdns.org:5000/admin` |

### Install PWA (Driver)
1. Buka URL di Chrome/Safari
2. Klik menu ⋮ → **"Add to Home Screen"**
3. Aplikasi terpasang seperti app native

---

## 2. Panduan Driver

### 2.1 Navigasi Bawah
- **⛽ BBM** - Form klaim BBM
- **🗺️ Trip** - Log perjalanan harian
- **📊 Rapor** - Cek performa kendaraan

### 2.2 Mengajukan Klaim BBM

1. Tab **⛽ BBM**
2. Tunggu GPS terdeteksi (kotak hijau ✅)
3. Pilih **Nama Driver** → Nopol & Kendaraan otomatis
4. Pilih **Jenis BBM** → Harga otomatis
5. Isi **Nominal, Appointment, Odometer, SPBU**
6. **Upload Foto:**
   - Klik 📷 Kamera atau 🖼️ Galeri
   - **Watermark OTOMATIS** ditambahkan (GPS + Waktu)
   - Lihat badge: ✅ Watermarked
   - Review foto di preview
7. Klik **📤 Kirim Laporan BBM**
8. 🎉 Modal sukses muncul dengan ID Transaksi

### 2.3 Log Perjalanan

1. Tab **🗺️ Trip**
2. Pilih Nama Driver
3. Isi KM Awal, Jam Berangkat
4. Klik **+ Tambah Rute**
5. Isi lokasi manual, atau klik **📍 GPS** untuk auto-isi:
   - Lokasi terisi dari GPS
   - Jam otomatis terisi waktu sekarang
   - KM terisi dari ODO tab BBM
6. Klik **📋 Kirim Log Perjalanan**

### 2.4 Mode Offline
- Jika sinyal hilang: 🟡 Offline - Data tersimpan lokal
- Data otomatis terkirim saat sinyal kembali
- Ada badge counter antrean offline

### 2.5 Cek Performa
- Tab **📊 Rapor**
- Masukkan plat nomor → **Cek**
- Lihat skor KM/L + saran AI

---

## 3. Panduan GA

### 3.1 Dashboard
- 🔴 **Antrean GA** (berkedip jika ada)
- 💰 Finance | ✍️ Driver TTD | 📦 Arsip

### 3.2 Approve
1. Tab Antrean GA → verifikasi foto (watermark terlihat)
2. Klik **Approve** → PIN 6-digit → OK

### 3.3 Reject
1. Klik **Tolak** → PIN → isi alasan → OK

---

## 4. Panduan Finance

### 4.1 Payout
1. Tab Finance → lihat Total Payout
2. Klik **Keluarkan Dana** → PIN → OK

### 4.2 Archive
1. Tab Driver TTD → pastikan TTD fisik
2. Klik **TTD & Arsip** → PIN → OK
3. Download ZIP untuk arsip digital

### 4.3 Rapor Massal
- Analytics → Cetak Rapor Driver → pilih periode → Unduh ZIP

---

## 5. Panduan Admin

### 5.1 Driver & Kendaraan
- Settings → PIN Admin
- Tambah/Nonaktifkan driver
- Sistem auto-register driver baru saat import

### 5.2 User & PIN
- Tambah user GA/Finance/Admin
- Ganti PIN (default: 123456)

### 5.3 Multi-Fill Threshold
- Atur batas KM top-up (default: 40)
- Transaksi di bawah threshold → badge ⛽ TOP-UP

### 5.4 Import Excel
- Download template → isi → upload
- Sistem otomatis daftarkan driver/kendaraan/BBM baru

### 5.5 Backup
- Settings → Download Backup (.sql)

### 5.6 Audit Trail
- Menu Audit Log → PIN Admin
- Lihat semua aktivitas sistem

---

## 6. FAQ

**Q: Watermark tidak muncul?**
A: Pastikan GPS aktif. Watermark diproses otomatis setelah foto dipilih. Lihat badge status.

**Q: Kenapa KM/L = 0?**
A: Transaksi pertama = 0. Berikutnya > 0. Normal.

**Q: Lupa PIN?**
A: Hubungi Admin untuk reset.

**Q: Offline, data aman?**
A: Ya, disimpan di IndexedDB HP. Otomatis terkirim saat online.

**Q: Import Excel gagal?**
A: Format tanggal: DD/MM/YYYY HH:MM. Format file: .xlsx.

---

## 📞 Kontak

**PT. Bestprofit Futures - Surabaya**  
BPF BBM System v1.0  
Developed & Maintained by **IT BPF Surabaya**
