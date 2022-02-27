import {defineConfig} from 'vite';
// import react from '@vitejs/plugin-react';
import reactRefresh from '@vitejs/plugin-react-refresh'

import envCompatible from 'vite-plugin-env-compatible'


import { ManifestOptions, VitePWA, VitePWAOptions } from 'vite-plugin-pwa'



export default defineConfig({
  plugins: [
    reactRefresh(),
    envCompatible({
      prefix: "REACT_APP"
    })
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
