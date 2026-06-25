const CACHE_NAME = 'bpf-bbm-v4';
const assetsToCache = ['/driver', '/manifest.json'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(assetsToCache))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method === 'POST') return;
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      return cachedResponse || fetch(event.request);
    })
  );
});
