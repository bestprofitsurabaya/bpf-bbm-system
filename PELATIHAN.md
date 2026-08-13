# 🎯 Lembar Latihan per Peran — BPF WorkHub

> Latihan singkat (±5–10 menit per peran) untuk gladi resik sebelum demo/meeting.
> Tiap latihan: **langkah** → **hasil yang harus terlihat**. Kalau hasilnya tidak sesuai, berarti ada yang perlu diperiksa.

---

## 👷 OB — Pengajuan Air Minum

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login `ob1` / PIN `123456` | Langsung masuk **Halaman Air Minum**, nama **Faisol** tampil |
| 2 | Klik **➕ Ajukan Pembelian** | Form muncul: tanggal, jumlah, jenis, merk, 2 kolom foto |
| 3 | Pilih jenis **Galon**, merk **AQUA Galon**, isi jumlah, unggah foto | Form terisi, tombol kirim aktif |
| 4 | Klik kirim | Pengajuan muncul di daftar dengan status **Menunggu Verifikasi** |
| 5 | (Coba) kirim tanpa foto | Muncul peringatan foto wajib — pengajuan tidak terkirim |

> 🔍 Cek: login sebagai `ob2` → harus TIDAK melihat pengajuan milik Faisol.

---

## 🚗 Driver — BBM, Kasbon, Trip

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Buka `/app/driver`, login PIN | Masuk aplikasi driver, 4 tab tampil |
| 2 | Tab **⛽ BBM** → isi klaim + foto struk | Klaim masuk antrean (cek via GA) |
| 3 | Tab **💰 Kasbon** → ajukan nominal | Total otomatis + **kode unik** |
| 4 | Tab **🗺️ Trip** → isi log perjalanan | Tersimpan, muncul di review GA |
| 5 | Tab **📊 Rapor** → masukkan nopol | Tampil HEMAT / CUKUP / BOROS |

> 🔍 Cek offline: matikan internet → isi data → hidupkan → tekan **🔄 Sinkron** → badge antrean hilang.

---

## 🧾 GA — Verifikasi Klaim & Kasbon

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login `ga_officer` / PIN `123456` | Langsung masuk **Dashboard GA** |
| 2 | Lihat antrean klaim | Klaim demo (BPF-DEMO-…) tampil |
| 3 | Klik **✅ Approve** satu klaim | Klaim pindah status (ke Finance) |
| 4 | Klik **✕ Tolak** tanpa alasan | Tombol terkunci — alasan wajib |
| 5 | Lihat kasbon menunggu approve | Kasbon DRAFT tampil dengan nominal |
| 6 | (Opsional) buka **🛡 Verifikasi Anomali** | Modal konfirmasi muncul |

> 🔍 Cek: GA mencoba buka `/app/dashboard` → **ditolak** (guard peran).

---

## 💰 Finance — Rekap & Verifikasi

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login `finance_officer` / PIN `123456` | Langsung masuk **Dashboard Finance** |
| 2 | Lihat **Rekap Air Minum** | Kartu statistik + ringkasan per OB + per jenis/merk terisi |
| 3 | Buka **antrean verifikasi** | Pengajuan pending (WTR-DEMO-01) tampil |
| 4 | Klik **✅ Verifikasi** → isi remark | Status jadi **Terverifikasi** |
| 5 | Klik **📄 PDF** pada yang terverifikasi | PDF tanda terima terbuka (nama Finance & GA tercetak) |
| 6 | Klik **⬇ Export CSV** | File Excel terunduh dengan data rekap |
| 7 | Lihat kasbon menunggu Finance | Kasbon GA_APPROVED tampil |

---

## 📣 Marketing — Appointment

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login akun Marketing (`Yusie`) | Masuk **Marketing Hub** |
| 2 | Buat appointment baru (tanggal, sesi, **jam kunjungan**, alamat) | Tersimpan, muncul di papan; jam tampil di board Chief Driver |
| 3 | Lihat jadwal hari ini | Appointment demo (APPT-DEMO-01/02) tampil |
| 4 | (Opsional) edit/batal | Status berubah, notifikasi keluar |

---

## 🚛 Chief Driver — Pembagian Tugas

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login akun Chief Driver | Masuk **board Chief Driver** |
| 2 | Lihat "Belum Ditugaskan" | Appointment tanpa driver tampil di board |
| 3 | Klik **⚡ Atur Rute Otomatis** | Modal saran rute per driver: urutan jam + area searah + estimasi km/BBM + **angka hemat %** |
| 4 | Klik **✅ Terapkan Rute** | Driver otomatis ditugaskan + notifikasi 🗺️; panel "Tugas Per Driver" terisi |
| 5 | Tugaskan manual (opsional) | Muncul di panel "Tugas Per Driver" |
| 6 | Unduh rekap harian | File Excel terunduh |

---

## 🪪 Receptionist — Pelamar Kerja

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login akun Receptionist | Masuk **dashboard Pelamar Kerja** |
| 2 | Buka `/app/apply` (tab baru, tanpa login) → isi form pelamar | Sukses + No. Registrasi `PLM-*` + jam interview otomatis |
| 3 | Cari nama pelamar tadi di dashboard (kotak pencarian / filter tanggal) | Baris pelamar tampil |
| 4 | Klik **✅ Verifikasi** lalu **🎯 Catat Kehadiran** → tandai Interview + Training H1 | Status naik otomatis; chip I & H1 menyala |
| 5 | Klik **🚪 Mengundurkan Diri** tanpa alasan | Ditolak — **alasan wajib** |
| 6 | Isi alasan → simpan | Status **Mengundurkan Diri** |
| 7 | Pilih tahap laporan → **📄 Laporan PDF** | PDF resmi berlogo BPF + TTD Receptionist terunduh |
| 8 | (Opsional) ✏️ Edit data yang salah | Data berubah, tercatat audit |

---

## 🎯 Traineer — Pantau Rekrutan

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login akun Traineer | Masuk **Rekrutan Saya** — langsung berisi pelamar yang mencantumkan UPLINE = kamu |
| 2 | Gunakan filter tanggal / user / status + pencarian | Daftar terfilter sesuai |
| 3 | Perhatikan chip kehadiran (I · H1–H4) | Chip menyala sesuai tahap yang sudah dihadiri |
| 4 | (Coba) klik tombol edit/hapus | Tidak ada — Traineer hanya melihat (read-only) |

---

## ⚙️ Admin — User & Pengaturan

| # | Langkah | Hasil yang diharapkan |
|---|---------|------------------------|
| 1 | Login `admin` / PIN `123456` | Masuk **Dashboard Admin** |
| 2 | Buka **Users** → cari user | Daftar user tampil; bisa nonaktifkan/aktifkan |
| 3 | Buka **Settings** | Nama Finance & GA untuk tanda terima bisa diubah |
| 4 | Buka **Audit Log** | Aksi-aksi tadi tercatat: siapa + kapan |
| 5 | Coba tombol 🌙 dan 🔆 di pojok kanan atas | Mode gelap & kontras tinggi berganti |

---

## 🧪 Daftar Periksa Sebelum Demo

- [ ] Data demo masih ada (cek: antrean GA ada klaim, rekap finance ada air minum)
- [ ] 2–3 tab browser siap (GA, Finance, OB) untuk demo realtime
- [ ] Foto contoh siap di perangkat (air minum sebelum/sesudah, struk BBM)
- [ ] Akun & PIN terverifikasi (`admin`, `ga_officer`, `finance_officer`, `ob1`, `ob2`, `ob3`, receptionist, traineer)
- [ ] PDF slide deck & PPTX siap dibagikan (`presentasi/`)
- [ ] Bersihkan data demo setelah selesai: `docker exec -i bbm_mariadb mariadb -uroot -ppassword_db bpf_asset_system < scripts/demo_cleanup.sql`

> 💡 Panduan lengkap & narasi demo ada di **`PRESENTASI.md`** — slide interaktif **`presentasi/index.html`**.
