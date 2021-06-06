const CACHE_NAME = 'static-cache';

const FILES_TO_CACHE = [
  '/static/offline_text.html',
  '/static/offline_page.html',
  '/static/styles/offline_page.css',
  '/static/images/logo.png',
  '/static/images/logo1.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(FILES_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME)
          return caches.delete(key);
      }));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request).catch(() => {
    return caches.open(CACHE_NAME).then((cache) => {
      if ((event.request.method !== 'GET') || (event.request.headers.get('accept').indexOf('text/html') !== -1))
        return cache.match('/static/offline_page.html');
      else
        return cache.match('/static/offline_text.html');
    });
  }));
});

