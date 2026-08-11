# 📋 Changelog

Semua perubahan penting pada **BPF Fleet & BBM System**.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/ID/1.0.0/) dan versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

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
