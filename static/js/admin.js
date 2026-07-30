/* ============================================================ */
/* BPF FLEET SYSTEM - Admin Dashboard Scripts                   */
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

// ---- PIN SYSTEM ----
var pendingAction = null, pendingTxId = null;

function requirePin(action, txId, role) {
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
            var name = encodeURIComponent(data.user.full_name);
            if (pendingAction === 'approve' && confirm('Setujui klaim #' + pendingTxId + '?'))
                window.location.href = '/ga/approve/' + pendingTxId + '?admin=' + name;
            else if (pendingAction === 'reject') { closePin(); showRejectModal(pendingTxId); }
            else if (pendingAction === 'payout' && confirm('Dana sudah dikeluarkan?'))
                window.location.href = '/finance/payout/' + pendingTxId + '?admin=' + name;
            else if (pendingAction === 'archive' && confirm('Driver sudah TTD?'))
                window.location.href = '/finance/archive/' + pendingTxId + '?admin=' + name;
        } else {
            document.getElementById('pinError').textContent = 'PIN salah!';
            document.getElementById('pinError').style.display = 'block';
            document.getElementById('pinInput').value = '';
            document.getElementById('pinInput').focus();
        }
    } catch(e) { document.getElementById('pinError').textContent = 'Error koneksi'; document.getElementById('pinError').style.display = 'block'; }
    finally { btn.textContent = 'Verifikasi'; btn.disabled = false; }
}

// ---- REJECT ----
function showRejectModal(txId) { document.getElementById('rejectForm').action = '/admin/reject/' + txId; document.getElementById('rejectModal').classList.add('active'); }
function closeReject() { document.getElementById('rejectModal').classList.remove('active'); }

// ---- CROSS-CHECK ----
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
        document.getElementById('ccBody').innerHTML = '<div class="cc-score"><span style="font-weight:700;">🏥 Health Score:</span><div class="cc-score-bar"><div class="cc-score-fill ' + scoreColor + '" style="width:' + d.health_score + '%;"></div></div><span style="font-weight:700;">' + d.health_score + '/100</span></div>' +
            '<div style="font-weight:600;font-size:13px;margin:10px 0 6px;">📋 Detail Transaksi:</div>' +
            '<div class="cc-row"><span class="label">Nopol</span><span class="value">' + d.current.nopol + '</span></div>' +
            '<div class="cc-row"><span class="label">Driver</span><span class="value">' + d.current.driver_name + '</span></div>' + prevOdo +
            '<div class="cc-row"><span class="label">Nominal</span><span class="value">Rp ' + d.current.nominal.toLocaleString('id-ID') + '</span></div>' +
            '<div style="font-weight:600;font-size:13px;margin:12px 0 6px;">🚩 Flags:</div>' + flagsHtml +
            '<div class="cc-recommendation ' + d.overall + '">' + d.recommendation + '</div>' +
            '<div class="cc-actions"><button class="btn btn-secondary" onclick="closeCC()" style="background:var(--gray-200);color:var(--gray-700);">Tutup</button>' +
            '<button class="btn btn-success" onclick="closeCC();requirePin(\'' + action + '\',' + txId + ',\'' + role + '\')">✅ Lanjut Approve</button></div>';
    } catch(e) { document.getElementById('ccBody').innerHTML = '<p style="color:red;">Error memuat data</p>'; }
}
function closeCC() { document.getElementById('ccModal').classList.remove('active'); }

// ---- ODO EDIT ----
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
        var r = await fetch('/admin/edit-odo/' + currentEditTxId, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({new_odo:newOdo, remark:remark, pin:pin, username:'finance_officer'}) });
        var d = await r.json();
        if (d.status === 'success') { alert('✅ ' + d.msg); closeOdoEdit(); location.reload(); }
        else { errEl.textContent = d.msg || 'Gagal menyimpan'; errEl.style.display = 'block'; }
    } catch(e) { errEl.textContent = 'Error koneksi'; errEl.style.display = 'block'; }
}

// ---- FINANCE REVIEW ----
async function openFinanceReview(txId) {
    document.getElementById('revTxId').textContent = '#' + txId;
    document.getElementById('reviewPhotos').innerHTML = '<p style="color:#94a3b8;text-align:center;padding:40px;">⏳ Memuat...</p>';
    document.getElementById('reviewData').innerHTML = '<p style="color:var(--gray-500);text-align:center;padding:20px;">⏳ Memuat...</p>';
    document.getElementById('reviewOverlay').classList.add('active');
    try {
        var r = await fetch('/api/finance-review/' + txId); var d = await r.json();
        if (d.error) { alert(d.error); return; }
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
        var r = await fetch('/api/finance-remark', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({tx_id:txId, remark:remark, username:'Finance Officer'}) });
        var d = await r.json();
        document.getElementById('remarkStatus').textContent = d.msg;
        document.getElementById('remarkStatus').style.color = d.status === 'success' ? '#059669' : '#dc2626';
    } catch(e) { document.getElementById('remarkStatus').textContent = 'Error'; }
}

// ---- CASH REQUESTS ----
async function loadDailyCode() {
    try {
        var r = await fetch('/api/cash/daily-code');
        var d = await r.json();
        window._dailyCode = d.code;
        window._manualMode = d.manual_mode;
        var inp = document.getElementById('dailyCodeInput');
        if (inp) {
            inp.value = d.code;
            inp.readOnly = !d.manual_mode;
            inp.style.background = d.manual_mode ? '#fff' : '#f1f5f9';
        }
    } catch(e) {}
}

async function setDailyCode() {
    if (!window._manualMode) { alert('⚠️ Mode manual belum diaktifkan. Buka Settings untuk mengubah.'); return; }
    var code = parseInt(document.getElementById('dailyCodeInput').value);
    if (code < 100 || code > 2000) { alert('Kode harus 100-2000!'); return; }
    
    // Verifikasi PIN Finance
    var pin = prompt('🔒 Verifikasi PIN Finance untuk mengubah kode unik:');
    if (!pin || pin.length !== 6) { alert('PIN 6-digit wajib!'); return; }
    
    try {
        // Verify PIN dulu
        var v = await fetch('/api/verify-pin', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:'finance_officer', pin:pin}) });
        var vd = await v.json();
        if (vd.status !== 'success') { alert('❌ PIN Finance salah!'); return; }
        
        // Set kode
        var r = await fetch('/api/cash/daily-code', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({code:code}) });
        var d = await r.json();
        document.getElementById('dailyCodeMsg').textContent = '✅ ' + d.msg;
        document.getElementById('dailyCodeMsg').style.color = '#059669';
        window._dailyCode = code;
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadCashRequests() {
    await loadDailyCode();
    try {
        var r = await fetch('/api/cash/history'); var data = await r.json();
        document.getElementById('cashCount').textContent = data.length + ' pengajuan';
        if (data.length === 0) { document.getElementById('cashRequestList').innerHTML = '<div class="empty">Tidak ada pengajuan kasbon.</div>'; return; }
        var steps=['DRAFT','GA_APPROVED','FINANCE_APPROVED','FUNDS_WITH_DRIVER','LPJ_SUBMITTED','COMPLETED'];
        var stepLabels=['📝','✅','💰','🤝','📋','🎉'];
        var statusColor = {'DRAFT':'#94a3b8','GA_APPROVED':'#0891b2','FINANCE_APPROVED':'#d97706','FUNDS_WITH_DRIVER':'#059669','LPJ_SUBMITTED':'#2563eb','COMPLETED':'#059669','REJECTED':'#dc2626'};
        var html = '';
        for (var i = 0; i < data.length; i++) {
            var c = data[i], color = statusColor[c.status] || '#94a3b8';
            var currentStep = steps.indexOf(c.status); if(currentStep<0) currentStep=0;
            var pct = c.status==='COMPLETED'?100:Math.round((currentStep/(steps.length-1))*100);
            var barColor = c.status==='COMPLETED'?'#059669':pct>=60?'#2563eb':pct>=30?'#d97706':'#94a3b8';
            html += '<div style="background:white;padding:14px;border-radius:8px;margin-bottom:8px;border-left:4px solid '+color+';box-shadow:0 1px 3px rgba(0,0,0,0.06);">' +
                '<div style="display:flex;justify-content:space-between;"><strong>'+c.display_id+'</strong><span style="background:'+color+';color:white;padding:3px 10px;border-radius:12px;font-size:10px;">'+c.status.replace(/_/g,' ')+'</span></div>' +
                '<div style="margin-top:4px;font-size:12px;">👤 '+c.driver_name+' | 🚗 '+(c.nopol||'-')+' | ⛽ '+c.bbm_type+'</div>' +
                '<div style="margin-top:4px;font-weight:700;color:#2563eb;">Rp '+Number(c.total_amount).toLocaleString('id-ID')+' <small>(kode: '+c.daily_code+')</small></div>' +
                '<div style="margin-top:6px;background:#e2e8f0;border-radius:4px;height:5px;"><div style="background:'+barColor+';height:100%;width:'+pct+'%;border-radius:4px;"></div></div>' +
                '<div style="display:flex;justify-content:space-between;margin-top:2px;font-size:9px;color:#94a3b8;">';
            for(var s=0;s<steps.length;s++){ html += '<span style="color:'+(s<=currentStep?barColor:'#cbd5e1')+';">'+stepLabels[s]+'</span>'; }
            html += '</div><div style="margin-top:8px;">';
            if (c.status === 'DRAFT') { html += '<button class="btn btn-info btn-sm" onclick="approveCashGA('+c.id+')">✅ GA Approve</button> <button class="btn btn-danger btn-sm" onclick="rejectCash('+c.id+')">❌ Tolak</button> <button class="btn btn-sm" style="background:#f59e0b;color:white;" onclick="editCash('+c.id+')">✏️ Edit</button> <button class="btn btn-secondary btn-sm" onclick="deleteCash('+c.id+')">🗑 Hapus</button>'; }
            else if (c.status === 'GA_APPROVED') { html += '<button class="btn btn-success btn-sm" onclick="approveCashFinance('+c.id+')">💰 Finance Approve</button> <button class="btn btn-warning btn-sm" onclick="cancelCash('+c.id+',false)">↩ Batal</button>'; }
            else if (c.status === 'FINANCE_APPROVED') { html += '<button class="btn btn-warning btn-sm" onclick="handoverCash('+c.id+')">🤝 Serahkan ke Driver</button> <button class="btn btn-warning btn-sm" onclick="cancelCash('+c.id+',false)" style="background:#94a3b8;">↩ Batal</button>'; }
            else if (c.status === 'FUNDS_WITH_DRIVER') { html += '<span style="color:#059669;">✅ Dana di Driver - Menunggu LPJ</span> <button class="btn btn-warning btn-sm" onclick="cancelCash('+c.id+',false)" style="background:#94a3b8;font-size:10px;">↩ Batal</button>'; }
            else if (c.status === 'COMPLETED') { html += '<span style="color:#059669;">🎉 Selesai</span> <button class="btn btn-warning btn-sm" onclick="cancelCash('+c.id+',true)" style="background:#94a3b8;font-size:10px;">🔄 Reset LPJ</button>'; }
            html += '</div></div>';
        }
        document.getElementById('cashRequestList').innerHTML = html;
    } catch(e) { console.error(e); }
}
async function approveCashGA(id) { var ga = prompt('Nama GA:')||'GA Officer'; if(!confirm('Approve?'))return; await fetch('/api/cash/approve-ga/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ga_name:ga})}); loadCashRequests(); }
async function approveCashFinance(id) { var fin = prompt('Nama Finance:')||'Finance Officer'; if(!confirm('Cairkan?'))return; await fetch('/api/cash/approve-finance/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({finance_name:fin})}); loadCashRequests(); }
async function handoverCash(id) { var ga = prompt('Nama GA:')||'GA Officer'; if(!confirm('Dana sudah di Driver?'))return; await fetch('/api/cash/handover/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ga_name:ga})}); loadCashRequests(); }
async function rejectCash(id) { var reason = prompt('Alasan:'); if(!reason)return; await fetch('/api/cash/reject/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reason:reason})}); loadCashRequests(); }

// ---- HEALTH WIDGET ----
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
        if (d.status === 'success') { setTimeout(function(){ closeRemark(); healthData = null; toggleHealth(); toggleHealth(); }, 1000); }
    } catch(e) {}
}

// ---- EVENT LISTENERS ----
document.getElementById('pinModal').addEventListener('click', function(e){ if(e.target===this) closePin(); });
document.getElementById('rejectModal').addEventListener('click', function(e){ if(e.target===this) closeReject(); });
document.getElementById('ccModal').addEventListener('click', function(e){ if(e.target===this) closeCC(); });
document.getElementById('odoModal').addEventListener('click', function(e){ if(e.target===this) closeOdoEdit(); });
document.getElementById('reviewOverlay').addEventListener('click', function(e){ if(e.target===this) closeReview(); });
document.getElementById('remarkModal').addEventListener('click', function(e){ if(e.target===this) closeRemark(); });
document.addEventListener('keydown', function(e){ if(e.key==='Escape') { closePin(); closeReject(); closeReview(); closeZoom(); } });
document.getElementById('pinInput').addEventListener('keydown', function(e){ if(e.key==='Enter') submitPin(); });

// ---- ARCHIVE ----
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
        // Reload with filters (server-side rendering)
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

// ---- INIT ----
async function deleteCash(id) {
    if (!confirm('HAPUS pengajuan ini? Hanya DRAFT yang bisa dihapus.')) return;
    try {
        var r = await fetch('/api/cash/delete/' + id, { method: 'POST' });
        var d = await r.json();
        alert(d.msg);
        loadCashRequests();
    } catch(e) { alert('Error: ' + e.message); }
}

if (document.getElementById('dailyCodeInput')) loadDailyCode();

async function editCash(id) {
    var newBase = prompt('Nominal dasar baru (tanpa kode unik):');
    if (!newBase || isNaN(newBase) || parseInt(newBase) <= 0) return;
    var reason = prompt('Alasan edit:') || 'Revisi nominal';
    try {
        var r = await fetch('/api/cash/edit/' + id, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({base_amount:parseInt(newBase), reason:reason}) });
        var d = await r.json();
        alert(d.msg);
        loadCashRequests();
    } catch(e) { alert('Error: ' + e.message); }
}

async function cancelCash(id, hasLPJ) {
    var reason = prompt('Alasan pembatalan:');
    if (!reason) return;
    if (!confirm('BATALKAN pengajuan ini?\n\n' + (hasLPJ ? 'LPJ akan dihapus dan status kembali ke DRAFT.' : 'Semua approval akan di-reset ke DRAFT.'))) return;
    var endpoint = hasLPJ ? '/api/cash/reset-lpj/' : '/api/cash/cancel/';
    try {
        var r = await fetch(endpoint + id, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({reason:reason}) });
        var d = await r.json();
        alert(d.msg);
        loadCashRequests();
    } catch(e) { alert('Error: ' + e.message); }
}

if (document.getElementById('cashRequestList')) loadCashRequests();
