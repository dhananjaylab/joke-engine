const CACHE_NAME = 'giggle-v1'
const STATIC_ASSETS = [
  '/',
  '/history',
  '/favicon.svg',
  '/icons.svg',
  '/manifest.json'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => cacheName !== CACHE_NAME)
            .map((cacheName) => caches.delete(cacheName))
        )
      })
      .then(() => self.clients.claim())
  )
})

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return

  // Skip API requests and WebSocket upgrades
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/ws/') ||
      event.request.headers.get('upgrade') === 'websocket') {
    return
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request)
          .then((fetchResponse) => {
            // Cache successful responses for static assets
            if (fetchResponse.ok && event.request.url.startsWith(self.location.origin)) {
              const responseClone = fetchResponse.clone()
              caches.open(CACHE_NAME)
                .then((cache) => cache.put(event.request, responseClone))
            }
            return fetchResponse
          })
      })
      .catch(() => {
        // Fallback for navigation requests when offline
        if (event.request.mode === 'navigate') {
          return caches.match('/')
        }
      })
  )
})

// Background sync for sharing jokes when back online
self.addEventListener('sync', (event) => {
  if (event.tag === 'share-joke') {
    event.waitUntil(
      // Handle background sync for sharing
      console.log('Background sync: share-joke')
    )
  }
})

// Push notifications (future feature)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json()
    event.waitUntil(
      self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/favicon.svg',
        badge: '/favicon.svg',
        tag: 'giggle-notification'
      })
    )
  }
})