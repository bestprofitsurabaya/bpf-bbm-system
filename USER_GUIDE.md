# 📖 Panduan Pengguna BPF Fleet & BBM System v1.2

**PT. Bestprofit Futures — Surabaya**

---

Halo, rekan-rekan BPF! 👋

Selamat datang di sistem manajemen armada dan BBM kita. Panduan ini akan menemani kamu memahami alur kerja sistem, dari mengajukan klaim BBM, mengelola kasbon, hingga memverifikasi laporan. Kami tulis dengan bahasa yang sederhana dan mudah diikuti, jadi tidak perlu khawatir meskipun baru pertama kali menggunakan.

> ⚠️ **Peringatan Keamanan:** Demi keamanan data bersama, **segera ganti PIN bawaan (`123456`) saat pertama kali login.** Akun yang masih menggunakan PIN bawaan berisiko dinonaktifkan oleh sistem.

---

## Daftar Isi

1. [Memulai](#1-memulai)
2. [Untuk Driver](#2-untuk-driver)
3. [Untuk GA (General Affairs)](#3-untuk-ga-general-affairs)
4. [Untuk Finance](#4-untuk-finance)
5. [Untuk Admin](#5-untuk-admin)
6. [Panduan Arsip](#6-panduan-arsip)
7. [Panduan Kasbon (Uang Muka BBM)](#7-panduan-kasbon-uang-muka-bbm)
8. [Perbandingan: Klaim Biasa vs. Kasbon](#8-perbandingan-klaim-biasa-vs-kasbon)
9. [Troubleshooting (Mengatasi Masalah)](#9-troubleshooting-mengatasi-masalah)
10. [Glosarium](#10-glosarium)

---

## 1. Memulai

### 1.1 Alamat Akses

| Pengguna | URL | Perangkat yang Disarankan |
|----------|-----|---------------------------|
| Driver | `https://nasbpfsby.duckdns.org:5000/driver` | HP Android / iPhone |
| GA, Finance, Admin | `https://nasbpfsby.duckdns.org:5000/admin` | Komputer / Laptop |
| GA (Penugasan Kendaraan) | `https://nasbpfsby.duckdns.org:5000/ga/assignments` | Komputer / Laptop |
| Analytics | `https://nasbpfsby.duckdns.org:5000/admin/analytics` | Komputer / Laptop |
| Settings | `https://nasbpfsby.duckdns.org:5000/admin/settings` | Komputer / Laptop |

### 1.2 Kredensial Awal

> 🔑 **Harap segera ganti PIN setelah login pertama.**

| Peran | Nama Pengguna | PIN Awal |
|-------|---------------|----------|
| Admin | `admin` | `123456` |
| GA | `ga_officer` | `123456` |
| Finance | `finance_officer` | `123456` |

### 1.3 Memasang Aplikasi di HP (Driver)

1. Buka browser Chrome di HP kamu.
2. Kunjungi URL Driver di atas.
3. Ketuk ikon titik tiga (⋮) di pojok kanan atas.
4. Pilih **"Add to Home Screen"** atau **"Tambahkan ke Layar Utama"**.
5. Aplikasi akan terpasang seperti aplikasi biasa di HP-mu. 🎉

---

## 2. Untuk Driver

Sebagai ujung tombak operasional, kamu bisa mengajukan klaim BBM, mencatat perjalanan, mengajukan kasbon, dan memantau performa kendaraan — semuanya langsung dari HP.

### 2.1 Navigasi Dasar

Di bagian bawah layar, terdapat 4 tab navigasi:

- **⛽ BBM** – Untuk mengajukan klaim BBM.
- **💰 Kasbon** – Untuk mengajukan uang muka BBM dan mengisi LPJ.
- **🗺️ Trip** – Untuk mencatat log perjalanan.
- **📊 Rapor** – Untuk mengecek performa kendaraan.

Tab yang sedang aktif akan ditandai dengan garis biru di bawahnya. Kamu bisa menggeser layar ke kiri atau kanan untuk berpindah tab.

### 2.2 Mengajukan Klaim BBM (Bayar Dulu, Klaim Belakangan)

1. Buka tab **⛽ BBM**. Tunggu hingga indikator GPS berubah menjadi hijau ✅.
2. Pilih **nama kamu** — nopol dan jenis kendaraan akan terisi otomatis.
3. Pilih **jenis BBM** — harga akan menyesuaikan secara otomatis.
4. Isi data pengisian:
   - **Nominal** (rupiah)
   - **Jumlah Appointment** (jika ada)
   - **Odometer** (angka KM saat ini)
   - **Jenis SPBU** (Rekanan atau Non-Rekanan)
5. Unggah **3 foto** pendukung. Kamu bisa memilih langsung dari 📷 kamera atau 🖼️ galeri. Sistem akan membubuhkan **watermark otomatis** pada foto.
6. Klik **📤 Kirim Laporan BBM**.

> 💡 **Tips GPS:** Jika GPS tidak kunjung hijau, pastikan izin lokasi di pengaturan HP sudah aktif dan kamu berada di area terbuka.

### 2.3 Mencatat Log Perjalanan

1. Buka tab **🗺️ Trip**.
2. Pilih nama kamu.
3. Isi **KM Awal** dan **Jam**.
4. Klik **+ Tambah Rute** — kamu bisa mengisi alamat secara manual atau mengetuk tombol **📍 GPS** untuk mengambil lokasi saat ini.
5. Setelah selesai, klik **📋 Kirim Log Perjalanan**.

### 2.4 Mode Offline

- Saat sinyal hilang, sistem akan otomatis beralih ke mode offline (ditandai indikator 🟡).
- Semua data yang kamu input **tidak akan hilang** — tersimpan aman di HP.
- Lencana (counter badge) akan muncul menunjukkan jumlah data yang menunggu dikirim.
- Data akan terkirim otomatis begitu koneksi internet kembali normal.

### 2.5 Mengecek Performa Kendaraan

1. Buka tab **📊 Rapor**.
2. Masukkan nopol kendaraan yang ingin dicek.
3. Ketuk **Cek**.
4. Kamu bisa melihat skor KM/Liter, status konsumsi, dan saran dari AI.

---

## 3. Untuk GA (General Affairs)

Tugas utama GA adalah memverifikasi klaim, mengatur penugasan kendaraan, dan meninjau log perjalanan driver.

### 3.1 Dashboard

Buka halaman `/admin`. Di sana terdapat 5 tab utama:

| Tab | Fungsi |
|-----|--------|
| 🔴 **Antrean GA** | Verifikasi klaim BBM dan LPJ Kasbon yang masuk (berkedip jika ada antrean) |
| 💰 **Finance** | Memantau antrean pencairan dana |
| ✍️ **Driver TTD** | Konfirmasi tanda tangan dan pengarsipan |
| 📦 **Arsip** | Melihat data yang sudah diarsipkan |
| 💰 **Kasbon** | Mengelola pengajuan kasbon (approve, handover, verifikasi LPJ) |

### 3.2 Menyetujui Klaim

1. Buka tab **Antrean GA**.
2. Klik tombol **🔍 Approve** pada klaim yang ingin diperiksa.
3. Sebuah modal **Cross-Check** akan tampil, menampilkan:
   - Skor kesehatan kendaraan (Health Score)
   - Perbandingan ODO
   - Penanda (flags) jika ada kejanggalan
   - Informasi budget
4. Jika semua sesuai, klik **Lanjut Approve**.
5. Masukkan **PIN** GA kamu.
6. Selesai.

### 3.3 Menolak Klaim

1. Klik tombol **Tolak** pada klaim.
2. Masukkan **PIN** GA kamu.
3. Isi **alasan penolakan** dengan jelas (*wajib* — ini penting untuk jejak audit).
4. Klik **OK**.

### 3.4 Mengatur Penugasan Kendaraan (GA Assignments)

Buka halaman `/ga/assignments`.

#### ➕ Menugaskan Kendaraan Kosong ke Driver
- Pilih kendaraan yang tersedia, pilih driver, lalu klik **➕ Assign**.

#### 🔄 Menukar Kendaraan Antar Driver

**Contoh kasus:** Mobil A (dipakai Budi) masuk bengkel. Budi perlu meminjam Mobil B (dipakai Ani).

1. Pada panel **Tukar Kendaraan**:
   - Pilih **Mobil A** → driver saat ini **Budi**.
   - Pilih **Driver Baru: Ani**.
   - Kategori: **🚗 Kendala Kendaraan**.
   - Alasan: "Mobil A masuk bengkel 3 hari".
2. Ulangi langkah di atas untuk **Mobil B**:
   - Pilih **Mobil B** → driver saat ini **Ani**.
   - Driver Baru: **Budi**.
   - Kategori dan alasan yang sama.
3. Hasilnya: Budi dan Ani bertukar kendaraan sementara. Keduanya tetap bisa bekerja.

#### ✕ Melepas Kendaraan dari Driver
- Klik tombol **✕ Lepas** pada assignment yang ingin diakhiri.
- Isi alasan pelepasan.
- Kendaraan akan kembali ke "pool" kendaraan kosong.

> 💡 Semua perubahan penugasan tercatat rapi di bagian **Riwayat Penukaran** dan **Audit Log**.

### 3.5 Meninjau Log Perjalanan (Trip Review)

1. Buka halaman **🗺️ Trips** (dari menu atau tab).
2. Klik pada salah satu baris log perjalanan.
3. Sebuah popup detail rute akan muncul.
4. Klik **✅ Verify** untuk menyetujui, atau **❌ Reject** untuk menolak.

---

## 4. Untuk Finance

Tugas tim Finance adalah mencairkan dana, melakukan koreksi data, dan mengarsipkan transaksi yang telah selesai.

### 4.1 Meninjau & Mencairkan Dana (Payout)

1. Buka tab **💰 Finance**.
2. Klik tombol **🔍 Review** pada transaksi yang ingin dicairkan.
3. Layar akan menampilkan tampilan *split-screen*: foto di satu sisi, data transaksi di sisi lain.
4. Kamu bisa menambahkan **remark** (catatan) jika diperlukan.
5. Klik **💰 Keluarkan Dana**.
6. Masukkan **PIN** Finance.
7. Status transaksi akan berubah, menandakan dana sudah dicairkan.

### 4.2 Melakukan Koreksi Odometer (ODO)

- Pada baris transaksi, klik ikon ✏️ di samping data ODO.
- Masukkan **ODO baru** yang benar.
- Tuliskan **alasan koreksi**.
- Masukkan **PIN** Finance.
- Klik **Simpan**.

### 4.3 Mengarsipkan & Mengunduh

1. Buka tab **✍️ Driver TTD**.
2. Pastikan driver sudah menandatangani dokumen fisik.
3. Klik **TTD & Arsip**.
4. Masukkan **PIN** Finance.
5. Transaksi akan masuk ke Arsip. Kamu juga bisa mengunduh semua foto dalam satu file **ZIP**.

### 4.4 Mencetak Rekap & Laporan PDF

- Buka halaman **📋 Rekap**.
- Atur **filter** yang diinginkan (tanggal, tipe transaksi, dll.).
- Klik tombol **PDF** untuk menghasilkan laporan dengan kop surat profesional yang siap dicetak.

---

## 5. Untuk Admin

Admin bertanggung jawab mengelola data master, pengguna, dan konfigurasi sistem secara keseluruhan.

### 5.1 Menu Settings (Pengaturan)

Buka halaman `/admin/settings`. PIN akses: `123456` (atau PIN Admin yang baru).

#### 👤 Manajemen Driver
- **Tambah, nonaktifkan, atau hapus** data driver.
- *Catatan:* Di sini kamu hanya mengisi nama driver. Penugasan kendaraan ke driver dilakukan oleh GA melalui menu GA Assignments.

#### 🚗 Manajemen Armada (Kendaraan)
- **Tambah, nonaktifkan, atau lihat** data kendaraan.
- Kolom "Driver" akan otomatis menampilkan nama pengemudi yang sedang ditugaskan (berdasarkan assignment dari GA).

#### 👥 Manajemen Pengguna & PIN
- **Reset PIN:** Klik ikon 🔑 di samping nama pengguna → masukkan PIN 6 digit baru → konfirmasi → Simpan.
- **Nonaktifkan, Aktifkan, atau Hapus** akun pengguna.

#### Fitur Konfigurasi Lainnya
- **📊 Data Demo:** Untuk mengisi sistem dengan data contoh (bisa diaktifkan/nonaktifkan).
- **📥 Import Excel:** Unduh template, isi data, lalu unggah kembali untuk impor massal.
- **⛽ Multi-Fill Threshold:** Batas minimal jarak antar pengisian (default: 40 KM).
- **📊 Batas Konsumsi KM/L:** Standar konsumsi BBM yang dianggap normal.
- **💾 Backup Database:** Untuk mencadangkan seluruh data sistem secara manual.

### 5.2 Audit Log (Jejak Digital)

- Buka **📝 Audit Log**.
- Masukkan PIN Admin.
- Semua aktivitas tercatat di sini: **siapa** yang bertindak, **apa** yang dilakukan, dan **kapan** waktunya. Ini adalah bukti pertanggungjawaban digital yang transparan.

---

## 6. Panduan Arsip

### 6.1 Mengakses Arsip

- Dari Dashboard Admin, buka tab **📦 Arsip**.
- Secara otomatis, arsip akan menampilkan data **1 minggu terakhir**.

### 6.2 Mencari & Memfilter Data

- **🔍 Pencarian:** Kamu bisa mencari berdasarkan nopol atau nama driver (cukup ketik sebagian).
- **📅 Rentang Tanggal:** Tentukan periode waktu yang spesifik.
- **⛽ Filter BBM:** Pilih PERTALITE, PERTAMAX, atau Semua.
- **📊 Panel Ringkasan:** Menampilkan jumlah data yang ditemukan dan total nominalnya.

### 6.3 Navigasi Halaman (Pagination)

- Data ditampilkan maksimal 50 item per halaman.
- Gunakan navigasi ◀ **1 2 3 ...** ▶ di bagian bawah untuk berpindah halaman.

### 6.4 Aksi pada Data Arsip

- **📦 ZIP:** Mengunduh semua foto pendukung dalam satu file kompresi.
- **🔍 Review:** Melihat detail lengkap transaksi.
- **📄 PDF:** Menghasilkan laporan individual yang profesional.

---

## 7. Panduan Kasbon (Uang Muka BBM)

Fitur Kasbon memungkinkan driver mengajukan uang muka BBM terlebih dahulu, sehingga tidak perlu mengeluarkan uang pribadi.

### 7.1 Ringkasan Alur Lengkap

```
Driver Ajukan Dana → GA Setujui → Finance Cairkan → GA Serahkan ke Driver
→ Driver Isi BBM → Driver Isi LPJ → GA Verifikasi LPJ → Finance Arsipkan ✅
```

### 7.2 Untuk Finance: Mengatur Kode Unik Harian

1. Buka **Settings** → **🔢 Konfigurasi Kode Unik Kasbon**.
2. Pilih mode **✋ Manual (Finance Set)**.
3. Klik **💾 Simpan**.
4. Buka **Dashboard** → tab **💰 Kasbon**.
5. Masukkan kode unik hari ini (angka antara **Rp 100 – Rp 2.000**, kelipatan 100).
6. Klik **💾 Simpan Kode** → verifikasi PIN Finance.
7. Kode unik ini akan berlaku untuk semua pengajuan kasbon di hari itu.

### 7.3 Untuk Driver: Mengajukan Dana

1. Buka tab **💰 Kasbon**.
2. Pilih nama kamu — nopol & kendaraan akan terisi otomatis.
3. Isi **Nominal Dasar** yang dibutuhkan (contoh: Rp 200.000).
4. **Kode Unik** akan muncul otomatis (diambil dari kode yang telah diatur Finance).
5. **Total Pengajuan** = Nominal Dasar + Kode Unik.
6. Klik **💰 Ajukan Dana**.
7. Tunggu persetujuan dari GA dan Finance.

### 7.4 Untuk GA: Menyetujui & Menyerahkan Dana

1. Buka Dashboard → tab **💰 Kasbon**.
2. Lihat pengajuan yang masuk. Progress bar akan menunjukkan statusnya:
   - **📝 DRAFT:** Klik **✅ GA Approve** untuk menyetujui.
   - **💰 FINANCE_APPROVED:** Klik **🤝 Serahkan ke Driver** setelah mengambil uang dari Finance.
3. Masukkan nama GA saat diminta.
4. Semua aksi tercatat di Audit Log.

### 7.5 Untuk Finance: Menyetujui Pencairan

1. Buka Dashboard → tab **💰 Kasbon**.
2. Cari pengajuan dengan status **✅ GA_APPROVED**.
3. **Siapkan uang fisik** sesuai total pengajuan, termasuk pecahan untuk kode uniknya.
4. Klik **💰 Finance Approve**.
5. Dana akan diambil oleh GA untuk diserahkan kepada driver.

### 7.6 Untuk Driver: Mengisi LPJ (Setelah Menerima Dana)

1. Status kasbon akan berubah menjadi "🤝 Dana di Driver".
2. Buka tab **💰 Kasbon** → cari bagian **📝 LPJ Pending**.
3. Klik **📝 Isi LPJ**.
4. Kamu akan otomatis diarahkan ke tab **⛽ BBM** dengan nominal yang sudah terkunci.
5. Lengkapi data pengisian BBM: ODO, SPBU, Jumlah Appointment.
6. Unggah **4 foto** pendukung:
   - Foto ODO sebelum pengisian
   - Foto Nota + ODO sesudah pengisian
   - Foto Struk pembelian
   - Foto Dispenser *(khusus SPBU non-rekanan)*
7. Klik **📤 Kirim LPJ Kasbon**.
8. Status akan berubah menjadi **📋 LPJ_SUBMITTED**, menunggu verifikasi GA.

### 7.7 Verifikasi LPJ oleh GA

> **Penting:** Proses verifikasi LPJ Kasbon mengikuti alur yang sama dengan klaim BBM biasa.

1. GA membuka Dashboard → tab **Antrean GA**.
2. Transaksi LPJ Kasbon akan muncul dan ditandai dengan lencana **💰 Kasbon**.
3. GA memverifikasi foto dan data.
4. Klik **Approve**. Status transaksi LPJ akan berubah menjadi **verified_ga**, dan status kasbon menjadi **COMPLETED**.
5. Finance kemudian dapat mengarsipkan transaksi tersebut melalui tab Finance seperti biasa.

### 7.8 Memahami Kode Unik (Angka Receh)

- **Tujuan:** Sebagai pengaman dan pembeda transaksi.
- **Cara Kerja:** Setiap hari, Finance akan menentukan satu kode unik (contoh: Rp 500). Kode ini ditambahkan ke setiap nominal dasar pengajuan.
- **Contoh:** Nominal Dasar Rp 150.000 + Kode Unik Rp 500 = **Total Rp 150.500**.
- **Manfaat:** Driver menerima dana dengan nominal yang "ganjil", sehingga kecil kemungkinan terjadi selisih atau kekeliruan. Finance menyiapkan uang dengan pecahan yang sesuai.

### 7.9 Edit, Batal, dan Hapus Kasbon

Tabel berikut menjelaskan tindakan yang bisa dilakukan pada setiap status:

| Status | Tindakan yang Tersedia |
|--------|------------------------|
| **DRAFT** | ✏️ Edit Nominal, ❌ Tolak, 🗑 Hapus |
| **GA_APPROVED** | 💰 Finance Approve, ↩️ Batal (kembali ke DRAFT) |
| **FINANCE_APPROVED** | 🤝 Serahkan ke Driver (Handover), ↩️ Batal |
| **FUNDS_WITH_DRIVER** | ↩️ Batal (kembali ke DRAFT) |
| **LPJ_SUBMITTED** | (Menunggu verifikasi GA) |
| **COMPLETED** | 🔄 Reset LPJ (menghapus LPJ, driver bisa submit ulang jika ada kesalahan) |

---

## 8. Perbandingan: Klaim Biasa vs. Kasbon

| Aspek | 🟢 Klaim Biasa | 💰 Kasbon (Uang Muka) |
|-------|----------------|------------------------|
| **Sumber Dana Awal** | Uang pribadi driver terlebih dahulu | Perusahaan memberikan dana di muka |
| **Alur Proses** | Isi BBM → Klaim → GA Verifikasi → Finance Bayar | Ajukan → GA Setuju → Finance Cairkan → GA Serahkan → Isi BBM → LPJ → Verifikasi → Arsip |
| **ID Pengajuan** | Tidak ada | `CASH-YYYYMMDD-HHMMSSXX` |
| **ID Transaksi (LPJ)** | `BPF-YYYYMMDD-HHMMSSXX` | `BPF-YYYYMMDD-HHMMSSXX` |
| **Nominal** | Bebas, sesuai bukti struk | Nominal Dasar + Kode Unik (Rp 100 - Rp 2.000) |
| **Pengenal Khusus** | – | Lencana kuning "💰 Kasbon" di Dashboard, Rekap, dan Analytics |
| **Risiko Selisih** | Ditanggung driver | Diminimalkan dengan kode unik, dana pas |

---

## 9. Troubleshooting (Mengatasi Masalah)

| Masalah | Penyebab Kemungkinan | Solusi |
|---------|----------------------|--------|
| **Lupa PIN** | – | Hubungi Admin untuk mereset PIN kamu. |
| **GPS tidak muncul / tidak hijau** | Izin lokasi HP belum aktif, atau kamu di dalam ruangan. | Buka pengaturan HP > izin aplikasi > aktifkan Lokasi. Coba di tempat terbuka. |
| **Nopol tidak muncul di dropdown** | Driver belum ditugaskan ke kendaraan. | Minta GA untuk menugaskanmu melalui menu **GA Assignments**. |
| **Dropdown "Tukar Kendaraan" kosong** | Tidak ada penugasan kendaraan yang aktif. | Pastikan sudah ada assignment aktif. GA bisa menambahkannya. |
| **Data offline hilang?** | – | **Tidak.** Semua data tersimpan aman di penyimpanan lokal HP dan akan terkirim otomatis saat online. |
| **Import Excel gagal** | Format file atau tanggal salah. | Pastikan format tanggal adalah `DD/MM/YYYY HH:MM`. Gunakan file `.xlsx`. |
| **Gagal menghasilkan PDF** | – | Hubungi tim IT. |
| **Kode unik kasbon tidak muncul** | Finance belum mengatur kode unik hari ini. | Minta Finance untuk mengatur kode unik melalui tab Kasbon di Dashboard. |
| **LPJ Kasbon tidak terkirim** | Koneksi internet bermasalah. | Tidak perlu khawatir. LPJ akan masuk ke antrean offline dan terkirim saat koneksi pulih. |

---

## 10. Glosarium

| Istilah | Kepanjangan / Penjelasan |
|---------|--------------------------|
| **BBM** | Bahan Bakar Minyak |
| **GA** | General Affairs (Bagian Umum) |
| **LPJ** | Laporan Pertanggungjawaban |
| **ODO** | Odometer (pengukur jarak tempuh kendaraan) |
| **SPBU** | Stasiun Pengisian Bahan Bakar Umum |
| **PWA** | Progressive Web App (teknologi aplikasi yang bisa diinstal lewat browser) |
| **Kasbon** | Kas Bon (uang muka / pengajuan dana operasional) |
| **Kode Unik** | Angka spesial harian yang ditambahkan ke nominal kasbon sebagai pengaman |
| **Watermark** | Tanda digital yang disematkan otomatis pada foto sebagai bukti keaslian |
| **Audit Trail** | Jejak digital semua aktivitas untuk keperluan audit |

---

## 📞 Kontak & Dukungan

**PT. Bestprofit Futures — Surabaya**  
BPF Fleet & BBM System v1.2  
Dikembangkan oleh **Tim IT BPF Surabaya**

> *"Sistem yang baik adalah sistem yang memudahkan pekerjaan, bukan menambah beban."*  
> — Tim IT BPF Surabaya