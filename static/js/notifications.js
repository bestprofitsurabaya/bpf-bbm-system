/* ============================================================ */
/* BPF FLEET SYSTEM - Driver Notifications (in-app real-time)    */
/* ============================================================ */
(function() {
    'use strict';

    var activeDriver = '';
    var socket = null;
    var notifItems = [];

    var ICONS = {
        claim:      { approved: '✅', paid: '💸', archived: '📦', rejected: '⛔' },
        cash:       { approved: '✅', paid: '💰', handover: '🤝', rejected: '⛔', cancelled: '↩️', completed: '🎉', lpj_rejected: '📋', reset: '🔄' },
        assignment: { assigned: '🚛', swapped: '🔄', released: '🚛' }
    };

    /* -------------------------------------------------------- */
    /* STYLES (injected so driver.html stays untouched)          */
    /* -------------------------------------------------------- */
    function injectStyles() {
        var css =
            '.notif-bell{position:relative;cursor:pointer;font-size:16px;padding:2px;line-height:1;}' +
            '.notif-badge{position:absolute;top:-5px;right:-9px;background:#dc2626;color:#fff;font-size:9px;font-weight:700;min-width:16px;height:16px;line-height:16px;text-align:center;border-radius:10px;padding:0 3px;}' +
            '.notif-backdrop{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,.45);z-index:9000;}' +
            '.notif-backdrop.show{display:block;}' +
            '.notif-panel{position:fixed;top:0;right:0;bottom:0;width:min(340px,88vw);background:#fff;z-index:9001;transform:translateX(105%);transition:transform .28s cubic-bezier(.4,0,.2,1);box-shadow:-6px 0 24px rgba(15,23,42,.18);display:flex;flex-direction:column;border-radius:16px 0 0 16px;}' +
            '.notif-panel.open{transform:translateX(0);}' +
            '.notif-panel-header{display:flex;align-items:center;gap:8px;padding:14px 16px;border-bottom:1px solid #e2e8f0;font-weight:700;font-size:13px;color:#0f172a;}' +
            '.notif-panel-header .notif-count{font-size:10px;background:#eff6ff;color:#2563eb;padding:2px 8px;border-radius:10px;}' +
            '.notif-close{margin-left:auto;background:none;border:none;font-size:16px;cursor:pointer;color:#64748b;padding:2px 6px;}' +
            '.notif-list{flex:1;overflow-y:auto;padding:8px 10px;}' +
            '.notif-item{display:flex;gap:10px;padding:10px;border-radius:10px;margin-bottom:6px;background:#f8fafc;border:1px solid #e2e8f0;}' +
            '.notif-item.unread{background:#eff6ff;border-color:#bfdbfe;}' +
            '.notif-item-icon{font-size:18px;flex-shrink:0;}' +
            '.notif-item-msg{font-size:12px;color:#1e293b;line-height:1.4;}' +
            '.notif-item-time{font-size:10px;color:#94a3b8;margin-top:2px;}' +
            '.notif-empty{text-align:center;color:#94a3b8;font-size:12px;padding:30px 10px;}' +
            '.notif-toast{position:fixed;left:50%;transform:translateX(-50%) translateY(24px);background:#1e293b;color:#fff;padding:10px 16px;border-radius:12px;font-size:12px;font-weight:600;z-index:9999;opacity:0;transition:all .3s ease;max-width:90%;text-align:center;box-shadow:0 8px 24px rgba(15,23,42,.3);pointer-events:none;}' +
            '.notif-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}' +
            'body.dark .notif-panel{background:#1e293b;}' +
            'body.dark .notif-panel-header{color:#e2e8f0;border-color:#334155;}' +
            'body.dark .notif-item{background:#0f172a;border-color:#334155;}' +
            'body.dark .notif-item-msg{color:#e2e8f0;}' +
            'body.dark .notif-item.unread{background:#1e3a5f;border-color:#2563eb;}' +
            'body.dark .notif-toast{background:#334155;}' +
            'body.dark .notif-close{color:#94a3b8;}' +
            '.rt-status{font-size:11px;line-height:1;cursor:default;margin-right:2px;}' +
            '.rt-status.off{animation:rtblink 1.3s infinite;}' +
            '@keyframes rtblink{0%,100%{opacity:1}50%{opacity:.3}}';
        var style = document.createElement('style');
        style.id = 'notifStyles';
        style.textContent = css;
        document.head.appendChild(style);
    }

    /* -------------------------------------------------------- */
    /* DRIVER IDENTITY                                          */
    /* -------------------------------------------------------- */
    function getSelectedDriver() {
        var ids = ['driver_name', 'kasbon_driver', 'trip_driver'];
        for (var i = 0; i < ids.length; i++) {
            var el = document.getElementById(ids[i]);
            if (el && el.value) return el.value.trim().toUpperCase();
        }
        return '';
    }

    function getActiveDriver() {
        return getSelectedDriver() || (localStorage.getItem('lastDriver') || '').trim().toUpperCase();
    }

    function watchDriverChanges() {
        document.addEventListener('change', function(e) {
            var t = e.target;
            if (t && (t.id === 'driver_name' || t.id === 'kasbon_driver' || t.id === 'trip_driver')) {
                var d = (t.value || '').trim().toUpperCase();
                if (d) localStorage.setItem('lastDriver', d);
                activeDriver = d;
                joinRoom();
                loadNotifications();
            }
        });
    }

    /* -------------------------------------------------------- */
    /* SOCKETIO                                                 */
    /* -------------------------------------------------------- */
    function setRtStatus(state) {
        var el = document.getElementById('rtStatus');
        if (!el) return;
        if (state === 'on') {
            el.textContent = '⚡';
            el.className = 'rt-status on';
            el.title = 'Notifikasi real-time: terhubung';
        } else {
            el.textContent = '🔴';
            el.className = 'rt-status off';
            el.title = 'Notifikasi real-time: terputus — mencoba menyambung otomatis…';
        }
    }

    function connectSocket() {
        if (typeof io === 'undefined') { setRtStatus('off'); return; }
        try {
            socket = io({
                reconnection: true,
                reconnectionAttempts: Infinity,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 8000,
                randomizationFactor: 0.3,
                timeout: 10000
            });
            socket.on('connect', function() {
                setRtStatus('on');
                joinRoom();
            });
            socket.on('disconnect', function() { setRtStatus('off'); });
            socket.on('connect_error', function() { setRtStatus('off'); });
            socket.on('driver_notification', function(d) {
                if (!d || !d.driver_name) return;
                if (activeDriver && d.driver_name !== activeDriver) return;
                onNewNotification(d);
                if (window.__onDriverNotif) window.__onDriverNotif(d);
            });
        } catch (e) { socket = null; setRtStatus('off'); }
    }

    function joinRoom() {
        if (!socket || !socket.connected) return;
        if (activeDriver) socket.emit('join_driver', { name: activeDriver });
    }

    /* -------------------------------------------------------- */
    /* RENDERING                                                */
    /* -------------------------------------------------------- */
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function(c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function iconFor(n) {
        try { return (ICONS[n.type] || {})[n.action] || '🔔'; } catch (e) { return '🔔'; }
    }

    function timeAgo(ts) {
        if (!ts) return '';
        var d = new Date(String(ts).replace(' ', 'T'));
        if (isNaN(d.getTime())) return '';
        var diff = (Date.now() - d.getTime()) / 1000;
        if (diff < 60) return 'baru saja';
        if (diff < 3600) return Math.floor(diff / 60) + ' mnt lalu';
        if (diff < 86400) return Math.floor(diff / 3600) + ' jam lalu';
        return d.toLocaleDateString('id-ID');
    }

    function renderList() {
        var list = document.getElementById('notifList');
        if (!list) return;
        if (!notifItems.length) { list.innerHTML = '<p class="notif-empty">Belum ada notifikasi</p>'; return; }
        var html = '';
        for (var i = 0; i < notifItems.length; i++) {
            var n = notifItems[i];
            html += '<div class="notif-item' + (n.is_read ? '' : ' unread') + '">' +
                '<span class="notif-item-icon">' + iconFor(n) + '</span>' +
                '<div class="notif-item-body"><div class="notif-item-msg">' + escapeHtml(n.message || '') + '</div>' +
                '<div class="notif-item-time">' + timeAgo(n.created_at) + '</div></div></div>';
        }
        list.innerHTML = html;
        var countEl = document.getElementById('notifPanelCount');
        if (countEl) countEl.textContent = notifItems.length ? notifItems.length + ' notifikasi' : '';
    }

    function setBadge(n) {
        var b = document.getElementById('notifBadge');
        if (!b) return;
        b.textContent = n > 99 ? '99+' : n;
        b.style.display = n > 0 ? 'block' : 'none';
    }

    function panelOpen() {
        var p = document.getElementById('notifPanel');
        return p && p.classList.contains('open');
    }

    /* -------------------------------------------------------- */
    /* DATA                                                     */
    /* -------------------------------------------------------- */
    function loadNotifications() {
        if (!activeDriver) { notifItems = []; renderList(); setBadge(0); return; }
        if (typeof navigator !== 'undefined' && navigator.onLine === false) return;
        fetch('/api/notifications?driver=' + encodeURIComponent(activeDriver))
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d && d.error) return;
                notifItems = (d && d.notifications) || [];
                if (!panelOpen()) setBadge((d && d.unread) || 0);
                renderList();
            })
            .catch(function() {});
    }

    function markAllRead() {
        if (!activeDriver) return;
        fetch('/api/notifications/read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ driver: activeDriver })
        }).catch(function() {});
    }

    function onNewNotification(d) {
        var open = panelOpen();
        d.is_read = open ? 1 : 0;
        notifItems.unshift(d);
        if (notifItems.length > 30) notifItems.pop();
        renderList();
        if (!open) {
            var unread = 0;
            for (var i = 0; i < notifItems.length; i++) if (!notifItems[i].is_read) unread++;
            setBadge(unread);
        }
        showNotifToast('🔔 ' + (d.message || 'Notifikasi baru'));
    }

    function showNotifToast(msg) {
        var t = document.createElement('div');
        t.className = 'notif-toast';
        t.textContent = msg;
        document.body.appendChild(t);
        requestAnimationFrame(function() { t.classList.add('show'); });
        setTimeout(function() {
            t.classList.remove('show');
            setTimeout(function() { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
        }, 4500);
    }

    /* -------------------------------------------------------- */
    /* PANEL TOGGLE                                             */
    /* -------------------------------------------------------- */
    window.toggleNotifPanel = function() {
        var p = document.getElementById('notifPanel');
        if (!p) return;
        if (p.classList.contains('open')) { closeNotifPanel(); return; }
        p.classList.add('open');
        var bd = document.getElementById('notifBackdrop');
        if (bd) bd.classList.add('show');
        setBadge(0);
        markAllRead();
        loadNotifications();
    };

    window.closeNotifPanel = function() {
        var p = document.getElementById('notifPanel');
        if (p) p.classList.remove('open');
        var bd = document.getElementById('notifBackdrop');
        if (bd) bd.classList.remove('show');
    };

    /* -------------------------------------------------------- */
    /* INIT                                                     */
    /* -------------------------------------------------------- */
    function init() {
        injectStyles();
        activeDriver = getActiveDriver();
        watchDriverChanges();
        connectSocket();
        loadNotifications();
        window.addEventListener('focus', function() { loadNotifications(); });
        window.addEventListener('online', function() { loadNotifications(); });
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) loadNotifications();
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
