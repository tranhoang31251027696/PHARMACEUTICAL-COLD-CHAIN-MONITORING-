(function () {
  'use strict';
  const listeners=new Set();
  const store={source:null,batches:[],decisions:Object.create(null),requests:Object.create(null),acknowledgements:Object.create(null),audit:[],revision:0};
  const key=b=>b.workflowKey||b.id;
  const publish=()=>{store.revision++;for(const fn of listeners)fn();};
  store.subscribe=fn=>{listeners.add(fn);return()=>listeners.delete(fn);};
  store.key=key;
  store.sync=(source,batches)=>{
    if(store.source!==source){store.source=source;store.decisions=Object.create(null);store.requests=Object.create(null);store.acknowledgements=Object.create(null);store.audit=[];}
    store.batches=batches;
    const allowed=new Set(batches.map(key));
    for(const id of Object.keys(store.decisions))if(!allowed.has(id))delete store.decisions[id];
    publish();
  };
  store.status=b=>store.decisions[key(b)]?.status||b.status||'Awaiting approval';
  function log(b,role,action,note,from,to){
    store.audit.push({sequence:store.audit.length+1,time:new Date().toISOString(),batch_id:b?.id??null,batch_key:b?key(b):null,role,action,note,from,to});
  }
  function find(id){const b=store.batches.find(b=>key(b)===id);if(!b)throw Error('This batch is no longer in the active dataset.');return b;}
  store.blocker=(b)=>{
    const product=b.Product_ID||b.productId,rank=Number(b.FEFO_Rank??b.fefoRank);
    if(!product||!Number.isFinite(rank))return null;
    return store.batches.find(x=>(x.Product_ID||x.productId)===product&&key(x)!==key(b)&&Number(x.FEFO_Rank??x.fefoRank)<rank&&['Approved','In queue'].includes(store.status(x)))||null;
  };
  store.transition=(id,target,role,note='')=>{
    const b=find(id),before=store.status(b);note=String(note).trim();
    const rules={qa:{Approved:['Awaiting approval'],Rejected:['Awaiting approval','Approved','In queue']},warehouse:{'In queue':['Approved'],Dispatched:['In queue']}};
    if(!rules[role]?.[target]?.includes(before))throw Error(`Cannot change ${before} to ${target} as ${role}. Refresh the batch status and use the permitted action.`);
    if(target==='Rejected'&&!note)throw Error('A rejection reason is required.');
    if(target==='Approved'&&b.risk==='High'&&!note)throw Error('A review note is required when approving a batch with an observed excursion.');
    if(role==='warehouse'){
      const earlier=store.blocker(b);if(earlier)throw Error(`FEFO: process approved batch ${earlier.id} first (same product, earlier expiry).`);
    }
    store.decisions[id]={status:target,note,role,time:new Date().toISOString()};
    log(b,role,target,note,before,target);publish();return target;
  };
  store.requestReview=(id,role)=>{
    const b=find(id);if(role!=='warehouse'||store.status(b)!=='Awaiting approval')throw Error('Only a pending batch can be sent for QA review by Warehouse Staff.');
    if(store.requests[id])return;
    store.requests[id]={time:new Date().toISOString(),role};log(b,role,'QA review requested','',store.status(b),store.status(b));publish();
  };
  store.acknowledge=(alert,role)=>{
    if(role!=='qa')throw Error('Only QA Manager can acknowledge alerts.');
    if(store.acknowledgements[alert.id])return;
    store.acknowledgements[alert.id]={time:new Date().toISOString(),role};log(null,role,'Alert acknowledged',alert.id,null,null);publish();
  };
  function download(name,data){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
  function useStore(React){const[,update]=React.useState(0);React.useEffect(()=>store.subscribe(()=>update(x=>x+1)),[]);}
  function Panel({React,role,onOpen=()=>{},title,mode='operations'}){
    const h=React.createElement;useStore(React);
    const [search,setSearch]=React.useState(''),[filter,setFilter]=React.useState(''),[limit,setLimit]=React.useState(50),[error,setError]=React.useState('');
    const rows=store.batches.filter(b=>`${b.id} ${b.product}`.toLowerCase().includes(search.toLowerCase())&&(!filter||store.status(b)===filter));
    const sorted=[...rows].sort((a,b)=>String(a.Product_ID||a.productId||'').localeCompare(String(b.Product_ID||b.productId||''))||(Number(a.FEFO_Rank??a.fefoRank??Infinity)-Number(b.FEFO_Rank??b.fefoRank??Infinity))||a.id.localeCompare(b.id));
    const count=status=>store.batches.filter(b=>store.status(b)===status).length;
    function request(b){try{store.requestReview(key(b),role);setError('');}catch(e){setError(e.message);}}
    return h('section',{className:'cc-panel','data-testid':'workflow-panel'},h('h2',null,title||(mode==='catalogue'?'Batch inventory':role==='warehouse'?'Warehouse dispatch operations':'QA batch decisions')),
      h('p',null,mode==='catalogue'?'Search all batches, filter by status and inspect product, temperature, expiry and QA decisions. Use Dispatch Board to prepare the dispatch queue.':'Shared workflow for this browser session. Decisions survive role changes and model refreshes. These actions do not update a remote warehouse or create a production shipping authorization.'),
      mode!=='catalogue'&&h('div',{className:'cc-metrics'},...['Awaiting approval','Approved','In queue','Dispatched','Rejected'].map(s=>h('div',{key:s,className:'cc-metric'},h('span',null,s),h('strong',{'data-testid':'count-'+s.replace(/ /g,'-')},count(s))))),
      h('div',{className:'cc-fields'},h('input',{'aria-label':'Search workflow batches',placeholder:'Search batches or products',value:search,onChange:e=>{setSearch(e.target.value);setLimit(50);}}),
        h('select',{'aria-label':'Workflow status filter',value:filter,onChange:e=>{setFilter(e.target.value);setLimit(50);}},h('option',{value:''},'All statuses'),...['Awaiting approval','Approved','In queue','Dispatched','Rejected'].map(s=>h('option',{key:s,value:s},s))),
        h('button',{className:'cc-button',onClick:()=>{setSearch('');setFilter('');setLimit(50);}},'Clear filters')),
      error&&h('p',{role:'alert',className:'cc-error'},error),
      h('div',{className:'cc-table-wrap'},h('table',null,h('thead',null,h('tr',null,...(mode==='catalogue'?['Batch','Product','FEFO rank','Current temperature','Workflow status','Dynamic expiry','Location','Action']:['Batch','Product','FEFO rank','Current temperature','Workflow status','Action']).map(s=>h('th',{key:s},s)))),h('tbody',null,...sorted.slice(0,limit).map(b=>{
        const status=store.status(b),decision=store.decisions[key(b)],earlier=store.blocker(b);
        return h('tr',{key:key(b),'data-testid':'workflow-row','data-batch':b.id},h('td',null,b.id),h('td',null,b.product||b.Product_ID||'Not supplied'),h('td',null,b.FEFO_Rank??b.fefoRank??'Unavailable'),h('td',null,b.temp||'N/A'),h('td',null,status,store.requests[key(b)]&&status==='Awaiting approval'&&h('small',null,' · QA review requested'),decision?.note&&h('small',null,' · '+decision.note)),
          mode==='catalogue'&&h('td',null,b.Dynamic_Expiry_Date||b.dynamicExpiry||'Not supplied'),mode==='catalogue'&&h('td',null,b.location||'Not supplied'),h('td',null,h('button',{className:'cc-button',onClick:()=>onOpen(b)},'View details'),
            role==='qa'&&status==='Awaiting approval'&&h('button',{className:'cc-button',onClick:()=>onOpen(b)},'Review batch'),
            mode!=='catalogue'&&role==='warehouse'&&status==='Awaiting approval'&&h('button',{className:'cc-button',disabled:!!store.requests[key(b)],onClick:()=>request(b)},store.requests[key(b)]?'QA review requested':'Request QA review'),
            mode!=='catalogue'&&role==='warehouse'&&['Approved','In queue'].includes(status)&&h('button',{className:'cc-button',disabled:!!earlier,title:earlier?`Process ${earlier.id} first`:undefined,onClick:()=>onOpen(b)},status==='Approved'?'Add to Queue':'Confirm Dispatch'),
            mode!=='catalogue'&&earlier&&role==='warehouse'&&['Approved','In queue'].includes(status)&&h('p',null,`FEFO: process ${earlier.id} first.`),
            role==='warehouse'&&status==='Rejected'&&h('p',null,'Rejected by QA. Open details to view the reason.'),
            role==='warehouse'&&status==='Awaiting approval'&&h('p',null,'QA approval is required before queueing.')));
      })))),!rows.length&&h('p',null,'No batches match the current filters.'),rows.length>limit&&h('button',{className:'cc-button',onClick:()=>setLimit(n=>n+50)},'Show 50 more'),
      h('button',{className:'cc-button',onClick:()=>download('warehouse-workflow-audit.json',{scope:'Browser session workflow',batches:store.batches.map(b=>({id:b.id,key:key(b),status:store.status(b),decision:store.decisions[key(b)]})),audit:store.audit})},'Download workflow audit JSON'));
  }
  function Board({React,onOpen=()=>{}}){
    const h=React.createElement;useStore(React);const[error,setError]=React.useState(''),[limit,setLimit]=React.useState(24);
    const sections=[['In queue','Dispatch queue'],['Approved','Ready to queue'],['Awaiting approval','Waiting for QA']];
    function cards(status){return store.batches.filter(b=>store.status(b)===status).sort((a,b)=>String(a.Product_ID||a.productId||'').localeCompare(String(b.Product_ID||b.productId||''))||Number(a.FEFO_Rank??a.fefoRank??Infinity)-Number(b.FEFO_Rank??b.fefoRank??Infinity)||a.id.localeCompare(b.id));}
    return h('div',{className:'cc-workbench','data-testid':'dispatch-board'},h('h2',null,'Dispatch operations'),h('p',null,'Prepare approved batches for dispatch. Queue and dispatch follow QA decisions and the available FEFO order. All actions are shared within this browser session.'),
      h('div',{className:'cc-metrics'},...['Approved','In queue','Dispatched'].map(status=>h('div',{className:'cc-metric',key:status},h('span',null,status==='Approved'?'Ready to queue':status),h('strong',null,cards(status).length)))),
      error&&h('p',{className:'cc-error',role:'alert'},error),
      ...sections.map(([status,title])=>h('section',{className:'cc-panel',key:status,'data-testid':'dispatch-section-'+status.replace(/ /g,'-')},h('h3',null,`${title} (${cards(status).length})`),
        !cards(status).length&&h('p',null,status==='In queue'?'No batches in the dispatch queue.':status==='Approved'?'No approved batches ready to queue.':'No batches awaiting QA.'),
        h('div',{className:'cc-dispatch-cards'},...cards(status).slice(0,limit).map(b=>{const earlier=store.blocker(b);return h('article',{className:'cc-dispatch-card',key:key(b),'data-testid':'dispatch-card','data-batch':b.id},h('h4',null,b.id),h('p',null,b.product||'Product not supplied'),h('p',null,`FEFO rank: ${b.FEFO_Rank??b.fefoRank??'Unavailable'} · ${b.temp||'N/A'}`),h('strong',null,status),
          h('div',{className:'cc-actions'},h('button',{className:'cc-button',onClick:()=>onOpen(b)},'View details'),
            status==='Awaiting approval'?h('button',{className:'cc-button',disabled:!!store.requests[key(b)],onClick:()=>{try{store.requestReview(key(b),'warehouse');}catch(e){setError(e.message);}}},store.requests[key(b)]?'QA review requested':'Request QA review'):
            h('button',{className:'cc-button',disabled:!!earlier,onClick:()=>onOpen(b)},status==='Approved'?'Add to Queue':'Confirm Dispatch')),
          earlier&&status!=='Awaiting approval'&&h('p',{className:'cc-warning'},`FEFO: process ${earlier.id} first.`));})))),
      store.batches.length>limit&&h('button',{className:'cc-button',onClick:()=>setLimit(x=>x+24)},'Show more cards'),
      h('details',null,h('summary',null,`Completed and rejected batches (${cards('Dispatched').length+cards('Rejected').length})`),...['Dispatched','Rejected'].flatMap(status=>cards(status).slice(0,limit).map(b=>h('p',{key:key(b)},`${b.id} · ${status} `,h('button',{className:'cc-button',onClick:()=>onOpen(b)},'View details'))))));
  }
  function Detail({React,batch,role,close}){
    const h=React.createElement;useStore(React);const[note,setNote]=React.useState(''),[confirm,setConfirm]=React.useState(''),[error,setError]=React.useState('');const ref=React.useRef(null);
    const[telemetry,setTelemetry]=React.useState([]),[historyError,setHistoryError]=React.useState(''),[loadingHistory,setLoadingHistory]=React.useState(false);
    React.useEffect(()=>{
      let active=true;setTelemetry([]);setHistoryError('');
      if(batch.source!=='saved'||window.ColdChainDataset.store.active)return;
      setLoadingHistory(true);
      const base=(window.__COLDCHAIN_CONFIG__?.apiBaseUrl||'').replace(/\/+$/,'');
      window.ColdChainRuntime.jsonFetch(base+'/api/sensor/'+encodeURIComponent(batch.id)).then(data=>{
        if(!Array.isArray(data.readings))throw Error('Sensor response has no readings array.');
        if(active)setTelemetry(data.readings);
      }).catch(e=>{if(active)setHistoryError(e.message);}).finally(()=>{if(active)setLoadingHistory(false);});
      return()=>{active=false;};
    },[batch.id,batch.source]);
    React.useEffect(()=>{const previous=document.activeElement,overflow=document.body.style.overflow;document.body.style.overflow='hidden';ref.current?.querySelector('button')?.focus();const listener=e=>{if(e.key==='Escape'){if(confirm)setConfirm('');else close();}if(e.key==='Tab'){const nodes=[...ref.current.querySelectorAll('button:not(:disabled),input,textarea,select,[tabindex="0"]')];const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}};document.addEventListener('keydown',listener);return()=>{document.removeEventListener('keydown',listener);document.body.style.overflow=overflow;previous?.focus();};},[close,confirm]);
    const b=store.batches.find(x=>key(x)===key(batch));if(!b)return h('div',{className:'modal-backdrop'},h('div',{className:'cc-panel'},h('p',null,'The dataset changed. This batch is no longer active.'),h('button',{onClick:close},'Close')));
    const status=store.status(b),decision=store.decisions[key(b)],earlier=store.blocker(b),uploadedRows=window.ColdChainDataset.store.active?.dataset.batches?.[b.id],rows=uploadedRows||telemetry;
    function act(){try{store.transition(key(b),confirm,role,note);setConfirm('');setNote('');setError('');}catch(e){setError(e.message);}}
    return h('div',{className:'modal-backdrop',onMouseDown:e=>{if(e.target===e.currentTarget)close();}},h('section',{ref,className:'cc-panel cc-workflow-detail',role:'dialog','aria-modal':true,'aria-label':'Batch workflow details'},
      h('button',{className:'cc-button','aria-label':'Close batch details',onClick:close},'Close'),h('h2',null,b.id),h('p',null,b.product||'Product not supplied'),h('strong',{'data-testid':'detail-workflow-status'},status),
      h('p',null,`Temperature: ${b.temp||'N/A'} · FEFO rank: ${b.FEFO_Rank??b.fefoRank??'Unavailable'} · Dynamic expiry: ${b.Dynamic_Expiry_Date||b.dynamicExpiry||'Not supplied'}`),
      h('p',null,`Last observed: ${b.observedAt||'Not supplied'} · Quantity: ${b.quantity||b.Quantity||'Not supplied'} · Location: ${b.location||'Not supplied'}`),
      decision&&h('p',null,`Last decision: ${decision.role}, ${decision.time}. Note: ${decision.note||'None supplied'}`),
      h('p',null,'Source facts and workflow decisions are separate. An approval here is a browser-session action; it is not proof of product quality or a remote stock movement.'),
      loadingHistory&&h('p',{role:'status'},'Loading historical sensor readings…'),historyError&&h('p',{className:'cc-error'},'Sensor history unavailable: '+historyError),
      rows.length?h('details',null,h('summary',null,`View ${uploadedRows?'uploaded':'historical'} sensor history (${rows.length} readings)`),h('pre',{className:'cc-json'},JSON.stringify(rows.slice(-30),null,2)),h('button',{className:'cc-button',onClick:()=>download(b.id+'-sensor-history.json',rows)},'Download full sensor history JSON')):!loadingHistory&&h('p',null,'Sensor telemetry is not included in this batch view. No sample trace or trip details are substituted.'),
      role==='warehouse'&&status==='Awaiting approval'&&h('p',null,'Awaiting QA approval. Request review from the dispatch board; Warehouse Staff cannot approve this batch.'),
      role==='warehouse'&&status==='Rejected'&&h('p',null,'QA rejected this batch. Queueing and dispatch are unavailable.'),
      earlier&&role==='warehouse'&&h('p',{className:'cc-warning'},`FEFO: process approved batch ${earlier.id} first.`),
      error&&h('p',{className:'cc-error',role:'alert'},error),
      confirm?h('section',{'data-testid':'workflow-confirm'},h('h3',null,confirm==='Dispatched'?'Confirm dispatch?':`Confirm ${confirm.toLowerCase()}?`),
        h('label',{className:'cc-field'},'Decision note',h('textarea',{'aria-label':'Decision note',value:note,onChange:e=>setNote(e.target.value)})),
        h('p',null,confirm==='Rejected'?'A rejection reason is required.':confirm==='Approved'&&b.risk==='High'?'An observed excursion requires an explicit QA review note.':'The current status and FEFO order will be checked again when you confirm.'),
        h('button',{className:'cc-button',onClick:()=>{setConfirm('');setError('');}},'Cancel'),h('button',{className:'cc-button',onClick:act},'Confirm action')):
        h('div',{className:'cc-actions'},role==='qa'&&status==='Awaiting approval'&&h('button',{className:'cc-button',onClick:()=>setConfirm('Approved')},'Approve'),
          role==='qa'&&['Awaiting approval','Approved','In queue'].includes(status)&&h('button',{className:'cc-button',onClick:()=>setConfirm('Rejected')},'Reject'),
          role==='warehouse'&&status==='Approved'&&h('button',{className:'cc-button',disabled:!!earlier,onClick:()=>setConfirm('In queue')},'Add to Queue'),
          role==='warehouse'&&status==='In queue'&&h('button',{className:'cc-button',disabled:!!earlier,onClick:()=>setConfirm('Dispatched')},'Confirm Dispatch')),
      h('details',null,h('summary',null,'Batch workflow audit'),h('pre',{className:'cc-json'},JSON.stringify(store.audit.filter(x=>x.batch_key===key(b)),null,2)))));
  }
  function Alerts({React,alerts,role,onOpen}){
    const h=React.createElement;useStore(React);const[filter,setFilter]=React.useState(''),[error,setError]=React.useState('');
    return h('section',{className:'cc-panel'},h('h2',null,'Shared alerts'),h('select',{'aria-label':'Alert severity',value:filter,onChange:e=>setFilter(e.target.value)},...['','Critical','Warning'].map(x=>h('option',{key:x,value:x},x||'All severities'))),error&&h('p',{role:'alert'},error),
      !alerts.length&&h('p',null,'No active alert records from this data source.'),...alerts.filter(a=>!filter||a.severity===filter).map(a=>{
        const ack=store.acknowledgements[a.id],b=store.batches.find(b=>b.id===a.batch);
        return h('article',{className:'cc-panel',key:a.id},h('h3',null,`${a.batch} · ${a.type}`),h('p',null,`${a.severity} · ${a.time}`),h('p',null,a.detail||(a.factors||[]).join(' · ')),h('p',null,ack?`Acknowledged by QA at ${ack.time}`:a.status||'Open'),
          b&&h('button',{className:'cc-button',onClick:()=>onOpen(b)},'View batch details'),
          role==='qa'&&!ack&&a.status!=='Resolved'&&h('button',{className:'cc-button',onClick:()=>{try{store.acknowledge(a,role);}catch(e){setError(e.message);}}},'Acknowledge Alert'),
          role==='warehouse'&&h('p',null,'Warehouse Staff can inspect alerts. QA Manager handles acknowledgement and quality decisions.'));
      }));
  }
  window.ColdChainWorkflow={store,Panel,Board,Detail,Alerts};
})();
