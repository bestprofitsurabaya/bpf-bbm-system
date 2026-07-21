const CACHE_NAME = 'bpf-bbm-20260721_FINAL';
const STATIC_ASSETS = [
    '/',
    '/driver',
    '/manifest.json',
    '/static/icon-192.png',
    '/static/icon-512.png'
];

// Install: langsung skip waiting agar SW baru langsung aktif
self.addEventListener('install', event => {
    console.log('[SW 20260717_v1412] Installing...');
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.warn('[SW] Some assets failed to cache:', err);
            });
        })
    );
});

// Activate: hapus SEMUA cache lama, langsung claim clients
self.addEventListener('activate', event => {
    // KILL SWITCH: Hapus semua cache lama
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    console.log('[SW] Deleting old cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
        }).then(function() {
            console.log('[SW] All caches cleared, claiming clients...');
            return // self.clients.claim(); // done in activate
        })
    );
    console.log('[SW 20260717_v1412] Activating...');
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => {
                        console.log('[SW] Deleting old cache:', key);
                        return caches.delete(key);
                    })
            );
        }).then(() => {
            console.log('[SW] Claiming all clients...');
            return // self.clients.claim(); // done in activate
        })
    );
});

// Fetch: cache-first untuk static, network-first untuk API
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;
    
    const url = new URL(event.request.url);
    
    // Skip API calls & uploads (network-first)
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/uploads/') || url.pathname.startsWith('/admin')) {
        return;
    }
    
    // Cache-first untuk static pages
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                // Fetch update di background (stale-while-revalidate)
                fetch(event.request).then(response => {
                    if (response && response.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, response.clone());
                        });
                    }
                }).catch(() => {});
                return cachedResponse;
            }
            return fetch(event.request).then(response => {
                if (response && response.status === 200 && response.type === 'basic') {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            });
        }).catch(() => {
            if (event.request.mode === 'navigate') {
                return caches.match('/driver');
            }
        })
    );
});

// Listen for message from client (skip waiting trigger)
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
