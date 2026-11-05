(function () {
  'use strict';
  const R = window.ColdChainRuntime;
  const listeners = new Set();
  const store = { active: null, revision: 0, run: 0 };
  store.subscribe = fn => { listeners.add(fn); return () => listeners.delete(fn); };
  function emit() { store.revision++; for (const fn of listeners) fn(store.active); }
  store.reset = () => { store.run++; store.active = null; emit(); };
  store.activate = (dataset, filename, options = {}) => {
    if (dataset.kind === 'regression') return; // Research inputs do not replace inventory.
    store.run++;
    store.active = { dataset, filename, historyComplete: options.historyComplete === true, predictions: {}, errors: {}, progress: 'Local calculations complete. Model inference not run.', busy: false };
    emit();
  };
  store.attachInventory = (inventory, filename) => {
    const a = store.active;
    if (!a || a.dataset.kind !== 'sensor' || inventory.kind !== 'inventory') throw Error('Load sensor data before attaching inventory.');
    const ids = new Set();
    for (const row of inventory.rows) {
      if (!a.dataset.batches[row.Batch_ID]) throw Error('Inventory batch has no sensor history: ' + row.Batch_ID);
      if (ids.has(row.Batch_ID)) throw Error('Each sensor batch must map to exactly one inventory product.');
      ids.add(row.Batch_ID);
    }
    a.dataset.inventory = inventory; a.dataset.inventoryFilename = filename;
    emit();
  };
  store.refresh = emit;
  function alerts() {
    const a = store.active; if (!a || a.dataset.kind !== 'sensor') return [];
    const out = [];
    for (const [id, rows] of Object.entries(a.dataset.batches)) {
      const last = rows.at(-1), t = last.calibrated_temp;
      if (t < 2 || t > 8) out.push({ id: id + ':observed', batch: id, type: 'Observed excursion', severity: 'Critical', time: last.Timestamp,
        detail: `Latest temperature ${t.toFixed(2)}°C is outside [2,8]°C. This is an observation, not a forecast.` });
      for (const p of a.predictions[id]?.result || []) {
        if (p.alert === true || p.alert === 1) out.push({ id: id + ':' + p.task, batch: id, type: 'Model alert', severity: 'Warning', time: last.Timestamp,
          detail: `${p.task}: p_cal=${p.p_cal ?? 'N/A'}, threshold=${p.threshold ?? 'N/A'}, status=${p.status}` });
      }
    }
    return out;
  }
  store.alerts = alerts;
  store.batchRows = () => {
    const a = store.active; if (!a) return [];
    if (a.dataset.kind === 'inventory') return a.dataset.rows.map(x => ({ ...x, id: x.Batch_ID, workflowKey: JSON.stringify([x.Product_ID,x.Batch_ID]), product: x.Product_Name || x.Product_ID, temp: 'N/A', risk: 'Unknown', status: 'Awaiting approval', shelf: 'N/A', source: 'uploaded' }));
    return Object.entries(a.dataset.batches).map(([id, rows]) => {
      const last = rows.at(-1), outside = rows.filter(x => x.calibrated_temp < 2 || x.calibrated_temp > 8).length;
      let min = Infinity, max = -Infinity; for (const r of rows) { min = Math.min(min,r.calibrated_temp); max = Math.max(max,r.calibrated_temp); }
      const inventory = a.dataset.inventory?.rows.find(x => x.Batch_ID === id);
      return { ...(inventory || {}), id, workflowKey: inventory ? JSON.stringify([inventory.Product_ID,id]) : id, product: inventory ? inventory.Product_Name || inventory.Product_ID : 'Not supplied', temp: `${last.calibrated_temp.toFixed(2)}°C`, current: last.calibrated_temp, min, max, outside, readings: rows.length,
        observedAt: last.Timestamp, risk: last.calibrated_temp < 2 || last.calibrated_temp > 8 ? 'High' : 'Unknown', status: 'Awaiting approval', source: 'uploaded' };
    });
  };
  store.record = (id, data) => {
    if (!store.active?.dataset.batches?.[id]) return;
    store.active.predictions[id] = data; delete store.active.errors[id]; emit();
  };
  store.runModels = async () => {
    const a = store.active; if (!a || a.dataset.kind !== 'sensor') return;
    if (!a.historyComplete) { a.progress='Local calculations complete. Confirm complete batch histories before running the model; partial tails are not accepted by the backend.'; emit(); return; }
    const token = ++store.run; a.busy = true; a.errors = {}; a.predictions = {}; emit();
    const batches = Object.entries(a.dataset.batches);
    for (let i = 0; i < batches.length; i++) {
      if (token !== store.run) return;
      const [id, rows] = batches[i]; a.progress = `Running model for batch ${i+1}/${batches.length}: ${id}`; emit();
      try {
        if (rows.length > 100000) throw Error('Batch exceeds the model limit of 100,000 readings.');
        for (let j=1;j<rows.length;j++) if (R.timeKey(rows[j].Timestamp)-R.timeKey(rows[j-1].Timestamp)!==3600000000000n)
          throw Error('Model inference requires consecutive hourly readings. Missing or irregular hours must be resolved explicitly.');
        const readings = rows.map(x=>({...x,Timestamp:R.modelTimestamp(x.Timestamp,false)}));
        const base = (window.__COLDCHAIN_CONFIG__?.apiBaseUrl || '').replace(/\/+$/,'');
        const data = await R.jsonFetch(base+'/predict', { readings, operating_point:'precision50', tasks:['w1_6','w1_12','w1_24'], history_complete:a.historyComplete });
        if (data.success !== true || !Array.isArray(data.result)) throw Error('The model returned an invalid response.');
        for (const task of ['w1_6','w1_12','w1_24']) {
          const p = data.result.find(p=>p.Batch_ID===id && p.task===task);
          if (!p || (p.p_cal != null && (typeof p.p_cal!=='number' || !Number.isFinite(p.p_cal) || p.p_cal<0 || p.p_cal>1))) throw Error('Missing or invalid batch/task model result.');
        }
        if (token !== store.run) return;
        a.predictions[id] = data;
      } catch (e) { if (token !== store.run) return; a.errors[id] = e.message; }
      emit();
    }
    if (token !== store.run) return;
    a.busy = false; a.progress = `Model run complete: ${Object.keys(a.predictions).length}/${batches.length} batches succeeded; ${Object.keys(a.errors).length} failed.`; emit();
  };
  store.cancel = () => { store.run++; if(store.active){store.active.busy=false;store.active.progress='Model run cancelled. Completed results retained.';emit();} };
  function download(name, data) {
    const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
    const el=document.createElement('a');el.href=url;el.download=name;el.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function Banner({React}) {
    const h=React.createElement, [,update]=React.useState(0);React.useEffect(()=>store.subscribe(()=>update(x=>x+1)),[]);
    const a=store.active;if(!a)return null;
    return h('section',{className:'cc-panel cc-active-source','data-testid':'active-dataset-banner'},
      h('strong',null,`Uploaded dataset: ${a.filename}`),h('p',null,`${a.dataset.count.toLocaleString('en-US')} rows · ${a.dataset.kind} · session only. Historical/demo polling is paused.`),
      h('p',null,a.progress),a.dataset.kind==='sensor'&&h('p',null,'Sensor histories are sent to the configured backend when automatic inference is enabled and complete history is confirmed. precision50 · 6/12/24 hours.'),
      a.dataset.kind==='sensor'&&h('label',{className:'cc-check'},h('input',{type:'checkbox',checked:a.historyComplete,disabled:a.busy,onChange:e=>{a.historyComplete=e.target.checked;if(!a.historyComplete){a.predictions={};a.errors={};}emit();}}),'I confirm that every uploaded sensor series contains the complete batch history required by the model'),
      a.dataset.warnings?.map((text,i)=>h('p',{key:i,className:'cc-warning'},text)),
      h('div',{className:'cc-actions'},a.dataset.kind==='sensor'&&h('button',{className:'cc-button',disabled:a.busy||!a.historyComplete,onClick:store.runModels},'Run models for all batches'),
        a.busy&&h('button',{className:'cc-button',onClick:store.cancel},'Cancel model run'),
        h('button',{className:'cc-button',onClick:store.reset},'Return to historical/demo data')));
  }
  function Views({React,page,role,onOpen}) {
    const h=React.createElement, [,update]=React.useState(0),[selected,setSelected]=React.useState(''),[search,setSearch]=React.useState(''),[limit,setLimit]=React.useState(50);
    React.useEffect(()=>store.subscribe(()=>{update(x=>x+1);setLimit(50);setSelected('');}),[]);
    const a=store.active;if(!a)return null;
    const batches=store.batchRows(), allAlerts=alerts(), sensor=a.dataset.kind==='sensor';
    const table=(headers,rows)=>h('div',{className:'cc-table-wrap'},h('table',null,h('thead',null,h('tr',null,headers.map(x=>h('th',{key:x},x)))),h('tbody',null,rows.map((row,i)=>h('tr',{key:i},row.map((v,j)=>h('td',{key:j},v??'N/A')))))));
    const card=(title,value)=>h('div',{className:'cc-metric'},h('span',null,title),h('strong',null,value));
    const id=a.dataset.batches?.[selected]?selected:Object.keys(a.dataset.batches||{})[0], history=a.dataset.batches?.[id]||[];
    const shown=batches.filter(b=>`${b.id} ${b.product}`.toLowerCase().includes(search.toLowerCase()));
    return h('div',{className:'cc-workbench','data-testid':'uploaded-'+page},h('h2',null,{dashboard:'Uploaded dataset overview',batches:'Uploaded batches',alerts:'Computed dataset alerts',reports:'Dataset results and export'}[page]),
      ['dashboard','batches'].includes(page)&&window.ColdChainWorkflow&&h(window.ColdChainWorkflow.Panel,{React,role,onOpen}),
      page==='alerts'&&window.ColdChainWorkflow&&h(window.ColdChainWorkflow.Alerts,{React,role,alerts:allAlerts,onOpen}),
      h('p',null,'All values below come from the active upload. Missing inventory facts remain unavailable. Model forecasts are separate from observed excursions.'),
      h('div',{className:'cc-metrics'},card('Batches / inventory rows',batches.length),card('Input rows',a.dataset.count),card('Latest-reading excursions',sensor?batches.filter(b=>b.current<2||b.current>8).length:'N/A'),card('Active alerts',allAlerts.length)),
      page==='alerts'?h(React.Fragment,null,table(['Batch','Type','Severity','Observed at','Details'],allAlerts.slice(0,limit).map(x=>[x.batch,x.type,x.severity,x.time,x.detail])),allAlerts.length===0&&h('p',null,sensor?'No current observed or returned model alerts. Unrun or failed predictions are not counted as safe.':'No sensor data supplied; temperature and prediction alerts are unavailable.')):
      page==='reports'?h(React.Fragment,null,h('p',null,'Export contains source identity, calculated batch summaries, FEFO where supplied, actual model responses, errors, import warnings and session workflow decisions. It is not a compliance certificate.'),h('button',{className:'cc-button',onClick:()=>download('uploaded-dataset-results.json',{filename:a.filename,kind:a.dataset.kind,input_rows:a.dataset.count,batches,alerts:allAlerts,predictions:a.predictions,research:a.researchState?.data,inventory:a.dataset.inventory,errors:a.errors,warnings:a.dataset.warnings,workflow:window.ColdChainWorkflow?{decisions:window.ColdChainWorkflow.store.decisions,audit:window.ColdChainWorkflow.store.audit,acknowledgements:window.ColdChainWorkflow.store.acknowledgements}:null})},'Download dataset results JSON')):
      h(React.Fragment,null,h('input',{'aria-label':'Search uploaded batches',placeholder:'Search uploaded batches',value:search,onChange:e=>{setSearch(e.target.value);setLimit(50);}}),
        sensor?table(['Batch','Latest °C','Min °C','Max °C','Readings','Outside [2,8]°C','Latest time'],shown.slice(0,limit).map(b=>[b.id,b.current.toFixed(2),b.min.toFixed(2),b.max.toFixed(2),b.readings,b.outside,b.observedAt])):
        table(['Product','Batch','Dynamic expiry','FEFO rank'],shown.slice(0,limit).map(b=>[b.product,b.id,b.Dynamic_Expiry_Date,b.FEFO_Rank])),
        h('p',null,'Outside-range counts are numbers of readings, not durations. FEFO requires supplied product IDs and expiry dates; temperature alone does not establish shelf life.')),
      (shown.length>limit||allAlerts.length>limit)&&h('button',{className:'cc-button',onClick:()=>setLimit(n=>n+50)},'Show 50 more'),
      sensor&&page!=='reports'&&h('section',{className:'cc-panel'},h('h3',null,'Batch history and model results'),
        h('select',{'aria-label':'Uploaded batch history',value:id,onChange:e=>setSelected(e.target.value)},Object.keys(a.dataset.batches).map(x=>h('option',{key:x,value:x},x))),
        h('p',null,`Showing the last ${Math.min(500,history.length)} readings for ${id}.`),
        h('svg',{viewBox:'0 0 800 180',role:'img','aria-label':'Uploaded temperature history',style:{width:'100%',height:180}},h('polyline',{points:(()=>{const p=history.slice(-500);let lo=2,hi=8;for(const x of p){lo=Math.min(lo,x.calibrated_temp);hi=Math.max(hi,x.calibrated_temp);}return p.map((x,i)=>`${i*800/Math.max(1,p.length-1)},${160-(x.calibrated_temp-lo)*140/(hi-lo||1)}`).join(' ');})(),fill:'none',stroke:'#087f8c',strokeWidth:2})),
        a.errors[id]&&h('p',{className:'cc-error'},a.errors[id]),
        a.predictions[id]?table(['Task','Model/version','p_cal','Threshold','Status','Alert'],a.predictions[id].result.map(p=>[p.task,`${p.model} / ${a.predictions[id].model_version}`,p.p_cal,p.threshold,p.status,String(p.alert??'N/A')])):h('p',null,'No successful model result for this batch.')));
  }
  window.ColdChainDataset={store,Banner,Views};
})();
