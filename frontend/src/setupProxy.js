const {createProxyMiddleware} = require("http-proxy-middleware");

const routes = [
  "/accounts",
  "/home",
  "/toc",
  "/birdseye",
  "/admin",
  "/static_backend/",
  "/api"
];

module.exports = function(app) {
  routes.forEach(function(route) {
    app.use(createProxyMiddleware(route, { target: "http://localhost:8000/" }));
  });
};
