import {defineConfig} from 'vite';

// import react from '@vitejs/plugin-react';
import reactRefresh from '@vitejs/plugin-react-refresh';
import envCompatible from 'vite-plugin-env-compatible';

// <TODO(hangtwenty)-clean-up>
// import { viteSingleFile } from "vite-plugin-singlefile"
// import legacy from '@vitejs/plugin-legacy'
// </TODO(hangtwenty)-clean-up>

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
    // VitePWA(...) // <-- we're not ready yet, WIP...
  ],
  // https://vitejs.dev/guide/build.html#public-base-path
  // base   : '/course', // FIXME(hangtwenty): need to reconcile "/course" vs "/" -- see "homepage" in package.json too  ...
  build: {
    target: 'modules',
    // target: 'es2015',

    // <TODO(hangtwenty)-clean-up>
    // // <vite-single-file>
    // assetsInlineLimit    : 100000000,
    // chunkSizeWarningLimit: 100000000,
    // cssCodeSplit         : false,
    // brotliSize           : false,
    // rollupOptions        : {
    //   inlineDynamicImports: true,
    // },
    // // </vite-single-file>
    // </TODO(hangtwenty)-clean-up>
  },
});
