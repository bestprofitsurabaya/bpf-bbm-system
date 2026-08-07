// ============================================================
// MARKETING HUB - Appointment Input
// ============================================================
(function () {
    'use strict';

    var USERNAME = document.body.dataset.username || '';
    var FULLNAME = document.body.dataset.fullname || '';
    var currentDate = document.getElementById('dateInput').value || new Date().toISOString().split('T')[0];
    var sesiFilter = '';
    var entryCounter = 0;

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

    // ============================================================
    // ENTRY FORM (multi-input)
    // ============================================================
    function entryTemplate() {
        entryCounter += 1;
        var div = document.createElement('div');
        div.className = 'appt-entry';
        div.innerHTML =
            '<div class="entry-head">' +
                '<span class="entry-num">Appointment #' + entryCounter + '</span>' +
                '<button type="button" class="entry-remove" title="Hapus entry">✕</button>' +
            '</div>' +
            '<div class="sesi-toggle">' +
                '<button type="button" class="sesi-btn" data-sesi="1">🌅 Sesi 1<small>08.30 Pagi</small></button>' +
                '<button type="button" class="sesi-btn" data-sesi="2">🌆 Sesi 2<small>14.30 Siang</small></button>' +
            '</div>' +
            '<div class="form-grid">' +
                '<div><label>Tanggal <span class="req">*</span></label><input type="date" class="form-control entry-date" value="' + currentDate + '"></div>' +
                '<div><label>No. HP Calon Nasabah</label><input type="tel" class="form-control entry-phone" placeholder="08xxxxxxxxxx" maxlength="30"></div>' +
                '<div class="full"><label>Nama Calon Nasabah <span class="req">*</span></label><input type="text" class="form-control entry-name" placeholder="Nama calon nasabah..."></div>' +
                '<div class="full"><label>Nama Marketing <span class="req">*</span></label><input type="text" class="form-control entry-member" list="memberList" placeholder="Nama anggota tim yang memprospek (ketik utk pilih saran)..."></div>' +
                '<div class="full"><label>Alamat Lengkap <span class="req">*</span></label>' +
                    '<textarea class="form-control entry-alamat" rows="2" placeholder="Ketik alamat, sistem akan mendeteksi area/wilayah otomatis..."></textarea>' +
                    '<span class="area-chip">📍 <span class="area-text"></span></span>' +
                '</div>' +
                '<div class="full"><label>Catatan</label><input type="text" class="form-control entry-notes" maxlength="500" placeholder="Opsional — contoh: nasabah lama, referral, dll"></div>' +
            '</div>';
        return div;
    }

    function renumberEntries() {
        var entries = document.querySelectorAll('#entryContainer .appt-entry');
        for (var i = 0; i < entries.length; i++) {
            entries[i].querySelector('.entry-num').textContent = 'Appointment #' + (i + 1);
        }
    }

    function addEntry() {
        var container = document.getElementById('entryContainer');
        var entry = entryTemplate();
        container.appendChild(entry);
        var first = entry.querySelector('input');
        if (first) first.focus();
        renumberEntries();
        entry.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function removeEntry(btn) {
        var entry = btn.closest('.appt-entry');
        var all = document.querySelectorAll('#entryContainer .appt-entry');
        if (all.length <= 1) {
            toast('Minimal 1 entry', 'err');
            return;
        }
        entry.remove();
        renumberEntries();
    }

    // Delegation: sesi toggle, remove, area detection
    document.getElementById('entryContainer').addEventListener('click', function (e) {
        var sesiBtn = e.target.closest('.sesi-btn');
        if (sesiBtn) {
            var wrap = sesiBtn.parentElement;
            wrap.querySelectorAll('.sesi-btn').forEach(function (b) { b.classList.remove('active'); });
            sesiBtn.classList.add('active');
            return;
        }
        if (e.target.classList.contains('entry-remove')) removeEntry(e.target);
    });

    var areaTimer = null;
    document.getElementById('entryContainer').addEventListener('input', function (e) {
        if (!e.target.classList.contains('entry-alamat')) return;
        var alamat = e.target.value;
        var chip = e.target.parentElement.querySelector('.area-chip');
        clearTimeout(areaTimer);
        if (!alamat.trim()) { chip.classList.remove('show'); return; }
        areaTimer = setTimeout(function () {
            fetch('/api/appointments/detect-area?alamat=' + encodeURIComponent(alamat))
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    chip.querySelector('.area-text').textContent = d.area;
                    chip.classList.add('show');
                })
                .catch(function () {});
        }, 350);
    });

    function validateEntry(entry) {
        var errs = [];
        if (!entry.querySelector('.entry-name').value.trim()) errs.push('nama nasabah');
        if (!entry.querySelector('.entry-member').value.trim()) errs.push('nama marketing');
        if (!entry.querySelector('.entry-alamat').value.trim()) errs.push('alamat');
        if (!entry.querySelector('.sesi-btn.active')) errs.push('sesi');
        if (!entry.querySelector('.entry-date').value) errs.push('tanggal');
        return errs;
    }

    function submitAppointments() {
        var entries = document.querySelectorAll('#entryContainer .appt-entry');
        var items = [];
        var hasError = false;
        entries.forEach(function (entry) {
            var errs = validateEntry(entry);
            if (errs.length) {
                entry.style.borderColor = '#dc2626';
                hasError = true;
                toast('Lengkapi: ' + errs.join(', '), 'err');
                return;
            }
            entry.style.borderColor = '';
            var sesiBtn = entry.querySelector('.sesi-btn.active');
            items.push({
                nasabah_name: entry.querySelector('.entry-name').value.trim(),
                marketing_member: entry.querySelector('.entry-member').value.trim(),
                nasabah_phone: entry.querySelector('.entry-phone').value.trim(),
                alamat: entry.querySelector('.entry-alamat').value.trim(),
                sesi: sesiBtn.dataset.sesi,
                appointment_date: entry.querySelector('.entry-date').value,
                notes: entry.querySelector('.entry-notes').value.trim()
            });
        });
        if (hasError) return;
        if (!items.length) { toast('Isi minimal 1 appointment', 'err'); return; }

        var btn = document.getElementById('submitApptBtn');
        btn.disabled = true; btn.textContent = '⏳ Menyimpan...';
        api('/api/appointments', { method: 'POST', body: { appointments: items } })
            .then(function (d) {
                if (d.status === 'success') {
                    toast('✅ ' + d.msg, 'ok');
                    if (d.errors && d.errors.length) {
                        toast('⚠️ ' + d.errors.length + ' entry gagal, cek kembali', 'err');
                    }
                    // Reset form: kosongkan nilai tapi jaga 1 entry
                    var container = document.getElementById('entryContainer');
                    container.innerHTML = '';
                    addEntry();
                    reloadAll();
                } else {
                    toast('❌ ' + (d.msg || 'Gagal menyimpan'), 'err');
                }
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); })
            .finally(function () { btn.disabled = false; btn.textContent = '📤 Simpan Appointment'; });
    }

    // ============================================================
    // LIST & STATS
    // ============================================================
    function statusBadge(status) {
        var map = {
            scheduled: ['badge-scheduled', '⏳ Menunggu Driver'],
            assigned: ['badge-assigned', '🚗 Driver Ditugaskan'],
            completed: ['badge-completed', '✅ Selesai'],
            cancelled: ['badge-cancelled', '✕ Dibatalkan']
        };
        var m = map[status] || map.scheduled;
        return '<span class="badge ' + m[0] + '">' + m[1] + '</span>';
    }

    function renderList(data) {
        var container = document.getElementById('listContainer');
        var rows = (data && data.data) || [];
        var stats = (data && data.stats) || {};

        document.getElementById('statTotal').textContent = stats.total || 0;
        document.getElementById('statSesi1').textContent = stats.sesi1 || 0;
        document.getElementById('statSesi2').textContent = stats.sesi2 || 0;
        document.getElementById('statScheduled').textContent = stats.scheduled || 0;
        document.getElementById('statAssigned').textContent = stats.assigned || 0;
        document.getElementById('statCompleted').textContent = stats.completed || 0;

        var filtered = rows;
        if (sesiFilter) filtered = rows.filter(function (r) { return r.sesi === sesiFilter; });

        if (!filtered.length) {
            container.innerHTML = '<div class="empty-state"><span class="big">📭</span>Tidak ada appointment untuk tanggal ini' + (sesiFilter ? ' pada sesi ini' : '') + '.<br>Gunakan form di atas untuk menambah.</div>';
            return;
        }

        var html = '';
        var groups = { '1': [], '2': [] };
        filtered.forEach(function (r) { (groups[r.sesi] = groups[r.sesi] || []).push(r); });

        ['1', '2'].forEach(function (sesi) {
            var list = groups[sesi] || [];
            if (!list.length) return;
            var sesiMeta = sesi === '1'
                ? { label: '🌅 Sesi 1', time: '08.30', cls: 'st-sesi1' }
                : { label: '🌆 Sesi 2', time: '14.30', cls: 'st-sesi2' };
            html += '<div class="sesi-group">' +
                '<div class="sesi-group-head">' + sesiMeta.label + ' · Pukul ' + sesiMeta.time + ' <span class="sesi-count">' + list.length + '</span></div>';
            list.forEach(function (r) {
                var actions = '';
                // Badge hasil kunjungan untuk appointment selesai (konversi marketing)
                var resultBadge = '';
                if (r.status === 'completed' && r.visit_result) {
                    var rl = { ditemui: '😊 Ditemui', prospek: '🤝 Prospek', gagal: '❌ Gagal' }[r.visit_result];
                    if (rl) resultBadge = '<span class="badge badge-result ' + escapeHtml(r.visit_result) + '">' + rl + '</span>';
                }
                if (r.status === 'scheduled') {
                    actions = '<button class="btn btn-outline btn-sm" onclick="window.__marketingEdit(' + r.id + ')">✏️ Edit</button>' +
                              '<button class="btn btn-danger btn-sm" onclick="window.__marketingCancel(' + r.id + ')">Batal</button>';
                }
                html += '<div class="appt-card ' + sesiMeta.cls + ' st-' + r.status + '">' +
                    '<div class="appt-time"><span class="t">' + sesiMeta.time + '</span>' + sesiMeta.label.split(' ')[1] + '</div>' +
                    '<div class="appt-body">' +
                        '<div class="appt-top">' +
                            '<span class="appt-name">' + escapeHtml(r.nasabah_name) + '</span>' +
                            statusBadge(r.status) +
                            '<span class="badge badge-area">📍 ' + escapeHtml(r.area || 'Lainnya') + '</span>' +
                            (r.team_name ? '<span class="tag-team badge">👥 ' + escapeHtml(r.team_name) + '</span>' : '') +
                        '</div>' +
                        '<div class="appt-alamat">📍 ' + escapeHtml(r.alamat) + '</div>' +
                        '<div class="appt-meta">' +
                            (r.marketing_member ? '<span class="appt-member">👤 Marketing: ' + escapeHtml(r.marketing_member) + '</span>' : '') +
                            (r.nasabah_phone ? '<span>📞 ' + escapeHtml(r.nasabah_phone) + '</span>' : '') +
                            '<span>🆔 ' + escapeHtml(r.display_id) + '</span>' +
                            (r.driver_name ? '<span class="appt-driver">🚗 ' + escapeHtml(r.driver_name) + '</span>' : '') +
                            (r.status === 'completed' ? '<span style="color:#059669;">Terintegrasi ke Log Perjalanan driver ✓</span>' : '') +
                            resultBadge +
                        '</div>' +
                        ((r.status === 'completed' && r.visit_note) ? '<div class="appt-meta">📝 ' + escapeHtml(r.visit_note) + '</div>' : '') +
                        (r.notes ? '<div class="appt-meta">📝 ' + escapeHtml(r.notes) + '</div>' : '') +
                    '</div>' +
                    '<div class="appt-actions">' + actions + '</div>' +
                '</div>';
            });
            html += '</div>';
        });
        container.innerHTML = html;
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function loadList() {
        var url = '/api/appointments?date=' + currentDate;
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(renderList)
            .catch(function () {
                document.getElementById('listContainer').innerHTML = '<div class="empty-state">Gagal memuat data</div>';
            });
    }

    function reloadAll() { loadList(); loadNotifications(); loadMembers(); }

    // ============================================================
    // MARKETING MEMBERS (nama anggota tim yang memprospek)
    // ============================================================
    function loadMembers() {
        fetch('/api/marketing/members')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                var members = (d && d.members) || [];
                var dl = document.getElementById('memberList');
                if (!dl) return;
                dl.innerHTML = members.map(function (m) {
                    return '<option value="' + escapeHtml(m) + '"></option>';
                }).join('');
            })
            .catch(function () {});
    }

    function shiftDate(n) {
        var d = new Date(currentDate + 'T00:00:00');
        d.setDate(d.getDate() + n);
        currentDate = d.toISOString().split('T')[0];
        document.getElementById('dateInput').value = currentDate;
        document.querySelectorAll('.entry-date').forEach(function (el) { el.value = currentDate; });
        reloadAll();
    }

    function goToday() {
        currentDate = new Date().toISOString().split('T')[0];
        document.getElementById('dateInput').value = currentDate;
        document.querySelectorAll('.entry-date').forEach(function (el) { el.value = currentDate; });
        reloadAll();
    }

    function setSesiFilter(chip) {
        sesiFilter = chip.dataset.sesi || '';
        document.querySelectorAll('.filter-chips .chip').forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');
        loadList();
    }

    // ============================================================
    // EDIT / CANCEL
    // ============================================================
    window.__marketingEdit = function (id) {
        fetch('/api/appointments?date=' + currentDate)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var row = null;
                (data.data || []).forEach(function (r) { if (r.id === id) row = r; });
                if (!row) { toast('Data tidak ditemukan', 'err'); return; }
                openEdit(row);
            })
            .catch(function () { toast('Error memuat data', 'err'); });
    };

    function openEdit(row) {
        document.getElementById('editId').value = row.id;
        document.getElementById('editDisplayId').textContent = row.display_id;
        document.getElementById('editName').value = row.nasabah_name;
        document.getElementById('editMember').value = row.marketing_member || '';
        document.getElementById('editPhone').value = row.nasabah_phone || '';
        document.getElementById('editAlamat').value = row.alamat;
        document.getElementById('editNotes').value = row.notes || '';
        document.getElementById('editSesiWrap').querySelectorAll('.sesi-btn').forEach(function (b) {
            b.classList.toggle('active', b.dataset.sesi === String(row.sesi));
        });
        document.getElementById('editModal').style.display = 'flex';
    }

    function closeEdit() { document.getElementById('editModal').style.display = 'none'; }

    function saveEdit() {
        var id = document.getElementById('editId').value;
        var payload = {
            nasabah_name: document.getElementById('editName').value.trim(),
            marketing_member: document.getElementById('editMember').value.trim(),
            nasabah_phone: document.getElementById('editPhone').value.trim(),
            alamat: document.getElementById('editAlamat').value.trim(),
            notes: document.getElementById('editNotes').value.trim()
        };
        var sesiBtn = document.getElementById('editSesiWrap').querySelector('.sesi-btn.active');
        if (sesiBtn) payload.sesi = sesiBtn.dataset.sesi;
        if (!payload.nasabah_name || !payload.alamat || !payload.marketing_member) {
            toast('Nama nasabah, nama marketing, dan alamat wajib', 'err'); return;
        }
        api('/api/appointments/' + id, { method: 'PATCH', body: payload })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); closeEdit(); reloadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    }

    window.__marketingCancel = function (id) {
        if (!confirm('Batalkan appointment ini?')) return;
        api('/api/appointments/' + id + '/cancel', { method: 'POST', body: { reason: 'Dibatalkan oleh marketing' } })
            .then(function (d) {
                if (d.status === 'success') { toast('✅ ' + d.msg, 'ok'); reloadAll(); }
                else toast('❌ ' + (d.msg || 'Gagal'), 'err');
            })
            .catch(function () { toast('❌ Error koneksi', 'err'); });
    };

    window.__marketingCloseEdit = closeEdit;
    window.__marketingSaveEdit = saveEdit;

    // ============================================================
    // NOTIFICATIONS
    // ============================================================
    function loadNotifications() {
        fetch('/api/appointments/notifications')
            .then(function (r) { return r.json(); })
            .then(function (rows) {
                if (!Array.isArray(rows)) return;
                var unread = rows.filter(function (n) { return !n.is_read; }).length;
                var badge = document.getElementById('notifBadge');
                if (unread > 0) { badge.textContent = unread; badge.style.display = 'flex'; }
                else badge.style.display = 'none';
                renderNotifications(rows);
            })
            .catch(function () {});
    }

    function renderNotifications(rows) {
        var list = document.getElementById('notifList');
        if (!rows.length) {
            list.innerHTML = '<p class="notif-empty">Belum ada notifikasi</p>';
            return;
        }
        var html = '';
        rows.slice(0, 30).forEach(function (n) {
            html += '<div class="notif-item' + (n.is_read ? '' : ' unread') + '">' +
                '<strong>' + escapeHtml(n.message) + '</strong>' +
                '<span class="ni-time">' + formatDate(n.created_at) + '</span></div>';
        });
        list.innerHTML = html;
    }

    function formatDate(s) {
        try {
            var d = new Date(s);
            return d.toLocaleString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
        } catch (e) { return s; }
    }

    function toggleNotifPanel() {
        var panel = document.getElementById('notifPanel');
        var overlay = document.getElementById('notifOverlay');
        var show = !panel.classList.contains('show');
        panel.classList.toggle('show', show);
        overlay.style.display = show ? 'block' : 'none';
        if (show) {
            api('/api/appointments/notifications/read', { method: 'POST', body: {} })
                .then(function () { loadNotifications(); });
        }
    }
    function closeNotifPanel() {
        document.getElementById('notifPanel').classList.remove('show');
        document.getElementById('notifOverlay').style.display = 'none';
    }

    // ============================================================
    // REALTIME
    // ============================================================
    function initSocket() {
        if (typeof io === 'undefined') return;
        var socket = io();
        socket.on('connect', function () {
            if (USERNAME) socket.emit('join_room', { room: 'marketing_' + USERNAME.toLowerCase() });
        });
        socket.on('appointment_update', function (data) {
            if (data && data.action === 'assigned') {
                toast('🚗 Driver ' + (data.driver || '') + ' ditugaskan ke ' + (data.display_id || 'appointment Anda'), 'ok');
            } else if (data && data.action === 'completed') {
                toast('✅ ' + (data.display_id || 'Appointment') + ' selesai dikunjungi', 'ok');
            } else if (data && data.action === 'unassigned') {
                toast('⚠️ Penugasan ' + (data.display_id || '') + ' dibatalkan', 'err');
            }
            reloadAll();
        });
    }

    // ============================================================
    // INIT
    // ============================================================
    document.getElementById('editModal').addEventListener('click', function (e) { if (e.target === this) closeEdit(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeEdit(); closeNotifPanel(); } });

    addEntry();
    reloadAll();
    initSocket();

    // Ekspos untuk inline onclick di template
    window.addEntry = addEntry;
    window.submitAppointments = submitAppointments;
    window.setSesiFilter = setSesiFilter;
    window.shiftDate = shiftDate;
    window.goToday = goToday;
    window.toggleNotifPanel = toggleNotifPanel;
    window.closeNotifPanel = closeNotifPanel;
})();
