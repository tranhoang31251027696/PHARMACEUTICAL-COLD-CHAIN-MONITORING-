"""Matched complete divergent-region outputs using partition and SMT AllSMT.

Both algorithms receive the same prepared finite candidate tables. Diagnostics
contain maximal divergent policy components and one representative witness per
component. That witness is existential, not one ID valid across the component.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,csv,time,hashlib
import numpy as np,z3
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import candidates,select
from policy_exact import DEFAULT
from external_sut_evaluation import upstream_functions,actual_table
from smt_baseline import expression

def member(interval,a):
    l,r=F(interval['lo']),F(interval['hi'])
    return (a>l or a==l and interval['left_closed']) and (a<r or a==r and interval['right_closed'])

def normalize(cells):
    out=[]
    for c in sorted(cells,key=lambda c:(F(c['lo']),not c['left_closed'],F(c['hi']))):
        if out and (F(c['lo'])<F(out[-1]['hi']) or c['lo']==out[-1]['hi'] and (out[-1]['right_closed'] or c['left_closed'])):
            if F(c['hi'])>F(out[-1]['hi']):out[-1]['hi']=c['hi'];out[-1]['right_closed']=c['right_closed']
            elif c['hi']==out[-1]['hi']:out[-1]['right_closed'] |= c['right_closed']
        else:out.append(dict(c))
    return out

def differs(gold,actual,a):return select(gold,a,True,DEFAULT)[2]!=select(actual,a,True,DEFAULT)[2]
def intervals_partition(gold,actual,lo=F(3,10),hi=F(9,10)):
    br=sorted({lo,hi}|{p for p,*_ in gold+actual if lo<p<hi});cells=[]
    for i,a in enumerate(br):
        if differs(gold,actual,a):cells.append(dict(lo=str(a),hi=str(a),left_closed=True,right_closed=True))
        if i and differs(gold,actual,(br[i-1]+a)/2):cells.append(dict(lo=str(br[i-1]),hi=str(a),left_closed=False,right_closed=False))
    return normalize(cells),{'critical_points':len(br)}

def intervals_smt(gold,actual,lo=F(3,10),hi=F(9,10)):
    alpha=z3.Real('alpha');solver=z3.SolverFor('QF_LRA');solver.set(timeout=5000)
    solver.add(alpha>=z3.RealVal(str(lo)),alpha<=z3.RealVal(str(hi)),expression(gold,alpha)!=expression(actual,alpha))
    cuts=sorted({p for p,*_ in gold+actual});cells=[];calls=0
    while True:
        out=solver.check();calls+=1
        if out==z3.unknown:raise RuntimeError('UNKNOWN is not a complete region result')
        if out==z3.unsat:break
        v=solver.model().eval(alpha,model_completion=True);a=F(v.numerator_as_long(),v.denominator_as_long())
        # Feasibility truth is constant on this entire predicate cell. Block the
        # cell rather than just the model point, so termination is finite.
        false=[p for p in cuts if p<a];true=[p for p in cuts if p>=a]
        l=max([lo]+false);r=min([hi]+true);lc=not any(p==l for p in false)
        region=dict(lo=str(l),hi=str(r),left_closed=lc,right_closed=True)
        assert l<=a<=r and member(region,a) and differs(gold,actual,a)
        condition=z3.And(alpha>=z3.RealVal(str(l)) if lc else alpha>z3.RealVal(str(l)),alpha<=z3.RealVal(str(r)))
        solver.add(z3.Not(condition));cells.append(region)
        assert calls<=len(cuts)+2
    return normalize(cells),{'solver_calls':calls,'predicate_cells':len(cells),'residual_result':'unsat'}

def certificate(gold,actual,regions):
    witnesses=[]
    for r in regions:
        l,h=F(r['lo']),F(r['hi']);a=l if r['left_closed'] else (l+h)/2
        old=select(gold,a,True,DEFAULT)[2];new=select(actual,a,True,DEFAULT)[2];xor=old^new;assert xor
        i=(xor&-xor).bit_length()-1;witnesses.append({'alpha':str(a),'row_index':i,'old_selected':bool(old>>i&1),'new_selected':bool(new>>i&1)})
    length=sum((F(r['hi'])-F(r['lo']) for r in regions),F(0))
    return {'domain':['3/10','9/10'],'equivalent':not bool(regions),'divergent_regions':regions,'psc_exact':str(length/F(3,5)),'representative_witnesses':witnesses,'witness_scope':'One example policy/ID per maximal component, not one universally changing ID over the component.'}

def verify_regions(gold,actual,c):
    lo,hi=map(F,c['domain']);br=sorted({lo,hi}|{p for p,*_ in gold+actual if lo<p<hi}|{F(r[k]) for r in c['divergent_regions'] for k in ['lo','hi']})
    assert (lo,hi)==(F(3,10),F(9,10))
    assert len(c['representative_witnesses'])==len(c['divergent_regions'])
    for r in c['divergent_regions']:
        assert lo<=F(r['lo'])<=F(r['hi'])<=hi
        if r['lo']==r['hi']:assert r['left_closed'] and r['right_closed']
    for left,right in zip(c['divergent_regions'],c['divergent_regions'][1:]):
        assert F(left['hi'])<=F(right['lo'])
        if F(left['hi'])==F(right['lo']):assert not left['right_closed'] and not right['left_closed'],'Components must be disjoint and maximal'
    assert c['equivalent']==(not bool(c['divergent_regions']))
    probes=set(br)|{(a+b)/2 for a,b in zip(br,br[1:])}
    for a in probes:assert any(member(r,a) for r in c['divergent_regions'])==differs(gold,actual,a)
    for r,w in zip(c['divergent_regions'],c['representative_witnesses']):
        a=F(w['alpha']);assert member(r,a);i=w['row_index'];old=select(gold,a,True,DEFAULT)[2];new=select(actual,a,True,DEFAULT)[2]
        assert bool(old>>i&1)==w['old_selected'] and bool(new>>i&1)==w['new_selected'] and w['old_selected']!=w['new_selected']
    length=sum((b-a for a,b in zip(br,br[1:]) if differs(gold,actual,(a+b)/2)),F(0));assert F(c['psc_exact'])==length/(hi-lo)
    return len(probes)

def main():
    R=Q/'results/v4';folder=R/'region_certificates';folder.mkdir(exist_ok=True)
    functions=upstream_functions();records=json.loads((Q/'inputs/external_sut/manifest.json').read_text(encoding='utf-8'))['cases']
    selected=[r for r in records if r['case_id']=='issue23213_protocol' or r['case_id'].endswith('seed0')];assert len(selected)==4
    rows=[];checks=0
    for rec in selected:
        d=np.load(Q/'inputs/external_sut'/rec['file']);gold=candidates(d['y'],d['scores'],DEFAULT)
        for variant in ['affected','fixed']:
            actual,_=actual_table(functions[variant][0],d['y'],d['scores']);expected=None
            for method,fn in [('partition',intervals_partition),('smt_all_regions',intervals_smt)]:
                for rep in range(3):
                    t=time.perf_counter_ns();regions,stats=fn(gold,actual);c=certificate(gold,actual,regions);encoded=json.dumps(c);producer_ms=(time.perf_counter_ns()-t)/1e6
                    t=time.perf_counter_ns();probes=verify_regions(gold,actual,c);checker_ms=(time.perf_counter_ns()-t)/1e6;checks+=1
                    if expected is None:expected=c
                    assert c==expected
                    if rep==0:(folder/f'{rec["case_id"]}_{variant}_{method}.json').write_text(json.dumps({'case_id':rec['case_id'],'variant':variant,'method':method,'certificate':c,'algorithm_stats':stats},indent=2),encoding='utf-8')
                    rows.append(dict(case_id=rec['case_id'],variant=variant,method=method,replicate=rep,producer_and_serialization_ms=producer_ms,independent_checker_ms=checker_ms,regions=len(regions),psc_exact=c['psc_exact'],certificate_bytes=len(encoded.encode()),checker_probes=probes,solver_calls=stats.get('solver_calls',0)))
            print('complete_regions',rec['case_id'],variant,flush=True)
    with (R/'complete_region_timings.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'status':'PASS','same_output_tasks':8,'input_workloads':4,'methods':2,'repetitions':3,'measured_records':len(rows),'certificates_independently_checked':checks,'all_regions_psc_and_witnesses_match':True,'solver_version':z3.get_version_string(),'scope':'Prepared nested threshold tables, complete divergent components+PSC+representative witnesses for both methods; counts/mask construction excluded for both. Partition is the external-table adapter, not the optimized rank-comparison core. Same checker invoked for both; no uniqueness or universal speed claim.'}
    summary['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (R/'complete_region_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
