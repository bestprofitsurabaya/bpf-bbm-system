# 🚗 BPF BBM System

**Sistem Manajemen dan Verifikasi Klaim BBM untuk Kendaraan Operasional PT. Bestprofit Surabaya**

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://www.python.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.11-003545?logo=mariadb)](https://mariadb.org/)
[![PWA](https://img.shields.io/badge/PWA-Enabled-5A0FC8?logo=pwa)](https://web.dev/progressive-web-apps/)

---

## 📋 Daftar Isi
- [Tentang Aplikasi](#-tentang-aplikasi)
- [Fitur Unggulan](#-fitur-unggulan)
- [Fitur Baru (v2.0)](#-fitur-baru-v20)
- [Tumpukan Teknologi](#-tumpukan-teknologi)
- [Memulai (Instalasi)](#-memulai-instalasi)
- [Panduan Penggunaan](#-panduan-penggunaan)
- [Struktur Proyek](#-struktur-proyek)
- [Keamanan & Audit](#-keamanan--audit)
- [Kontribusi](#-kontribusi)
- [Lisensi](#-lisensi)

---

## 🎯 Tentang Aplikasi

Aplikasi ini adalah solusi internal **end-to-end** untuk mengatasi *trust issue* dalam pelaporan BBM kendaraan operasional. Dengan menyediakan alur verifikasi visual yang ketat, otomatisasi pembuatan kronologis, dan fitur pelaporan profesional, sistem ini memastikan **transparansi** dan **akuntabilitas** penuh atas setiap klaim BBM.

**Masalah yang Dipecahkan:**
- ❌ Klaim BBM fiktif atau markup harga
- ❌ Kesulitan verifikasi bukti fisik
- ❌ Proses rekap dan pelaporan manual yang memakan waktu
- ❌ Tidak ada arsip digital terstandar

**Solusi:**
- ✅ Verifikasi berbasis bukti foto (ODO, Struk, Dispenser)
- ✅ Auto-kronologis untuk klaim error
- ✅ Generate PDF laporan profesional otomatis
- ✅ PWA siap diakses dari perangkat apapun

---

## ✨ Fitur Unggulan

### 1. 🧑‍✈️ Portal Driver (Form Input)
- **Upload Bukti Visual Dinamis**: Proses unggah yang menyesuaikan dengan jenis SPBU (Rekanan/Non-Rekanan):
  - 📸 Foto Odometer (Sebelum & Sesudah)
  - 📸 Foto Struk Fisik
  - 📸 Foto Dispenser (khusus SPBU Non-Rekanan)
  - 📸 Foto MyPertamina (dari admin)
- **Input Data Transaksi**: Formulir terstruktur untuk mencatat:
  - Nomor Polisi, Nama Driver, Tipe Kendaraan
  - Jenis BBM, Nominal, Harga/Liter, Volume
  - Odometer (KM), Lokasi SPBU, GPS (otomatis)
  - **📊 Jumlah Appointment Marketing** (fitur baru untuk analitik)

### 2. 👨‍💼 Portal Admin / Finance
- **Dashboard Verifikasi Terpusat**: Satu pintu untuk menyetujui, memodifikasi, atau meminta klarifikasi klaim.
- **Manajemen Bukti**: Kemampuan mengunggah bukti tambahan (foto MyPertamina).
- **Penanganan Error**: Fasilitas menandai klaim dengan error MyPertamina dan membuat kronologis otomatis.
- **Modifikasi Data**: Edit data transaksi jika terjadi kesalahan input oleh driver.

### 3. 🤖 Auto-Kronologis & ML Anomaly Detection
- **Otomatisasi Laporan**: Membuat teks laporan kronologis secara otomatis jika terjadi kendala (contoh: mutasi MyPertamina tidak muncul).
- **Deteksi Anomali ML**:
  - Menggunakan **Isolation Forest** untuk mendeteksi data BBM yang tidak wajar.
  - Menandai transaksi mencurigakan untuk review admin.
  - Analisis performa kendaraan (rata-rata KM/L, tren konsumsi).

### 4. 📄 Profesional Reporting
- **PDF Generator**:
  - **Laporan Per Transaksi**: PDF 1 halaman kompak dengan semua bukti foto dan data.
  - **Laporan Rekap**: PDF multi-halaman dengan tabel rekap, tanda tangan Finance & Branch Manager.
- **Dokumen Detail**: Rapi, profesional, dan siap untuk audit internal.
- **Filter Laporan**: Berdasarkan tanggal, nopol, dan nama driver.

### 5. 📊 Analytics & Performance Insight
- **Dashboard Analitik**:
  - Rata-rata KM/L per kendaraan.
  - Tren efisiensi harian.
  - Peringkat performa kendaraan (Baik, Cukup, Boros).
- **Insight Real-time**: Setelah submit, driver melihat performa kendaraannya 30 hari terakhir.

### 6. ⚙️ Sistem Terpadu
- **Infrastruktur Modern**: Berjalan di atas **Docker** dan **Docker Compose** dengan **Gunicorn** sebagai WSGI server production.
- **Database Relasional**: **MariaDB 10.11** dengan connection pooling untuk performa tinggi.
- **PWA Support**: Bisa di-install sebagai aplikasi di HP (Android/iOS) dengan manifest.json dan service worker.
- **Production-Ready**:
  - Environment variables untuk konfigurasi.
  - Connection pooling (10 koneksi default).
  - ThreadPoolExecutor untuk tugas asynchronous (logging, daily summary).

---

## 🆕 Fitur Baru (v2.0)

| Fitur | Deskripsi | Manfaat |
|-------|-----------|---------|
| **Jumlah Appointment** | Kolom baru di form driver dan database | Analisis marketing effectiveness per kendaraan |
| **Performance Insight Modal** | Tampilan pop-up setelah submit klaim | Driver tahu performa kendaraannya langsung |
| **Kompresi Gambar Client-Side** | Kompresi foto di browser sebelum upload | Menghemat bandwidth dan penyimpanan, mencegah error 413 |
| **Endpoint API /api/get-performance** | Analisis performa 30 hari terakhir | Basis untuk dashboard dan insight |
| **AJAX Submit** | Submit form tanpa reload halaman | UX lebih mulus, feedback real-time |
| **Fix 413 Entity Too Large** | Limit upload 16MB | Mendukung foto resolusi tinggi dari iPhone |
| **Daily Summary Async** | Rekap harian di background | Tidak blocking proses utama |
| **Activity Logging** | Log semua aktivitas admin/driver | Audit trail lengkap |

---

## 🛠️ Tumpukan Teknologi

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| **Backend** | Python (Flask) | 3.9+ |
| **WSGI Server** | Gunicorn | 20.1.0 |
| **Database** | MariaDB | 10.11 |
| **Infrastructure** | Docker & Docker Compose | Latest |
| **Reporting** | fpdf2 | 2.7.8 |
| **ML/Analytics** | scikit-learn, numpy, pandas | Latest |
| **Frontend** | HTML, CSS, Jinja2 Templates | - |
| **PWA Support** | manifest.json, sw.js | - |
| **Image Compression** | browser-image-compression (CDN) | 2.0.1 |

---

## 🚀 Memulai (Instalasi)

### Prasyarat
- **Docker** & **Docker Compose** terpasang.
- Port **5001** (web) dan **3307** (db) tersedia (bisa diubah di docker-compose.yml).

### Langkah Instalasi
1. **Clone Repository**
   ```bash
   git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
   cd bpf-bbm-system
   ```

2. **Jalankan dengan Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Akses Aplikasi**
   - Buka browser: `http://localhost:5001`
   - **Driver**: `/driver`
   - **Admin**: `/admin`

4. **Hentikan Aplikasi**
   ```bash
   docker-compose down
   ```

### Konfigurasi Environment (Opsional)
Buat file `.env` untuk mengubah pengaturan default:
```env
DB_HOST=db
DB_USER=bpf_user
DB_PASSWORD=bpf_pass
DB_NAME=bpf_asset_system
DB_POOL_SIZE=10
SECRET_KEY=your_secret_key_here
```

---

## 📖 Panduan Penggunaan

### Untuk Driver
1. **Akses** `http://[server-ip]:5001/driver`
2. **Isi Form**:
   - Data kendaraan & driver
   - Pilih **SPBU Rekanan** atau **Non-Rekanan** (akan memunculkan field berbeda)
   - Upload foto ODO, Struk, dan Dispenser (jika non-rekanan)
   - **Isi Jumlah Appointment Marketing** (0 jika tidak ada)
3. **Submit Klaim**:
   - Foto akan dikompresi otomatis
   - Setelah submit, akan muncul **Performance Insight Modal** dengan analisis 30 hari terakhir
4. **Tunggu Verifikasi** oleh admin/finance.

### Untuk Admin / Finance
1. **Akses** `http://[server-ip]:5001/admin`
2. **Dashboard** menampilkan daftar klaim **Pending** dan **Modified**.
3. **Periksa Bukti**:
   - Klik foto untuk memperbesar
   - Cek kesesuaian ODO, nominal, dan waktu
4. **Tindakan**:
   - **Verifikasi**: Setujui klaim, upload bukti MyPertamina jika perlu.
   - **Error MyPertamina**: Centang opsi error → sistem buat kronologis otomatis.
   - **Modifikasi**: Edit data jika ada kesalahan input (contoh: salah nominal).
5. **Rekap & Report**:
   - Buka `/admin/rekap` untuk lihat semua data terverifikasi.
   - Filter berdasarkan tanggal, nopol, atau driver.
   - **Generate PDF Rekap**: Dengan tanda tangan Finance & Branch Manager.
6. **Lihat Analitik**:
   - Buka `/admin/analytics` untuk dashboard performa kendaraan.

---

## 📁 Struktur Proyek

```
bpf-bbm-system/
├── app.py                     # Aplikasi utama Flask (dengan ML, PDF, API)
├── Dockerfile                 # Multi-stage build untuk production
├── docker-compose.yml         # Orchestration (web + db)
├── requirements.txt           # Dependensi Python (Flask, sklearn, fpdf, dll)
├── init.sql                   # Skrip inisialisasi database (schema + seed data)
├── manifest.json              # Konfigurasi Progressive Web App (PWA)
├── sw.js                      # Service Worker untuk PWA (caching offline)
├── generate_icon.py           # Skrip generate icon PWA
├── .gitignore                 # File yang diabaikan Git
├── templates/                 # Template HTML (Jinja2)
│   ├── driver.html            # Form input driver (dengan AJAX + compression)
│   ├── admin.html             # Dashboard verifikasi admin
│   ├── riwayat.html           # Riwayat transaksi terverifikasi
│   ├── rekap.html             # Filter dan rekap data
│   ├── analytics.html         # Dashboard performa kendaraan
│   └── settings.html          # Manajemen master data (vehicle, bbm, limits)
├── static/                    # File statis (CSS, JS, gambar)
├── uploads/                   # Direktori penyimpanan foto bukti (auto-created)
└── reports/                   # Direktori penyimpanan PDF report (auto-created)
```

---

## 🔒 Keamanan & Audit

| Aspek | Implementasi | Status |
|-------|--------------|--------|
| **SQL Injection** | Parameterized query (`cursor.execute(... , params)`) | ✅ Terlindungi |
| **File Upload** | Validasi ekstensi dan penyimpanan dengan nama unik | ✅ Terlindungi |
| **CSRF** | Belum diimplementasikan | ⚠️ Perlu ditambahkan |
| **Rate Limiting** | Belum diimplementasikan | ⚠️ Perlu ditambahkan |
| **HTTPS** | Bergantung pada reverse proxy (NGINX) | ⚠️ Perlu konfigurasi |
| **Secret Key** | Menggunakan environment variable di production | ✅ Terlindungi |
| **Connection Pooling** | MySQLConnectionPool dengan pool_size=10 | ✅ Performa & Stabil |
| **Error Handling** | Try-except dengan logging | ✅ Terlindungi |
| **Activity Log** | Semua aksi admin/driver tercatat di `activity_logs` | ✅ Audit Trail |

**Rekomendasi Keamanan Tambahan:**
- Gunakan **HTTPS** dengan reverse proxy (NGINX) + SSL/TLS.
- Tambahkan **CSRF token** pada setiap form.
- Implementasikan **rate limiting** per IP untuk endpoint publik.
- Lakukan **regular backup** database dan file upload.

---

## 🤝 Kontribusi

Kontribusi dari tim internal sangat diterima untuk pengembangan lebih lanjut. Untuk berkontribusi:

1. **Fork** repositori ini.
2. Buat **branch** fitur baru:
   ```bash
   git checkout -b fitur-keren
   ```
3. **Commit** perubahan Anda:
   ```bash
   git commit -m 'Menambahkan fitur keren'
   ```
4. **Push** ke branch:
   ```bash
   git push origin fitur-keren
   ```
5. Buat **Pull Request** untuk ditinjau tim IT.

### Panduan Coding
- Ikuti **PEP 8** untuk kode Python.
- Gunakan **parameterized query** untuk semua operasi database.
- Tambahkan **docstring** pada fungsi baru.
- Uji di lingkungan **development** sebelum push ke production.

---

## 📄 Lisensi

Proyek ini adalah hak milik **PT. Bestprofit** dan digunakan untuk keperluan internal perusahaan. Penyebaran atau penggunaan di luar lingkungan internal tanpa izin tertulis dilarang.

© 2026 PT. Bestprofit Surabaya. All Rights Reserved.

---

## 📞 Kontak & Dukungan

Untuk pertanyaan, saran, atau laporan masalah:
- 📧 **Email**: it2.sby@bestprofit-futures.co.id
- 💬 **Internal**: Hubungi Tim IT PT. Bestprofit Surabaya
- 🐛 **Issue**: Laporkan melalui GitHub Issues (internal)

---

**Dibuat dengan ❤️ oleh Tim IT PT. Bestprofit Surabaya**

---

## 📸 Screenshot (Contoh)

<img width="501" height="618" alt="image" src="https://github.com/user-attachments/assets/9fb6362b-fae2-404b-9455-f66335c9514f" />
<img width="839" height="346" alt="image" src="https://github.com/user-attachments/assets/c3314673-2f34-45a7-b943-ceb72dd6cf78" />
<img width="1354" height="283" alt="image" src="https://github.com/user-attachments/assets/fdff4bc2-3429-4752-904d-916d6bb1a8a1" />


---

## 🔄 Changelog

### v2.0 (30 Juni 2026)
- ✅ Tambahan kolom `jumlah_appointment` di database dan form driver
- ✅ Endpoint `/api/get-performance` untuk analitik 30 hari
- ✅ Kompresi gambar client-side dengan browser-image-compression
- ✅ AJAX submit dengan modal insight real-time
- ✅ Fix error 413 (upload limit 16MB)
- ✅ Perbaikan endpoint duplikat dan error di `/api/get-feedback`
- ✅ Update README dengan fitur terbaru

### v1.0 (24 Juni 2026)
- ✅ Initial release dengan fitur core (driver form, admin verifikasi, PDF report)
- ✅ PWA support (manifest.json, sw.js)
- ✅ ML Anomaly Detection dengan Isolation Forest
- ✅ Auto-kronologis untuk error MyPertamina
- ✅ Docker deployment dengan Gunicorn
```

---

## 📋 Catatan Penting untuk Tim IT

| Hal | Status | Tindakan |
|-----|--------|----------|
| **Hapus file `__pycache__` dari repo** | ❌ | Tambahkan ke `.gitignore` dan hapus dari tracking |
| **Gunakan `.env` untuk credential** | ⚠️ | Buat template `.env.example` |
| **Backup reguler** | ⚠️ | Buat cron job backup DB dan uploads |
| **HTTPS** | ⚠️ | Konfigurasi reverse proxy dengan SSL |
| **Testing** | ⚠️ | Buat test suite untuk endpoint kritis |

---

Jika ada pertanyaan atau perlu penyesuaian, silakan hubungi Tim IT. ✅
