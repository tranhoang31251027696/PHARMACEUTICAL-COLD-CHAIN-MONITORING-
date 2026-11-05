(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.ColdChainExpiry=api;})(globalThis,function(){
'use strict';
function num(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error('Missing '+name);const n=Number(value);if(!Number.isFinite(n))throw Error('Invalid '+name);return n;}
function time(value,name){const s=String(value||'').trim();if(!/^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,3})?)?)?$/.test(s))throw Error(name+': use YYYY-MM-DD or timezone-free ISO timestamp');const t=Date.parse(s.replace(' ','T')+(s.length===10?'T00:00:00Z':'Z'));if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==s.slice(0,10))throw Error('Invalid '+name);return t;}
function calculate(sensor,metadata){
 if(sensor?.kind!=='sensor')throw Error('Upload sensor histories first');
 const required=['Product_ID','Batch_ID','Manufacture_Date','Label_Expiry_Date','Standard_Shelf_Life_Days','Ea_J_per_mol','Reference_Temp_C'];
 const seen=new Set(),rows=[];
 for(const m of metadata){
  for(const k of required)if(m[k]===undefined||String(m[k]).trim()==='')throw Error('Missing '+k);
  if(seen.has(m.Batch_ID))throw Error('Duplicate batch metadata: '+m.Batch_ID);seen.add(m.Batch_ID);
  const history=sensor.batches[m.Batch_ID];if(!history||history.length<2)throw Error('Need at least two sensor readings for '+m.Batch_ID);
  const points=history.map(r=>({t:time(r.Timestamp,'Timestamp'),temp:num(r.calibrated_temp,'temperature')})).sort((a,b)=>a.t-b.t);
  const manufacture=time(m.Manufacture_Date,'Manufacture_Date'),label=time(m.Label_Expiry_Date,'Label_Expiry_Date');
  const shelf=num(m.Standard_Shelf_Life_Days,'shelf life'),ea=num(m.Ea_J_per_mol,'activation energy'),ref=num(m.Reference_Temp_C,'reference temperature');
  if(shelf<=0||ea<=0||ref<=-273.15)throw Error('Shelf life and activation energy must be positive; reference temperature must exceed absolute zero');
  if(points[0].t<manufacture||label<manufacture)throw Error('Sensor history and label expiry must not precede manufacture');
  let monitored=0,equivalent=0;
  for(let i=0;i<points.length;i++){
   if(points[i].temp<=-273.15)throw Error('Temperature must exceed absolute zero');
   if(i===points.length-1)break;
   const hours=(points[i+1].t-points[i].t)/3600000;
   if(hours!==1)throw Error('Consecutive hourly sensor readings required for '+m.Batch_ID+'; gaps and duplicate times are not filled');
   const rate=Math.exp(ea/8.314*(1/(ref+273.15)-1/(points[i].temp+273.15)));
   if(!Number.isFinite(rate))throw Error('Arrhenius rate overflow');monitored+=hours;equivalent+=rate*hours;
  }
  monitored/=24;equivalent/=24;
  const asOf=points.at(-1).t,age=(asOf-manufacture)/86400000;
  const remaining=Math.max(0,shelf-age-(equivalent-monitored));
  const priority=Math.max(0,Math.min((label-asOf)/86400000,remaining));
  const expiry=Math.min(label,asOf+priority*86400000);
  rows.push({...m,Dynamic_Expiry_Date:new Date(expiry).toISOString().replace('Z',''),Remaining_Days:priority,As_Of:new Date(asOf).toISOString().replace('Z',''),Monitored_Days:monitored,Equivalent_Days:equivalent,Age_Days:age,Excess_Aging_Days:equivalent-monitored,Calculation_Method:'Arrhenius estimate; unmonitored age at reference temperature; capped at label expiry',_expiry:expiry});
 }
 if(!rows.length)throw Error('Metadata CSV is empty');
 const missing=Object.keys(sensor.batches).filter(id=>!seen.has(id));if(missing.length)throw Error('Metadata missing for sensor batches: '+missing.slice(0,5).join(', '));
 rows.sort((a,b)=>a.Product_ID.localeCompare(b.Product_ID)||a._expiry-b._expiry||a.Batch_ID.localeCompare(b.Batch_ID));
 let product,expiry,rank=0;for(const r of rows){if(r.Product_ID!==product){rank=0;expiry=undefined;}if(r._expiry!==expiry)rank++;product=r.Product_ID;expiry=r._expiry;r.FEFO_Rank=rank;delete r._expiry;}
 return {kind:'inventory',count:rows.length,rows,warnings:['Model-based expiry estimate, not a certified product expiry. Unmonitored age is assumed to have elapsed at reference temperature. No interval is added after the last reading.'],expiry_calculation:{source:'Uploaded sensor histories and product/batch metadata',method:'remaining=max(0,shelf-age-(equivalent-monitored)); expiry capped at label date',assumptions:'Hourly left-hold integration; unmonitored age at reference temperature; no XGBoost scores used'}};
}
return {calculate};
});
