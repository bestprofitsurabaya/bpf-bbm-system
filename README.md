BPF BBM System

**Sistem Manajemen dan Verifikasi Klaim BBM untuk Kendaraan Operasional PT. Bestprofit**

Aplikasi ini adalah solusi internal yang dirancang untuk mengatasi *trust issue* dalam pelaporan BBM. Dengan menyediakan alur verifikasi visual yang ketat, otomatisasi pembuatan kronologis, dan fitur pelaporan profesional, sistem ini memastikan transparansi dan akuntabilitas penuh atas setiap klaim BBM.

## ✨ Fitur Unggulan

### 1. Portal Driver
- **Unggah Bukti Visual Dinamis**: Proses unggah yang menyesuaikan dengan jenis SPBU (Rekanan/Non-Rekanan), mencakup:
    - Foto Odometer (sebelum & sesudah)
    - Foto Struk Fisik
    - Foto Dispenser
- **Input Data Transaksi**: Formulir terstruktur untuk mencatat volume, harga, dan detail transaksi lainnya.

### 2. Portal Admin / Finance
- **Dashboard Verifikasi Terpusat**: Satu pintu untuk menyetujui, menolak, atau meminta klarifikasi klaim.
- **Manajemen Bukti**: Kemampuan untuk mengunggah bukti tambahan dari sisi admin.
- **Penanganan Error**: Fasilitas untuk menangani dan meluruskan klaim yang bermasalah.

### 3. Auto-Kronologis
- **Otomatisasi Laporan**: Membuat teks laporan kronologis secara otomatis jika terjadi kendala seperti mutasi MyPertamina yang tidak muncul, memastikan setiap klaim tetap terdokumentasi.

### 4. Profesional Reporting
- **PDF Generator**: Menghasilkan dokumen PDF arsip yang komprehensif secara otomatis, yang menyusun:
    - Seluruh bukti foto
    - Data transaksi
    - Kronologis kejadian
- **Dokumen Detail**: Menghasilkan laporan yang rapi, profesional, dan siap untuk keperluan audit internal.

### 5. Sistem Terpadu
- **Infrastruktur Modern**: Berjalan di atas **Docker** dan **Docker Compose** untuk kemudahan deployment dan isolasi.
- **Database Relasional**: Menggunakan **MariaDB** internal untuk penyimpanan data yang aman dan persisten.

## 🛠️ Tumpukan Teknologi

| Komponen | Teknologi |
| :--- | :--- |
| **Backend** | Python (Flask) |
| **Database** | MariaDB |
| **Infrastructure** | Docker & Docker Compose |
| **Reporting** | fpdf2 (PDF Generation) |
| **Frontend** | HTML, CSS, Jinja2 Templates |
| **PWA Support** | Progressive Web App (manifest.json, sw.js) |

## 🚀 Memulai (Instalasi)

### Prasyarat
Pastikan **Docker** dan **Docker Compose** telah terpasang pada sistem Anda.

### Langkah-langkah

1.  **Clone Repository**
    ```bash
    git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
    cd bpf-bbm-system
    ```

2.  **Jalankan dengan Docker Compose**
    ```bash
    docker-compose up -d
    ```

3.  **Akses Aplikasi**
    Buka browser dan akses `http://localhost:5000`. Aplikasi siap digunakan.

4.  **Hentikan Aplikasi**
    ```bash
    docker-compose down
    ```

## 📖 Panduan Penggunaan

### Untuk Driver
1.  Login ke portal driver.
2.  Pilih jenis SPBU (Rekanan/Non-Rekanan).
3.  Unggah foto ODO, struk, dan dispenser sesuai dengan panduan.
4.  Isi data transaksi dengan lengkap.
5.  Kirim klaim untuk proses verifikasi.

### Untuk Admin / Finance
1.  Login ke portal admin.
2.  Pantau daftar klaim yang masuk pada dashboard.
3.  Periksa setiap bukti yang diunggah oleh driver.
4.  Ambil tindakan: **Setujui**, **Tolak**, atau minta klarifikasi tambahan.
5.  Gunakan fitur kronologis otomatis jika diperlukan untuk klaim yang error.
6.  Generate laporan PDF untuk keperluan arsip.

## 📁 Struktur Proyek

```
bpf-bbm-system/
├── app.py                 # Aplikasi utama Flask
├── Dockerfile             # Konfigurasi Docker image
├── docker-compose.yml     # Konfigurasi Docker Compose
├── requirements.txt       # Dependensi Python
├── init.sql               # Skrip inisialisasi database
├── manifest.json          # Konfigurasi Progressive Web App (PWA)
├── sw.js                  # Service Worker untuk PWA
├── generate_icon.py       # Skrip untuk generate icon PWA
├── templates/             # Template HTML (Jinja2)
│   ├── index.html
│   ├── driver.html
│   ├── admin.html
│   └── ...
├── static/                # File statis (CSS, JS, gambar)
└── README.md              # Dokumentasi ini
```

## 🤝 Kontribusi

Kontribusi dari tim internal sangat diterima untuk pengembangan lebih lanjut. Untuk berkontribusi:

1.  **Fork** repositori ini.
2.  Buat **branch** fitur baru (`git checkout -b fitur-keren`).
3.  **Commit** perubahan Anda (`git commit -m 'Menambahkan fitur keren'`).
4.  **Push** ke branch (`git push origin fitur-keren`).
5.  Buat **Pull Request** untuk ditinjau.

## 📄 Lisensi

Proyek ini adalah hak milik **PT. Bestprofit** dan digunakan untuk keperluan internal perusahaan. Penyebaran atau penggunaan di luar lingkungan internal tanpa izin tertulis dilarang.

## 📞 Kontak & Dukungan

Untuk pertanyaan, saran, atau laporan masalah, silakan hubungi Tim IT PT. Bestprofit Surabaya.

---

**Dibuat dengan ❤️ oleh Tim IT PT. Bestprofit Surabaya**
