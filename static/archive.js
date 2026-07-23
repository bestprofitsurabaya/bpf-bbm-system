// ============================================================
// ARCHIVE TAB - Pagination + Search + Filter
// ============================================================
var archivePage = 1;
var archiveTotalPages = 1;
var archiveLoading = false;

async function loadArchive(page) {
    if (archiveLoading) return;
    archiveLoading = true;
    page = page || 1;
    archivePage = page;
    
    // Show skeleton
    document.getElementById('archiveTableBody').innerHTML = '<div class="skeleton" style="height:60px;"></div><div class="skeleton" style="height:60px;"></div><div class="skeleton" style="height:60px;"></div>';
    
    var params = new URLSearchParams({
        page: page, limit: 50,
        search: document.getElementById('archiveSearch').value,
        start_date: document.getElementById('archiveStartDate').value,
        end_date: document.getElementById('archiveEndDate').value,
        bbm_type: document.getElementById('archiveBbmType').value
    });
    
    try {
        var r = await fetch('/api/transactions/archive?' + params.toString());
        var d = await r.json();
        if (d.error) { console.error(d.error); return; }
        archiveTotalPages = d.total_pages;
        renderArchiveTable(d.data);
        renderArchiveSummary(d);
        renderArchivePagination(d);
    } catch(e) { console.error(e); }
    finally { archiveLoading = false; }
}

function renderArchiveSummary(d) {
    var el = document.getElementById('archiveSummary');
    if (!el) return;
    var nominal = (d.summary.total_nominal || 0).toLocaleString('id-ID');
    el.innerHTML = '📊 ' + d.data.length + ' dari <strong>' + d.total + '</strong> data · Total <strong>Rp ' + nominal + '</strong>';
}

function renderArchiveTable(data) {
    var el = document.getElementById('archiveTableBody');
    if (!el) return;
    if (!data || data.length === 0) {
        el.innerHTML = '<div class="empty-state"><div class="icon">📭</div><h3>Tidak Ada Data</h3><p>Coba ubah filter atau rentang tanggal</p></div>';
        return;
    }
    var rows = '';
    data.forEach(function(tx) {
        var date = tx.created_at ? new Date(tx.created_at).toLocaleDateString('id-ID', {day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}) : '-';
        var nominal = 'Rp ' + (tx.nominal || 0).toLocaleString('id-ID');
        var photos = '';
        ['foto_odo_sebelum','foto_nota_odo_sesudah','foto_struk'].forEach(function(f) {
            if (tx[f]) photos += '<a href="/uploads/' + tx[f] + '" target="_blank"><img src="/uploads/' + tx[f] + '" class="photo-thumb" loading="lazy"></a>';
        });
        rows += '<div class="tx-item">' +
            '<div class="tx-header">' +
                '<span class="nopol">' + (tx.display_id || '#'+tx.id) + ' · ' + tx.nopol + ' <small>(' + (tx.vehicle_type||'AVANZA') + ')</small></span>' +
                '<span class="badge badge-archive">ARCHIVED</span>' +
            '</div>' +
            '<div class="tx-detail">' +
                '<span><strong>' + tx.driver_name + '</strong></span>' +
                '<span>' + date + '</span>' +
                '<span>' + nominal + '</span>' +
                '<span>' + (tx.bbm_type||'PERTALITE') + ' · ' + tx.liter + 'L</span>' +
                '<span>ODO: ' + (tx.odo_km||0).toLocaleString('id-ID') + ' km</span>' +
            '</div>' +
            (photos ? '<div class="photo-gallery">' + photos + '</div>' : '') +
            '<div class="flex gap-2 flex-wrap" style="margin-top:10px;">' +
                '<a href="/finance/download-archive/' + tx.id + '" class="btn btn-outline btn-sm">📦 ZIP</a> ' +
                '<button class="review-btn btn-sm" onclick="openFinanceReview(' + tx.id + ')">🔍 Review</button> ' +
                '<a href="/admin/report/' + tx.id + '" class="btn btn-secondary btn-sm">📄 PDF</a>' +
            '</div>' +
        '</div>';
    });
    el.innerHTML = rows;
}

function renderArchivePagination(d) {
    var el = document.getElementById('archivePagination');
    if (!el || d.total_pages <= 1) { if(el) el.innerHTML = ''; return; }
    var html = '<div class="pagination">';
    if (d.page > 1) html += '<button class="btn btn-outline btn-sm" onclick="loadArchive(' + (d.page-1) + ')">◀</button>';
    var start = Math.max(1, d.page - 2), end = Math.min(d.total_pages, d.page + 2);
    for (var p = start; p <= end; p++) {
        html += '<button class="btn ' + (p === d.page ? 'active' : 'btn-outline') + ' btn-sm" onclick="loadArchive(' + p + ')">' + p + '</button>';
    }
    if (d.page < d.total_pages) html += '<button class="btn btn-outline btn-sm" onclick="loadArchive(' + (d.page+1) + ')">▶</button>';
    html += '</div>';
    el.innerHTML = html;
}

var archiveTimer = null;
function debounceArchive() { clearTimeout(archiveTimer); archiveTimer = setTimeout(loadArchive, 500); }

// Init dates
(function() {
    var today = new Date(), weekAgo = new Date(today); weekAgo.setDate(today.getDate() - 7);
    var endEl = document.getElementById('archiveEndDate'), startEl = document.getElementById('archiveStartDate');
    if (endEl) endEl.value = today.toISOString().split('T')[0];
    if (startEl) startEl.value = weekAgo.toISOString().split('T')[0];
})();
