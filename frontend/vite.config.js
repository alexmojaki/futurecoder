import {defineConfig} from 'vite';
// import react from '@vitejs/plugin-react';
import reactRefresh from '@vitejs/plugin-react-refresh';

import envCompatible from 'vite-plugin-env-compatible';

// import { viteSingleFile } from "vite-plugin-singlefile"
import legacy from '@vitejs/plugin-legacy'



import {ManifestOptions, VitePWA, VitePWAOptions} from 'vite-plugin-pwa';


export default defineConfig({
  plugins: [
    reactRefresh(),
    envCompatible({
      prefix: 'REACT_APP',
    }),
    legacy({targets  : ['Chrome >= 49'],
      polyfills      : ['es.promise.finally', 'es/map', 'es/set'],
      modernPolyfills: ['es.promise.finally'],
    }),
    // viteSingleFile(),
    // VitePWA({
    //   workbox: {
    //     importScripts: [
    //       "Worker.js",
    //       // "service-worker.js",
    //     ],
    //   }
    // }),
  ],
  base   : '/course', // FIXME...https://vitejs.dev/guide/build.html#public-base-path
  build  : {
    target: 'es2015',
    // target: "esnext",
    // TODO(maybe): Consider using https://polyfill.io/v3/ from the index.html, to get polyfills aside from transforms.
    // TODO(maybe): ... Alternatively, check out: https://github.com/vitejs/vite/tree/main/packages/plugin-legacy
    assetsInlineLimit    : 100000000,
    chunkSizeWarningLimit: 100000000,
    cssCodeSplit         : false,
    brotliSize           : false,
    rollupOptions        : {
      inlineDynamicImports: true,
      // output: {
      //   manualChunks: () => "everything.js",
      // },
    },
  },
});
