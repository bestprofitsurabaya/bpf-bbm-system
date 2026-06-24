# BPF BBM System

**Sistem Manajemen dan Verifikasi Klaim BBM untuk Kendaraan Operasional PT. Bestprofit**

Aplikasi ini dirancang untuk mengatasi *trust issue* dalam pelaporan BBM dengan menyediakan alur verifikasi visual yang ketat, otomatisasi pembuatan kronologis, dan fitur pelaporan (*reporting*) profesional.

---

## 📋 Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Struktur Teknologi](#struktur-teknologi)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Struktur Proyek](#struktur-proyek)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

---

## 🚀 Fitur Utama

### 1. Portal Driver
- **Unggah bukti visual** secara dinamis berdasarkan jenis SPBU (Rekanan/Non-Rekanan):
  - Foto ODO (sebelum & sesudah)
  - Foto struk fisik
  - Foto dispenser
- **Input data transaksi** yang terstruktur

### 2. Portal Admin/Finance
- **Dashboard verifikasi satu pintu** untuk:
  - Menyetujui atau menolak klaim
  - Mengunggah bukti tambahan
  - Menangani error sistem
- **Fitur kronologis otomatis** untuk mencatat riwayat klaim

### 3. Auto-Kronologis
- Pembuatan teks laporan kronologis secara **otomatis** jika mutasi MyPertamina tidak muncul
- Memastikan transparansi dan akuntabilitas setiap klaim

### 4. Profesional Reporting
- **PDF Generator** otomatis yang menyusun:
  - Seluruh bukti foto
  - Data transaksi
  - Kronologis kejadian
- Menghasilkan dokumen arsip yang **detail dan profesional**

### 5. Sistem Terpadu
- Berjalan di atas **infrastruktur Docker**
- Menggunakan **MariaDB internal** untuk penyimpanan data yang aman dan persisten
- **Terisolasi** dan mudah dideploy

---

## 🛠️ Struktur Teknologi

| Komponen | Teknologi |
|----------|-----------|
| **Backend** | Python (Flask) |
| **Database** | MariaDB |
| **Infrastructure** | Docker & Docker Compose |
| **Reporting** | fpdf2 (PDF Generation) |
| **Frontend** | HTML, CSS, Jinja2 Templates |

---

## 🔧 Instalasi

### Prasyarat
Pastikan Anda memiliki **Docker** dan **Docker Compose** yang terpasang di server.

### Langkah-langkah

1. **Clone repositori**
   ```bash
   git clone https://github.com/bestprofitsurabaya/bpf-bbm-system.git
   cd bpf-bbm-system
   ```

2. **Jalankan dengan Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Akses aplikasi**
   - Buka browser dan akses `http://localhost:5000`
   - Aplikasi siap digunakan

4. **Hentikan aplikasi**
   ```bash
   docker-compose down
   ```

---

## 📖 Penggunaan

### Untuk Driver
1. Login ke portal driver
2. Pilih jenis SPBU (Rekanan/Non-Rekanan)
3. Unggah foto ODO, struk, dan dispenser sesuai ketentuan
4. Isi data transaksi (volume, harga, dll)
5. Kirim klaim untuk diverifikasi

### Untuk Admin/Finance
1. Login ke portal admin
2. Lihat daftar klaim yang masuk di dashboard
3. Periksa bukti-bukti yang diunggah
4. Setujui atau tolak klaim
5. Jika ada error, gunakan fitur kronologis otomatis
6. Generate PDF laporan untuk arsip

---

## 📁 Struktur Proyek

```
bpf-bbm-system/
├── app.py                 # Aplikasi utama Flask
├── Dockerfile             # Konfigurasi Docker image
├── docker-compose.yml     # Konfigurasi Docker Compose
├── requirements.txt       # Dependensi Python
├── init.sql               # Inisialisasi database
├── templates/             # Template HTML (Jinja2)
│   ├── index.html
│   ├── driver.html
│   ├── admin.html
│   └── ...
├── static/                # File statis (CSS, JS, gambar)
└── README.md              # Dokumentasi ini
```

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Untuk berkontribusi:

1. **Fork** repositori ini
2. Buat **branch** fitur baru (`git checkout -b fitur-keren`)
3. **Commit** perubahan Anda (`git commit -m 'Menambahkan fitur keren'`)
4. **Push** ke branch (`git push origin fitur-keren`)
5. Buat **Pull Request**

---

## 📄 Lisensi

Proyek ini adalah milik **PT. Bestprofit** dan digunakan untuk keperluan internal perusahaan.

---

## 📞 Kontak

Untuk pertanyaan atau dukungan, silakan hubungi tim IT PT. Bestprofit.

---

**Dibuat dengan ❤️ oleh Tim IT PT. Bestprofit Surabaya**
