cat << 'EOF' > README.md
# BPF BBM System

Sistem manajemen dan verifikasi klaim BBM untuk kendaraan operasional PT. Bestprofit. Aplikasi ini dirancang untuk mengatasi *trust issue* dalam pelaporan BBM dengan menyediakan alur verifikasi visual yang ketat, otomatisasi pembuatan kronologis, dan fitur pelaporan (*reporting*) profesional.

## Fitur Utama

- **Portal Driver:** Pengunggahan bukti visual (ODO sebelum/sesudah, struk fisik, dan foto dispenser) secara dinamis berdasarkan jenis SPBU (Rekanan/Non-Rekanan).
- **Portal Admin/Finance:** *Dashboard* verifikasi satu pintu untuk menyetujui klaim, mengunggah bukti tambahan, dan menangani *error* sistem dengan fitur kronologis otomatis.
- **Auto-Kronologis:** Pembuatan teks laporan kronologis secara otomatis jika mutasi MyPertamina tidak muncul.
- **Profesional Reporting:** *Engine* PDF otomatis yang menyusun seluruh bukti foto dan data transaksi menjadi dokumen arsip yang detail.
- **Sistem Terpadu:** Berjalan di atas infrastruktur Docker dengan MariaDB internal untuk memastikan data tersimpan aman dan persisten.

## Struktur Teknologi
- **Backend:** Python (Flask)
- **Database:** MariaDB
- **Infrastructure:** Docker & Docker Compose
- **Reporting:** fpdf2 (PDF Generation)

## Instalasi

Pastikan Anda memiliki Docker dan Docker Compose yang terpasang di *server*.

1. Clone repositori:
   ```bash
   git clone [https://github.com/bestprofitsurabaya/bpf-bbm-system.git](https://github.com/bestprofitsurabaya/bpf-bbm-system.git)
   cd bpf-bbm-system
