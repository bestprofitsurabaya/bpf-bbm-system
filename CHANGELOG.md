# 📋 Changelog

Semua perubahan penting pada **BPF WorkHub**.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/ID/1.0.0/) dan versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

---

## [2.22.1] - 2026-08-18

### 🚗 Migrasi penuh Overtime DRIVER (sheet private tanpa akses pemilik)

- **8.665 baris overtime Driver (2020–2026) berhasil dimigrasikan** dari Google Sheet via URL Google Apps Script Web App — tabel `overtime_driver` yang tadinya 0 kini penuh (100 baris kosong sheet dilewati).
- **Solusi sheet PRIVATE tanpa akun pemilik**: cukup akun Google yang SUDAH punya akses (termasuk view/read-only) membuat **script standalone** di `script.google.com` dari template `scripts/apps_script_overtime_driver.gs`, deploy sebagai Web App (*Execute as: Me*, *Who has access: Anyone*). Script dieksekusi atas nama akun itu → bisa membaca sheet private → hasil JSON publik; sheet tetap private, pemilik tidak perlu dilibatkan.
- **Parser ISO UTC → WIB (+7 jam)**: Apps Script mengirim nilai sebagai ISO 8601 UTC (`2020-12-12T07:08:54.000Z`, waktu murni `1899-12-30T11:47:56.000Z`); semua tanggal & jam dikonversi ke zona WIB sheet (`parse_iso_dt` / `parse_date_any` / `parse_time_any` / `parse_submitted_at_any`).
- **Kolom lengkap sheet Driver** kini tersimpan: `no_kendaraan`, `broker` (Nama Broker/Marketing), `manager` (Nama Manager/Team leader), `doc_url` (Merged Doc URL) — tampil di tabel dashboard & PDF laporan Driver, dan ikut dicari di filter.
- **`scripts/migrate_overtime_driver.py`** — migrasi massal idempoten (kunci `sheet_row`), menerima URL Web App / CSV / gviz, opsi `--reset`. Dipakai juga untuk sinkronisasi penuh berikutnya.
- Tombol **🔄 Refresh dari Google Sheet** di dashboard GA HR kini bekerja memakai URL Web App tersebut (`system_config.overtime_driver_sheet_url` diisi).
- **Auto-refresh saat login & logout** — data Driver otomatis disinkronkan di background setiap kali user `ga_hr`/`admin` login atau logout (fire-and-forget via thread pool, login tetap cepat; debounce 30 dtk anti-spam ke Google). Logika refresh dipindah ke `_do_refresh_driver()` yang dipakai bersama tombol manual & auto; audit log `overtime_driver_refresh` tetap tercatat.

### 🔔 Notifikasi data overtime baru

- **GA HR/Admin dapat notifikasi realtime** (bell 🔔) saat sinkronisasi sheet menemukan data Driver baru ATAU ada submit baru dari form publik OB/Security — event `overtime_new` ke room `ga_hr_board`, tersimpan di tabel `notifications` (`push_overtime_notification`).

### ✏️ Edit & hapus data overtime (dashboard)

- Tombol **✏️ Edit** & **🗑️ Hapus** di setiap baris tab Driver & OB/Security — GA HR bisa mengoreksi typo/kesalahan data langsung dari dashboard (modal edit: nama, kendaraan, tanggal, jam, keterangan, broker/manager, posisi untuk OB).
- Endpoint `PATCH/DELETE /api/overtime/<driver|ob>/<id>` (role `ga_hr`/`admin`, 404 bila tidak ada) + audit log `overtime_update` / `overtime_delete`.

### 🧹 Pembersihan data

- **13 baris Driver dengan tahun typo dikoreksi** (bukti dari baris tetangga sheet): 1921→2021, 2923→2023, 2033→2023, 2004→2024, 2029→2026 — rentang data kini wajar 2020-12-12 s/d 2026-08-30.
- **Akun demo `ga_hr_officer`** (PIN `123456`, role `ga_hr`) dibuat untuk pengujian nyata tim GA.

### 🧪 Pengujian

- **243 pytest** (17 baru: header sheet Driver, parser ISO→WIB, `normalize_driver_row`, migrasi, role-gating & debounce auto-refresh, validasi modul/kolom/posisi CRUD) + **82 Vitest** — semua hijau. SPA di-build, app di-restart, verifikasi live: login GA HR (`ga_hr_officer` → home `/app/ga-hr`), auto-refresh saat login/logout, PATCH edit (terverifikasi di DB), DELETE + 404, audit log `overtime_update`/`overtime_delete`, notifikasi tersimpan, `/api/overtime/stats` (Driver 8.665 · OB/Security 546), halaman `/app/ga-hr` HTTP 200.
- **Verifikasi browser nyata 16/16** (`frontend/scripts/verify_ga_hr_full.mjs`, Chrome via puppeteer): login GA HR → dashboard & statistik → tombol Refresh/Sumber Data/PDF → tombol ✏️/🗑️ di Driver & OB/Security → modal edit terbuka (kolom lengkap) → **simpan edit sukses (PATCH) + revert otomatis** → konfirmasi hapus muncul (dibatalkan, data aman) → bell 🔔 → **notifikasi realtime end-to-end** (form publik diisi di tab kedua → badge bell GA HR muncul) → role GA ditolak 403 → **0 error konsol, 0 data uji tersisa**.

## [2.22.0] - 2026-08-14

### ⏰ Sistem Overtime — GA HR

- **Role baru `ga_hr`** (GA HR) dengan halaman sendiri `/app/ga-hr` — akun dibuat Admin di Manajemen User (`/app/users`), menu & dashboard otomatis muncul.

### 🚗 Overtime Driver (sinkronisasi Google Sheet)

- Tabel `overtime_driver` — data ditarik dari Google Sheet read-only (diisi Google Form lama) via tombol **🔄 Refresh dari Google Sheet** di dashboard GA HR. Sinkronisasi upsert idempoten (kunci = nomor baris sheet).
- URL sumber data bisa diatur di **⚙️ Sumber Data** (modal di dashboard): CSV publik `…/gviz/tq?tqx=out:csv` ATAU URL Google Apps Script Web App (solusi untuk sheet PRIVATE — script dijalankan sebagai pemilik akun, sheet tetap aman).
- Pemetaan kolom toleran ejaan (Timestamp, Nama, Tanggal, Waktu Mulai/Selesai, Keterangan, foto) + parsing jam 12 jam (`6:29:00 PM` → `18:29`).

### 🧑‍🔧 Overtime OB & Security (migrasi penuh + form publik)

- Tabel `overtime_ob_security` — **546 baris data sheet lama dimigrasikan** (407 OB · 139 Security; nama di-normalisasi dari typo: `Faisool` → `Faisol`, dll).
- **Form publik tanpa login** di `/app/overtime-form` — dropdown **Posisi** (OB/Security) & **Nama** (sesuai data yang ada), tanggal, waktu mulai/selesai, keterangan (datalist), rate-limit anti spam 10/menit/IP.
- Pemetaan posisi sesuai konfirmasi user (14/8/2026): **Muhajir = Security**, Edwin P/Febri/Faisol = OB.

### 🔐 Keamanan & kontrol akses

- Endpoint overtime hanya untuk role `ga_hr` & `admin` (403 untuk role lain); form publik dibatasi rate-limit; audit log `overtime_submit` / `overtime_driver_refresh` / `overtime_config`.
- `users.role` ENUM diperluas (migrasi otomatis di startup), daftar role valid `/api/users/sync` diperbarui.

### 📄 Laporan PDF Overtime

- **`GET /api/overtime/report?modul=driver|ob`** → `OvertimeReportPDF` baru (kop & logo BPF, TTD GA HR) — tombol **📄 PDF** di tiap tab dashboard GA HR, mengikuti filter tanggal/posisi/nama yang aktif.

### 🧪 Pengujian

- **21 pytest baru** (`tests/test_overtime.py`): pemetaan header sheet, parsing tanggal/jam, normalisasi nama, tebak posisi, fetch CSV & JSON Apps Script, role GA HR, PDF driver & OB/Security. SPA di-build, **verifikasi browser nyata 9/9** (`frontend/scripts/verify_overtime_ui.mjs`: form publik dropdown Posisi/Nama + submit OTL-*, dashboard GA HR statistik & tab data migrasi, role GA → 403, 0 error konsol).

## [2.21.0] - 2026-08-13

### 🔐 Keamanan & Observabilitas

- **Security headers lengkap** (ISO/IEC 27001 A.8.2/A.8.7/A.8.8): `Content-Security-Policy` ketat (`script-src 'self'` — tanpa inline/eval), `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options`. Script dark-mode dipindah ke `dark-init.js` eksternal agar CSP tetap ketat — **terverifikasi: SPA berjalan normal, 0 error konsol**.
- **Rate limit** terpusat (`modules/security.py`) — diterapkan di seed-demo per cabang (10/menit/IP); login & form pelamar sudah punya limit sendiri.
- **Logging akses JSON**: satu baris terstruktur per request (ts, method, path, status, ip, user, role, ms) — siap dipipakan ke aggregator.
- **`GET /api/health`**: status DB master, Redis, pool — opsi `?branches=1` (admin) untuk kesehatan tiap DB cabang.

### 🗄️ Backup DB otomatis

- Service `backup` baru di docker-compose: `mysqldump` **semua database (master + tiap cabang)** setiap 03:00 WIB, retensi 30 hari, status di `last-backup.txt`. Script `scripts/backup-db.sh`.

### 📊 Laporan Konsolidasi Lintas Cabang

- **`GET /api/branches/consolidated`** (JSON) + **`consolidated-pdf`** (`ConsolidatedReportPDF` baru di pdf_generator.py) + **`consolidated-excel`** (2 sheet: Ringkasan + Transaksi Terbaru) — agregasi statistik & transaksi BBM terbaru dari **semua DB cabang** dalam satu dokumen resmi.
- Tombol **🧮 PDF Konsolidasi / Excel Konsolidasi** di kartu Ringkasan Cabang (`/app/dashboard`).

### 🖥️ UI/UX

- Komponen reusable **LoadingState (skeleton) · EmptyState · ErrorState** diterapkan di Logs, Rekap, Admin Dashboard.
- **Pagination** di Audit Log (25/halaman) & Rekap (50/halaman) — hasil filter & total tetap akurat.
- **Export Excel antrean** (`GET /api/queue/export-excel?tab=…`) + tombol ⬇️ Excel di dashboard Admin (dukungan `raw` blob di api.js).
- **Error boundary global** (Vue `errorHandler`) — kesalahan tak tertangkap tampil sebagai toast, bukan layar kosong.
- Aksesibilitas: aria-label tombol ikon & export; Modal/bell sudah punya focus trap + `role="dialog"`.

### 🧪 Pengujian

- **208 pytest** (9 baru: security headers, rate limit, health, konsolidasi PDF/endpoint) + **82 Vitest** hijau · SPA di-build & image web di-rebuild · verifikasi browser (CSP, tombol baru, pagination, konsol 0 error).

## [2.20.2] - 2026-08-13

### 🗂️ Filter Cabang di Audit Log

- Dropdown **Filter Cabang** di `/app/logs`: "Cabang aktif" (default) atau cabang spesifik → `/api/audit-logs?branch=CODE` memfilter `activity_logs.branch_code`.

### 🖨️ PDF Ringkasan per Cabang

- **`GET /api/branches/report-pdf`** (admin): `BranchSummaryPDF` baru di `pdf_generator.py` — kop resmi + tabel per cabang (transaksi, kunjungan hari ini, user) dengan palet monokrom resmi.
- Tombol **⬇️ PDF Ringkasan** di kartu Ringkasan Cabang (`/app/dashboard`).

### 🧪 Seed data demo per cabang

- **`POST /api/branches/<code>/seed-demo`** (admin): tanam rute + transaksi demo langsung ke DB cabang tertentu tanpa mengganti cabang aktif — idempoten (`DEMO-*` dilewati).
- Tombol **✨ Demo** per baris cabang di kartu Cabang (`/app/settings`).
- **Fix**: `seed_demo_appointments` membaca `users` dari **DB master** (bukan koneksi cabang) agar pengecekan marketing/driver tidak gagal di cabang baru.
- **Audit**: `branch_seed_demo` kini dicatat dengan `branch_code` = **cabang target** (param baru `branch_code` di `log_activity_async`), bukan cabang sesi admin.
- Terverifikasi live: seed MLG → 20 rute + 2 transaksi dummy, SBY tidak berubah; audit tercatat `branch_code=MLG`; PDF ringkasan 200 OK.

### 🧪 Pengujian

- **199 pytest** + **82 Vitest** hijau (test LogsView diperbarui untuk urutan select baru) · SPA di-build & image web di-rebuild.

## [2.20.1] - 2026-08-13

### 👥 Akun khusus cabang (diuji end-to-end)

- User baru dibuat lewat **Buat Akun Sekaligus** kini otomatis dicatat dengan `branch_code` cabang aktif — akun **`bagus`** (driver) & **`dewi`** (marketing) untuk cabang **MLG** dibuat & **login terverifikasi masuk ke data MLG**: `/api/driver/me` → BAGUS N 777 ML (dari DB `bpf_branch_malang`), `/api/marketing/members` → Dewi.
- **Fix multi-cabang**: `_user_team_name` (tim marketing) kini membaca `users` dari **DB master** (bukan koneksi cabang yang tabel `users`-nya kosong).

### 📊 Ringkasan Cabang di dashboard Admin

- **`GET /api/branches/stats`** (admin): transaksi, kunjungan hari ini & jumlah user per cabang — dihitung dari DB masing-masing cabang + user master per `branch_code` (cabang yang DB-nya tidak bisa dihubungi → 0, tidak menggagalkan laporan).
- **UI**: kartu **🏢 Ringkasan Cabang** di `/app/dashboard` (khusus admin) — terverifikasi: SBY (135 tx, 22 kunjungan hari ini, 20 user) vs MLG (0/0/2).

### 🧾 Audit log bertanda cabang

- `activity_logs.branch_code` (migrasi otomatis di semua DB, termasuk cabang) — `log_activity_async` menangkap `session['branch_code']` di thread pemanggil lalu mencatatnya.
- **UI Audit Log** (`/app/logs`) menampilkan kolom **Cabang**; endpoint `/api/audit-logs` menyertakan `branch_code`.
- Terverifikasi: `login dewi/bagus`, `user_bulk_create`, `driver_sync`, `branch_switch` tercatat dengan `branch_code=MLG`.

### 🧪 Pengujian

- **197 pytest** (3 baru: audit branch_code, branch_stats) + **82 Vitest** hijau · SPA di-build & image web di-rebuild.

## [2.20.0] - 2026-08-13

### 🏢 Multi-Cabang — satu instalasi melayani banyak cabang (isolasi data penuh)

- **Setiap cabang = database MySQL sendiri** (isolasi data penuh). DB master (`DB_NAME`) menyimpan `users`, `branches`, dan data operasional cabang utama; cabang baru memakai DB terpisah yang skemanya **disalin otomatis** dari master (`CREATE TABLE ... LIKE` + migrasi aplikasi).
- **Modul baru `modules/branch_manager.py`**: registri cabang (`tabel branches`), CRUD, `ensure_branch_database()` (buat DB + salin skema + tanam identitas), cache resolusi cabang.
- **Routing koneksi** di `modules/config.py`: `get_db_connection()` otomatis menunjuk ke DB cabang dari `session['branch_code']` (pool per-DB, lazy); `get_master_connection()` untuk data user/cabang.
- **Login scoping**: `users.branch_code` (migrasi otomatis) → sesi mengarah ke DB cabang; cabang nonaktif → login ditolak 403.
- **Endpoint cabang** (`modules/routes_branches.py`, admin): `GET /api/branches`, `POST /api/branches/save` (opsi langsung buat DB), `activate/deactivate`, `<code>/ensure-db`, `switch` (Admin bisa mengoperasikan cabang mana pun).
- **UI `/app/settings` → kartu 🏢 Cabang**: daftar cabang, tambah/edit (kode, nama, DB, kota, alamat, telp, identitas), tombol DB/aktif-nonaktif, dan **pemilih cabang aktif** untuk Admin. Sidebar menampilkan badge cabang.
- **Identitas per cabang**: kop surat & footer PDF, halaman login, sidebar, judul tab & watermark foto mengikuti cabang aktif (terverifikasi: cabang MLG → "Sistem Operasional | Malang").
- **Catatan penyiapan**: user DB aplikasi butuh hak pada pola `bpf\_%` agar bisa membuat database cabang — `GRANT ALL PRIVILEGES ON \`bpf\_%\`.* TO 'bpf_user'@'%'` (dijalankan di DB dev).
- **E2E terverifikasi**: cabang MLG dibuat (`bpf_branch_malang`, 40+ tabel), isolasi data terbukti (demo 0 di MLG vs 20 di SBY), switch bolak-balik tanpa gangguan.

### 📇 Identitas cabang diperluas

- Variabel baru `company_address` & `company_phone` (6 variabel total) — tampil di **kop surat PDF** (baris alamat | telp) dan dikelola di Settings (kartu Identitas + form Cabang).

### 🚛 Verifikasi PWA driver dengan username baru (huruf kecil)

- Login `guruh` / `akhad` / `wicak` (PIN 123456) via browser: profil benar, **kunjungan hari ini tampil** (GURUH→DEMO-R10, AKHAD→DEMO-R07), 4 tab berfungsi, **konsol 0 error**.

### 🧪 Pengujian

- **194 pytest** (10 baru: branches API, scoping login, routing DB; konvensi username & identitas diperbarui) + **82 Vitest** hijau · SPA di-build & image web di-rebuild.

## [2.19.2] - 2026-08-13

### 🔤 Nama akun driver dirapikan (username huruf kecil)

- Konvensi akun baru dari **Buat Akun Sekaligus**: username **huruf kecil tanpa spasi** (mis. `WICAK` → `wicak`), `full_name` title-case (mis. `Wicak`).
- **Script migrasi `scripts/tidy_driver_accounts.py`** (idempoten, aman konflik, mode `--dry-run`) — **7 akun driver existing dirapikan** di DB dev (ABIEM, AHMAD, AKHAD, DWIKI, GURUH, RIVAN, WICAK). Login driver dengan username baru **terverifikasi** & `/api/driver/me` tetap terhubung ke data kendaraan (sesi di-UPPER-kan → cocok dengan `drivers.name`).

### 🧪 Data demo dikelola Admin (create & bersihkan)

- **Endpoint admin baru**: `GET /api/demo/status`, `POST /api/demo/seed`, `POST /api/demo/clean` (scope `routes` / `transactions` / `all`, idempoten, audit log).
  - Rute demo = appointment `display_id` berawalan `DEMO-` (20 lokasi Surabaya & sekitarnya + Madura/Jember/Probolinggo/Pasuruan).
  - Transaksi demo = `transactions.is_dummy=1` (2 transaksi) + flag `dummy_data_enabled`.
- **UI di `/app/settings` → kartu 🧪 Data Demo**: status jumlah rute & transaksi demo, tombol ✨ Buat dan 🧹 Bersihkan — data asli tidak pernah terpengaruh.
- `scripts/seed_demo_routes.py` di-refactor jadi fungsi importable (`seed_demo_appointments` / `clean_demo_appointments`) — dipakai CLI & API.

### 🏢 Identitas perusahaan / cabang bisa diubah Admin (siap multi-cabang)

- **Variabel branding dinamis** di `system_config` (default ada, bisa diubah tanpa ubah kode): `company_name`, `company_subtitle`, `system_name`, `system_version`.
- **Endpoint**: `GET /api/system-config/identity` (publik — untuk branding pra-login) & `PUT /api/system-config/identity` (admin).
- **Dipakai otomatis di**: kop surat & footer **PDF** (semua laporan), **halaman login**, **sidebar**, **judul tab browser** (`document.title`) & **watermark foto** — terverifikasi PDF berganti identitas mengikuti config.
- **UI di `/app/settings` → kartu 🏢 Identitas Perusahaan / Cabang**: 4 field + Simpan (langsung berlaku).
- Modul baru `modules/company_identity.py` (get/save dengan fallback aman tanpa DB).

### 🧪 Pengujian

- **184 pytest** (9 baru: demo endpoints, identitas, konvensi username) + **82 Vitest** hijau · verifikasi browser nyata (Settings, login, konsol 0 error) · SPA di-build & image web di-rebuild.

## [2.19.1] - 2026-08-13

### 📄 Desain ulang PDF generator — compact, resmi, minimal warna

- **Palet dokumen resmi (monokrom):** teks hitam pekat (`INK`), label abu, garis & border abu tipis, isian header tabel abu sangat terang (`HEADER_FILL`), zebra ultra-tipis — **tanpa blok/aksen biru, hijau, atau merah**.
- **Header tabel seragam:** judul tabel kini hitam pekat + teks putih (sebelumnya biru `#2563eb`) di semua laporan: Rekap BBM, Laporan Pelamar, Laporan Aset, dan Log Perjalanan (export PDF trip di admin).
- **Status verifikasi air minum:** `✔ TERVERIFIKASI` / `✘ DITOLAK` kini dicetak teks tebal hitam pekat (sebelumnya hijau/merah) — tetap jelas, tanpa warna.
- **Kop surat & footer** dipertegas (garis `RULE` abu tua, teks ink) — kesan surat resmi.
- **Satu halaman** untuk laporan compact (PDFReportCompact) — lebih ringkas.
- **Tes:** 4 pytest baru (`tests/test_pdf_compact.py`) untuk `PDFReportCompact` & `BBMReportPDF` — **total 175 pytest hijau**, verifikasi render 5 kelas PDF dari image live (0 aksen warna, 1 halaman).

## [2.19.0] - 2026-08-13

### 🐛 Debugging menyeluruh halaman Driver + akun massal + rute manual + data demo rute

**Dilakukan berdasarkan hasil gladi resik nyata di browser (Chrome headless):**

- **🐛 Fix: tab "Trip" bocor ke semua tab lain di PWA driver** — `TripTab.vue` punya **dua root element** (fragment: `.tab-page` + modal hasil kunjungan), sehingga `v-show` di `DriverView` tidak bisa menyembunyikannya → konten Trip (form rute + jadwal appointment) selalu tampil di bawah tab BBM/Kasbon/Rapor. Kini template dibungkus **satu root** → 4 tab benar-benar terisolasi (terverifikasi display per tab di DOM).
- **🐛 Fix: jendela notifikasi driver selalu muncul & tidak bisa ditutup** — panel `.notif-panel` di `DriverNotifBell.vue` dirender **tanpa syarat** (tidak ada `v-if="open"`) dan CSS-nya tidak menyembunyikan → menutupi ±88% layar HP. Kini panel hanya dirender saat dibuka; tombol ✕ / Esc / klik backdrop berfungsi.
- **🐛 Fix: spam error server 1452 (FK)** — `log_activity_async(0, ...)` (dipakai banyak aksi tanpa transaksi terkait) meng-INSERT `transaction_id=0` yang ditolak foreign key `activity_logs.transaction_id` → membanjiri log container. Kini `tx_id 0` otomatis jadi `NULL` (tanpa referensi) — log server bersih.
- **🐛 Fix: warning konsol meta PWA** — `<meta name="apple-mobile-web-app-capable">` deprecated; diganti `mobile-web-app-capable`.

### 👥 Buat Akun Sekaligus (admin, `/app/settings`)

- **Endpoint `POST /api/users/bulk-create`** (admin; idempoten — akun yang sudah ada dilewati, PIN default 123456):
  - `scope=driver` → **seluruh driver aktif** di tabel `drivers` yang belum punya akun (username = nama driver, role `driver`).
  - `scope=marketing` → **seluruh user di dropdown marketing** (`marketing_members`) yang belum punya akun (role `marketing`, `team_name` ikut diset).
- **UI di Settings**: tombol `🚗 Buat Akun Semua Driver` & `📣 Buat Akun User Marketing` + modal hasil (akun dibuat / dilewati + alasan) + audit `user_bulk_create`.
- **✅ Dijalankan di DB dev**: **7 akun dibuat** — ABIEM, AHMAD, AKHAD, DWIKI, GURUH, WICAK (driver) + **Icang** (marketing, tim Yusie); RIVAN dilewati (sudah ada). Semua PIN `123456`, terverifikasi login.

### 🖐️ Atur Rute Manual (Chief Driver) — otomatis tetap ada

- **⚡ Atur Rute Otomatis (v2.15) dibiarkan utuh.**
- **Endpoint `POST /api/appointments/route-manual/apply`** (khusus role **chief_driver** — GA/Admin → 403): chief driver menentukan **sendiri** driver + **no. urut kunjungan** per appointment pada satu tanggal (tanpa algoritma). Validasi: driver aktif, appointment pada tanggal tsb & berstatus scheduled/assigned; baris tidak valid dilewati dengan laporan. Menulis `driver_name`+`route_order`+`status='assigned'`, notifikasi 🗺️ ke tiap driver, event realtime, audit `appointment_route_manual_apply`.
- **UI di board Chief Driver**: tombol `🖐️ Atur Rute Manual` → modal daftar appointment (scheduled+assigned) dengan dropdown driver + input no. urut (default urut per sesi) → `✅ Terapkan Rute Manual`.
- **Terverifikasi E2E**: 4 appointment ditugaskan via API (GURUH/WICAK/ABIEM/AKHAD, order 1) + DB ter-update; GA ditolak 403.

### 🗺️ Data demo rute diperkaya

- **`scripts/seed_demo_routes.py`** (idempoten, koordinat ditanam langsung): **20 appointment demo** untuk hari ini — Surabaya dalam kota (Pusat/Barat/Utara/Timur/Selatan), sekitar Surabaya (Sidoarjo, Gresik, Mojokerto, Lamongan) dan **luar kota** (Madura–Bangkalan & Sampang, **Jember, Probolinggo, Pasuruan**) — siap diuji dengan Atur Rute Otomatis & Manual (route-plan: 22 kunjungan, 522 km, hemat ±29,7%).
- **Bonus**: `modules/config.py` membaca `DB_PORT` (untuk script seed dari host).

### 🧪 Pengujian

- **pytest +11 → total 171 hijau** (`tests/test_bulk_accounts_manual_route.py`): bulk-create (driver+marketing, scope per jenis, skip akun ada, PIN/scope invalid, non-admin 403) + rute manual (apply, uppercase driver, driver nonaktif dilewati, appointment di luar tanggal dilewati, tanpa data 400, non-chief 403).
- **Vitest 82 hijau** + `npm run build` sukses → `static/app` diperbarui (bind-mount langsung live).
- **Verifikasi browser nyata**: 4 tab driver terisolasi (tidak ada konten Trip di tab lain) · panel notifikasi tersembunyi & bisa ditutup · modal 🖐️ Atur Rute Manual menampilkan 22 baris + dropdown driver · UI Buat Akun Sekaligus tampil · **konsol 100% bersih**.

---

## [2.18.0] - 2026-08-13

### 🔧 Aset & Pemeliharaan (migrasi dari bpf-asset-system) — role GA/Admin

Aplikasi Streamlit "BPF Asset Management System" (pemeliharaan AC kantor + kendaraan) **dimigrasikan total** ke BPF WorkHub — satu aplikasi, satu login, data di MySQL.

- **🗄️ Migrasi data** (`scripts/migrate_asset_system.py`): **15 unit AC** (Daikin Split Duct/Wall per ruangan: R. BEST 1–8, VIP, Lounge, Karaoke, Meeting, Trainer, Compliance, IT, Training) + **12 komponen kendaraan** (Oli Mesin, Ban, Aki, Timing Belt, dst. + umur standar km/bulan + estimasi biaya) + **8 kendaraan ASLI kantor** (Innova B 1126 DFC + 7 Avanza: B 2628 SRP, B 2731 SRQ, B 2737 SRQ, L 1413 CBI, L 1415 CBI, L 1904 TF, L 1906 TF) — diambil dari tabel `vehicles` WorkHub (satu sumber data, bukan sample lama).
- **❄️ Master & log AC**: CRUD unit AC (merk, tipe, kapasitas, lokasi, status) + **log servis** parameter teknikal (V supply, ampere kompresor, tekanan rendah/tinggi, temp return/supply/outdoor, delta T, drainage, test run) + **health score otomatis 0–100** dari parameter + biaya sparepart + jadwal servis berikutnya.
- **🚗 Master & log kendaraan**: CRUD kendaraan (nopol, tipe, merk, tahun, odometer, pajak/asuransi) + **log servis per komponen** (odometer, umur pakai km/bulan, biaya, montir, no invoice) — terhubung ke kendaraan BBM via `vehicle_id`.
- **📋 Rekomendasi maintenance OTOMATIS berbasis aturan** (tanpa dependensi ML berat): AC > 90 hari tanpa servis → servis rutin; health score < 60 → periksa; komponen kendaraan melewati umur pakai (km/bulan vs standar master) → servis. Prioritas Kritis/Tinggi/Sedang + batas hari; tombol 🔄 Perbarui + tandai Selesai/Batalkan.
- **📄 Laporan PDF resmi berlogo BPF** (AC / kendaraan): daftar aset + log servis terakhir + ringkasan + TTD General Affairs.
- **🔐 Keamanan**: role `ga`/`admin` saja (403 untuk yang lain), CSRF aktif, audit log `asset_*` lengkap.
- **🗄️ Skema DB** (migrasi otomatis di startup): 6 tabel baru `asset_ac`, `asset_ac_logs`, `vehicle_assets`, `vehicle_service_logs`, `vehicle_components`, `maintenance_recommendations` (FK cascade, index).

### 🧪 Pengujian & Verifikasi

- **pytest +9 → total 160 hijau** (`tests/test_assets.py`): health score AC (normal/ampere tinggi/delta T rendah/kosong), rekomendasi aturan (terlambat → muncul, baru → tidak), PDF AC & kendaraan valid berisi data (parser ToUnicode) + kosong.
- **Verifikasi browser nyata** (`frontend/scripts/verify_assets_ui.mjs`): **8/8 lulus, konsol bersih** — tab AC 15 unit, tab kendaraan 8 unit asli, tab rekomendasi, tab komponen 12, tombol PDF.
- **E2E produksi**: login `ga_officer` → summary (15 AC/8 kendaraan) ✓ · tambah log servis AC → health score 75 otomatis ✓ · rekomendasi refresh 14–15 item ✓ · PDF AC 61KB & kendaraan 59KB valid ✓ · tanpa login 401 ✓ · data test dibersihkan ✓.
- **Gladi resik penuh tetap hijau**: rehearsal 20/20, verify_ui 13/13, verify_route_ui 8/8, verify_applicants_ui 12/12.

---

## [2.17.0] - 2026-08-13

### 🗄️ Migrasi Data Google Sheet + Dropdown User (dikelola Receptionist)

Data riwayat pelamar dari **Google Spreadsheet lama** (1.014 baris) dipindahkan ke database internal — DB kini **bersih, hanya berisi data dari Google Sheet tersebut** (tabel `applicants` + `applicant_attendance` di-reset & diisi ulang dari ekspor CSV).

- **📥 Migrasi (914 data valid; 101 baris kosong draft dilewati)**: Nama, Pendidikan, No. HP, UPLINE, User, Posisi, **interview_at dari Tanggal + Jam sheet** (tanggal & jam interview tetap otomatis dari data lama). Kehadiran **H1–H4 (TRUE) → `applicant_attendance`** dengan tanggal masing-masing; status mengikuti tahap terjauh (interview / training_1–4). **Pulang=TRUE → status `resigned`** dengan alasan (kolom Alasan / "PULANG").
- **🔄 Normalisasi data**: spasi ganda dibersihkan (`TEAM  EDI 2` → `TEAM EDI 2`) sehingga nilai User konsisten dengan dropdown.
- **🔽 Kolom User kini dropdown di form pelamar** (sebelumnya teks bebas) — nilai diambil dari tabel `applicant_user_options`, **diatur oleh Receptionist**:
  - Seed awal = daftar User unik dari Google Sheet: **TEAM YUSIE 3, TEAM EDI 2, TEAM LULUK 5, TEAM SISKA 4, TEAM BAPAKE 1** (694+93+48+46+33 = 914 pelamar terpetakan).
  - **⚙️ Tombol "Kelola User"** di dashboard Receptionist: tambah, aktifkan/nonaktifkan, hapus opsi (audit log `user_option_*`).
  - Endpoint: `GET /api/applicants/user-options` (publik, hanya aktif) & `/manage` (resepsionis), POST/PATCH/DELETE (resepsionis/admin, CSRF + role). Form edit pelamar juga memakai dropdown (nilai lama tetap tampil bila bukan opsi aktif).
- **🔧 Fix**: seed `applicant_user_options` kini ter-commit eksplisit (DDL MySQL ter-commit implisit, DML tidak — seed sebelumnya hilang di sesi berikutnya).

### 🧪 Pengujian & Verifikasi

- **pytest +3 → total 151 hijau** (`TestSheetMigration`): normalisasi spasi ganda, parse tanggal `M/D/YYYY` + jam, `is_true` TRUE/FALSE.
- **Verifikasi browser nyata 12/12, konsol bersih**: form publik menampilkan dropdown User berisi opsi sheet; submit pelamar dengan pilihan dropdown; dashboard Receptionist punya tombol ⚙️ Kelola User + modal daftar opsi; dashboard Traineer tetap menampilkan rekrutan upline sendiri.
- **E2E produksi**: CRUD opsi (tambah → nonaktifkan → hapus; duplikat 409; tanpa login → 403); meta menyertakan `user_options`; list migrasi 914 baris; kehadiran H4 = 232; resign 26 dengan alasan.
- **Gladi resik penuh tetap hijau**: rehearsal 20/20, verify_ui 13/13, verify_route_ui 8/8 (tidak ada regresi).

---

## [2.16.1] - 2026-08-13

### 🏢 Ganti Nama Aplikasi → **BPF WorkHub**

- Nama aplikasi berubah dari "BPF Fleet & BBM System" menjadi **BPF WorkHub** — mencerminkan cakupan yang lebih luas (BBM, kasbon, trip, air minum, appointment & rute, pelamar kerja). Nama tampil di: judul SPA & tab browser, halaman login, brand sidebar, manifest PWA, kop & footer PDF, slide presentasi (HTML/PPTX/PDF), materi presentasi, panduan & dokumen. Nama perusahaan **PT Bestprofit Futures** tidak berubah.
- File presentasi baru: `presentasi/BPF_WorkHub_Presentasi.pptx` (12 slide) & `.pdf` (12 halaman A4 landscape) — yang lama dihapus.
- Referensi infra (`bpf-bbm-system`: repo, folder, cron, docker) sengaja dibiarkan agar tidak merusak deployment.

---

## [2.16.0] - 2026-08-13

### 🪪 Sistem Pelamar Kerja (menggantikan Google Form + Google Sheet)

Pelamar kerja yang datang ke kantor **PT Bestprofit Futures Surabaya** kini mengisi form di server internal (bukan lagi tautan Google Form/Spreadsheet). Data dikelola penuh oleh Receptionist; Traineer/Upline memantau rekrutannya.

- **📝 Form publik `/app/apply` (tanpa login)**: Nama Lengkap, Pendidikan Terakhir, Nomor HP, UPLINE, User, Posisi Yang Dilamar. **Tanggal & jam interview diambil otomatis dari timestamp submit** (ditampilkan ke pelamar bersama No. Registrasi `PLM-*`). Rate limit anti-spam per IP (10 submit/10 menit).
- **🪪 Dashboard Receptionist `/app/receptionist`** (role baru):
  - **Filter by tanggal (dari/sampai), UPLINE, User, status + fungsi search** (nama/HP/posisi) + statistik (total, hari ini, interview, dalam training, lulus, mundur).
  - **✏️ Edit** perbaiki kesalahan input pelamar, **✅ Verifikasi** data, **🗑 Hapus** (beserta riwayat kehadiran), semua tercatat audit.
  - **🎯 Manajemen kehadiran**: interview + **4 hari training** (I · H1 · H2 · H3 · H4) — pelamar bisa berhenti di tahap mana pun.
  - **🚪 Mengundurkan diri: alasan WAJIB bila pelamar sudah pernah hadir** (jejak resmi). Juga **🏁 Lulus** & **✕ Tolak** (alasan opsional).
  - **📄 Laporan PDF resmi berlogo BPF per tahap** (interview / training H1–H4): rentang tanggal + filter UPLINE/User, tabel kehadiran, ringkasan, TTD Receptionist — kombinasi fitur yang biasa dipakai resepsionis.
- **🎯 Dashboard Traineer `/app/traineer`** (role baru): pantau kehadiran orang yang direkrutnya — **scope otomatis UPLINE sendiri** (cocok parsial case-insensitive: pelamar bebas menulis nama lengkap/username), search + filter tanggal/UPLINE/User/status, chip kehadiran I/H1–H4, statistik rekrutan. Tanpa akses edit/PDF (read-only).
- **🔐 Keamanan**: role `receptionist`/`traineer` di `users.role` (migrasi otomatis), `ROLE_META` + route + menu per peran, kontrol akses per endpoint (403 untuk yang tidak berhak), audit log lengkap (`applicant_*`), CSRF tetap aktif.
- **🗄️ Skema DB** (migrasi otomatis di startup + perbaikan urutan `cursor.close()`): tabel `applicants` + `applicant_attendance` (UNIQUE per pelamar+tahap, FK cascade).

### 🧪 Pengujian & Verifikasi

- **pytest +7 → total 148 hijau** (`tests/test_applicants.py`): label tahap/status, `home_for_role` receptionist/traineer, PDF berlogo (kosong & berisi — teks diekstrak via parser ToUnicode), scope traineer. Plus perbaikan test lama.
- **Verifikasi browser nyata** (`frontend/scripts/verify_applicants_ui.mjs`, Chrome headless): **9/9 lulus, konsol bersih** — form publik 6 field + sukses + jam otomatis, dashboard Receptionist (tabel, search, aksi lengkap, tombol PDF), dashboard Traineer (rekrutan upline sendiri + chip kehadiran).
- **E2E produksi (port 5001)**: submit publik → PLM-* + timestamp ✓ · verify/edit ✓ · kehadiran interview & training H1 ✓ (status naik otomatis) · resign tanpa alasan → 400, dengan alasan → sukses ✓ · PDF report valid (1 halaman) ✓ · scope traineer hanya rekrutan upline sendiri ✓ · traineer tidak bisa edit/PDF (403) ✓ · data test dibersihkan ✓.
- **🐛 Perbaikan hasil E2E**: (1) migrasi `applicants` gagal karena `cursor.close()` dipanggil sebelum CREATE — kini urutan benar + retry startup; (2) `Unread result found` di `/api/applicants/meta` (dua query satu cursor) — diperbaiki; (3) audit log pelamar gagal FK `activity_logs.transaction_id` — kini log pakai `transaction_id=NULL`; (4) scope traineer duplikat klausa `upline LIKE` — diperbaiki; (5) route `/app/apply` belum terdaftar di router SPA — ditambahkan.

---

## [2.15.2] - 2026-08-13

### 💚 Estimasi Penghematan BBM + Backfill Koordinat + Verifikasi Browser Nyata

- **💚 Angka penghematan rute otomatis**: `route-plan` kini menghitung **baseline** (berapa km/BBM kalau kunjungan dibagi tanpa optimasi — round-robin urut daftar) lalu menampilkan `savings_percent`/`savings_km`/`savings_bbm_liter`/`savings_bbm_cost`. Modal Chief Driver menampilkan banner hijau, mis. *"💚 Hemat 38,3% jarak — 13,5 km, ±1,12 L (≈ Rp 11.248) dibanding penugasan tanpa optimasi"* — bukti efisiensi untuk manajemen.
- **🗺️ Backfill koordinat data lama**: `scripts/backfill_geocode.py` (idempotent) mengisi `lat/lng` untuk appointment lama yang belum ter-geocode — dijalankan di produksi: **2 appointment demo terisi**.
- **🧪 Verifikasi UI browser nyata** (`frontend/scripts/verify_route_ui.mjs`, Chrome headless + puppeteer-core, context incognito per peran): **8/8 lulus, konsol bersih** — label & input Jam Kunjungan di Marketing Hub, tombol ⚡ Atur Rute Otomatis di board Chief Driver, modal rute per driver + banner penghematan (38,3%), statistik total, tutup Esc.
- **🧹 Struktur .md dirapikan**: README — fitur lama dipindah ke bagian **📜 Riwayat Versi Sebelumnya** (heading `###`), fitur terbaru paling atas; USER_GUIDE — langkah jam kunjungan (Marketing §7.1), bagian **8.2 Atur Rute Otomatis ⚡** (Chief Driver), glosarium & footer v2.15; ONEPAGER, PELATIHAN, PRESENTASI disesuaikan.
- **🧪 Test: total 141 pytest hijau** (+2: penghematan vs baseline & tanpa penghematan satu driver).

---

## [2.15.1] - 2026-08-13

### 🚀 Terdeploy + Perbaikan Hasil E2E Produksi (Rute Canggih v2.15.0)

- **🚀 Deploy ke server**: `DEPOT_LAT=-7.2656732` / `DEPOT_LNG=112.7449129` di-set di `docker-compose.yml` (titik awal rute = **PT Bestprofit Futures Cab. Surabaya, Gedung Graha Bukopin, Jl. Panglima Besar Sudirman 10-18** — hasil geocoding persis), image di-rebuild (`docker compose up -d --build web`), migrasi skema otomatis jalan, kolom `visit_time/lat/lng/route_order` + tabel `geocode_cache` terverifikasi di DB produksi.
- **🐛 Fix geocoding — alamat "Jl. ... No ..." tidak ditemukan Nominatim**: uji E2E nyata menunjukkan query seperti `Jl. Rungkut Industri Raya No 12, Surabaya` mengembalikan kosong. `modules/geocode.py` kini mencoba **varian query berurutan** (alamat asli → tanpa token `jl./jalan/no./nomor/rt/rw` → tanpa nomor rumah) + **cache negatif ber-TTL 24 jam** (alamat yang diperbaiki marketing bisa di-query ulang, tanpa membebani Nominatim) + kolom `found` di `geocode_cache`. Terverifikasi: 4 alamat test di-geocode dengan benar.
- **🐛 Fix format jam "9:00:"**: `_clean` meng-slice `str(timedelta)` (9:00:00 → "9:00:") sehingga jam satu digit tampil rusak. Kini `_fmt_visit_time` mengonversi timedelta/string dengan benar → `09:00`.
- **🧪 E2E produksi penuh (data test dibersihkan)**: marketing input 4 appointment (2 Rungkut + 2 Wiyung, jam 09:00–10:30) → geocoding terisi ✓ → Chief Driver `route-plan` = **ABIEM: 2 kunjungan Rungkut (09:00→09:30, 8,7 km) · AHMAD: 2 kunjungan Wiyung (10:00→10:30, 13,0 km)** — rute searah, urut jam, total 21,8 km / ±1,81 L / Rp 18.136 ✓ → `route-plan/apply` menulis driver+route_order+assigned ✓ → notifikasi 🗺️ terkirim per driver ✓.
- **🧪 Test: total 139 pytest hijau** (+8 baru: `tests/test_geocode.py` — varian query geocoding & format visit_time).

---

## [2.15.0] - 2026-08-13

### 🗺️ Rute Canggih + Jam Kunjungan (masukan Marketing → Chief Driver)

**Tujuan: pembagian driver supaya tiap driver mendapat beberapa appointment searah (hemat BBM), dan chief driver langsung tahu rute siapa siapa.**

- **⏰ Jam kunjungan per appointment (tetap 2 sesi)**: Marketing tetap memilih Sesi 1 (08.30) / Sesi 2 (14.30), lalu bisa menentukan **jam bebas** di dalam rentang sesi (Sesi 1: 08:00–12:59, Sesi 2: 13:00–17:59). Kosongkan = otomatis jam mulai sesi. Divalidasi di `validate_appointment_input` (baru: `normalize_visit_time`), tersimpan di kolom `appointments.visit_time`.
- **📍 Geocoding alamat → koordinat** (`modules/geocode.py`): tiap alamat di-resolve ke lat/lng via **Nominatim/OpenStreetMap gratis** dengan **cache DB** (`geocode_cache`) + throttle 1 req/detik + env `GEOCODE_ENABLED=0` untuk menonaktifkan. Tanpa koordinat, appointment tetap tersimpan tapi belum ikut dioptimasi rute (terdaftar sebagai "belum terpetakan").
- **⚡ Algoritma Atur Rute Otomatis** (`modules/route_optimizer.py`): heuristic VRPTW — *greedy insertion urut jam* + *load balancing* + cek kelayakan waktu tempuh antar kunjungan. Hasilnya: rute **searah secara geografis**, urut sesuai jam kunjungan, beban antar driver merata, dan **penugasan manual yang sudah ada tetap dihormati** (seed rute). Estimasi jarak (Haversine), liter & biaya BBM ikut dihitung.
- **Tombol "⚡ Atur Rute Otomatis" di board Chief Driver**: preview rute per driver (urutan kunjungan + jam, km, estimasi BBM & biaya, total, daftar yang belum terpetakan) → **"✅ Terapkan Rute"** menulis `driver_name` + `route_order` + status assigned + notifikasi ringkas ke tiap driver (audit trail + event realtime). Titik awal perjalanan (kantor) bisa diset via env `DEPOT_LAT`/`DEPOT_LNG` (default pusat Surabaya).
- **Tampilan**: board Chief Driver & daftar Marketing menampilkan jam kunjungan; nomor urut rute (#1, #2…) di tabel tugas per driver; PWA driver mendapat notifikasi rute baru.
- **Skema DB** (migrasi otomatis di startup): `appointments.visit_time` (TIME), `lat`/`lng` (DOUBLE), `route_order` (INT) + tabel `geocode_cache`.

### 🧪 Cakupan Pengujian

- **pytest +25 → total 131 hijau**: `tests/test_route_optimizer.py` (19 test: haversine, waktu tempuh, time-window feasibility, BBM estimate, klaster searah per driver, urutan sesuai jam, penugasan manual dihormati, load balance, tanpa koordinat → unassigned, total km termasuk ke kantor, konsistensi area antar sesi) + `TestVisitTime` di `test_appointments.py` (6 test: default jam mulai sesi, valid, format salah, di luar rentang, ikut validasi input, dinormalisasi).
- SPA di-build ulang (`npm run build`), bundle disalin ke `static/app/` (bind-mount → langsung live).

---

## [2.14.2] - 2026-08-12

### 🔒 Perubahan Backend Terkunci di Image Docker + Uji Ketahanan DB

- **Image Docker di-rebuild** (`docker compose up -d --build web`): perbaikan `config.py`/`helpers.py` v2.14.1 kini **terkunci permanen di image** (tidak lagi hanya lewat `docker cp`) — verifikasi ulang: container `bbm_web` up, login 200, `MySQLConnection` & `finally` terkonfirmasi ada di image.
- **Unit test baru `tests/test_db_resilience.py` (+7)**: pool dipakai saat tersedia; fallback **non-pool** saat pool exhausted (memastikan `pool_name`/`pool_size`/`pool_reset_session` TIDAK diteruskan); fallback dipakai saat `db_pool=None`; retry lalu raise saat DB mati; `log_activity_async` menutup koneksi di `finally` (sukses & gagal); aman saat koneksi `None`. **Total pytest kini 104, semua hijau.**

### 🎬 Kartu Judul Video Walkthrough Dilengkapi Logo BPF

- `scripts/make_videos.sh` kini membuat **badge logo bulat BPF** (lingkaran putih + cincin biru, dari `static/icon-192.png`) dan menempatkannya di kartu judul tiap peran + intro/outro, dengan **latar gradien biru** & aksen warna khas. 8 video dibangun ulang (h264 1440×900, durasi sama) dan terverifikasi: logo, cincin, & teks judul tampil di frame.

### 🖥️ Slide Deck Bernuansa BPF + Logo & Gradien

- `presentasi/index.html` kini memiliki **brand fixed** (badge logo + nama sistem) di pojok kiri setiap slide, **hero logo** besar di slide judul, dan **latar gradien halus** (aksen biru & hijau, menyesuaikan mode gelap) — selaras dengan video walkthrough.
- **PDF diperbarui** (`presentasi/BPF_Fleet_BBM_System_Presentasi.pdf`): 12 halaman A4 landscape terverifikasi per halaman — semua judul utuh, tidak ada halaman kosong, brand tampil di tiap halaman.

### 🧪 E2E Pemulihan Pool DB (+2 test, total 106)

- `tests/test_db_resilience.py` kini punya **uji E2E simulasi pool habis**: `db_pool.get_connection()` selalu melempar `PoolError`, fallback `MySQLConnection` non-pool menjawab query → **login tetap 200 & sesi terbentuk** (fail-open, aplikasi tidak mati); PIN salah tetap **401** (tidak membocorkan status). Total **pytest 106** hijau di container.

### 🖊️ PPTX Editabel Kini Berlogo BPF + ONEPAGER Diperbarui

- `scripts/make_pptx.py` + **`presentasi/bpf-badge.png`** (badge bulat 400px, cincin biru): badge besar di slide judul + logo kecil di footer **semua 12 slide** — konsisten dengan slide deck HTML & video. Terverifikasi 12 slide, tiap slide punya logo.
- `ONEPAGER.md`: badge logo di header + angka test terkini (**82 frontend + 106 backend**).
- **Push v2.14.2 ke `origin/main`** (8bdb136..6c0cc4b) + **gladi resik final 20/20 konsol bersih** setelah semua perubahan.

---

## [2.14.1] - 2026-08-12

### 🐛 Perbaikan Kritis: Koneksi DB Bocor + Font Self-Host (konsol 100% bersih)

- **🐛 Fix kritis — pool MySQL habis & login 500 (ditemukan saat gladi resik ulang)**: `log_activity_async` (audit log async, dipanggil di SETIAP login) tidak menutup koneksi saat query error — hanya di jalur sukses, bukan `finally` → tiap kegagalan membocorkan 1 koneksi dari pool (10–15). Setelah aktivitas cukup (mis. gladi resik), pool habis total dan semua login/API 500. Kini `conn.close()` dipindah ke `finally` — koneksi selalu kembali ke pool. (ISO/IEC 27001 A.8.2 · keandalan layanan)
- **🐛 Fix kritis — fallback DB tak pernah pulih saat pool habis**: `get_db_connection()` saat pool exhausted memanggil `mysql.connector.connect()` yang (di versi 8.2.0) **masih me-routing ke pool global yang sama** karena `fallback_config` menyisakan `pool_reset_session` (salah satu `CNX_POOL_ARGS`) → fallback ikut gagal `PoolError`, sistem tak pernah pulih tanpa restart. Kini fallback memakai `MySQLConnection(...)` langsung (non-pool) + semua argumen pool dibuang — aplikasi tetap jalan walau pool penuh.
- **🔤 Font Inter di-self-host** (`frontend/public/fonts/inter-latin-var.woff2`, 48 KB variable font weight 100–900): tautan Google Fonts dihapus dari `index.html` → menghilangkan **404 `fonts.gstatic.com`** yang mengotori konsol, UI lebih cepat & **tetap rapi saat internet lambat/offline** (penting untuk demo).
- **🎬 Gladi resik dijalankan ulang → 20/20 cek lulus + konsol 100% bersih (0 error JS)** — termasuk cek isolasi OB, antrean GA, verifikasi Finance, board Chief Driver, 4 tab driver, realtime.

### 🎬 Video Walkthrough Diperkaya (8 mp4, total 22 adegan)

- **Lebih banyak adegan per peran + interaksi nyata**: `frontend/scripts/record.mjs` kini merekam 22 adegan (admin 4, finance 4, driver 4, ga 3, ob/marketing/chief 2) dengan klik tombol (form pengajuan OB, modal verifikasi Finance), isi form (deteksi area otomatis Marketing), dan ganti tab driver (BBM → Kasbon → Trip → Rapor).
- **Kartu judul per peran** + **intro & outro** pada `walkthrough-all.mp4` (sekarang ±95 dtk), **transisi fade** antar adegan, dan **keterangan teks di tiap adegan** (dari `captions.json`) — di-render oleh `scripts/make_videos.sh` (ffmpeg: zoom Ken Burns + drawtext + fade).
- Catatan teknis: concat ffmpeg relatif terhadap lokasi file list → path absolut; output per-peran kini memakai glob `for` yang lebih andal.

---

## [2.14.0] - 2026-08-12

### 🎬 Gladi Resik Otomatis & Paket Video Walkthrough

- **Gladi resik otomatis** (`frontend/scripts/rehearsal.mjs`): login nyata di Chrome utk 7 peran + verifikasi alur PRESENTASI (antrean GA, kasbon, air minum OB→Finance, appointment marketing, board chief driver, aplikasi driver, realtime bell). **20/20 cek lulus, konsol bersih** — laporan kesiapan langsung tampil di terminal.
  - Perbaikan penting: tiap peran kini pakai **browser context incognito terpisah** sehingga cookie & localStorage tidak bocor antar login (sebelumnya halaman login ter-redirect ke dashboard sesi lama).
- **Video walkthrough per peran** (`scripts/make_videos.sh` + `frontend/scripts/record.mjs`): 8 video mp4 1440×900 di `presentasi/videos/` (admin, ob, finance, ga, marketing, chief, driver, + `walkthrough-all.mp4` 80 dtk) — dihasilkan dari screenshot nyata dengan efek zoom lembut, siap diputar di meeting.
- **One-pager peserta meeting** (`ONEPAGER.md`): ringkasan satu halaman — mengapa sistem ini ada, siapa memakai, fitur utama, keamanan, dan apa yang dilihat di demo.
- **Auto-cleanup data demo** (`scripts/auto_cleanup_demo.sh` + cron): data label DEMO otomatis dihapus **H+1 setelah tanggal meeting** (set default `MEETING_DATE`, mudah diubah). Cron terpasang: tiap hari 02:15.

## [2.13.0] - 2026-08-12

### 🎤 Paket Lengkap Presentasi & Demo

- **Versi PPTX editabel**: `presentasi/BPF_Fleet_BBM_System_Presentasi.pptx` — 12 slide 16:9 dari materi presentasi, siap diedit di PowerPoint. Generator: `scripts/make_pptx.py` (python-pptx, jalankan ulang kapan saja). Terverifikasi 12 slide dengan judul lengkap.
- **PDF diperiksa halaman per halaman** (pdftotext): 12 halaman A4 landscape, semua judul slide utuh, tidak ada halaman kosong atau terpotong — aman dibagikan.
- **Data analytics demo**: 70 transaksi riwayat ~3 bulan (label `BPF-DEMO-H*`, 5 driver, nominal & km_per_liter bervariasi) — grafik Analytics kini hidup (90+ transaksi, grafik bulanan 2–3 bar). Ikut terhapus oleh `scripts/demo_cleanup.sql` (prefix `BPF-DEMO-%`).
- **Lembar latihan per peran**: `PELATIHAN.md` — langkah + hasil yang diharapkan untuk OB, Driver, GA, Finance, Marketing, Chief Driver, Admin, plus daftar periksa sebelum demo.
- Tooling: `python3-pip` + `poppler-utils` terpasang di server (pengembangan/dokumen).

---

## [2.12.1] - 2026-08-12

### 📄 Versi PDF Slide Deck

- `presentasi/BPF_Fleet_BBM_System_Presentasi.pdf` — **12 halaman** landscape A4 dari slide deck (tanpa catatan pembicara), siap dibagikan sebelum meeting. CSS print di `presentasi/index.html` dioptimalkan: satu slide = satu halaman, ukuran font/table disesuaikan agar tidak terpotong.

---

## [2.12.0] - 2026-08-12

### 🎤 Siap Demo: Slide Deck, Data Demo, Verifikasi Chrome Host

- **Chrome host berfungsi**: dependensi sistem (`libnspr4`, `libnss3`, dll) terpasang → Chrome for Testing 151 berjalan langsung di host. `frontend/scripts/verify_ui.mjs` kini launch Chrome sendiri (tanpa Docker) — **13/13 cek lulus, console 100% bersih** (login per peran, PIN toggle, dashboard, dark, kontras tinggi, fokus keyboard, bell+Esc, Finance, Air Minum).
- **Slide deck interaktif**: `presentasi/index.html` — 12 slide dari materi `PRESENTASI.md`, navigasi keyboard (→ ←, Home/End), **catatan pembicara** (tekan N), swipe di HP, mode cetak/PDF (Ctrl+P), dark mode otomatis.
- **Data demo lengkap** (label `DEMO`, aman dibedakan):
  - Merk air minum (AQUA Galon, Club, Le Minerale, VIT Botol, VIT Gelas) + 2 pengajuan (WTR-DEMO-01 pending Faisol, WTR-DEMO-02 verified Febri).
  - Klaim BBM: 2 pending + 1 `verified_ga` + 1 `os_finance` (RIVAN/BUDI/ANDRE).
  - Kasbon: 2 DRAFT + 1 GA_APPROVED · Trip 1 pending · Appointment 2 (scheduled & assigned).
  - **Terverifikasi E2E**: antrean GA, kasbon, rekap air minum, trips semuanya menampilkan data demo.
  - **Pembersih**: `scripts/demo_cleanup.sql` (hapus semua baris label DEMO).
- **Akses HTTP lokal**: opsi `SESSION_COOKIE_SECURE=false` di `docker-compose.yml` (baris komentar, aman produksi) + catatan praktis di `DEPLOYMENT.md` — solusi "login gagal di browser lewat http dev".
- `PRESENTASI.md` ditautkan ke slide deck & data demo.

---

## [2.11.0] - 2026-08-12

### 🎨 Aksesibilitas Dialog & Kontras + Verifikasi Browser Nyata

- **Dialog non-Modal diaksesibel**: panel notifikasi (NotificationBell & DriverNotifBell) kini punya `role="dialog"`, `aria-expanded`/`aria-haspopup`, **tutup dengan Esc**, dan perbaikan variabel `--card` → `--surface`. Modal hasil kunjungan di TripTab (driver) dapat `role="dialog"`, `aria-modal`, tutup Esc.
- **Kontras tombol diperbaiki** (WCAG 2.1.4): `.btn-success` → `#047857` dan `.btn-warning` → `#b45309` agar teks putih ≥ 4,5:1.
- **Mode Kontras Tinggi (baru) 🔆**: tombol di topbar (di samping 🌙) — token warna diperkuat (teks hitam/putih pekat, border menebal 2px), tersimpan di `localStorage` (`bpf_hc`), kombinasi dengan dark mode (`html.dark.hc`).
- **Verifikasi browser nyata**: Chrome dijalankan di Docker (CDP port 9222) dan di-drive dengan `puppeteer-core` (`frontend/scripts/verify_ui.mjs`) — **13/13 cek lulus**: login per peran, toggle lihat PIN, dashboard, dark mode, kontras tinggi (border 2px), fokus keyboard terlihat (outline 2px), bell buka/tutup Esc + `aria-expanded`, Dashboard Finance & Air Minum, console bersih.
- **Materi presentasi**: `PRESENTASI.md` — draft lengkap & terstruktur sesuai prioritas demo (air minum, dashboard per peran, kasbon & kode unik, realtime, offline, keamanan, kualitas), bahasa humanis, dengan skrip, durasi, dan FAQ.

### 🧪 Cakupan Pengujian

- **82 Vitest + 97 pytest** hijau; SPA di-build ulang & terverifikasi langsung di browser.

---

## [2.10.0] - 2026-08-12

### 🎨 Peningkatan UI/UX sesuai Standar (WCAG 2.1 · ISO 9241-11)

- **Fokus keyboard terlihat**: ring `:focus-visible` global di tombol/link/input (WCAG 2.4.7) — pengguna keyboard selalu tahu posisi fokus.
- **Kontras teks diperbaiki**: `--text-3` (mode terang) digelapkan `#94a3b8 → #64748b` — rasio ≥ 4,5:1 terhadap permukaan (WCAG 2.1.4).
- **Gerakan terbatas**: blok `prefers-reduced-motion` mematikan animasi bagi pengguna yang sensitif (WCAG 2.3.3).
- **Skip-link** "Langsung ke konten" di layout — ditempatkan di luar sidebar agar tetap bisa diakses di layar kecil (WCAG 2.4.1).
- **Modal diaksesibel penuh**: `role="dialog"` + `aria-modal`, tutup dengan **Esc**, fokus awal ke tombol tutup, **restore fokus** ke pemicu, dan **focus trap Tab** agar fokus tidak bocor ke konten belakang (WCAG 2.4.3).
- **Halaman Login**: toggle **👁 lihat / 🙈 sembunyikan PIN**, peringatan **Caps Lock aktif**, dan label terhubung (`for`/`id`).
- **Toast**: region `aria-live="polite"` (dibaca pembaca layar), **warna aksen per tipe event** (klaim ⚠️, trip 🔵, appointment 🟣, air minum 🩵), perbaikan variabel `--card` yang keliru → `--surface`.
- **Loading skeleton**: efek shimmer pada semua state "Memuat…" di 15+ tampilan (teks tidak diubah — test tetap hijau).

### 🧹 Bersih-bersih

- **Akun `ob` (Office Boy) dihapus total dari database** (sebelumnya nonaktif) — tidak ada FK yang mereferensikan users, aman. User aktif: admin, ga_officer, finance_officer, qa, Yusie, driver, ob1/ob2/ob3.
- **PWA legacy**: root `sw.js` lama bersifat network-first dan melewati `/app` (SPA punya SW sendiri) — perangkat yang sudah terpasang lama tetap berfungsi; instalasi baru memakai `/app/sw.js`. Verifikasi: tidak ada referensi tersisa.
- **README dirapikan** — riwayat versi lama dipertahankan sebagai catatan sejarah, tabel akses sudah memakai URL `/app/*`.

### 🧪 Cakupan Pengujian

- **82 Vitest + 97 pytest** hijau (tidak ada assert yang berubah).
- Build SPA sukses, `/app/` & `/app/login` 200.

---

## [2.9.0] - 2026-08-12

### 🧹 Bersih-Bersih Kode + Panduan Baru + Server Efisien

- **Kode mati dibuang**:
  - `modules/routes_admin.py` dipangkas total — endpoint aksi klasik (ga_approve, finance_payout, finance_archive, reject, unverify, delete, edit-odo, trips verify/reject) **dihapus** karena SPA sudah punya pengganti resmi (`/api/queue/*` & `/api/trips/*`). Tersisa: redirect kompat (`/admin`, `/admin/queue-fragment/<tab>`, `/admin/trips`, `/ga/assignments` → SPA) + **export logsheet Excel/PDF** yang belum punya tombol di SPA.
  - `modules/routes_driver.py`: route `/manifest.json` & `/sw.js` (root legacy) dihapus — SPA memakai `/app/manifest.webmanifest` & `/app/sw.js`.
  - File mati di-root **`sw.js` & `manifest.json` dihapus dari repo**; `CSRF_EXEMPT_PREFIXES` di `app.py` dibersihkan (tidak ada lagi `/manifest.json` & `/sw.js`).
- **Akun OB generik dinonaktifkan**: `ob` (Office Boy) `is_active=0` — tidak bisa login. OB aktif kini hanya `ob1` **Faisol**, `ob2` **Febri**, `ob3` **Edwin**.
- **Dashboard GA auto-refresh**: antrean klaim langsung ter-refresh saat ada klaim baru masuk (event realtime `new_claim` dipantau lewat watch `realtime.items[0]`, dengan guard anti-overlap saat masih loading).
- **USER_GUIDE.md ditulis ulang total**: struktur rapi per peran (OB, Driver, GA, Finance, Marketing, Chief Driver, Admin) + alur kasbon lengkap + troubleshooting + glosarium — bahasa humanis, mudah dipahami orang awam, disesuaikan dengan user nyata (Faisol/Febri/Edwin & dashboard per-role).
- **Server & Docker efisien**: `docker system/image/builder/volume prune` → **1,7 GB+ dibebaskan** (volume 2,1 GB → 677 MB, build cache 220 MB → 0).

### 🧪 Cakupan Pengujian

- **pytest**: `test_cleanup_function_exists` diperbarui — cleanup file kini diverifikasi di `routes_spa.py`/`routes_cash.py` (lokasi sebenarnya setelah routes_admin dipangkas), assert `os.remove`/`_os.remove`. Total **97** hijau.
- **Vitest**: `GaDashboard.test.js` ditambah setup Pinia (`setActivePinia(createPinia())`) untuk store realtime. Total **82** hijau.
- **E2E produksi**: GA → `/app/ga` ✅ · Finance → `/app/finance` ✅ · OB1 (Faisol) → `/app/water` ✅ · `ob` nonaktif → login **ditolak** ✅ · `/login` → 302 `/app/login` ✅ · `/admin` → 302 `/app/dashboard` ✅ · `/sw.js` & `/manifest.json` root → **404** ✅ · SPA `/app/` 200 ✅ · antrean GA ✅.

---

## [2.8.0] - 2026-08-12

### 🧾 Dashboard Khusus GA + Nama OB Asli

- **GA kini punya halaman sendiri**: `/app/ga` (sebelumnya tercampur dengan admin di `/app/dashboard`). Setelah login, GA langsung diarahkan ke dashboard-nya — menu menampilkan **Dashboard GA** khusus (admin tetap di `/app/dashboard`, dan bisa membuka ketiga dashboard).
- **Isi dashboard GA**: kartu statistik (antrean GA, verified GA, terarsip, transaksi hari ini, kasbon menunggu approve), **antrean klaim BBM** dengan tombol ✅ Approve / ✕ Tolak (modal alasan — alasan wajib untuk audit trail), **🛡 Verifikasi anomali ML langsung di dashboard** (klaim ber-flag ⚠️ tidak lagi perlu ke Dashboard Admin: modal konfirmasi → `/api/queue/verify` dengan `confirm_anomaly`), ringkasan **kasbon DRAFT** yang menunggu approve GA, **laporan perjalanan pending**, dan aksi cepat (Trip, Assignments, Kasbon, Air Minum, Analytics).
- **Kontrol akses tetap ketat**: GA tidak bisa membuka `/app/dashboard` maupun `/api/water/recap` (403); `/api/queue/reject` & `/api/queue/verify` memang untuk ga/admin — GA memegang kendali penuh siklus klaimnya.
- **Nama OB asli**: `ob1` → **Faisol**, `ob2` → **Febri**, `ob3` → **Edwin** (PIN tetap 123456) — nama tampil di PDF tanda terima & notifikasi.

### 🧪 Cakupan Pengujian

- **Vitest +5** (`GaDashboard.test.js`, kini 6 test): kartu statistik, antrean & kasbon DRAFT, approve (confirm), verifikasi anomali (wajib centang → `/api/queue/verify` dengan `confirm_anomaly`), tolak (tombol terkunci tanpa alasan). Update `auth.test.js` (`ga.home` → `/ga`). Total **82**.
- **pytest**: update assert lama `home_for_role('ga')` → `/app/ga`. Total **97** (hijau di container).
- **E2E produksi**: GA login → home `/app/ga` ✅ · data dashboard GA (stats/queue/cash/trips) ✅ · GA → `/api/water/recap` = **403** ✅ · admin tetap `/app/dashboard` ✅ · **verifikasi anomali GA**: tanpa konfirmasi → 422, dengan konfirmasi → `verified_ga` ✅ · Faisol buat pengajuan → isolasi OB (`ob_name` Faisol) ✅ · data test dibersihkan ✅.

---

## [2.7.0] - 2026-08-12

### 💰 Dashboard Khusus Finance + Rekap Air Minum

- **Finance kini punya halaman sendiri**: `/app/finance` (sebelumnya tercampur dengan admin/GA di `/app/dashboard`). Setelah login, Finance langsung diarahkan ke dashboard-nya — menu juga menampilkan **Dashboard Finance** khusus.
- **Rekap air minum**: kartu statistik (total, menunggu verifikasi, terverifikasi, ditolak, total kuantitas), **antrean verifikasi** (langsung link ke halaman Air Minum), **ringkasan per OB**, **per jenis & per merk** (bar chart ringan), filter **rentang tanggal** (default 90 hari terakhir), dan **Export CSV** (UTF-8 BOM — terbuka rapi di Excel, satu baris per item).
- **Ringkasan kasbon yang menunggu Finance**: jumlah + nominal kasbon berstatus `GA_APPROVED` (menunggu approve) dan LPJ `LPJ_SUBMITTED` (menunggu approve) — dengan link ke halaman Kasbon.
- **Kontrol akses**: endpoint `/api/water/recap` & `/api/water/recap/export` hanya untuk Finance/Admin (OB & GA → 403), semua aksi tercatat audit (`water_recap_view`/`water_recap_export`). Query rekap dibatasi rentang tanggal + `LIMIT 2000` (anti pembesaran data), parameter tanggal divalidasi format.
- **Beberapa akun OB didukung**: akun per orang (ob1/ob2/ob3…), tiap OB hanya melihat pengajuannya sendiri (identitas dari `full_name` sesi).

### 🧪 Cakupan Pengujian

- **pytest +3** (`TestWaterRecap`): agregasi ringkasan/per-OB, per-jenis/merk + antrean, CSV BOM/header/baris. Update test lama: `home_for_role('finance')` → `/app/finance`. Total **97**.
- **Vitest +5** (`FinanceDashboard.test.js`): kartu statistik, antrean & per-OB, kasbon, export CSV, filter tanggal. Update `auth.test.js` (finance home `/finance`). Total **76**.
- **E2E produksi**: login finance → home `/app/finance` ✅ · OB1 buat pengajuan → rekap menampilkan ringkasan/per-OB/antrean ✅ · Export CSV berisi BOM + header + data ✅ · **isolasi OB** (OB1 hanya melihat 1 punya) ✅ · OB & GA akses rekap → **403** ✅ · akun ob1/ob2/ob3 login → `/app/water` ✅ · data test dibersihkan ✅.

---

## [2.6.0] - 2026-08-12

### 💧 Tanda Terima Pembelian Air Minum (Gelas/Botol/Galon)

- **Role baru `OB`** (Office Boy): halaman khusus `/app/water` — mengisi tanggal pembelian, daftar item multi-baris (tipe + merk + satuan + kuantitas, tanpa harga), serta **wajib mengunggah 2 foto timestamp: "sebelum diisi" dan "sesudah diisi"**.
- **Finance mengelola master data**: tipe air minum (Gelas/Botol/Galon — seed otomatis) dan **merk** (dropdown untuk OB). Finance juga memverifikasi setiap pengajuan — **approve** (remark wajib + note tambahan opsional) atau **tolak** (alasan).
- **PDF Tanda Terima Serah Terima** (`WaterReceiptPDF`): kop surat PT Bestprofit, nomor unik `WTR-YYYYMMDD-xxxx`, tabel item, hasil verifikasi (remark/note/alasan), **blok tanda tangan Finance (menyerahkan) & GA (menerima)** — nama TTD di-set global oleh admin di `/app/settings`, dan **lampiran 2 foto**. Status pending/verified/rejected masing-masing punya tampilan PDF sendiri.
- **Kontrol akses**: OB hanya melihat & mengunduh PDF pengajuannya sendiri; master merk & verifikasi khusus Finance/admin; tanpa sesi → 401. Semua aksi tercatat di audit trail (`water_*`).
- **Validasi input**: minimal 1 item, maks 20 item/pengajuan, kuantitas angka 1–99.999, satuan di-whitelist, foto wajib (JPG/PNG), remark di-truncate 500 / note 2000 karakter. Batch-load item di daftar pengajuan (hindari N+1), page-break aman untuk blok TTD PDF.
- **🔔 Notifikasi realtime ke Finance**: saat OB mengirim pengajuan, event `water_purchase_new` di-broadcast — Finance & admin mendapat toast 💧 + badge di lonceng notifikasi tanpa reload (pola sama dengan `new_claim`/`new_trip_report`).

### 🗄️ Skema Database (otomatis di startup + init.sql)

- Tabel baru: `water_drink_types` (seed Gelas/Botol/Galon), `water_drink_brands` (soft-delete), `water_purchases` (status, ob_name, foto, remark/note, verified_by), `water_purchase_items` (drink_type, brand, satuan, quantity).
- `users.role` enum diperluas dengan `'ob'` (idempotent).

### 🧪 Cakupan Pengujian

- **pytest +7** (`tests/test_water.py`) — PDF verified/rejected/pending diekstrak teksnya lewat helper `_pdf_text` (parser ToUnicode per-font tanpa dependensi pypdf), `_get_ttd_names` dari `system_config`, `home_for_role('ob')` → `/app/water`. Total **94** (terverifikasi di container).
- **Vitest +4** (`WaterView.test.js`) — render form OB, verifikasi Finance, detail modal. Total **71**.
- **E2E produksi (:5001)**: login OB → home `/app/water` ✅ · Finance tambah merk ✅ · OB kirim pengajuan multi-item + 2 foto ✅ · Finance approve & tolak ✅ · OB dilarang verifikasi (403) ✅ · PDF berisi item, remark/note, TTD FIN/GA ✅ · validasi qty non-angka → 400 ✅ · tanpa sesi → 401 ✅ · data test dibersihkan ✅.

---

## [2.5.0] - 2026-08-12

### 🚮 Pensiun Total Antarmuka Klasik — 100% SPA Vue 3

- **File sampah klasik dihapus dari repo**: `templates/*.html` (14), `static/js/*` (13), `static/css/*` (11), dan `static/archive.js`. Repo kini murni SPA Vue 3 (bundle di `static/app/`, sumber di `frontend/`) + backend Flask API. Referensi terverifikasi: tidak ada kode tersisa yang memakai `render_template` / aset klasik.
- **Semua halaman klasik → redirect ke SPA** (bookmark lama tetap berfungsi): `/login` → `/app/login`, `/admin` → `/app/dashboard`, `/admin/trips` → `/app/trips`, `/admin/rekap` → `/app/rekap`, `/admin/analytics` → `/app/analytics`, `/admin/logs` → `/app/logs`, `/admin/users` → `/app/users`, `/admin/settings` → `/app/settings`, `/admin/queue-fragment/<tab>` → `/app/dashboard`, `/marketing` → `/app/marketing`, `/chief-driver` → `/app/chief-driver`, `/ga/assignments` → `/app/assignments`, `/driver` → `/app/driver`, `/` → `/app/`. `_auth_denied_response`/`_auth_forbidden_response` kini mengarah langsung ke SPA (login / home sesuai role).
- **Jalur legacy `?driver=` anonim DITUTUP** (sebelumnya `session_driver_name() or param` — kini helper baru `resolve_driver_scope()`: sesi driver = identitas sesi, sesi back-office = param eksplisit diizinkan, **tanpa sesi → 401**). Berlaku di: `POST /driver`, `POST /submit-trip`, `/api/cash/request`, `pending-lpj`, `history`, `delete`, `submit-lpj`, `/api/notifications*`, `/api/appointments/driver-today`, `driver-complete`, `completed`, `driver-summary`. (ISO/IEC 27001 A.8.2)
- **CSRF diperketat (defense-in-depth)**: prefix `/submit-trip`, `/api/cash/request`, `/api/cash/submit-lpj/`, `/api/cash/delete/`, `/api/appointments/driver-complete/` dihapus dari `CSRF_EXEMPT_PREFIXES` — SPA driver mengirim `X-CSRF-Token` di semua request tersebut.
- **Reset PIN Massal Driver**: `POST /api/drivers/pin-reset` (admin) + tombol `🔑 PIN Driver = 123456` di `/app/settings` — seluruh user ber-role `driver` di-reset ke **123456** (audit `bulk_driver_pin_reset`).
- `POST /driver` & `POST /submit-trip` kini mengembalikan JSON error (bukan render/flash) — konsisten dengan SPA; pesan "Dashboard Klasik" pada guard anomali ML diganti "dari baris antrean".
- **🐛 Fix kritis (ditemukan E2E)**: kolom `users.role` di DB lama masih `ENUM(...)` **tanpa `'driver'`** sehingga pembuatan akun driver gagal `Data truncated`. Kini migrasi otomatis di `appointments_schema.py` + `init.sql` menyertakan `'driver'` (idempotent, aman di startup), dan ALTER sudah diterapkan ke DB produksi.

### 🧪 Cakupan Pengujian

- **Vitest naik ke 67 test** — `SettingsView` +1 (reset PIN massal → `/api/drivers/pin-reset` dengan `new_pin: '123456'`).
- **pytest +4** (`tests/test_driver_session.py`) — `resolve_driver_scope`: anonim→None (401), sesi driver mengalahkan param, back-office param diizinkan, back-office tanpa param → '' (semua). Total **87** (terverifikasi di container).
- `py_compile` semua modul ✅ · `npm test` + `npm run build` + `scripts/build-spa.sh` ✅.
- **E2E produksi (DuckDNS :5001)**: semua redirect klasik → SPA ✅ · legacy `?driver=` anonim → 401 ✅ · CSRF driver kini aktif ✅ · create akun driver → login PIN → bulk PIN `123456` ✅ · akun test dinonaktifkan setelah verifikasi ✅.

---

## [2.4.0] - 2026-08-12

### 🎯 Paritas SPA Lengkap — Semua Alur Back-Office Kini di Vue (Fase 1 Migrasi)

- **Antrean GA — verifikasi anomali ML penuh langsung dari SPA**: tombol `🛡 Verifikasi` di baris antrean ber-flag anomali membuka modal detail langsung ke form verifikasi (konfirmasi wajib + foto MyPertamina) — tanpa lagi pindah ke Dashboard Klasik. Tautan `📋 Verifikasi Penuh (Klasik)`, `📋 Klasik`, dan tombol `Dashboard/Assignments Klasik` **dihapus**; halaman klasik back-office tidak lagi ditaut dari SPA.
- **Board Chief Driver lengkap (paritas dengan halaman klasik)**: saran driver load-balancing otomatis **terisi sebagai default** per baris per sesi (+ hint `💡 Saran`), filter tab Sesi 1/2, override area manual `🌍` (PATCH `area`), `🔄 Ganti` driver (re-assign), `↩️ Batal Tugas` (unassign), `✅ Selesai` dengan **modal hasil kunjungan wajib** (😊 Ditemui / 🤝 Prospek / ❌ Gagal + catatan), `✕` batal appointment (wajib alasan), badge hasil kunjungan + tombol `🎯 Hasil` untuk mengubah hasil appointment selesai, **Ringkasan per Marketing Anggota** (Total/⏳/🚗/✅/✕/konversi/sesi — klik baris = filter board), dan dropdown **filter Marketing Anggota** (bisa dikombinasikan dengan export Excel).
- **Marketing Hub SPA**: `✏️ Edit` (modal, hanya milik sendiri & status scheduled → PATCH), `✕ Batal` dengan alasan (busy-guard anti double-click), **datalist saran nama marketing anggota** tim sendiri, **preview deteksi area** otomatis dari alamat (📍 chip, saat blur), dan kolom **Hasil** kunjungan di daftar.
- Backend tidak berubah — semua memakai endpoint yang sudah ada (`PATCH /api/appointments/<id>`, `/assign`, `/unassign`, `/complete`, `/cancel`, `/member-summary`, `/suggestions`, `/marketing/members`, `/detect-area`).

### 🧪 Cakupan Pengujian

- **Vitest naik ke 56 test** (dari 47): AdminDashboard +2 (tombol 🛡 baris → form verifikasi terbuka langsung), ChiefDriverDashboard ditulis ulang jadi 8 test (saran default per sesi, select independen per baris, override area, unassign, cancel, complete wajib hasil + POST `/complete`, filter member dari ringkasan, badge hasil di baris APP-4), MarketingDashboard +2 (edit → PATCH, batal → `/cancel`).
- `npm run build` sukses ✅ · `bash scripts/build-spa.sh` → `static/app` termutakhirkan ✅ (bind-mount otomatis melayani versi baru).

---

## [2.4.0] - 2026-08-12 (Fase 2) — Driver PWA Migrasi ke Vue + Login PIN

### 🔐 Driver Wajib Login PIN (role baru `driver`)

- **Role `driver`** di tabel `users` (dibuat/reset PIN via halaman Users/Settings — role kini diizinkan di `/api/users/sync`); `ROLE_META['driver']` + route `/app/driver` + `home_for_role('driver')` → `/app/driver`.
- **`/driver` (GET) redirect ke `/app/driver`** (SPA; guard mengarahkan ke login PIN). POST `/driver` & `/submit-trip` tetap berfungsi untuk antrean offline legacy.
- **Identitas sesi dipaksa di semua endpoint driver** (anti impersonasi & IDOR — ISO/IEC 27001 A.8.2): `POST /driver`, `/submit-trip`, `/api/cash/request`, `pending-lpj`, `history`, `delete` (cek kepemilikan utk sesi driver), **`submit-lpj` (baru: LPJ hanya untuk kasbon milik sendiri → 403)**, `/api/notifications*`, `/api/appointments/driver-today` & `driver-complete`. Jalur legacy (tanpa sesi, `?driver=`) tetap berjalan sebagai transisi.
- Endpoint baru **`GET /api/driver/me`** (role driver): profil (nopol, kendaraan, BBM) dari sesi.

### 📱 Driver PWA Vue 3 di `/app/driver` (offline-first penuh)

- **Shell mobile mandiri** `DriverView.vue`: header (logo, nama, bell 🔔, dark mode, logout), status bar 🟢/🟡 online-offline + badge antrean + tombol Sinkron, **bottom-nav 4 tab** (⛽ BBM · 💰 Kasbon · 🗺️ Trip · 📊 Rapor) — port dari PWA klasik.
- **BBM**: form klaim (auto-fill dari profil master data, daftar BBM valid per kendaraan, hitung liter otomatis, SPBU rekanan/non-rekanan, foto 4x **watermark canvas** perusahaan+tanggal+GPS, GPS satu-klik) → kirim online atau **antre offline**; **mode LPJ** dari kasbon (nominal terkunci).
- **Trip**: baris rute dinamis + GPS+jam auto-fill, **panel "Jadwal Appointment Saya"** (tel/maps/🏁 hasil kunjungan modal: 😊/🤝/❌), **"📥 Muat Semua ke Rute"** (rute berantai + `appointment_id[]` → auto-complete), multi-rute aman (array per key — fix bug rute tertimpa yang ditemukan review).
- **Kasbon**: kode unik harian + mode manual/otomatis, pengajuan (total = dasar + kode), daftar LPJ pending → isi di tab BBM, riwayat dengan progress bar + hapus DRAFT.
- **Rapor**: cek performa km/L (`/api/get-feedback`).
- **Offline-first**: `utils/idb.js` (3 antrean IndexedDB) + `driverStore.syncAll()` (BBM→`/driver`, LPJ→`/api/cash/submit-lpj`, trip→`/submit-trip`, urut & hapus per item) + auto-sync saat online & tiap 30 detik.
- **Notifikasi real-time**: bell + panel + toast, Socket.IO join room `driver_<NAMA>`, `driver_notification` realtime.
- **`DriverNotifBell.vue`** + `stores/driverStore.js` + `utils/gps.js` (Nominatim) + `utils/watermark.js`.

### 🧪 Cakupan Pengujian

- **Vitest naik ke 66 test** (dari 56): `driverStore.test.js` (5: profil, enqueue+badge, syncAll kirim+hapus, push notifikasi, locate GPS, toForm multi-rute array) + `DriverView.test.js` (3: shell 4 tab, profil dari `/api/driver/me`, switch tab kasbon) + guard router +3 kasus role driver (bisa buka `/driver`, tidak bisa masuk back-office, role lain tidak bisa masuk `/driver`).
- **pytest +7** (`tests/test_driver_session.py`): `session_driver_name` (tanpa sesi→None, sesi driver→UPPER, role lain→None) + `home_for_role('driver')` → `/app/driver`. Dijalankan CI (`docker exec bbm_web pytest`); sintaks semua modul terverifikasi `py_compile`.
- `npm run build` sukses ✅ · `static/app` termutakhirkan ✅.

---

## [2.3.0] - 2026-08-11

### ⚡ Rate Limit Redis (Konsisten Antar Replica)

- Backing store rate limit (login & verify-pin) dipindah dari memori proses ke **Redis** (service `redis:7-alpine` di docker-compose, TTL otomatis, limit memori 64MB).
- **Fallback aman**: bila Redis tidak dikonfigurasi / gagal connect, otomatis kembali ke memori proses — deployment lama tetap berfungsi tanpa perubahan.
- Abstraksi `_RateStore(prefix)` + `_get_redis()` lazy singleton; key `bpf_rl:{prefix}:{ip}`. (ISO/IEC 27001 A.8.5 · A.12.6)
- Terverifikasi: `redis-cli` menunjukkan key `bpf_rl:pin:*` terbentuk dari percobaan gagal nyata.
- **Fix bug e2e**: nilai key lock Redis awalnya tersimpan sebagai `now` (bukan `now + lockout`) sehingga `check()` menganggap lock sudah lewat → lockout tidak efektif di path Redis. Diperbaiki & dibuktikan: 8x gagal → `allowed: False, retry_after: 599` di Redis nyata.

### 🛡 Verifikasi Mendalam Lengkap di SPA — Anomali ML & Perbaikan Data

- **🛡 Verifikasi Anomali** (pengganti rute klasik): transaksi ber-flag anomali ML kini bisa diverifikasi langsung dari modal SPA — centang konfirmasi (wajib), tandai error MyPertamina, upload foto MyPertamina opsional → `POST /api/queue/verify/<id>` (role ga/admin, pelaku dari session). Tanpa konfirmasi → 422 (ISO 9001 · kontrol proses).
- **✏️ Edit / Perbaikan Data** (pengganti form klasik modify): kendaraan, BBM, nominal, ODO, SPBU → `POST /api/queue/modify/<id>` (role ga/admin), status menjadi `modified` untuk review ulang.

### 🔍 Audit SQL Injection Menyeluruh

- Di-scan **semua** `cursor.execute`/`conn.execute` di `modules/` dengan script `scripts/audit_sql.py` (berkelanjutan di CI/codebase).
- **Hasil: 0 celah** — semua nilai input user lewat placeholder `%s`; f-string hanya menginterpolasi fragment whitelist statis (`wc`, `cash_where`, `cols`). Parameterisasi penuh (OWASP A03 · ISO/IEC 27001 A.8.26).

### 🧪 Cakupan Pengujian

- **Vitest 47 test** (naik dari 44) — AdminDashboard +3: verifikasi anomali tanpa konfirmasi tidak mengirim API, verifikasi anomali mengirim FormData ke `/api/queue/verify`, edit mengirim `/api/queue/modify`.
- **pytest 77 test** (naik dari 70) — `tests/test_rate_limit.py` (7 test): store fallback memori, prefix terpisah, lockout login 5x & pin 8x, sukses mereset.
- Smoke e2e: redis connected + ping ✅, verify-pin salah → 401 & key Redis terbentuk ✅, verify/modify tanpa auth → 401 ✅, app/ & driver 200 ✅.

---

## [2.2.3] - 2026-08-11

### 🔐 Audit Keamanan Menyeluruh — 5 Celah Berbahaya Diperbaiki

1. **Upload file (CRITICAL) — path traversal & stored XSS** — `save_file` sebelumnya menyimpan nama file asli user tanpa sanitasi (celah `../`) dan tanpa whitelist ekstensi; file `.html`/`.svg`/`.py` yang diunggah driver bisa dieksekusi saat diakses via `/uploads/`. Kini: `secure_filename` + ekstensi whitelist (gambar & PDF saja) + nama file dibangkitkan server-side (acak) + header `X-Content-Type-Options: nosniff` & `Content-Disposition: inline` pada `/uploads/`. (ISO/IEC 27001 A.8.2 · A.8.9)
2. **SECRET_KEY hardcoded di repo publik** — siapa pun bisa memalsukan cookie sesi admin. Kini diambil dari `.env` (gitignored) via `SECRET_KEY=${SECRET_KEY:?}` di `docker-compose.yml`; nilai acak baru sudah di-generate di server (semua sesi lama di-invalidasi — wajib login ulang sekali).
3. **`/api/verify-pin` tanpa proteksi brute-force** — PIN 6 digit bisa ditebak bebas. Kini rate limit per-IP: 8 gagal / 5 menit → lockout 10 menit (jalur terpisah dari login).
4. **IDOR pada `/api/cash/delete`** — driver bisa menghapus pengajuan DRAFT driver lain. Kini tanpa sesi wajib `?driver=` yang cocok dengan pemilik (403 jika bukan miliknya), konsisten dengan `history`/`pending-lpj`.
5. **Rate limit bisa dibypass via `X-Forwarded-For` palsu** — login & verify-pin memakai nilai pertama header yang dikontrol penuh klien. Kini helper `client_ip()`: `CF-Connecting-IP` **hanya dipercaya bila `remote_addr` loopback/private** (jalur cloudflared tunnel) → jika origin diakses langsung dari IP publik, CF palsu diabaikan & dipakai `remote_addr` (peer TCP nyata); XFF diabaikan total. Dipakai seragam di login, verify-pin, & audit SPA.
6. **Klaim/LPJ tanpa bukti saat foto ditolak** — sebelumnya jika `save_file` menolak file berbahaya, transaksi tetap tersimpan tanpa foto. Kini server menolak transaksi (flash error di PWA driver / 400 di LPJ) jika foto wajib gagal disimpan — termasuk **foto dispenser (wajib utk SPBU non-rekanan)** + pembersihan file yatim yang sudah tersimpan. (ISO 9001:8.6)
7. **Hardening tambahan** — header `nosniff` pada seluruh respon upload; template bebas `render_template_string` (terverifikasi); `deleteCash` PWA driver kini mengirim `?driver=` konsisten dengan guard IDOR. Catatan desain: kasus "foto tidak dikirim sama sekali" sengaja tidak ditolak server karena alur offline PWA (sync.js) mengirim tanpa foto.

### 🔍 Verifikasi Mendalam di SPA — Modal Detail Transaksi

- **Tombol 👁 Detail** di setiap baris antrean membuka modal: info transaksi lengkap (driver, nopol, BBM, nominal, liter, ODO, km/L, status, alasan tolak), **foto bukti** (thumbnail → buka di tab baru), **hasil cross-check** (health score, budget %, selisih ODO, flag, rekomendasi), plus riwayat pelaku (GA/finance/arsip).
- Aksi dari modal: **Approve / Tolak / Cairkan / Arsipkan / ↩️ Unverify / 🗑 Hapus** (admin) sesuai status & role.
- Backend baru: `GET /api/transactions/detail/<id>` (role ga/finance/admin), `POST /api/queue/unverify/<id>` (ga/admin), `POST /api/queue/delete/<id>` (admin — hapus transaksi + file bukti, dengan audit).

### 🧪 Cakupan Pengujian (ISO 9001)

- **Vitest naik ke 44 test** — `AdminDashboard.test.js` kini 10 test (tambah: modal detail dengan foto+cross-check, approve dari modal, hapus admin, unverify).
- **pytest naik ke 70 test** — `tests/test_upload_security.py` (9 test: traversal dinetralkan, ekstensi berbahaya ditolak, gambar/PDF diterima, nama aman) + `tests/test_client_ip.py` (5 test: CF-Connecting-IP menang atas XFF palsu via proxy lokal, CF palsu diabaikan saat origin publik, XFF diabaikan, fallback remote_addr).
- Smoke e2e: login dengan secret baru ✅, `/api/transactions/detail` 200/401 ✅, unverify/delete 401 tanpa auth ✅, `cash/delete` tanpa driver 400 ✅, verify-pin sukses via tunnel ✅.

---

## [2.2.2] - 2026-08-11

### 🚀 Antrean Kerja di SPA Dashboard (`/app/dashboard`)

- **Tab antrean real-time** — GA/Admin melihat **Antrean GA** (pending/modified), Finance/Admin melihat **Finance** (verified_ga) & **Konfirmasi Driver** (os_finance). Setiap tab menampilkan ID, driver, nopol, BBM, nominal, liter, ODO, flag anomali ML & waktu.
- **Aksi langsung dari SPA**:
  - GA/Admin → **✅ Approve** (pending → verified_ga) & **❌ Tolak** (wajib alasan, → rejected)
  - Finance/Admin → **💰 Cairkan** (verified_ga → os_finance) & **📦 Arsipkan** (os_finance → archived)
  - Notifikasi driver tetap dikirim (approved / paid / archived / rejected) + audit trail.
  - **Guard anomali ML**: transaksi ber-flag `ml_anomaly_flag` **tidak bisa di-approve cepat dari SPA** (tombol diganti "⚠️ Wajib verifikasi klasik" + backend menolak 409) — wajib verifikasi penuh dengan foto bukti di dashboard klasik (ISO 9001 · kontrol proses).
- **Backend JSON baru** di `routes_spa.py`: `GET /api/queue?tab=`, `POST /api/queue/approve-ga/<id>`, `POST /api/queue/payout/<id>`, `POST /api/queue/archive/<id>`, `POST /api/queue/reject/<id>` — semua `role_required` + CSRF, dan **nama pelaku diambil dari session** (anti audit-trail forgery, tidak seperti endpoint klasik yang menerima `?admin=` dari query).
- Verifikasi mendalam (foto bukti, cross-check, finance review, edit ODO) tetap di antarmuka klasik — tautan "Verifikasi Penuh (Klasik)" disediakan.

### 🧪 Cakupan Pengujian (ISO 9001)

- **Vitest naik ke 41 test** — `AdminDashboard.test.js` (7: kartu statistik per role, tab antrean, approve, reject dengan prompt, payout, **archive**, **guard anomali ML**) & `MarketingDashboard.test.js` (3: form+stat+list, submit valid → POST array, validasi tanpa nama).
- `pytest tests/` → **56 PASS** ✅
- Smoke: `/api/queue` (admin) → JSON ✅, tanpa login → 401 ✅, POST tanpa CSRF → 400 ✅, approve tx tak ada → 409 ✅.

---

## [2.2.1] - 2026-08-11

### 🧪 Cakupan Pengujian Diperluas (ISO 9001 · proses mutu)

- **Unit test frontend (Vitest) naik ke 31 test** — tambah 19 test untuk view baru v2.2: `AnalyticsView` (kartu statistik, 3 grafik Chart.js di-mock, tabel Top 5, state error), `LogsView` (render, filter aksi/peran, badge hari ini & total), `SettingsView` (toggle driver, modal tambah driver dengan uppercase, hapus driver dengan konfirmasi, dedupe tipe kendaraan), `UsersView` (render, toggle & hapus **tanpa field pin** — proteksi PIN, tambah user dengan pin), dan `ChiefDriverDashboard` (select driver independen per-baris + assign memakai id baris yang benar).
- **Test backend (pytest) naik ke 56 test** — file baru `tests/test_user_pin_protection.py` (7 test): kontrak `resolve_user_pin` (PIN eksplisit mengganti, `None`/kosong berarti jangan ubah, strip whitespace) + fallback level-route `finalize_pin` (None → pertahankan existing, user baru → default) + alur lengkap create→toggle.

### 🐛 Perbaikan Bug

- **Chief Driver Dashboard — select driver kini per-baris** — sebelumnya satu `<select>` dibagikan ke semua baris "Belum Ditugaskan" sehingga memilih driver di satu baris mengubah semua baris; kini tiap baris punya pilihan driver sendiri (`selDriver[apptId]`).
- **Refactor `resolve_user_pin` + `finalize_pin` + perbaikan kontrak** — logika proteksi PIN diekstrak ke `modules/helpers.py`; helper keputusan mengembalikan `None` (bukan default `'123456'`) saat field `pin` tidak dikirim, dan `finalize_pin` memutuskan fallback di level route. Bug pada refactor awal (helper mengembalikan default sehingga menimpa PIN) terdeteksi oleh pengujian end-to-end: create user PIN `888444` → toggle nonaktif → PIN tetap `888444` ✅.

### 🧪 Verifikasi

- `npm test` → **31 passed** ✅ · `npm run build` → sukses ✅
- `pytest tests/` → **56 PASS** ✅ · e2e: create user + toggle nonaktif tanpa pin → PIN dipertahankan ✅

---

## [2.2.0] - 2026-08-11

### 🐛 Perbaikan Halaman Analytics SPA

- **Analytics (`/app/analytics`) diperbaiki total** — sebelumnya halaman ini salah membaca response API (`/api/analytics/data` mengembalikan `{finance, ga, cash, fleet}`, bukan array transaksi) sehingga statistik & grafik tidak tampil benar. Kini: **8 kartu statistik** (total nominal, jumlah transaksi, rata-rata/hari, rata-rata/transaksi, driver aktif, total klaim, total appointment, driver teratas, kasbon selesai, kendaraan paling efisien, rata-rata km/L), **3 grafik Chart.js** (tren nominal bulanan, frekuensi per driver, efisiensi per kendaraan), dan **tabel Top 5 driver**. Grafik digambar setelah render (fix race condition `nextTick`).

### ✨ Penyempurnaan Halaman Lainnya

- **Rekap (`/app/rekap`)** — tombol **Preview PDF** (tab baru) & **Download PDF** langsung dari SPA dengan rentang tanggal aktif (tidak perlu lagi pindah ke halaman klasik). Backend `/admin/rekap/pdf` kini mendukung `dl=1` → header `Content-Disposition: attachment` (unduhan nyata).
- **Audit Log (`/app/logs`)** — filter **aksi** & **peran** (klien-side), badge **“Hari ini”** dan **“Total tampil / total log”**, label aksi dibersihkan (underscore → judul).
- **Settings (`/app/settings`)** — **tambah driver** (modal: nama, nopol, tipe kendaraan, tipe BBM), **hapus driver permanen** (dengan konfirmasi), dan **tambah kendaraan** (modal: nopol, tipe, merk, BBM default) — menyusul toggle aktif/nonaktif yang sudah ada.
- **Manajemen User (`/app/users`)** — tombol **nonaktifkan/aktifkan** (🚫/🟢) dan **hapus user** (🗑, set nonaktif sesuai perilaku klasik), di samping edit & reset PIN.

### 🔐 Perbaikan Keamanan PIN (hasil review kode)

- **Toggle aktif/nonaktif & hapus user tidak lagi menimpa PIN** — sebelumnya `/api/users/sync` selalu mengeksekusi `pin=VALUES(pin)`, sehingga toggle status atau "hapus" user (yang mengirim `pin:'000000'`) diam-diam **mereset PIN user menjadi 000000**. Kini backend hanya mengubah PIN bila field `pin` dikirim **eksplisit dan tidak kosong** (pola sama seperti `team_name`); SPA & halaman klasik (`users.html`, `settings.html`) tidak lagi mengirim `pin` pada operasi toggle/hapus. (ISO/IEC 27001 A.8.2 · A.9.4)

### 🧪 Verifikasi

- `npm test` → 12 passed ✅ · `npm run build` → sukses ✅
- `pytest tests/` → 49 PASS ✅ · CI GitHub Actions hijau pada v2.1 ✅
- Smoke: `/api/analytics/data` (sesi admin) → JSON `{finance, ga, cash, fleet}` ✅ · `/admin/rekap/pdf` → PDF inline, dengan `dl=1` → attachment ✅

---

## [2.1.0] - 2026-08-11

### ✨ Fitur Baru

- **Halaman Kasbon/BBM di SPA (`/app/cash`)** — workflow kasbon lengkap (sebelumnya hanya ada di antarmuka klasik): kode unik harian (Finance set saat mode manual), daftar pengajuan dengan progress bar status, **GA Approve → Finance Approve → Serahkan ke Driver**, tolak (wajib alasan), edit nominal, hapus (DRAFT), batal (reset ke DRAFT), verifikasi/tolak LPJ, reset LPJ. Menu & route dibatasi role `ga/finance/admin` (guard router + `role_required` di server).
- **Notifikasi real-time di SPA** — bell 🔔 dengan badge unread + toast popup: GA/Finance/Admin menerima `new_claim` & `new_trip_report` saat driver mengirim laporan; Marketing & Chief Driver join room `appointments_board` dan menerima `appointment_update` real-time. Indikator ⚡/🔴 status koneksi tetap ada di topbar.
- **PWA untuk SPA** — `/app/` kini installable (manifest `manifest.webmanifest`, ikon, `theme-color`) + service worker khusus `sw.js` (scope `/app/`): app-shell di-cache saat install, navigasi network-first dengan fallback offline ke `index.html`, asset ber-hash cache-first. `sw.js` driver klasik diperbaiki agar **tidak lagi menghapus cache SPA** (kini hanya membersihkan cache `bpf-bbm-*`).
- **CI/CD (GitHub Actions)** — workflow `.github/workflows/ci.yml`: job Frontend (npm ci → `npm test` → `npm run build`) dan job Backend (`pip install -r requirements.txt` → `pytest tests/`) — otomatis di setiap push ke `main` dan pull request.
- **Unit test frontend (Vitest)** — 12 test: guard router per role (login redirect, forbidden, akses role, halaman publik) + auth store (login simpan user & CSRF, bootstrap sesi, logout bersih). Jalan via `npm test` dan di CI.

### 🔐 Hardening Akses (ISO/IEC 27001 A.8.2)

- `/api/cash/history`, `/api/cash/pending-lpj`, dan `/api/cash/detail/<id>` sebelumnya **bisa dibaca tanpa login** (data kasbon semua driver terekspos). Kini: tanpa sesi (PWA driver) **wajib filter `driver`** (400 jika kosong — hanya data miliknya), sedangkan admin/GA/Finance dengan sesi tetap akses penuh; `/api/cash/detail` kini `role_required(['ga','finance','admin'])`.

### 🧪 Verifikasi

- `npm test` → **12 passed** ✅ · `npm run build` → sukses (CashView + manifest + sw.js tersalin ke `dist/`) ✅
- `pytest tests/` → 49 PASS ✅ · smoke: `/api/cash/history` tanpa sesi → 400, dengan `?driver=` → 200, tanpa sesi `/detail` → 401, dengan sesi admin → 200 ✅

---

## [2.0.0] - 2026-08-11

### 🎉 SPA Vue 3 + Dashboard per Role

- **Antarmuka admin/back-office ditulis ulang sebagai SPA Vue 3 (Vite + vue-router + pinia)** di `/app/*` — responsif, lazy-loading per view, dark mode, indikator realtime.
- **Dashboard terpisah per role setelah login**: Admin/GA/Finance (kartu statistik relevan dari `/api/stats` + aksi cepat), **Marketing** (input appointment + ringkasan harian), **Chief Driver** (board penugasan + rekap Excel).
- **Kontrol akses berlapis (ISO/IEC 27001 · least privilege)**: guard router per role (`meta.roles`) + menu sidebar terfilter + halaman 403; server tetap `role_required` di semua API. Matriks hak akses terdokumentasi di `SECURITY.md`.
- **Auth JSON baru**: `GET /api/auth/me`, `POST /api/auth/login`, `POST /api/auth/logout` (session + CSRF). Login klasik tetap berfungsi dan kini mengarah ke dashboard role masing-masing di SPA.
- **API JSON baru**: `GET /api/trips` (list + filter), `POST /api/trips/verify/<id>`, `POST /api/trips/reject/<id>`.
- **View SPA**: Log Perjalanan (detail + verify/reject), Assignments (assign/lepas), Rekap (filter tanggal), Analytics (Chart.js), Manajemen User (tambah/edit/reset PIN), Audit Log, Pengaturan (driver/kendaraan/BBM).
- **Dockerfile multi-stage**: Stage 1 build SPA (node:20-alpine), Stage 2 runtime Python; `docker-compose` tidak berubah. Karena `./static` di-bind-mount ke container, hasil build SPA juga disalin ke `static/app/` di host via `scripts/build-spa.sh` (lihat `DEPLOYMENT.md` §12.1).
- **Hardening keamanan (ISO/IEC 27001 A.8.5)**: rate limiting login anti brute-force (5x gagal/5 menit → lockout 15 menit, per-IP, berlaku di login klasik & JSON); cookie sesi kini `HttpOnly` + `SameSite=Lax` + `Secure` (HTTPS) dengan masa berlaku 12 jam (`SESSION_HOURS`); `verified_by` trip diambil dari session (anti audit forgery — input klien tidak dipercaya); `.dockerignore` memperkecil build context; cache header SPA (asset ber-hash immutable, `index.html` no-cache).
- **Dokumentasi ISO**: `SECURITY.md` — pemetaan ISO/IEC 27001:2022 (kontrol akses A.5.15/A.8.2/A.8.5/A.8.15/A.8.28), ISO 9241-11 (usability), dan proses ISO 9001 (mutu & rilis).
- Halaman klasik (driver PWA `/driver`, antrean kerja `/admin`, GA assignments, dll.) **tetap berjalan** — SPA menyediakan tautan transisi ke antarmuka klasik.

### 🧪 Verifikasi

- `cd frontend && npm run build` → sukses (34 modul, semua view lazy-loaded) ✅
- `pytest tests/` → 49 PASS ✅
- Smoke test: `/app/` melayani SPA, `/api/auth/me` & `/api/auth/login` (JSON) ✅ · halaman klasik & WebSocket tetap OK ✅

---

## [1.2.3] - 2026-08-11

### 🐛 Perbaikan

- **Notifikasi real-time driver (WebSocket) — 2 akar masalah**:
  1. **Nginx reverse proxy tidak meneruskan header WebSocket**: produksi via `https://nasbpfsby.duckdns.org:5000` lewat nginx (container `nextcloud_nginx`) tanpa `Upgrade`/`Connection` — upgrade `wss://` gagal (`400 Bad Request` di browser, `Invalid transport for session <sid>` di log `bbm_web`). Ditambahkan `proxy_http_version 1.1`, `proxy_set_header Upgrade $http_upgrade`, `proxy_set_header Connection "upgrade"`, `proxy_buffering off`, dan timeout panjang di `bbm_system.conf` → handshake kini `101 Switching Protocols`.
  2. **Bug kritis room join (`modules/realtime.py`)**: handler `join_driver`/`join_room` memanggil `sio.enter_room` yang **tidak ada** di wrapper flask-socketio (yang benar `sio.server.enter_room`) → setiap join melempar `'SocketIO' object has no attribute 'enter_room'` → notifikasi **tidak pernah terkirim real-time** meski WebSocket sudah terhubung. Diganti ke `sio.server.enter_room/leave_room` + logging join & error emit (sebelumnya error ditelan diam-diam). Dockerfile kini `python3 -u` agar log `docker logs` terbaca.
- **Sinkronisasi offline driver (`static/js/sync.js`) diperbaiki**: item `fuel_queue` dikirim ke endpoint LPJ yang salah (`/api/cash/submit-lpj/undefined`) dan antrean `lpj_queue` tidak pernah tersinkron. Kini 3 antrean tersinkron ke endpoint yang benar: BBM → `POST /driver`, LPJ → `POST /api/cash/submit-lpj/<id>`, trip → `POST /submit-trip` (dengan guard `try/finally`).
- **Batal kasbon (`POST /api/cash/cancel/<id>`) diperbaiki**: update status ke `DRAFT` hanya terjadi untuk status `FUNDS_WITH_DRIVER` (ada juga query duplikat) — untuk status lain (DRAFT/GA_APPROVED/FINANCE_APPROVED/LPJ_SUBMITTED) status **tidak pernah berubah** padahal respons mengaku berhasil. Kini satu `UPDATE` bersih men-set status + membersihkan semua penanda approve/handover/LPJ untuk semua status yang bisa dibatalkan (terungkap saat uji E2E notifikasi).

### ✨ Peningkatan

- **Indikator koneksi realtime di PWA driver**: status bar kini menampilkan ⚡/🔴 status koneksi WebSocket (Socket.IO) + reconnect otomatis yang lebih eksplisit (`reconnection`, `reconnectionAttempts`).
- Bump cache service worker (`bpf-bbm-20260811b`) & versi asset agar perangkat driver otomatis mengambil versi baru.

### 🌐 Infrastruktur & Dokumentasi

- Produksi kini memakai **domain permanen DuckDNS `https://nasbpfsby.duckdns.org:5000`** (nginx reverse proxy + Let's Encrypt). Service `cloudflared` (quick tunnel `*.trycloudflare.com`) **dinonaktifkan** di `docker-compose.yml` (opsional, bisa diaktifkan kembali).
- README, USER_GUIDE, dan DEPLOYMENT diperbarui: semua URL diganti ke domain DuckDNS, dokumentasi config nginx WebSocket + troubleshooting ditambahkan.

### 🧪 Verifikasi

- WebSocket handshake via domain publik: `101 Switching Protocols` ✅
- Uji end-to-end notifikasi real-time: login GA → buat kasbon test → client WebSocket join room driver → GA approve → **`driver_notification` diterima real-time via domain publik** ✅ (data test dibersihkan)
- `node --check` semua JS driver ✅ · `pytest tests/` → **49 passed** ✅

---

## [1.2.2] - 2026-08-07

### ✨ Fitur Baru

#### 🗺️ Jadwal Appointment Saya di PWA Driver
- Driver kini melihat **semua appointment yang ditugaskan padanya** (status Ditugaskan + Selesai) di panel **"Jadwal Appointment Saya Hari Ini"** pada tab Trip — bukan hanya yang sudah selesai.
- Setiap kartu: nama nasabah, alamat, area, marketing anggota, badge status, tombol **📞 Telepon** (tel:) dan **🌍 Buka Google Maps** (navigasi sekali ketuk).
- **Notifikasi realtime ke driver** saat Chief Driver menugaskan/mencabut appointment (reuse `push_driver_notification` + room `driver_<nama>`); panel ikut refresh otomatis.
- **Auto-complete via log perjalanan**: driver bisa **memuat rute sebelum berangkat** (📥 Muat Semua ke Rute kini mencakup appointment yang ditugaskan); saat log perjalanan di-submit, appointment yang dirujuk **otomatis menjadi ✅ Selesai** (+ notifikasi marketing & board real-time, audit `appointment_complete_by_trip`).
- Endpoint baru `GET /api/appointments/driver-today?driver=&date=` (scope hanya appointment milik driver tsb).
- Tombol **🏁 Selesai Dikunjungi** di kartu appointment yang ditugaskan — driver bisa mengonfirmasi kunjungan **tanpa submit log perjalanan** (endpoint `POST /api/appointments/driver-complete/<id>`, verifikasi driver pemilik + status assigned, notifikasi marketing & board real-time, audit `appointment_driver_complete`).

#### 🎯 Hasil Kunjungan (Data Konversi Marketing)
- Saat driver menekan **🏁 Selesai Dikunjungi**, muncul **modal hasil kunjungan** — wajib pilih **😊 Ditemui / 🤝 Prospek / ❌ Gagal** + **alasan/catatan** opsional → tersimpan di `appointments.visit_result` & `appointments.visit_note`.
- Notifikasi marketing kini menyertakan hasil kunjungan (mis. *"Driver AKHAD selesai mengunjungi Budi (APP-...) — 😊 Ditemui"*).
- Badge hasil kunjungan tampil di: **panel PWA driver**, **board Chief Driver** (Appointment Selesai), dan **daftar marketing** (bersama alasan 📝).
- **Ringkasan per Marketing Anggota** di Chief Driver bertambah kolom konversi **😊 Ditemui / 🤝 Prospek / ❌ Gagal** — data konversi marketing terukur per anggota.
- **Rekap Excel** harian bertambah kolom **Hasil Kunjungan** + **Alasan** + ringkasan konversi di footer.
- Chief Driver juga bisa mencatat hasil (opsional) lewat tombol ✅ Selesai, atau **mengisi/mengubah hasil kunjungan kapan saja** lewat endpoint PATCH — termasuk appointment yang selesai otomatis lewat log perjalanan (sebelumnya hasilnya NULL permanen). Audit `appointment_result_edit` + real-time ke board.
- Logika finalisasi di-share (`_finalize_appointment_complete` + validasi nilai di `VISIT_RESULTS`); semua badge hasil di-render dari map tetap (anti-XSS).

### 🛠 Perbaikan
- **Bug pra-ada diperbaiki**: kolom `trip_masters.display_id` tidak ada di `init.sql` (kode sudah memakainya sejak lama) — database fresh akan gagal saat submit trip. Kini ditambahkan di `init.sql` + migrasi guarded + **backfill otomatis** untuk trip lama.
- Unit test & smoke test end-to-end: 49 test PASS + 38 check smoke (assign → lihat → trip → auto-complete → selesai dikunjungi → hasil kunjungan → agregasi konversi).

---

## [1.2.1] - 2026-08-07

### ✨ Fitur Baru

#### 👤 Nama Marketing Anggota per Appointment
- Kolom baru `appointments.marketing_member` + tabel `marketing_members` (auto-register saat input).
- Satu akun marketing (level manager, mis. Icang Tim Yusie) bisa input appointment untuk **banyak anggota tim** — wajib mencantumkan **nama marketing yang memprospek**.
- Form & modal edit marketing: field **Nama Marketing** dengan **datalist saran** (nama anggota yang sudah pernah dipakai di tim tersebut).
- Kartu appointment (Marketing & Chief Driver) menampilkan badge 👤 nama marketing anggota; kolom baru **"Marketing Anggota"** di Rekap Excel harian.
- Endpoint baru `GET /api/marketing/members?team=...` untuk daftar anggota per tim.

#### 🌍 Override Area Manual oleh Chief Driver
- Tombol 🌍 di kartu appointment (Belum Ditugaskan & Tugas Per Driver) → Chief Driver/GA/Admin bisa **mengubah area hasil deteksi otomatis** secara manual (mis. koreksi zona, alamat daerah baru).
- Perubahan area terekam di audit log (`appointment_area_edit`) + real-time ke board.

#### 👤 Filter Marketing Anggota di Chief Driver
- **Filter bar "Marketing Anggota"** di halaman Chief Driver: dropdown berisi semua anggota lintas tim (dari `marketing_members`), mendukung pencarian parsial.
- Board, kartu statistik, dan **Rekap Excel** otomatis ikut terfilter per anggota — memudahkan evaluasi per anggota tim.
- Backend: param `member` (LIKE) di `GET /api/appointments` (list + stats) dan `GET /api/appointments/export`; `GET /api/marketing/members` tanpa `team` kini mengembalikan semua anggota (untuk dropdown chief driver).

#### 📊 Ringkasan per Marketing Anggota
- Panel **"Ringkasan per Marketing Anggota"** di header board Chief Driver: tabel Total / ⏳ Menunggu / 🚗 Ditugaskan / ✅ Selesai / ✕ Batal / 🌅 Sesi 1 / 🌆 Sesi 2 per anggota (per tanggal terpilih, urut total terbesar).
- **Klik baris anggota** → otomatis menerapkan filter board ke anggota tersebut (baris aktif ditandai).
- Endpoint baru `GET /api/appointments/member-summary?date=...` (agregasi GROUP BY `marketing_member`).

### 🛠 Perbaikan
- Validasi `validate_appointment_input` kini mewajibkan `marketing_member` (dipakai di POST & PATCH).
- Unit test diperbarui: 8 test validasi input dengan member + 1 test baru wajib member.

---

## [1.1.0] - 2026-08-06

### ✨ Fitur Baru

#### 🔐 Autentikasi & Keamanan
- **Login / Logout session-based**: halaman `/login` (username + PIN 6 digit dari tabel `users`), tombol **🚪 Keluar** di navbar semua halaman admin.
- **Role-Based Access**: 66 endpoint dilindungi `@role_required` (admin/ga/finance). Halaman tidak berhak → redirect + flash; API → JSON 401/403.
- **CSRF Protection**: token CSRF di semua form POST + header `X-CSRF-Token` diinjeksi otomatis oleh fetch wrapper (`theme.js`, `admin-ui.js`). Endpoint PWA driver di-exempt agar driver tetap berjalan tanpa login.
- **Anti Open-Redirect**: parameter `next` pada login disanitasi (hanya redirect internal) + di-URL-encode; dipertahankan saat login gagal.
- **Konversi GET → POST** untuk semua aksi state-changing: `/ga/approve`, `/finance/payout`, `/finance/archive`, `/admin/unverify`, `/admin/delete`, `/admin/trips/verify` (GET kini 405).

#### 🔔 Notifikasi Driver Real-Time
- Modul baru `realtime.py` (SocketIO bus + per-driver rooms) dan `notifications.py` (persist + push).
- Driver menerima notifikasi langsung saat transaksi/kasbon-nya diproses (approve, payout, handover, reject, dsb).
- Notifikasi tersimpan di tabel `notifications` → offline catch-up (muncul saat driver kembali online).
- API baru: `GET /api/notifications?driver=...` dan `POST /api/notifications/read`; badge unread di PWA driver.

#### 👥 Manajemen Pengguna
- Halaman baru **`/admin/users`** (admin-only): lihat, tambah, ubah role, aktif/nonaktifkan pengguna, reset PIN.
- Link "Users" di navbar 7 halaman admin.

#### 🌙 Dark Mode
- Toggle 🌙/☀️ di semua halaman admin + login (dashboard, analytics, rekap, settings, logs, trips, GA assignments, users).
- Preferensi di `localStorage` (key `adminDark`), diterapkan inline di `<head>` untuk mencegah flash.
- Chart.js analytics menyesuaikan warna grid/label + re-render otomatis.

#### 🖥️ Dashboard Admin UX
- **SPA tab switching** tanpa reload (fragment HTML `/admin/queue-fragment/<tab>` + history API + popstate).
- **Sticky context bar**: ringkasan "Hari Ini" (jumlah transaksi, nominal, status, indikator koneksi) selalu terlihat.
- **Skeleton loading** (shimmer) saat berpindah tab.
- **Bulk action GA**: "✅ Tandai Semua Dicek" (approve massal + PIN + ringkasan hasil).
- **Shortcut keyboard** `1`–`5` untuk pindah tab; `focus-visible` outline; `aria-label`/`role=tab`.
- **Count-up animation** angka statistik.
- **Cari langsung di antrean** tanpa reload.

#### 📦 Arsip Cerdas
- Filter search/start_date/end_date/bbm_type + pagination di tab Arsip (`_queue_txs` menghormati URL params, default 7 hari terakhir, LIMIT 50).
- Tombol **"Muat Lebih Banyak"** (load-more) tanpa reload.
- Fragment arsip jauh lebih ringan (157KB → 22.8KB pada default window).

### 🛠 Refactor & Pembersihan
- **JS modular**: `admin.js` dipecah → `admin-ui.js`, `admin-dashboard.js`, `admin-tabs.js`, `admin-cash.js`; baru `driver.js`, `theme.js`, `notifications.js` (total 12 modul JS).
- **CSS per halaman**: `base.css` + 8 file CSS per halaman, konsolidasi duplikasi, dukungan dark mode.
- Tabel `notifications` ditambahkan ke `init.sql` + auto-create/auto-prune (30 hari) saat startup.
- `modules/realtime.py` & `modules/notifications.py` sebagai service layer baru.
- Pembersihan dead code (query V1.1 yang tak terpakai, blok duplikat di excel_generator, `except:` polos → `except Exception`).

### 🐛 Perbaikan Bug
- `?page=-3` pada arsip → OFFSET negatif → di-clamp `max(1, ...)`.
- Race condition popstate → guard `_switchingTab`.
- Import test yang salah (eventlet monkey-patch crash saat pytest collection) → diarahkan ke `modules.helpers`.
- `unique_cents` kasbon dipertahankan.
- Duplikat `@keyframes pulse`/body background di CSS dirapikan.

### 🧪 Test
- 29 test PASS: `test_cash_and_workflow.py`, `test_driver_context.py`, `test_excel_generator.py` (baru).

---

## [1.2.0] - 2026-08-07

### ✨ Fitur Baru: Sistem Appointment Canggih

#### 📣 Halaman Marketing (`/marketing`)
- Role baru **marketing** (mis. Icang dari Tim Yusie): login PIN → langsung ke halaman input appointment.
- **Form multi-input**: bisa isi 2+ appointment sekaligus dalam satu submit (nama calon nasabah, no. HP, alamat, catatan).
- **Sesi toggle**: Sesi 1 (🌅 08.30) & Sesi 2 (🌆 14.30) — menentukan slot perjalanan.
- **Deteksi area otomatis**: sistem mengenali zona wilayah dari alamat (Darmo, Rungkut, Sidoarjo, dsb.) sebagai preview + data untuk Chief Driver.
- Statistik harian, filter sesi, edit/batal (sebelum ditugaskan), notifikasi real-time saat driver ditugaskan/diproses.

#### 🚛 Halaman Chief Driver (`/chief-driver`)
- Role **chief_driver** (+ GA/Admin) — command center pembagian driver.
- **Board Belum Ditugaskan** per sesi dengan **saran driver sistem** (load-balancing: driver dengan beban paling ringan pada sesi itu).
- **Tugas Per Driver**: lihat jadwal lengkap per driver, tandai ✅ Selesai, 🔄 ganti driver, ↩️ batalkan penugasan, ✕ batalkan appointment.
- **Unduh Rekap Excel** harian (openpyxl) + ringkasan status.
- Board real-time (Socket.IO) — semua perubahan langsung terlihat.

#### 🔗 Integrasi Log Perjalanan
- Appointment yang **selesai** otomatis tersedia di form **Trip** PWA driver pada tanggal yang sama.
- Tombol **"📥 Muat Semua ke Rute"**: rute (lokasi tujuan = alamat nasabah, pukul = jam sesi) terisi otomatis ke `trip_details`.
- `trip_details.appointment_id` menyimpan referensi; badge **"📅 APP-xxxx · nama nasabah"** muncul di detail Trip Review.
- Notifikasi marketing real-time: driver ditugaskan / selesai / penugasan dibatalkan.

#### 👥 User & Teams
- Role dropdown Users: **Marketing** + **Chief Driver**; field **Tim Marketing** (ketik nama tim baru → auto-register ke `marketing_teams`).
- Login redirect berbasis role: marketing → `/marketing`, chief_driver → `/chief-driver`.

### 🧪 Test
- Test baru `test_appointments.py`: deteksi area, sesi, validasi input, display ID (12 test).

---

## [1.0.0] - 2026-07-30

Versi awal yang diluncurkan ke produksi.

### ✨ Fitur
- Modul **Kasbon** (Cash Request) dengan kode unik harian Rp 100–2.000.
- Workflow lengkap DRAFT → GA → Finance → Handover → LPJ → Completed.
- **PWA Offline-First** driver (IndexedDB + auto-sync + watermark foto GPS).
- **GA Assignments**: assign, swap, release dengan audit trail.
- **Cross-Check Verifikasi** (Health Score + Flags + Budget).
- **Finance Review Panel** split-screen + ODO edit + Archive ZIP.
- **PDF enterprise** (FPDF + DejaVu Sans, kop surat, grid foto 2×2) & **Excel export**.
- **Chart.js Analytics** 3-tab + deteksi anomali ML (Isolation Forest).
- Audit trail 30+ tipe aksi, PIN 6 digit, parameterized SQL.

---

[1.2.3]: https://github.com/bestprofitsurabaya/bpf-bbm-system/releases/tag/v1.2.3
[1.2.2]: https://github.com/bestprofitsurabaya/bpf-bbm-system/releases/tag/v1.2.2
[1.2.1]: https://github.com/bestprofitsurabaya/bpf-bbm-system/releases/tag/v1.2.1
[1.1.0]: https://github.com/bestprofitsurabaya/bpf-bbm-system/releases/tag/v1.1.0
[1.0.0]: https://github.com/bestprofitsurabaya/bpf-bbm-system/releases/tag/v1.0.0
