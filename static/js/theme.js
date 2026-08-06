/* ============================================================ */
/* BPF FLEET SYSTEM - Shared Theme (dark mode) + Auth redirect  */
/* Dipakai oleh semua halaman admin (analytics/rekap/settings/  */
/* logs/trips/ga_assignments). Panggil applyStoredTheme() di    */
/* <head> sedini mungkin untuk hindari flash.                   */
/* ============================================================ */

/* Catatan: penerapan tema awal dilakukan inline di <head> tiap template
   (if localStorage.getItem('adminDark') === '1' ...) untuk hindari flash.
   Toggle dark mode + persist */
function togglePageDark() {
    var on = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', on);
    localStorage.setItem('adminDark', on ? '1' : '0');
    var btn = document.getElementById('navDarkToggle');
    if (btn) btn.textContent = on ? '☀️' : '🌙';
    // Beri tahu halaman agar mengupdate elemen (mis. chart)
    document.dispatchEvent(new CustomEvent('themechange', { detail: { dark: on } }));
}

/* Sinkronkan ikon tombol saat DOM siap */
function syncDarkToggleIcon() {
    var btn = document.getElementById('navDarkToggle');
    if (btn) {
        btn.textContent = document.documentElement.classList.contains('dark') ? '☀️' : '🌙';
    }
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncDarkToggleIcon);
} else {
    syncDarkToggleIcon();
}

/* ============================================================ */
/* FETCH 401 -> redirect ke login (session kedaluwarsa)          */
/* ============================================================ */
(function() {
    if (!window.fetch) return;
    var _orig = window.fetch;
    window.fetch = function(url, opts) {
        opts = opts || {};
        var u = String(url);
        var method = (opts.method || 'GET').toUpperCase();
        var sameOrigin = u.indexOf('http') !== 0 || u.indexOf(window.location.origin) === 0;
        // Injeksi CSRF token untuk semua state-change same-origin
        if (sameOrigin && ['POST', 'PUT', 'DELETE', 'PATCH'].indexOf(method) !== -1) {
            var meta = document.querySelector('meta[name="csrf-token"]');
            if (meta && meta.content) {
                opts.headers = opts.headers || {};
                opts.headers['X-CSRF-Token'] = meta.content;
            }
        }
        return _orig(u, opts).then(function(res) {
            if (res.status === 401) {
                var u2 = u;
                var onLogin = window.location.pathname.indexOf('/login') !== -1;
                // Jangan ganggu: verifikasi PIN (PIN salah = 401 bisnis), dan halaman login
                if (!onLogin && u2.indexOf('/api/verify-pin') === -1 && u2.indexOf('/login') === -1) {
                    var nxt = encodeURIComponent(window.location.pathname + window.location.search);
                    window.location.href = '/login?next=' + nxt;
                }
            }
            return res;
        });
    };
})();
