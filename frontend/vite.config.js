import {defineConfig} from 'vite';

// import react from '@vitejs/plugin-react';
import reactRefresh from '@vitejs/plugin-react-refresh';

import envCompatible from 'vite-plugin-env-compatible';

// import { viteSingleFile } from "vite-plugin-singlefile"
// import legacy from '@vitejs/plugin-legacy'
// import {ManifestOptions, VitePWA, VitePWAOptions} from 'vite-plugin-pwa';


export default defineConfig({
  server: {
    hmr: {
      overlay: false
    }
  },
  plugins: [
    reactRefresh(),
    envCompatible({
      prefix: 'REACT_APP',
    }),
    // TODO(maybe): Consider using https://polyfill.io/v3/ from the index.html, to get polyfills aside from transforms.
    // TODO(maybe): ... Alternatively, check out: https://github.com/vitejs/vite/tree/main/packages/plugin-legacy
    // // XXX Might want to use vite plugin legacy, as easiest way to do some polyfills
    // legacy({targets  : ['Chrome >= 49'],
    //   polyfills      : ['es.promise.finally', 'es/map', 'es/set'],
    //   modernPolyfills: ['es.promise.finally'],
    // }),
    // viteSingleFile(), // <-- Was not necessary, but keeping the memo for a little. TODO: cleanup: remove
    // VitePWA(...) // <-- we're not ready yet, WIP...
  ],
  // base   : '/course', // FIXME: need to update package.json back to homepage: "/course/" instead of "/", and may need to set "base" config to "/course/" ...https://vitejs.dev/guide/build.html#public-base-path
  build: {
    target: 'modules',
    // target: 'es2015',

    // // <vite-single-file>
    // assetsInlineLimit    : 100000000,
    // chunkSizeWarningLimit: 100000000,
    // cssCodeSplit         : false,
    // brotliSize           : false,
    // rollupOptions        : {
    //   inlineDynamicImports: true,
    // },
    // // </vite-single-file>
  },
});
