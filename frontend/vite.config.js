import {defineConfig} from 'vite';
// import react from '@vitejs/plugin-react';
import reactRefresh from '@vitejs/plugin-react-refresh'


import { ManifestOptions, VitePWA, VitePWAOptions } from 'vite-plugin-pwa'



export default defineConfig({
  plugins: [
    reactRefresh(),
    // VitePWA({
    //   workbox: {
    //     importScripts: [
    //       "Worker.js",
    //       // "service-worker.js",
    //     ],
    //   }
    // }),
  ],
});
