(function () {
  'use strict';
  function Workbench({ React, notify = () => {} }) {
    const R = window.ColdChainRuntime, h = React.createElement;
    const shared = window.ColdChainDataset.store;
    const initial = shared.active;
    const initialBatch = Object.keys(initial?.dataset.batches || {})[0] || '';
    const [dataset, setDataset] = React.useState(initial?.dataset || null), [filename, setFilename] = React.useState(initial?.filename || '');
    const [researchState, setResearchState] = React.useState(initial?.researchState || null);
    const [, refreshLinked] = React.useState(0);
    const [autoRun, setAutoRun] = React.useState(false);
    const [autoHistoryComplete, setAutoHistoryComplete] = React.useState(false);
    const [batch, setBatch] = React.useState(initialBatch), [cursor, setCursor] = React.useState(initial?.dataset.batches?.[initialBatch]?.length - 1 || 0), [task, setTask] = React.useState('w1_24');
    const [adjust, setAdjust] = React.useState(0), [complete, setComplete] = React.useState(false);
    const [convertAwareToUTC, setConvertAwareToUTC] = React.useState(false);
    const [readingOptions, setReadingOptions] = React.useState({ defaultShipment: 'Air', defaultHumidity: 60, applyOffset: false });
    const [parsing, setParsing] = React.useState(false), [busy, setBusy] = React.useState(false), [error, setError] = React.useState('');
    const [inference, setInference] = React.useState(null), [diagnostic, setDiagnostic] = React.useState(null);
    const [local, setLocal] = React.useState(null), [modelHealth, setModelHealth] = React.useState(null);
    const [lo, setLo] = React.useState('0.30'), [hi, setHi] = React.useState('0.90');
    const [oldPrecision, setOldPrecision] = React.useState('inclusive'), [newPrecision, setNewPrecision] = React.useState('inclusive');
    const [queryKind, setQueryKind] = React.useState('finite'), [values, setValues] = React.useState('0.50, 0.80, 0.90');
    const [queryLo, setQueryLo] = React.useState('0.30'), [queryHi, setQueryHi] = React.useState('0.90');
    const [leftClosed, setLeftClosed] = React.useState(true), [rightClosed, setRightClosed] = React.useState(true), [digits, setDigits] = React.useState(2);
    const [inventoryPage, setInventoryPage] = React.useState(0);
    const [scorePage, setScorePage] = React.useState(0);
    const generation = React.useRef(0), fileGeneration = React.useRef(0), lastText = React.useRef(null), workerRef = React.useRef(null);
    const remote = (window.__COLDCHAIN_CONFIG__?.apiBaseUrl || '').replace(/\/+$/, '');
    const researchRemote = (window.__COLDCHAIN_CONFIG__?.researchApiBaseUrl || '').replace(/\/+$/, '');
    const researchAvailable = !!(local?.regression_available || researchRemote);
    const rows = dataset?.kind === 'sensor' ? dataset.batches[batch] || [] : [];
    const research = dataset?.kind === 'regression' ? dataset : researchState?.dataset === dataset && researchState.batch === batch && researchState.cursor === cursor ? researchState.data : cursor === rows.length - 1 ? dataset?.researchByBatch?.[batch] : null;
    const inventory = dataset?.kind === 'inventory' ? dataset : dataset?.inventory;
    React.useEffect(() => shared.subscribe(() => refreshLinked(x => x + 1)), []);
    const current = rows[cursor], temp = current ? current.calibrated_temp + Number(adjust) : null;
    let thermal = null;
    try { if (temp != null && Number.isFinite(temp)) thermal = R.arrhenius(temp); } catch (_) { /* Invalid what-if temperature: no derived metric. */ }
    const stats = React.useMemo(() => {
      if (!rows.length) return null;
      return rows.reduce((a, x) => ({ min: Math.min(a.min, x.calibrated_temp), max: Math.max(a.max, x.calibrated_temp),
        sum: a.sum + x.calibrated_temp, excursions: a.excursions + (x.calibrated_temp < 2 || x.calibrated_temp > 8 ? 1 : 0) }),
      { min: Infinity, max: -Infinity, sum: 0, excursions: 0 });
    }, [dataset, batch]);
    React.useEffect(() => {
      let active = true;
      R.jsonFetch('/api/local-health', undefined, 3000).then(x => { if (active) setLocal(x.service === 'coldchain-local' ? x : null); }).catch(() => { if (active) setLocal(null); });
      if (remote) R.jsonFetch(remote + '/health', undefined, 90000).then(x => { if (active) setModelHealth(x); }).catch(() => { if (active) setModelHealth({ error: 'The backend has not responded. Results require a successful request.' }); });
      return () => { active = false; generation.current++; fileGeneration.current++; workerRef.current?.terminate(); };
    }, []);
    React.useEffect(() => { generation.current++; setInference(null); setBusy(false); setError(''); }, [dataset, batch, cursor, task, adjust, complete, convertAwareToUTC]);
    React.useEffect(() => { generation.current++; setDiagnostic(null); setBusy(false); }, [dataset, research, lo, hi, oldPrecision, newPrecision, queryKind, values, queryLo, queryHi, leftClosed, rightClosed, digits]);
    React.useEffect(() => { setScorePage(0); }, [dataset]);
    function fail(e) { setError(e.message || String(e)); }
    function download(name, data) {
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
      const a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
    async function readText(text, name) {
      const token = ++fileGeneration.current; generation.current++; setParsing(true); setError(''); setInference(null); setDiagnostic(null); setDataset(null);
      lastText.current = { text, name };
      workerRef.current?.terminate();
      try {
        const parsed = await new Promise((resolve, reject) => {
          const worker = new Worker(new URL('./csv-worker.js', document.baseURI)); workerRef.current = worker;
          worker.onmessage = event => { worker.terminate(); event.data.ok ? resolve(event.data.result) : reject(Error(event.data.error)); };
          worker.onerror = () => { worker.terminate(); reject(Error('The CSV worker could not start. Launch start_ui.py instead of opening the HTML file directly.')); };
          worker.postMessage({ text, options: { ...readingOptions, uploadName: name } });
        });
        if (token !== fileGeneration.current) return;
        lastText.current = { text, name }; setFilename(name); setDataset(parsed); setInventoryPage(0); setAdjust(0); setComplete(false);
        if (parsed.kind === 'sensor') { const key = Object.keys(parsed.batches)[0]; setBatch(key); setCursor(parsed.batches[key].length - 1); }
        if (parsed.kind !== 'regression') {
          shared.activate(parsed, name, { historyComplete: autoHistoryComplete });
          if (parsed.kind === 'sensor' && autoRun) shared.runModels();
        }
        return parsed;
      } catch (e) { if (token === fileGeneration.current) fail(e); }
      finally { if (token === fileGeneration.current) setParsing(false); }
    }
    async function upload(file) {
      if (!file) return;
      if (file.size > 75 * 1024 * 1024) return fail(Error('The file exceeds 75 MiB. Split or filter the data before uploading.'));
      await readText(await file.text(), file.name);
    }
    async function sample(name) {
      try {
        const response = await fetch(new URL('./samples/' + name, document.baseURI));
        if (!response.ok) throw Error('Could not load the sample file.');
        const text = await response.text();
        let inventorySample, paired;
        if (name.startsWith('sample_sensor_')) {
          const responses = await Promise.all(['sample_linked_inventory.csv','sample_linked_predictions.json'].map(n => fetch(new URL('./samples/' + n, document.baseURI))));
          if (responses.some(r => !r.ok)) throw Error('Could not load the linked sample package.');
          inventorySample = R.normalize(await responses[0].text());
          const cache = await responses[1].json();
          const bytes = new TextEncoder().encode(text);
          const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
          paired = cache[name];
          if (!paired || Object.values(paired).some(x=>x.live_prediction.sensor_file_sha256 !== hash)) throw Error('Stored scores do not match this sensor sample. Run both models on the uploaded sensor instead.');
        }
        const parsed = await readText(text, name + ' (linked sample)');
        if (parsed && paired && shared.active?.dataset === parsed) {
          const ids = new Set(Object.keys(parsed.batches));
          const subset = R.normalize(['Product_ID,Product_Name,Batch_ID,Dynamic_Expiry_Date', ...inventorySample.rows.filter(x=>ids.has(x.Batch_ID)).map(x=>[x.Product_ID,JSON.stringify(x.Product_Name),x.Batch_ID,x.Dynamic_Expiry_Date].join(','))].join('\n'));
          const matched = {};
          for (const [id, data] of Object.entries(paired)) {
            const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(parsed.batches[id]))))].map(x=>x.toString(16).padStart(2,'0')).join('');
            if (digest === data.normalized_sensor_sha256) matched[id] = data;
          }
          if (shared.active?.dataset !== parsed) return;
          parsed.researchByBatch = matched;
          shared.attachInventory(subset, 'sample_linked_inventory.csv');
          notify(Object.keys(matched).length === ids.size ? 'Linked sensor, inventory and saved paired scores loaded. Select a batch and verify in section 3.' : 'Sensor and inventory linked. Import options differ from the saved scores; run both XGBoost models to create matching scores.');
        }
      } catch (e) { fail(e); }
    }
    async function attachInventory(file) {
      if (!file) return;
      try {
        if (file.size > 75*1024*1024) throw Error('Inventory exceeds 75 MiB.');
        const data = R.normalize(await file.text());
        shared.attachInventory(data, file.name);
        notify('Inventory linked to the current sensor batches.');
      } catch(e) { fail(e); }
    }
    async function runInference() {
      const token = ++generation.current; setBusy(true); setError(''); setInference(null);
      try {
        if (!rows.length) throw Error('Upload a sensor CSV first.');
        const history = rows.slice(0, cursor + 1).map(x => ({ ...x, Timestamp: R.modelTimestamp(x.Timestamp, convertAwareToUTC) }));
        if (history.length > 100000) throw Error('The backend accepts up to 100,000 readings per request. Select a smaller data window.');
        if (!Number.isFinite(Number(adjust)) || Math.abs(Number(adjust)) > 30) throw Error('The temperature adjustment must be within [-30,30]°C.');
        history[history.length - 1].calibrated_temp += Number(adjust);
        if (history[history.length - 1].calibrated_temp <= -273.15 || Math.abs(history[history.length - 1].calibrated_temp) > 1000) throw Error('The adjusted temperature is invalid.');
        const base = local?.service === 'coldchain-local' ? '' : remote;
        if (!base && !local) throw Error('No model backend is configured.');
        const data = await R.jsonFetch(base + '/predict', { readings: history, operating_point: 'precision50', tasks: [task], history_complete: complete });
        const prediction = data.result?.find(x => x.task === task && x.Batch_ID === batch);
        if (data.success !== true || !prediction) throw Error('The backend did not return a result for the requested task and batch.');
        if (prediction.p_cal != null && (typeof prediction.p_cal !== 'number' || !Number.isFinite(prediction.p_cal) || prediction.p_cal < 0 || prediction.p_cal > 1)) throw Error('The backend returned an invalid p_cal value.');
        if (token === generation.current) setInference({ ...data, selected_prediction: prediction,
          request: { filename, batch, task, readings: history.length, adjusted_last_temperature: Number(adjust), history_complete: complete, operating_point: 'precision50', aware_timestamps_converted_to_UTC_naive: convertAwareToUTC } });
      } catch (e) { if (token === generation.current) fail(e); }
      finally { if (token === generation.current) setBusy(false); }
    }
    async function runLivePair() {
      const token = ++generation.current; setBusy(true); setError('');
      try {
        if (!local) throw Error('Start the local Python app to run both XGBoost models.');
        const history = rows.slice(0, cursor + 1).map(x => ({ ...x, Timestamp: R.modelTimestamp(x.Timestamp, convertAwareToUTC) }));
        const data = await R.jsonFetch('/api/live-model-pair', { readings: history, history_complete: complete }, 120000);
        if (token !== generation.current) return;
        const state = {dataset, batch, cursor, data};
        setResearchState(state);
        if (shared.active?.dataset === dataset) shared.active.researchState = state;
        setDiagnostic(null); setScorePage(0);
        notify('Both XGBoost models executed. Fresh paired scores are ready in section 3.');
      } catch(e) { if(token === generation.current) fail(e); }
      finally { if(token === generation.current) setBusy(false); }
    }
    function query() {
      if (queryKind === 'none') return undefined;
      if (queryKind === 'finite') return { semantics: 'rational', kind: 'finite', values: values.split(/[,;\s]+/).filter(Boolean) };
      return { semantics: 'rational', kind: queryKind, lo: queryLo, hi: queryHi, left_closed: leftClosed, right_closed: rightClosed,
        ...(queryKind === 'lattice' ? { decimal_places: Number(digits) } : {}) };
    }
    async function runRegression(wrapper) {
      const token = ++generation.current; setBusy(true); setError(''); setDiagnostic(null);
      try {
        if (!researchAvailable) throw Error('Run start_ui.py with NumPy installed, or configure researchApiBaseUrl for a deployed research API.');
        const body = wrapper || { ...research.payload, lo, hi, old_precision: oldPrecision, new_precision: newPrecision, query: query() };
        const data = await R.jsonFetch((local?.regression_available ? '' : researchRemote) + (wrapper ? '/api/check-certificate' : '/api/regression'), body);
        if (data.verified !== true || data.verification?.verified !== true) throw Error('The checker has not verified the result. No verdict is available.');
        if (token === generation.current) setDiagnostic(data);
      } catch (e) { if (token === generation.current) fail(e); }
      finally { if (token === generation.current) setBusy(false); }
    }
    async function loadCertificate(file) {
      if (!file) return;
      try {
        if (file.size > 20 * 1024 * 1024) throw Error('The certificate JSON exceeds 20 MiB.');
        await runRegression(JSON.parse(await file.text()));
      } catch (e) { fail(e); }
    }
    const button = (label, onClick, disabled = false, extra = {}) => h('button', { type: 'button', className: 'cc-button', onClick, disabled, ...extra }, label);
    const field = (label, value, setter, extra = {}) => h('label', { className: 'cc-field' }, h('span', null, label),
      h('input', { value, onChange: e => setter(e.target.value), ...extra }));
    const checkbox = (label, value, setter) => h('label', { className: 'cc-check' }, h('input', { type: 'checkbox', checked: value, onChange: e => setter(e.target.checked) }), label);
    const option = (value, label) => h('option', { value, key: value }, label);
    const select = (label, value, setter, options) => h('label', { className: 'cc-field' }, h('span', null, label), h('select', { value, 'aria-label': label, onChange: e => setter(e.target.value) }, options));
    const pre = object => h('pre', { className: 'cc-json' }, JSON.stringify(object, null, 2));
    const card = (label, value) => h('div', { className: 'cc-metric' }, h('span', null, label), h('strong', null, value));
    const table = (heads, data) => h('div', { className: 'cc-table-wrap' }, h('table', null,
      h('thead', null, h('tr', null, heads.map(x => h('th', { key: x }, x)))),
      h('tbody', null, data.map((row, i) => h('tr', { key: i }, row.map((v, j) => h('td', { key: j }, String(v ?? '—'))))))));
    let chart = null;
    if (rows.length) {
      const points = rows.slice(Math.max(0, cursor - 499), cursor + 1), low = Math.min(1, stats.min), high = Math.max(9, stats.max), range = high - low || 1;
      const y = t => 130 - (t - low) / range * 110;
      chart = h('figure', { className: 'cc-chart' }, h('svg', { viewBox: '0 0 800 150', role: 'img', 'aria-label': 'Observed CSV temperature' },
        h('rect', { x: 0, width: 800, y: y(8), height: y(2) - y(8), fill: '#143b38' }),
        h('polyline', { points: points.map((x, i) => `${i * 800 / Math.max(1, points.length - 1)},${y(x.calibrated_temp)}`).join(' '), fill: 'none', stroke: '#67e8c2', strokeWidth: 2 })),
        h('figcaption', null, `Last ${points.length} readings up to the selected position; the shaded band is [2,8]°C. These are CSV observations, not forecasts.`));
    }
    return h('div', { className: 'cc-workbench' },
      h('header', null, h('h1', null, 'Dataset & Research Workbench'), h('p', null, 'Upload your CSV · run backend inference · diagnose regression with an independent checker')),
      h('section', { className: 'cc-panel' }, h('h2', null, '1. Upload your dataset'),
        h('p', null, 'Load sensor once to keep its chart, linked inventory FEFO and regression together. Sensor samples include the matching data. For your own sensor file, attach inventory below and run both XGBoost models. Standalone inventory/regression CSV uploads are also supported.'),
        checkbox('Automatically run backend models for all sensor batches after upload (sends sensor histories to the configured model API)', autoRun, setAutoRun),
        checkbox('I confirm before upload that all sensor series contain complete batch histories (required for automatic model inference)', autoHistoryComplete, setAutoHistoryComplete),
        h('div', { className: 'cc-upload', onDragOver: e => e.preventDefault(), onDrop: e => { e.preventDefault(); upload(e.dataTransfer.files[0]).catch(fail); } },
          h('label', { htmlFor: 'cc-upload-file' }, 'Select a CSV/TSV file or drag and drop it here'),
          h('input', { id: 'cc-upload-file', type: 'file', accept: '.csv,.tsv,text/csv,text/tab-separated-values', onChange: e => { upload(e.target.files[0]).catch(fail); e.target.value = ''; } }),
          h('small', null, 'Up to 75 MiB / 500,000 rows. Supports commas, semicolons, tabs, empty cells and quoted fields.')),
        h('div', { className: 'cc-actions' }, button('Sensor sample 1 (1 batch)', () => sample('sample_sensor_BATCH-01004.csv'), parsing),
          button('Sensor sample 2 (3 batches)', () => sample('sample_sensor_multi_batch.csv'), parsing),
          button('Sensor sample 3 (positive events / divergent)', () => sample('sample_sensor_positive.csv'), parsing),
          button('FEFO for current batches', () => document.getElementById('cc-linked-fefo')?.scrollIntoView({behavior:'smooth'}), !inventory), button('Regression for current batch', () => document.getElementById('cc-linked-regression')?.scrollIntoView({behavior:'smooth'}), !research)),
        h('p', { className: 'cc-note' }, 'Sensor samples include matching inventory and saved scores computed by both XGBoost models on those same histories. FEFO and Regression buttons navigate within the current data; they do not load another sample. Fresh model execution is optional.'),
        h('details', null, h('summary', null, 'Sensor import options and supported schemas'),
          h('p', null, 'Sensor: Timestamp, calibrated_temp/actual_temp/Temperature, Humidity; Batch_ID and Shipment_Mode can use the defaults below. Regression: id,y,old_score,new_score. Inventory: Product_ID,Batch_ID,Dynamic_Expiry_Date. Missing numeric values are not converted to zero.'),
          h('div', { className: 'cc-fields' }, field('Shipment_Mode default if missing', readingOptions.defaultShipment, v => setReadingOptions({ ...readingOptions, defaultShipment: v })),
            field('Humidity default if missing (%)', readingOptions.defaultHumidity, v => setReadingOptions({ ...readingOptions, defaultHumidity: v }), { type: 'number', min: 0, max: 100 })),
          checkbox('For Temperature: apply Temperature × (1 − Calibration_Offset_Pct/100)', readingOptions.applyOffset, v => setReadingOptions({ ...readingOptions, applyOffset: v })),
          h('p', null, 'calibrated_temp/actual_temp remain as provided. Options apply when reading the file and do not validate compatibility with the model calibration profile.'),
          button('Reload file with current options', () => readText(lastText.current.text, lastText.current.name), parsing || !lastText.current)),
        parsing && h('p', { role: 'status' }, 'Reading and validating CSV in a worker…'),
        dataset && h('p', { className: 'cc-source', 'data-testid': 'dataset-summary' }, `${filename} · ${dataset.count.toLocaleString('en-US')} rows · type ${dataset.kind} · uploaded data, not the server demo`),
        dataset?.warnings?.map((x, i) => h('p', { className: 'cc-warning', key: i }, x))),
      error && h('div', { className: 'cc-error', role: 'alert', 'data-testid': 'workbench-error' }, error),
      (!dataset || dataset.kind === 'regression') && h('section', { className: 'cc-panel', 'data-testid': 'processing-guide' },
        h('h2', null, '2. Process your dataset'),
        h('p', null, dataset?.kind === 'regression'
          ? 'Regression labels and paired old/new scores are loaded. Continue to section 3 to select a policy domain and run verification. This dataset does not use sensor inference or FEFO ranking.'
          : 'Upload a file in section 1 or select a sample. Sensor CSVs display a chart and inference controls here. Inventory CSVs display a FEFO table. For regression CSVs, continue to section 3.')),
      dataset?.kind === 'sensor' && h('section', { className: 'cc-panel' }, h('h2', null, '2. Sensor analysis and backend inference'),
        h('div', { className: 'cc-fields' }, select('Batch', batch, key => { setBatch(key); setCursor(dataset.batches[key].length - 1); }, Object.keys(dataset.batches).map(x => option(x, `${x} · ${dataset.batches[x].length} readings`))),
          select('Backend forecast horizon', task, setTask, ['w1_6', 'w1_12', 'w1_24'].map(x => option(x, x.replace('w1_', '') + ' hours')))),
        h('p', null, 'Operating point: precision50, provided by the backend. Available horizons follow the model API. The response identifies the model used.'),
        h('label', { className: 'cc-field' }, `Position ${cursor + 1}/${rows.length} · ${current?.Timestamp || ''}`,
          h('input', { type: 'range', min: 0, max: Math.max(0, rows.length - 1), value: cursor, onChange: e => setCursor(+e.target.value), 'aria-label': 'Sensor cursor' })), chart,
        h('div', { className: 'cc-metrics' }, card('Temperature at cursor', temp == null ? '—' : temp.toFixed(3) + '°C'), card('Min / Max CSV', stats ? `${stats.min.toFixed(2)} / ${stats.max.toFixed(2)}°C` : '—'),
          card('Readings outside [2,8]°C', stats?.excursions ?? '—'), card('Arrhenius ratio', thermal ? thermal.ratio.toFixed(4) + '×' : '—')),
        h('p', null, 'Arrhenius is a descriptive calculation with Ea=51,044.8 J/mol and Tref=5°C. It does not certify product quality or authorize stock release.'),
        field('What-if adjustment at the last reading (°C)', adjust, v => setAdjust(v), { type: 'number', min: -30, max: 30, step: 0.1 }),
        checkbox('I confirm that the submitted history is complete for this batch', complete, setComplete),
        checkbox('Convert timezone-aware timestamps to UTC-naive for the API (source CSV unchanged)', convertAwareToUTC, setConvertAwareToUTC),
        h('p', { className: 'cc-note' }, 'The API requires source-local timestamps without a timezone. For ISO timestamps with Z or an offset, enable UTC conversion above or normalize them to the model timezone. Timezone information is not silently discarded.'),
        h('p', {className:'cc-note'}, 'Run both frozen research XGBoost models locally on this sensor history, then compare fresh scores in section 3. Labels are derived from future temperature excursions in this file; the last 9 hours are excluded. Requires complete hourly history. No model training is performed.'),
        button('Run two XGBoost models locally', runLivePair, busy || parsing || !complete || !local, {'data-testid':'run-live-pair'}),
        button(busy ? 'Running inference…' : 'Run backend inference', runInference, busy || parsing, { 'data-testid': 'run-inference' }),
        h('p', { className: 'cc-note' }, 'Click Run to send the selected batch history up to the cursor to the configured model backend. Failed requests do not produce substitute scores.'),
        inference ? h('div', { className: 'cc-result', 'data-testid': 'inference-result' }, h('h3', null, 'Backend result received'),
          h('div', { className: 'cc-metrics' }, card('Model / version', `${inference.selected_prediction.model} / ${inference.model_version}`),
            card('p_cal', inference.selected_prediction.p_cal == null ? 'Not applicable' : String(inference.selected_prediction.p_cal)),
            card('Threshold', inference.selected_prediction.threshold ?? 'Not applicable'), card('Status', inference.selected_prediction.status)),
          h('p', null, 'This is an inference result, not a selector-equivalence certificate.'), pre(inference), button('Download inference JSON', () => download('inference-result.json', inference)))
          : h('p', { className: 'cc-note' }, 'INFERENCE NOT RUN · no result for the current configuration.')),
      dataset?.kind === 'sensor' && h('section', {className:'cc-panel'}, h('h2',null,'Link inventory to these sensor batches'), h('p',null,'Attach Product_ID, Batch_ID and Dynamic_Expiry_Date for the same batches. Supplied expiry dates are retained; ranks cover only the attached inventory. This does not calculate dynamic expiry.'), h('input',{type:'file',accept:'.csv,.tsv',onChange:e=>{attachInventory(e.target.files[0]);e.target.value='';}})),
      inventory && h('section', { className: 'cc-panel', id:'cc-linked-fefo' }, h('h2', null, 'FEFO for current batches'),
        h('p', null, 'FEFO ranks only the attached inventory within each product using supplied expiry dates. The linked sample uses stored inventory snapshots; those dates are not recalculated from the selected sensor window or model scores.'),
        button('Download inventory JSON',()=>download('inventory-fefo.json',inventory)),
        table(['Product', 'Batch', 'Dynamic expiry', 'FEFO rank'], inventory.rows.slice(inventoryPage * 50, inventoryPage * 50 + 50).map(x => [`${x.Product_ID ?? x.product_id}${(x.Product_Name ?? x.product_name) ? " · " + (x.Product_Name ?? x.product_name) : ""}`, x.Batch_ID ?? x.batch_id, x.Dynamic_Expiry_Date ?? x.dynamic_expiry_date, x.FEFO_Rank])),
        h('div', { className: 'cc-actions' }, button('Previous page', () => setInventoryPage(x => x - 1), inventoryPage === 0),
          h('span', null, `Page ${inventoryPage + 1}/${Math.ceil(inventory.count / 50)}`), button('Next page', () => setInventoryPage(x => x + 1), (inventoryPage + 1) * 50 >= inventory.count))),
      h('section', { className: 'cc-panel', id:'cc-linked-regression' }, h('h2', null, '3. Exact Policy Regression Diagnosis'),
        dataset?.kind === 'sensor' && h('p', {className:'cc-source'}, `Same sensor source · batch ${batch} · history through ${current?.Timestamp || '—'}. FEFO above refers to these same batches. Regression checks alert selections, not expiry or FEFO order.`),
        research?.live_prediction && h('div', {'data-testid':'live-model-result'}, h('h3',null,'Paired XGBoost score provenance'), pre(research.live_prediction)),
        !!research && h('div', { 'data-testid': 'regression-models' },
          h('div', { className: 'cc-metrics' },
            card('Reference · old_score', research.modelNames?.[0] || 'Model name not supplied'),
            card('Comparison · new_score', research.modelNames?.[1] || 'Model name not supplied')),
          h('p', null, research.live_prediction ? research.live_prediction.source + '. Labels are derived from future excursions in this same sensor history.' : 'The CSV supplies paired model predictions. This step compares selected observation IDs; the model names describe the input columns. Each ID identifies one labeled observation.'),
          filename === 'sample_regression.csv (sample)' && h('p', { className: 'cc-note' },
            'Built-in sample: two trained feature variants for the same 6-hour task. The reference uses thermal-history features; the comparison adds Arrhenius features. Verification applies to this 2,000-row subset.',
            ' ', h('a', { href: './samples/sample_regression_provenance.json', target: '_blank', rel: 'noopener' }, 'View model artifacts, hashes and sampling method'))),
        !!research && h('div', { 'data-testid': 'regression-scores' },
          h('h3', null, 'Paired input scores'),
          h('div', {className:'cc-metrics'}, card('Observations', research.count), card('Positive labels y=1', research.payload.labels.reduce((a,b)=>a+b,0)), card('Negative labels y=0', research.payload.labels.filter(y=>y===0).length)),
          research.payload.labels.every(y=>y===0) && h('p',{className:'cc-note'},'No positive labels in this input. Under this selector contract both versions abstain; equivalence is not evidence of model quality.'),
          table(['Observation ID', 'Label y', 'Reference · old_score', 'Comparison · new_score'],
            research.payload.ids.slice(scorePage * 20, scorePage * 20 + 20).map((id, offset) => {
              const index = scorePage * 20 + offset;
              return [id, research.payload.labels[index], research.payload.reference_scores[index], research.payload.actual_scores[index]];
            })),
          h('div', { className: 'cc-actions' },
            button('Previous scores', () => setScorePage(page => page - 1), scorePage === 0),
            h('span', null, `Page ${scorePage + 1}/${Math.ceil(research.count / 20)} · ${research.count} observations`),
            button('Next scores', () => setScorePage(page => page + 1), (scorePage + 1) * 20 >= research.count))),
        h('p', null, 'Upload CSV columns id,y,old_score,new_score for the same observations and labels. Verification covers fixed inputs and declared selector contracts; it does not prove arbitrary program source code correct.'),
        h('p', { className: researchAvailable ? 'cc-source' : 'cc-warning' }, researchAvailable ? 'Verification API configured. A verdict is available only after independent checking.' : 'Verification API unavailable. Run start_ui.py with requirements-ui.txt installed. Static hosting alone cannot run the Python checker.'),
        h('div', { className: 'cc-fields' }, field('Policy domain lo (rational)', lo, setLo), field('Policy domain hi (rational)', hi, setHi),
          select('Reference precision', oldPrecision, setOldPrecision, [option('inclusive', '≥ alpha'), option('strict', '> alpha')]),
          select('Actual precision', newPrecision, setNewPrecision, [option('inclusive', '≥ alpha'), option('strict', '> alpha')])),
        h('div', { className: 'cc-fields' }, select('Allowed policy query', queryKind, setQueryKind, [option('finite', 'Finite set'), option('interval', 'Interval'), option('lattice', 'Decimal lattice'), option('none', 'No query')]),
          queryKind === 'finite' ? field('Policies, e.g. 1/2,0.8,0.9', values, setValues) : queryKind !== 'none' && h(React.Fragment, null,
            field('Query lo', queryLo, setQueryLo), field('Query hi', queryHi, setQueryHi), queryKind === 'lattice' && field('Decimal places', digits, setDigits, { type: 'number', min: 0, max: 12 }))),
        ['interval', 'lattice'].includes(queryKind) && h('div', { className: 'cc-actions' }, checkbox('Include left endpoint', leftClosed, setLeftClosed), checkbox('Include right endpoint', rightClosed, setRightClosed)),
        button(busy ? 'Verifying…' : 'Compare and verify independently', () => runRegression(), busy || parsing || !researchAvailable || !research, { 'data-testid': 'run-regression' }),
        h('label', { className: 'cc-field' }, 'Or recheck a downloaded certificate JSON (checker only)',
          h('input', { type: 'file', accept: '.json,application/json', onChange: e => { loadCertificate(e.target.files[0]); e.target.value = ''; }, disabled: busy || !researchAvailable })),
        diagnostic ? h('div', { className: 'cc-result', 'data-testid': 'regression-result' }, h('h3', null, `${diagnostic.status} · independent checker accepted`),
          h('div', { className: 'cc-metrics' }, card('PSC exact', diagnostic.certificate.psc_exact), card('Verified probes', diagnostic.verification.probes),
            card('Candidate counts old/new', diagnostic.certificate.candidate_counts.join(' / ')), card('Input SHA-256', diagnostic.certificate.input_sha256.slice(0, 16) + '…')),
          !diagnostic.certificate.equivalent && diagnostic.certificate.psc === 0 && h('p', { className: 'cc-warning' }, 'PSC=0 with pointwise divergence. The selectors are not equivalent.'),
          table(['Lo', 'Hi', 'Left closed', 'Right closed', 'Equal', 'Old selected', 'New selected', 'Witness ID', 'Witness label y', 'Reference · old_score', 'Comparison · new_score'],
            diagnostic.certificate.cells.slice(0, 100).map(c => {
              const index = diagnostic.download.ids.indexOf(c.witness?.row_id);
              return [c.lo, c.hi, c.left_closed, c.right_closed, c.equal, c.old_n, c.new_n, c.witness?.row_id,
                diagnostic.download.labels[index], diagnostic.download.reference_scores[index], diagnostic.download.actual_scores[index]];
            })),
          diagnostic.certificate.cells.length > 100 && h('p', null, 'Showing the first 100 cells. The downloaded JSON contains all cells.'),
          diagnostic.query_result && pre({ full_query: diagnostic.query_result, boolean_query: diagnostic.boolean_result }),
          button('Download certificate with inputs for rechecking', () => download('verified-policy-certificate.json', diagnostic.download)))
          : h('p', { className: 'cc-note' }, 'NOT RUN / UNVERIFIED · no verification result is available.')),
      h('footer', { className: 'cc-note' }, `Uploaded sensor/inventory data drives the app until you return to historical/demo data. Session data is cleared on reload and is not automatically approved or dispatched. Backend model: ${modelHealth?.model?.loaded ? modelHealth.model.artifact_name : 'status not confirmed'}.`));
  }
  window.ColdChainApp = { Workbench };
})();
