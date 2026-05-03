const CACHE_VERSION = 'v5';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

const APP_SHELL = [
  './',
  './index.html',
  './styles.css',
  './pyscript_app.py',
  './manifest.json',
  'https://pyscript.net/releases/2023.11.1/core.css',
  'https://pyscript.net/releases/2023.11.1/core.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(APP_SHELL);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== STATIC_CACHE)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      
      return fetch(event.request).then((response) => {
        // Cache external resources (like fonts, scripts) dynamically
        if (event.request.url.startsWith('http')) {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
                cache.put(event.request, responseClone);
            });
        }
        return response;
      }).catch(() => {
        // Return nothing or an offline page if implemented
        return new Response('Network error occurred');
      });
    })
  );
});
