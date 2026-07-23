#!/bin/bash
# ==============================================================================
# ENHANCE: Halaman Arsip - Search, Filter, Pagination
# ==============================================================================

cd ~/bpf-bbm-system
cp templates/admin.html "templates/admin.html.backup_archive_$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('templates/admin.html', 'r') as f:
    html = f.read()

# ============================================================
# 1. TAMBAH CSS untuk search/filter/pagination
# ============================================================
archive_css = """
        /* Archive Filter Bar */
        .filter-bar {
            display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
            padding: 12px 16px; background: #f8fafc; border-radius: 10px;
            margin-bottom: 14px; border: 1px solid #e2e8f0;
        }
        .filter-bar input, .filter-bar select {
            padding: 8px 12px; border: 1.5px solid #e2e8f0; border-radius: 8px;
            font-size: 12px; background: white;
        }
        .filter-bar input:focus, .filter-bar select:focus {
            border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
        }
        .filter-bar input { min-width: 180px; }
        .filter-bar .btn { white-space: nowrap; }
        
        /* Pagination */
        .pagination {
            display: flex; gap: 4px; justify-content: center; align-items: center;
            padding: 16px 0; flex-wrap: wrap;
        }
        .pagination button, .pagination span {
            padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 500;
            border: 1px solid #e2e8f0; background: white; cursor: pointer;
            transition: all 0.15s;
        }
        .pagination button:hover:not(:disabled) { background: #2563eb; color: white; border-color: #2563eb; }
        .pagination button.active { background: #2563eb; color: white; border-color: #2563eb; font-weight: 700; }
        .pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
        .pagination .info { border: none; color: #64748b; font-size: 11px; }
        
        /* Archive info bar */
        .archive-info {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 0; font-size: 11px; color: #64748b;
        }
"""

html = html.replace('</style>', archive_css + '\n    </style>')

# ============================================================
# 2. UPDATE TAB ARCHIVE - tambah filter bar
# ============================================================
# Cari bagian archive tab
old_archive = """{% elif stats.tab == 'archive' %}Arsip{% endif %}</span>
                <span style="font-size:12px;color:var(--gray-500);">{{ transactions|length }} transaksi</span>"""

new_archive = """{% elif stats.tab == 'archive' %}Arsip{% endif %}</span>
                <span style="font-size:12px;color:var(--gray-500);" id="archiveCount">0 transaksi</span>"""

if old_archive in html:
    html = html.replace(old_archive, new_archive)
    print("✓ Archive header updated")
else:
    print("⚠ Archive header not found")

# ============================================================
# 3. TAMBAH FILTER BAR + PAGINATION di archive section
# ============================================================
# Cari setelah card-header archive
old_card_body = """<div class="card-body">
                {% if transactions %}"""

new_card_body = """<div class="card-body">
                <!-- Filter Bar (only for archive) -->
                <div class="filter-bar" id="archiveFilterBar" style="display:none;">
                    <input type="text" id="archiveSearch" placeholder="🔍 Cari Nopol atau Driver..." oninput="filterArchive()">
                    <input type="date" id="archiveStartDate" onchange="filterArchive()" style="width:140px;">
                    <span style="color:#94a3b8;">s/d</span>
                    <input type="date" id="archiveEndDate" onchange="filterArchive()" style="width:140px;">
                    <button class="btn btn-outline btn-sm" onclick="resetArchiveFilter()">🔄 Reset</button>
                    <span style="font-size:11px;color:#64748b;margin-left:auto;" id="archiveInfo"></span>
                </div>
                <div id="archiveTableContainer">
                {% if transactions %}"""

html = html.replace(old_card_body, new_card_body)

# Cari penutup archive section
old_end = """{% else %}
                    <div class="empty">Tidak ada transaksi.</div>
                {% endif %}
            </div>"""

new_end = """{% else %}
                    <div class="empty">Tidak ada transaksi.</div>
                {% endif %}
                </div>
                <!-- Pagination -->
                <div class="pagination" id="archivePagination" style="display:none;"></div>
            </div>"""

html = html.replace(old_end, new_end)
print("✓ Archive filter + pagination container added")

# ============================================================
# 4. TAMBAH JAVASCRIPT
# ============================================================
archive_js = """
    // ============================================================
    // ARCHIVE - Search, Filter, Pagination
    // ============================================================
    var archiveData = [];
    var archivePage = 1;
    var archivePerPage = 50;
    
    // Init archive: ambil semua data archived
    async function initArchive() {
        var isArchiveTab = window.location.href.indexOf('tab=archive') > -1;
        if (!isArchiveTab) return;
        
        document.getElementById('archiveFilterBar').style.display = 'flex';
        
        // Set default tanggal (7 hari terakhir)
        var today = new Date();
        var weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        document.getElementById('archiveStartDate').value = weekAgo.toISOString().split('T')[0];
        document.getElementById('archiveEndDate').value = today.toISOString().split('T')[0];
        
        await loadArchiveData();
    }
    
    async function loadArchiveData() {
        try {
            var res = await fetch('/api/transactions/archived');
            archiveData = await res.json();
            filterArchive();
        } catch(e) {
            console.error('Archive load error:', e);
        }
    }
    
    function filterArchive() {
        var search = (document.getElementById('archiveSearch').value || '').toLowerCase();
        var startDate = document.getElementById('archiveStartDate').value;
        var endDate = document.getElementById('archiveEndDate').value;
        
        // Filter
        var filtered = archiveData.filter(function(tx) {
            var nopol = (tx.nopol || '').toLowerCase();
            var driver = (tx.driver_name || '').toLowerCase();
            var matchSearch = !search || nopol.includes(search) || driver.includes(search);
            
            var txDate = tx.created_at ? tx.created_at.split(' ')[0] : '';
            var matchStart = !startDate || txDate >= startDate;
            var matchEnd = !endDate || txDate <= endDate;
            
            return matchSearch && matchStart && matchEnd;
        });
        
        // Sort terbaru di atas
        filtered.sort(function(a, b) {
            return (b.created_at || '').localeCompare(a.created_at || '');
        });
        
        // Pagination
        var totalPages = Math.ceil(filtered.length / archivePerPage);
        if (archivePage > totalPages) archivePage = 1;
        if (archivePage < 1) archivePage = 1;
        
        var start = (archivePage - 1) * archivePerPage;
        var paged = filtered.slice(start, start + archivePerPage);
        
        renderArchiveTable(paged);
        renderArchivePagination(filtered.length, totalPages);
        
        document.getElementById('archiveCount').textContent = filtered.length + ' transaksi';
        document.getElementById('archiveInfo').textContent = 
            'Menampilkan ' + (filtered.length > 0 ? (start + 1) + '-' + Math.min(start + archivePerPage, filtered.length) : '0') + 
            ' dari ' + filtered.length + ' data';
    }
    
    function renderArchiveTable(transactions) {
        var container = document.getElementById('archiveTableContainer');
        if (!container) return;
        
        if (transactions.length === 0) {
            container.innerHTML = '<div class="empty">Tidak ada transaksi yang cocok.</div>';
            return;
        }
        
        var html = '';
        transactions.forEach(function(tx) {
            var statusClass = 'badge-archive';
            var statusText = tx.status.replace(/_/g, ' ').toUpperCase();
            
            html += '<div class="tx-item">' +
                '<div class="tx-header">' +
                    '<span class="nopol">' + (tx.display_id || '#' + tx.id) + ' · ' + (tx.nopol || '-') + ' <small style="color:#94a3b8;">(' + (tx.vehicle_type || '-') + ')</small></span>' +
                    '<span class="badge ' + statusClass + '">' + statusText + '</span>' +
                '</div>' +
                '<div class="tx-detail">' +
                    '<span><strong>' + (tx.driver_name || '-') + '</strong></span>' +
                    '<span>' + (tx.created_at ? new Date(tx.created_at).toLocaleString('id-ID') : '-') + '</span>' +
                    '<span>Rp ' + (tx.nominal ? Number(tx.nominal).toLocaleString('id-ID') : '0') + '</span>' +
                    '<span>' + (tx.bbm_type || '-') + ' · ' + (tx.liter || '0') + 'L</span>' +
                    '<span>ODO: ' + (tx.odo_km ? Number(tx.odo_km).toLocaleString('id-ID') : '0') + ' km</span>' +
                    '<span>Appt: ' + (tx.jumlah_appointment || 0) + 'x</span>' +
                '</div>' +
                '<div class="photo-gallery">' +
                    (tx.foto_odo_sebelum ? '<a href="/uploads/' + tx.foto_odo_sebelum + '" target="_blank"><img src="/uploads/' + tx.foto_odo_sebelum + '" class="photo-thumb"></a>' : '') +
                    (tx.foto_nota_odo_sesudah ? '<a href="/uploads/' + tx.foto_nota_odo_sesudah + '" target="_blank"><img src="/uploads/' + tx.foto_nota_odo_sesudah + '" class="photo-thumb"></a>' : '') +
                    (tx.foto_struk ? '<a href="/uploads/' + tx.foto_struk + '" target="_blank"><img src="/uploads/' + tx.foto_struk + '" class="photo-thumb"></a>' : '') +
                '</div>' +
                '<div class="flex gap-2 flex-wrap" style="margin-top:10px;">' +
                    '<a href="/finance/download-archive/' + tx.id + '" class="btn btn-outline">📦 ZIP</a> ' +
                    '<button class="review-btn" onclick="openFinanceReview(' + tx.id + ')">🔍 Review</button> ' +
                    '<a href="/admin/report/' + tx.id + '" class="btn btn-secondary">📄 PDF</a>' +
                '</div>' +
            '</div>';
        });
        container.innerHTML = html;
    }
    
    function renderArchivePagination(total, totalPages) {
        var container = document.getElementById('archivePagination');
        if (!container || totalPages <= 1) {
            if (container) container.style.display = 'none';
            return;
        }
        container.style.display = 'flex';
        
        var html = '';
        html += '<button onclick="goToPage(1)" ' + (archivePage === 1 ? 'disabled' : '') + '>«</button>';
        html += '<button onclick="goToPage(' + (archivePage - 1) + ')" ' + (archivePage === 1 ? 'disabled' : '') + '>‹</button>';
        
        var startPage = Math.max(1, archivePage - 2);
        var endPage = Math.min(totalPages, archivePage + 2);
        
        if (startPage > 1) html += '<span class="info">...</span>';
        for (var i = startPage; i <= endPage; i++) {
            html += '<button class="' + (i === archivePage ? 'active' : '') + '" onclick="goToPage(' + i + ')">' + i + '</button>';
        }
        if (endPage < totalPages) html += '<span class="info">...</span>';
        
        html += '<button onclick="goToPage(' + (archivePage + 1) + ')" ' + (archivePage === totalPages ? 'disabled' : '') + '>›</button>';
        html += '<button onclick="goToPage(' + totalPages + ')" ' + (archivePage === totalPages ? 'disabled' : '') + '>»</button>';
        html += '<span class="info">' + total + ' data · ' + totalPages + ' hlm</span>';
        
        container.innerHTML = html;
    }
    
    function goToPage(page) {
        archivePage = page;
        filterArchive();
        document.getElementById('archiveTableContainer').scrollIntoView({behavior: 'smooth'});
    }
    
    function resetArchiveFilter() {
        document.getElementById('archiveSearch').value = '';
        var today = new Date();
        var weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        document.getElementById('archiveStartDate').value = weekAgo.toISOString().split('T')[0];
        document.getElementById('archiveEndDate').value = today.toISOString().split('T')[0];
        archivePage = 1;
        filterArchive();
    }
    
    // Init on load
    initArchive();
"""

# Sisipkan sebelum </script> penutup
html = html.replace('    </script>\n    \n    <!-- Service Worker', archive_js + '\n    </script>\n    \n    <!-- Service Worker')

with open('templates/admin.html', 'w') as f:
    f.write(html)
print("✓ Archive JS added")
PYEOF

# ============================================================
# 5. TAMBAH API ENDPOINT /api/transactions/archived
# ============================================================
python3 << 'PYEOF'
with open('modules/routes_api.py', 'r') as f:
    code = f.read()

if '/api/transactions/archived' not in code:
    archived_ep = """
    @app.route('/api/transactions/archived')
    def api_transactions_archived():
        try:
            conn = get_db_connection()
            if not conn: return jsonify({'error': 'DB error'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE status='archived' AND (is_dummy=0 OR is_dummy IS NULL) ORDER BY created_at DESC")
            data = cursor.fetchall()
            # Convert Decimal to float
            for tx in data:
                for key in ['nominal', 'liter', 'price_per_liter', 'odo_km', 'km_per_liter', 'jumlah_appointment']:
                    if tx.get(key) is not None:
                        tx[key] = float(tx[key])
            cursor.close(); conn.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
"""
    # Sisipkan setelah endpoint audit-logs
    marker = "@app.route('/api/audit-logs')"
    if marker in code:
        idx = code.find(marker)
        end = code.find("\n\n", idx + 50)
        if end > 0:
            code = code[:end] + archived_ep + code[end:]
            print("✓ /api/transactions/archived added")
    else:
        code += archived_ep
        print("✓ /api/transactions/archived appended")

with open('modules/routes_api.py', 'w') as f:
    f.write(code)
PYEOF

echo ""
echo "=== Rebuild ==="
docker compose down
docker compose build --no-cache web
docker compose up -d
sleep 15

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ ARCHIVE ENHANCED                                           ║"
echo "║                                                                ║"
echo "║  🔍 Search: cari Nopol atau Nama Driver                       ║"
echo "║  📅 Filter: default 7 hari terakhir, custom range             ║"
echo "║  📄 Pagination: max 50/halaman, navigasi « ‹ 1 2 3 › »      ║"
echo "║  📊 Info: "Menampilkan X-Y dari Z data"                       ║"
echo "║  🔄 Reset button                                               ║"
echo "║  ⚡ Client-side filtering (cepat)                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
