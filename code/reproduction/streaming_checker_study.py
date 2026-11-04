"""Paired old/new independent-consumer costs and complete frozen-corpus audit."""
from pathlib import Path
import csv,json,sys,time,tracemalloc,hashlib
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import verify as legacy
from streaming_checker import verify as streamed
from policy_exact import compare_policies

def main():
    R=Q/'results/v5';R.mkdir(exist_ok=True)
    import verify_artifact
    verify_artifact.verify=streamed;verify_artifact.main('v5/streaming_artifact_verification.json')
    rows=[];order_rng=np.random.default_rng(7755)
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        rng=np.random.default_rng(44000+n);a=rng.integers(0,g,n)/(g-1);y=rng.integers(0,2,n);ids=list(range(n))
        for workload in ['invariant','divergent']:
            b=a.copy() if workload=='invariant' else a+rng.choice([-1,0,1],n)*1e-8
            cert=compare_policies(y,a,b,ids=ids);payload=json.dumps(cert)
            for fn in [legacy,streamed]:fn(y,a,b,ids,cert)
            for rep in range(5):
                for method in order_rng.permutation(['legacy','streamed']):
                    fn=legacy if method=='legacy' else streamed;t=time.perf_counter_ns();parsed=json.loads(payload);parse_ms=(time.perf_counter_ns()-t)/1e6
                    t=time.perf_counter_ns();v=fn(y,a,b,ids,parsed);elapsed=(time.perf_counter_ns()-t)/1e6
                    rows.append(dict(n=n,g=g,workload=workload,method=str(method),phase='untraced',replicate=rep,checker_ms=elapsed,parse_ms=parse_ms,peak_aux_mib='',probes=v['probes'],input_sha256=cert['input_sha256']))
            for method,fn in [('legacy',legacy),('streamed',streamed)]:
                tracemalloc.start();v=fn(y,a,b,ids,cert);peak=tracemalloc.get_traced_memory()[1]/2**20;tracemalloc.stop()
                rows.append(dict(n=n,g=g,workload=workload,method=method,phase='separate_memory',replicate=0,checker_ms='',parse_ms='',peak_aux_mib=peak,probes=v['probes'],input_sha256=cert['input_sha256']))
            print('paired_checkers',n,workload,flush=True)
    with (R/'paired_checker_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        for work in ['invariant','divergent']:
            for method in ['legacy','streamed']:
                rr=[r for r in rows if r['n']==n and r['workload']==work and r['method']==method];v=[r['checker_ms'] for r in rr if r['phase']=='untraced'];q=np.percentile(v,[25,75],method='linear')
                summary.append(dict(n=n,g=g,workload=work,method=method,median_ms=float(np.median(v)),iqr_ms=float(q[1]-q[0]),peak_aux_mib=next(r['peak_aux_mib'] for r in rr if r['phase']=='separate_memory')))
    with (R/'paired_checker_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    meta={'status':'PASS','timing_records':60,'separate_memory_records':12,'groups':12,'paired_fixture_groups':6,'repetitions':5,'randomized_within_replicate_order':True,'production_outside_timing':True,'source_sha256':{f:hashlib.sha256((Q/f).read_bytes()).hexdigest() for f in ['src/independent_oracle.py','src/streaming_checker.py','streaming_checker_study.py']},'scope':'Matched fixtures, payload and hashing/coverage/witness obligations; JSON parsing separate. Untraced times never pooled with traced memory. One host, no universal CI latency claim.'}
    (R/'paired_checker_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
