const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..'),R=require(path.join(root,'NETLIFY_DASHBOARD/coldchain-runtime.js'));
const cache=JSON.parse(fs.readFileSync(path.join(root,'NETLIFY_DASHBOARD/samples/sample_linked_predictions.json'),'utf8'));
let hooks=[],index=0,effects=[],dirty=false,tree,apiCalls=[];
const React={createElement:(tag,props,...children)=>({tag,props:props||{},children:children.flat(Infinity)}),Fragment:'fragment',
 useState(initial){const i=index++;if(!(i in hooks))hooks[i]=initial;return[hooks[i],v=>{const next=typeof v==='function'?v(hooks[i]):v;if(next!==hooks[i]){hooks[i]=next;dirty=true;}}]},
 useRef(initial){const i=index++;return hooks[i]||(hooks[i]={current:initial})},
 useMemo(fn,deps){const i=index++,old=hooks[i];if(!old||deps.some((v,j)=>v!==old.deps[j]))hooks[i]={deps,value:fn()};return hooks[i].value},
 useEffect(fn,deps){const i=index++,old=hooks[i];if(!old||deps.some((v,j)=>v!==old[j])){hooks[i]=deps;effects.push(fn)}}};
const runtime={...R,jsonFetch:async(url,body)=>{apiCalls.push({url,body});if(url==='/api/local-health')return{service:'coldchain-local',regression_available:true};if(url==='/api/live-model-pair')return structuredClone(cache['sample_sensor_multi_batch.csv'][body.readings[0].Batch_ID]);throw Error('Unexpected API '+url)}};
const window={ColdChainRuntime:runtime,__COLDCHAIN_CONFIG__:{}};
const context={window,console,Blob,URL,TextEncoder,crypto:webcrypto,setTimeout,document:{baseURI:'http://localhost/',getElementById:()=>({scrollIntoView(){}})},
 fetch:async url=>{const p=path.join(root,'NETLIFY_DASHBOARD',new URL(url).pathname);const text=fs.readFileSync(p,'utf8');return{ok:true,text:async()=>text,json:async()=>JSON.parse(text)}},
 Worker:class{terminate(){}postMessage(data){queueMicrotask(()=>this.onmessage({data:{ok:true,result:R.normalize(data.text,data.options)}}))}}};
vm.createContext(context);
for(const f of ['coldchain-dataset.js','coldchain-workbench.js'])vm.runInContext(fs.readFileSync(path.join(root,'NETLIFY_DASHBOARD',f),'utf8'),context);
const store=window.ColdChainDataset.store;
function render(){let n=0;do{dirty=false;index=0;effects=[];tree=window.ColdChainApp.Workbench({React});for(const fn of effects)fn();if(++n>20)throw Error('Render loop')}while(dirty)}
function nodes(node){return !node||typeof node!=='object'?[]:[node,...node.children.flatMap(x=>x===undefined?[]:nodes(x))]}
function button(text){const b=nodes(tree).find(n=>n.tag==='button'&&n.children.includes(text));assert(b,'Missing button '+text);return b}
async function settle(){await new Promise(r=>setImmediate(r));render()}
(async()=>{
 render();await settle();assert.equal(button('Sensor sample 2 (3 batches)').props.disabled,false);
 await button('Sensor sample 2 (3 batches)').props.onClick();await settle();
 assert.equal(store.active.dataset.kind,'sensor');assert.equal(store.batchRows().length,3);assert(store.batchRows().every(b=>b.Product_ID&&b.FEFO_Rank));
 assert.equal(button('FEFO for current batches').props.disabled,false);assert.equal(button('Regression for current batch').props.disabled,false);
 const identity=store.active.dataset;
 const select=nodes(tree).find(n=>n.tag==='select'&&n.props['aria-label']==='Batch');select.props.onChange({target:{value:'BATCH-01004'}});render();
 assert(nodes(tree).some(n=>n.props['data-testid']==='regression-scores'));
 const position=nodes(tree).find(n=>n.props['aria-label']==='Sensor cursor');position.props.onChange({target:{value:20}});render();
 assert.equal(button('Regression for current batch').props.disabled,true,'full-history scores must not leak into partial cursor');
 position.props.onChange({target:{value:335}});render();
 const check=nodes(tree).find(n=>n.tag==='label'&&n.children.includes('I confirm that the submitted history is complete for this batch')).children.find(n=>n.tag==='input');check.props.onChange({target:{checked:true}});render();
 await button('Run two XGBoost models locally').props.onClick();await settle();
 assert.equal(store.active.dataset,identity,'fresh scores must preserve sensor and FEFO source');assert.equal(store.batchRows().length,3);
 assert(nodes(tree).some(n=>n.props.id==='cc-linked-fefo'));assert(nodes(tree).some(n=>n.props['aria-label']==='Sensor cursor'));assert(nodes(tree).some(n=>n.props['data-testid']==='regression-scores'));
 assert.throws(()=>store.attachInventory(R.normalize('Product_ID,Batch_ID,Dynamic_Expiry_Date\nP,OTHER,2027-01-01'),'bad.csv'),/no sensor/);
 assert.equal(store.active.dataset,identity);
 const offset=nodes(tree).find(n=>n.tag==='label'&&n.children.includes('For Temperature: apply Temperature × (1 − Calibration_Offset_Pct/100)')).children.find(n=>n.tag==='input');
 offset.props.onChange({target:{checked:true}});render();
 await button('Sensor sample 2 (3 batches)').props.onClick();await settle();
 assert.equal(button('Regression for current batch').props.disabled,true,'changed import values must reject cached scores');
 assert.equal(button('FEFO for current batches').props.disabled,false);
 console.log('PASS: linked sample load, batch selection, cursor invalidation, fresh inference preserving sensor/FEFO, and rejection of unrelated inventory');
})().catch(e=>{console.error(e);process.exit(1)});

