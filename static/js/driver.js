
// ============================================================
// INDEXEDDB SETUP
// ============================================================

// ============================================================
// CONNECTION STATUS
// ============================================================


// ============================================================
// SUBMIT (Online/Offline)
// ============================================================


    // ============================================================
    // WATERMARK ENGINE
    // ============================================================
    var watermarkedBlobs = {}; // Simpan hasil watermark per foto

    function getGPSCoordinates() {
        return new Promise(function(resolve) {
            // Prioritaskan alamat administratif dari GPS box
            if (gpsData && gpsData.addr) {
                resolve(gpsData.addr);
                return;
            }

            // Coba dari hidden input
            var addrEl = document.getElementById('gps_address');
            if (addrEl && addrEl.value) {
                resolve(addrEl.value);
                return;
            }

            // Fallback ke koordinat
            if (gpsData && gpsData.lat && gpsData.lon) {
                // Coba reverse geocode cepat
                fetch('https://nominatim.openstreetmap.org/reverse?lat='+gpsData.lat+'&lon='+gpsData.lon+'&format=json&zoom=18&accept-language=id',
                    { headers: { 'User-Agent': 'BPF-BBM/1.0' } })
                    .then(function(r) { return r.json(); })
                    .then(function(d) {
                        if (d && d.display_name) {
                            gpsData.addr = d.display_name;
                            resolve(d.display_name);
                        } else {
                            resolve(gpsData.lat.toFixed(5) + ', ' + gpsData.lon.toFixed(5));
                        }
                    })
                    .catch(function() {
                        resolve(gpsData.lat.toFixed(5) + ', ' + gpsData.lon.toFixed(5));
                    });
                return;
            }

            if (!navigator.geolocation) { resolve('GPS Tidak Didukung'); return; }
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    fetch('https://nominatim.openstreetmap.org/reverse?lat='+pos.coords.latitude+'&lon='+pos.coords.longitude+'&format=json&zoom=18&accept-language=id',
                        { headers: { 'User-Agent': 'BPF-BBM/1.0' } })
                        .then(function(r) { return r.json(); })
                        .then(function(d) {
                            if (d && d.display_name) resolve(d.display_name);
                            else resolve(pos.coords.latitude.toFixed(5) + ', ' + pos.coords.longitude.toFixed(5));
                        });
                },
                function() { resolve('GPS Tidak Aktif'); },
                { enableHighAccuracy: true, timeout: 5000 }
            );
        });
    }

    async function applyWatermarkToPhoto(fileInputId) {
        var input = document.getElementById(fileInputId);
        if (!input || !input.files || !input.files[0]) return null;

        var file = input.files[0];
        if (!file.type.startsWith('image/')) return null;

        // Update badge
        var badge = document.getElementById('wm_' + fileInputId);
        if (badge) { badge.textContent = '⏳ Memproses...'; badge.className = 'wm-badge processing'; }

        try {
            var gpsText = await getGPSCoordinates();
            var now = new Date();
            var timeText = now.toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' });

            var img = new Image();
            var blobUrl = URL.createObjectURL(file);

            return new Promise(function(resolve) {
                img.onload = function() {
                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    var fontSize = Math.max(16, Math.floor(canvas.width / 35));
                    var padding = 20;
                    var lineH = fontSize * 1.5;
                    var barH = lineH * 3 + padding * 2;

                    // Background bar
                    ctx.fillStyle = 'rgba(0,0,0,0.6)';
                    ctx.fillRect(0, canvas.height - barH, canvas.width, barH);

                    // Text
                    ctx.fillStyle = '#FFD700';
                    ctx.font = 'bold ' + fontSize + 'px Inter, Arial';
                    ctx.fillText('PT BESTPROFIT FUTURES SBY', padding, canvas.height - barH + lineH);

                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = (fontSize * 0.8) + 'px Inter, Arial';
                    ctx.fillText('📅 ' + timeText, padding, canvas.height - barH + lineH * 2);
                    ctx.fillText('📍 ' + gpsText, padding, canvas.height - barH + lineH * 3);

                    canvas.toBlob(function(blob) {
                        URL.revokeObjectURL(blobUrl);
                        watermarkedBlobs[fileInputId] = blob;

                        // Update preview dengan watermark
                        var previewImg = document.getElementById('img_' + fileInputId);
                        if (previewImg) { previewImg.src = URL.createObjectURL(blob); }

                        // Update badge
                        if (badge) { badge.textContent = '✅ Watermarked'; badge.className = 'wm-badge done'; }

                        resolve(blob);
                    }, 'image/jpeg', 0.85);
                };
                img.src = blobUrl;
            });
        } catch(e) {
            console.log('Watermark error:', e);
            if (badge) { badge.textContent = '⚠ Gagal'; badge.className = 'wm-badge error'; }
            return null;
        }
    }

    // Auto-watermark saat foto dipilih
    document.addEventListener('change', function(e) {
        if (!e.target.classList.contains('form-control-file') || !e.target.files[0]) return;
        var id = e.target.id;
        var f = e.target.files[0];
        if (!f.type.startsWith('image/')) { e.target.value = ''; return; }

        // Tampilkan preview dulu
        var reader = new FileReader();
        reader.onload = function(ev) {
            var img = document.getElementById('img_' + id);
            if (img) img.src = ev.target.result;
            var prev = document.getElementById('prev_' + id);
            if (prev) prev.classList.remove('hidden');
        };
        reader.readAsDataURL(f);

        // Apply watermark
        applyWatermarkToPhoto(id);
    });

    async function submitForm(form, store, endpoint, successMsg) {
    let fd = new FormData(form);
    var lpjCashId = window._activeLPJCashId;
    if (lpjCashId) { fd.append('cash_request_id', lpjCashId); window._activeLPJCashId = null; document.getElementById('bbmBtn').textContent = '📤 Kirim Laporan BBM'; document.getElementById('nominal').style.background = ''; }

    if (navigator.onLine) {
        let btn = form.querySelector('.btn-submit');
        let orig = btn.textContent;
        btn.textContent = '⏳...'; btn.disabled = true;
        try {
            // Replace file inputs with watermarked blobs
            let wm_fd = new FormData();
            for (let [k, v] of fd.entries()) {
                if (v instanceof File && watermarkedBlobs[k]) {
                    wm_fd.append(k, watermarkedBlobs[k], v.name);
                } else {
                    wm_fd.append(k, v);
                }
            }
            // Gunakan endpoint LPJ jika ini dari Kasbon
            let finalEndpoint = endpoint;
            if (lpjCashId && store === 'fuel_queue') {
                finalEndpoint = '/api/cash/submit-lpj/' + lpjCashId;
            }
            let r = await fetch(finalEndpoint, { method:'POST', body:wm_fd, headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'} });
            let result = await r.json();
            if (r.ok && result.status === 'success') {
                showModal(successMsg, result.transaction_id || result.trip_id);
                // Reset LPJ state
                if (lpjCashId) {
                    window._activeLPJCashId = null;
                    document.getElementById('bbmBtn').textContent = '📤 Kirim Laporan BBM';
                    document.getElementById('nominal').style.background = '';
                }
                // Simpan data offline sebelum clear
                clearSavedFormData(store);
                form.reset();
                if (store === 'fuel_queue') {
                    document.getElementById('jumlah_appointment').value = '0';
                    document.querySelectorAll('[id^="prev_"]').forEach(el => el.classList.add('hidden'));
                }
                if (store === 'trip_queue') {
                    document.getElementById('tripRows').innerHTML = '';

addTripRow();
                }
            } else {
                showToast('❌ ' + (result.message || 'Gagal'), 'error');
            }
        } catch(e) {
            showToast('❌ Error koneksi', 'error');
        } finally {
            btn.textContent = orig; btn.disabled = false;
        }
    } else {
        // Save form data dulu (jaga-jaga)
        saveFormData(store);
        let data = {};
        for (let [k, v] of fd.entries()) data[k] = v;
        data.gps_lat = document.getElementById('gps_lat').value;
        data.gps_lon = document.getElementById('gps_lon').value;
        data.gps_address = document.getElementById('gps_address').value;
        if (lpjCashId) {
            await saveToQueue('lpj_queue', { cashId: window._activeLPJCashId, data: data, timestamp: new Date().toISOString() });
            console.log('[LPJ] Queued offline: cashId=' + window._activeLPJCashId);
            window._activeLPJCashId = null;
            document.getElementById('bbmBtn').textContent = '📤 Kirim Laporan BBM';
            document.getElementById('nominal').style.background = '';
        } else {
            await saveToQueue(store, { data, timestamp: new Date().toISOString() });
        }
        form.reset();
        if (store === 'fuel_queue') {
            document.getElementById('jumlah_appointment').value = '0';
            document.querySelectorAll('[id^="prev_"]').forEach(el => el.classList.add('hidden'));
        }
        if (store === 'trip_queue') {
            document.getElementById('tripRows').innerHTML = '';

addTripRow();
        }
        document.getElementById('trip_date').value = new Date().toISOString().split('T')[0];
        showToast('⚠️ Offline. Data disimpan lokal!', 'warning');
        updateBadge();
    }
}

// ============================================================
// BOTTOM NAV
// ============================================================
document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('page-' + this.dataset.page).classList.add('active');
    });
});

// ============================================================
// GPS
// ============================================================
// GPS state
var gpsData = { lat: null, lon: null, addr: '', spbu: '' };


    // ============================================================
    // ASSIGNMENT CHECK (serah terima kendaraan)
    // ============================================================
    var pendingAssignment = null;

    function checkPendingAssignment() {
        // Cek assignment pending untuk driver yang sedang dipilih
        var box = document.getElementById('assignNotif');
        if (!box) return;
        var sel = document.getElementById('driver_name');
        var driverName = ((sel && sel.value) || '').trim().toUpperCase();
        if (!driverName) { box.classList.remove('show'); pendingAssignment = null; return; }
        fetch('/api/assignments/pending')
            .then(function(r) { return r.json(); })
            .then(function(list) {
                if (!Array.isArray(list)) return;
                var mine = null;
                for (var i = 0; i < list.length; i++) {
                    if (String(list[i].driver_name || '').trim().toUpperCase() === driverName) {
                        mine = list[i]; break;
                    }
                }
                if (mine) {
                    pendingAssignment = mine;
                    var text = document.getElementById('assignNotifText');
                    if (text) {
                        text.textContent = 'Kendaraan ' + (mine.nopol || '-') + ' (' + (mine.vehicle_type || '-') + ') menunggu konfirmasi serah terima Anda.';
                    }
                    box.classList.add('show');
                } else {
                    box.classList.remove('show');
                    pendingAssignment = null;
                }
            })
            .catch(function() {});
    }

    function confirmAssignment() {
        var box = document.getElementById('assignNotif');
        var sel = document.getElementById('driver_name');
        var driverName = ((sel && sel.value) || '').trim().toUpperCase();
        if (!pendingAssignment || !driverName) { return; }
        var nopol = pendingAssignment.nopol || '';
        fetch('/api/assignments/confirm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ driver_name: driverName, nopol: nopol })
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.status === 'success') {
                showToast('✅ ' + (d.msg || 'Konfirmasi berhasil'), '');
                if (box) box.classList.remove('show');
                pendingAssignment = null;
                loadDrivers();
            } else {
                showToast('❌ ' + (d.msg || 'Gagal konfirmasi'), 'error');
            }
        })
        .catch(function() { showToast('❌ Error koneksi', 'error'); });
    }

    // Cek ulang setiap kali driver dipilih (BBM, Trip, atau Kasbon)
    document.addEventListener('change', function(e) {
        var id = e.target && e.target.id;
        if (id === 'driver_name' || id === 'trip_driver' || id === 'kasbon_driver') checkPendingAssignment();
    });

    function initGPS() {
    if (!navigator.geolocation) { updateGpsUI(); return; }
    var box = document.getElementById('gpsBox');
    box.style.background = '#fef3c7';
    box.style.borderColor = '#d97706';
    document.getElementById('gpsTitle').textContent = '🔍 Mencari lokasi...';

    navigator.geolocation.getCurrentPosition(function(pos) {
        gpsData.lat = pos.coords.latitude;
        gpsData.lon = pos.coords.longitude;
        document.getElementById('gps_lat').value = gpsData.lat;
        document.getElementById('gps_lon').value = gpsData.lon;
        document.getElementById('gpsCoords').textContent = gpsData.lat.toFixed(6) + ', ' + gpsData.lon.toFixed(6);

        // Reverse geocode
        fetch('https://nominatim.openstreetmap.org/reverse?lat='+gpsData.lat+'&lon='+gpsData.lon+'&format=json&zoom=18&addressdetails=1&accept-language=id',
            { headers: { 'User-Agent': 'BPF-BBM/1.0' } })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d && d.address) {
                    var a = d.address;
                    var parts = [];
                    if (a.road) parts.push(a.road);
                    if (a.suburb || a.village) parts.push(a.suburb || a.village);
                    if (a.city || a.town) parts.push(a.city || a.town);
                    if (a.state) parts.push(a.state);
                    gpsData.addr = parts.join(', ') || d.display_name;
                    document.getElementById('gpsAddr').textContent = gpsData.addr;
                    document.getElementById('gps_address').value = gpsData.addr;
                }
                updateGpsUI();
            }).catch(function() { updateGpsUI(); });

        // Find nearby SPBU
        fetch('https://nominatim.openstreetmap.org/search?q=SPBU&format=json&limit=3&lat='+gpsData.lat+'&lon='+gpsData.lon+'&bounded=1&addressdetails=1&accept-language=id',
            { headers: { 'User-Agent': 'BPF-BBM/1.0' } })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data && data.length > 0) {
                    var names = data.slice(0, 2).map(function(d) {
                        var dist = d.dist ? Math.round(d.dist) + 'm' : '';
                        var name = d.display_name.split(',')[0].trim();
                        return name + (dist ? ' (' + dist + ')' : '');
                    });
                    gpsData.spbu = names.join(' | ');
                    var spbuEl = document.getElementById('gpsSpbu');
                    spbuEl.textContent = '⛽ ' + gpsData.spbu;
                    spbuEl.style.display = 'inline-block';
                }
            }).catch(function() {});
    }, function() {
        updateGpsUI();
    }, { enableHighAccuracy: true, timeout: 20000, maximumAge: 300000 });
}

function updateGpsUI() {
    var box = document.getElementById('gpsBox');
    if (gpsData.lat) {
        box.style.background = '#f0fdf4';
        box.style.borderColor = '#059669';
        document.getElementById('gpsTitle').textContent = '📍 Lokasi Terdeteksi';
    } else {
        box.style.background = '#fee2e2';
        box.style.borderColor = '#dc2626';
        document.getElementById('gpsTitle').textContent = '⚠ GPS Tidak Aktif';
        document.getElementById('gpsAddr').textContent = 'Mohon izinkan akses lokasi';
    }
}

// ============================================================
// DRIVERS
function autoFill() {
    var sel = document.getElementById('driver_name');
    var opt = sel.options[sel.selectedIndex];
    if (!opt || !opt.dataset.nopol) return;

    document.getElementById('nopol').value = opt.dataset.nopol || '';
    document.getElementById('vehicle_type').value = opt.dataset.vehicle || '';

    var bbm = document.getElementById('bbm_type');
    bbm.innerHTML = '<option value="">Loading...</option>';

    var vehicleType = opt.dataset.vehicle || 'AVANZA';

    fetch('/api/vehicle-allowed-bbm/' + encodeURIComponent(vehicleType))
        .then(function(r) { return r.json(); })
        .then(function(list) {
            bbm.innerHTML = '';

            if (!list || list.length === 0) {
                // Fallback: tidak ada BBM terdaftar → pakai default dari dataset
                var fallbackBBM = opt.dataset.bbm || 'PERTALITE';
                var o = document.createElement('option');
                o.value = fallbackBBM;
                o.textContent = fallbackBBM + ' (default)';
                o.dataset.price = (fallbackBBM === 'PERTAMAX') ? 16250 : 10000;
                o.selected = true;
                bbm.appendChild(o);
                updatePrice();
                return;
            }

            // Urutkan: default dulu, PERTALITE kedua
            list.sort(function(a, b) {
                if (a.is_default) return -1;
                if (b.is_default) return 1;
                if (a.bbm_type === 'PERTALITE') return -1;
                if (b.bbm_type === 'PERTALITE') return 1;
                return 0;
            });

            var hasSelection = false;

            list.forEach(function(b) {
                var o = document.createElement('option');
                o.value = b.bbm_type;
                o.textContent = b.bbm_type + ' (Rp ' + Number(b.price_per_liter).toLocaleString('id-ID') + ')';
                o.dataset.price = b.price_per_liter;

                // Prioritas seleksi:
                // 1. is_default = true
                // 2. Cocok dengan dataset driver
                // 3. PERTALITE
                if (b.is_default && !hasSelection) {
                    o.selected = true;
                    hasSelection = true;
                }
                if (b.bbm_type === opt.dataset.bbm && !hasSelection) {
                    o.selected = true;
                    hasSelection = true;
                }

                bbm.appendChild(o);
            });

            // Jika belum ada yang selected → pilih PERTALITE
            if (!hasSelection) {
                for (var i = 0; i < bbm.options.length; i++) {
                    if (bbm.options[i].value === 'PERTALITE') {
                        bbm.options[i].selected = true;
                        break;
                    }
                }
            }

            updatePrice();
        })
        .catch(function(e) {
            console.error('[BBM] Error:', e);
            bbm.innerHTML = '<option value="PERTALITE">PERTALITE (default)</option>';
            updatePrice();
        });
}

function autoFillTrip() {
    var sel = document.getElementById('trip_driver');
    var opt = sel.options[sel.selectedIndex];
    if (opt) {
        document.getElementById('trip_nopol').value = opt.dataset.nopol || '';
    }
}

function updatePrice() {
    let sel = document.getElementById('bbm_type');
    let opt = sel.options[sel.selectedIndex];
    if (opt && opt.dataset.price) { document.getElementById('price_per_liter').value = opt.dataset.price; calcL(); }
}

function calcL() {
    let n = document.getElementById('nominal').value;
    let p = document.getElementById('price_per_liter').value || 10000;
    if (n > 0) { let l = n/p; document.getElementById('liter').value = l.toFixed(2); document.getElementById('literDisplay').textContent = l.toFixed(2) + ' L'; }
}

// ============================================================
// PHOTOS
// ============================================================
function cap(id) { let el = document.getElementById(id); el.setAttribute('capture','environment'); el.click(); }
function pick(id) { let el = document.getElementById(id); el.removeAttribute('capture'); el.click(); }
function rm(id) { document.getElementById(id).value = ''; document.getElementById('prev_'+id).classList.add('hidden'); }
document.addEventListener('change', function(e) {
    if (!e.target.classList.contains('form-control-file') || !e.target.files[0]) return;
    let f = e.target.files[0];
    if (!f.type.startsWith('image/')) { e.target.value = ''; return; }
    let r = new FileReader();
    r.onload = ev => { document.getElementById('img_'+e.target.id).src = ev.target.result; document.getElementById('prev_'+e.target.id).classList.remove('hidden'); };
    r.readAsDataURL(f);
});
document.getElementById('spbu_type').addEventListener('change', function() {
    let d = document.getElementById('dispenser_div');
    if (this.value === 'non_rekanan') { d.classList.remove('hidden'); document.getElementById('foto_struk_dispenser').setAttribute('required','required'); }
    else { d.classList.add('hidden'); document.getElementById('foto_struk_dispenser').removeAttribute('required'); }
});

// ============================================================
// TRIP ROWS
// ============================================================
function addTripRow() {
    let d = document.createElement('div');
    d.className = 'trip-row';
    d.innerHTML = '<button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>' +
        '<div><div class="row-label">Lokasi Berangkat <button type="button" onclick="fillGPSWithTime(this)" style="background:#dbeafe;color:#1e40af;border:none;border-radius:3px;cursor:pointer;font-size:9px;padding:1px 5px;margin-left:4px;" title="Isi GPS + Jam otomatis">📍 GPS</button></div><input name="lokasi_berangkat[]" class="form-control loc-input" required placeholder="Nama tempat..."></div>' +
        '<div><div class="row-label">Pukul</div><input type="time" name="pukul_berangkat[]" class="form-control time-input" required></div>' +
        '<div><div class="row-label">KM</div><input type="number" name="km_berangkat[]" class="form-control km-input" required placeholder="0"></div>' +
        '<div><div class="row-label">Lokasi Tujuan <button type="button" onclick="fillGPSWithTime(this)" style="background:#dbeafe;color:#1e40af;border:none;border-radius:3px;cursor:pointer;font-size:9px;padding:1px 5px;margin-left:4px;" title="Isi GPS + Jam otomatis">📍 GPS</button></div><input name="lokasi_tujuan[]" class="form-control loc-input" required placeholder="Nama tempat..."></div>' +
        '<div><div class="row-label">Pukul</div><input type="time" name="pukul_tujuan[]" class="form-control time-input" required></div>' +
        '<div><div class="row-label">KM</div><input type="number" name="km_tujuan[]" class="form-control km-input" required placeholder="0"></div>';
    document.getElementById('tripRows').appendChild(d);
}


    // ============================================================
    // ONE-CLICK GPS FILL + AUTO TIME
    // ============================================================
    function fillGPSWithTime(btn) {
        // Cari parent trip-row
        var row = btn.closest('.trip-row');
        if (!row) return;

        // Cari input lokasi (setelah tombol GPS)
        var locInput = btn.parentElement.nextElementSibling;

        // Isi lokasi dari GPS
        if (gpsData.addr) {
            locInput.value = gpsData.addr;
            locInput.style.background = '#f0fdf4';
            locInput.style.borderColor = '#059669';
            setTimeout(function() {
                locInput.style.background = '';
                locInput.style.borderColor = '';
            }, 2000);
        } else if (gpsData.lat && gpsData.lon) {
            locInput.value = 'Mendeteksi...';
            locInput.disabled = true;
            fetch('https://nominatim.openstreetmap.org/reverse?lat='+gpsData.lat+'&lon='+gpsData.lon+'&format=json&zoom=18&accept-language=id',
                { headers: { 'User-Agent': 'BPF-BBM/1.0' } })
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    if (d && d.display_name) {
                        gpsData.addr = d.display_name;
                        locInput.value = d.display_name;
                        document.getElementById('gps_address').value = d.display_name;
                        document.getElementById('gpsAddr').textContent = d.display_name;
                    } else {
                        locInput.value = gpsData.lat.toFixed(6) + ', ' + gpsData.lon.toFixed(6);
                    }
                    locInput.style.background = '#f0fdf4';
                    locInput.style.borderColor = '#059669';
                })
                .catch(function() {
                    locInput.value = gpsData.lat.toFixed(6) + ', ' + gpsData.lon.toFixed(6);
                })
                .finally(function() {
                    locInput.disabled = false;
                    setTimeout(function() {
                        locInput.style.background = '';
                        locInput.style.borderColor = '';
                    }, 2000);
                });
        } else {
            alert('GPS belum terdeteksi. Mohon tunggu atau izinkan akses lokasi.');
            return;
        }

        // Auto-fill waktu sekarang ke input "Pukul" di row yang sama
        var now = new Date();
        var timeStr = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0');
        var timeInputs = row.querySelectorAll('.time-input');
        if (timeInputs.length > 0) {
            // Isi waktu ke input pukul yang sesuai (berangkat atau tujuan)
            // Cari input pukul yang paling dekat dengan tombol
            var allInputs = row.querySelectorAll('input');
            var btnIndex = Array.from(allInputs).indexOf(locInput);
            if (btnIndex >= 0 && btnIndex + 1 < allInputs.length) {
                var nextTimeInput = allInputs[btnIndex + 1];
                if (nextTimeInput.type === 'time') {
                    nextTimeInput.value = timeStr;
                    nextTimeInput.style.background = '#f0fdf4';
                    setTimeout(function() { nextTimeInput.style.background = ''; }, 2000);
                }
            }
        }

        // Auto-fill KM dari ODO tab BBM (jika tersedia)
        var odoInput = document.getElementById('odo_km');
        if (odoInput && odoInput.value) {
            var kmInputs = row.querySelectorAll('.km-input');
            if (kmInputs.length > 0 && !kmInputs[0].value) {
                kmInputs[0].value = odoInput.value;
                kmInputs[0].style.background = '#f0fdf4';
                setTimeout(function() { kmInputs[0].style.background = ''; }, 2000);
            }
        }

        // Toast feedback
        showToast('📍 Lokasi & jam terisi otomatis', '');
    }

    // Update getGPSForInput untuk backward compatibility
    function getGPSForInput(input) {
        // Cari tombol GPS terdekat dan panggil fillGPSWithTime
        var row = input.closest('.trip-row');
        if (row) {
            var btn = row.querySelector('button[onclick*="fillGPSWithTime"]');
            if (btn) { fillGPSWithTime(btn); return; }
        }
        // Fallback
        if (gpsData.addr) { input.value = gpsData.addr; }
        else if (gpsData.lat && gpsData.lon) { input.value = gpsData.lat.toFixed(6) + ', ' + gpsData.lon.toFixed(6); }
    }


// ============================================================
// FORM SUBMITS
// ============================================================
document.getElementById('bbmForm').addEventListener('submit', function(e) {
    e.preventDefault();
    submitForm(this, 'fuel_queue', '/driver', 'Laporan BBM berhasil!');
});

document.getElementById('tripForm').addEventListener('submit', function(e) {
    e.preventDefault();
    submitForm(this, 'trip_queue', '/submit-trip', 'Log perjalanan berhasil!');
});

// ============================================================
// RAPOR
// ============================================================
function checkPerf() {
    let n = document.getElementById('perfNopol').value.trim().toUpperCase();
    if (!n) { showToast('Masukkan plat nomor!', 'error'); return; }
    let box = document.getElementById('perfResult');
    box.style.display = 'block';
    box.innerHTML = 'Menganalisis...';
    fetch('/api/get-feedback/' + encodeURIComponent(n)).then(r => r.json()).then(d => {
        if (d.status === 'success') {
            let cls = d.performa === 'BOROS' ? 'badge-danger' : (d.performa === 'CUKUP' ? 'badge-warn' : 'badge-good');
            box.innerHTML = '<span class="badge '+cls+'">'+d.performa+'</span> | <strong>'+d.avg_km_per_liter+' KM/L</strong><br><small>'+d.msg+'</small>';
        } else { box.innerHTML = 'Data tidak ditemukan'; }
    });
}

// ============================================================
// HELPERS
// ============================================================
function showToast(msg, type) {
    var t = document.createElement('div');
    t.className = 'toast' + (type ? ' ' + type : '');
    t.textContent = msg;
    t.style.animation = 'fadeInUp 0.3s ease';
    document.body.appendChild(t);
    // Progress bar
    var bar = document.createElement('div');
    bar.style.cssText = 'height:3px;background:rgba(255,255,255,0.5);border-radius:0 0 12px 12px;margin-top:6px;transition:width 3.5s linear;width:100%;';
    t.appendChild(bar);
    setTimeout(function() { bar.style.width = '0%'; }, 500);
    setTimeout(function() { t.style.opacity = '0'; t.style.transition = 'opacity 0.3s'; }, 3500);
    setTimeout(function() { t.remove(); }, 4000);
}
function showModal(msg, txId) {
    document.getElementById('modalMsg').textContent = msg;
    if (txId) { document.getElementById('modalTxId').textContent = '#' + txId; document.getElementById('modalTxId').style.display = 'inline-block'; }
    document.getElementById('successModal').classList.add('active');
}
function closeModal() { document.getElementById('successModal').classList.remove('active'); }

// ============================================================
// INIT
// ============================================================
openDB().then(() => { updateStatus(); syncAll(); });
window.addEventListener('online', () => { updateStatus(); syncAll(); });
window.addEventListener('offline', updateStatus);
setInterval(() => { if (navigator.onLine) syncAll(); updateStatus(); }, 30000);

initGPS();
    checkPendingAssignment();
loadDrivers();
    function switchTab(page) {
        // Update pages
        document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
        document.getElementById('page-' + page).classList.add('active');
        var labels = {bbm: '⛽ BBM', trip: '🗺️ Log Perjalanan', kasbon: '💰 Kasbon', rapor: '📊 Rapor Performa'};
        document.getElementById('currentTabLabel').textContent = labels[page] || '';

        // Update nav
        document.querySelectorAll('.nav-item').forEach(function(n) { n.classList.remove('active'); });
        document.querySelector('.nav-item[data-page="' + page + '"]').classList.add('active');

        // Save active tab
        localStorage.setItem('activeTab', page);

        // Restore form data for this tab
        if (page === 'bbm') restoreFormData('fuel_queue');
        if (page === 'trip') restoreFormData('trip_queue');
    }

    // Restore last active tab
    (function() {
        var saved = localStorage.getItem('activeTab') || 'bbm';
        switchTab(saved);
    })();

    // ============================================================
    // AUTO-SAVE FORM DATA (anti-hilang)
    // ============================================================
    function saveFormData(store) {
        var form = store === 'fuel_queue' ? document.getElementById('bbmForm') : document.getElementById('tripForm');
        var data = {};
        var inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(el) {
            if (el.name) data[el.name] = el.value;
        });
        localStorage.setItem('saved_' + store, JSON.stringify(data));
    }

    function restoreFormData(store) {
        var saved = localStorage.getItem('saved_' + store);
        if (!saved) return;
        try {
            var data = JSON.parse(saved);
            var form = store === 'fuel_queue' ? document.getElementById('bbmForm') : document.getElementById('tripForm');
            for (var key in data) {
                var el = form.querySelector('[name="' + key + '"]');
                if (el && !el.value) el.value = data[key];
            }
        } catch(e) {}
    }

    function clearSavedFormData(store) {
        localStorage.removeItem('saved_' + store);
    }

    // Auto-save setiap 3 detik
    setInterval(function() {
        var activePage = document.querySelector('.page.active');
        if (!activePage) return;
        if (activePage.id === 'page-bbm') saveFormData('fuel_queue');
        if (activePage.id === 'page-trip') saveFormData('trip_queue');
    }, 3000);

    // Restore data saat halaman load
    restoreFormData('fuel_queue');
    restoreFormData('trip_queue');

    // Save sebelum unload
    window.addEventListener('beforeunload', function() {
        saveFormData('fuel_queue');
        saveFormData('trip_queue');
    });


var dailyCode=null;
async function loadKasbonData(){try{var r=await fetch('/api/cash/daily-code');var d=await r.json();dailyCode=d.code||(Math.floor(Math.random()*20)+1)*100;document.getElementById('kasbon_code').value='Rp '+dailyCode;
    // Tampilkan mode
    var modeEl=document.getElementById('kasbonMode');
    if(modeEl){
        if(d.manual_mode){modeEl.textContent='🔒 Kode ditentukan Finance';modeEl.style.color='#d97706';}
        else{modeEl.textContent='🤖 Kode otomatis';modeEl.style.color='#059669';}
    }
}catch(e){} fillKasbonDrivers();loadPendingLPJ();}
var _kasbonDriversFilled=false;function fillKasbonDrivers(){var sel=document.getElementById('kasbon_driver');if(_kasbonDriversFilled&&sel.options.length>1)return;var drivers=window.masterDrivers||window._cachedDrivers||[];if(drivers.length===0){console.log('[Kasbon] No cached drivers, triggering loadDrivers...');if(typeof loadDrivers==='function'){loadDrivers().then(function(){setTimeout(fillKasbonDrivers,500)})}else{setTimeout(fillKasbonDrivers,1000)}return}_kasbonDriversFilled=true;drivers.forEach(function(d){if(!d.name||!d.is_active)return;var o=document.createElement('option');o.value=d.name;o.textContent=d.name;o.dataset.nopol=d.nopol||'';o.dataset.vehicle=d.vehicle_type||'AVANZA';o.dataset.bbm=d.bbm_type||'PERTALITE';sel.appendChild(o)})}
function fillKasbonDriver(){var s=document.getElementById('kasbon_driver'),o=s.options[s.selectedIndex];if(o){document.getElementById('kasbon_nopol').value=o.dataset.nopol||'';document.getElementById('kasbon_vehicle').value=o.dataset.vehicle||''}}
function calcKasbon(){var b=parseInt(document.getElementById('kasbon_base').value)||0;if(b>0&&dailyCode)document.getElementById('kasbon_total').value='Rp '+(b+dailyCode).toLocaleString('id-ID')}

async function deleteCash(id){if(!confirm('Hapus pengajuan ini?'))return;try{await fetch('/api/cash/delete/'+id,{method:'POST'});loadKasbonHistory();loadPendingLPJ();}catch(e){}}
async function submitKasbon(){var d=document.getElementById('kasbon_driver').value,b=parseInt(document.getElementById('kasbon_base').value)||0,m=document.getElementById('kasbonMsg');if(!d||b<=0){m.textContent='Isi driver dan nominal!';m.style.color='#dc2626';return}var total=document.getElementById('kasbon_total').value;if(!confirm('Ajukan dana sebesar '+total+'?\n\nNominal ini sudah termasuk kode unik hari ini.'))return;m.textContent='...';try{var r=await fetch('/api/cash/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({driver_name:d,nopol:document.getElementById('kasbon_nopol').value,base_amount:b})});var j=await r.json();m.textContent=j.status==='success'?'✅ '+j.msg:'❌ '+(j.msg||'Gagal');m.style.color=j.status==='success'?'#059669':'#dc2626';if(j.status==='success'){document.getElementById('kasbon_base').value='';document.getElementById('kasbon_total').value='';loadPendingLPJ();loadKasbonHistory()}}catch(e){m.textContent='Error';m.style.color='#dc2626'}}
async function loadPendingLPJ(){var sel=document.getElementById('kasbon_driver');var driver=sel.options[sel.selectedIndex]?.value||'';var url='/api/cash/pending-lpj';if(driver)url+='?driver='+encodeURIComponent(driver);try{var r=await fetch(url),d=await r.json();document.getElementById('lpjCount').textContent='('+d.length+')'+(driver?' - '+driver:'');if(d.length===0){document.getElementById('lpjList').innerHTML='<p style="color:#94a3b8;text-align:center;">Tidak ada LPJ pending</p>';return}var h='';for(var i=0;i<d.length;i++){var c=d[i];h+='<div style="background:#fef3c7;padding:10px;border-radius:8px;margin-bottom:6px;border-left:4px solid #d97706;"><strong>'+c.display_id+'</strong> | Rp '+Number(c.total_amount).toLocaleString('id-ID')+'<br><small>Kode: '+c.daily_code+'</small><br><button class="btn-sm" style="margin-top:6px;background:#2563eb;" onclick="openLPJForm('+c.id+','+c.total_amount+',\''+c.nopol+'\',\''+c.bbm_type+'\')">📝 Isi LPJ</button></div>'}document.getElementById('lpjList').innerHTML=h}catch(e){}}
function openLPJForm(cid,amt,nopol,bbm){if(!confirm('Isi LPJ untuk Kasbon #'+cid+'?\n\nNominal: Rp '+Number(amt).toLocaleString('id-ID')+'\nNominal ini sudah termasuk kode unik dan TIDAK BISA DIUBAH.'))return;switchTab('bbm');document.getElementById('nominal').value=amt;document.getElementById('nopol').value=nopol||'';document.getElementById('bbm_type').value=bbm||'PERTALITE';document.getElementById('nominal').style.background='#fef3c7';document.getElementById('nominal').title='Nominal dari Kasbon #'+cid;updatePrice();calcL();window._activeLPJCashId=cid;document.getElementById('bbmBtn').textContent='📤 Kirim LPJ Kasbon'}
async function loadKasbonHistory(){var sel=document.getElementById('kasbon_driver');var driver=sel.options[sel.selectedIndex]?.value||'';var url='/api/cash/history';if(driver)url+='?driver='+encodeURIComponent(driver);try{var r=await fetch(url),d=await r.json();if(d.length===0){document.getElementById('kasbonHistory').innerHTML='<p style="color:#94a3b8;text-align:center;">Belum ada pengajuan</p>';return}var steps=['DRAFT','GA_APPROVED','FINANCE_APPROVED','FUNDS_WITH_DRIVER','LPJ_SUBMITTED','COMPLETED'],sl={'DRAFT':'📝','GA_APPROVED':'✅','FINANCE_APPROVED':'💰','FUNDS_WITH_DRIVER':'🤝','LPJ_SUBMITTED':'📋','COMPLETED':'🎉','REJECTED':'❌'};
var stepTooltips={'DRAFT':'Menunggu GA Approve','GA_APPROVED':'Menunggu Finance Approve','FINANCE_APPROVED':'Siap Handover','FUNDS_WITH_DRIVER':'Dana di Tangan Driver - Isi LPJ','LPJ_SUBMITTED':'LPJ Terkirim','COMPLETED':'Selesai','REJECTED':'Ditolak'};var h='';for(var i=0;i<Math.min(d.length,10);i++){var c=d[i];if(c.status==='REJECTED'){h+='<div style="background:#fee2e2;padding:8px;border-radius:6px;margin-bottom:4px;font-size:11px;"><strong>'+c.display_id+'</strong> | Rp '+Number(c.total_amount).toLocaleString('id-ID')+' <span style="float:right;color:#dc2626;">❌ Ditolak</span></div>';continue}var currentStep=steps.indexOf(c.status);if(currentStep<0)currentStep=0;var pct=c.status==='COMPLETED'?100:Math.round((currentStep/(steps.length-1))*100);var barColor=c.status==='COMPLETED'?'#059669':pct>=60?'#2563eb':pct>=30?'#d97706':'#94a3b8';h+='<div style="background:#fff;padding:10px;border-radius:8px;margin-bottom:6px;box-shadow:0 1px 3px rgba(0,0,0,0.06);"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><strong>'+c.display_id+'</strong><span style="font-size:11px;color:#64748b;">Rp '+Number(c.total_amount).toLocaleString('id-ID')+'</span></div><div style="background:#e2e8f0;border-radius:4px;height:6px;overflow:hidden;"><div style="background:'+barColor+';height:100%;width:'+pct+'%;border-radius:4px;transition:width 0.5s;"></div></div><div style="display:flex;justify-content:space-between;margin-top:3px;font-size:9px;color:#94a3b8;">';for(var s=0;s<steps.length;s++){h+='<span style="color:'+(s<=currentStep?barColor:'#cbd5e1')+';">'+sl[steps[s]]+'</span>'}h+='</div></div>'}document.getElementById('kasbonHistory').innerHTML=h;
    var legend=document.createElement('div');
    legend.style.cssText='margin-top:8px;padding:6px;background:#f8fafc;border-radius:6px;font-size:9px;color:#64748b;text-align:center;';
    legend.innerHTML='📝 Draft → ✅ GA → 💰 Finance → 🤝 Serah → 📋 LPJ → 🎉 Done';
    document.getElementById('kasbonHistory').appendChild(legend);
}catch(e){}}
var _kasbonLoaded=false;var _origSwitchTab=switchTab;switchTab=function(p){_origSwitchTab(p);if(p==='kasbon'&&!_kasbonLoaded){_kasbonLoaded=true;loadKasbonData()}};


    // ============================================================
    // SKELETON LOADING
    // ============================================================
    function showSkeleton(containerId, type) {
        var el = document.getElementById(containerId);
        if (!el) return;
        if (type === 'card') {
            el.innerHTML = '<div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div>';
        } else if (type === 'text') {
            el.innerHTML = '<div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text short"></div>';
        } else if (type === 'table') {
            el.innerHTML = '<div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text short"></div>';
        }
    }

    // Tampilkan skeleton sebelum load




    // ============================================================
    // PULL-TO-REFRESH
    // ============================================================
    var touchStartY = 0;
    var pullThreshold = 80;
    var isPulling = false;

    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) touchStartY = e.touches[0].clientY;
    }, {passive: true});

    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && e.touches[0].clientY - touchStartY > 20) {
            isPulling = true;
            var pull = Math.min(e.touches[0].clientY - touchStartY, pullThreshold);
            var indicator = document.getElementById('ptrIndicator');
            if (indicator) {
                indicator.style.display = 'block';
                indicator.style.height = pull + 'px';
                indicator.textContent = pull >= pullThreshold ? '✅ Lepas untuk refresh' : '⬇️ Tarik untuk refresh';
                indicator.className = 'ptr-indicator show' + (pull >= pullThreshold ? ' refreshing' : '');
            }
        }
    }, {passive: true});

    document.addEventListener('touchend', function() {
        if (isPulling) {
            var pull = document.getElementById('ptrIndicator')?.offsetHeight || 0;
            if (pull >= pullThreshold) {
                // Refresh current tab
                var activePage = document.querySelector('.page.active');
                if (activePage) {
                    if (activePage.id === 'page-bbm') { loadDrivers(); }
                    if (activePage.id === 'page-kasbon') { loadKasbonData(); }
                }
            }
            var indicator = document.getElementById('ptrIndicator');
            if (indicator) { indicator.style.display = 'none'; indicator.style.height = '0'; }
            isPulling = false;
        }
    });

    // ============================================================
    // SWIPE GESTURE (antar tab)
    // ============================================================
    var swipeStartX = 0;
    var tabs = ['bbm', 'trip', 'kasbon', 'rapor']; // urutan sama dengan bottom-nav

    document.addEventListener('touchstart', function(e) {
        swipeStartX = e.touches[0].clientX;
    }, {passive: true});

    document.addEventListener('touchend', function(e) {
        var diff = e.changedTouches[0].clientX - swipeStartX;
        if (Math.abs(diff) < 50) return; // minimum swipe distance

        var activePage = document.querySelector('.page.active');
        if (!activePage) return;
        var currentTab = activePage.id.replace('page-', '');
        var currentIndex = tabs.indexOf(currentTab);
        if (currentIndex < 0) return;

        var newIndex = currentIndex;
        if (diff < -50) newIndex = Math.min(currentIndex + 1, tabs.length - 1); // swipe left → next
        if (diff > 50) newIndex = Math.max(currentIndex - 1, 0); // swipe right → prev

        if (newIndex !== currentIndex) {
            switchTab(tabs[newIndex]);
            // Tampilkan hint
            var hint = document.createElement('div');
            hint.className = 'swipe-hint';
            hint.textContent = '← Swipe →';
            document.body.appendChild(hint);
            setTimeout(function() { hint.remove(); }, 3000);
        }
    }, {passive: true});


    // ============================================================
    // DARK MODE
    // ============================================================
    function toggleDarkMode() {
        document.body.classList.toggle('dark');
        var isDark = document.body.classList.contains('dark');
        document.getElementById('darkToggle').textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem('darkMode', isDark ? '1' : '0');
    }
    // Restore dark mode
    if (localStorage.getItem('darkMode') === '1') {
        document.body.classList.add('dark');
        document.getElementById('darkToggle').textContent = '☀️';
    }

// ============================================================
// APPOINTMENT -> TRIP LOG INTEGRATION
// ============================================================
var completedApps = [];

function loadAppointmentPanel() {
    var panel = document.getElementById('apptPanel');
    var driverSel = document.getElementById('trip_driver');
    var dateEl = document.getElementById('trip_date');
    var driver = driverSel ? driverSel.value.trim().toUpperCase() : '';
    var tripDate = dateEl ? dateEl.value : '';
    if (!panel) return;
    if (!driver || !tripDate) { panel.style.display = 'none'; return; }

    fetch('/api/appointments/completed?driver=' + encodeURIComponent(driver) + '&date=' + encodeURIComponent(tripDate))
        .then(function(r) { return r.json(); })
        .then(function(list) {
            if (!Array.isArray(list)) return;
            completedApps = list;
            var panelList = document.getElementById('apptPanelList');
            var countEl = document.getElementById('apptPanelCount');
            var btn = document.getElementById('fillApptBtn');
            if (!completedApps.length) {
                panel.style.display = 'none';
                return;
            }
            panel.style.display = 'block';
            countEl.textContent = completedApps.length;
            var html = '';
            for (var i = 0; i < completedApps.length; i++) {
                var a = completedApps[i];
                var waktu = a.sesi === '1' ? '🌅 08.30' : '🌆 14.30';
                html += '<div class="appt-item">' +
                    '<span class="appt-item-time">' + waktu + '</span>' +
                    '<div class="appt-item-body"><strong>' + a.nasabah_name + '</strong>' +
                    '<div>' + a.alamat + '</div>' +
                    '<div class="appt-item-meta">' + a.display_id + (a.area ? ' · ' + a.area : '') + '</div></div>' +
                '</div>';
            }
            panelList.innerHTML = html;
            btn.style.display = 'block';
        })
        .catch(function() {});
}

function fillTripFromAppointments() {
    if (!completedApps.length) { showToast('Tidak ada appointment selesai', 'error'); return; }
    var rowsWrap = document.getElementById('tripRows');
    if (!rowsWrap) return;

    // Hapus hidden appointment_id lama agar tidak duplikat
    rowsWrap.querySelectorAll('input[name="appointment_id[]"]').forEach(function(h) { h.remove(); });

    // Pastikan jumlah row cukup
    while (rowsWrap.children.length < completedApps.length) addTripRow();

    var previousTujuan = null;
    var previousPukul = null;
    var previousKm = null;
    for (var i = 0; i < completedApps.length; i++) {
        var a = completedApps[i];
        var row = rowsWrap.children[i];
        if (!row) continue;
        var waktu = a.sesi === '1' ? '08:30' : '14:30';

        var locInputs = row.querySelectorAll('.loc-input');
        var timeInputs = row.querySelectorAll('.time-input');
        var kmInputs = row.querySelectorAll('.km-input');

        // Lokasi berangkat: sambung dari tujuan sebelumnya (rute berantai)
        if (previousTujuan) {
            locInputs[0].value = previousTujuan;
        } else {
            locInputs[0].value = '';
            locInputs[0].placeholder = 'Kantor / titik awal keberangkatan';
        }
        timeInputs[0].value = previousPukul || waktu;
        kmInputs[0].value = previousKm != null ? previousKm : 0;

        // Lokasi tujuan = alamat nasabah appointment
        locInputs[1].value = a.alamat;
        timeInputs[1].value = waktu;
        kmInputs[1].value = 0;

        // Tandai baris sebagai terisi otomatis
        row.style.background = '#f0fdf4';
        row.style.borderLeft = '3px solid #059669';

        // Simpan referensi appointment (terintegrasi di trip_details)
        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'appointment_id[]';
        hidden.value = a.id;
        row.appendChild(hidden);

        previousTujuan = a.alamat;
        previousPukul = waktu;
        previousKm = 0;
    }
    showToast('📥 ' + completedApps.length + ' rute appointment dimuat. Lengkapi KM & pukul bila perlu.', '');
}

// Panggil panel saat driver/tanggal trip berubah atau tab trip dibuka
var _origAutoFillTrip = autoFillTrip;
autoFillTrip = function() {
    _origAutoFillTrip();
    loadAppointmentPanel();
};
document.getElementById('trip_date').addEventListener('change', loadAppointmentPanel);
var _origSwitchTab3 = switchTab;
switchTab = function(p) {
    _origSwitchTab3(p);
    if (p === 'trip') setTimeout(loadAppointmentPanel, 100);
};

addTripRow();
document.getElementById('trip_date').value = new Date().toISOString().split('T')[0];
setTimeout(loadAppointmentPanel, 300);
