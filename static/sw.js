const CACHE_NAME = 'static-cache';

const FILES_TO_CACHE = [
  '/static/offline-text.html',
  '/static/offline.html',
  '/static/styles/offline.css',
  '/static/images/logo.png'
];

self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Pre-caching offline page');
      return cache.addAll(FILES_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('[ServiceWorker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request).catch(() => {
    return caches.open(CACHE_NAME).then((cache) => {
      if (event.request.method === 'GET' && event.request.headers.get('accept').indexOf('text/html') !== -1)
        return cache.match('/static/offline.html');
      else
        return cache.match('/static/offline-text.html');
    });
  }));
});

