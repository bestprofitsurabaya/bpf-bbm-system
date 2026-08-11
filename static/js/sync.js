let syncInProgress = false;

function updateStatus() {
    let bar = document.getElementById('statusBar');
    let txt = document.getElementById('statusText');
    if (navigator.onLine) {
        bar.className = 'status-bar online';
        txt.textContent = '🟢 Online';
    } else {
        bar.className = 'status-bar offline';
        txt.textContent = '🟡 Offline - Data tersimpan lokal';
    }
    updateBadge();
}

async function updateBadge() {
    let fuel = await countQueue('fuel_queue');
    let trip = await countQueue('trip_queue');
    let lpj = await countQueue('lpj_queue');
    let total = fuel + trip + lpj;
    let badge = document.getElementById('queueBadge');
    badge.textContent = total;
    badge.className = total > 0 ? 'queue-count show' : 'queue-count';
}

async function syncAll() {
    if (!navigator.onLine || !db || syncInProgress) return;
    syncInProgress = true;
    try {
        // 1) Laporan BBM offline → POST /driver
        let fuelItems = await getAllFromQueue('fuel_queue');
        for (let item of fuelItems) {
            try {
                let fd = new FormData();
                for (let k in item.data) fd.append(k, item.data[k]);
                fd.append('gps_lat', item.data.gps_lat || '');
                fd.append('gps_lon', item.data.gps_lon || '');
                fd.append('gps_address', item.data.gps_address || '');
                let r = await fetch('/driver', { method:'POST', body:fd, headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'} });
                let result = await r.json();
                if (r.ok && result.status === 'success') await deleteFromQueue('fuel_queue', item.id);
            } catch(e) {}
        }

        // 2) LPJ kasbon offline → POST /api/cash/submit-lpj/<cashId>
        let lpjItems = await getAllFromQueue('lpj_queue');
        for (let item of lpjItems) {
            try {
                if (!item.cashId) continue;
                let fd = new FormData();
                for (let k in item.data) fd.append(k, item.data[k]);
                let r = await fetch('/api/cash/submit-lpj/' + item.cashId, { method:'POST', body:fd, headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'} });
                let result = await r.json();
                if (r.ok && result.status === 'success') await deleteFromQueue('lpj_queue', item.id);
            } catch(e) {}
        }

        // 3) Log perjalanan offline → POST /submit-trip
        let tripItems = await getAllFromQueue('trip_queue');
        for (let item of tripItems) {
            try {
                let fd = new FormData();
                for (let k in item.data) fd.append(k, item.data[k]);
                let r = await fetch('/submit-trip', { method:'POST', body:fd, headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'} });
                let result = await r.json();
                if (r.ok && result.status === 'success') await deleteFromQueue('trip_queue', item.id);
            } catch(e) {}
        }
    } finally {
        syncInProgress = false;
        updateBadge();
    }
}

function refreshMasterCache() {
    if (!navigator.onLine) return;
    Promise.all([
        fetch('/api/drivers').then(r => r.json()),
        fetch('/api/assignments/active').then(r => r.json()),
        fetch('/api/vehicles/with-nopol').then(r => r.json())
    ]).then(([drivers, assignments, vehicles]) => {
        cacheMasterData(CACHE_KEY_DRIVERS, drivers);
        cacheMasterData(CACHE_KEY_VEHICLES, vehicles);
        cacheMasterData(CACHE_KEY_ASSIGNMENTS, assignments);
    }).catch(() => {});
}
