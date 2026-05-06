const CACHE="kalki-v3";
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["/","/index.html","/js/kalki-v3.js","/manifest.json"])))});
self.addEventListener("fetch",e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))});
