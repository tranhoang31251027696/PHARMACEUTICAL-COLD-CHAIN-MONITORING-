(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ColdChainRuntime = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const MAX_ROWS = 500000;
  const aliases = {
    id: ['id', 'row_id', 'observation_id'], label: ['y', 'label', 'ground_truth'],
    old: ['old_score', 'reference_score', 'score_old'], actual: ['new_score', 'actual_score', 'score_new'],
    time: ['timestamp', 'time', 'datetime', 'date', 'reading_time'],
    temp: ['calibrated_temp', 'actual_temp', 'temperature', 'temp'],
    humidity: ['humidity', 'rh', 'hum'], batch: ['batch_id', 'batch', 'batchid'],
    mode: ['shipment_mode', 'mode', 'transport'], offset: ['calibration_offset_pct', 'offset']
  };
  function delimiter(text) {
    const counts = { ',': 0, ';': 0, '\t': 0 }; let quoted = false;
    for (let i = 0; i < text.length && i < 100000; i++) {
      const c = text[i];
      if (c === '"') { if (quoted && text[i + 1] === '"') i++; else quoted = !quoted; }
      else if (!quoted && (c === '\n' || c === '\r')) break;
      else if (!quoted && Object.prototype.hasOwnProperty.call(counts, c)) counts[c]++;
    }
    return Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
  }
  function parseCSV(text) {
    if (typeof text !== 'string' || !text.trim()) throw Error('The CSV is empty.');
    text = text.replace(/^\uFEFF/, '');
    const sep = delimiter(text), rows = []; let row = [], field = '', quoted = false, closed = false;
    function cell() { row.push(field.trim()); field = ''; closed = false; }
    function record() {
      cell(); if (row.some(v => v !== '')) rows.push(row); row = [];
      if (rows.length > MAX_ROWS + 1) throw Error('The CSV exceeds the 500,000-row limit.');
    }
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else { quoted = false; closed = true; } }
        else field += c;
      } else if (c === sep) cell();
      else if (c === '\r' || c === '\n') { record(); if (c === '\r' && text[i + 1] === '\n') i++; }
      else if (c === '"') {
        if (field.trim() || closed) throw Error('Invalid CSV quotation mark.');
        field = ''; quoted = true;
      } else if (closed) { if (!/\s/.test(c)) throw Error('Unexpected characters after a closing CSV quote.'); }
      else field += c;
    }
    if (quoted) throw Error('The CSV has an unclosed quoted field.');
    if (field || row.length || closed) record();
    if (rows.length < 2) throw Error('The CSV requires a header and at least one data row.');
    const headers = rows.shift();
    if (headers.some(h => !h) || new Set(headers.map(h => h.toLowerCase())).size !== headers.length)
      throw Error('Column names must be nonempty and unique.');
    rows.forEach((r, i) => { if (r.length !== headers.length) throw Error(`Record ${i + 2}: found ${r.length} cells; expected ${headers.length}.`); });
    return { headers, rows, delimiter: sep };
  }
  function number(value, name) {
    if (value === '' || value == null || !Number.isFinite(Number(value))) throw Error(`${name}: a finite, nonempty number is required.`);
    return Number(value);
  }
  function timeKey(value) {
    const m = String(value).trim().match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,9}))?)?)?(Z|[+-]\d{2}:\d{2})?$/);
    if (!m) throw Error(`Invalid timestamp: ${value}. Use YYYY-MM-DD HH:mm:ss or ISO 8601.`);
    const year = +m[1], month = +m[2], day = +m[3], hour = +(m[4] || 0), minute = +(m[5] || 0), second = +(m[6] || 0);
    if (month < 1 || month > 12 || day < 1 || day > new Date(Date.UTC(year, month, 0)).getUTCDate() || hour > 23 || minute > 59 || second > 59)
      throw Error(`Invalid date or time: ${value}`);
    const zone = m[8] || 'Z';
    const ms = Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}${zone}`);
    if (!Number.isFinite(ms)) throw Error(`Invalid timezone: ${value}`);
    return BigInt(ms) * 1000000n + BigInt((m[7] || '').padEnd(9, '0'));
  }
  function normalize(text, options = {}) {
    if (/Note:\s*All Date-Time values are in:\s*UTC\s*\+05:45/i.test(text)) {
      const readings = [], seen = new Set();
      for (const raw of text.replace(/^\uFEFF/, '').split(/[\r\n]+/)) {
        if (!raw.trim() || /^Note:/i.test(raw.trim())) continue;
        const cells = raw.split(',').map(x=>x.trim());
        if (!/^\d+$/.test(cells[0]) || !/^\d{4}-\d{2}-\d{2}$/.test(cells[1]||'') || !/^\d{2}:\d{2}:\d{2}$/.test(cells[2]||''))
          throw Error('Unsupported Nepal logger row. Expected index, YYYY-MM-DD, HH:mm:ss, temperature.');
        const stamp=cells[1]+' '+cells[2], key=timeKey(stamp);
        if(seen.has(String(key))) throw Error('Duplicate Nepal logger timestamp: '+stamp);
        const temp=number(cells[3],'Nepal temperature');
        if(temp<=-273.15||Math.abs(temp)>1000)throw Error('Invalid Nepal temperature before hourly aggregation.');
        if(cells.slice(4).some(x=>x!==''))throw Error('Unexpected extra Nepal logger values.');
        seen.add(String(key));readings.push({stamp,key,temp});
        if(readings.length>MAX_ROWS) throw Error('The logger exceeds the 500,000-row limit.');
      }
      readings.sort((a,b)=>a.key<b.key?-1:1);
      const bins = new Map();
      for(const row of readings){const hour=row.stamp.slice(0,13)+':00:00';if(!bins.has(hour))bins.set(hour,[]);bins.get(hour).push(row);}
      const id='NEPAL-'+String(options.uploadName||'LOGGER').replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,120);
      const lines=['Batch_ID,Timestamp,Temperature'];let discarded=0;
      for(const [hour,rows] of bins){
        if(rows.length!==6 || rows.some((x,i)=>i>0&&x.key-rows[i-1].key!==600000000000n)){discarded+=rows.length;continue;}
        lines.push(`${id},${hour},${rows.reduce((sum,x)=>sum+x.temp,0)/rows.length}`);
      }
      if(lines.length<2) throw Error('No complete hourly bins: Nepal import requires six consecutive 10-minute readings per hour.');
      const result=normalize(lines.join('\n'),options);
      result.warnings.unshift(`Nepal logger import: ${readings.length} raw readings → ${result.count} complete hourly means; ${discarded} readings in incomplete/irregular hourly bins excluded. Missing hours are not interpolated.`,
        'Source clock: Nepal UTC+05:45, retained as local wall time for the model. Logger ID is a series identifier, not a verified shipment batch. Hourly means may hide short excursions; model validity on Nepal is not established.');
      result.provenance={format:'Nepal logger CSV',timezone:'UTC+05:45',aggregation:'hourly mean, six consecutive 10-minute samples per bin',raw_rows:readings.length,excluded_rows:discarded};
      return result;
    }
    const csv = parseCSV(text), lower = csv.headers.map(h => h.toLowerCase());
    function find(keys) { for (const k of keys) { const i = lower.indexOf(k); if (i >= 0) return i; } return -1; }
    const at = key => find(aliases[key]);
    const warnings = new Set();
    if (at('old') >= 0 && at('actual') >= 0 && at('label') >= 0) {
      if (at('id') < 0) throw Error('Regression CSV requires id, y, old_score, new_score.');
      if (csv.rows.length > 2000) throw Error('Independent verification is limited to 2,000 observations per request.');
      const ids = [], labels = [], old = [], actual = [], newIds = []; const ni = find(['new_id', 'actual_id']);
      csv.rows.forEach((r, i) => {
        if (!r[at('id')]) throw Error(`Record ${i + 2}: missing ID.`);
        if (!['0', '1'].includes(r[at('label')])) throw Error(`Record ${i + 2}: y must be 0 or 1.`);
        ids.push(r[at('id')]); labels.push(+r[at('label')]);
        old.push(number(r[at('old')], 'old_score')); actual.push(number(r[at('actual')], 'new_score'));
        newIds.push(ni >= 0 ? r[ni] : r[at('id')]);
      });
      if (new Set(ids).size !== ids.length) throw Error('Duplicate observation IDs.');
      if (newIds.some((id, i) => id !== ids[i])) throw Error('Old/new IDs are not aligned in the same order.');
      const modelNames = ['reference_model', 'comparison_model'].map(column => {
        const index = find([column]);
        if (index < 0) return null;
        const names = new Set(csv.rows.map(row => row[index].trim()));
        if (names.size !== 1 || names.has('')) throw Error(column + ' must name the same model on every row.');
        return [...names][0];
      });
      return { kind: 'regression', count: ids.length, modelNames,
        payload: { labels, reference_scores: old, actual_scores: actual, ids, new_ids: newIds }, warnings: [] };
    }
    const product = find(['product_id']), expiry = find(['dynamic_expiry_date']);
    if (product >= 0 && expiry >= 0) {
      const batch = at('batch'); if (batch < 0) throw Error('FEFO CSV requires Batch_ID.');
      const seen = new Set(); const entries = csv.rows.map((r, i) => {
        if (!r[product] || !r[batch] || !r[expiry]) throw Error(`Record ${i + 2}: missing Product_ID, Batch_ID or Dynamic_Expiry_Date.`);
        const key = JSON.stringify([r[product], r[batch]]);
        if (seen.has(key)) throw Error('FEFO requires one inventory row per Product_ID/Batch_ID. Sensor streams cannot be used as inventory.');
        seen.add(key); return { values: Object.fromEntries(csv.headers.map((h, j) => [h, r[j]])), product: r[product], batch: r[batch], expiry: timeKey(r[expiry]) };
      });
      entries.sort((a, b) => a.product.localeCompare(b.product) || (a.expiry < b.expiry ? -1 : a.expiry > b.expiry ? 1 : a.batch.localeCompare(b.batch)));
      let lastProduct = null, lastExpiry = null, rank = 0;
      const productName = find(['product_name']);
      const rows = entries.map(e => {
        if (lastProduct !== e.product) { rank = 0; lastExpiry = null; }
        if (lastExpiry !== e.expiry) rank++;
        lastProduct = e.product; lastExpiry = e.expiry;
        return { ...e.values, Product_ID: e.product, Batch_ID: e.batch,
          Dynamic_Expiry_Date: e.values[csv.headers[expiry]],
          ...(productName >= 0 ? { Product_Name: e.values[csv.headers[productName]] } : {}), FEFO_Rank: rank };
      });
      return { kind: 'inventory', count: rows.length, rows, warnings: ['FEFO ranks within each Product_ID using the supplied Dynamic_Expiry_Date; it does not predict expiry from temperature.'] };
    }
    if (at('time') < 0 || at('temp') < 0) throw Error('Sensor CSV requires Timestamp and calibrated_temp / actual_temp / Temperature. Alternatively, use a regression or FEFO schema.');
    const batches = Object.create(null), seen = new Map();
    csv.rows.forEach((r, i) => {
      const line = i + 2, id = at('batch') >= 0 ? r[at('batch')] : 'UPLOADED-BATCH';
      if (!id) throw Error(`Record ${line}: Batch_ID is empty.`);
      const timestamp = r[at('time')]; const key = timeKey(timestamp);
      if (!seen.has(id)) seen.set(id, new Set());
      if (seen.get(id).has(String(key))) throw Error(`Duplicate timestamp in ${id}: ${timestamp}`);
      seen.get(id).add(String(key));
      let temp = number(r[at('temp')], `Temperature at record ${line}`);
      if (temp <= -273.15 || Math.abs(temp) > 1000) throw Error(`Invalid temperature at record ${line}.`);
      if (lower[at('temp')] === 'temperature' && at('offset') >= 0 && r[at('offset')] !== '') {
        if (options.applyOffset) temp *= 1 - number(r[at('offset')], 'Calibration_Offset_Pct') / 100;
        else warnings.add('Calibration_Offset_Pct is present but has not been applied. Using Temperature as supplied in the CSV.');
      }
      if (!Number.isFinite(temp) || temp <= -273.15 || Math.abs(temp) > 1000) throw Error(`Invalid adjusted temperature at record ${line}.`);
      const humidityCell = at('humidity') >= 0 ? r[at('humidity')] : '';
      const humidity = number(humidityCell === '' ? options.defaultHumidity : humidityCell, `Humidity at record ${line}`);
      if (humidity < 0 || humidity > 100) throw Error(`Humidity at record ${line} must be within [0,100].`);
      if (humidityCell === '') warnings.add(`Missing humidity: using ${options.defaultHumidity} from the import form.`);
      const modeCell = at('mode') >= 0 ? r[at('mode')] : '';
      const mode = modeCell || options.defaultShipment;
      if (typeof mode !== 'string' || !mode.trim()) throw Error('Missing Shipment_Mode. Select a default in the import form.');
      if (!modeCell) warnings.add(`Missing Shipment_Mode: using ${mode} from the import form.`);
      if (at('batch') < 0) warnings.add('No Batch_ID column: using UPLOADED-BATCH for a single batch.');
      if (!batches[id]) batches[id] = [];
      batches[id].push({ Batch_ID: id, Timestamp: timestamp, calibrated_temp: temp, Humidity: humidity, Shipment_Mode: mode.trim() });
    });
    for (const rows of Object.values(batches)) rows.sort((a, b) => timeKey(a.Timestamp) < timeKey(b.Timestamp) ? -1 : 1);
    return { kind: 'sensor', count: csv.rows.length, batches, warnings: [...warnings] };
  }
  function arrhenius(temp) {
    const kelvin = number(temp, 'Temperature') + 273.15;
    if (kelvin <= 0) throw Error('Temperature is at or below absolute zero.');
    const exponent = 51044.8 / 8.31446261815324 * (1 / 278.15 - 1 / kelvin);
    const ratio = Math.exp(Math.max(-50, Math.min(50, exponent)));
    return { ratio, excessDaysPerHour: Math.max(ratio - 1, 0) / 24, clamped: Math.abs(exponent) > 50 };
  }
  function modelTimestamp(value, convertAwareToUTC) {
    timeKey(value);
    if (/(Z|[+-]\d{2}:\d{2})$/.test(value)) {
      if (!convertAwareToUTC) throw Error('The model API requires timestamps without a timezone. Enable conversion to UTC-naive or normalize the CSV to the model timezone.');
      return new Date(Number(timeKey(value) / 1000000n)).toISOString().replace('T', ' ').replace(/Z$/, '');
    }
    return value.replace('T', ' ');
  }
  async function jsonFetch(url, body, timeout = 90000) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(url, { method: body === undefined ? 'GET' : 'POST',
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body), signal: controller.signal });
      if (!(response.headers.get('content-type') || '').includes('application/json')) throw Error('The API did not return JSON. Check the URL or launch start_ui.py.');
      const data = await response.json();
      if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data.error || `HTTP ${response.status}`));
      return data;
    } catch (e) { if (e.name === 'AbortError') throw Error('The API request timed out. No verified result is available.'); throw e; }
    finally { clearTimeout(timer); }
  }
  return { parseCSV, normalize, timeKey, number, arrhenius, modelTimestamp, jsonFetch, MAX_ROWS };
});
