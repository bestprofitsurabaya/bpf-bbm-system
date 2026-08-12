/* BPF Fleet — Service Worker legacy (v2.4)
   Sejak migrasi Vue, /driver redirect ke SPA /app/driver (yang punya SW sendiri
   scope /app/). SW ini kini network-first: perangkat driver lama tidak lagi
   menampilkan halaman klasik dari cache. Offline: fallback halaman minimal. */
const CACHE_NAME = 'bpf-bbm-20260812c';
const STATIC_ASSETS = ['/manifest.json', '/static/icon-192.png', '/static/icon-512.png'];

// Install: langsung aktif + cache asset statis saja (tanpa /driver yang kini 302).
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)).catch(() => {})
  );
});

// Activate: hapus cache lama milik driver (prefix bpf-bbm-), JANGAN sentuh cache SPA (bpf-spa-*).
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('bpf-bbm-') && k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Fetch: network-first untuk semua GET (redirect /driver diteruskan ke server),
// API/uploads/admin/SPA tetap dilewati (SPA punya SW sendiri di /app/).
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/uploads/')
      || url.pathname.startsWith('/admin') || url.pathname.startsWith('/app/')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache hanya respons 200 (redirect 302 /driver → /app/driver tidak di-cache)
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((c) => c.put(event.request, clone)).catch(() => {});
        }
        return response;
      })
      .catch(() =>
        caches.match(event.request).then((hit) => hit || (
          event.request.mode === 'navigate'
            ? new Response('<!doctype html><html><head><meta charset="utf-8"><title>Offline</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:90vh;margin:0;background:#0f172a;color:#e2e8f0;text-align:center}div{padding:24px}h1{font-size:18px}p{font-size:13px;opacity:.7}a{color:#60a5fa}</style></head><body><div><h1>🔌 Tidak Ada Koneksi</h1><p>Anda sedang offline. Buka aplikasi saat sudah online agar dapat sinkron.</p><p><a href="/app/driver">Buka Aplikasi Driver</a></p></div></body></html>', { headers: { 'Content-Type': 'text/html; charset=utf-8' } })
            : undefined
        ))
      )
  );
});

// Listen for message from client (skip waiting trigger)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
