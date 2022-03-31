const path = require('path');

const WorkboxWebpackPlugin = require('workbox-webpack-plugin');

const isEnvProduction = process.env.NODE_ENV === "production"

module.exports = {
  webpack: {
    configure: (webpackConfig, {env, paths}) => {
      // Output to ./course (instead of ./build)
      paths.appBuild = webpackConfig.output.path = path.resolve('course');

      // Override config for WorkboxWebpackPlugin.{GenerateSW,InjectManifest}
      webpackConfig.plugins = webpackConfig.plugins.map(plugin => {
        if(plugin.constructor.name === 'InjectManifest') {
          console.info({plugin})
          return new WorkboxWebpackPlugin.InjectManifest({
            // At time of writing, the {exclude,maximumFileSize*,dontCacheBust*} arguments are the same as after "CRA eject",
            // and the swSrc/swDest arguments are (... or should be ...) equivalent.
            swSrc: './src/service-worker.js',
            swDest: 'service-worker.js',
            dontCacheBustURLsMatching: /\.[0-9a-f]{8}\./,
            exclude: [/\.map$/, /asset-manifest\.json$/, /LICENSE/],
            maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
            /////////////////////////////////////////////////////////////////////////////////////////////////////////////
            // To get birdseye to be included in precaching ... This might work ...
            /////////////////////////////////////////////////////////////////////////////////////////////////////////////
            include: [
              // NOT SURE IF THIS IS ACTUALLY WORKING... Intention is to get all contents of "./public/",
              // including birdseye stuff and bootstrap stuff, to be part of `precacheAndRoute(self.__WB_MANIFEST)`
              // in service-worker.js. At time of writing, other options are Craco's defaults for WorkboxWebpackPlugin.
              /public\/.*/
            ],
            /////////////////////////////////////////////////////////////////////////////////////////////////////////////
          })
        }

        return plugin
      })

      return webpackConfig;
    },
  },

  // Staged for deletion -- the CORS headers override should not be needed as of recent commits in https://github.com/alexmojaki/futurecoder/pull/320
  // devServer: {
  //   headers: {
  //     'Cross-Origin-Opener-Policy': 'same-origin',
  //     'Cross-Origin-Embedder-Policy': 'require-corp',
  //   },
  // },
};
