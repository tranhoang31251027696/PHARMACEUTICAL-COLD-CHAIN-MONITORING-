"""Extend matched diagnostics to G=250/500 without a universal speed claim."""
from pathlib import Path
from fractions import Fraction as F
import csv,json,time,hashlib
import numpy as np
from expanded_region_benchmark import fixture,prepare
from complete_region_comparison import intervals_partition,intervals_smt,certificate,verify_regions
Q=Path(__file__).resolve().parent

def main():
    R=Q/'results/v6';folder=R/'large_g_certificates';folder.mkdir(parents=True,exist_ok=True);rows=[];tasks=[];rng=np.random.default_rng(9661);n=10000
    for g in [250,500]:
        y,s=fixture(n,g);digest=hashlib.sha256(y.astype('<i8').tobytes()+s.astype('<f8').tobytes()).hexdigest()
        for pattern in ['none','one','alternating']:
            case=f'n{n}_g{g}_{pattern}';expected=None
            for rep in range(3):
                for method in rng.permutation(['partition','smt_all_regions']):
                    t=time.perf_counter_ns();gold,actual=prepare(y,s,pattern);prep=(time.perf_counter_ns()-t)/1e6
                    t=time.perf_counter_ns();regions,stats=(intervals_partition if method=='partition' else intervals_smt)(gold,actual);c=certificate(gold,actual,regions);payload=json.dumps(c);producer=(time.perf_counter_ns()-t)/1e6
                    t=time.perf_counter_ns();probes=verify_regions(gold,actual,c);checker=(time.perf_counter_ns()-t)/1e6
                    if expected is None:expected=c
                    assert c==expected
                    if rep==0:(folder/(case+'_'+str(method)+'.json')).write_text(json.dumps({'case_id':case,'n':n,'g':g,'pattern':pattern,'method':str(method),'input_sha256':digest,'certificate':c,'algorithm_stats':stats},indent=2),encoding='utf-8')
                    rows.append(dict(case_id=case,n=n,g=g,pattern=pattern,method=str(method),replicate=rep,gold_candidates=len(gold),actual_candidates=len(actual),critical_points=len({p for p,*_ in gold+actual if F(3,10)<p<F(9,10)})+2,components=len(regions),preparation_ms=prep,producer_serialization_ms=producer,checker_ms=checker,total_checked_ms=prep+producer+checker,policy_probes=probes,solver_calls=stats.get('solver_calls',0),certificate_bytes=len(payload.encode()),psc_exact=c['psc_exact'],input_sha256=digest))
                print('large_G',case,'replicate',rep,flush=True)
            tasks.append(dict(case_id=case,g=g,n=n,pattern=pattern,components=len(expected['divergent_regions']),psc_exact=expected['psc_exact']))
    with (R/'large_g_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'status':'PASS','tasks':tasks,'controlled_tasks':6,'raw_records':len(rows),'saved_certificates':12,'repetitions':3,'all_complete_outputs_agree':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Six additional designed candidate-family tasks at N=10000 and G=250/500, randomized within-replicate order; exact same complete output and checker. Three repetitions, not pooled with the earlier five-repetition protocol. Z3 unknown/timeout prevents certification; no universal or state-of-the-art AllSMT superiority is inferred.'}
    (R/'large_g_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
