"""Record within-invocation phase timings; do not subtract independent medians."""
from pathlib import Path
import sys,json,csv,time,hashlib
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from policy_exact import compare_policies

def main():
    rows=[]
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        rng=np.random.default_rng(90210+n);a=rng.integers(0,g,n)/(g-1);y=rng.integers(0,2,n);ids=list(range(n));b=a+rng.choice([-1,0,1],n)*1e-8
        for flag in [False,True]:compare_policies(y,a,b,ids=ids,with_witness=flag)
        for rep in range(10):
            for flag in rng.permutation([False,True]):
                stages={};t=time.perf_counter_ns();c=compare_policies(y,a,b,ids=ids,with_witness=bool(flag),stage_timings=stages)
                z=time.perf_counter_ns();payload=json.dumps(c);stages['serialization_ms']=(time.perf_counter_ns()-z)/1e6;total=(time.perf_counter_ns()-t)/1e6
                assert not c['equivalent'] and all(v>=0 for v in stages.values())
                rows.append(dict(n=n,g=g,replicate=rep,witness=bool(flag),input_sha256=c['input_sha256'],**stages,total_ms=total,unattributed_ms=total-sum(stages.values()),witness_cells=sum(x['witness'] is not None for x in c['cells']),serialized_bytes=len(payload.encode())))
    R=Q/'results/v2';R.mkdir(exist_ok=True)
    with (R/'ablation_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        for flag in [False,True]:
            rr=[r for r in rows if r['n']==n and r['witness']==flag]
            for phase in ['construction_ms','sweep_excluding_witness_ms','witness_ms','assembly_and_hash_ms','serialization_ms','total_ms']:
                v=[r[phase] for r in rr];q=np.percentile(v,[25,75],method='linear');summaries.append(dict(n=n,g=g,witness=flag,phase=phase,reps=10,median_ms=float(np.median(v)),iqr_ms=float(q[1]-q[0])))
    with (R/'ablation_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    r={'status':'PASS','records':len(rows),'groups':len(summaries),'seed_rule':'90210+N','tracemalloc':False,'source_sha256':hashlib.sha256((Q/'src/policy_exact.py').read_bytes()).hexdigest(),'scope':'Same-invocation instrumented wall-clock stages; profiler overhead remains; medians are descriptive and need not sum to median total. Not pooled with traced timings.'}
    (R/'ablation_metadata.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
