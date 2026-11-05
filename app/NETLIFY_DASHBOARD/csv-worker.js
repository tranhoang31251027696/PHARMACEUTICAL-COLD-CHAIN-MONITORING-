importScripts('./coldchain-runtime.js?v=20261105-real-regression');
self.onmessage = function (event) {
  try { self.postMessage({ ok: true, result: self.ColdChainRuntime.normalize(event.data.text, event.data.options) }); }
  catch (error) { self.postMessage({ ok: false, error: error.message }); }
};
