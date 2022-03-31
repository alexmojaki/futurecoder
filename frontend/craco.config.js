const path = require('path');

module.exports = {
  // Output to ./course (instead of ./build)
  webpack: {
    configure: (webpackConfig, {env, paths}) => {
      paths.appBuild = webpackConfig.output.path = path.resolve('course');
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
