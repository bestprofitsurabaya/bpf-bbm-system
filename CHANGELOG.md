# 📋 Changelog

Semua perubahan penting pada **BPF Fleet & BBM System**.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/ID/1.0.0/) dan versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

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
