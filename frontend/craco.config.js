const path = require('path');

module.exports = {
  devServer: {
    headers: {
      'Cross-Origin-Opener-Policy'  : 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
    },
  },
  // XXX: Here's how to make craco output to ./course instead of ./build.
  // webpack  : {
  //   configure: (webpackConfig, {env, paths}) => {
  //     paths.appBuild = webpackConfig.output.path = path.resolve('course');
  //     return webpackConfig;
  //   },
  // },
};
