// ============================================================
// CHIEF DRIVER COMMAND CENTER
// ============================================================
(function () {
    'use strict';

    var currentDate = document.getElementById('dateInput').value || new Date().toISOString().split('T')[0];
    var allDrivers = [];
    var suggestions = { '1': null, '2': null };
    var reloadTimer = null;
    var areaLookup = {};
    var memberFilter = '';

    function getCSRF() {
        var m = document.querySelector('meta[name="csrf-token"]');
        return m ? m.getAttribute('content') : '';
    }

    function api(url, opts) {
        opts = opts || {};
        opts.headers = opts.headers || {};
        opts.headers['X-CSRF-Token'] = getCSRF();
        if (opts.body && typeof opts.body !== 'string') {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(opts.body);
        }
        return fetch(url, opts).then(function (r) { return r.json(); });
    }

    function toast(msg, type) {
        var t = document.createElement('div');
        t.className = 'toast' + (type ? ' ' + type : '');
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(function () { t.style.opacity = '0'; t.style.transition = 'opacity 0.3s'; }, 2800);
        setTimeout(function () { t.remove(); }, 3200);
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    // ============================================================
    // LOAD
    // ============================================================
    function loadDrivers() {
        return fetch('/api/drivers')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                allDrivers = (Array.isArray(data) ? data : []).filter(function (d) { return d.is_active && d.name; });
            })
            .catch(function () { allDrivers = []; });
    }

    function loadSuggestions() {
        return fetch('/api/appointments/suggestions?date=' + currentDate)
            .then(function (r) { return r.json(); })
            .then(function (d) { suggestions = d || {}; })
            .catch(function () {});
    }

    function loadMembers() {
        return fetch('/api/marketing/members')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                var options = (d && d.members) || [];
                var dl = document.getElementById('memberFilterList');
                if (!dl) return;
                dl.innerHTML = options.map(function (m) {
                    return '<option value="' + escapeHtml(m) + '"></option>';
                }).join('');
            })
            .catch(function () {});
    }

    function driverOptions(selected) {
        var opts = '<option value="">-- Pilih Driver --</option>';
        allDrivers.forEach(function (d) {
            var sel = d.name === selected ? ' selected' : '';
            opts += '<option value="' + escapeHtml(d.name) + '"' + sel + '>' + escapeHtml(d.name) + '</option>';
        });
        return opts;
    }

    function loadAll() {
        Promise.all([
            loadDrivers(),
            loadSuggestions(),
            loadMembers(),
            fetch('/api/appointments?date=' + currentDate + (memberFilter ? '&member=' + encodeURIComponent(memberFilter) : '')).then(function (r) { return r.json(); }),
            fetch('/api/appointments/driver-summary?date=' + currentDate).then(function (r) { return r.json(); }),
            fetch('/api/appointments/member-summary?date=' + currentDate).then(function (r) { return r.json(); })
        ]).then(function (results) {
            // Urutan results: 0=drivers, 1=suggestions, 2=members, 3=appointments, 4=driver-summary, 5=member-summary
            renderAll(results[3]);
            document.getElementById('integratedCount').textContent =
                (results[4] && results[4].completed) || 0;
            renderMemberSummary((results[5] && results[5].members) || []);
        }).catch(function () {});
    }

    var memberFilterTimer = null;
    function applyMemberFilter(name) {
        clearTimeout(memberFilterTimer);
        document.getElementById('memberFilter').value = name;
        memberFilter = name;
        var info = document.getElementById('memberFilterInfo');
        if (memberFilter) {
            info.textContent = '👤 Menampilkan: ' + memberFilter;
            info.style.display = 'inline-block';
        } else {
            info.style.display = 'none';
        }
        loadAll();
    }

    function onMemberFilterInput() {
        clearTimeout(memberFilterTimer);
        memberFilterTimer = setTimeout(function () {
            applyMemberFilter(document.getElementById('memberFilter').value.trim());
        }, 300);
    }

    function clearMemberFilter() {
        applyMemberFilter('');
    }

    // ============================================================
    // MEMBER SUMMARY (ringkasan statistik per anggota)
    // ============================================================
    function renderMemberSummary(list) {
        var wrap = document.getElementById('memberSummaryWrap');
        var tbody = document.getElementById('memberSummaryBody');
        if (!wrap || !tbody) return;
        if (!list || !list.length) {
            wrap.style.display = 'none';
            return;
        }
        wrap.style.display = '';
        document.getElementById('memberSummaryCount').textContent = list.length;
        var html = '';
        list.forEach(function (m) {
            var active = memberFilter && memberFilter.toLowerCase() === m.marketing_member.toLowerCase();
            html += '<tr class="' + (active ? 'active' : '') + '" data-member="' + escapeHtml(m.marketing_member) + '">' +
                '<td class="member-name">👤 ' + escapeHtml(m.marketing_member) + '</td>' +
                '<td class="num total">' + m.total + '</td>' +
                '<td class="num">' + m.scheduled + '</td>' +
                '<td class="num">' + m.assigned + '</td>' +
                '<td class="num done">' + m.completed + '</td>' +
                '<td class="num result-ditemui">' + m.ditemui + '</td>' +
                '<td class="num result-prospek">' + m.prospek + '</td>' +
                '<td class="num result-gagal">' + m.gagal + '</td>' +
                '<td class="num">' + m.cancelled + '</td>' +
                '<td class="num">' + m.sesi1 + '</td>' +
                '<td class="num">' + m.sesi2 + '</td>' +
            '</tr>';
        });
        tbody.innerHTML = html;
    }

    // ============================================================
    // RENDER
    // ============================================================
    function renderAll(data) {
        var rows = (data && data.data) || [];
        var stats = (data && data.stats) || {};
        areaLookup = {};
        rows.forEach(function (r) { areaLookup[r.id] = r.area || 'Lainnya'; });

        document.getElementById('statTotal').textContent = stats.total || 0;
        document.getElementById('statScheduled').textContent = stats.scheduled || 0;
        document.getElementById('statAssigned').textContent = stats.assigned || 0;
        document.getElementById('statCompleted').textContent = stats.completed || 0;
        document.getElementById('statCancelled').textContent = stats.cancelled || 0;

        var scheduled = rows.filter(function (r) { return r.status === 'scheduled'; });
        var assigned = rows.filter(function (r) { return r.status === 'assigned'; });
        var completed = rows.filter(function (r) { return r.status === 'completed'; });

        document.getElementById('unassignedCount').textContent = scheduled.length;
        document.getElementById('assignedCount').textContent = assigned.length;
        document.getElementById('completedCount').textContent = completed.length;

        renderUnassigned(scheduled);
        renderAssigned(assigned);
        renderCompleted(completed);
    }

    function renderUnassigned(list) {
        var board = document.getElementById('unassignedBoard');
        if (!list.length) {
            board.innerHTML = '<div class="empty-state" style="grid-column:1/-1;">' +
                '<span class="big">🎉</span>Semua appointment sudah ditugaskan</div>';
            return;
        }
        var groups = { '1': [], '2': [] };
        list.forEach(function (r) { groups[r.sesi].push(r); });

        var html = '';
        ['1', '2'].forEach(function (sesi) {
            var items = groups[sesi];
            var sesiMeta = sesi === '1'
                ? { cls: 'sesi1', label: '🌅 Sesi 1', time: '08.30' }
                : { cls: 'sesi2', label: '🌆 Sesi 2', time: '14.30' };
            var suggest = suggestions[sesi] || '';
            html += '<div class="sesi-col">' +
                '<div class="sesi-col-head ' + sesiMeta.cls + '">' + sesiMeta.label + ' <small>' + sesiMeta.time + ' · ' + items.length + ' appt</small></div>' +
                '<div class="sesi-col-body">' +
                (suggest ? '<div class="tag-suggest">⭐ Saran sistem: ' + escapeHtml(suggest) + '</div>' : '');
            if (!items.length) {
                html += '<div class="empty-state">Tidak ada</div>';
            }
            items.forEach(function (r) {
                html += unassignedCard(r, suggest);
            });
            html += '</div></div>';
        });
        board.innerHTML = html;
    }

    function unassignedCard(r, suggest) {
        var suggestSelected = (r.driver_name) ? r.driver_name : (suggest || '');
        return '<div class="appt-card" id="appt-' + r.id + '">' +
            '<div class="appt-id">' + escapeHtml(r.display_id) + ' · ' + escapeHtml(r.team_name || 'Tanpa Tim') + '</div>' +
            '<div class="appt-nama">👤 ' + escapeHtml(r.nasabah_name) + '</div>' +
            '<div class="appt-alamat">📍 ' + escapeHtml(r.alamat) + '</div>' +
            '<div class="appt-meta">' +
                '<span class="badge badge-area">' + escapeHtml(r.area || 'Lainnya') + '</span>' +
                (r.nasabah_phone ? '<span class="badge" style="background:#f1f5f9;color:#334155;">📞 ' + escapeHtml(r.nasabah_phone) + '</span>' : '') +
                (r.marketing_member ? '<span class="badge badge-team">👤 ' + escapeHtml(r.marketing_member) + '</span>' : '') +
            '</div>' +
            '<div class="appt-actions" style="display:flex;gap:6px;">' +
                '<select class="form-control" id="sel-' + r.id + '" style="flex:1;">' + driverOptions(suggestSelected) + '</select>' +
                '<button class="btn btn-primary" onclick="window.__cdAssign(' + r.id + ')">Tugaskan</button>' +
                '<button class="btn btn-outline" onclick="window.__cdArea(' + r.id + ')" title="Atur area/wilayah manual">🌍</button>' +
                '<button class="btn btn-danger" onclick="window.__cdCancel(' + r.id + ')" title="Batalkan appointment">✕</button>' +
            '</div>' +
        '</div>';
    }

    function renderAssigned(list) {
        var board = document.getElementById('driverBoard');
        if (!list.length) {
            board.innerHTML = '<div class="empty-state">' +
                '<span class="big">🚗</span>Belum ada appointment yang ditugaskan ke driver</div>';
            return;
        }
        var groups = {};
        list.forEach(function (r) {
            (groups[r.driver_name] = groups[r.driver_name] || []).push(r);
        });
        var html = '';
        Object.keys(groups).sort().forEach(function (driver) {
            var items = groups[driver];
            var first = items[0] || {};
            html += '<div class="driver-block">' +
                '<div class="driver-head">' +
                    '<span class="driver-avatar">🚛</span>' +
                    '<span>' + escapeHtml(driver) + '</span>' +
                    '<span class="d-count">' + items.length + ' perjalanan</span>' +
                '</div>' +
                '<div class="driver-grid">';
            items.forEach(function (r) {
                var sesiMeta = r.sesi === '1' ? '🌅 08.30' : '🌆 14.30';
                html += '<div class="appt-card st-assigned">' +
                    '<div class="appt-id">' + escapeHtml(r.display_id) + '</div>' +
                    '<div class="appt-nama">👤 ' + escapeHtml(r.nasabah_name) + ' <span class="badge badge-sesi">' + sesiMeta + '</span></div>' +
                    '<div class="appt-alamat">📍 ' + escapeHtml(r.alamat) + '</div>' +
                    '<div class="appt-meta">' +
                        '<span class="badge badge-area">' + escapeHtml(r.area || 'Lainnya') + '</span>' +
                        (r.marketing_member ? '<span class="badge badge-team">👤 ' + escapeHtml(r.marketing_member) + '</span>' : '') +
                    '</div>' +
                    '<div class="appt-actions">' +
                        '<button class="btn btn-success" onclick="window.__cdComplete(' + r.id + ')">✅ Selesai</button>' +
                        '<button class="btn btn-warning" onclick="window.__cdReassign(' + r.id + ')">🔄 Ganti</button>' +
                        '<button class="btn btn-outline" onclick="window.__cdArea(' + r.id + ')" title="Atur area/wilayah manual">🌍</button>' +
                        '<button class="btn btn-outline" onclick="window.__cdUnassign(' + r.id + ')">↩️</button>' +
                        '<button class="btn btn-danger" onclick="window.__cdCancel(' + r.id + ')">✕</button>' +
                    '</div>' +
                '</div>';
            });
            html += '</div></div>';
        });
        board.innerHTML = html;
    }

    function renderCompleted(list) {
        var board = document.getElementById('completedBoard');
        if (!list.length) {
            board.innerHTML = '<div class="empty-state">' +
                '<span class="big">✅</span>Belum ada appointment yang selesai</div>';
            return;
        }
        var html = '<div class="completed-list">';
        list.forEach(function (r) {
            var sesiMeta = r.sesi === '1' ? '🌅 Sesi 1 (08.30)' : '🌆 Sesi 2 (14.30)';
            // Badge hasil kunjungan + alasan (dari driver / chief driver)
            var resultBadge = '';
            var resultNote = '';
            if (r.visit_result) {
                var rl = { ditemui: '😊 Ditemui', prospek: '🤝 Prospek', gagal: '❌ Gagal' }[r.visit_result];
                if (rl) {
                    resultBadge = '<span class="badge result-' + escapeHtml(r.visit_result) + '">' + rl + '</span>';
                    if (r.visit_note) {
                        resultNote = '<div class="completed-note">📝 ' + escapeHtml(r.visit_note) + '</div>';
                    }
                }
            }
            html += '<div class="completed-item">' +
                '<span class="completed-check">✅</span>' +
                '<div class="completed-body">' +
                    '<div class="n">' + escapeHtml(r.nasabah_name) + ' ' + resultBadge + '</div>' +
                    resultNote +
                    '<div class="meta">' + sesiMeta + ' · ' + escapeHtml(r.area || 'Lainnya') +
                        (r.driver_name ? ' · 🚗 ' + escapeHtml(r.driver_name) : '') + '</div>' +
                    '<div class="meta" style="color:#059669;">Terintegrasi dengan Log Perjalanan driver ✓</div>' +
                '</div>' +
            '</div>';
        });
        html += '</div>';
        board.innerHTML = html;
    }

    // ============================================================
    // ACTIONS
    // ============================================================
    window.__cdAssign = function (id) {
        var sel = document.getElementById('sel-' + id);
        var driver = sel ? sel.value : '';
        if (!driver) { toast('Pilih driver terlebih dahulu', 'err'); sel && sel.focus(); return; }
        api('/api/appointments/' + id + '/assign', { method: 'POST', body: { driver_name: driver } })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); loadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    window.__cdComplete = function (id) {
        if (!confirm('Tandai appointment ini SELESAI dikunjungi driver?')) return;
        api('/api/appointments/' + id + '/complete', { method: 'POST', body: {} })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); loadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    window.__cdUnassign = function (id) {
        if (!confirm('Batalkan penugasan driver? Appointment kembali ke daftar belum ditugaskan.')) return;
        api('/api/appointments/' + id + '/unassign', { method: 'POST', body: {} })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); loadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    window.__cdCancel = function (id) {
        var reason = prompt('Alasan pembatalan appointment ini?', 'Nasabah menunda / tidak bisa ditemui');
        if (reason === null) return;
        api('/api/appointments/' + id + '/cancel', { method: 'POST', body: { reason: reason || '' } })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); loadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    window.__cdArea = function (id) {
        var current = areaLookup[id] || 'Lainnya';
        var area = prompt('Atur area/wilayah manual untuk appointment ini:', current);
        if (area === null) return;
        area = area.trim();
        if (!area) { toast('Area tidak boleh kosong', 'err'); return; }
        api('/api/appointments/' + id, { method: 'PATCH', body: { area: area } })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ Area diperbarui: ' + area, 'ok'); loadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    var reassignId = null;
    window.__cdReassign = function (id) {
        reassignId = id;
        document.getElementById('reassignId').value = id;
        var display = document.getElementById('reassignDisplay');
        display.textContent = '#' + id;
        document.getElementById('reassignDriver').innerHTML = driverOptions('');
        document.getElementById('reassignNote').value = '';
        document.getElementById('reassignModal').style.display = 'flex';
    };

    function submitReassign() {
        if (!reassignId) return;
        var driver = document.getElementById('reassignDriver').value;
        if (!driver) { toast('Pilih driver baru', 'err'); return; }
        api('/api/appointments/' + reassignId + '/assign', {
            method: 'POST',
            body: { driver_name: driver, driver_note: document.getElementById('reassignNote').value.trim() }
        }).then(function (d) {
            if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); closeReassign(); loadAll(); }
            else toast('❌ ' + (d.msg || 'Gagal'), 'err');
        }).catch(function () { toast('❌ Error koneksi', 'err'); });
    }

    function closeReassign() {
        document.getElementById('reassignModal').style.display = 'none';
        reassignId = null;
    }

    window.__cdSubmitReassign = submitReassign;
    window.__cdCloseReassign = closeReassign;

    // ============================================================
    // NAV & EXPORT
    // ============================================================
    function shiftDate(n) {
        var d = new Date(currentDate + 'T00:00:00');
        d.setDate(d.getDate() + n);
        currentDate = d.toISOString().split('T')[0];
        document.getElementById('dateInput').value = currentDate;
        loadAll();
    }

    function goToday() {
        currentDate = new Date().toISOString().split('T')[0];
        document.getElementById('dateInput').value = currentDate;
        loadAll();
    }

    function onDateChange() {
        currentDate = document.getElementById('dateInput').value;
        loadAll();
    }

    function exportExcel() {
        window.location.href = '/api/appointments/export?date=' + currentDate +
            (memberFilter ? '&member=' + encodeURIComponent(memberFilter) : '');
    }

    // ============================================================
    // REALTIME
    // ============================================================
    function initSocket() {
        if (typeof io === 'undefined') return;
        var socket = io();
        socket.on('connect', function () {
            socket.emit('join_room', { room: 'appointments_board' });
        });
        socket.on('appointment_update', function (data) {
            if (data && data.action) {
                var msgs = {
                    created: '📋 Appointment baru masuk',
                    assigned: '🚗 ' + (data.driver || 'Driver') + ' ditugaskan',
                    unassigned: '↩️ Penugasan dibatalkan',
                    completed: '✅ Appointment selesai',
                    cancelled: '✕ Appointment dibatalkan'
                };
                toast(msgs[data.action] || 'Data berubah', 'ok');
            }
            clearTimeout(reloadTimer);
            reloadTimer = setTimeout(loadAll, 300);
        });
    }

    // ============================================================
    // INIT
    // ============================================================
    document.getElementById('reassignModal').addEventListener('click', function (e) { if (e.target === this) closeReassign(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeReassign(); });

    // Klik baris ringkasan anggota -> filter board
    document.getElementById('memberSummaryBody').addEventListener('click', function (e) {
        var tr = e.target.closest('tr[data-member]');
        if (tr) applyMemberFilter(tr.getAttribute('data-member'));
    });

    loadMembers();
    loadAll();
    initSocket();

    // Ekspos untuk inline onclick di template
    window.shiftDate = shiftDate;
    window.goToday = goToday;
    window.onDateChange = onDateChange;
    window.onMemberFilterInput = onMemberFilterInput;
    window.clearMemberFilter = clearMemberFilter;
    window.exportExcel = exportExcel;
})();
