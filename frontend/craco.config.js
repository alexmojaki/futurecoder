const path = require('path');

module.exports = {
  // Output to ./course (instead of ./build)
  webpack: {
    configure: (webpackConfig, {env, paths}) => {
      paths.appBuild = webpackConfig.output.path = path.resolve('course');
      return webpackConfig;
    },
  },
};
