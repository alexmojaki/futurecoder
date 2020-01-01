const proxy = require("http-proxy-middleware");

const routes = [
  "/accounts",
  "/static_backend/",
  "/shell",
  "/admin",
  "/api"
];

module.exports = function(app) {
  routes.forEach(function(route) {
    app.use(proxy(route, { target: "http://localhost:8000/" }));
  });
};
