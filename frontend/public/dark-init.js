// Inisialisasi tema gelap sebelum SPA termuat (anti-flash, tanpa inline script
// sehingga Content-Security-Policy bisa ketat: script-src 'self').
(function () {
  try {
    if (localStorage.getItem('bpf_dark') === '1') {
      document.documentElement.classList.add('dark')
    }
  } catch (e) { /* localStorage tidak tersedia — abaikan */ }
})()
