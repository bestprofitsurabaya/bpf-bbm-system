/* ============================================================ */
/* BPF FLEET SYSTEM - Admin UI Primitives                        */
/* (toast, dialogs, PIN session cache)                           */
/* Load BEFORE admin-dashboard.js and admin-cash.js              */
/* ============================================================ */

// ---- NAVBAR TOGGLE ----
(function() {
    var navToggle = document.getElementById('navToggle');
    var navLinks = document.querySelector('.nav-links');
    if (!navToggle || !navLinks) return;

    if (window.innerWidth <= 768) navLinks.style.display = 'none';

    navToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        navLinks.style.display = (navLinks.style.display === 'flex') ? 'none' : 'flex';
    });

    navLinks.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) navLinks.style.display = 'none';
        });
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-links') && !e.target.closest('.nav-toggle')) {
            if (window.innerWidth <= 768) navLinks.style.display = 'none';
        }
    });
})();

/* ============================================================ */
/* TOAST                                                        */
/* ============================================================ */

function toast(msg, type) {
    type = type || 'success';
    var c = document.getElementById('toastContainer');
    if (!c) {
        c = document.createElement('div');
        c.id = 'toastContainer';
        c.className = 'toast-container';
        document.body.appendChild(c);
    }
    var t = document.createElement('div');
    t.className = 'toast toast-' + type;
    var icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    t.innerHTML = '<span class="toast-icon">' + (icons[type] || '') + '</span>' +
        '<span class="toast-msg"></span><button class="toast-close" title="Tutup">&times;</button>';
    t.querySelector('.toast-msg').textContent = msg;
    c.appendChild(t);
    requestAnimationFrame(function() { t.classList.add('show'); });
    var kill = function() {
        t.classList.remove('show');
        setTimeout(function() { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
    };
    t.querySelector('.toast-close').addEventListener('click', kill);
    setTimeout(kill, 4200);
}

/* ============================================================ */
/* DIALOGS                                                      */
/* ============================================================ */

/**
 * Reusable modal dialog with fields. Resolves with {fieldId: value} or null if cancelled.
 * opts: { title, message, okText, danger, fields: [{id,label,type,placeholder,required,numeric,maxlength}], validate(out)->errMsg|null }
 */
function showDialog(opts) {
    return new Promise(function(resolve) {
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay active dialog-overlay';
        var box = document.createElement('div');
        box.className = 'modal-box dialog-box';
        var html = '<h3>' + (opts.title || '') + '</h3>';
        if (opts.message) html += '<p class="dlg-message">' + opts.message + '</p>';
        var fields = opts.fields || [];
        (fields || []).forEach(function(f) {
            var tag = f.type === 'textarea' ? 'textarea' : 'input';
            var extra = '';
            if (tag === 'input') {
                extra += ' type="' + (f.type || 'text') + '"';
                if (f.type === 'password') extra += ' maxlength="' + (f.maxlength || 6) + '" inputmode="numeric" autocomplete="off"';
                if (f.numeric) extra += ' inputmode="numeric"';
                extra += ' placeholder="' + (f.placeholder || '') + '"';
            } else {
                extra += ' rows="3" placeholder="' + (f.placeholder || '') + '"';
            }
            html += '<label class="dlg-label">' + (f.label || '') + (f.required ? ' <span class="req">*</span>' : '') + '</label>' +
                '<' + tag + ' id="dlg_' + f.id + '" class="form-control dlg-field" ' + extra + '></' + tag + '>';
        });
        html += '<p class="dlg-error" style="display:none;"></p>' +
            '<div class="flex gap-2 dlg-actions">' +
            '<button type="button" class="btn btn-secondary dlg-cancel">Batal</button>' +
            '<button type="button" class="btn ' + (opts.danger ? 'btn-danger' : 'btn-success') + ' dlg-ok">' + (opts.okText || 'OK') + '</button></div>';
        box.innerHTML = html;
        overlay.appendChild(box);
        document.body.appendChild(overlay);

        var errEl = box.querySelector('.dlg-error');
        function fail(msg) { errEl.textContent = msg; errEl.style.display = 'block'; }
        function ok() {
            if (!document.body.contains(overlay)) return; // guard double-fire (Enter on focused button)
            var out = {}, valid = true;
            fields.forEach(function(f) {
                var el = document.getElementById('dlg_' + f.id);
                var v = f.type === 'password' ? el.value : (el.value || '').trim();
                if (f.required && !v) { fail((f.label || 'Field ini') + ' wajib diisi'); valid = false; return; }
                if (f.numeric && f.type !== 'password' && v && isNaN(parseInt(v, 10))) { fail((f.label || 'Field ini') + ' harus angka'); valid = false; return; }
                out[f.id] = v;
            });
            if (!valid) return;
            if (opts.validate) { var ve = opts.validate(out); if (ve) { fail(ve); return; } }
            document.removeEventListener('keydown', handler);
            document.body.removeChild(overlay);
            resolve(out);
        }
        function cancel() { if (document.body.contains(overlay)) document.body.removeChild(overlay); document.removeEventListener('keydown', handler); resolve(null); }
        function handler(e) {
            if (e.key === 'Escape') { cancel(); return; }
            if (e.key === 'Enter' && e.target && e.target.tagName !== 'TEXTAREA' && !e.target.classList.contains('dlg-cancel')) { e.preventDefault(); ok(); }
        }
        box.querySelector('.dlg-ok').addEventListener('click', ok);
        box.querySelector('.dlg-cancel').addEventListener('click', cancel);
        overlay.addEventListener('click', function(e) { if (e.target === overlay) cancel(); });
        document.addEventListener('keydown', handler);
        var first = box.querySelector('.dlg-field');
        if (first) setTimeout(function() { first.focus(); }, 150);
    });
}

function confirmDialog(opts) {
    return new Promise(function(resolve) {
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay active dialog-overlay';
        var box = document.createElement('div');
        box.className = 'modal-box dialog-box';
        box.innerHTML = '<h3>' + (opts.title || 'Konfirmasi') + '</h3>' +
            '<p class="dlg-message">' + (opts.message || '') + '</p>' +
            '<div class="flex gap-2 dlg-actions">' +
            '<button type="button" class="btn btn-secondary dlg-cancel">Batal</button>' +
            '<button type="button" class="btn ' + (opts.danger ? 'btn-danger' : 'btn-success') + ' dlg-ok">' + (opts.okText || 'Ya') + '</button></div>';
        overlay.appendChild(box);
        document.body.appendChild(overlay);
        function done(v) {
            if (document.body.contains(overlay)) document.body.removeChild(overlay);
            document.removeEventListener('keydown', handler);
            resolve(v);
        }
        function handler(e) {
            if (e.key === 'Escape') done(false);
            else if (e.key === 'Enter') done(true);
        }
        box.querySelector('.dlg-ok').addEventListener('click', function() { done(true); });
        box.querySelector('.dlg-cancel').addEventListener('click', function() { done(false); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) done(false); });
        document.addEventListener('keydown', handler);
        setTimeout(function() { box.querySelector('.dlg-ok').focus(); }, 150);
    });
}

/* ============================================================ */
/* SESSION PIN CACHE (15 min)                                    */
/* ============================================================ */

var _idnCache = {};
var _IDN_TTL = 15 * 60 * 1000;

async function getVerifiedIdentity(username, roleLabel) {
    var cached = _idnCache[username];
    if (cached && (Date.now() - cached.ts) < _IDN_TTL) return cached;
    var res = await showDialog({
        title: '🔒 Verifikasi PIN ' + roleLabel,
        message: 'Masukkan PIN 6-digit untuk melanjutkan. Terverifikasi 15 menit dalam sesi ini.',
        okText: 'Verifikasi',
        fields: [{ id: 'pin', label: 'PIN', type: 'password', maxlength: 6, required: true }],
        validate: function(v) { if (!/^\d{6}$/.test(v.pin || '')) return 'PIN harus 6 digit angka!'; }
    });
    if (!res) return null;
    try {
        var r = await fetch('/api/verify-pin', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username, pin: res.pin }) });
        var d = await r.json();
        if (d.status !== 'success') { toast('PIN salah untuk ' + roleLabel, 'error'); return null; }
        _idnCache[username] = { name: d.user.full_name, username: username, ts: Date.now() };
        return _idnCache[username];
    } catch (e) { toast('Error koneksi', 'error'); return null; }
}

/* ============================================================ */
/* FORMATTING                                                   */
/* ============================================================ */

function formatIDR(n) { return Number(n || 0).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

/* ============================================================ */
/* SESSION: redirect ke login bila API mengembalikan 401        */
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
                var onLogin = window.location.pathname.indexOf('/login') !== -1;
                // Jangan ganggu: verify-pin (PIN salah = 401 bisnis) & halaman login
                if (!onLogin && u.indexOf('/api/verify-pin') === -1 && u.indexOf('/login') === -1) {
                    var nxt = encodeURIComponent(window.location.pathname + window.location.search);
                    window.location.href = '/login?next=' + nxt;
                }
            }
            return res;
        });
    };
})();
