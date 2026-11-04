"""Separate query-API cost from certificate assurance on the existing V8 plans."""
from pathlib import Path
from fractions import Fraction as F
import json,csv,time,random,hashlib,statistics
import numpy as np
from reuse_cost_study import CASE_IDS,BATCHES,REPEATS,plans,run as old_run
from scipy_documented_defect import functions,cases
from policy_exact import compare_policies,DEFAULT
from independent_oracle import candidates,select
from policy_domain_query import answer,contains
from verified_boolean_query import VerifiedBooleanIndex
Q=Path(__file__).resolve().parent
METHODS=['checked_certificate','boolean_certificate','direct_masks','incremental_z3']

def run(method,y,old,new,ids,requests):
    if method!='boolean_certificate':return old_run(method,y,old,new,ids,requests)
    start=time.perf_counter_ns();cert=compare_policies(y,old,new,ids=ids)
    cert=json.loads(json.dumps(cert,allow_nan=False));index=VerifiedBooleanIndex(y,old,new,ids,cert)
    prepared=time.perf_counter_ns();out=[index.query(q) for q in requests];end=time.perf_counter_ns()
    return out,dict(setup_ms=(prepared-start)/1e6,queries_ms=(end-prepared)/1e6,total_ms=(end-start)/1e6)

def main():
    R=Q/'results/v9';R.mkdir(parents=True,exist_ok=True);folder=R/'boolean_outputs';folder.mkdir(exist_ok=True)
    protocol=dict(case_ids=CASE_IDS,batch_sizes=BATCHES,repetitions=REPEATS,methods=METHODS,request_protocol='Exact same six V8 inputs and deterministic singleton/window plans; no outcome or timing filtering. 2,028 unique case/query plans are reused, not new workloads.',matched_assurance_panel='checked_certificate versus boolean_certificate: both construct a complete core diagnostic certificate, perform JSON roundtrip and independent full verification once per batch. Boolean route additionally freezes/merges/indexes unequal cells; both answer existence plus rational witness.',workflow_cost_panel='Four implementations answer the same Boolean question but do not have equal assurance obligations. Direct masks and incremental Z3 do not produce or independently verify a complete certificate. These are request-cost comparisons, not matched-assurance verification rankings.',timing='One warmup per case/type/method, 5 fresh setups per batch/method, seeded randomized method order. Setup/query/total retained separately; no tracemalloc. Same executed interpolation outputs outside all timers. No result memoization; requests within a batch differ. Imports, disk I/O and human work excluded.',scope='API cost isolation on existing controlled fixtures. No new algorithmic primitive, independent developer/production requirement evidence, defect count or universal speed claim.')
    (R/'boolean_protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8');funcs,_,_=functions();source_cases={r[0]:r for r in cases()};raw=[];saved_plans={};rng=random.Random(20261030)
    for name in CASE_IDS:
        _,x,scores,y,ids,rec=source_cases[name];old=funcs['fixed'](x,scores,kind='nearest')(x);new=funcs['affected'](x,scores,kind='nearest')(x)
        wrapper=json.loads((Q/'results/v6/scipy_defect_certificates'/(name+'_affected.json')).read_text(encoding='utf-8'))
        assert np.array_equal(old,wrapper['reference_scores']) and np.array_equal(new,wrapper['actual_scores'])
        a=candidates(y,old,DEFAULT);b=candidates(y,new,DEFAULT);positive=bool(y.sum())
        for kind in ['singleton','continuous_window']:
            for method in METHODS:run(method,y,old,new,ids,plans(kind,1))
            for batch in BATCHES:
                requests=plans(kind,batch);expected=[answer(wrapper['certificate'],q)['affected'] for q in requests];key=f'{name}__{kind}__b{batch}'
                saved_plans[key]=dict(case_id=name,kind=kind,batch=batch,requests=requests,expected=expected)
                for rep in range(REPEATS):
                    order=METHODS.copy();rng.shuffle(order)
                    for rank,method in enumerate(order):
                        out,timing=run(method,y,old,new,ids,requests);assert [r['affected'] for r in out]==expected
                        for q,r in zip(requests,out):
                            if r['witness'] is not None:
                                value=F(r['witness']);assert select(a,value,positive,DEFAULT)[2]!=select(b,value,positive,DEFAULT)[2]
                                assert value in map(F,q['values']) if q['kind']=='finite' else contains(q,value)
                        path=folder/f'{key}__r{rep}__{method}.json';path.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
                        raw.append(dict(case_id=name,kind=kind,batch=batch,replicate=rep,method=method,order=rank,**timing,affected_queries=sum(expected),output_file=path.name,output_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
                print('boolean_api_cost',name,kind,batch,flush=True)
    (R/'boolean_query_plans.json').write_text(json.dumps(saved_plans,indent=2),encoding='utf-8')
    with (R/'boolean_raw.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]));writer.writeheader();writer.writerows(raw)
    groups=[]
    for name in CASE_IDS:
        for kind in ['singleton','continuous_window']:
            for batch in BATCHES:
                for method in METHODS:
                    selected=[r for r in raw if (r['case_id'],r['kind'],r['batch'],r['method'])==(name,kind,batch,method)];assert len(selected)==5
                    entry=dict(case_id=name,kind=kind,batch=batch,method=method,repetitions=5)
                    for phase in ['setup_ms','queries_ms','total_ms']:
                        values=[r[phase] for r in selected];entry['median_'+phase]=statistics.median(values);entry['iqr_'+phase]=float(np.quantile(values,.75)-np.quantile(values,.25))
                    groups.append(entry)
    with (R/'boolean_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(groups[0]));writer.writeheader();writer.writerows(groups)
    lookup={(r['case_id'],r['kind'],r['batch'],r['method']):r for r in groups};paired=[];workflow=[]
    for name in CASE_IDS:
        for kind in ['singleton','continuous_window']:
            old=lookup[name,kind,128,'checked_certificate'];new=lookup[name,kind,128,'boolean_certificate']
            paired.append(dict(case_id=name,kind=kind,batch=128,query_phase_speedup=old['median_queries_ms']/new['median_queries_ms'],total_speedup=old['median_total_ms']/new['median_total_ms']))
    for batch in BATCHES:
        for kind in ['singleton','continuous_window']:
            for other in ['checked_certificate','direct_masks','incremental_z3']:
                wins=sum(lookup[name,kind,batch,'boolean_certificate']['median_total_ms']<lookup[name,kind,batch,other]['median_total_ms'] for name in CASE_IDS)
                workflow.append(dict(batch=batch,kind=kind,comparator=other,boolean_certificate_faster_total_cases=wins,cases=6,assurance_matched=other=='checked_certificate'))
    result=dict(status='PASS',case_count=6,query_kinds=2,batch_sizes=BATCHES,repetitions=5,methods=METHODS,raw_records=len(raw),summary_groups=len(groups),unique_case_query_plans=2028,matched_method_answers=sum(r['batch'] for r in raw),smt_unknown=0,paired_certificate_comparisons=paired,workflow_comparisons=workflow,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),index_source_sha256=hashlib.sha256((Q/'verified_boolean_query.py').read_bytes()).hexdigest(),v8_baseline_source_sha256=hashlib.sha256((Q/'reuse_cost_study.py').read_bytes()).hexdigest(),scope=protocol['scope'])
    (R/'boolean_cost_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
