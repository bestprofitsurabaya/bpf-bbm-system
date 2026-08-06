/* ============================================================ */
/* BPF FLEET SYSTEM - Admin Kasbon (Cash Request)                */
/* Load AFTER admin-ui.js                                       */
/* ============================================================ */

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
    if (!window._manualMode) { toast('⚠️ Mode manual belum diaktifkan. Buka Settings untuk mengubah.', 'warning'); return; }
    var code = parseInt(document.getElementById('dailyCodeInput').value);
    if (code < 100 || code > 2000) { toast('Kode harus 100-2000!', 'warning'); return; }
    var idn = await getVerifiedIdentity('finance_officer', 'Finance');
    if (!idn) return;
    try {
        var r = await fetch('/api/cash/daily-code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code }) });
        var d = await r.json();
        document.getElementById('dailyCodeMsg').textContent = '✅ ' + d.msg;
        document.getElementById('dailyCodeMsg').style.color = '#059669';
        window._dailyCode = code;
        toast(d.msg || 'Kode unik tersimpan', 'success');
    } catch(e) { toast('Error: ' + e.message, 'error'); }
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

async function approveCashGA(id) {
    var idn = await getVerifiedIdentity('ga_officer', 'GA');
    if (!idn) return;
    var ok = await confirmDialog({ title: '✅ Approve Kasbon', message: 'Setujui pengajuan kasbon #' + id + ' sebagai ' + idn.name + '?', okText: 'Setujui' });
    if (!ok) return;
    try {
        var r = await fetch('/api/cash/approve-ga/' + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ga_name: idn.name }) });
        var d = await r.json();
        toast(d.msg || 'Disetujui', d.status === 'success' ? 'success' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error koneksi', 'error'); }
}

async function approveCashFinance(id) {
    var idn = await getVerifiedIdentity('finance_officer', 'Finance');
    if (!idn) return;
    var ok = await confirmDialog({ title: '💰 Approve Finance', message: 'Cairkan dana kasbon #' + id + ' sebagai ' + idn.name + '?', okText: 'Cairkan' });
    if (!ok) return;
    try {
        var r = await fetch('/api/cash/approve-finance/' + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ finance_name: idn.name }) });
        var d = await r.json();
        toast(d.msg || 'Dana dicairkan', d.status === 'success' ? 'success' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error koneksi', 'error'); }
}

async function handoverCash(id) {
    var idn = await getVerifiedIdentity('ga_officer', 'GA');
    if (!idn) return;
    var ok = await confirmDialog({ title: '🤝 Serah Terima', message: 'Dana sudah diterima driver untuk kasbon #' + id + '?', okText: 'Ya, sudah' });
    if (!ok) return;
    try {
        var r = await fetch('/api/cash/handover/' + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ga_name: idn.name }) });
        var d = await r.json();
        toast(d.msg || 'Dana di driver', d.status === 'success' ? 'success' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error koneksi', 'error'); }
}

async function rejectCash(id) {
    var res = await showDialog({
        title: '⛔ Tolak Kasbon #' + id,
        message: 'Jelaskan alasan penolakan.',
        okText: 'Tolak', danger: true,
        fields: [{ id: 'reason', label: 'Alasan', type: 'textarea', required: true, placeholder: 'Alasan penolakan...' }]
    });
    if (!res) return;
    try {
        var r = await fetch('/api/cash/reject/' + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ reason: res.reason }) });
        var d = await r.json();
        toast(d.msg || 'Kasbon ditolak', d.status === 'success' ? 'warning' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error koneksi', 'error'); }
}

async function deleteCash(id) {
    var ok = await confirmDialog({ title: '🗑 Hapus Kasbon', message: 'HAPUS pengajuan #' + id + '? Hanya DRAFT yang bisa dihapus.', okText: 'Hapus', danger: true });
    if (!ok) return;
    try {
        var r = await fetch('/api/cash/delete/' + id, { method: 'POST' });
        var d = await r.json();
        toast(d.msg || 'Dihapus', d.status === 'success' ? 'success' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function editCash(id) {
    var res = await showDialog({
        title: '✏️ Edit Kasbon #' + id,
        message: 'Nominal dasar tanpa kode unik.',
        okText: 'Simpan',
        fields: [
            { id: 'amount', label: 'Nominal dasar', type: 'text', numeric: true, required: true, placeholder: 'Contoh: 500000' },
            { id: 'reason', label: 'Alasan edit', type: 'textarea', required: true, placeholder: 'Alasan revisi...' }
        ]
    });
    if (!res) return;
    try {
        var r = await fetch('/api/cash/edit/' + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ base_amount: parseInt(res.amount, 10), reason: res.reason }) });
        var d = await r.json();
        toast(d.msg || 'Kasbon diperbarui', d.status === 'success' ? 'success' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function cancelCash(id, hasLPJ) {
    var res = await showDialog({
        title: '↩️ Batal Kasbon #' + id,
        message: hasLPJ ? 'LPJ akan dihapus dan status kembali ke DRAFT.' : 'Semua approval akan di-reset ke DRAFT.',
        okText: 'Batalkan', danger: true,
        fields: [{ id: 'reason', label: 'Alasan pembatalan', type: 'textarea', required: true }]
    });
    if (!res) return;
    var endpoint = hasLPJ ? '/api/cash/reset-lpj/' : '/api/cash/cancel/';
    try {
        var r = await fetch(endpoint + id, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ reason: res.reason }) });
        var d = await r.json();
        toast(d.msg || 'Dibatalkan', d.status === 'success' ? 'warning' : 'error');
        loadCashRequests();
    } catch(e) { toast('Error: ' + e.message, 'error'); }
}
