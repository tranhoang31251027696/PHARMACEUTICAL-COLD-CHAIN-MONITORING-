// Public endpoints only; local mode uses the same-origin Python proxy.
(function () {
  const remote = "https://coldchain-backend-jq65.onrender.com";
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(window.location.hostname);
  window.__COLDCHAIN_CONFIG__ = {
    apiBaseUrl: local ? window.location.origin : remote,
    researchApiBaseUrl: ""
  };
})();
