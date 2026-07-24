# 📖 Panduan Pengguna BPF Fleet & BBM System v1.1

**PT. Bestprofit Futures - Surabaya**

---

Halo! Selamat datang di sistem manajemen armada dan BBM kami. Panduan ini akan memandumu langkah demi langkah, dari hal paling dasar sampai fitur-fitur canggih. Tenang saja, kami tulis dengan bahasa yang mudah dipahami. 😊

---

## Daftar Isi
1. [Mulai dari Mana?](#1-mulai-dari-mana)
2. [Untuk Driver (di HP)](#2-untuk-driver-di-hp)
3. [Untuk GA (General Affairs)](#3-untuk-ga-general-affairs)
4. [Untuk Finance](#4-untuk-finance)
5. [Untuk Admin](#5-untuk-admin)
6. [Pertanyaan yang Sering Muncul](#6-pertanyaan-yang-sering-muncul)

---

## 1. Mulai dari Mana?

### Alamat yang Perlu Kamu Tahu

| Kamu Siapa? | Buka Alamat Ini | Pakai Apa? |
|-------------|-----------------|------------|
| **Driver** | `https://nasbpfsby.duckdns.org:5000/driver` | HP Android/iPhone |
| **GA / Finance / Admin** | `https://nasbpfsby.duckdns.org:5000/admin` | Komputer atau Laptop |
| **GA (Atur Kendaraan)** | `https://nasbpfsby.duckdns.org:5000/ga/assignments` | Komputer atau Laptop |
| **Lihat Grafik & Data** | `https://nasbpfsby.duckdns.org:5000/admin/analytics` | Komputer atau Laptop |
| **Pengaturan Sistem** | `https://nasbpfsby.duckdns.org:5000/admin/settings` | Komputer atau Laptop |

### PIN Bawaan (Jangan Lupa Diganti ya!)

| Peran | Username | PIN Awal |
|-------|----------|----------|
| Admin | `admin` | `123456` |
| GA | `ga_officer` | `123456` |
| Finance | `finance_officer` | `123456` |

> ⚠️ **Penting:** Ganti PIN setelah login pertama. Keamanan data tanggung jawab bersama.

### Tips: Pasang Aplikasi di HP (Driver)

1. Buka Chrome di HP kamu
2. Kunjungi alamat Driver di atas
3. Tap menu ⋮ (pojok kanan atas) → pilih **"Add to Home Screen"**
4. Selesai! Sekarang kamu punya icon aplikasi di layar HP. Keren kan? 😎

---

## 2. Untuk Driver (di HP)

Sebagai driver, kamu bisa mengajukan klaim BBM, mencatat perjalanan, dan melihat performa kendaraan — semua dari HP.

### 2.1 Tiga Menu Utama

Di bagian bawah layar, ada 3 tombol:
- **⛽ BBM** — Buat laporan klaim BBM
- **🗺️ Trip** — Catat log perjalanan harian
- **📊 Rapor** — Lihat performa kendaraanmu

Tab yang sedang aktif ditandai dengan garis biru di atasnya. Gampang dikenali!

### 2.2 Cara Mengajukan Klaim BBM

1. Buka tab **⛽ BBM**
2. Tunggu sampai GPS mendeteksi lokasimu (kotak hijau ✅)
3. **Pilih nama kamu** dari dropdown. Nopol dan tipe kendaraan akan muncul otomatis
4. Pilih **jenis BBM** (PERTALITE atau PERTAMAX) — harga terisi otomatis
5. Isi data:
   - **Nominal** (Rp) — volume akan dihitung otomatis
   - **Jumlah Appointment** — berapa klien yang kamu temui hari itu
   - **Odometer (KM)** — lihat angka di dashboard mobilmu
   - **SPBU** — Rekanan atau Non-Rekanan
6. **Upload 3 foto:**
   - Foto ODO (speedometer)
   - Foto ODO + Struk (berdampingan)
   - Foto Struk (close-up)
   - Kalau SPBU Non-Rekanan: tambah foto dispenser
   - Klik 📷 untuk kamera, 🖼️ untuk memilih dari galeri
   - Setiap foto akan diberi **watermark otomatis** (GPS + waktu)
7. Klik **📤 Kirim Laporan BBM**
8. 🎉 Selesai! Data kamu sudah masuk ke sistem.

### 2.3 Mencatat Perjalanan Harian

1. Buka tab **🗺️ Trip**
2. Pilih nama kamu
3. Isi **KM Awal** dan **Jam Berangkat**
4. Klik **+ Tambah Rute** untuk setiap tujuan
5. Kamu bisa isi manual, atau klik **📍 GPS** — lokasi, jam, dan KM akan terisi otomatis!
6. Klik **📋 Kirim Log Perjalanan**

### 2.4 Bagaimana Kalau Sinyal Hilang?

Tenang! Sistem kami sudah **offline-first**. Artinya:
- Kalau sinyal hilang, data tetap tersimpan di HP kamu
- Ada badge counter yang menunjukkan berapa data yang antre dikirim
- Begitu sinyal kembali, data akan terkirim otomatis
- **Tidak ada data yang hilang.** Janji! 🤝

### 2.5 Cek Performa Kendaraan

1. Buka tab **📊 Rapor**
2. Masukkan nomor polisi
3. Klik **Cek**
4. Kamu akan lihat: skor KM/L, status (BOROS/CUKUP/BAIK/SANGAT BAIK), dan saran dari AI

---

## 3. Untuk GA (General Affairs)

Sebagai GA, tugasmu adalah memverifikasi klaim BBM dan mengatur kendaraan siapa pakai apa.

### 3.1 Dashboard — Pusat Kendali

Buka `/admin`. Kamu akan lihat 4 tab:
- 🔴 **Antrean GA** — Klaim yang menunggu persetujuanmu (berkedip merah kalau ada)
- 💰 **Finance** — Klaim yang sudah kamu setujui, menunggu pencairan dana
- ✍️ **Driver TTD** — Menunggu tanda tangan fisik driver
- 📦 **Arsip** — Semua yang sudah selesai

### 3.2 Menyetujui Klaim BBM

1. Buka tab **Antrean GA**
2. Lihat detail transaksi: foto, nominal, ODO
3. Klik **🔍 Approve**
4. Kamu akan lihat **Cross-Check Verifikasi**:
   - 🏥 Health Score kendaraan (0-100)
   - 📋 Perbandingan ODO dengan sebelumnya
   - 🚩 Flags (kalau ada yang mencurigakan: ODO mundur, KM/L rendah, budget hampir habis)
   - ✅ Rekomendasi: AMAN / PERLU PERHATIAN / INVESTIGASI
5. Kalau yakin, klik **Lanjut Approve** → masukkan PIN → selesai!

### 3.3 Menolak Klaim

1. Klik **Tolak** pada transaksi yang mencurigakan
2. Masukkan PIN
3. Tulis alasan penolakan (ini penting untuk audit)
4. Klik **Tolak**

### 3.4 Mengatur Kendaraan (GA Assignments) — FITUR PENTING!

Buka `/ga/assignments`. Di sini kamu mengatur **siapa pakai kendaraan apa**.

#### A. Assign Kendaraan ke Driver

1. Lihat panel **➕ Assign Kendaraan Kosong** (bagian bawah)
2. Pilih **Kendaraan** dari dropdown (nopol + tipe)
3. Pilih **Driver** dari dropdown
4. Klik **➕ Assign Kendaraan**
5. Selesai! Kendaraan sekarang terhubung ke driver itu.

#### B. Tukar Kendaraan Antar Driver

Misalnya: mobil ABIEM masuk bengkel, mau dipinjami mobil lain.

1. Lihat panel **🔄 Tukar Kendaraan** (bagian tengah)
2. Pilih **Kendaraan** yang mau ditukar → driver saat ini muncul otomatis
3. Pilih **Driver Baru** yang akan memakai
4. Pilih **Kategori Alasan:**
   - 👤 Kendala Driver (sakit, cuti, dll)
   - 🚗 Kendala Kendaraan (rusak, servis, dll)
   - 🔄 Rotasi Biasa
   - 📝 Lainnya
5. Tulis **alasan lengkap** (ini dicatat di history)
6. Isi **nama kamu** sebagai GA
7. Klik **🔄 Tukar Kendaraan**

#### C. Lepas Kendaraan (Tanpa Driver Baru)

Misalnya: mobil masuk bengkel lama, belum ada pengganti.

1. Di tabel **Assignment Aktif**, klik **✕ Lepas**
2. Tulis alasan (contoh: "Masuk bengkel 2 minggu")
3. Klik OK
4. Kendaraan kembali ke daftar "Kosong", siap di-assign nanti.

> 💡 **Penting:** Semua perubahan (assign, tukar, lepas) tercatat di **Riwayat Penukaran** dan **Audit Log**. Jadi semua bisa dipertanggungjawabkan.

---

## 4. Untuk Finance

Sebagai Finance, kamu yang mencairkan dana dan mengarsipkan dokumen.

### 4.1 Review Sebelum Cairkan Dana

1. Buka tab **💰 Finance**
2. Klik **🔍 Review** pada transaksi
3. Kamu akan lihat **split-screen**:
   - **Kiri:** Semua foto (bisa diklik untuk zoom)
   - **Kanan:** Data lengkap transaksi + pemakaian budget bulan ini
4. Kalau perlu, tambah **remark** (catatan)
5. Kalau semua OK, klik **💰 Keluarkan Dana** → PIN → selesai!

### 4.2 Koreksi ODO (Kalau Ada Kesalahan)

1. Klik ikon **✏️** di samping angka ODO
2. Masukkan ODO yang benar
3. Tulis alasan perubahan
4. Masukkan PIN Finance
5. Klik **Simpan Perubahan**
6. Semua perubahan tercatat di Audit Log.

### 4.3 Arsip & Download

1. Buka tab **✍️ Driver TTD**
2. Pastikan driver sudah tanda tangan fisik
3. Klik **TTD & Arsip** → PIN → selesai
4. Kamu bisa **download ZIP** berisi semua foto + info transaksi

### 4.4 Cetak Rekap & PDF

1. Buka menu **📋 Rekap**
2. Filter berdasarkan tanggal, nopol, atau driver
3. Klik **PDF** untuk cetak rekap dalam format profesional dengan kop surat
4. Atau klik **PDF** di setiap transaksi untuk laporan detail per klaim

---

## 5. Untuk Admin

Sebagai Admin, kamu yang mengatur data master: driver, kendaraan, user, dan konfigurasi sistem.

### 5.1 Cara Masuk Settings

1. Buka **⚙️ Settings**
2. Masukkan **PIN Admin** (`123456` bawaan)
3. Halaman Settings akan terbuka

### 5.2 Mengelola Driver

Di bagian **👤 Driver Management**, kamu bisa:
- **Lihat** semua driver (nama + status)
- **Nonaktifkan** driver yang sudah tidak aktif (ini TIDAK mempengaruhi assignment kendaraan)
- **Aktifkan** kembali driver yang sudah nonaktif
- **Hapus** driver (hati-hati, ini permanen!)
- **Tambah driver baru** — cukup isi nama, tidak perlu nopol. Nopol diatur oleh GA.

### 5.3 Mengelola Kendaraan (Fleet)

Di bagian **🚗 Fleet Kendaraan**, kamu bisa:
- **Lihat** semua kendaraan (nopol, tipe, brand, kapasitas, BBM default)
- **Lihat driver** yang sedang memakai (dari assignment GA)
- **Tambah kendaraan baru** — isi nopol, tipe, brand, BBM default. Tidak perlu driver!
- **Nonaktifkan** kendaraan yang sudah tidak dipakai

> 💡 Kendaraan yang kamu tambah di sini akan langsung muncul di dropdown GA Assignments. Praktis!

### 5.4 Mengelola User & PIN

Di bagian **👥 User & PIN**, kamu bisa:
- **Lihat** semua user (username, nama, role, status, login terakhir)
- **Reset PIN** — klik 🔑 PIN, masukkan PIN baru 6 digit, konfirmasi, simpan
- **Nonaktifkan/Aktifkan** user
- **Tambah user baru** — isi username, nama, role (GA/Finance/Admin), dan PIN

### 5.5 Fitur Lainnya

- **📊 Data Demo** — klik untuk menampilkan/menyembunyikan data dummy (buat testing)
- **📥 Import Excel** — unduh template, isi data historis, upload. Sistem akan otomatis mendaftarkan driver/kendaraan/BBM baru.
- **⛽ Multi-Fill Threshold** — atur batas KM untuk deteksi top-up (default: 40). Kalau driver isi BBM dengan jarak di bawah ini, sistem menandai sebagai top-up.
- **📊 Batas Konsumsi** — atur standar KM/L per kendaraan (Baik, Warning, Min, Max)
- **💾 Backup** — download seluruh database dalam format SQL

### 5.6 Audit Log

Buka menu **📝 Audit Log** (masukkan PIN Admin). Di sini kamu bisa melihat **semua aktivitas** di sistem: siapa melakukan apa, kapan, dari IP mana. Transparan dan akuntabel.

---

## 6. Panduan Arsip (Tab Archive)

### 6.1 Akses Arsip
1. Buka Dashboard → klik tab **📦 Arsip**
2. Default menampilkan **1 minggu terakhir**

### 6.2 Fitur Pencarian & Filter
- **🔍 Search**: Cari berdasarkan **nopol** ATAU **nama driver** (cukup ketik sebagian)
- **📅 Rentang Tanggal**: Pilih tanggal mulai dan akhir
- **⛽ Filter BBM**: Pilih PERTALITE, PERTAMAX, atau Semua
- **📊 Summary**: Menampilkan jumlah data + total nominal

### 6.3 Pagination
- Maksimal **50 data per halaman**
- Navigasi: ◀ Sebelumnya | 1 2 3 ... | Selanjutnya ▶
- Klik nomor halaman untuk berpindah

### 6.4 Aksi di Arsip
- **📦 ZIP**: Download semua foto dalam 1 file
- **🔍 Review**: Lihat detail transaksi (Finance Review Panel)
- **📄 PDF**: Download laporan PDF profesional

---

## 7. Pertanyaan yang Sering Muncul

### Q: Kok nopol tidak muncul waktu saya pilih driver?
**A:** Driver itu belum di-assign kendaraan oleh GA. Minta GA untuk assign dulu via menu GA Assignments.

### Q: Dropdown "Tukar Kendaraan" kosong?
**A:** Belum ada kendaraan yang di-assign. Assign dulu minimal 1 kendaraan lewat "Assign Kendaraan Kosong".

### Q: Apa beda "Tukar" dan "Lepas"?
**A:** **Tukar** = ganti driver (kendaraan tetap aktif, cuma drivernya ganti). **Lepas** = kendaraan dikembalikan ke pool kosong (tidak dipakai siapapun).

### Q: Saya nonaktifkan driver, kendaraannya gimana?
**A:** Aman. Kendaraan tidak terpengaruh. GA yang akan mengatur apakah kendaraan itu di-assign ke driver lain atau dilepas.

### Q: Bisa tambah kendaraan tanpa driver?
**A:** Bisa! Settings → Fleet Kendaraan → isi nopol + tipe → Tambah. Nanti GA yang akan assign ke driver.

### Q: Lupa PIN?
**A:** Kalau kamu Admin, PIN bisa direset dari database. Kalau kamu GA/Finance, minta Admin untuk reset PIN-mu lewat Settings → 🔑 PIN.

### Q: HP offline, data ilang?
**A:** Tidak. Data tersimpan di HP dan akan otomatis terkirim begitu sinyal kembali. Ada counter yang menunjukkan antrean data.

### Q: Format import Excel gimana?
**A:** Unduh template dari Settings → Bulk Import. Isi dengan format: Tanggal (DD/MM/YYYY HH:MM), Nama Driver, No Polisi, Tipe Kendaraan, Jenis BBM, Nominal, Harga/Liter, Odometer, Jumlah Appointment, Alamat GPS.

### Q: PDF yang dicetak seperti apa?
**A:** Profesional! Ada kop surat PT Bestprofit Futures, logo, grid foto 2×2, cross-check verifikasi, health score, status approval bar. Semua dalam satu halaman yang rapi.

---

## 📞 Butuh Bantuan?

**PT. Bestprofit Futures - Surabaya**  
BPF Fleet & BBM System v1.1  
Dikembangkan oleh **IT BPF Surabaya**

> *"Sistem yang baik adalah sistem yang memudahkan, bukan menyulitkan."*  
> — Tim IT BPF Surabaya

### 3.5 Review Trip Log (Logsheet)

Buka menu **🗺️ Trips**. Di sini kamu bisa melihat semua log perjalanan yang disubmit driver.

#### Fitur di Halaman Trips:
- **📊 Summary Cards** — Lihat sekilas: berapa Pending, Verified, Rejected, Total
- **🔍 Filter** — Cari berdasarkan nama driver, tanggal, atau status
- **🖱️ Klik Baris** — Muncul popup detail lengkap setiap rute perjalanan
- **🖨️ Print** — Cetak detail perjalanan dari popup
- **📥 Excel** — Unduh logsheet dalam format Excel
- **📄 PDF** — Unduh logsheet dalam format PDF dengan kop surat

#### Cara Verifikasi:
1. Klik baris trip → lihat detail rute di popup
2. Kalau sesuai, klik **✅ Verify**
3. Kalau tidak, klik **❌ Reject** → isi alasan

#### Detail yang Ditampilkan:
- Nama driver, nopol, tanggal
- Jam berangkat & tiba
- KM awal & akhir
- **Tabel rute**: lokasi berangkat, pukul, KM → lokasi tujuan, pukul, KM