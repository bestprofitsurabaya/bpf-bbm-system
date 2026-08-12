# 📖 Panduan Pengguna BPF Fleet & BBM System

> **Siapa pun kamu — sopir, OB, admin, atau pimpinan — panduan ini ditulis untuk kamu.**
> Tidak perlu paham teknis. Cukup ikuti langkah-langkah sesuai bagianmu.

---

## 📑 Daftar Isi

1. [Selamat Datang](#1-selamat-datang)
2. [Cara Masuk (Login)](#2-cara-masuk-login)
3. [Untuk OB — Pembelian Air Minum 💧](#3-untuk-ob--pembelian-air-minum)
4. [Untuk Driver — BBM & Perjalanan 🚗](#4-untuk-driver--bbm--perjalanan)
5. [Untuk GA — Verifikasi & Pengawasan 🧾](#5-untuk-ga--verifikasi--pengawasan)
6. [Untuk Finance — Pembayaran & Rekap 💰](#6-untuk-finance--pembayaran--rekap)
7. [Untuk Marketing — Jadwal Appointment 📣](#7-untuk-marketing--jadwal-appointment)
8. [Untuk Chief Driver — Pembagian Tugas 🚛](#8-untuk-chief-driver--pembagian-tugas)
9. [Untuk Admin — Pengaturan Sistem ⚙️](#9-untuk-admin--pengaturan-sistem)
10. [Kasbon: Alur Lengkap dari A sampai Z](#10-kasbon-alur-lengkap-dari-a-sampai-z)
11. [Mengatasi Masalah (Troubleshooting)](#11-mengatasi-masalah-troubleshooting)
12. [Istilah-istilah Penting](#12-istilah-istilah-penting)

---

## 1. Selamat Datang

Aplikasi ini adalah **satu tempat untuk semua urusan armada dan kantor**:

- **Driver** mencatat pembelian BBM, mengajukan kasbon (uang muka), dan melaporkan perjalanan.
- **OB** mengajukan pembelian air minum galon/botol/gelas.
- **GA, Finance, Marketing, Chief Driver, dan Admin** memverifikasi, menyetujui, dan mengelola semuanya dari dashboard masing-masing.

Setiap orang **hanya melihat menu sesuai tugasnya**. Tidak ada yang tercampur — tiap bagian punya halaman sendiri (prinsip *least privilege*: akses seminimal mungkin).

> 💡 Aplikasi bisa dibuka dari **komputer, laptop, atau HP** — cukup pakai browser.

---

## 2. Cara Masuk (Login)

### 2.1 Halaman Login

1. Buka alamat aplikasi (tanyakan ke Admin jika belum tahu).
2. Halaman **Login** akan muncul.
3. Isi **Username** dan **PIN 6 digit** milikmu.
4. Klik **🔐 Masuk**.

Setelah masuk, kamu otomatis diarahkan ke halaman utama sesuai peranmu:

| Peran | Langsung dibawa ke |
|-------|--------------------|
| Admin | Dashboard Admin |
| GA | Dashboard GA |
| Finance | Dashboard Finance |
| Marketing | Marketing Hub |
| Chief Driver | Dashboard Chief Driver |
| Driver | Aplikasi Driver |
| OB | Halaman Air Minum |

### 2.2 Keluar dari Aplikasi

Klik tombol **🚪 Keluar** di pojok kanan atas. Selalu keluar jika memakai komputer bersama agar data tetap aman.

### 2.3 Kalau Lupa PIN?

Mintalah **Admin** untuk mereset PIN-mu (dari halaman Manajemen User). Jangan berbagi PIN dengan siapa pun — PIN adalah tanda tangan digitalmu.

> 🔑 **Saran:** segera ganti PIN setelah pertama kali masuk. PIN awal semua akun biasanya `123456`.

### 2.4 Memasang di Layar Utama HP (Opsional)

1. Buka aplikasi di browser HP (Chrome).
2. Ketuk ikon **⋮** (titik tiga) di pojok kanan atas.
3. Pilih **"Tambahkan ke Layar Utama"** (Add to Home Screen).
4. Aplikasi tampil seperti aplikasi biasa di HP-mu — bisa dibuka sekali sentuh. 📱

---

## 3. Untuk OB — Pembelian Air Minum 💧

> **Kamu adalah OB (Office Boy).** Tugasmu: mencatat pembelian air minum dan mengunggah bukti fotonya. Bagian yang lain (jenis, merek, verifikasi) sudah diurus Finance & GA — kamu tinggal mengisi form.

### 3.1 Yang Kamu Lihat

Setelah login, kamu langsung berada di **Halaman Air Minum**. Di sana ada form pengajuan dan daftar pengajuanmu.

### 3.2 Mengajukan Pembelian Air Minum (Langkah demi Langkah)

1. Isi **Tanggal** pembelian.
2. Isi **Jumlah yang dibeli** (berapa galon/botol/gelas).
3. Pilih **Jenis air minum** — pilihannya: **Gelas, Botol, atau Galon** (disediakan Finance).
4. Pilih **Merk** dari daftar (misalnya AQUA Galon, Le Minerale, dll).
5. **Unggah foto bukti** — dua foto wajib:
   - 📸 **Foto sebelum diisi** (kondisi galon kosong / sebelum isi ulang)
   - 📸 **Foto sesudah diisi** (galon sudah terpasang/penuh)
6. Klik **Kirim**.

Pengajuanmu akan muncul di daftar dengan status **"Menunggu Verifikasi"**.

> ⚠️ **Foto wajib.** Pengajuan tanpa foto bukti tidak bisa diproses. Foto juga harus jelas menunjukkan waktu (time stamp) — inilah bukti bahwa air benar-benar dibeli.

### 3.3 Setelah Kamu Mengirim

- **Finance** akan memeriksa dan memverifikasi pengajuanmu (bisa menambah catatan).
- Jika disetujui, akan terbit **PDF tanda terima** yang ditandatangani Finance (penyerah) dan GA (penerima).
- Jika ditolak, lihat alasan penolakan dan perbaiki pengajuannya.

### 3.4 Status yang Mungkin Kamu Lihat

| Status | Artinya |
|--------|---------|
| Menunggu Verifikasi | Sudah dikirim, sedang diperiksa Finance |
| Terverifikasi | Disetujui — nanti terbit tanda terima PDF |
| Ditolak | Ada yang kurang — perbaiki sesuai alasan |

> 💡 Semua pengajuanmu **hanya terlihat olehmu, Finance, dan Admin**. OB lain tidak bisa melihat pengajuanmu.

---

## 4. Untuk Driver — BBM & Perjalanan 🚗

> **Kamu adalah Driver.** Tiga hal utama: (1) melaporkan pembelian BBM, (2) mengajukan kasbon, (3) mencatat log perjalanan. Semuanya dari satu aplikasi yang ramah HP.

### 4.1 Halaman Driver

Buka halaman Driver (bisa dipasang di HP). **Login dengan Username & PIN** yang diberikan Admin. Ada 4 tab: **⛽ BBM**, **💰 Kasbon**, **🗺️ Trip**, **📊 Rapor**.

### 4.2 Melaporkan Pembelian BBM (Bayar Dulu, Klaim Belakangan)

1. Buka tab **⛽ BBM**.
2. Isi data pembelian: **jenis BBM**, **liter**, **harga per liter**, **nominal**, **SPBU**, dan **foto struk/bukti**.
3. Klik **Kirim**.

Klaimmu masuk antrean **GA** untuk disetujui, lalu **Finance** untuk dibayar. Statusnya bisa kamu pantau di daftar riwayat.

### 4.3 Mengajukan Kasbon (Uang Muka Sebelum Berangkat)

1. Buka tab **💰 Kasbon**.
2. Isi **nominal dasar** yang kamu butuhkan. Sistem otomatis menambahkan **kode unik** (angka receh, misal Rp 100.000 + kode) supaya pembayaranmu bisa dicocokkan.
3. Klik **💰 Ajukan Kasbon**.

Alur lengkapnya ada di [Bagian 10](#10-kasbon-alur-lengkap-dari-a-sampai-z).

### 4.4 Mencatat Log Perjalanan (Trip)

1. Buka tab **🗺️ Trip**.
2. Isi **tujuan perjalanan, lokasi berangkat, lokasi tujuan, dan KM awal**.
3. Saat sampai, catat **KM akhir** dan klik selesai.

Laporan ini dipakai GA untuk meninjau dan menghitung efisiensi kendaraan.

### 4.5 Cek Performa Kendaraan (Rapor)

Di tab **📊 Rapor**, masukkan **nomor polisi** kendaraanmu untuk melihat performa bahan bakar (rata-rata km/liter). Statusnya: **HEMAT**, **CUKUP**, atau **BOROS**.

### 4.6 Mode Offline 📡

Pernah di jalan tanpa sinyal? Tenang:

- Data yang kamu isi **tersimpan otomatis di HP**.
- Saat sinyal kembali, aplikasi **mengirim sendiri datanya** ke server.
- Tanda **🟡 Offline** di atas layar berarti datamu belum terkirim. Tekan **🔄 Sinkron** untuk mengirim manual.

### 4.7 Jadwal Appointment Saya

Jika Marketing menjadwalkan kunjungan untukmu, jadwalnya muncul di aplikasi Driver. Setelah kunjungan selesai, isi **hasil kunjungan** — data ini menjadi bahan laporan Marketing.

---

## 5. Untuk GA — Verifikasi & Pengawasan 🧾

> **Kamu adalah GA (General Affairs).** Dashboard-mu adalah pusat kendali: menyetujui klaim BBM, memverifikasi anomali, menyetujui kasbon, dan mengawasi laporan perjalanan.

### 5.1 Dashboard GA

Setelah login, kamu langsung masuk **Dashboard GA** (`/app/ga`). Di sana ada:

- **🕐 Antrean Klaim BBM** — klaim driver yang menunggu persetujuanmu.
- **🛡 Verifikasi Anomali** — klaim ber-tanda ⚠️ yang perlu diperiksa lebih teliti.
- **💵 Kasbon menunggu approve** — jumlah & nominal.
- **🗺️ Laporan perjalanan pending** — laporan yang belum ditinjau.

> ⚡ **Anti-ngoding:** kalau ada klaim baru masuk saat kamu sedang membuka dashboard, antreannya **langsung ter-refresh sendiri**. Tidak perlu muat ulang halaman.

### 5.2 Menyetujui Klaim BBM

1. Di antrean klaim, periksa data klaim & foto bukti.
2. Klik **✅ Approve** jika benar.
3. Klaim berpindah ke antrean Finance untuk pembayaran.

### 5.3 Menolak Klaim

1. Klik **✕ Tolak**.
2. **Alasan penolakan wajib diisi** — ini penting untuk jejak audit.
3. Driver akan melihat alasan tersebut di aplikasinya.

### 5.4 Memverifikasi Klaim Ber-Tanda ⚠️

Klaim dengan tanda ⚠️ (anomali) punya tombol **🛡 Verifikasi** tersendiri. Saat diverifikasi, pastikan bukti (foto, nominal, waktu) benar-benar cocok. Kamu akan diminta konfirmasi sebelum menyetujui.

### 5.5 Menyetujui & Menyerahkan Kasbon

Lihat [Bagian 10](#10-kasbon-alur-lengkap-dari-a-sampai-z) — peranmu ada di langkah **GA: menyetujui & menyerahkan dana**.

### 5.6 Menu Lain yang Bisa Kamu Akses

- **Log Perjalanan** — meninjau laporan trip driver.
- **Assignments** — menugaskan/menukar kendaraan antar driver.
- **Kasbon / BBM** — melihat semua pengajuan.
- **Analytics** — memantau performa armada.

---

## 6. Untuk Finance — Pembayaran & Rekap 💰

> **Kamu adalah Finance.** Tugasmu: membayar klaim, mengatur kode unik kasbon, memverifikasi pembelian air minum, dan menyediakan data (jenis & merk air) untuk OB.

### 6.1 Dashboard Finance

Setelah login, kamu langsung masuk **Dashboard Finance** (`/app/finance`). Di sana ada:

- **💧 Rekap Air Minum** — ringkasan pembelian (total, menunggu verifikasi, terverifikasi, ditolak), **per OB**, **per jenis** (gelas/botol/galon), dan **per merk**.
- **🕐 Antrean Verifikasi** — pengajuan air minum yang menunggu keputusanmu.
- **💵 Kasbon menunggu Finance** — kasbon yang sudah disetujui GA & siap kamu cairkan, plus LPJ yang menunggu.

### 6.2 Memverifikasi Pembelian Air Minum

1. Buka **Antrean Verifikasi** (di dashboard atau halaman Air Minum).
2. Periksa pengajuan OB: tanggal, jumlah, jenis, merk, dan **dua foto bukti** (sebelum & sesudah).
3. Setuju? Isi **remark** (mis. "sesuai struk") dan klik verifikasi.
4. Perlu catatan tambahan? Tulis di kolom **note** — catatanmu ikut tersimpan sebagai jejak audit.
5. Setelah terverifikasi, **PDF tanda terima** otomatis bisa dicetak — ditandatangani **Finance** (yang menyerahkan) dan **GA** (yang menerima).

### 6.3 Menyediakan Jenis & Merk Air Minum

OB memilih jenis & merk dari daftar yang **kamu** kelola:

- Jenis: **Gelas, Botol, Galon**.
- Merk: daftar brand (mis. AQUA Galon, Le Minerale, dll) — bisa ditambah/diubah dari menu yang tersedia.

### 6.4 Rekap & Export

- Filter rekap berdasarkan **tanggal** (secara otomatis menampilkan 90 hari terakhir).
- Klik **⬇️ Export CSV** untuk mengunduh data ke Excel.

### 6.5 Menyetujui Pencairan Kasbon

Lihat [Bagian 10](#10-kasbon-alur-lengkap-dari-a-sampai-z) — peranmu ada di langkah **Finance: menyetujui pencairan**.

### 6.6 Menu Lain

- **Rekap** — mencetak rekap & laporan (PDF).
- **Kasbon / BBM**, **Analytics**, **Log Perjalanan**.

---

## 7. Untuk Marketing — Jadwal Appointment 📣

> **Kamu adalah Marketing.** Tugasmu: menjadwalkan kunjungan (appointment) untuk para driver.

### 7.1 Membuat Appointment Baru

1. Buka **Marketing Hub**.
2. Pilih **tanggal, driver, dan lokasi kunjungan**.
3. Simpan. Driver akan menerima jadwalnya di aplikasi.

### 7.2 Memantau & Mengedit

- Semua jadwal tampil di papan **realtime** — perubahan langsung terlihat semua orang yang berhak.
- Bisa **mengedit** atau **membatalkan** jadwal; statusnya langsung diperbarui (mis. "Selesai dikunjungi").

### 7.3 Hasil Kunjungan = Data Konversimu

Setelah driver mengunjungi lokasi, driver mengisi **hasil kunjungan**. Data ini menjadi laporan konversi untukmu. Notifikasi 🔔 memberi tahu saat status berubah.

---

## 8. Untuk Chief Driver — Pembagian Tugas 🚛

> **Kamu adalah Chief Driver.** Tugasmu: memastikan setiap driver punya tugas, dan setiap tugas ada drivernya.

### 8.1 Dashboard Chief Driver

- **Ringkasan harian** — gambaran tugas hari ini.
- **Board "Belum Ditugaskan"** — kendaraan/tugas yang belum ada drivernya.
- **Panel "Tugas Per Driver"** — melihat beban tiap driver sekaligus.

### 8.2 Menugaskan Driver

Dari board "Belum Ditugaskan", pilih kendaraan lalu tentukan drivernya. Tugas langsung muncul di aplikasi driver yang bersangkutan.

### 8.3 Unduh Rekap Harian

Ada tombol **📥 unduh rekap** untuk laporan harian (Excel).

### 8.4 Real-Time ⚡

Semua perubahan papan berjalan realtime — saat driver menyelesaikan tugas, statusnya langsung berubah tanpa muat ulang.

---

## 9. Untuk Admin — Pengaturan Sistem ⚙️

> **Kamu adalah Admin.** Kamu memegang kunci utama: membuat akun, mengatur nama untuk tanda terima, dan memantau jejak audit.

### 9.1 Manajemen User (Halaman Users)

- **Membuat akun baru** — pilih peran (Admin, GA, Finance, Marketing, Chief Driver, Driver, OB), isi nama & PIN.
- **Mengganti nama** — misalnya mengganti nama placeholder OB dengan nama asli. Nama ini yang tampil di dokumen (mis. PDF tanda terima air minum).
- **Reset PIN** — kalau user lupa PIN.
- **Nonaktifkan/Aktifkan** — akun yang dinonaktifkan **tidak bisa login** (tanpa harus dihapus, supaya jejak datanya tetap aman).
- **Hapus** — hapus akun (jika memang tidak dipakai).

### 9.2 Pengaturan (Settings)

- **Manajemen Driver** — tambah/hapus data driver.
- **Manajemen Armada** — tambah kendaraan (nopol, jenis, dll).
- **Nama untuk Tanda Terima Air Minum** — set **nama Finance** (yang menyerahkan) & **nama GA** (yang menerima). Nama ini otomatis tercetak di PDF tanda terima air minum.
- Pengaturan lain sesuai kebutuhan kantor.

### 9.3 Audit Log (Jejak Digital)

Semua aksi penting tercatat di **Audit Log**: siapa, melakukan apa, kapan. Berguna saat ada selisih atau pertanyaan. Bisa difilter berdasarkan aksi & peran.

### 9.4 Dark Mode 🌙

Suka tampilan gelap? Klik tombol **🌙/☀️** di pojok kanan atas. Pilihanmu tersimpan otomatis.

---

## 10. Kasbon: Alur Lengkap dari A sampai Z

Kasbon = uang muka yang diberikan ke driver sebelum berangkat. Alurnya seperti relay — tiap bagian menyentuh sekali:

### Langkah 1 — Driver mengajukan 💰
Driver isi nominal + kode unik otomatis. Status: **Draft**.

### Langkah 2 — GA menyetujui ✅
GA menyetujui pengajuan & **menyerahkan dana** ke driver (bisa juga dibatalkan jika batal berangkat). Status: **Disetujui GA**.

### Langkah 3 — Finance mencairkan 💵
Finance melihat antrean kasbon di Dashboard Finance dan menyetujui pencairan. Status: **Menunggu Serah / Diserahkan**.

### Langkah 4 — Driver mengisi LPJ 📋
Setelah dana diterima, driver mengisi **LPJ (Laporan Pertanggungjawaban)** — berapa yang benar-benar dipakai, lengkap dengan bukti. Status: **LPJ Diajukan**.

### Langkah 5 — GA memverifikasi LPJ 🧾
GA memeriksa LPJ. Jika sesuai, status menjadi **Selesai** 🎉. Jika tidak, dikembalikan ke driver untuk diperbaiki.

### Apa itu Kode Unik? 🤔
Angka "receh" yang ditambahkan ke nominal kasbon (mis. Rp 100.023, bukan Rp 100.000). Tujuannya: saat Finance membayar, **nominal persis ini** memastikan uang itu memang untuk kasbon tersebut — mencegah kesalahan pembayaran. Kode unik harian diatur oleh **Finance**.

### Bisa dibatalkan? 
- **Draft** → driver bisa menghapus sendiri.
- **Sudah diproses** → batal hanya lewat Admin/GA dengan alasan yang tercatat.

---

## 11. Mengatasi Masalah (Troubleshooting)

| Masalah | Solusi |
|---------|--------|
| **Tidak bisa login ("Username atau PIN salah")** | Periksa huruf besar/kecil & angka PIN. Jika tetap gagal, minta Admin reset PIN. |
| **Login terlalu sering gagal** | Sistem sengaja mengunci sementara (anti peretasan). Tunggu beberapa menit lalu coba lagi. |
| **Halaman tidak muncul / blank** | Muat ulang (F5). Coba browser lain atau mode penyamaran. |
| **Foto bukti tidak bisa diunggah** | Pastikan foto berukuran wajar (di bawah 16 MB) dan format JPG/PNG. |
| **Pengajuan air minum ditolak** | Baca alasan penolakan di daftar pengajuannya, perbaiki, ajukan ulang. |
| **Data offline belum terkirim** | Pastikan HP terhubung internet, lalu tekan **🔄 Sinkron** di aplikasi Driver. |
| **Lupa PIN / akun terkunci** | Hubungi Admin — hanya Admin yang bisa mereset PIN. |
| **Aplikasi terasa lambat** | Periksa koneksi internet. Data akan tetap tersimpan di HP (offline). |
| **Muncul pesan "CSRF token tidak valid"** | Muat ulang halaman dan coba lagi (sesi browser sedang kedaluwarsa). |

> Kalau masalah tetap berlanjut, hubungi Admin / tim IT dengan menyebutkan: **siapa kamu, kapan kejadiannya, dan pesan error yang muncul.**

---

## 12. Istilah-istilah Penting

| Istilah | Artinya (bahasa sehari-hari) |
|---------|------------------------------|
| **PIN** | Kata sandi 6 digit milikmu. |
| **Role / Peran** | Jabatanmu di sistem (Admin, GA, Finance, dll) — menentukan menu yang kamu lihat. |
| **Klaim BBM** | Laporan driver soal pembelian BBM, lengkap dengan bukti, untuk diganti uangnya. |
| **Kasbon** | Uang muka yang diterima driver sebelum berangkat. |
| **LPJ** | Laporan Pertanggungjawaban — bukti pemakaian kasbon setelah dana diterima. |
| **Kode Unik** | Angka receh tambahan pada nominal kasbon supaya pembayaran mudah dicocokkan. |
| **Anomali** | Kejanggalan pada klaim (tanda ⚠️) — perlu pemeriksaan ekstra oleh GA. |
| **Appointment** | Jadwal kunjungan yang dibuat Marketing untuk driver. |
| **Trip / Log Perjalanan** | Catatan perjalanan driver (dari mana, ke mana, KM berapa). |
| **Tanda Terima (PDF)** | Dokumen resmi — misalnya bukti pembelian air minum, ditandatangani Finance & GA. |
| **Audit Log** | Buku catatan digital semua aksi penting di sistem. |
| **SPBU Rekanan** | SPBU langganan kantor tempat driver mengisi BBM. |
| **Offline Mode** | Kondisi tanpa internet — data tetap tersimpan di HP dan terkirim otomatis saat online. |

---

## 📞 Kontak & Dukungan

Ada pertanyaan atau kendala? Hubungi **Admin** atau **tim IT** — mereka bisa melihat riwayat sistem (Audit Log) untuk membantu menyelesaikan masalahmu dengan cepat.

*Terakhir diperbarui: v2.9 — panduan disesuaikan dengan dashboard & peran terbaru (GA, Finance, OB).*
