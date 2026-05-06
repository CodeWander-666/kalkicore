const CACHE = "kalki-core-v2";
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(["/","/index.html","/css/style.css","/js/kalki.js","/manifest.json","/404.html"])));
});
self.addEventListener("fetch", e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
