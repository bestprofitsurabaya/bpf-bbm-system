# 📖 Panduan Pengguna BPF Fleet & BBM System v1.2

**PT. Bestprofit Futures — Surabaya**

---

Halo, rekan-rekan BPF! 👋

Selamat datang di sistem manajemen armada dan BBM kita. Panduan ini akan menemani kamu memahami alur kerja sistem, dari mengajukan klaim BBM, mengelola kasbon, memverifikasi laporan, hingga **mengelola appointment calon nasabah** (Marketing) dan **pembagian driver** (Chief Driver). Kami tulis dengan bahasa yang sederhana dan mudah diikuti, jadi tidak perlu khawatir meskipun baru pertama kali menggunakan.

> ⚠️ **Peringatan Keamanan:** Demi keamanan data bersama, **segera ganti PIN bawaan (`123456`) saat pertama kali login.** Akun yang masih menggunakan PIN bawaan berisiko dinonaktifkan oleh sistem.

---

## Daftar Isi

1. [Memulai](#1-memulai)
2. [Untuk Driver](#2-untuk-driver)
3. [Untuk GA (General Affairs)](#3-untuk-ga-general-affairs)
4. [Untuk Finance](#4-untuk-finance)
5. [Untuk Marketing (Input Appointment)](#5-untuk-marketing-input-appointment)
6. [Untuk Chief Driver (Pembagian Driver)](#6-untuk-chief-driver-pembagian-driver)
7. [Untuk Admin](#7-untuk-admin)
8. [Panduan Arsip](#8-panduan-arsip)
9. [Panduan Kasbon (Uang Muka BBM)](#9-panduan-kasbon-uang-muka-bbm)
10. [Perbandingan: Klaim Biasa vs. Kasbon](#10-perbandingan-klaim-biasa-vs-kasbon)
11. [Troubleshooting (Mengatasi Masalah)](#11-troubleshooting-mengatasi-masalah)
12. [Glosarium](#12-glosarium)

---

## 1. Memulai

### 1.1 Alamat Akses

| Pengguna | URL | Perangkat yang Disarankan |
|----------|-----|---------------------------|
| Driver | `https://census-biological-ran-stories.trycloudflare.com/driver` | HP Android / iPhone |
| **Login (semua role)** | **`https://census-biological-ran-stories.trycloudflare.com/login`** | Komputer / Laptop |
| **📣 Marketing (Input Appointment)** | `https://census-biological-ran-stories.trycloudflare.com/marketing` | Komputer / Laptop |
| **🚛 Chief Driver (Pembagian Driver)** | `https://census-biological-ran-stories.trycloudflare.com/chief-driver` | Komputer / Laptop |
| GA, Finance, Admin | `https://census-biological-ran-stories.trycloudflare.com/admin` | Komputer / Laptop |
| GA (Penugasan Kendaraan) | `https://census-biological-ran-stories.trycloudflare.com/ga/assignments` | Komputer / Laptop |
| GA (Review Trip) | `https://census-biological-ran-stories.trycloudflare.com/admin/trips` | Komputer / Laptop |
| Analytics | `https://census-biological-ran-stories.trycloudflare.com/admin/analytics` | Komputer / Laptop |
| Users (Admin saja) | `https://census-biological-ran-stories.trycloudflare.com/admin/users` | Komputer / Laptop |
| Settings | `https://census-biological-ran-stories.trycloudflare.com/admin/settings` | Komputer / Laptop |

> ⚠️ **URL online (Cloudflare Tunnel):** URL di atas adalah *quick tunnel* dan dapat **berubah setiap kali server di-restart**. Untuk melihat URL yang sedang aktif, jalankan `bash scripts/tunnel-url.sh` di server.
> 🔐 **Baru di v1.1:** Semua halaman admin kini **wajib login**. Jika belum login, kamu akan diarahkan ke halaman Login. Driver PWA **tidak perlu login**.
> 🌐 **Akses lokal (dev):** ganti `https://census-biological-ran-stories.trycloudflare.com` dengan `http://localhost:5001`.

### 1.2 Login & Logout

1. Buka halaman **Login** (`/login`).
2. Masukkan **Username** dan **PIN 6 digit** kamu.
3. Klik **Masuk**.
4. Setelah berhasil, kamu akan dibawa ke halaman sesuai **peran (role)** kamu:
   - **Marketing** → halaman **📣 Marketing Hub** (`/marketing`)
   - **Chief Driver** → halaman **🚛 Chief Driver** (`/chief-driver`)
   - **Admin / GA / Finance** → Dashboard Admin
5. Untuk keluar, klik tombol **🚪 Keluar** di pojok kanan atas halaman mana pun.

> 💡 **Tips:** Jika sesi kamu berakhir (mis. browser ditutup), sistem otomatis mengarahkan kembali ke halaman Login saat kamu mengakses halaman admin berikutnya. Driver tidak terpengaruh.

### 1.3 Kredensial Awal

> 🔑 **Harap segera ganti PIN setelah login pertama.**

| Peran | Nama Pengguna | PIN Awal |
|-------|---------------|----------|
| Admin | `admin` | `123456` |
| GA | `ga_officer` | `123456` |
| Finance | `finance_officer` | `123456` |
| Marketing | dibuat oleh Admin (contoh: `icang`) | `123456` (bisa direset Admin) |
| Chief Driver | dibuat oleh Admin (contoh: `chief_driver`) | `123456` (bisa direset Admin) |

### 1.4 Memasang Aplikasi di HP (Driver)

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

#### 📅 Integrasi Appointment (Baru di v1.2)

> Jika kamu mendapat penugasan **appointment** (kunjungan calon nasabah) dari Chief Driver:

- Setiap appointment yang **sudah selesai** akan otomatis muncul di panel **📅 Appointment Selesai** pada tab Trip (tanggal yang sama).
- Klik tombol **📥 Muat Semua ke Rute** — rute perjalanan terisi otomatis:
  - **Lokasi tujuan** = alamat calon nasabah
  - **Pukul** = jam sesi appointment (🌅 08.30 atau 🌆 14.30)
- Kamu tinggal melengkapi **KM** dan menyesuaikan waktu, lalu klik **📋 Kirim Log Perjalanan**.
- Trip yang dikirim tetap bisa diverifikasi GA seperti biasa, dan menampilkan badge **📅 APP-xxxx** di detail rute sebagai jejak appointment.

### 2.4 Mode Offline

- Saat sinyal hilang, sistem akan otomatis beralih ke mode offline (ditandai indikator 🟡).
- Semua data yang kamu input **tidak akan hilang** — tersimpan aman di HP.
- Lencana (counter badge) akan muncul menunjukkan jumlah data yang menunggu dikirim.
- Data akan terkirim otomatis begitu koneksi internet kembali normal.

### 2.5 Notifikasi Status Transaksi (Baru di v1.1) 🔔

Mulai v1.1, kamu akan menerima **notifikasi di HP** setiap kali transaksi atau kasbon kamu diproses di dashboard admin. Contoh notifikasi:

- ✅ Klaim BBM kamu **disetujui GA**
- 💰 Dana kasbon kamu **sudah dicairkan Finance**
- 🤝 Uang kasbon **sudah diserahkan** ke kamu
- ❌ Pengajuan kamu **ditolak** (beserta alasannya)

**Cara kerja:**
- Notifikasi muncul **langsung** saat admin memproses transaksimu (real-time via WebSocket).
- Jika HP sedang offline, notifikasi **tidak hilang** — akan muncul begitu koneksi kembali.
- Badge 🔔 menunjukkan jumlah notifikasi yang belum dibaca.
- Ketuk notifikasi untuk menandainya sudah dibaca.

### 2.6 Mengecek Performa Kendaraan

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

**Tips dashboard (v1.1):**
- **Ganti tab tanpa reload** — klik tab mana pun, konten berpindah instan.
- **Shortcut keyboard** — tekan tombol `1`–`5` untuk berpindah tab.
- **Ringkasan "Hari Ini"** selalu terlihat di atas, bahkan saat halaman di-scroll.
- **Cari langsung di antrean** — ketik nopol / nama driver pada kolom pencarian untuk memfilter tanpa reload.
- **Tandai Semua Dicek** — pada tab Antrean GA, kamu bisa menyetujui semua klaim sekaligus (tetap diminta PIN).

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

## 5. Untuk Marketing (Input Appointment)

Sebagai Marketing, tugas kamu adalah **mencatat kunjungan calon nasabah** (appointment) yang akan diprospek, agar Chief Driver bisa menyiapkan driver dan kendaraan yang tepat.

### 5.1 Alur Singkat

```
Kamu input appointment → Chief Driver bagi driver → Driver kunjungi nasabah
→ appointment selesai → otomatis masuk Log Perjalanan driver
```

### 5.2 Mengisi Appointment Baru

1. Login dengan akun **Marketing** — kamu langsung diarahkan ke halaman **📣 Marketing Hub** (`/marketing`).
2. Di panel **➕ Input Appointment Baru**, isi:
   - **Tanggal** kunjungan (default: hari ini)
   - **Sesi**: 🌅 **Sesi 1 (08.30)** atau 🌆 **Sesi 2 (14.30)** — tentukan slot perjalanan
   - **Nama Calon Nasabah** *(wajib)*
   - **No. HP** calon nasabah *(opsional)*
   - **Alamat lengkap** *(wajib)* — sistem otomatis **mendeteksi area/wilayah** (mis. Surabaya Barat, Sidoarjo) sebagai bantuan Chief Driver membagi tugas
   - **Catatan** *(opsional)*, mis. nasabah lama / referral
3. Butuh lebih dari satu? Klik **＋ Tambah Entry Lagi**, lalu isi semua sekaligus dan klik **📤 Simpan Appointment**.

> 💡 **Tips:** Pilih sesi sesuai kesepakatan jadwal dengan nasabah. Sesi 1 untuk kunjungan pagi, Sesi 2 untuk kunjungan siang/sore.

### 5.3 Memantau Jadwal Appointment

- Gunakan **pemilih tanggal** di atas untuk berpindah hari.
- Kartu statistik menampilkan ringkasan: total, Sesi 1, Sesi 2, menunggu driver, driver ditugaskan, dan selesai.
- Daftar appointment dikelompokkan per sesi dengan status:
  - ⏳ **Menunggu Driver** — belum ditugaskan
  - 🚗 **Driver Ditugaskan** — Chief Driver sudah menunjuk driver (nama driver tampil)
  - ✅ **Selesai** — nasabah sudah dikunjungi
  - ✕ **Dibatalkan**
- Filter **Semua / Sesi 1 / Sesi 2** untuk memfilter tampilan.

### 5.4 Mengedit & Membatalkan

- **✏️ Edit**: bisa mengubah data appointment **selama masih berstatus Menunggu Driver** (nama, HP, alamat, sesi, catatan).
- **Batal**: klik tombol **Batal** jika kunjungan tidak jadi — *hanya* bisa dilakukan sebelum appointment diproses driver.
- Setelah driver ditugaskan atau selesai, appointment **tidak bisa diubah/dibatalkan** dari sisi marketing.

### 5.5 Notifikasi 🔔

- Lonceng **🔔** di pojok kanan atas menampilkan notifikasi real-time, misalnya:
  - 🚗 "Driver **AKHAD** ditugaskan ke appointment APP-xxxx"
  - ✅ "Appointment APP-xxxx selesai dikunjungi"
- Notifikasi muncul **langsung** saat Chief Driver memproses appointment kamu.

---

## 6. Untuk Chief Driver (Pembagian Driver)

Tugas Chief Driver adalah **membagi appointment yang masuk kepada driver** berdasarkan alamat/area, memantau pelaksanaannya, dan memastikan semuanya tercatat di Log Perjalanan.

### 6.1 Buka Halaman

Login dengan akun **Chief Driver** (atau GA) → langsung diarahkan ke **🚛 Chief Driver Command Center** (`/chief-driver`).

### 6.2 Ringkasan Harian

- Pilih **tanggal** (◀ ▶ atau tombol **Hari Ini**).
- Kartu statistik menampilkan: Total, ⏳ Belum Tugas, 🚗 Ditugaskan, ✅ Selesai, ✕ Batal.
- Banner **🔗 Integrasi Log Perjalanan** menunjukkan berapa appointment yang sudah selesai dan siap masuk log perjalanan driver.

### 6.3 Menugaskan Driver (Board "Belum Ditugaskan")

1. Pada panel **📋 Belum Ditugaskan**, appointment dikelompokkan per sesi (🌅 08.30 / 🌆 14.30).
2. Setiap kartu menampilkan: nama calon nasabah, **area otomatis** (dari alamat), tim & marketing penginput, dan no. HP.
3. Ada **⭐ saran sistem**: driver aktif dengan beban paling ringan pada sesi tersebut — bisa dipakai langsung.
4. Pilih **driver** pada dropdown, lalu klik **Tugaskan**.
5. Jika kunjungan batal, klik **✕** untuk membatalkan appointment (wajib diisi alasan).

### 6.4 Memantau Tugas Per Driver (Panel "Tugas Per Driver")

Appointment yang sudah ditugaskan dikelompokkan **per driver**, sehingga terlihat jadwal lengkap satu driver dalam sehari:

| Tombol | Fungsi |
|--------|--------|
| ✅ **Selesai** | Menandai appointment selesai dikunjungi → otomatis terintegrasi ke Log Perjalanan driver |
| 🔄 **Ganti** | Memindahkan appointment ke driver lain |
| ↩️ | Membatalkan penugasan (appointment kembali ke "Belum Ditugaskan") |
| ✕ | Membatalkan appointment (dengan alasan) |

### 6.5 Unduh Rekap Harian 📥

- Klik **📥 Unduh Rekap Excel** untuk mengunduh laporan lengkap tanggal tersebut: nasabah, sesi, alamat, area, tim, marketing, dan driver — siap untuk arsip atau rapat.

### 6.6 Real-Time ⚡

- Board diperbarui otomatis (**tanpa reload**) setiap kali ada perubahan: appointment baru dari marketing, penugasan, atau penyelesaian.

> 💡 **Alur yang benar:** Tugaskan driver di sesi yang sesuai dengan lokasi agar perjalanan efisien — gunakan saran area dan saran driver dari sistem.

---

## 7. Untuk Admin

Admin bertanggung jawab mengelola data master, pengguna, dan konfigurasi sistem secara keseluruhan.

### 7.1 Menu Settings (Pengaturan)

Buka halaman `/admin/settings`. Halaman ini memiliki **PIN gate** tambahan — masukkan PIN Admin (`123456` atau PIN baru kamu).

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

### 7.2 Halaman Users 👥

Buka halaman **Users** (`/admin/users`) — **khusus Admin**.

Di halaman ini kamu bisa mengelola akun pengguna sistem secara terpusat:
- **Lihat semua pengguna** beserta role dan status aktif/nonaktif.
- **Tambah pengguna baru** (username, nama lengkap, role, PIN awal).
- **Ubah data & role** pengguna.
- **Reset PIN** pengguna yang lupa PIN.
- **Aktifkan / Nonaktifkan** akun (akun nonaktif tidak bisa login).

**Role yang tersedia (v1.2):**

| Role | Kegunaan | Catatan |
|------|----------|---------|
| `admin` | Akses penuh sistem | – |
| `ga` | Verifikasi klaim, trip review, penugasan kendaraan | – |
| `finance` | Pencairan dana, arsip | – |
| `marketing` | Input & kelola appointment nasabah | **Wajib punya Tim Marketing** |
| `chief_driver` | Pembagian driver appointment | – |

**👥 Tim Marketing (baru):** saat membuat user dengan role **Marketing**, isi kolom **Tim Marketing** (mis. "Tim Yusie"). Ketik nama tim baru → sistem otomatis mendaftarkannya; atau pilih dari daftar tim yang sudah ada. Nama tim akan tampil di halaman Marketing dan di board Chief Driver.

> 💡 Setelah login, Marketing otomatis diarahkan ke halaman Marketing, dan Chief Driver ke halaman Chief Driver.

### 7.3 Dark Mode 🌙

- Semua halaman admin punya tombol **🌙/☀️** di pojok kanan atas.
- Klik untuk berganti tema terang/gelap.
- Pilihan tersimpan otomatis — konsisten di semua halaman.

### 7.4 Audit Log (Jejak Digital)

- Buka **📝 Audit Log**.
- Masukkan PIN Admin.
- Semua aktivitas tercatat di sini: **siapa** yang bertindak, **apa** yang dilakukan, dan **kapan** waktunya. Ini adalah bukti pertanggungjawaban digital yang transparan.

---

## 8. Panduan Arsip

### 6.1 Mengakses Arsip

- Dari Dashboard Admin, buka tab **📦 Arsip**.
- Secara otomatis, arsip akan menampilkan data **1 minggu terakhir** (default).

### 6.2 Mencari & Memfilter Data

- **🔍 Pencarian:** Kamu bisa mencari berdasarkan nopol atau nama driver (cukup ketik sebagian).
- **📅 Rentang Tanggal:** Tentukan periode waktu yang spesifik.
- **⛽ Filter BBM:** Pilih PERTALITE, PERTAMAX, atau Semua.
- **📊 Panel Ringkasan:** Menampilkan jumlah data yang ditemukan dan total nominalnya.
- **💡 Tanpa reload:** Ketik filter lalu tekan terapkan — hasil langsung tampil, dan nilai filter tetap tersimpan saat halaman dimuat ulang.

### 6.3 Navigasi Halaman (Pagination)

- Data ditampilkan maksimal **50 item per halaman**.
- Di bagian bawah ada tombol **"Muat Lebih Banyak"** — klik untuk menampilkan halaman berikutnya tanpa reload.
- Tombol akan otomatis menghilang saat semua data sudah tampil.

### 6.4 Aksi pada Data Arsip

- **📦 ZIP:** Mengunduh semua foto pendukung dalam satu file kompresi.
- **🔍 Review:** Melihat detail lengkap transaksi.
- **📄 PDF:** Menghasilkan laporan individual yang profesional.

---

## 9. Panduan Kasbon (Uang Muka BBM)

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
7. Tunggu persetujuan dari GA dan Finance — kamu akan mendapat **notifikasi** di HP setiap ada perubahan status.

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

## 10. Perbandingan: Klaim Biasa vs. Kasbon

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

## 11. Troubleshooting (Mengatasi Masalah)

| Masalah | Penyebab Kemungkinan | Solusi |
|---------|----------------------|--------|
| **Tidak bisa masuk ke halaman admin** | Belum login / sesi berakhir. | Login dulu di `/login` dengan username + PIN. |
| **Lupa PIN** | – | Hubungi Admin untuk mereset PIN kamu. |
| **Akun terkunci / tidak bisa login** | Akun dinonaktifkan. | Hubungi Admin untuk mengaktifkan kembali akunmu (via halaman Users). |
| **Halaman admin langsung keluar ke login** | Sesi kedaluwarsa (browser ditutup / waktu habis). | Login ulang. Aksi yang belum tersimpan perlu diulang. |
| **Notifikasi driver tidak muncul** | Koneksi internet bermasalah / aplikasi belum dibuka ulang. | Pastikan online lalu muat ulang aplikasi. Notifikasi lama akan tetap muncul (tersimpan di server). |
| **GPS tidak muncul / tidak hijau** | Izin lokasi HP belum aktif, atau kamu di dalam ruangan. | Buka pengaturan HP > izin aplikasi > aktifkan Lokasi. Coba di tempat terbuka. |
| **Nopol tidak muncul di dropdown** | Driver belum ditugaskan ke kendaraan. | Minta GA untuk menugaskanmu melalui menu **GA Assignments**. |
| **Dropdown "Tukar Kendaraan" kosong** | Tidak ada penugasan kendaraan yang aktif. | Pastikan sudah ada assignment aktif. GA bisa menambahkannya. |
| **Data offline hilang?** | – | **Tidak.** Semua data tersimpan aman di penyimpanan lokal HP dan akan terkirim otomatis saat online. |
| **Import Excel gagal** | Format file atau tanggal salah. | Pastikan format tanggal adalah `DD/MM/YYYY HH:MM`. Gunakan file `.xlsx`. |
| **Gagal menghasilkan PDF** | – | Hubungi tim IT. |
| **Kode unik kasbon tidak muncul** | Finance belum mengatur kode unik hari ini. | Minta Finance untuk mengatur kode unik melalui tab Kasbon di Dashboard. |
| **LPJ Kasbon tidak terkirim** | Koneksi internet bermasalah. | Tidak perlu khawatir. LPJ akan masuk ke antrean offline dan terkirim saat koneksi pulih. |
| **Marketing tidak bisa login** | Akun belum dibuat / role salah. | Minta Admin membuat akun dengan role **Marketing** via halaman Users. |
| **Halaman Marketing tidak bisa diakses GA/Admin** | Halaman khusus role Marketing. | Gunakan halaman **Chief Driver** (`/chief-driver`) untuk melihat & mengelola semua appointment. |
| **Appointment belum muncul di board Chief Driver** | Tanggal berbeda / masih loading. | Pastikan tanggal di board sama dengan tanggal appointment; board memperbarui otomatis. |
| **Driver tidak muncul di dropdown penugasan** | Driver belum terdaftar / nonaktif. | Daftarkan driver via **Settings → Manajemen Driver** atau `/api/drivers/sync`, lalu muat ulang halaman. |
| **Appointment selesai tidak muncul di form Trip driver** | Driver/ tanggal berbeda, atau status belum "Selesai". | Pastikan Chief Driver menandai **✅ Selesai**, dan driver memilih nama + tanggal yang sama pada tab Trip. |
| **Tidak bisa edit appointment** | Status sudah diproses (ditugaskan/selesai). | Hanya appointment berstatus **Menunggu Driver** yang bisa diedit/dibatalkan oleh marketing. |

---

## 12. Glosarium

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
| **Session** | Status login pengguna yang tersimpan di browser (berakhir saat logout/browser ditutup) |
| **CSRF** | Cross-Site Request Forgery — perlindungan agar aksi di sistem tidak bisa dipalsukan dari situs lain |
| **Role-Based Access** | Pengaturan hak akses berdasarkan peran (Admin / GA / Finance / Marketing / Chief Driver) |
| **Notifikasi Real-Time** | Pemberitahuan langsung yang muncul di HP driver saat transaksinya diproses |
| **Appointment** | Jadwal kunjungan ke calon nasabah yang dicatat Marketing dan ditugaskan ke driver oleh Chief Driver |
| **Calon Nasabah** | Prospek/calon nasabah yang akan dikunjungi marketing (nama, alamat, dan jadwal) |
| **Sesi** | Slot waktu perjalanan appointment — **Sesi 1 (08.30)** dan **Sesi 2 (14.30)** |
| **Deteksi Area** | Fitur sistem yang mengenali wilayah dari alamat (mis. Surabaya Barat, Sidoarjo) untuk membantu pembagian driver |
| **Marketing** | Bagian yang mencatat dan mengelola appointment calon nasabah |
| **Chief Driver** | Petugas yang membagi appointment ke driver dan memantau pelaksanaannya |
| **Tim Marketing** | Kelompok marketing (mis. "Tim Yusie") tempat anggota marketing bernaung |

---

## 📞 Kontak & Dukungan

**PT. Bestprofit Futures — Surabaya**  
BPF Fleet & BBM System v1.2  
Dikembangkan oleh **Tim IT BPF Surabaya**

> *"Sistem yang baik adalah sistem yang memudahkan pekerjaan, bukan menambah beban."*  
> — Tim IT BPF Surabaya
