"""Predeclared policy-domain queries on the existing SciPy defect cohort.

No new bugs, deployments, developer study or optimized solver comparison.
Direct enumeration reuses executed interpolation outputs and independently
prepared masks. It does not rerun the public interpolation API per policy.
"""
from pathlib import Path
from fractions import Fraction as F
import json,csv,time,hashlib
import numpy as np
import z3
from scipy_documented_defect import functions,cases
from policy_domain_query import answer
from streaming_checker import verify
from independent_oracle import candidates,select
from policy_exact import DEFAULT
Q=Path(__file__).resolve().parent

def queries():
    common=dict(semantics='rational',lo='3/10',hi='9/10',left_closed=True,right_closed=True)
    return [('grid13',dict(semantics='rational',kind='finite',values=[str(F(3,10)+F(i,20)) for i in range(13)])),
            ('declared_three',dict(semantics='rational',kind='finite',values=['1/2','4/5','9/10']))]+[(f'decimal{d}',dict(common,kind='lattice',decimal_places=d)) for d in [2,3,4,6]]+[
            ('whole_interval',dict(common,kind='interval')),('high_interval',dict(common,kind='interval',lo='4/5'))]

def smt_answer(a,b,q):
    alpha=z3.Real('alpha');s=z3.Solver();s.set(timeout=30000)
    if q['kind']=='finite':s.add(z3.Or(*[alpha==z3.RealVal(str(F(v))) for v in q['values']]))
    else:
        s.add(alpha>=z3.RealVal(q['lo']) if q['left_closed'] else alpha>z3.RealVal(q['lo']))
        s.add(alpha<=z3.RealVal(q['hi']) if q['right_closed'] else alpha<z3.RealVal(q['hi']))
        if q['kind']=='lattice':s.add(alpha==z3.ToReal(z3.Int('policy_index'))/10**q['decimal_places'])
    def winner(table):
        w=z3.IntVal(0)
        for p,k,n,bits in sorted(table,key=lambda t:(t[1],t[2])):w=z3.If(alpha<=z3.RealVal(str(p)),z3.IntVal(bits),w)
        return w
    s.add(winner(a)!=winner(b));verdict=s.check()
    if verdict==z3.unknown:raise RuntimeError('SMT timeout/unknown: '+s.reason_unknown())
    witness=None
    if verdict==z3.sat:
        v=s.model().eval(alpha);witness=str(F(v.numerator_as_long(),v.denominator_as_long()))
    return dict(affected=verdict==z3.sat,witness=witness,verdict=str(verdict))

def direct_values(q):
    if q['kind']=='finite':return sorted(set(map(F,q['values'])))
    if q['kind']=='lattice' and q['decimal_places']<=3:
        scale=10**q['decimal_places'];return [F(i,scale) for i in range(3*scale//10,9*scale//10+1)]
    return None

def main():
    R=Q/'results/v7';R.mkdir(parents=True,exist_ok=True);funcs,_,_=functions();rows=[];audits=[]
    (R/'query_protocol.json').write_text(json.dumps({'queries':dict(queries()),'cohort':'All 36 existing SciPy affected-source workloads, no outcome filtering','contract':'Exact rational precision and selected observation IDs; policy sets are declared study scenarios, not observed deployment policies','direct_enumeration':'Executed interpolation scores are cached once; masks are independently prepared; only finite sets and decimal2/3 are exhaustively enumerated','timing':'Single descriptive invocation per case/query; no runtime ranking or amortization threshold inferred'},indent=2),encoding='utf-8')
    for name,x,knots,y,ids,rec in cases():
        w=json.loads((Q/'results/v6/scipy_defect_certificates'/(name+'_affected.json')).read_text(encoding='utf-8'))
        scores=funcs['affected'](x,knots,kind='nearest')(x);gold=funcs['fixed'](x,knots,kind='nearest')(x)
        assert np.array_equal(scores,w['actual_scores']) and np.array_equal(gold,w['reference_scores'])
        t=time.perf_counter();audit=verify(y,gold,scores,ids,w['certificate']);verify_ms=1000*(time.perf_counter()-t)
        a=candidates(y,gold,DEFAULT);b=candidates(y,scores,DEFAULT)
        differs=lambda alpha:select(a,alpha,bool(y.sum()),DEFAULT)[2]!=select(b,alpha,bool(y.sum()),DEFAULT)[2]
        audits.append(dict(case_id=name,certificate_sha256=hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest(),verification=audit,verification_ms=verify_ms))
        for label,q in queries():
            t=time.perf_counter();r=answer(w['certificate'],q);query_ms=1000*(time.perf_counter()-t)
            t=time.perf_counter();s=smt_answer(a,b,q);smt_ms=1000*(time.perf_counter()-t)
            assert r['affected']==s['affected']
            for witness in [r['witness'],s['witness']]:
                if witness is not None:assert differs(F(witness))
            values=direct_values(q);count=None;t=time.perf_counter()
            if values is not None:
                count=sum(differs(alpha) for alpha in values);assert count==r['affected_count']
            enumeration_ms=1000*(time.perf_counter()-t) if values is not None else None
            rows.append(dict(case_id=name,query=label,allowed_count=r.get('allowed_count'),affected_count=r.get('affected_count'),affected=r['affected'],certificate_witness=r['witness'],smt_verdict=s['verdict'],smt_witness=s['witness'],direct_policies=len(values) if values is not None else 0,direct_affected=count,certificate_query_ms=query_ms,smt_build_solve_ms=smt_ms,direct_cached_mask_enumeration_ms=enumeration_ms))
        print('policy_domain',name,flush=True)
    with (R/'domain_query_results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (R/'domain_query_audits.json').write_text(json.dumps(audits,indent=2),encoding='utf-8')
    summary={'status':'PASS','workloads':len(audits),'queries_per_workload':len(queries()),'matched_query_answers':len(rows),'direct_policies_enumerated':sum(r['direct_policies'] for r in rows),'smt_unknown':0,'new_documented_defects':0,'study_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'query_source_sha256':hashlib.sha256((Q/'policy_domain_query.py').read_bytes()).hexdigest(),'by_query':[],'scope':'Functional diagnostic utility on existing controlled SciPy propagation fixtures. Scenario policies are not observed application requirements. SMT answers the same questions; no unique solver capability, speed superiority, measured developer benefit or new real-bug detection gain.'}
    for label,q in queries():
        selected=[r for r in rows if r['query']==label];summary['by_query'].append(dict(query=label,workloads=len(selected),affected_workloads=sum(r['affected'] for r in selected),allowed_count_per_workload=selected[0]['allowed_count'],affected_policy_workload_pairs=sum(r['affected_count'] for r in selected) if selected[0]['affected_count'] is not None else None))
    (R/'domain_query_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
