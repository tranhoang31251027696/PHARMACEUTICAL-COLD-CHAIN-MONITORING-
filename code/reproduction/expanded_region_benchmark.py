"""Factorial complete-region study over N, candidate count and omissions.

Controlled selector-family omissions are designed tasks, not external bugs.
Preparation, complete diagnostics/JSON and independent checking timed apart.
"""
from pathlib import Path
import sys,csv,json,time,hashlib
from fractions import Fraction as F
import numpy as np
from complete_region_comparison import candidates,DEFAULT,intervals_partition,intervals_smt,certificate,verify_regions
Q=Path(__file__).resolve().parent

def fixture(n,g):
    rng=np.random.default_rng(5500+n+g);sizes=np.full(g,n//g);sizes[:n%g]+=1;labels=[];scores=[]
    for j,m in enumerate(sizes):
        k=int(round(int(m)*(.95-.70*j/(g-1))));yy=np.r_[np.ones(k,dtype=int),np.zeros(int(m)-k,dtype=int)];rng.shuffle(yy);labels.extend(yy);scores.extend([1-j/(g-1)]*int(m))
    order=rng.permutation(n);return np.asarray(labels)[order],np.asarray(scores)[order]

def prepare(y,s,pattern):
    gold=candidates(y,s,DEFAULT)
    if pattern=='none':actual=list(gold)
    elif pattern=='one':actual=[r for j,r in enumerate(gold) if j!=len(gold)//2]
    else:actual=[r for j,r in enumerate(gold) if j%2==0]
    return gold,actual

def main():
    R=Q/'results/v5';folder=R/'expanded_region_certificates';folder.mkdir(parents=True,exist_ok=True);rows=[];tasks=[];rng=np.random.default_rng(9552)
    for n in [1000,10000,100000]:
        for g in [10,30,90]:
            y,s=fixture(n,g);input_hash=hashlib.sha256(y.astype('<i8').tobytes()+s.astype('<f8').tobytes()).hexdigest()
            for pattern in ['none','one','alternating']:
                case=f'n{n}_g{g}_{pattern}';expected=None
                for rep in range(5):
                    for method in rng.permutation(['partition','smt_all_regions']):
                        t=time.perf_counter_ns();gold,actual=prepare(y,s,pattern);prep=(time.perf_counter_ns()-t)/1e6
                        t=time.perf_counter_ns();regions,stats=(intervals_partition if method=='partition' else intervals_smt)(gold,actual);c=certificate(gold,actual,regions);payload=json.dumps(c);producer=(time.perf_counter_ns()-t)/1e6
                        t=time.perf_counter_ns();probes=verify_regions(gold,actual,c);checker=(time.perf_counter_ns()-t)/1e6
                        if expected is None:expected=c
                        assert c==expected
                        if rep==0:(folder/(case+'_'+str(method)+'.json')).write_text(json.dumps({'case_id':case,'n':n,'g':g,'pattern':pattern,'input_sha256':input_hash,'method':str(method),'certificate':c,'algorithm_stats':stats},indent=2),encoding='utf-8')
                        rows.append(dict(case_id=case,n=n,g=g,pattern=pattern,method=str(method),replicate=rep,gold_candidates=len(gold),actual_candidates=len(actual),critical_points=len({p for p,*_ in gold+actual if F(3,10)<p<F(9,10)})+2,divergent_components=len(regions),policy_probes=probes,preparation_ms=prep,producer_serialization_ms=producer,checker_ms=checker,total_checked_ms=prep+producer+checker,certificate_bytes=len(payload.encode()),solver_calls=stats.get('solver_calls',0),psc_exact=c['psc_exact'],input_sha256=input_hash))
                tasks.append(dict(case_id=case,n=n,g=g,pattern=pattern,components=len(expected['divergent_regions']),psc_exact=expected['psc_exact']));print('expanded_regions',case,len(expected['divergent_regions']),flush=True)
    with (R/'expanded_region_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'status':'PASS','controlled_tasks':len(tasks),'methods':2,'repetitions':5,'raw_records':len(rows),'saved_certificates':len(tasks)*2,'n_levels':[1000,10000,100000],'g_levels':[10,30,90],'patterns':['none','one','alternating'],'all_complete_outputs_agree':True,'component_range':[min(t['components'] for t in tasks),max(t['components'] for t in tasks)],'tasks':tasks,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Systematic designed omissions, not real defects. Full diagnostic output equal for both methods; preparation, producer/JSON and same independent checker separately timed with randomized within-replicate method order. Includes fresh preparation in total; one host and five repetitions, no universal superiority claim.'}
    (R/'expanded_region_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
