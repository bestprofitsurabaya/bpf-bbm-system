/* ============================================================ */
/* BPF FLEET SYSTEM - Admin Tab SPA & UX Enhancements            */
/* (switchAdminTab via server fragment, context bar, dark mode,  */
/*  keyboard shortcuts, bulk approve GA, count-up, koneksi)      */
/* Load AFTER admin-ui.js, admin-dashboard.js, admin-cash.js     */
/* ============================================================ */

/* ============================================================ */
/* TAB SWITCH TANPA RELOAD (fragment server, render Jinja sama)  */
/* ============================================================ */

var _switchingTab = false;

async function switchAdminTab(tab) {
    if (_switchingTab) return;
    _switchingTab = true;
    try {
        setActiveTab(tab);
        showTabSkeleton();
        var html = await fetchFragmentHtml(tab);
        var content = document.getElementById('tabContent');
        if (!content) { window.location = '?tab=' + tab; return; }
        content.innerHTML = html;
        afterTabLoaded(tab);
        // Update URL tanpa reload
        var u = new URL(window.location.href);
        u.searchParams.set('tab', tab);
        if (tab !== 'archive') {
            ['search', 'start_date', 'end_date', 'bbm_type', 'page'].forEach(function(k) { u.searchParams.delete(k); });
        }
        history.pushState({ tab: tab }, '', u.toString());
    } catch (e) {
        // Fallback aman: full reload
        window.location = '?tab=' + tab;
    } finally {
        _switchingTab = false;
    }
}

function setActiveTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(function(b) {
        b.classList.toggle('active', b.getAttribute('data-tab') === tab);
    });
}

function showTabSkeleton() {
    var content = document.getElementById('tabContent');
    if (!content) return;
    content.innerHTML = '<div class="tab-skeleton">' +
        '<div class="sk sk-card"></div><div class="sk sk-card"></div>' +
        '<div class="sk sk-card"></div><div class="sk sk-card"></div>' +
        '</div>';
}

async function fetchFragmentHtml(tab) {
    var r = await fetch('/admin/queue-fragment/' + encodeURIComponent(tab), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return await r.text();
}

function afterTabLoaded(tab) {
    if (tab === 'cash') {
        // Render data kasbon (fungsi sudah guard element null)
        loadDailyCode();
        loadCashRequests();
    }
    if (tab === 'archive') {
        // Reset pagination saat pertama masuk tab Arsip
        _archivePage = 1;
    }
    // Sinkronkan angka stat & ringkasan setelah konten berubah
    refreshStats();
}

/* Back/Forward browser */
window.addEventListener('popstate', function() {
    if (_switchingTab) return;
    _switchingTab = true;
    var t = new URLSearchParams(window.location.search).get('tab') || 'ga_queue';
    setActiveTab(t);
    showTabSkeleton();
    fetchFragmentHtml(t).then(function(html) {
        var content = document.getElementById('tabContent');
        if (content) { content.innerHTML = html; afterTabLoaded(t); }
    }).catch(function() { window.location.reload(); })
    .finally(function() { _switchingTab = false; });
});

/* Kartu stat (a[data-tab]) juga SPA-switch, tetap punya href utk fallback */
document.addEventListener('click', function(e) {
    if (!e.target || !e.target.closest) return;
    var card = e.target.closest('a[data-tab]');
    if (card) { e.preventDefault(); switchAdminTab(card.getAttribute('data-tab')); }
});

/* ============================================================ */
/* CONTEXT BAR: ringkasan hari ini + koneksi                    */
/* ============================================================ */

async function refreshTodaySummary() {
    try {
        var r = await fetch('/api/stats');
        var d = await r.json();
        if (d.error) return;
        var tx = document.getElementById('todayTx');
        if (tx && d.today_tx !== undefined) tx.textContent = d.today_tx;
        var nom = document.getElementById('todayNominal');
        if (nom && d.today_nominal !== undefined) nom.textContent = 'Rp ' + formatIDR(d.today_nominal);
        var dt = document.getElementById('todayDate');
        if (dt) dt.textContent = '📅 ' + new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    } catch (e) {}
}

function updateConnIndicator() {
    var dot = document.getElementById('connDot');
    if (!dot) return;
    var online = navigator.onLine;
    dot.className = 'conn-dot ' + (online ? 'online' : 'offline');
    dot.title = online ? 'Online — data real-time aktif' : 'Offline — data mungkin tidak diperbarui';
}
window.addEventListener('online', updateConnIndicator);
window.addEventListener('offline', updateConnIndicator);

/* ============================================================ */
/* DARK MODE (persist localStorage, diterapkan sedini mungkin)   */
/* ============================================================ */

function initAdminDark() {
    var btn = document.getElementById('navDarkToggle');
    if (!btn) return;
    btn.textContent = document.documentElement.classList.contains('dark') ? '☀️' : '🌙';
}

function toggleAdminDark() {
    var on = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', on);
    localStorage.setItem('adminDark', on ? '1' : '0');
    var btn = document.getElementById('navDarkToggle');
    if (btn) btn.textContent = on ? '☀️' : '🌙';
}

/* ============================================================ */
/* SHORTCUT KEYBOARD: 1-5 pindah tab                             */
/* ============================================================ */

document.addEventListener('keydown', function(e) {
    if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var map = { '1': 'ga_queue', '2': 'finance', '3': 'driver_confirm', '4': 'archive', '5': 'cash' };
    var tab = map[e.key];
    if (tab) { e.preventDefault(); switchAdminTab(tab); }
});

/* ============================================================ */
/* BULK ACTION GA: Tandai Semua Dicek (loop /ga/approve)         */
/* ============================================================ */

async function approveAllGA() {
    var items = document.querySelectorAll('#tabContent .tx-item[data-id]');
    var ids = [];
    var total = 0;
    items.forEach(function(it) {
        ids.push(it.getAttribute('data-id'));
        total += parseFloat(it.getAttribute('data-nominal')) || 0;
    });
    if (ids.length < 2) { toast('Antrean GA kurang dari 2 transaksi', 'info'); return; }
    var idn = await getVerifiedIdentity('ga_officer', 'GA');
    if (!idn) return;
    var ok = await confirmDialog({
        title: '✅ Tandai Semua Dicek',
        message: 'Approve ' + ids.length + ' transaksi GA sekaligus (total Rp ' + formatIDR(total) + ') sebagai ' + idn.name + '?<br>Verifikasi menyeluruh tetap bisa dilakukan di tab Arsip.',
        okText: 'Ya, approve semua', danger: true
    });
    if (!ok) return;
    var okCount = 0, failCount = 0;
    for (var i = 0; i < ids.length; i++) {
        try {
            var r = await fetch('/ga/approve/' + ids[i] + '?admin=' + encodeURIComponent(idn.name), { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            var d = null; try { d = await r.json(); } catch (e) {}
            if (r.ok && d && d.status === 'success') okCount++; else failCount++;
        } catch (e) { failCount++; }
    }
    toast('✅ ' + okCount + ' transaksi disetujui' + (failCount ? ' · ' + failCount + ' gagal' : ''), failCount ? 'warning' : 'success');
    if (okCount > 0) {
        var t = new URLSearchParams(window.location.search).get('tab') || 'ga_queue';
        switchAdminTab(t);
    }
}

/* ============================================================ */
/* ARSIP: PAGINATION MUAT LEBIH BANYAK (tanpa reload)            */
/* ============================================================ */

var _archivePage = 1;

async function loadMoreArchive() {
    var btn = document.getElementById('archiveLoadMore');
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    var status = document.getElementById('archiveMoreStatus');
    if (status) status.textContent = '⏳ Memuat...';

    // Baca filter aktif dari input
    var s = (document.getElementById('archiveSearch') || {}).value || '';
    var sd = (document.getElementById('archiveStartDate') || {}).value || '';
    var ed = (document.getElementById('archiveEndDate') || {}).value || '';
    var bb = (document.getElementById('archiveBbm') || {}).value || '';

    _archivePage += 1;
    var params = new URLSearchParams();
    params.set('page', _archivePage);
    if (s) params.set('search', s);
    if (sd) params.set('start_date', sd);
    if (ed) params.set('end_date', ed);
    if (bb) params.set('bbm_type', bb);

    try {
        var r = await fetch('/admin/queue-fragment/archive?' + params.toString(), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        var html = await r.text();
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var items = doc.querySelectorAll('.tx-item');
        var list = document.querySelector('#tabContent .card .card-body');
        if (list) items.forEach(function(it) { list.appendChild(it); });

        // Update URL agar state konsisten (replaceState, tanpa reload)
        var u = new URL(window.location.href);
        u.searchParams.set('page', _archivePage);
        history.replaceState({}, '', u.toString());

        if (status) status.textContent = 'Menampilkan ±' + (_archivePage * 50) + ' data terakhir';
        if (items.length < 50) {
            if (btn) btn.style.display = 'none';
            if (status) status.textContent = '· Semua data telah dimuat';
        } else {
            btn.disabled = false;
        }
    } catch (e) {
        _archivePage -= 1;
        if (status) status.textContent = 'Gagal memuat data.';
        btn.disabled = false;
    }
}

/* ============================================================ */
/* COUNT-UP ANIMASI angka stat (initial load)                    */
/* ============================================================ */

function animateCount(el, from, to, dur) {
    var start = null;
    function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        el.textContent = Math.round(from + (to - from) * p);
        if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

/* ============================================================ */
/* INIT                                                          */
/* ============================================================ */

(function initAdminTabs() {
    initAdminDark();
    updateConnIndicator();
    refreshTodaySummary();
    // Animasi count-up angka stat yang sudah dirender server
    document.querySelectorAll('.stat-card .number[data-stat]').forEach(function(el) {
        var target = parseInt(el.textContent, 10) || 0;
        animateCount(el, 0, target, 600);
    });
})();
