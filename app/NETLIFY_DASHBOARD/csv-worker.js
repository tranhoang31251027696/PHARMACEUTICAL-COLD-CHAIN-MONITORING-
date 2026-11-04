importScripts('./coldchain-runtime.js');
self.onmessage = function (event) {
  try { self.postMessage({ ok: true, result: self.ColdChainRuntime.normalize(event.data.text, event.data.options) }); }
  catch (error) { self.postMessage({ ok: false, error: error.message }); }
};
