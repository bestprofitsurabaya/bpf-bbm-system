/* ============================================================ */
/* BPF FLEET SYSTEM - Admin Dashboard Workflow                   */
/* (approve/payout/archive/reject, cross-check, ODO, review,     */
/*  health widget, socket, archive, queue search)                */
/* Load AFTER admin-ui.js                                        */
/* ============================================================ */

/* ============================================================ */
/* PIN SYSTEM (legacy modal, kept for compatibility)             */
/* ============================================================ */

var pendingAction = null, pendingTxId = null;

function requirePin(action, txId, role) {
    if (action === 'archive') { completeAction('archive', txId); return; }
    if (action === 'reject') { openRejectFlow(txId); return; }
    // Fallback to legacy PIN modal for any other action
    pendingAction = action; pendingTxId = txId;
    document.getElementById('pinTitle').textContent = 'Verifikasi ' + role;
    document.getElementById('pinMsg').textContent = 'Masukkan PIN 6-digit ' + role;
    document.getElementById('pinInput').value = '';
    document.getElementById('pinError').style.display = 'none';
    document.getElementById('pinBtn').disabled = false;
    document.getElementById('pinBtn').textContent = 'Verifikasi';
    document.getElementById('pinModal').classList.add('active');
    setTimeout(function(){ document.getElementById('pinInput').focus(); }, 200);
}

function closePin() { document.getElementById('pinModal').classList.remove('active'); }

async function submitPin() {
    var pin = document.getElementById('pinInput').value;
    if (pin.length !== 6 || !/^\d{6}$/.test(pin)) {
        document.getElementById('pinError').textContent = 'PIN harus 6 digit angka!';
        document.getElementById('pinError').style.display = 'block'; return;
    }
    var btn = document.getElementById('pinBtn'); btn.textContent = '...'; btn.disabled = true;
    document.getElementById('pinError').style.display = 'none';
    try {
        var username = (pendingAction === 'payout' || pendingAction === 'archive') ? 'finance_officer' : 'ga_officer';
        var res = await fetch('/api/verify-pin', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:username, pin:pin}) });
        var data = await res.json();
        if (data.status === 'success') {
            closePin();
            // Legacy path: delegate to the no-reload workflow
            completeAction(pendingAction, pendingTxId);
        } else {
            document.getElementById('pinError').textContent = 'PIN salah!';
            document.getElementById('pinError').style.display = 'block';
            document.getElementById('pinInput').value = '';
            document.getElementById('pinInput').focus();
        }
    } catch(e) { document.getElementById('pinError').textContent = 'Error koneksi'; document.getElementById('pinError').style.display = 'block'; }
    finally { btn.textContent = 'Verifikasi'; btn.disabled = false; }
}

/* ============================================================ */
/* NO-RELOAD WORKFLOW: approve / payout / archive / reject       */
/* ============================================================ */

var _inFlight = {};
async function completeAction(action, txId) {
    var key = action + ':' + txId;
    if (_inFlight[key]) return; // prevent double-submit
    _inFlight[key] = true;
    var ccBtn = document.querySelector('#ccBody .cc-actions .btn-success');
    var ccLabel = ccBtn ? ccBtn.textContent : null;
    if (ccBtn) { ccBtn.disabled = true; ccBtn.textContent = '⏳ Memproses...'; }
    try {
        var labels = { approve: 'Klaim', payout: 'Dana', archive: 'Transaksi' };
        if (action === 'payout') {
            var okP = await confirmDialog({ title: '💸 Payout Dana', message: 'Konfirmasi dana sudah dikeluarkan untuk transaksi #' + txId + '?', okText: 'Ya, sudah cair' });
            if (!okP) return;
        }
        if (action === 'archive') {
            var okA = await confirmDialog({ title: '📦 Arsipkan Transaksi', message: 'Driver sudah TTD? Transaksi #' + txId + ' akan diarsipkan permanen.', okText: 'Ya, arsipkan' });
            if (!okA) return;
        }
        var username = (action === 'payout' || action === 'archive') ? 'finance_officer' : 'ga_officer';
        var roleLabel = (action === 'payout' || action === 'archive') ? 'Finance' : 'GA';
        var idn = await getVerifiedIdentity(username, roleLabel);
        if (!idn) return;
        var url = action === 'approve' ? '/ga/approve/' + txId + '?admin=' + encodeURIComponent(idn.name)
                : action === 'payout' ? '/finance/payout/' + txId + '?admin=' + encodeURIComponent(idn.name)
                : action === 'archive' ? '/finance/archive/' + txId + '?admin=' + encodeURIComponent(idn.name)
                : null;
        // POST (state-change) + CSRF token diinjeksi otomatis oleh fetch wrapper
        var r = await fetch(url, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        var d = null;
        try { d = await r.json(); } catch (e) {}
        if (!r.ok || (d && d.status === 'error')) {
            toast((d && d.msg) || ('Gagal memproses: HTTP ' + r.status), 'error');
            return;
        }
        var msgs = { approve: '✅ Klaim disetujui', payout: '💸 Dana dikeluarkan', archive: '📦 Transaksi diarsipkan' };
        toast((d && d.msg) || ((msgs[action] || 'Selesai') + ' — ' + labels[action] + ' #' + txId), 'success');
        // Money/final actions: require a fresh PIN next time
        if (action === 'payout' || action === 'archive') delete _idnCache['finance_officer'];
        closeCC();
        removeItemAndAdvance(txId);
        refreshStats();
    } catch (e) { toast('Error koneksi: ' + e.message, 'error'); }
    finally {
        _inFlight[key] = false;
        if (ccBtn) { ccBtn.disabled = false; if (ccLabel !== null) ccBtn.textContent = ccLabel; }
    }
}

async function openRejectFlow(txId) {
    var idn = await getVerifiedIdentity('ga_officer', 'GA');
    if (!idn) return;
    var res = await showDialog({
        title: '⛔ Tolak Transaksi #' + txId,
        message: 'Jelaskan alasan penolakan — akan terlihat oleh driver.',
        okText: 'Tolak',
        danger: true,
        fields: [{ id: 'reason', label: 'Alasan penolakan', type: 'textarea', required: true, placeholder: 'Alasan penolakan...' }]
    });
    if (!res) return;
    try {
        var fd = new FormData();
        fd.append('rejection_reason', res.reason);
        fd.append('rejected_by', idn.name);
        var r = await fetch('/admin/reject/' + txId, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' }, body: fd });
        var d = null;
        try { d = await r.json(); } catch (e) {}
        if (!r.ok || (d && d.status === 'error')) {
            toast((d && d.msg) || ('Gagal menolak: HTTP ' + r.status), 'error');
            return;
        }
        toast((d && d.msg) || ('⛔ Transaksi #' + txId + ' ditolak'), 'warning');
        removeItemAndAdvance(txId);
        refreshStats();
    } catch (e) { toast('Error koneksi: ' + e.message, 'error'); }
}

/* Remove the processed item from the DOM (no reload) and focus the next one */
function removeItemAndAdvance(txId) {
    var item = document.querySelector('.tx-item[data-id="' + txId + '"]');
    if (!item) return;
    item.classList.add('tx-removing');
    setTimeout(function() {
        item.remove();
        updateQueueMeta();
        var next = document.querySelector('.card .card-body .tx-item:not(.tx-hidden)');
        if (next) {
            next.scrollIntoView({ behavior: 'smooth', block: 'center' });
            next.classList.add('tx-flash');
            setTimeout(function() { next.classList.remove('tx-flash'); }, 1200);
        }
    }, 350);
}

function updateQueueMeta() {
    var body = document.querySelector('.card .card-body');
    if (!body) return;
    var all = body.querySelectorAll('.tx-item');
    var items = body.querySelectorAll('.tx-item:not(.tx-hidden)');
    if (all.length === 0) { body.innerHTML = '<div class="empty">Tidak ada transaksi.</div>'; return; }
    var cnt = document.getElementById('queueCount');
    if (cnt) cnt.textContent = items.length + ' transaksi';
    var total = 0;
    items.forEach(function(i) { total += parseFloat(i.getAttribute('data-nominal')) || 0; });
    var tot = document.getElementById('financePayoutTotal');
    if (tot) tot.textContent = 'Rp ' + formatIDR(total);
}

/* ============================================================ */
/* QUEUE LIVE SEARCH (no reload)                                */
/* ============================================================ */

function filterQueue() {
    var inp = document.getElementById('queueSearch');
    if (!inp) return;
    var q = (inp.value || '').trim().toLowerCase();
    var body = document.querySelector('.card .card-body');
    if (!body) return;
    var items = body.querySelectorAll('.tx-item');
    var shown = 0;
    items.forEach(function(it) {
        var match = !q || (it.textContent || '').toLowerCase().indexOf(q) !== -1;
        it.classList.toggle('tx-hidden', !match);
        if (match) shown++;
    });
    var countEl = document.getElementById('queueSearchCount');
    if (countEl) countEl.textContent = q ? (shown + '/' + items.length + ' transaksi') : '';
    var empty = body.querySelector('.queue-empty');
    if (!empty) {
        empty = document.createElement('div');
        empty.className = 'queue-empty empty';
        body.appendChild(empty);
    }
    var noMatch = q && shown === 0;
    empty.style.display = noMatch ? 'block' : 'none';
    if (noMatch) empty.textContent = 'Tidak ada transaksi yang cocok dengan "' + q + '".';
    updateQueueMeta();
}

function clearQueueSearch() {
    var inp = document.getElementById('queueSearch');
    if (inp) inp.value = '';
    filterQueue();
    if (inp) inp.focus();
}

async function refreshStats() {
    try {
        var r = await fetch('/api/stats');
        var d = await r.json();
        var map = { pending: d.pending, verified_ga: d.verified_ga, os_finance: d.os_finance, archived: d.archived };
        Object.keys(map).forEach(function(k) {
            document.querySelectorAll('[data-stat="' + k + '"]').forEach(function(el) {
                if (el.textContent !== String(map[k])) el.textContent = map[k];
            });
        });
    } catch (e) {}
}

/* ============================================================ */
/* SOCKETIO REAL-TIME                                           */
/* ============================================================ */

function setupSocket() {
    if (typeof io === 'undefined') return;
    var socket = io();
    socket.on('new_claim', function(d) { onLiveData('⛽ Klaim baru', d); });
    socket.on('new_trip_report', function(d) { onLiveData('🗺️ Trip baru', d); });
}

function onLiveData(label, d) {
    var who = (d.driver_name || '') + (d.nopol ? ' (' + d.nopol + ')' : '');
    toast(label + (who ? ' — ' + who : ''), 'info');
    refreshStats();
    var pill = document.getElementById('newDataPill');
    if (!pill) {
        pill = document.createElement('div');
        pill.id = 'newDataPill';
        pill.className = 'new-data-pill';
        pill.innerHTML = '🔄 Ada data baru <button type="button" class="btn btn-primary btn-sm" onclick="location.reload()">Muat Ulang</button>';
        document.body.appendChild(pill);
    }
    pill.classList.add('show');
    clearTimeout(pill._t);
    pill._t = setTimeout(function() { pill.classList.remove('show'); }, 10000);
}

/* ============================================================ */
/* REJECT (legacy modal kept for compatibility)                  */
/* ============================================================ */

function showRejectModal(txId) { document.getElementById('rejectForm').action = '/admin/reject/' + txId; document.getElementById('rejectModal').classList.add('active'); }
function closeReject() { document.getElementById('rejectModal').classList.remove('active'); }

/* ============================================================ */
/* CROSS-CHECK                                                  */
/* ============================================================ */

async function openCrossCheck(txId, action, role) {
    document.getElementById('ccModal').classList.add('active');
    document.getElementById('ccBody').innerHTML = '<p style="text-align:center;color:var(--gray-500);padding:20px;">⏳ Menganalisis data...</p>';
    try {
        var r = await fetch('/api/cross-check/' + txId); var d = await r.json();
        if (d.error) { document.getElementById('ccBody').innerHTML = '<p style="color:red;">Error: ' + d.error + '</p>'; return; }
        var flagsHtml = '';
        if (d.flags && d.flags.length > 0) { d.flags.forEach(function(f) { flagsHtml += '<div class="cc-flag ' + f.level + '">' + f.msg + '</div>'; }); }
        else { flagsHtml = '<div class="cc-flag" style="background:#d1fae5;color:#065f46;border-left:4px solid #059669;">✅ Semua parameter normal</div>'; }
        var scoreColor = d.health_score >= 70 ? 'good' : (d.health_score >= 40 ? 'warn' : 'danger');
        var prevOdo = d.previous_odo ? '<div class="cc-row"><span class="label">ODO Sebelumnya</span><span class="value">' + d.previous_odo.odo_km.toLocaleString('id-ID') + ' km (' + d.previous_odo.date + ')</span></div><div class="cc-row"><span class="label">Selisih ODO</span><span class="value" style="color:' + (d.odo_diff < 0 ? '#dc2626' : '#059669') + '">' + (d.odo_diff >= 0 ? '+' : '') + d.odo_diff.toLocaleString('id-ID') + ' km</span></div>' : '<div class="cc-row"><span class="label">ODO Sebelumnya</span><span class="value" style="color:var(--gray-500);">Belum ada data</span></div>';
        var actionLabel = action === 'payout' ? '💸 Approve & Keluarkan Dana' : '✅ Approve';
        document.getElementById('ccBody').innerHTML = '<div class="cc-score"><span style="font-weight:700;">🏥 Health Score:</span><div class="cc-score-bar"><div class="cc-score-fill ' + scoreColor + '" style="width:' + d.health_score + '%;"></div></div><span style="font-weight:700;">' + d.health_score + '/100</span></div>' +
            '<div style="font-weight:600;font-size:13px;margin:10px 0 6px;">📋 Detail Transaksi:</div>' +
            '<div class="cc-row"><span class="label">Nopol</span><span class="value">' + d.current.nopol + '</span></div>' +
            '<div class="cc-row"><span class="label">Driver</span><span class="value">' + d.current.driver_name + '</span></div>' + prevOdo +
            '<div class="cc-row"><span class="label">Nominal</span><span class="value">Rp ' + d.current.nominal.toLocaleString('id-ID') + '</span></div>' +
            '<div style="font-weight:600;font-size:13px;margin:12px 0 6px;">🚩 Flags:</div>' + flagsHtml +
            '<div class="cc-recommendation ' + d.overall + '">' + d.recommendation + '</div>' +
            '<div class="cc-actions"><button class="btn btn-secondary" onclick="closeCC()" style="background:var(--gray-200);color:var(--gray-700);">Tutup</button>' +
            '<button class="btn btn-success" onclick="completeAction(\'' + action + '\',' + txId + ')">' + actionLabel + '</button></div>';
    } catch(e) { document.getElementById('ccBody').innerHTML = '<p style="color:red;">Error memuat data</p>'; }
}
function closeCC() { document.getElementById('ccModal').classList.remove('active'); }

/* ============================================================ */
/* ODO EDIT                                                     */
/* ============================================================ */

var currentEditTxId = null;
function openOdoEdit(txId, currentOdo) {
    currentEditTxId = txId;
    document.getElementById('currentOdo').value = currentOdo.toLocaleString('id-ID') + ' km';
    document.getElementById('newOdo').value = ''; document.getElementById('odoRemark').value = '';
    document.getElementById('odoPin').value = ''; document.getElementById('odoError').style.display = 'none';
    document.getElementById('odoModal').classList.add('active');
}
function closeOdoEdit() { document.getElementById('odoModal').classList.remove('active'); currentEditTxId = null; }
async function submitOdoEdit() {
    var newOdo = parseInt(document.getElementById('newOdo').value);
    var remark = document.getElementById('odoRemark').value.trim();
    var pin = document.getElementById('odoPin').value;
    var errEl = document.getElementById('odoError');
    if (!newOdo || newOdo <= 0) { errEl.textContent = 'ODO baru tidak valid'; errEl.style.display = 'block'; return; }
    if (!remark) { errEl.textContent = 'Alasan perubahan wajib diisi'; errEl.style.display = 'block'; return; }
    if (pin.length !== 6) { errEl.textContent = 'PIN 6-digit wajib diisi'; errEl.style.display = 'block'; return; }
    errEl.style.display = 'none';
    try {
        var r = await fetch('/admin/edit-odo/' + currentEditTxId, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ new_odo: newOdo, remark: remark, pin: pin, username: 'finance_officer' }) });
        var d = await r.json();
        if (d.status === 'success') { toast('✅ ' + d.msg, 'success'); closeOdoEdit(); setTimeout(function() { location.reload(); }, 600); }
        else { errEl.textContent = d.msg || 'Gagal menyimpan'; errEl.style.display = 'block'; }
    } catch(e) { errEl.textContent = 'Error koneksi'; errEl.style.display = 'block'; }
}

/* ============================================================ */
/* FINANCE REVIEW                                               */
/* ============================================================ */

async function openFinanceReview(txId) {
    document.getElementById('revTxId').textContent = '#' + txId;
    document.getElementById('reviewPhotos').innerHTML = '<p style="color:#94a3b8;text-align:center;padding:40px;">⏳ Memuat...</p>';
    document.getElementById('reviewData').innerHTML = '<p style="color:var(--gray-500);text-align:center;padding:20px;">⏳ Memuat...</p>';
    document.getElementById('reviewOverlay').classList.add('active');
    try {
        var r = await fetch('/api/finance-review/' + txId); var d = await r.json();
        if (d.error) { toast('Error: ' + d.error, 'error'); return; }
        var photosHtml = '';
        if (d.photos && d.photos.length > 0) { d.photos.forEach(function(p) { photosHtml += '<div class="review-photo-item" onclick="openZoom(\'' + p.url + '\')"><img src="' + p.url + '" alt="' + p.label + '" loading="lazy"><div class="photo-label">📷 ' + p.label + '</div></div>'; }); }
        else { photosHtml = '<p style="color:#94a3b8;text-align:center;padding:40px;">Tidak ada foto</p>'; }
        document.getElementById('reviewPhotos').innerHTML = photosHtml;
        var tx = d.transaction, prev = d.previous_odo, odoDiff = prev ? tx.odo_km - prev.odo_km : 0;
        var budgetPct = d.budget > 0 ? Math.round(d.monthly.total_nominal / d.budget * 100) : 0;
            var budgetColor = budgetPct > 80 ? '#dc2626' : (budgetPct > 60 ? '#d97706' : '#059669');
            document.getElementById('reviewData').innerHTML = '<h4>📋 Data Transaksi</h4>' +
            '<div class="info-row"><span class="lbl">Nopol</span><span class="val">' + tx.nopol + '</span></div>' +
            '<div class="info-row"><span class="lbl">Driver</span><span class="val">' + tx.driver_name + '</span></div>' +
            '<div class="info-row"><span class="lbl">Kendaraan</span><span class="val">' + (tx.vehicle_type || 'AVANZA') + ' · ' + (tx.bbm_type || 'PERTALITE') + '</span></div>' +
            '<div class="info-row"><span class="lbl">Tanggal</span><span class="val">' + new Date(tx.created_at).toLocaleString('id-ID') + '</span></div>' +
            '<div class="info-row"><span class="lbl">Nominal</span><span class="val" style="font-size:14px;color:var(--primary-dark);">Rp ' + tx.nominal.toLocaleString('id-ID') + '</span></div>' +
            '<div class="info-row"><span class="lbl">Volume</span><span class="val">' + tx.liter + ' L (@Rp ' + (tx.price_per_liter || 0).toLocaleString('id-ID') + ')</span></div>' +
            '<div class="info-row"><span class="lbl">ODO</span><span class="val">' + tx.odo_km.toLocaleString('id-ID') + ' km</span></div>' +
            (prev ? '<div class="info-row"><span class="lbl">ODO Sebelumnya</span><span class="val">' + prev.odo_km.toLocaleString('id-ID') + ' km (' + prev.date + ')</span></div>' : '') +
            (prev ? '<div class="info-row"><span class="lbl">Selisih ODO</span><span class="val" style="color:' + (odoDiff < 0 ? '#dc2626' : '#059669') + '">' + (odoDiff >= 0 ? '+' : '') + odoDiff.toLocaleString('id-ID') + ' km</span></div>' : '') +
            '<div class="info-row"><span class="lbl">KM/L</span><span class="val">' + (tx.km_per_liter || 'N/A') + '</span></div>' +
            '<div class="info-row"><span class="lbl">Appointment</span><span class="val">' + (tx.jumlah_appointment || 0) + 'x</span></div>' +
            '<div class="info-row"><span class="lbl">SPBU</span><span class="val">' + (tx.spbu_type || '-') + '</span></div>' +
            '<div class="info-row"><span class="lbl">GPS</span><span class="val" style="font-size:10px;">' + (tx.gps_address || 'Tidak tersedia') + '</span></div>' +
            '<div class="info-row"><span class="lbl">Budget Bulanan</span><span class="val" style="color:' + budgetColor + '">Rp ' + d.monthly.total_nominal.toLocaleString('id-ID') + ' / Rp ' + d.budget.toLocaleString('id-ID') + ' (' + budgetPct + '%)</span></div>' +
            '<div class="info-row"><span class="lbl">Status</span><span class="val">' + tx.status.toUpperCase() + '</span></div>' +
            '<div class="review-remark"><h4 style="margin-top:12px;">📝 Remark Finance</h4><textarea id="reviewRemark" placeholder="Tambahkan catatan..."></textarea>' +
            '<button class="btn btn-info btn-sm" onclick="submitFinanceRemark(' + txId + ')">💾 Simpan Remark</button><p id="remarkStatus" style="font-size:10px;"></p></div>';
    } catch(e) { document.getElementById('reviewData').innerHTML = '<p style="color:#dc2626;">Error memuat data</p>'; }
}
function openZoom(url) { document.getElementById('zoomImage').src = url; document.getElementById('zoomOverlay').classList.add('active'); }
function closeZoom() { document.getElementById('zoomOverlay').classList.remove('active'); }
function closeReview() { document.getElementById('reviewOverlay').classList.remove('active'); }
async function submitFinanceRemark(txId) {
    var remark = document.getElementById('reviewRemark').value.trim();
    if (!remark) { document.getElementById('remarkStatus').textContent = 'Remark tidak boleh kosong'; return; }
    try {
        var r = await fetch('/api/finance-remark', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tx_id: txId, remark: remark, username: 'Finance Officer' }) });
        var d = await r.json();
        document.getElementById('remarkStatus').textContent = d.msg;
        document.getElementById('remarkStatus').style.color = d.status === 'success' ? '#059669' : '#dc2626';
        if (d.status === 'success') toast('💾 Remark tersimpan', 'success');
    } catch(e) { document.getElementById('remarkStatus').textContent = 'Error'; }
}

/* ============================================================ */
/* HEALTH WIDGET                                                */
/* ============================================================ */

var healthData = null;
async function toggleHealth() {
    var widget = document.getElementById('healthWidget'), btn = document.getElementById('healthToggleBtn');
    if (widget.style.display === 'none') { widget.style.display = 'block'; btn.textContent = 'Sembunyikan';
        if (!healthData) { try { var r = await fetch('/api/vehicle-health'); healthData = await r.json(); renderHealthCards(healthData); } catch(e) {} }
    } else { widget.style.display = 'none'; btn.textContent = 'Tampilkan'; }
}
function renderHealthCards(data) {
    document.getElementById('avgHealth').textContent = data.avg_fleet_health || 0;
    var html = '';
    if (data.units && data.units.length > 0) {
        data.units.forEach(function(u) {
            html += '<div class="health-card"><div class="score-circle '+(u.status||'good')+'">'+u.health_score+'</div><div class="nopol">'+u.nopol+'</div><div class="driver">👤 '+(u.current_driver||'-')+' | '+u.vehicle_type+'</div>' +
                '<div class="stats"><div>KM/L: <span>'+(u.avg_kml||'-')+'</span></div><div>Transaksi: <span>'+u.total_tx+'x</span></div><div>Appt: <span>'+(u.total_appt||0)+'x</span></div><div>Biaya: <span>Rp '+((u.total_nominal||0)/1000).toFixed(0)+'K</span></div></div>' +
                (u.latest_notes?'<div style="font-size:10px;color:#d97706;margin-top:6px;">📝 '+u.latest_notes+'</div>':'')+'<button class="remark-btn" onclick="quickRemark(\''+u.nopol+'\')">+ Remark</button></div>';
        });
    } else { html = '<p style="color:var(--gray-500);padding:20px;text-align:center;">Belum ada data kendaraan</p>'; }
    document.getElementById('healthCards').innerHTML = html;
}
function quickRemark(nopol) { document.getElementById('remarkNopol').value = nopol; document.getElementById('remarkText').value = ''; document.getElementById('remarkModal').classList.add('active'); }
function openRemarkModal() { document.getElementById('remarkNopol').value = ''; document.getElementById('remarkText').value = ''; document.getElementById('remarkModal').classList.add('active'); }
function closeRemark() { document.getElementById('remarkModal').classList.remove('active'); }
async function submitRemark() {
    var nopol = document.getElementById('remarkNopol').value.trim(), remark = document.getElementById('remarkText').value.trim(), ga = document.getElementById('remarkGA').value.trim();
    if (!nopol || !remark) { document.getElementById('remarkMsg').textContent = 'Nopol dan remark wajib!'; return; }
    try {
        var r = await fetch('/api/assignment-remark', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({nopol:nopol, remark:remark, driver_name:ga}) });
        var d = await r.json();
        document.getElementById('remarkMsg').textContent = d.msg;
        if (d.status === 'success') { toast('📝 Remark tersimpan', 'success'); setTimeout(function(){ closeRemark(); healthData = null; toggleHealth(); toggleHealth(); }, 800); }
    } catch(e) {}
}

/* ============================================================ */
/* EVENT LISTENERS                                              */
/* ============================================================ */

document.getElementById('pinModal').addEventListener('click', function(e){ if(e.target===this) closePin(); });
document.getElementById('rejectModal').addEventListener('click', function(e){ if(e.target===this) closeReject(); });
document.getElementById('ccModal').addEventListener('click', function(e){ if(e.target===this) closeCC(); });
document.getElementById('odoModal').addEventListener('click', function(e){ if(e.target===this) closeOdoEdit(); });
document.getElementById('reviewOverlay').addEventListener('click', function(e){ if(e.target===this) closeReview(); });
document.getElementById('remarkModal').addEventListener('click', function(e){ if(e.target===this) closeRemark(); });
document.addEventListener('keydown', function(e){ if(e.key==='Escape') { closePin(); closeReject(); closeReview(); closeZoom(); } });
document.getElementById('pinInput').addEventListener('keydown', function(e){ if(e.key==='Enter') submitPin(); });

/* ============================================================ */
/* ARCHIVE (kept server-render flow)                             */
/* ============================================================ */

var archivePage = 1, archiveLimit = 50;
async function loadArchive() {
    var s = document.getElementById('archiveSearch')?.value || '';
    var sd = document.getElementById('archiveStartDate')?.value || '';
    var ed = document.getElementById('archiveEndDate')?.value || '';
    var bb = document.getElementById('archiveBbm')?.value || '';
    var params = new URLSearchParams({page: archivePage, limit: archiveLimit});
    if (s) params.append('search', s);
    if (sd) params.append('start_date', sd);
    if (ed) params.append('end_date', ed);
    if (bb) params.append('bbm_type', bb);
    try {
        var r = await fetch('/api/transactions/archive?' + params.toString());
        var d = await r.json();
        var summary = document.getElementById('archiveSummary');
        if (summary) summary.textContent = d.total + ' data | Rp ' + Number(d.summary?.total_nominal || 0).toLocaleString('id-ID');
        var u = new URL(window.location);
        u.searchParams.set('tab', 'archive');
        if (s) u.searchParams.set('search', s); else u.searchParams.delete('search');
        if (sd) u.searchParams.set('start_date', sd); else u.searchParams.delete('start_date');
        if (ed) u.searchParams.set('end_date', ed); else u.searchParams.delete('end_date');
        if (bb) u.searchParams.set('bbm_type', bb); else u.searchParams.delete('bbm_type');
        u.searchParams.set('page', archivePage);
        window.location.href = u.toString();
    } catch (e) { console.error('Archive error:', e); }
}
function filterArchive() { archivePage = 1; loadArchive(); }
function clearArchiveFilter() { window.location.href = '?tab=archive'; }
