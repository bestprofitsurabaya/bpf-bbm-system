# 🔐 Keamanan & Kepatuhan Standar — BPF WorkHub v1.0

Dokumen ini memetakan kontrol keamanan & kualitas aplikasi terhadap standar internasional yang relevan.

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

## 📋 Daftar Isi

1. [ISO/IEC 27001:2022 — Manajemen Keamanan Informasi](#1-isoiec-270012022--manajemen-keamanan-informasi)
2. [ISO 9241-11 — Usability](#2-iso-9241-11--usability)
3. [ISO 9001 — Manajemen Mutu](#3-iso-9001--manajemen-mutu)

---

## 1. ISO/IEC 27001:2022 — Manajemen Keamanan Informasi

Sistem menerapkan kontrol akses berbasis peran (RBAC) dengan prinsip **least privilege** dan **segregation of duties**.

### 1.1 Pemetaan Kontrol

| Kontrol ISO 27001 | Implementasi |
|-------------------|--------------|
| **A.5.15 — Access control** | Autentikasi session-based (username + PIN 6 digit); setiap peran hanya bisa membuka menu/halaman yang menjadi wewenangnya; UI menyembunyikan menu tak berhak & router SPA menolak akses (403). |
| **A.8.2 — Privileged access rights** | Hak istimewa (Admin) dibatasi: halaman Users, Settings, dan Audit Log khusus admin (`@role_required(['admin'])` di server + guard `meta.roles` di SPA). |
| **A.8.5 — Secure authentication** | PIN disimpan di DB; login menolak user nonaktif; sesi cookie (`session.permanent`) dengan masa berlaku; anti open-redirect pada parameter `next`. |
| **A.8.15 — Logging** | Seluruh aksi state-changing tercatat di `activity_logs` (siapa, apa, kapan, IP) dan tampil di halaman Audit Log (admin). |
| **A.8.16 — Monitoring activities** | Indikator koneksi real-time (⚡/🔴) di topbar SPA; log aplikasi `docker logs bbm_web`. |
| **A.8.28 — Secure coding** | SQL berparameter (anti-injection), proteksi CSRF di semua POST (token + header `X-CSRF-Token`), header `no-store` anti-cache, validasi input. |
| **A.8.9 / A.8.25 — Configuration & secure development** | Konfigurasi via environment (`SECRET_KEY`, kredensial DB); pipeline rilis terdokumentasi; test otomatis (`pytest`) sebelum rilis. |

### 1.2 Matriks Hak Akses per Peran

| Fitur / Halaman | Admin | GA | Finance | Marketing | Chief Driver |
|-----------------|:-----:|:--:|:-------:|:---------:|:------------:|
| Dashboard admin/statistik | ✅ | ✅ | ✅ | – | – |
| Log Perjalanan (trips) | ✅ | ✅ | ✅ | – | – |
| Assignments kendaraan | ✅ | ✅ | – | – | – |
| Rekap & Analytics | ✅ | ✅ | ✅ | – | – |
| Marketing Hub | – | – | – | ✅ | – |
| Chief Driver board | ✅ | ✅ | – | – | ✅ |
| Manajemen User | ✅ | – | – | – | – |
| Pengaturan (settings) | ✅ | – | – | – | – |
| Audit Log | ✅ | – | – | – | – |

Enforcement berlapis: (1) server `role_required` pada setiap route/API, (2) guard router SPA, (3) penyembunyian menu di sidebar. Membuka URL langsung oleh user tak berhak → **403**.

---

## 2. ISO 9241-11 — Usability

| Prinsip | Implementasi |
|---------|--------------|
| **Efektivitas** | Dashboard per role menampilkan hanya informasi yang relevan; aksi cepat satu klik; status & konteks selalu terlihat. |
| **Efisiensi** | SPA tanpa reload antar-halaman; lazy-loading per view; menu terfilter mengurangi langkah navigasi; shortcut & filter instan. |
| **Kepuasan** | Desain responsif (mobile-friendly), dark mode, indikator realtime, umpan balik visual (toast/alert), bahasa Indonesia. |

---

## 3. ISO 9001 — Manajemen Mutu

| Klausul | Implementasi |
|---------|--------------|
| **4–5 (Konteks & Kepemimpinan)** | Ruang lingkup & peran terdokumentasi di README/USER_GUIDE/DEPLOYMENT. |
| **7.5 (Informasi terdokumentasi)** | CHANGELOG (Keep a Changelog), DEPLOYMENT.md, USER_GUIDE.md, SECURITY.md. |
| **8.1 (Perencanaan operasional)** | Alur rilis: CHANGELOG → tag → GitHub Release (`scripts/release.sh`). |
| **8.6 (Rilis produk)** | Verifikasi sebelum rilis: `pytest` (243 test), `npm run build`, smoke test HTTP/WebSocket. |
| **10 (Peningkatan)** | Audit log & umpan balik; perbaikan berkelanjutan di tiap versi (lihat CHANGELOG). |

---

## 🔒 Ringkasan Fitur Keamanan

| Fitur | Deskripsi |
|-------|-----------|
| Login PIN | Username + 6 digit PIN per orang |
| Session | HTTP-only cookie, SameSite=Lax, Secure (HTTPS) |
| CSRF | Token di semua POST/PUT/DELETE/PATCH |
| Role-Based Access | 11 role, least privilege, enforcement berlapis |
| Audit Trail | 30+ action types, siapa + kapan + apa |
| Rate Limit | Anti brute-force login (Redis) |
| Watermark | GPS + timestamp di foto bukti |
| Security Headers | CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| Backup | DB otomatis tiap 03:00 WIB, retensi 30 hari |

---

## 📞 Kontak Tim IT

**PT. Bestprofit Futures — Surabaya**  
Graha Bukopin Lantai 11, Jl. Panglima Sudirman No. 10-18, Surabaya 60271  
Telp: 031-5349888

---

*BPF WorkHub v1.0 · Keamanan & Kepatuhan*
