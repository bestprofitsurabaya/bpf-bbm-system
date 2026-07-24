const DB_NAME = 'BPF_Driver_DB', DB_VER = 3;
const CACHE_KEY_DRIVERS = 'cached_drivers';
const CACHE_KEY_VEHICLES = 'cached_vehicles';
const CACHE_KEY_ASSIGNMENTS = 'cached_assignments';
let db = null;

function openDB() {
    return new Promise((resolve, reject) => {
        let req = indexedDB.open(DB_NAME, DB_VER);
        req.onupgradeneeded = e => {
            let d = e.target.result;
            if (!d.objectStoreNames.contains('fuel_queue')) d.createObjectStore('fuel_queue', { keyPath: 'id', autoIncrement: true });
            if (!d.objectStoreNames.contains('trip_queue')) d.createObjectStore('trip_queue', { keyPath: 'id', autoIncrement: true });
        };
        req.onsuccess = e => { db = e.target.result; resolve(db); };
        req.onerror = e => reject(e);
    });
}

function saveToQueue(store, data) {
    return new Promise((resolve, reject) => {
        let tx = db.transaction(store, 'readwrite');
        let req = tx.objectStore(store).add(data);
        req.onsuccess = () => resolve(req.result);
        req.onerror = e => reject(e);
    });
}

function getAllFromQueue(store) {
    return new Promise((resolve, reject) => {
        let tx = db.transaction(store, 'readonly');
        let req = tx.objectStore(store).getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror = e => reject(e);
    });
}

function deleteFromQueue(store, id) {
    return new Promise((resolve, reject) => {
        let tx = db.transaction(store, 'readwrite');
        tx.objectStore(store).delete(id);
        tx.oncomplete = () => resolve();
        tx.onerror = e => reject(e);
    });
}

function countQueue(store) {
    return new Promise((resolve, reject) => {
        let tx = db.transaction(store, 'readonly');
        let req = tx.objectStore(store).count();
        req.onsuccess = () => resolve(req.result);
        req.onerror = e => reject(e);
    });
}

function cacheMasterData(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify({ data: data, timestamp: Date.now() }));
    } catch(e) {}
}

function getCachedMasterData(key) {
    try {
        let raw = localStorage.getItem(key);
        if (!raw) return null;
        let cached = JSON.parse(raw);
        if (Date.now() - cached.timestamp < 86400000) return cached.data;
    } catch(e) {}
    return null;
}
