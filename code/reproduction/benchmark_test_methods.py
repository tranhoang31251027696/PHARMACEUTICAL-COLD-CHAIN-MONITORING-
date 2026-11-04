"""Matched-input local checking costs; flags retain each method's own scope."""
from pathlib import Path
import sys,json,csv,time,datetime,hashlib
import numpy as np
from fractions import Fraction
Q=Path(__file__).resolve().parent;sys.path[:0]=[str(Q/'src'),str(Q/'vendor')]
from policy_exact import profile,winner,compare_policies,DEFAULT
from decision_regression import compare
from benchmark_baselines import b4_exact_comparator_workflow

def main():
    manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'));rows=[];rng=np.random.default_rng(271828)
    for rec in manifest['cases']:
        if rec.get('seed')!=0:continue
        z=np.load(Q/'inputs'/rec['file']);y=z['y'];a=z['old'];ids=z['ids'].tolist()
        for workload in ['invariant','roundoff','strict_selector']:
            b=a.copy() if workload!='roundoff' else a+np.random.default_rng(4000).choice([-1,0,1],len(a))*np.finfo(np.float32).eps/2
            spec={**DEFAULT,**({'precision':'strict'} if workload=='strict_selector' else {})}
            def output(scores,alpha,ss):
                p=profile(y,scores,ss);n=winner(p,alpha);mask=np.zeros(len(y),bool);mask[p['order'][:n]]=True;return mask
            def snapshot():return not np.array_equal(output(a,Fraction(1,2),DEFAULT),output(b,Fraction(1,2),spec))
            def grid():
                # Always visit the complete grid, matching the exhaustive query
                # scope rather than benefitting from first-difference early exit.
                found=False
                for v in range(30,91,5):found |= not np.array_equal(output(a,Fraction(v,100),DEFAULT),output(b,Fraction(v,100),spec))
                return bool(found)
            methods={'snapshot':snapshot,'grid_13':grid,'score_B4':lambda:not b4_exact_comparator_workflow(a,b),
                'current_guard':lambda:compare(y,a,b,.5,mode='full')['regression_flag'],
                'exact_certificate':lambda:compare_policies(y,a,b,ids=ids,new_spec=spec)['equivalent'] is False}
            for f in methods.values():f()
            for rep in range(6):
                for name in rng.permutation(list(methods)):
                    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter_ns();flag=bool(methods[name]());ms=(time.perf_counter_ns()-t)/1e6
                    rows.append(dict(case_id=rec['case_id'],pipeline=rec['pipeline'],n=len(y),workload=workload,method=name,replicate=rep,started_utc=started,elapsed_ms=ms,flag=flag))
    out=Q/'results'
    def save(fn,rr):
        with (out/fn).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('matched_method_timings.csv',rows);summary=[]
    for key in sorted({(r['pipeline'],r['workload'],r['method']) for r in rows}):
        rr=[r for r in rows if (r['pipeline'],r['workload'],r['method'])==key];v=[r['elapsed_ms'] for r in rr];q=np.percentile(v,[25,75],method='linear')
        summary.append(dict(pipeline=key[0],workload=key[1],method=key[2],reps=len(rr),median_ms=float(np.median(v)),iqr_ms=float(q[1]-q[0])))
    save('matched_method_summary.csv',summary)
    metadata={'status':'PASS','records':len(rows),'groups':len(summary),'repetitions':6,'seed':271828,'tracemalloc':False,'timing':'perf_counter_ns; setup performed anew for each call; one warmup; randomized method order; no JSON serialization in this matched-input comparison','scope':'Each flag retains its distinct observation contract. B4/current guard cannot observe selector-code mutation. This is implementation cost, not equal-capability dominance. Certificate witness construction is enabled; serialization is timed only in the separate certificate benchmark. Snapshot/grid use the declared functional SUT adapter, not independent oracle enumeration.','source_sha256':{str(f.relative_to(Q)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Q/'src/policy_exact.py',Q/'vendor/decision_regression.py',Q/'vendor/benchmark_baselines.py']}}
    (out/'matched_method_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8');print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
