"""Measured batch reuse costs, including setup, on predeclared existing inputs.

No human productivity, production policy frequency, universal break-even point,
new defect corpus or independently optimized parametric tool is claimed.
"""
from pathlib import Path
from fractions import Fraction as F
import json,csv,time,random,hashlib,statistics
import numpy as np
import z3
from scipy_documented_defect import functions,cases
from policy_exact import compare_policies,DEFAULT
from streaming_checker import verify
from independent_oracle import candidates,select
from policy_domain_query import answer,contains
Q=Path(__file__).resolve().parent
CASE_IDS=['upstream_int8','unix_seconds_int32','small_int32_control',
          'pipeline_axis_wdbc_logistic_isotonic_seed0',
          'pipeline_axis_digits_svc_sigmoid_seed0',
          'pipeline_axis_generated_rf_quantized_seed0']
BATCHES=[1,8,32,128];REPEATS=5

def plans(kind,batch):
    result=[]
    for i in range(batch):
        if kind=='singleton':
            a=F(3,10)+F(3,5)*F(2*i+1,2*batch)
            result.append(dict(semantics='rational',kind='finite',values=[str(a)]))
        else:
            a=F(3,10)+F(11,20)*F(2*i+1,2*batch)
            result.append(dict(semantics='rational',kind='interval',lo=str(a),hi=str(a+F(1,20)),left_closed=i%2==0,right_closed=i%3!=0))
    return result

def direct_answer(a,b,positive,q,breaks):
    if q['kind']=='finite':probes=list(map(F,q['values']))
    else:
        lo,hi=F(q['lo']),F(q['hi']);cuts=sorted({lo,hi}|{v for v in breaks if lo<v<hi})
        probes=[v for v in cuts if contains(q,v)]+[(x+y)/2 for x,y in zip(cuts,cuts[1:])]
    for p in probes:
        if select(a,p,positive,DEFAULT)[2]!=select(b,p,positive,DEFAULT)[2]:return dict(affected=True,witness=str(p))
    return dict(affected=False,witness=None)

class IncrementalSMT:
    def __init__(self,a,b,positive):
        self.alpha=z3.Real('alpha');self.s=z3.Solver();self.s.set(timeout=30000)
        def winner(table):
            w=z3.IntVal(0)
            if positive:
                for p,k,n,bits in sorted(table,key=lambda t:(t[1],t[2])):w=z3.If(self.alpha<=z3.RealVal(str(p)),z3.IntVal(bits),w)
            return w
        self.s.add(self.alpha>=z3.RealVal('3/10'),self.alpha<=z3.RealVal('9/10'),winner(a)!=winner(b))
    def query(self,q):
        self.s.push()
        try:
            if q['kind']=='finite':self.s.add(z3.Or(*[self.alpha==z3.RealVal(v) for v in q['values']]))
            else:
                lo,hi=z3.RealVal(q['lo']),z3.RealVal(q['hi'])
                self.s.add(self.alpha>=lo if q['left_closed'] else self.alpha>lo,self.alpha<=hi if q['right_closed'] else self.alpha<hi)
            verdict=self.s.check()
            if verdict==z3.unknown:raise RuntimeError('Incremental Z3 unknown: '+self.s.reason_unknown())
            witness=None
            if verdict==z3.sat:
                v=self.s.model().eval(self.alpha);witness=str(F(v.numerator_as_long(),v.denominator_as_long()))
            return dict(affected=verdict==z3.sat,witness=witness)
        finally:self.s.pop()

def run(method,y,old,new,ids,requests):
    start=time.perf_counter_ns()
    if method=='checked_certificate':
        cert=compare_policies(y,old,new,ids=ids)
        # Include the in-memory serialization boundary and independent checking.
        cert=json.loads(json.dumps(cert,allow_nan=False));verify(y,old,new,ids,cert)
        def query(q):
            r=answer(cert,q);return dict(affected=r['affected'],witness=r['witness'])
    else:
        a=candidates(y,old,DEFAULT);b=candidates(y,new,DEFAULT);positive=bool(y.sum())
        if method=='direct_masks':
            breaks=sorted({p for p,k,n,bits in a+b if F(3,10)<=p<=F(9,10)})
            query=lambda q:direct_answer(a,b,positive,q,breaks)
        else:
            solver=IncrementalSMT(a,b,positive);query=solver.query
    prepared=time.perf_counter_ns();out=[query(q) for q in requests];end=time.perf_counter_ns()
    return out,dict(setup_ms=(prepared-start)/1e6,queries_ms=(end-prepared)/1e6,total_ms=(end-start)/1e6)

def main():
    R=Q/'results/v8';R.mkdir(parents=True,exist_ok=True);folder=R/'reuse_outputs';folder.mkdir(exist_ok=True)
    protocol=dict(case_ids=CASE_IDS,selection='Six fixed existing fixtures: upstream int8, Unix int32, small-int control, and seed-zero from each pipeline family. No timing/outcome-based filtering.',batch_sizes=BATCHES,repetitions=REPEATS,query_kinds=['singleton','continuous_window'],methods=['checked_certificate','direct_masks','incremental_z3'],request_generation='Deterministic distinct rational points or width-1/20 windows spread over [0.30,0.90]; alternating endpoint ownership; study scenarios, not observed deployment configurations.',contract='Same Boolean existence-of-divergence answer plus rational witness; counts/intersection enumeration are not required of the direct/SMT baselines. Certificate API still materializes its own intersections before projection.',timing='perf_counter_ns, no tracemalloc, one warmup per case/kind/method, five fresh setups per batch/method, seeded random method order. Common interpolation outside all timings. Direct and SMT prepare masks once per batch; incremental Z3 reuses base constraints with push/pop. Checked certificate includes construction, JSON roundtrip and independent verification once per batch. No query memoization; all requests within a batch are distinct. Disk I/O, human triage and dependency import excluded.',crossing_definition='First tested batch size with certificate total median below comparator, remaining below at every larger tested size. Discrete observed crossing only, no extrapolation or population significance.')
    (R/'reuse_protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    funcs,_,_=functions();source_cases={row[0]:row for row in cases()};assert set(CASE_IDS)<=source_cases.keys()
    raw=[];rng=random.Random(20261030);payloads={}
    for name in CASE_IDS:
        _,x,scores,y,ids,rec=source_cases[name];old=funcs['fixed'](x,scores,kind='nearest')(x);new=funcs['affected'](x,scores,kind='nearest')(x)
        w=json.loads((Q/'results/v6/scipy_defect_certificates'/(name+'_affected.json')).read_text(encoding='utf-8'))
        assert np.array_equal(old,w['reference_scores']) and np.array_equal(new,w['actual_scores'])
        a=candidates(y,old,DEFAULT);b=candidates(y,new,DEFAULT);pos=bool(y.sum())
        for kind in protocol['query_kinds']:
            methods=protocol['methods'];warm=plans(kind,1)
            for method in methods:run(method,y,old,new,ids,warm)
            for batch in BATCHES:
                requests=plans(kind,batch);expected=[answer(w['certificate'],q)['affected'] for q in requests]
                plan_key=f'{name}__{kind}__b{batch}';payloads[plan_key]=dict(case_id=name,kind=kind,batch=batch,requests=requests,expected=expected)
                for rep in range(REPEATS):
                    order=methods.copy();rng.shuffle(order)
                    for rank,method in enumerate(order):
                        out,timing=run(method,y,old,new,ids,requests)
                        assert [r['affected'] for r in out]==expected
                        for q,r in zip(requests,out):
                            if r['witness'] is not None:
                                v=F(r['witness']);assert select(a,v,pos,DEFAULT)[2]!=select(b,v,pos,DEFAULT)[2]
                                assert v in map(F,q['values']) if q['kind']=='finite' else contains(q,v)
                        output=folder/f'{plan_key}__r{rep}__{method}.json';output.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
                        raw.append(dict(case_id=name,kind=kind,batch=batch,replicate=rep,method=method,order=rank,**timing,affected_queries=sum(expected),output_file=output.name,output_sha256=hashlib.sha256(output.read_bytes()).hexdigest()))
                print('reuse_cost',name,kind,batch,flush=True)
    (R/'reuse_query_plans.json').write_text(json.dumps(payloads,indent=2),encoding='utf-8')
    with (R/'reuse_raw.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]));writer.writeheader();writer.writerows(raw)
    groups=[]
    for name in CASE_IDS:
        for kind in protocol['query_kinds']:
            for batch in BATCHES:
                for method in protocol['methods']:
                    selected=[r for r in raw if (r['case_id'],r['kind'],r['batch'],r['method'])==(name,kind,batch,method)];assert len(selected)==REPEATS
                    entry=dict(case_id=name,kind=kind,batch=batch,method=method,repetitions=REPEATS)
                    for phase in ['setup_ms','queries_ms','total_ms']:
                        values=[r[phase] for r in selected];entry['median_'+phase]=statistics.median(values);entry['iqr_'+phase]=float(np.quantile(values,.75)-np.quantile(values,.25))
                    groups.append(entry)
    with (R/'reuse_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(groups[0]));writer.writeheader();writer.writerows(groups)
    lookup={(r['case_id'],r['kind'],r['batch'],r['method']):r['median_total_ms'] for r in groups};crossings=[]
    for name in CASE_IDS:
        for kind in protocol['query_kinds']:
            for other in ['direct_masks','incremental_z3']:
                crossing=next((b for b in BATCHES if all(lookup[name,kind,t,'checked_certificate']<lookup[name,kind,t,other] for t in BATCHES if t>=b)),None)
                crossings.append(dict(case_id=name,kind=kind,comparator=other,first_observed_sustained_batch=crossing))
    result=dict(status='PASS',case_count=6,query_kinds=2,batch_sizes=BATCHES,repetitions=REPEATS,raw_records=len(raw),summary_groups=len(groups),matched_answers=sum(r['batch'] for r in raw),smt_unknown=0,observed_crossings=crossings,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Computational batch-reuse costs on six existing controlled fixtures, with initial construction/verification included. No human productivity, production requirements, industrial effectiveness, universal threshold or optimized external-tool superiority.')
    (R/'reuse_cost_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
