"""Measure certificate consumer/checker cost independently from the producer."""
from pathlib import Path
import json,csv,sys,time,tracemalloc,hashlib
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from policy_exact import compare_policies
from independent_oracle import verify

def main():
    rows=[]
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        rng=np.random.default_rng(44000+n);a=rng.integers(0,g,n)/(g-1);y=rng.integers(0,2,n);ids=list(range(n))
        for workload in ['invariant','divergent']:
            b=a.copy() if workload=='invariant' else a+rng.choice([-1,0,1],n)*1e-8
            cert=compare_policies(y,a,b,ids=ids);payload=json.dumps(cert);verify(y,a,b,ids,cert)
            for rep in range(5):
                t=time.perf_counter_ns();parsed=json.loads(payload);parse_ms=(time.perf_counter_ns()-t)/1e6;t=time.perf_counter_ns();v=verify(y,a,b,ids,parsed);check_ms=(time.perf_counter_ns()-t)/1e6
                rows.append(dict(n=n,g=g,workload=workload,phase='untraced_consumer',replicate=rep,parse_ms=parse_ms,checker_ms=check_ms,peak_aux_mib='',policy_probes=v['probes'],certificate_bytes=len(payload.encode()),input_sha256=cert['input_sha256']))
            tracemalloc.start();v=verify(y,a,b,ids,cert);peak=tracemalloc.get_traced_memory()[1]/2**20;tracemalloc.stop()
            rows.append(dict(n=n,g=g,workload=workload,phase='separate_memory_run',replicate=0,parse_ms='',checker_ms='',peak_aux_mib=peak,policy_probes=v['probes'],certificate_bytes=len(payload.encode()),input_sha256=cert['input_sha256']))
            print('checker',n,workload,flush=True)
    R=Q/'results/v4'
    with (R/'checker_cost_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        for work in ['invariant','divergent']:
            rr=[r for r in rows if r['n']==n and r['workload']==work and r['phase']=='untraced_consumer'];v=[r['checker_ms'] for r in rr];q=np.percentile(v,[25,75],method='linear');mem=next(r['peak_aux_mib'] for r in rows if r['n']==n and r['workload']==work and r['phase']=='separate_memory_run')
            summary.append(dict(n=n,g=g,workload=work,repetitions=5,checker_median_ms=float(np.median(v)),checker_iqr_ms=float(q[1]-q[0]),parse_median_ms=float(np.median([r['parse_ms'] for r in rr])),separate_peak_aux_mib=mem,policy_probes=rr[0]['policy_probes']))
    with (R/'checker_cost_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    meta={'status':'PASS','raw_records':len(rows),'timing_records':30,'memory_records':6,'timing_tracemalloc':False,'memory_timing_pooled':False,'checker_source_sha256':hashlib.sha256((Q/'src/independent_oracle.py').read_bytes()).hexdigest(),'scope':'Producer runs before timing and is excluded. Inputs/certificate prepared before memory tracing; checker construction, hashing, coverage and witness/PSC checks included. Independent checker materializes Boolean threshold masks before bitset packing, so peak scratch includes O(NG) bytes, not only stored O(NG) bits. One host; five repetitions per timing group.'}
    (R/'checker_cost_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
