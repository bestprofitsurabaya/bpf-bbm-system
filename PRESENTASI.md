# 🎤 Materi Presentasi — BPF Fleet & BBM System

> **Panduan demo lengkap**: urutan sudah disusun dari yang paling berkesan ke yang paling teknis.
> Tiap bagian berisi: tujuan, yang diklik di layar, poin yang dibicarakan, dan "satu kalimat kunci".
> Total durasi fleksibel — **demo inti ±15 menit**, versi lengkap ±30 menit.
> 🖥️ **Slide deck interaktif**: buka `presentasi/index.html` di browser (navigasi → ←, tekan **N** untuk catatan pembicara, **Ctrl+P** untuk cetak/PDF).
> 📄 **Versi PDF siap bagikan**: `presentasi/BPF_Fleet_BBM_System_Presentasi.pdf` (12 halaman landscape A4, tanpa catatan pembicara).
> 🧪 **Data demo**: sudah diisi di database (label `DEMO` — air minum, klaim BBM, kasbon, trip, appointment). Bersihkan dengan `scripts/demo_cleanup.sql`.

---

## 🧭 Peta Presentasi (urutkan prioritas)

| # | Bagian | Durasi | Mengapa di sini |
|---|--------|--------|-----------------|
| 0 | Pembuka: cerita masalah | 2 mnt | Menyentuh, audiens paham konteks |
| 1 | Satu aplikasi, semua peran | 2 mnt | Gambaran besar sebelum detail |
| 2 | **Demo: Air Minum (OB → Finance)** | 3 mnt | Fitur terbaru, unik, mudah dipahami |
| 3 | **Demo: Dashboard per peran** | 3 mnt | Menunjukkan pemisahan hak akses |
| 4 | **Demo: Klaim BBM + Kasbon + Kode Unik** | 3 mnt | Alur uang — inti bisnis |
| 5 | **Demo: Realtime & notifikasi** | 2 mnt | "Wow factor", teknologi terasa |
| 6 | **Demo: Driver PWA offline** | 2 mnt | Relevan untuk pengguna lapangan |
| 7 | **Demo: Marketing & Chief Driver** | 2 mnt | Fitur pendukung penjualan |
| 8 | Keamanan & tata kelola | 3 mnt | Menjawab kekhawatiran pengambil keputusan |
| 9 | Kualitas & kepatuhan | 2 mnt | Bukti kredibilitas teknis |
| 10 | Penutup: nilai & langkah berikutnya | 2 mnt | Ajakan bertindak |

---

## 0️⃣ Pembuka — "Cerita dari Lapangan" (2 menit)

> Buka dengan cerita, bukan dengan fitur. Cerita membuat orang menempel.

**Skrip usulan (boleh diparafrase):**
> "Coba bayangkan seorang sopir yang habis isi bensin Rp 300 ribu. Dia bayar pakai uang sendiri dulu. Setibanya di kantor, dia harus mengantre laporan, menyerahkan struk, lalu menunggu berhari-hari uangnya diganti. Di sisi lain, tim Finance harus mengecek satu per satu struk, merekap manual di Excel, dan bertanya-tanya: 'uang yang saya transfer ini untuk yang mana ya?'
>
> Di kantor, OB membeli galon air minum, dan tidak ada bukti resmi kapan dan berapa yang dibeli.
>
> Hari ini, semua itu kami rapikan dalam satu aplikasi — **BPF Fleet & BBM System**."

**Satu kalimat kunci:**
> *"Dari 'catat di kertas, rekap di Excel' menjadi 'satu aplikasi, semua tercatat otomatis, semua bisa diaudit'."*

---

## 1️⃣ Satu Aplikasi, Semua Peran (2 menit)

**Yang ditampilkan:** halaman Login → masuk sebagai Admin.

**Poin yang dibicarakan:**
- Satu aplikasi yang dipakai **semua orang di perusahaan** — sopir, OB, GA, Finance, Marketing, Chief Driver, dan Admin.
- Setiap orang **masuk dengan Username + PIN 6 digit**, dan langsung dibawa ke **halamannya masing-masing**.
- Tidak ada yang tercampur: sopir tidak bisa melihat rekap keuangan, OB tidak bisa melihat klaim BBM. **Setiap orang hanya melihat menu yang menjadi tugasnya.**

**Satu kalimat kunci:**
> *"Satu aplikasi untuk semua, tapi setiap orang melihat dunianya sendiri."*

---

## 2️⃣ Demo Utama 1 — Air Minum: OB → Finance → PDF (3 menit) 💧

> **Fitur paling baru dan paling mudah diceritakan.** Mulai dari sini karena audiens langsung paham alurnya.

**Skenario demo (siapkan 1 pengajuan contoh):**

| Langkah | Layar | Yang dilakukan | Yang dibicarakan |
|---|---|---|---|
| 1 | Login sebagai OB (`ob1` / PIN `123456`) | Masuk → otomatis ke **Halaman Air Minum** | "Tiap OB punya halaman sendiri. Nama mereka: Faisol, Febri, Edwin." |
| 2 | Form Air Minum | Isi tanggal, jumlah, pilih **jenis** (Gelas/Botol/Galon) & **merk**, unggah **foto sebelum & sesudah** | "Dua foto wajib — bukti dengan tanda waktu. Tanpa foto, pengajuan tidak bisa diproses." |
| 3 | Kirim | Klik **Ajukan** | Status berubah jadi **"Menunggu Verifikasi"**. |
| 4 | Login sebagai Finance (`finance_officer`) | Buka **Dashboard Finance** | "Finance langsung melihat antrean verifikasi — tanpa menunggu OB datang melapor." |
| 5 | Verifikasi | Periksa foto → isi **remark** → verifikasi | "Finance bisa menambah catatan — semua tercatat sebagai jejak audit." |
| 6 | PDF | Klik **📄 PDF** | "Muncul **tanda terima resmi** yang ditandatangani Finance (penyerah) dan GA (penerima). Nama mereka diatur Admin — dokumen siap arsip." |

**Satu kalimat kunci:**
> *"Dari pembelian galon sampai tanda terima resmi — tercatat, terbukti, dan bisa diaudit, tanpa kertas."*

> 💡 **Tips demo:** pastikan 2 foto contoh sudah siap di HP/komputer. Kalau tidak sempat upload, tunjukkan saja alurnya sampai form.

---

## 3️⃣ Demo Utama 2 — Dashboard per Peran (3 menit) 🧾💰

**Skenario:** login bergantian 3 akun dan tunjukkan perbedaan halamannya.

| Login sebagai | Halaman | Sorotan |
|---|---|---|
| **Admin** | Dashboard Admin | Ringkasan seluruh operasi + akses semua menu (Users, Settings, Logs) |
| **GA** | Dashboard GA | Antrean klaim + **tombol Approve/Tolak** + **🛡 Verifikasi Anomali** + kasbon + trip pending |
| **Finance** | Dashboard Finance | Rekap air minum (per OB, per jenis, per merk) + antrean verifikasi + kasbon + **Export CSV** |

**Poin yang dibicarakan:**
- **GA** bisa menyetujui atau menolak klaim **langsung dari dashboard-nya** — alasan penolakan wajib diisi (jejak audit).
- Klaim bertanda ⚠️ (anomali) punya alur verifikasi khusus.
- **Finance** punya rekap lengkap dengan filter tanggal dan **tombol export ke Excel** — tidak perlu rekap manual lagi.
- Ini prinsip **least privilege**: admin boleh melihat semua, tapi GA dan Finance hanya melihat wilayah tugasnya.

**Satu kalimat kunci:**
> *"Setiap peran punya dashboard sendiri — pekerjaan selesai dari satu halaman, bukan berpindah-pindah menu."*

---

## 4️⃣ Demo Utama 3 — Klaim BBM, Kasbon & Kode Unik (3 menit) 🚗💰

**Skenario:** ceritakan alur "bayar dulu, ganti belakangan" dengan 4 peran.

| Langkah | Peran | Alur |
|---|---|---|
| 1 | **Driver** | Ajukan klaim BBM + foto struk → masuk antrean GA |
| 2 | **GA** | Approve → klaim pindah ke Finance |
| 3 | **Finance** | Cairkan dana → status "Diserahkan" |
| 4 | **Driver** | Isi **LPJ** (laporan pertanggungjawaban) |
| 5 | **GA** | Verifikasi LPJ → **Selesai 🎉** |

**Sorotan: Kode Unik Kasbon**
> "Saat driver mengajukan kasbon Rp 100.000, sistem otomatis menambahkan **kode unik** — misalnya menjadi Rp 100.023. Saat Finance mentransfer, nominal persis itu yang menjadi bukti: *uang ini untuk kasbon siapa*. Tidak ada lagi tebak-tebakan. Angka recehnya ditentukan Finance setiap hari."

**Satu kalimat kunci:**
> *"Setiap rupiah tercatat — dari pengajuan, persetujuan, pencairan, sampai pertanggungjawaban. Tidak ada celah 'saya tidak tahu itu untuk apa'."*

---

## 5️⃣ Demo Utama 4 — Realtime & Notifikasi (2 menit) ⚡

**Skenario:** buka Dashboard GA dan Dashboard Finance **bersebelahan** (2 tab browser), lalu:
1. Login OB di tab 3 → buat pengajuan air minum.
2. Lihat: di tab Finance muncul **toast 💧** + lonceng 🔔, dan antrean **ter-refresh sendiri tanpa muat ulang**.
3. (Opsional) driver kirim klaim → antrean GA ikut refresh.

**Poin yang dibicarakan:**
- Semua perubahan berjalan **real-time** via WebSocket.
- Indikator **⚡ Realtime** di pojok kanan atas — kalau putus, muncul 🔴.
- Artinya: Finance tahu ada pengajuan **saat itu juga**, bukan besok pagi.

**Satu kalimat kunci:**
> *"Aplikasi ini 'hidup' — begitu ada yang mengajukan, yang berwenang langsung tahu, tanpa menunggu laporan."*

---

## 6️⃣ Demo Utama 5 — Driver PWA: Offline di Jalan (2 menit) 📱

**Skenario:** buka `/app/driver` (bisa di mode ponsel DevTools).

**Poin yang dibicarakan:**
- Driver **login dengan PIN** — identitasnya otomatis menempel di semua laporan (tidak bisa mengaku-ngaku orang lain).
- 4 tab: **⛽ BBM · 💰 Kasbon · 🗺️ Trip · 📊 Rapor**.
- **Mode offline**: kalau di jalan tanpa sinyal, data tersimpan di HP dan **terkirim otomatis** saat online. Ada tombol **🔄 Sinkron** dan badge antrean.
- **Rapor performa**: masukkan nopol → tahu kendaraan **HEMAT / CUKUP / BOROS**.
- Aplikasi bisa **dipasang di layar utama HP** seperti aplikasi biasa (PWA).

**Satu kalimat kunci:**
> *"Sopir di jalan tetap produktif — sinyal hilang bukan alasan data hilang."*

---

## 7️⃣ Demo Pendukung — Marketing & Chief Driver (2 menit) 📣

**Poin yang dibicarakan (cukup 1–2 layar):**
- **Marketing**: input jadwal kunjungan (appointment) untuk driver, pantau status, lihat hasil kunjungan — data penjualan tersaji otomatis.
- **Chief Driver**: papan pembagian tugas — kendaraan yang belum ditugaskan, beban tiap driver, dan **unduh rekap harian Excel**.

**Satu kalimat kunci:**
> *"Bukan hanya BBM — penjadwalan kunjungan dan pembagian sopir juga satu pintu."*

---

## 8️⃣ Keamanan & Tata Kelola (3 menit) 🔐

> Bagian ini yang paling sering ditanya pengambil keputusan. Siapkan jawaban singkat.

| Topik | Satu kalimat yang bisa dipakai |
|---|---|
| **Login PIN per orang** | "Setiap orang punya PIN — tidak ada akun bersama, semua aksi tercatat siapa." |
| **Role-based access** | "GA tidak bisa membuka rekap keuangan; OB tidak bisa melihat klaim. Hanya yang menjadi tugasnya." |
| **Audit Log** | "Semua aksi penting tercatat: siapa, apa, kapan — bisa difilter, jadi tidak ada yang 'hilang'." |
| **Anti peretasan** | "Login dibatasi percobaan (anti tebak PIN), token CSRF anti peretasan sesi, unggahan foto diperiksa keamanannya." |
| **Kerahasiaan data** | "Sesi browser aman, data dilindungi, foto bukti tidak bisa disalahgunakan." |

**Satu kalimat kunci:**
> *"Sistem ini dibangun dengan prinsip keamanan berlapis — dari PIN pengguna sampai jejak audit setiap transaksi."*

---

## 9️⃣ Kualitas & Kepatuhan (2 menit) 🧪

**Poin yang dibicarakan:**
- **97 uji otomatis backend + 82 uji frontend** — setiap perubahan diuji sebelum dipakai.
- **Uji end-to-end di produksi** untuk alur kritis (login per peran, verifikasi, isolasi data OB, export).
- Pemetaan standar: **ISO/IEC 27001** (keamanan informasi), **ISO 9241-11** (kegunaan/UX), **ISO 9001** (mutu) — tersedia di `SECURITY.md`.
- **Aksesibilitas**: fokus keyboard terlihat, kontras warna ≥ 4,5:1, mode kontras tinggi 🔆, mode gelap 🌙, dukungan pembaca layar.
- **Antarmuka responsif** — rapi di komputer maupun HP.

**Satu kalimat kunci:**
> *"Bukan prototipe — sistem yang diuji, diamankan, dan siap dipakai harian."*

---

## 🔟 Penutup — Nilai & Langkah Berikutnya (2 menit)

**Rangkum dalam 3 angka:**
> - **1 aplikasi** untuk semua peran.
> - **0 kertas** yang harus diarsip manual — semuanya digital & bisa dicetak kapan saja.
> - **100% tercatat & bisa diaudit** — setiap rupiah, setiap galon, setiap perjalanan.

**Langkah berikutnya yang ditawarkan:**
1. **Data master lengkap** — daftar armada, driver, merk air minum.
2. **Pelatihan singkat** per peran (panduan sudah ada: `USER_GUIDE.md`).
3. **Roadmap**: apa yang ingin dikembangkan berikutnya (laporan otomatis mingguan, approval berjenjang, dll).

---

## 🛠️ Persiapan Demo (sebelum presentasi)

| Persiapan | Detail |
|---|---|
| **Data contoh** | 1 pengajuan air minum + 1 klaim BBM + 1 kasbon (status beragam agar tiap layar hidup) |
| **2 tab/3 tab browser** | Dashboard GA, Dashboard Finance, dan login OB (untuk demo realtime) |
| **Foto contoh** | 2 foto air minum (sebelum/sesudah) + 1 struk BBM, sudah ada di perangkat |
| **Akun** | `admin`, `ga_officer`, `finance_officer`, `ob1` (PIN semua `123456`) |
| **Mode gelap/kontras** | Tunjukkan tombol 🌙 dan 🔆 di pojok kanan atas sebagai penutup bagian UI/UX |
| **Koneksi** | Pastikan internet stabil (demo realtime butuh koneksi) |

## ❓ Kemungkinan Pertanyaan Audiens

| Pertanyaan | Jawaban singkat |
|---|---|
| "Kalau internet mati?" | Driver tetap bisa kerja (offline-first, sinkron otomatis). |
| "Data aman?" | Login PIN, hak akses per peran, audit log, percobaan login dibatasi. |
| "Bisa diakses dari mana?" | Dari browser apa pun — komputer, laptop, HP. |
| "Bagaimana kalau ada sopir baru / OB baru?" | Admin membuat akun dalam hitungan menit dari halaman Users. |
| "Bisa integrasi Excel?" | Sudah: export CSV rekap air minum, export Excel logsheet & rekap harian. |
| "Apakah ini bisa dipakai untuk cabang lain?" | Ya — tinggal tambah pengguna & data master; alurnya sama. |

---

## ✨ Kata Penutup (siap dibacakan)

> "Kami tidak hanya membuat aplikasi — kami merapikan cara kerja sehari-hari. Sopir tidak perlu menunggu uangnya diganti berhari-hari. Finance tidak perlu menerka struk ini milik siapa. OB tidak perlu bingung bukti pembeliannya. Semuanya tercatat, terverifikasi, dan bisa dipertanggungjawabkan — dengan satu aplikasi yang dipakai semua orang, sesuai porsinya masing-masing. Terima kasih."
