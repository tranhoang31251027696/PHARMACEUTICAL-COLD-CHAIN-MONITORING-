"""Run exact inherited/pipeline policies, controlled mutants, and timed certificates."""
from pathlib import Path
import sys,json,csv,time,hashlib,datetime,platform,tracemalloc,shutil
import importlib.metadata
from fractions import Fraction
from copy import deepcopy
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'));sys.path.insert(0,str(Q/'vendor'))
from policy_exact import compare_policies,at,DEFAULT,profile
from independent_oracle import verify,candidates,select
import decision_regression as current
from benchmark_baselines import b4_exact_comparator_workflow
R=Q/'results';R.mkdir(exist_ok=True);C=R/'certificates';C.mkdir(exist_ok=True)

def write_csv(name,rows):
    with (R/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def emit(name,obj):
    (R/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
def load(rec):
    f=Q/'inputs'/rec['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256'];d=np.load(f)
    return d['y'],d['old'],d['new'],d['ids'].tolist()
def savecert(name,cert):
    f=C/(name+'.json');f.write_text(json.dumps(cert,indent=2),encoding='utf-8');return hashlib.sha256(f.read_bytes()).hexdigest()

def policy_cases(records):
    rows=[];gridchecks=0;historical=[]
    historical=Q/'inputs/historical/counterfactual_policy_sensitivity_255_configs.csv'
    manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(historical.read_bytes()).hexdigest()==manifest['assets']['historical/counterfactual_policy_sensitivity_255_configs.csv']
    oldgrid=list(csv.DictReader(historical.open(encoding='utf-8-sig')))
    historical=[]
    for i,rec in enumerate(records):
        y,a,b,ids=load(rec);hi='.9' if rec['cohort'] in ['Public_WDBC','Independent_pipeline'] else '.8'
        t=time.perf_counter_ns();cert=compare_policies(y,a,b,hi=hi,ids=ids);ms=(time.perf_counter_ns()-t)/1e6
        validation=verify(y,a,b,ids,cert)
        oldrows=[r for r in oldgrid if r['case_id']==rec['case_id']]
        for r in oldrows:
            cell=at(cert,r['alpha']);assert (not cell['equal'])==(r['is_divergent']=='True');gridchecks+=1
            assert cell['old_n']==int(r['old_N']) and cell['new_n']==int(r['new_N'])
        sha=savecert(f'policy_{i:03}',cert)
        row=dict(case_id=rec['case_id'],cohort=rec['cohort'],n=len(y),domain_hi=hi,equivalent=cert['equivalent'],psc_exact=cert['psc_exact'],psc=cert['psc'],cells=len(cert['cells']),critical_values=len(cert['critical_values']),witness_cells=sum(not c['equal'] for c in cert['cells']),exact_ms=ms,oracle_probes=validation['probes'],certificate_file=f'certificates/policy_{i:03}.json',certificate_sha256=sha,old_grid_configs=len(oldrows),old_grid_divergent=sum(r['is_divergent']=='True' for r in oldrows))
        rows.append(row)
        if oldrows:historical.append(row)
        print('policy',i,rec['case_id'],'PSC',cert['psc_exact'],flush=True)
    assert gridchecks==255 and len(historical)==23
    write_csv('policy_cases.csv',rows);return rows

MUTANTS=[('strict_precision',{'precision':'strict'}),('threshold_gt',{'family':'gt'}),('reverse_tie_break',{'objective':'max_tp_min_n'}),('drop_middle_group',{'family':'drop_group'}),('split_score_ties',{'family':'split_ties'}),('tp_count_plus_one',{'count_offset':1}),('round_one_decimal',{}),('roundoff_tie_split',{}),('row_id_misalignment',{}),('identity_control',{}),('monotone_control',{}),('aligned_permutation_control',{})]
def mutation_cases(records):
    rows=[];j=0
    for rec in records:
        if rec['cohort']!='Independent_pipeline':continue
        y,a,_,ids=load(rec)
        for name,delta in MUTANTS:
            b=a.copy();spec={**DEFAULT,**delta};yy=y.copy();oi=ids.copy();ni=ids.copy();aa=a.copy();control=name.endswith('control')
            if name=='round_one_decimal':b=np.round(a,1)
            if name=='roundoff_tie_split':b=a+np.random.default_rng(4000+rec['seed']).choice([-1,0,1],len(a))*np.finfo(np.float32).eps/2
            if name=='row_id_misalignment':b=b[::-1].copy();ni=ni[::-1]
            if name=='monotone_control':b=3*a+2
            if name=='aligned_permutation_control':
                perm=np.random.default_rng(rec['seed']).permutation(len(y));yy=y[perm];aa=a[perm];b=b[perm];oi=[ids[k] for k in perm];ni=oi.copy()
            if name=='row_id_misalignment':
                detected=False
                try:compare_policies(yy,aa,b,ids=oi,new_ids=ni,new_spec=spec)
                except ValueError:detected=True
                assert detected
                rows.append(dict(case_id=rec['case_id'],pipeline=rec['pipeline'],seed=rec['seed'],mutant=name,control=False,contract_failure=True,policy_divergent='',psc='',snapshot_detected='',grid_detected='',score_b4_flag='',current_guard_flag='',exact_detected=detected,certificate_ms='',certificate_sha256=''));continue
            t=time.perf_counter_ns();cert=compare_policies(yy,aa,b,ids=oi,new_ids=ni,new_spec=spec);ms=(time.perf_counter_ns()-t)/1e6
            verify(yy,aa,b,oi,cert)
            # The fixed-grid harness observes the actual mutant selector output.
            oa=candidates(yy,aa,DEFAULT);ob=candidates(yy,b,spec);pos=bool(yy.sum())
            def differs(alpha):return select(oa,alpha,pos,DEFAULT)[2]!=select(ob,alpha,pos,spec)[2]
            snap=differs(Fraction(1,2));grid=any(differs(Fraction(v,100)) for v in range(30,91,5))
            b4=not b4_exact_comparator_workflow(aa,b)
            guard=current.compare(yy,aa,b,.5,mode='full',old_ids=np.array(oi),new_ids=np.array(ni))['regression_flag']
            if control:assert cert['equivalent'],'Valid control raised policy alarm'
            sha=savecert(f'mutation_{j:03}',cert);j+=1
            rows.append(dict(case_id=rec['case_id'],pipeline=rec['pipeline'],seed=rec['seed'],mutant=name,control=control,contract_failure=False,policy_divergent=not cert['equivalent'],psc=cert['psc'],snapshot_detected=snap,grid_detected=grid,score_b4_flag=b4,current_guard_flag=guard,exact_detected=not cert['equivalent'],certificate_ms=ms,certificate_sha256=sha))
        print('mutations',rec['case_id'],flush=True)
    write_csv('mutations.csv',rows);return rows

def benchmark():
    rows=[]
    # Actual certificate-producing divergence vs invariant paths. Inputs excluded
    # from tracing; full certificate construction and JSON serialization included.
    for n,g in [(1000,20),(10000,100),(100000,500)]:
        rng=np.random.default_rng(n+g);a=rng.integers(0,g,n)/(g-1);y=rng.integers(0,2,n);ids=list(range(n))
        for workload in ['invariant','divergent']:
            b=a.copy() if workload=='invariant' else a+rng.choice([-1,0,1],n)*1e-8
            for with_witness in [False,True]:
                compare_policies(y,a,b,ids=ids,with_witness=with_witness)
            for rep in range(10):
                for with_witness in rng.permutation([False,True]):
                    tracemalloc.start();t=time.perf_counter_ns();c=compare_policies(y,a,b,ids=ids,with_witness=bool(with_witness));payload=json.dumps(c);ms=(time.perf_counter_ns()-t)/1e6;peak=tracemalloc.get_traced_memory()[1]/2**20;tracemalloc.stop()
                    assert c['equivalent']==(workload=='invariant')
                    rows.append(dict(n=n,g=g,workload=workload,witness=bool(with_witness),replicate=rep,elapsed_ms=ms,peak_aux_mib=peak,bytes=len(payload.encode()),cells=len(c['cells']),witness_cells=sum(x['witness'] is not None for x in c['cells']),psc=c['psc']))
            print('benchmark',n,workload,flush=True)
    write_csv('certificate_timings.csv',rows)
    summaries=[]
    for key in sorted({(r['n'],r['g'],r['workload'],r['witness']) for r in rows}):
        rr=[r for r in rows if (r['n'],r['g'],r['workload'],r['witness'])==key];v=np.array([r['elapsed_ms'] for r in rr]);q=np.percentile(v,[25,75],method='linear')
        summaries.append(dict(n=key[0],g=key[1],workload=key[2],witness=key[3],repetitions=len(rr),median_ms=float(np.median(v)),iqr_ms=float(q[1]-q[0]),median_peak_mib=float(np.median([r['peak_aux_mib'] for r in rr])),median_witness_cells=float(np.median([r['witness_cells'] for r in rr]))))
    write_csv('certificate_timing_summary.csv',summaries);return summaries

def main():
    snapshot=R/'execution_source_snapshot';snapshot.mkdir(exist_ok=True)
    for source in [Path(__file__),Q/'src/policy_exact.py']:
        shutil.copy2(source,snapshot/source.name)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
    manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'));records=manifest['cases']
    policy=policy_cases(records);mutants=mutation_cases(records);timings=benchmark()
    tested=[r for r in mutants if not r['contract_failure']];div=[r for r in tested if r['policy_divergent']];controls=[r for r in tested if r['control']]
    summary={'status':'PASS','started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-t,
        'policy_cases':len(policy),'historical_grid_checks':255,'policy_sensitive_cases':sum(not r['equivalent'] for r in policy),
        'cohorts':{k:{'cases':len([r for r in policy if r['cohort']==k]),'sensitive':sum(not r['equivalent'] for r in policy if r['cohort']==k)} for k in sorted({r['cohort'] for r in policy})},
        'mutation_runs':len(mutants),'contract_failures_detected':sum(r['contract_failure'] and r['exact_detected'] for r in mutants),'policy_divergent_mutants':len(div),
        'observed_equivalent_mutants':sum(not r['policy_divergent'] and not r['control'] for r in tested),'valid_controls':len(controls),'policy_false_alarms_on_controls':sum(r['exact_detected'] for r in controls),
        'detections_on_policy_divergent':{k:sum(r[k] for r in div) for k in ['snapshot_detected','grid_detected','score_b4_flag','current_guard_flag','exact_detected']},
        'structural_flags_without_policy_divergence':{k:sum(r[k] for r in tested if not r['policy_divergent']) for k in ['score_b4_flag','current_guard_flag']},
        'benchmark_rows':len(timings)*10,'limitations':['Single host; descriptive latency under tracemalloc includes certificate serialization','Hand-designed mutants and synthetic perturbations, not naturally occurring releases','Repeated splits of three datasets are not independent external deployments','B4/current guard observe scores, not arbitrary changes inside selector code','Finite local evidence does not establish novelty, universal correctness, or journal acceptance'],
        'environment':{'python':sys.version,'numpy':np.__version__,'sklearn':importlib.metadata.version('scikit-learn'),'scipy':importlib.metadata.version('scipy'),'platform':platform.platform()},'frozen_input_generation_environment':manifest['environment']}
    emit('summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
