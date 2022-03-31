const path = require('path');
const fs = require('fs');

const WorkboxWebpackPlugin = require('workbox-webpack-plugin');
const paths = require('./paths'); // <-- Copied from "CRA eject" -- "config" folder.

const isEnvProduction = process.env.NODE_ENV === "production"
const swSrc = paths.swSrc;
console.info({swSrc, exists: fs.existsSync(swSrc)})

module.exports = {
  webpack: {
    configure: (webpackConfig, {env, paths}) => {
      // Output to ./course (instead of ./build)
      paths.appBuild = webpackConfig.output.path = path.resolve('course');
      return webpackConfig;
    },
    plugins: [
      isEnvProduction &&
      fs.existsSync(swSrc) &&
      new WorkboxWebpackPlugin.InjectManifest({
        // At time of writing, the swSrc snd other arguments are the same as when doing "CRA eject",
        // and so they SHOULD behave the same as when this whole block (`plugins`) is commented-out.
        // However, for some reason, we're getting "Can't find self.__WB_MANIFEST in your SW source"
        // even though `self.__WB_MANIFEST` clearly exists in src/service-worker.js, and it works
        // when the default settings are left in place... Rather opaque error right now...
        swSrc,
        dontCacheBustURLsMatching: /\.[0-9a-f]{8}\./,
        exclude: [/\.map$/, /asset-manifest\.json$/, /LICENSE/],
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
        // /////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // // To get birdseye to be included in precaching ... This might work ...
        // /////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // include: [
        //   // NOT SURE IF THIS IS ACTUALLY WORKING... Intention is to get all contents of "./public/",
        //   // including birdseye stuff and bootstrap stuff, to be part of `precacheAndRoute(self.__WB_MANIFEST)`
        //   // in service-worker.js. At time of writing, other options are Craco's defaults for WorkboxWebpackPlugin.
        //   /public\/.*/
        // ],
        // /////////////////////////////////////////////////////////////////////////////////////////////////////////////
      }),
    ],
  },

  // Staged for deletion -- the CORS headers override should not be needed as of recent commits in https://github.com/alexmojaki/futurecoder/pull/320
  // devServer: {
  //   headers: {
  //     'Cross-Origin-Opener-Policy': 'same-origin',
  //     'Cross-Origin-Embedder-Policy': 'require-corp',
  //   },
  // },
};
