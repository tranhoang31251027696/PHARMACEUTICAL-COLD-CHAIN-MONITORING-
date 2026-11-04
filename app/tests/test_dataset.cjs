const fs=require('fs'),assert=require('assert'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..'),R=require(path.join(root,'NETLIFY_DASHBOARD/coldchain-runtime.js'));
let resolveLate;const fakeR={...R,jsonFetch:()=>new Promise(resolve=>resolveLate=resolve)};const context={window:{ColdChainRuntime:fakeR,__COLDCHAIN_CONFIG__:{apiBaseUrl:'http://example.invalid'}},console,Blob,URL,setTimeout};
vm.runInNewContext(fs.readFileSync(path.join(root,'NETLIFY_DASHBOARD/coldchain-dataset.js'),'utf8'),context);const store=context.window.ColdChainDataset.store;
(async()=>{
const opts={defaultHumidity:60,defaultShipment:'Air'};
const raw='Note: All Date-Time values are in: UTC +05:45\r\n'+Array.from({length:12},(_,i)=>`${i+1},2019-11-18,${String(Math.floor(i/6)).padStart(2,'0')}:${String(i%6*10).padStart(2,'0')}:00,${i<6?5:9},`).join('\r\n');
const nepal=R.normalize(raw,{...opts,uploadName:'logger.csv'});assert.equal(nepal.count,2);assert.equal(nepal.provenance.raw_rows,12);assert.equal(Object.values(nepal.batches)[0][0].calibrated_temp,5);assert(nepal.warnings.some(x=>x.includes('UTC+05:45')));assert.throws(()=>R.normalize(raw.replace(',5,',',-300,'),opts),/Invalid Nepal temperature/);
store.activate(nepal,'logger.csv');await store.runModels();assert.equal(resolveLate,undefined);assert.match(store.active.progress,/Confirm complete/);
store.activate(nepal,'logger.csv',{historyComplete:true});assert.equal(store.alerts().length,1);assert.equal(store.batchRows()[0].outside,1);
const pending=store.runModels();assert.equal(store.active.busy,true);
store.activate(R.normalize('Product_ID,Batch_ID,Dynamic_Expiry_Date\nP,INV,2027-01-01'),'inventory.csv');
resolveLate({success:true,result:[]});await pending;assert.equal(store.active.filename,'inventory.csv');assert.equal(store.alerts().length,0);assert.equal(Object.keys(store.active.predictions).length,0);
store.activate(R.normalize('id,y,old_score,new_score\nx,1,.9,.8'),'regression.csv');assert.equal(store.active.filename,'inventory.csv');
store.reset();assert.equal(store.active,null);
console.log('PASS: Nepal hourly conversion, raw-value validation, derived alerts, stale-response isolation, inventory replacement and reset');
})().catch(e=>{console.error(e);process.exit(1)});
