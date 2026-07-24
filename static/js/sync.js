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
    let total = fuel + trip;
    let badge = document.getElementById('queueBadge');
    badge.textContent = total;
    badge.className = total > 0 ? 'queue-count show' : 'queue-count';
}

async function syncAll() {
    if (!navigator.onLine || !db || syncInProgress) return;
    syncInProgress = true;
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
    updateBadge();
    syncInProgress = false;
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
