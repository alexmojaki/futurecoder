import {serviceWorkerFetchListener} from "sync-message";

console.log(self.__WB_MANIFEST);

const fetchListener = serviceWorkerFetchListener({readTimeout: 5000});

addEventListener('fetch', function (e) {
  if (fetchListener(e)) {
    return;
  }
  e.respondWith(fetch(e.request));
});

addEventListener('install', function (e) {
  e.waitUntil(self.skipWaiting());
});

addEventListener('activate', function (e) {
  e.waitUntil(self.clients.claim());
});
