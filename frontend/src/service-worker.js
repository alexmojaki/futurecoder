import {serviceWorkerFetchListener} from "sync-message";

console.log(self.__WB_MANIFEST);

const fetchListener = serviceWorkerFetchListener();

addEventListener('fetch', fetchListener);

addEventListener('install', function (e) {
  e.waitUntil(self.skipWaiting());
});

addEventListener('activate', function (e) {
  e.waitUntil(self.clients.claim());
});
