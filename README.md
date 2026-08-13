# 🏢 BPF WorkHub v2.21.0 (SPA Vue 3 penuh — 100% Vue)

**Sistem Manajemen Armada, Klaim BBM, Kasbon, Log Perjalanan, Appointment & Air Minum**  
**PT. Bestprofit Futures - Surabaya**

---

Sistem end-to-end untuk pencatatan, verifikasi, persetujuan, pencairan dana, pengarsipan klaim BBM, **pengajuan kasbon dengan kode unik**, dan log perjalanan harian (logsheet) dengan workflow GA → Finance → Archive. Dilengkapi **sistem appointment canggih** (Marketing → Chief Driver → Log Perjalanan), deteksi anomali Machine Learning, GPS tracking, **watermark foto otomatis**, PIN security, **session-based login & role-based access**, **CSRF protection**, **notifikasi real-time**, import Excel, audit trail, Chart.js visualization, **PWA offline-first**, dan **WebSocket real-time**.

---

## 🆕 Fitur Terbaru v2.21.0 — Keamanan, Backup, Konsolidasi Cabang, UI/UX

| Fitur | Deskripsi |
|-------|-----------|
| **🔐 Security headers lengkap** | CSP ketat (`script-src 'self'`, tanpa inline/eval) + X-Frame-Options + Referrer-Policy + Permissions-Policy — SPA terverifikasi tetap jalan, 0 error konsol |
| **🗄️ Backup DB otomatis** | Service `backup` di compose: dump semua database (master + tiap cabang) tiap 03:00 WIB, retensi 30 hari, status `last-backup.txt` |
| **📊 Konsolidasi lintas cabang** | `GET /api/branches/consolidated(-pdf/-excel)` — statistik + transaksi terbaru dari SEMUA DB cabang dalam satu PDF/Excel resmi; tombol 🧮 di dashboard Admin |
| **🏥 Health check** | `GET /api/health` — DB, Redis, pool, opsi per-cabang (`?branches=1`); access log JSON terstruktur per request |
| **🖥️ UI/UX** | LoadingState/EmptyState/ErrorState reusable, pagination Audit Log & Rekap, export Excel antrean, error boundary global, aksesibilitas |
| **🧪 Test** | 208 pytest (9 baru) + 82 Vitest |

---

## 🆕 Fitur Terbaru v2.20.2 — Filter Audit, PDF Ringkasan Cabang, Seed Demo per Cabang

| Fitur | Deskripsi |
|-------|-----------|
| **🗂️ Filter Cabang (Audit)** | `/app/logs` punya dropdown cabang — "Cabang aktif" atau cabang spesifik; `activity_logs.branch_code` jadi sumber filter |
| **🖨️ PDF Ringkasan per Cabang** | `GET /api/branches/report-pdf` — laporan resmi per cabang (transaksi, kunjungan, user) dengan kop identitas cabang; tombol di `/app/dashboard` |
| **🧪 Seed demo per cabang** | Admin tanam rute + transaksi demo langsung ke DB cabang mana pun (tombol ✨ Demo di `/app/settings`); idempoten; audit mencatat cabang target |
| **🧪 Test** | 199 pytest + 82 Vitest |

---

## 🆕 Fitur Terbaru v2.20.1 — Akun Cabang, Ringkasan Cabang, Audit Bertanda Cabang

| Fitur | Deskripsi |
|-------|-----------|
| **👥 Akun khusus cabang** | Akun dari Buat Akun Sekaligus otomatis memakai `branch_code` cabang aktif — contoh: `bagus` (driver) & `dewi` (marketing) login langsung masuk data cabang MLG |
| **📊 Ringkasan Cabang (Admin)** | `/app/dashboard` menampilkan transaksi, kunjungan hari ini & user per cabang (`GET /api/branches/stats`) |
| **🧾 Audit bertanda cabang** | `activity_logs.branch_code` — setiap aktivitas tercatat dengan kode cabang asal; ditampilkan di `/app/logs` |
| **🧪 Test** | 197 pytest (3 baru) + 82 Vitest |

---

## 🆕 Fitur Terbaru v2.20.0 — Multi-Cabang (Satu Instalasi, Banyak Cabang)

| Fitur | Deskripsi |
|-------|-----------|
| **🏢 Multi-cabang** | Setiap cabang punya **database sendiri** (isolasi data penuh); Admin daftar cabang di `/app/settings`, DB dibuat & skemanya disalin otomatis; login men-scope ke DB cabang (`users.branch_code`); Admin bisa **ganti cabang aktif** langsung dari UI |
| **📇 Identitas cabang diperluas** | 6 variabel (nama, subjudul, sistem, versi, **alamat**, **telp**) — muncul di kop PDF, login, sidebar & watermark |
| **🚛 PWA driver terverifikasi** | Login `guruh`/`akhad`/`wicak` → kunjungan hari ini tampil, 4 tab jalan, konsol 0 error |
| **🧪 Test** | 194 pytest (10 baru) + 82 Vitest |

> **Catatan penyiapan multi-cabang:** user DB aplikasi perlu hak pada pola nama database cabang, mis. `GRANT ALL PRIVILEGES ON \`bpf\_%\`.* TO 'bpf_user'@'%'` — jalankan sekali sebagai root DB.

---

## 🆕 Fitur Terbaru v2.19.2 — Akun Rapi, Data Demo Admin, Multi-Cabang

| Fitur | Deskripsi |
|-------|-----------|
| **🔤 Nama akun driver rapi** | Username huruf kecil tanpa spasi (WICAK → `wicak`) + nama title-case; 7 akun existing di-migrasi via `scripts/tidy_driver_accounts.py` (idempoten, `--dry-run`) |
| **🧪 Data demo dikelola Admin** | `/app/settings`: buat ✨ & bersihkan 🧹 data demo (20 rute appointment `DEMO-*` + transaksi dummy) — data asli aman, endpoint `GET/POST /api/demo/{status,seed,clean}` |
| **🏢 Identitas perusahaan dinamis (multi-cabang)** | `company_name`, `company_subtitle`, `system_name`, `system_version` bisa diubah Admin — otomatis dipakai PDF, login, sidebar, judul tab & watermark foto (`GET/PUT /api/system-config/identity`) |
| **🧪 Test** | 184 pytest (9 baru) + 82 Vitest + verifikasi browser nyata |

---

## 🆕 Fitur Terbaru v2.19.1 — Desain Ulang PDF Resmi

| Fitur | Deskripsi |
|-------|-----------|
| **📄 PDF generator compact & resmi** | Palet monokrom (hitam/abu/putih) tanpa aksen biru/hijau/merah di semua laporan: Rekap BBM, Laporan Pelamar, Laporan Aset, Tanda Terima Air Minum, Log Perjalanan & laporan transaksi — kop surat + garis tegas, 1 halaman untuk laporan compact |
| **🧪 Test** | 175 pytest (4 PDF baru) — semua hijau, render terverifikasi dari image live |

---

## 🆕 Fitur Terbaru v2.19.0 — Debug Driver, Akun Massal, Rute Manual

| Fitur | Deskripsi |
|-------|-----------|
| **🐛 Tab Trip PWA driver diperbaiki** | Konten tab Trip sebelumnya bocor ke semua tab (fragment root membuat `v-show` tidak bekerja) — kini 4 tab terisolasi bersih |
| **🐛 Jendela notifikasi driver diperbaiki** | Panel notifikasi yang selalu menutupi layar & tak bisa ditutup kini hanya muncul saat dibuka (✕/Esc/backdrop berfungsi) |
| **🐛 Log server dibersihkan** | `log_activity_async(0, ...)` gagal FK `activity_logs.transaction_id` (spam 1452) — kini `tx_id 0` → NULL |
| **👥 Buat Akun Sekaligus (admin)** | Tombol di `/app/settings`: buat akun login (PIN 123456) untuk **semua driver aktif** & **semua user di dropdown marketing** yang belum punya akun — idempoten, audit log |
| **🖐️ Atur Rute Manual (Chief Driver)** | Mode manual di board Chief Driver: tentukan sendiri driver + no. urut kunjungan per appointment (otomatis ⚡ tetap tersedia) — endpoint khusus role `chief_driver` (GA/Admin → 403) |
| **🗺️ Data demo rute diperkaya** | 20 appointment demo (script `scripts/seed_demo_routes.py`): Surabaya dalam kota & sekitarnya (Sidoarjo, Gresik, Mojokerto, Lamongan) + luar kota (Madura, Jember, Probolinggo, Pasuruan) dengan koordinat langsung |
| **🧪 Test** | 171 pytest (11 baru) + 82 Vitest + verifikasi browser nyata (tab, notifikasi, rute manual, konsol bersih) |

---

## 🆕 Fitur Terbaru v2.18.0 — Aset & Pemeliharaan (GA)

| Fitur | Deskripsi |
|-------|-----------|
| **🔧 Halaman Aset `/app/assets`** | Pemeliharaan **15 unit AC kantor** + **8 kendaraan asli** (Innova B 1126 DFC + 7 Avanza) + **12 komponen** — role GA/Admin (migrasi total dari bpf-asset-system/Streamlit) |
| **❄️ Log servis AC** | Parameter teknikal (ampere, tekanan, delta T) → **health score otomatis 0–100**, biaya sparepart, jadwal servis berikutnya |
| **🚗 Log servis kendaraan** | Per komponen (odometer, umur pakai km/bulan vs standar master, biaya, montir) — terhubung kendaraan BBM |
| **📋 Rekomendasi otomatis** | Aturan (bukan ML berat): AC > 90 hari tanpa servis / health rendah; komponen melewati umur pakai → prioritas Kritis/Tinggi/Sedang + tandai selesai |
| **📄 Laporan PDF berlogo BPF** | Laporan AC & kendaraan + TTD General Affairs |
| **🧪 Test** | 160 pytest (9 baru: `test_assets.py`) + verifikasi browser 8/8 + gladi resik 20/20 + 13/13 + 8/8 + 12/12 |

---

## ✨ Fitur Sebelumnya — v2.17 Migrasi Google Sheet + Dropdown User

| Fitur | Deskripsi |
|-------|-----------|
| **🗄️ Data dari Google Sheet** | **914 riwayat pelamar** dari Google Spreadsheet lama dipindahkan ke database internal (DB di-reset — kini **bersih, hanya data Google Sheet**): kehadiran H1–H4 & tanggal, status mengikuti tahap terjauh, Pulang → `resigned` dengan alasan |
| **🔽 Kolom User = dropdown** | Form pelamar & edit Receptionist memakai dropdown dari tabel `applicant_user_options` — **diatur Receptionist** lewat tombol **⚙️ Kelola User** (tambah / aktif-nonaktif / hapus, audit log) |
| **📥 Migrasi terotomasi** | `scripts/migrate_applicants_sheet.py` — baca CSV ekspor sheet, normalisasi spasi, isi `applicants` + `applicant_attendance` |

---

## ✨ Fitur Sebelumnya — Sistem Pelamar Kerja (v2.16, menggantikan Google Form)

| Fitur | Deskripsi |
|-------|-----------|
| **📝 Form publik `/app/apply`** | Pelamar kerja mengisi Nama Lengkap, Pendidikan, No. HP, UPLINE, User, Posisi — **tanggal & jam interview otomatis dari timestamp submit** + No. Registrasi `PLM-*` (tanpa login, anti-spam per IP) |
| **🪪 Receptionist `/app/receptionist`** | Verifikator & pengelola data: **filter tanggal/UPLINE/User/status + search**, **✏️ edit** kesalahan input, ✅ verifikasi, 🗑 hapus, **kehadiran interview + 4 hari training** (I·H1–H4), **🚪 mengundurkan diri dengan alasan WAJIB** (bila sudah pernah hadir), 🏁 lulus / ✕ tolak |
| **📄 Laporan PDF resmi berlogo BPF** | Per tahap (interview / training H1–H4) + rentang tanggal + filter UPLINE/User + TTD Receptionist |
| **🎯 Traineer `/app/traineer`** | Pantau kehadiran orang yang direkrutnya — **scope UPLINE sendiri** otomatis (nama/username), search + filter, chip kehadiran, statistik rekrutan |
| **🔐 Keamanan** | Role baru `receptionist`/`traineer`, kontrol akses per endpoint (403), audit trail lengkap, CSRF aktif |

---

## 📜 Riwayat Versi Sebelumnya

> Catatan fitur dari rilis-rilis lama dipertahankan sebagai dokumentasi sejarah. Fitur terbaru selalu ada di bagian atas dokumen ini.

### 🆕 Fitur Terbaru v2.15.0 — Rute Canggih + Jam Kunjungan (masukan Marketing)

| Fitur | Deskripsi |
|-------|-----------|
| **⏰ Jam kunjungan bebas** | Marketing tetap memilih Sesi 1/2, lalu menentukan jam spesifik kunjungan dalam rentang sesi (Sesi 1: 08.00–12.59, Sesi 2: 13.00–17.59) — default jam mulai sesi |
| **📍 Geocoding gratis** | Alamat di-resolve ke koordinat (lat/lng) via Nominatim/OpenStreetMap dengan cache DB — tanpa API key, aman rate-limit |
| **⚡ Atur Rute Otomatis** | Tombol di board Chief Driver: algoritma membagi appointment supaya tiap driver mendapat rute **searah** & **urut sesuai jam** (VRPTW heuristic: greedy insertion + load balance + cek waktu tempuh) — estimasi jarak, liter & biaya BBM ikut dihitung |
| **✅ Terapkan Rute** | Preview rute per driver (urutan + jam + km + estimasi BBM) → terapkan: assignment + nomor urut kunjungan + notifikasi ringkas ke driver; penugasan manual tetap dihormati |
| **🗺️ Output** | Board Chief Driver & daftar Marketing menampilkan jam kunjungan; nomor urut rute (#1, #2…) per driver; PWA driver menerima notifikasi rute baru |
| **🧪 Test** | 139 pytest (33 baru: `test_route_optimizer.py`, `test_geocode.py`, validasi jam) — semua hijau |

> ⚙️ **Konfigurasi opsional**: titik awal perjalanan = **Gedung Graha Bukopin, Jl. Panglima Besar Sudirman 10-18** (`DEPOT_LAT=-7.2656732`, `DEPOT_LNG=112.7449129` di docker-compose); matikan geocoding via `GEOCODE_ENABLED=0`; estimasi BBM default 12 km/liter & Rp 10.000/liter (bisa disesuaikan di `modules/route_optimizer.py`).

---

### 🆕 Fitur Terbaru v2.9.0 — Bersih-Bersih Kode, Panduan Baru, Server Efisien

| Fitur | Deskripsi |
|-------|-----------|
| **🧹 Kode mati dibuang** | Endpoint aksi klasik dihapus dari `routes_admin.py` (SPA sudah punya `/api/queue/*` & `/api/trips/*`); `sw.js` & `manifest.json` root dihapus; daftar CSRF-exempt dibersihkan |
| **🔒 Akun OB generik dinonaktifkan** | `ob`/Office Boy nonaktif (tidak bisa login) — hanya `ob1` Faisol, `ob2` Febri, `ob3` Edwin |
| **⚡ Dashboard GA auto-refresh** | Antrean klaim langsung ter-refresh saat klaim baru masuk (realtime `new_claim`) — tanpa muat ulang halaman |
| **📖 USER_GUIDE ditulis ulang** | Struktur rapi per peran (OB, Driver, GA, Finance, Marketing, Chief Driver, Admin) — bahasa humanis, mudah dipahami orang awam |
| **🧹 Server & Docker efisien** | Prune volume/image/cache → **1,7 GB+ dibebaskan** |
| **🧪 Test** | 82 Vitest + 97 pytest + E2E produksi |

---

### 🆕 Fitur Terbaru v2.8.0 — Dashboard Khusus GA + Nama OB Asli

| Fitur | Deskripsi |
|-------|-----------|
| **🧾 Dashboard GA sendiri** | GA login → `/app/ga` (terpisah dari admin) — antrean klaim, kasbon, laporan perjalanan, aksi cepat |
| **✅ Approve / ✕ Tolak klaim** | Langsung dari dashboard GA — alasan tolak wajib (audit trail) |
| **🛡 Verifikasi anomali ML** | Klaim ber-flag ⚠️ diverifikasi di dashboard GA (modal konfirmasi foto bukti) — tanpa harus ke Dashboard Admin |
| **👤 Nama OB asli** | `ob1`=Faisol, `ob2`=Febri, `ob3`=Edwin (PIN 123456) — tampil di PDF & notifikasi |
| **🛡 Kontrol akses** | GA tak bisa buka `/app/dashboard` & rekap finance (403); admin bisa buka semua dashboard |
| **🧪 Test** | 82 Vitest + 97 pytest + E2E produksi |

---

### 🆕 Fitur Terbaru v2.7.0 — Dashboard Khusus Finance + Rekap Air Minum

| Fitur | Deskripsi |
|-------|-----------|
| **💰 Dashboard Finance sendiri** | Finance login → `/app/finance` (terpisah dari admin/GA) — menu khusus + ringkasan pekerjaan |
| **📊 Rekap air minum** | Kartu statistik, antrean verifikasi, ringkasan per OB, per jenis & merk, filter tanggal, **Export CSV** (Excel-ready) |
| **💵 Kasbon menunggu Finance** | Jumlah + nominal kasbon `GA_APPROVED` & LPJ `LPJ_SUBMITTED` di dashboard |
| **👥 Beberapa akun OB** | Satu akun per orang (ob1/ob2/ob3…) — tiap OB hanya melihat pengajuannya sendiri |
| **🛡 Kontrol akses rekap** | Rekap hanya Finance/Admin (OB & GA → 403); query dibatasi rentang tanggal + LIMIT |
| **🧪 Test** | 76 Vitest + 97 pytest + E2E produksi |

---

### 🆕 Fitur Terbaru v2.6.0 — Tanda Terima Pembelian Air Minum

| Fitur | Deskripsi |
|-------|-----------|
| **💧 Role OB baru** | Halaman `/app/water`: OB mengisi tanggal + item multi-baris (tipe/merk/satuan/kuantitas) + **2 foto timestamp wajib** (sebelum & sesudah diisi) |
| **🏷️ Master merk oleh Finance** | Tipe (Gelas/Botol/Galon) + merk dikelola Finance di halaman yang sama → dropdown untuk OB |
| **✅ Verifikasi Finance** | Approve (remark wajib + note opsional) atau tolak (alasan) |
| **📄 PDF Tanda Terima TTD** | PDF `WTR-…` berisi tabel item, remark/note, TTD **Finance (menyerahkan) & GA (menerima)** — nama di-set admin di `/app/settings`, plus lampiran 2 foto |
| **🛡 Kontrol akses** | OB hanya melihat pengajuannya sendiri; verifikasi/master khusus Finance/admin; audit trail `water_*`; tanpa sesi → 401 |
| **🧪 Test** | 71 Vitest + 94 pytest (`tests/test_water.py` + `WaterView.test.js` + E2E produksi) |

---

### 🆕 Fitur Terbaru v2.5.0 — Pensiun Total Antarmuka Klasik

| Fitur | Deskripsi |
|-------|-----------|
| **🚮 Halaman klasik dihapus** | `templates/*.html`, `static/js/*`, `static/css/*`, `archive.js` dihapus dari repo — 100% SPA Vue 3 (halaman lama kini redirect ke `/app/*`) |
| **🔗 Redirect lengkap** | `/login` `/admin` `/admin/trips` `/admin/rekap` `/admin/analytics` `/admin/logs` `/admin/users` `/admin/settings` `/marketing` `/chief-driver` `/driver` → halaman SPA sesuai role |
| **🚫 Jalur legacy ditutup** | Endpoint `?driver=` anonim (cash, notifications, appointments, `/driver`, `/submit-trip`) kini **wajib sesi login PIN** → 401 tanpa sesi (anti impersonasi/IDOR) |
| **🔑 Reset PIN Massal Driver** | Tombol di `/app/settings` → `POST /api/drivers/pin-reset` — seluruh akun driver di-reset ke **123456** (audit trail) |
| **🛡 CSRF diperketat** | Endpoint driver (submit-trip, cash, driver-complete) tak lagi dikecualikan dari proteksi CSRF |
| **🧪 Test** | 67 Vitest + 87 pytest (`resolve_driver_scope` + sesi driver) |

> ✅ **Migrasi Vue selesai total (v2.5)** — semua halaman (back-office + driver PWA) adalah SPA Vue 3. Halaman klasik **dihapus dari repo**; endpoint lama hanya redirect, dan jalur anonim `?driver=` **diblokir** — driver wajib login PIN (role `driver` dibuat via `/app/users`, PIN massal 123456 via `/app/settings`).

---

### 🆕 Fitur Terbaru v2.4.0 — Paritas SPA Lengkap (Fase 1 Migrasi Vue)

| Fitur | Deskripsi |
|-------|-----------|
| **🛡 Verifikasi anomali di SPA** | Transaksi ber-flag ML diverifikasi penuh dari antrean GA (`🛡 Verifikasi` → konfirmasi + foto MyPertamina) — tanpa pindah ke Dashboard Klasik |
| **🚛 Board Chief Driver lengkap** | Saran driver default per sesi, override area 🌍, ganti/batal tugas, ✅ selesai + hasil kunjungan wajib, 🎯 ubah hasil, ringkasan & filter per marketing anggota, export Excel |
| **📣 Marketing Hub lengkap** | ✏️ Edit & ✕ Batal appointment, saran anggota tim, preview deteksi area 📍, kolom hasil kunjungan |
| **🚫 Tautan klasik dihapus** | SPA tidak lagi menaut ke halaman klasik back-office (admin/ga/trips/rekap/analytics) — semuanya selesai dari SPA |
| **🧪 56 Vitest** | AdminDashboard +2, ChiefDriver 8 test (board lengkap), Marketing +2 |

### 🆕 Fitur Terbaru v2.4.0 (Fase 2) — Driver PWA di Vue + Login PIN

| Fitur | Deskripsi |
|-------|-----------|
| **🔐 Login PIN driver** | Role baru `driver` di Users; driver wajib login PIN sebelum submit; identitas sesi dipaksa di semua endpoint (anti impersonasi/IDOR); `/driver` → redirect `/app/driver` |
| **📱 Driver PWA Vue** | `/app/driver`: 4 tab (⛽ BBM · 💰 Kasbon · 🗺️ Trip · 📊 Rapor), foto watermark, GPS satu-klik, panel appointment, hasil kunjungan 🏁 |
| **🔄 Offline-first penuh** | IndexedDB 3 antrean (BBM/LPJ/Trip) + sinkronisasi otomatis saat online & tiap 30 detik + badge antrean |
| **🔔 Notifikasi real-time** | Bell + panel + toast via Socket.IO room per driver |
| **🧪 66 Vitest + 84 pytest** | Test store driver, shell 4 tab, guard role driver, sesi driver |

> ✅ **Migrasi Vue selesai total** — semua halaman (back-office + driver PWA) kini SPA Vue 3. Halaman klasik lama tetap ada di repo sebagai referensi & jalur legacy (endpoint dengan `?driver=` masih diterima).

---

### 🆕 Fitur Terbaru v2.2.3 — Audit Keamanan & Verifikasi Mendalam

| Fitur | Deskripsi |
|-------|-----------|
| **🔐 5 celah keamanan ditutup** | Upload file (path traversal + stored XSS), SECRET_KEY publik → `.env` (gitignored), brute-force verify-pin → rate limit, IDOR cash/delete → ownership check, header nosniff |
| **🔍 Modal Detail Transaksi** | 👁 Detail di antrean: foto bukti, cross-check (health score, flag, budget), riwayat + aksi unverify/delete |
| **🧪 47 Vitest + 77 pytest** | Test keamanan upload (9) + anti-spoofing IP (5) + rate limit Redis (7) + aksi verify/edit |

### 🆕 Fitur Terbaru v2.2.2 — Antrean Kerja di SPA

| Fitur | Deskripsi |
|-------|-----------|
| **🕐 Antrean Kerja** | Tab GA/Finance/Konfirmasi Driver di `/app/dashboard` — approve GA, tolak dengan alasan, cairkan dana, arsipkan klaim langsung dari SPA (JSON API + CSRF + pelaku dari session) |
| **🧪 39 test Vitest** | +8 test dashboard (AdminDashboard antrean & peran, MarketingDashboard form) → total 39 |
| **✅ CI hijau** | GitHub Actions lulus otomatis di setiap push |

### 🆕 Fitur Terbaru v2.2 — SPA Back-Office Lengkap

| Fitur | Deskripsi |
|-------|-----------|
| **📈 Analytics diperbaiki** | Halaman `/app/analytics` kini benar menampilkan 8+ kartu statistik (finance, GA, kasbon, fleet) + 3 grafik Chart.js + tabel Top 5 driver (memperbaiki kesalahan baca response API) |
| **📄 Rekap + PDF** | Preview & **Download PDF** langsung dari `/app/rekap` dengan rentang tanggal aktif (backend `dl=1` → attachment) |
| **📝 Audit Log + filter** | Filter aksi & peran, badge "Hari ini" & total tampil di `/app/logs` |
| **🚗 Settings lengkap** | Tambah driver, hapus driver permanen, tambah kendaraan — selain toggle aktif/nonaktif di `/app/settings` |
| **👥 Users lengkap** | Nonaktifkan/aktifkan & hapus user di `/app/users` — selain edit & reset PIN |
| **✅ CI hijau** | GitHub Actions lulus otomatis (build SPA + Vitest + pytest) |

### 🆕 Fitur Terbaru v2.1 — Kasbon di SPA, Notifikasi, PWA & CI/CD

| Fitur | Deskripsi |
|-------|-----------|
| **💵 Kasbon di SPA** | Workflow kasbon lengkap di `/app/cash` (kode unik harian, approve GA/Finance, handover, LPJ, batal/edit/hapus) — menu per role `ga/finance/admin` |
| **🔔 Notifikasi real-time SPA** | Bell + toast: GA/Finance/Admin menerima klaim & trip baru, Marketing/Chief Driver menerima pembaruan appointment (Socket.IO) |
| **📱 PWA untuk SPA** | `/app/` installable (manifest + service worker scope `/app/`, offline fallback) |
| **🤖 CI/CD** | GitHub Actions: build SPA + `npm test` (Vitest, 47 test) + `pytest tests/` (77 test) otomatis tiap push/PR |
| **🧪 Unit test frontend** | Vitest: guard router per role + auth store (login/bootstrap/logout + CSRF) |

### 🆕 Fitur v2.0 — SPA Vue 3 & Dashboard per Role

| Fitur | Deskripsi |
|-------|-----------|
| **SPA Vue 3 (Vite)** | Antarmuka admin/back-office ditulis ulang sebagai Single Page App responsif di `/app/*` (vue-router + pinia, lazy-loading) |
| **Dashboard per Role** | Setelah login, tiap peran mendapat dashboard sendiri: Admin/GA/Finance (statistik relevan), Marketing (input & ringkasan appointment), Chief Driver (board penugasan) |
| **Kontrol Akses Berlapis** | Server `role_required` + guard router SPA + menu tersembunyi per role; user tak berhak mendapat 403 (ISO/IEC 27001 · least privilege) |
| **Auth JSON baru** | `/api/auth/me`, `/api/auth/login`, `/api/auth/logout` (session + CSRF) |
| **Kepatuhan ISO** | Pemetaan ISO/IEC 27001:2022, ISO 9241-11, dan ISO 9001 di `SECURITY.md` |

> Login klasik tetap berfungsi dan kini mengarah ke SPA (`/app/dashboard` atau dashboard role masing-masing).
> Halaman klasik back-office (admin/GA/trips/rekap/analytics) sudah sepenuhnya digantikan SPA dan tidak lagi ditaut dari SPA.
> **Driver PWA** kini di `/app/driver` (Vue 3, offline-first, wajib login PIN) — URL `/driver` lama redirect ke SPA.

---

### 🆕 Fitur Terbaru v1.2 — Sistem Appointment

### 📣 Marketing Hub (`/marketing`)
| Fitur | Deskripsi |
|-------|-----------|
| **Login Role Marketing** | User marketing (mis. Icang dari Tim Yusie) login PIN → langsung ke halaman inputnya |
| **Form Multi-Input** | Input 2+ appointment sekaligus: nama calon nasabah, no. HP, alamat, catatan |
| **Nama Marketing Anggota** | 1 akun (manager) bisa input untuk banyak anggota — wajib cantumkan **siapa yang memprospek**; nama auto-register jadi daftar saran |
| **Sesi Perjalanan** | 🌅 Sesi 1 (08.30) / 🌆 Sesi 2 (14.30) — menentukan slot kunjungan |
| **Deteksi Area Otomatis** | Sistem mengenali zona alamat (Darmo, Rungkut, Sidoarjo, dsb.) |
| **Notifikasi Real-Time** | Marketing tahu saat driver ditugaskan / appointment selesai |

### 🚛 Chief Driver Command Center (`/chief-driver`)
| Fitur | Deskripsi |
|-------|-----------|
| **Board Belum Ditugaskan** | Per sesi + **saran driver otomatis** (load-balancing beban sesi) |
| **Tugas Per Driver** | Jadwal lengkap per driver: ✅ Selesai, 🔄 Ganti, ↩️ Batal Tugas, ✕ Batal Appt |
| **🌍 Ubah Area Manual** | Chief Driver bisa **override area** hasil deteksi otomatis (tombol 🌍 di kartu) |
| **Rekap Excel Harian** | Unduh laporan appointment per tanggal (openpyxl, termasuk nama marketing anggota) |
| **Board Real-Time** | Perubahan langsung tampil (Socket.IO) |

### 🔗 Integrasi Log Perjalanan
| Fitur | Deskripsi |
|-------|-----------|
| **Auto-Integrasi** | Appointment selesai → otomatis muncul di form Trip driver pada tanggal sama |
| **Muat Sekali Klik** | "📥 Muat Semua ke Rute" mengisi rute dari alamat nasabah + jam sesi |
| **Audit Jejak** | `trip_details.appointment_id` + badge "📅 APP-xxxx" di Trip Review |

---

### 🆕 Fitur Terbaru v1.1

### 🔐 Autentikasi & Keamanan (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Login / Logout** | Halaman `/login` (username + PIN), session cookie, tombol Keluar di semua halaman |
| **Role-Based Access** | 66 endpoint dilindungi `@role_required` (admin/ga/finance) — halaman di-redirect, API JSON 401/403 |
| **CSRF Protection** | Token CSRF di semua form + header `X-CSRF-Token` otomatis oleh fetch wrapper |
| **Anti Open-Redirect** | Parameter `next` pada login disanitasi & di-URL-encode |
| **GET → POST** | Semua aksi state-changing kini POST-only (approve, payout, archive, unverify, delete, trips verify) |

### 🔔 Notifikasi Driver Real-Time (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Push Live** | Driver menerima notifikasi via WebSocket saat transaksi/kasbon-nya diproses di dashboard admin |
| **Offline Catch-Up** | Notifikasi tersimpan di DB — langsung terlihat saat driver kembali online |
| **Badge Belum Dibaca** | Jumlah notifikasi unread di PWA driver |
| **API Notifikasi** | `GET /api/notifications?driver=...` + `POST /api/notifications/read` |

### 👥 Manajemen Pengguna (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **Halaman /admin/users** | Kelola akun pengguna (admin-only): tambah, update role, aktif/nonaktif |
| **Reset PIN** | Atur ulang PIN 6 digit pengguna |

### 🌙 Dark Mode (Baru)
- Toggle 🌙/☀️ di navbar **semua halaman admin** (dashboard, analytics, rekap, settings, logs, trips, GA assignments, users, login)
- Tersimpan di `localStorage` — konsisten antar halaman, tanpa flash saat load

### 🖥️ Dashboard Admin UX (Baru)
| Fitur | Deskripsi |
|-------|-----------|
| **SPA Tab Switching** | Ganti tab antrean tanpa reload (fragment HTML + history API) |
| **Sticky Context Bar** | Ringkasan "Hari Ini" selalu terlihat saat scroll |
| **Skeleton Loading** | Kartu shimmer saat berpindah tab |
| **Bulk Action GA** | "✅ Tandai Semua Dicek" — approve massal dengan konfirmasi PIN |
| **Shortcut Keyboard** | Tekan `1`–`5` untuk berpindah tab |
| **Arsip Cerdas** | Filter search/tanggal/BBM, default 7 hari terakhir, tombol "Muat Lebih Banyak" |

---

## 🚀 Fitur Utama

### 📱 Driver (PWA Offline-First)
| Fitur | Deskripsi |
|-------|-----------|
| **4-Tab Navigation** | ⛽ BBM, 💰 Kasbon, 🗺️ Trip, 📊 Rapor |
| **Offline-First** | IndexedDB + localStorage + auto-sync |
| **Notifikasi Real-Time** | 🔔 Info status transaksi & kasbon langsung di HP |
| **Watermark Otomatis** | GPS + Waktu + Nama Perusahaan di setiap foto |
| **One-Click GPS** | 📍 Lokasi + jam + KM terisi otomatis |
| **Swipe Gesture** | Geser kiri/kanan pindah tab |
| **Dark Mode** | Toggle 🌙/☀️, tersimpan di localStorage |
| **Pull-to-Refresh** | Tarik ke bawah untuk refresh data |

### 👨‍💼 GA (General Affairs)
| Fitur | Deskripsi |
|-------|-----------|
| **GA Assignments** | Assign, Tukar, Lepas kendaraan dengan audit trail |
| **Cross-Check Verifikasi** | Health Score + Flags + Budget sebelum approve |
| **Trip Review** | Popup detail rute + Print + PDF + Excel |
| **Progress Bar Kasbon** | Visual tracking per pengajuan |
| **Auto-Refresh Antrean** | Antrean baru tampil otomatis (polling 30 detik) |

### 💰 Finance
| Fitur | Deskripsi |
|-------|-----------|
| **Finance Review Panel** | Split-screen foto + data + remark |
| **ODO Edit** | Koreksi ODO dengan PIN + alasan |
| **Archive + ZIP** | Download semua bukti dalam 1 file |
| **PDF Report** | Kop surat profesional + Grid foto 2×2 |

### 📊 Analytics & Rekap
| Fitur | Deskripsi |
|-------|-----------|
| **3-Tab Analytics** | Finance, GA, Fleet + Cash chart |
| **Filter Tipe Transaksi** | Klaim Biasa vs Kasbon |
| **Display ID Konsisten** | Sama di semua tempat (Driver, Admin, Rekap) |
| **Dark-Aware Charts** | Warna chart menyesuaikan tema |

### ⚙️ Admin Settings
| Fitur | Deskripsi |
|-------|-----------|
| **Driver Management** | Toggle aktif/nonaktif + hapus (3 kolom) |
| **Fleet Kendaraan** | Tambah kendaraan mandiri (tanpa driver) |
| **User & PIN** | Reset PIN via popup 🔑 + halaman Users terpisah |
| **Multi-Fill Threshold** | Deteksi top-up BBM |

---

## 🔄 Workflow

```

DRIVER → GA Approve → Finance Payout → Driver TTD → Archive ZIP
│          │              │               │            │
└─ pending └─ verified_ga └─ os_finance   └─ archived └─ download

```

### Alur Kasbon
```

Driver 💰→ GA ✅→ Finance 💰→ GA 🤝→ Driver ⛽→ LPJ 📋→ ✅ Selesai

```

### Alur Appointment (v1.2)
```

Marketing 📣 → Chief Driver 🚛 → Driver 🗺️ → GA ✅
   │              │                │            │
   └─ input       └─ bagi driver    └─ log       └─ review trip
      nasabah +      (saran          perjalanan
      alamat +        otomatis       auto-terisi
      sesi 08.30/     per sesi/      dari alamat
      14.30 +         area +         nasabah
      nama            area bisa
      marketing       diubah manual
      anggota         🌍)

```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Architecture | **Modular** (11 route modules + service layer) |
| Auth | Session-based (PIN users) + role_required + CSRF |
| Real-Time | Flask-SocketIO + eventlet + per-driver rooms |
| Database | MariaDB 10.11 |
| ML Engine | Scikit-learn (Isolation Forest) |
| PDF | FPDF + DejaVu Sans (Unicode) |
| Excel | openpyxl |
| Charts | Chart.js 4.4 |
| Frontend | **Vue 3 + Vite** (vue-router + pinia) — SPA penuh, tidak ada halaman server-render |
| PWA | Service Worker (scope `/app/`) + IndexedDB + localStorage (offline-first driver) |
| Container | Docker + Docker Compose |
| Font | Inter (self-host, offline-friendly) + DejaVu Sans |

---

## 📦 Quick Start

```bash
git clone https://github.com/bestprofitsurabaya/bpf-workhub.git
cd bpf-workhub
docker compose up -d
```

Access

### 🌐 Akses Online (Domain DuckDNS)

Aplikasi diakses publik melalui **domain permanen** `nasbpfsby.duckdns.org` (HTTPS via nginx reverse proxy):

| Halaman | URL Online |
|---------|------------|
| **Login (semua role)** | `https://nasbpfsby.duckdns.org:5000/app/login` |
| **📣 Marketing Hub** | `https://nasbpfsby.duckdns.org:5000/app/marketing` |
| **🚛 Chief Driver** | `https://nasbpfsby.duckdns.org:5000/app/chief-driver` |
| **📝 Form Pelamar (publik)** | `https://nasbpfsby.duckdns.org:5000/app/apply` |
| **🪪 Receptionist** | `https://nasbpfsby.duckdns.org:5000/app/receptionist` |
| **🎯 Traineer** | `https://nasbpfsby.duckdns.org:5000/app/traineer` |
| **🔧 Aset & Pemeliharaan** | `https://nasbpfsby.duckdns.org:5000/app/assets` |
| **📱 Driver PWA** | `https://nasbpfsby.duckdns.org:5000/app/driver` |
| Dashboard Admin | `https://nasbpfsby.duckdns.org:5000/app/dashboard` |
| GA Assignments | `https://nasbpfsby.duckdns.org:5000/app/assignments` |
| Trips | `https://nasbpfsby.duckdns.org:5000/app/trips` |
| Users | `https://nasbpfsby.duckdns.org:5000/app/users` |

> URL lama (`/login`, `/admin`, `/driver`, `/marketing`, dst.) otomatis redirect ke halaman SPA di atas.

> ✅ **URL permanen (DuckDNS)** — tidak berubah saat server di-restart. WebSocket/notifikasi real-time aktif (nginx meneruskan header Upgrade).
> ⚠️ **Akses cadangan opsional:** Cloudflare Tunnel *quick tunnel* (URL acak `*.trycloudflare.com`) bisa diaktifkan kembali di `docker-compose.yml` — lihat `DEPLOYMENT.md` §11.

### 🖥️ Akses Lokal (Development)

| Halaman | URL | Aktor |
|---------|-----|-------|
| Login | http://localhost:5001/app/login | Semua |
| Driver PWA | http://localhost:5001/app/driver | Driver (wajib login PIN) |
| **Marketing Hub** | http://localhost:5001/app/marketing | Marketing |
| **Chief Driver** | http://localhost:5001/app/chief-driver | Chief Driver, GA |
| **Form Pelamar (publik)** | http://localhost:5001/app/apply | Tanpa login |
| **Pelamar Kerja (Receptionist)** | http://localhost:5001/app/receptionist | Receptionist, Admin |
| **Rekrutan Saya (Traineer)** | http://localhost:5001/app/traineer | Traineer |
| **Aset & Pemeliharaan** | http://localhost:5001/app/assets | GA, Admin |
| Dashboard | http://localhost:5001/app/dashboard | GA, Finance, Admin |
| GA Assignments | http://localhost:5001/app/assignments | GA |
| Rekap | http://localhost:5001/app/rekap | Finance, Admin |
| Analytics | http://localhost:5001/app/analytics | Manager, Admin |
| Trips | http://localhost:5001/app/trips | GA, Admin |
| Users | http://localhost:5001/app/users | Admin |
| Audit Log | http://localhost:5001/app/logs | Admin |
| Settings | http://localhost:5001/app/settings | Admin |

> ⚠️ **Semua halaman (termasuk Driver PWA) kini memerlukan login PIN.** URL klasik redirect ke halaman SPA di atas.

Default Credentials

| Role | Username | PIN |
|------|----------|-----|
| Admin | admin | 123456 |
| GA | ga_officer | 123456 |
| Finance | finance_officer | 123456 |
| Marketing (buat via Users) | mis. icang | 123456 (set via Users) |
| Chief Driver (buat via Users) | mis. chief_driver | 123456 (set via Users) |
| Driver (buat via Users, role Driver) | mis. rivan | 123456 (**reset massal** via `/app/settings`) |
| Receptionist (buat via Users) | mis. receptionis | 123456 (set via Users) |
| Traineer / Upline (buat via Users) | mis. traineer_a | 123456 (set via Users) |

---

## 📁 Project Structure

```
bpf-workhub/
├── app.py                          # Main entry point (auth, CSRF, SocketIO)
├── init.sql                        # Schema + data awal (termasuk tabel notifications)
├── modules/
│   ├── config.py                   # DB connection pool
│   ├── helpers.py                  # Utils + role_required decorator
│   ├── engine.py                   # ML insights & rekap
│   ├── pdf_generator.py            # PDF classes (enterprise)
│   ├── excel_generator.py          # Excel export
│   ├── realtime.py                 # SocketIO bus + per-driver rooms
│   ├── notifications.py            # Store & push notifikasi driver/marketing
│   ├── appointments_schema.py      # Migrasi tabel appointments (startup)
│   ├── routes_auth.py              # Login / logout (session, redirect per-role)
│   ├── routes_appointments.py      # Marketing & Chief Driver (halaman + API)
│   ├── routes_driver.py            # Driver & PWA routes
│   ├── routes_admin.py             # Redirect kompat + export logsheet (aksi via /api/queue/*)
│   ├── routes_reports.py           # Reports, rekap, analytics
│   ├── routes_settings.py          # Settings + /admin/users (redirect SPA)
│   ├── routes_cash.py              # Cash request & LPJ
│   ├── routes_notifications.py     # Notifikasi API
│   ├── routes_api_master.py        # Master data API
│   ├── routes_api_transactions.py  # Transactions API
│   ├── routes_api_assignments.py   # Assignments API
│   └── routes_spa.py               # Auth JSON + trips/queue/detail API + serve /app/*
├── frontend/                       # SUMBER SPA Vue 3 (Vite + vue-router + pinia)
│   └── src/
│       ├── views/                  # dashboard per role, driver/ (4 tab), view back-office
│       ├── stores/                 # auth, realtime, driverStore (IndexedDB queue + sync)
│       ├── components/             # Modal, ToastStack, NotificationBell, DriverNotifBell
│       ├── utils/                  # idb (antrean offline), gps, watermark
│       └── router/                 # guard per role
├── static/
│   ├── app/                        # Bundle SPA hasil build (dilayani di /app/*)
│   └── icon-*.png                  # Ikon PWA
├── scripts/
│   ├── tunnel-check.sh             # Periksa status URL public (online/offline)
│   ├── tunnel-url.sh               # Tampilkan URL public aktif
│   └── release.sh                  # Buat GitHub Release dari CHANGELOG
├── fonts/                          # DejaVu Sans (Unicode PDF)
├── docker-compose.yml              # Service cloudflared (opsional — nonaktif, URL via DuckDNS)
├── Dockerfile
├── README.md
├── DEPLOYMENT.md
└── USER_GUIDE.md
```

---

## 🔒 Security

| Fitur | Deskripsi |
|-------|-----------|
| **Session Login** | `/login` username+PIN, session cookie, logout |
| **Role-Based Access** | `@role_required` di 66 halaman/API (admin/ga/finance) |
| **CSRF Protection** | Token di form + header `X-CSRF-Token` (SPA); endpoint driver kini ber-CSRF penuh |
| **Anti Open-Redirect** | Validasi parameter `next` |
| **GET → POST** | Semua aksi state-changing wajib POST |
| PIN 6-Digit | GA/Finance/Admin (verifikasi ganda di aksi penting) |
| Watermark | GPS + Timestamp di foto |
| Audit Trail | 30+ action types |
| SQL Parameterized | Anti injection |
| Anti-Cache | no-store headers |

---

## 📊 Monitoring

```bash
# Status transaksi
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT status, COUNT(*) FROM transactions GROUP BY status;"

# Audit log
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT created_at, user_name, action FROM activity_logs ORDER BY id DESC LIMIT 20;"

# Cash requests
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT display_id, driver_name, total_amount, status FROM fuel_cash_requests ORDER BY id DESC;"

# Notifikasi driver
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT driver_name, type, message, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 20;"

# Appointment harian
docker exec bbm_mariadb mysql -uroot -ppassword_db bpf_asset_system \
  -e "SELECT appointment_date, sesi, status, COUNT(*) FROM appointments GROUP BY appointment_date, sesi, status ORDER BY appointment_date DESC LIMIT 20;"
```

---

## 📋 Changelog v1.2

- ✅ **Sistem Appointment**: tabel `appointments` + `marketing_teams` + `marketing_members`, role `marketing` & `chief_driver`, migrasi otomatis saat startup (`appointments_schema.py`)
- ✅ **Halaman Marketing Hub** `/marketing`: form multi-input, **nama marketing anggota (wajib, ada saran otomatis)**, sesi 08.30/14.30, deteksi area alamat otomatis, notifikasi real-time
- ✅ **Halaman Chief Driver** `/chief-driver`: board penugasan per sesi & per driver, saran driver load-balancing, **override area manual 🌍**, export Excel harian, board real-time
- ✅ **Integrasi Log Perjalanan**: appointment selesai → auto-terisi di form Trip driver + jejak `appointment_id` di Trip Review
- ✅ **Login redirect per-role**: marketing → `/marketing`, chief_driver → `/chief-driver`
- ✅ **User management**: role Marketing + Chief Driver + field Tim Marketing (auto-register `marketing_teams`)
- ✅ **Tests**: 48+ test PASS + smoke test end-to-end

## 📋 Changelog v1.1

- ✅ **Auth**: login/logout session-based + role_required (66 endpoint)
- ✅ **CSRF protection** di semua POST state-changing (exempt driver PWA)
- ✅ **Konversi GET → POST** untuk semua aksi admin state-changing
- ✅ **Notifikasi driver real-time** (SocketIO per-driver room + offline catch-up)
- ✅ **Halaman User Management** `/admin/users`
- ✅ **Dark mode** di semua halaman admin + login (localStorage, tanpa flash)
- ✅ **Dashboard UX**: SPA tab tanpa reload, sticky context bar, skeleton, bulk approve GA, shortcut keyboard 1–5, count-up
- ✅ **Arsip cerdas**: filter + default 7 hari + tombol "Muat Lebih Banyak"
- ✅ **Refactor modular JS** (12 modul) + CSS per halaman
- ✅ **Tests**: 29+ test PASS (workflow kasbon, driver context, excel generator)

---

## 👥 Roles

| Role | Akses | Default PIN |
|------|-------|-------------|
| Admin | Settings, Users, Audit Log, semua dashboard | 123456 |
| GA Officer | Approve, reject, trip review, serah terima kendaraan, kasbon, chief driver board | 123456 |
| Finance Officer | Payout, Archive, ZIP, Export, ODO Edit, kasbon | 123456 |
| Chief Driver | Command center penugasan driver appointment | 123456 |
| Receptionist | Form pelamar → verifikasi, edit, kehadiran interview & 4 hari training, status, laporan PDF | 123456 |
| Traineer / Upline | Pantau kehadiran rekrutan upline sendiri (read-only) | 123456 |
| Marketing | Input & kelola appointment prospek nasabah (1 akun bisa untuk banyak anggota tim) | 123456 |
| Driver | Submit BBM, Trip Log, Kasbon, Self-analytics, notifikasi — **wajib login PIN** (anti impersonasi) | 123456 (via Users / reset massal) |

---

## 📄 License

Internal use - PT. Bestprofit Futures Surabaya  
Version 1.2 | August 2026  
Developed & Maintained by IT BPF Surabaya
