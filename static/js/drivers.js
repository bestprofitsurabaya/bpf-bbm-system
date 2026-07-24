async function loadDrivers() {
    if (navigator.onLine) {
        try {
            let [drivers, assignments, vehicles] = await Promise.all([
                fetch('/api/drivers').then(r => r.json()),
                fetch('/api/assignments/active').then(r => r.json()),
                fetch('/api/vehicles/with-nopol').then(r => r.json())
            ]);
            cacheMasterData(CACHE_KEY_DRIVERS, drivers);
            cacheMasterData(CACHE_KEY_VEHICLES, vehicles);
            cacheMasterData(CACHE_KEY_ASSIGNMENTS, assignments);
            populateDropdowns(drivers, assignments, vehicles);
            return;
        } catch(e) {}
    }
    let drivers = getCachedMasterData(CACHE_KEY_DRIVERS);
    let assignments = getCachedMasterData(CACHE_KEY_ASSIGNMENTS) || [];
    let vehicles = getCachedMasterData(CACHE_KEY_VEHICLES) || [];
    if (drivers && drivers.length > 0) {
        populateDropdowns(drivers, assignments, vehicles);
    }
}

function populateDropdowns(drivers, assignments, vehicles) {
    [document.getElementById('driver_name'), document.getElementById('trip_driver')].forEach(function(sel) {
        if (!sel) return;
        while (sel.options.length > 1) sel.remove(1);
        drivers.forEach(function(drv) {
            if (!drv.name || !drv.is_active) return;
            var assign = null;
            for (var i = 0; i < assignments.length; i++) {
                if (assignments[i].driver_name === drv.name) { assign = assignments[i]; break; }
            }
            var o = document.createElement('option');
            o.value = drv.name;
            o.textContent = drv.name;
            o.dataset.nopol = assign ? assign.nopol : (drv.nopol || '');
            o.dataset.vehicle = assign ? assign.vehicle_type : (drv.vehicle_type || 'AVANZA');
            o.dataset.bbm = assign ? assign.bbm_type : (drv.bbm_type || 'PERTALITE');
            sel.appendChild(o);
        });
    });
}
