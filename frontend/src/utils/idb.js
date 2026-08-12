/**
 * IndexedDB wrapper — antrean offline driver (port dari static/js/db.js).
 * 3 antrean: fuel_queue (klaim BBM), trip_queue (log perjalanan), lpj_queue (LPJ kasbon).
 */
const DB_NAME = 'BPF_Driver_DB'
const DB_VER = 3
const STORES = ['fuel_queue', 'trip_queue', 'lpj_queue']

let _dbPromise = null

function openDB() {
  if (_dbPromise) return _dbPromise
  _dbPromise = new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB tidak didukung browser ini'))
      return
    }
    const req = indexedDB.open(DB_NAME, DB_VER)
    req.onupgradeneeded = (e) => {
      const d = e.target.result
      for (const s of STORES) {
        if (!d.objectStoreNames.contains(s)) d.createObjectStore(s, { keyPath: 'id', autoIncrement: true })
      }
    }
    req.onsuccess = (e) => resolve(e.target.result)
    req.onerror = (e) => { _dbPromise = null; reject(e) }
  })
  return _dbPromise
}

function tx(store, mode) {
  return openDB().then((db) => db.transaction(store, mode))
}

export async function addToQueue(store, data) {
  const t = await tx(store, 'readwrite')
  return new Promise((resolve, reject) => {
    const req = t.objectStore(store).add(data)
    req.onsuccess = () => resolve(req.result)
    req.onerror = (e) => reject(e)
  })
}

export async function getAllFromQueue(store) {
  const t = await tx(store, 'readonly')
  return new Promise((resolve, reject) => {
    const req = t.objectStore(store).getAll()
    req.onsuccess = () => resolve(req.result)
    req.onerror = (e) => reject(e)
  })
}

export async function deleteFromQueue(store, id) {
  const t = await tx(store, 'readwrite')
  return new Promise((resolve, reject) => {
    t.objectStore(store).delete(id)
    t.oncomplete = () => resolve()
    t.onerror = (e) => reject(e)
  })
}

export async function countQueue(store) {
  const t = await tx(store, 'readonly')
  return new Promise((resolve, reject) => {
    const req = t.objectStore(store).count()
    req.onsuccess = () => resolve(req.result)
    req.onerror = (e) => reject(e)
  })
}

/** Hitung semua antrean sekaligus → { fuel, trip, lpj }. */
export async function countAllQueues() {
  try {
    const [fuel, trip, lpj] = await Promise.all([
      countQueue('fuel_queue'), countQueue('trip_queue'), countQueue('lpj_queue'),
    ])
    return { fuel, trip, lpj }
  } catch {
    return { fuel: 0, trip: 0, lpj: 0 }
  }
}
