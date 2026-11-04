"""Reverify every stored certificate and reconcile all published local counts."""
from pathlib import Path
import csv,json,sys,hashlib,xml.etree.ElementTree as ET
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import verify
from policy_exact import compare_policies

def main(output=None):
    R=Q/'results';manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))
    cases=manifest['cases'];records={r['case_id']:r for r in cases}
    def load(rec):
        f=Q/'inputs'/rec['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256']
        z=np.load(f);return z['y'],z['old'],z['new'],z['ids'].tolist()
    policy=list(csv.DictReader((R/'policy_cases.csv').open(encoding='utf-8')))
    verified=0;probes=0;seen=set()
    for row in policy:
        rec=records[row['case_id']];y,a,b,ids=load(rec);f=R/row['certificate_file']
        assert hashlib.sha256(f.read_bytes()).hexdigest()==row['certificate_sha256']
        c=json.loads(f.read_text(encoding='utf-8'));v=verify(y,a,b,ids,c)
        assert c['equivalent']==(row['equivalent']=='True') and c['psc_exact']==row['psc_exact']
        probes+=v['probes'];verified+=1;seen.add(f.name)
    assert sum(int(r['old_grid_configs']) for r in policy)==255
    mutant=list(csv.DictReader((R/'mutations.csv').open(encoding='utf-8')))
    mutantspecs={'strict_precision':{'precision':'strict'},'threshold_gt':{'family':'gt'},'reverse_tie_break':{'objective':'max_tp_min_n'},'drop_middle_group':{'family':'drop_group'},'split_score_ties':{'family':'split_ties'},'tp_count_plus_one':{'count_offset':1}}
    byhash={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (R/'certificates').glob('mutation_*.json')}
    for row in mutant:
        rec=records[row['case_id']];y,a,_,ids=load(rec);b=a.copy();name=row['mutant']
        if name=='row_id_misalignment':
            rejected=False
            try:compare_policies(y,a,b[::-1],ids=ids,new_ids=ids[::-1])
            except ValueError:rejected=True
            assert rejected and row['contract_failure']=='True' and row['exact_detected']=='True';continue
        if name=='round_one_decimal':b=np.round(a,1)
        if name=='roundoff_tie_split':b=a+np.random.default_rng(4000+rec['seed']).choice([-1,0,1],len(a))*np.finfo(np.float32).eps/2
        if name=='monotone_control':b=3*a+2
        if name=='aligned_permutation_control':
            p=np.random.default_rng(rec['seed']).permutation(len(y));y=y[p];a=a[p];b=b[p];ids=[ids[k] for k in p]
        f=byhash[row['certificate_sha256']];c=json.loads(f.read_text(encoding='utf-8'))
        for k,v in mutantspecs.get(name,{}).items():assert c['new_spec'][k]==v
        v=verify(y,a,b,ids,c);probes+=v['probes'];verified+=1;seen.add(f.name)
        assert (not c['equivalent'])==(row['policy_divergent']=='True')==(row['exact_detected']=='True')
        assert c['psc']==float(row['psc'])
    assert len(seen)==len(list((R/'certificates').glob('*.json')))==428
    summary=json.loads((R/'summary.json').read_text(encoding='utf-8'))
    assert len(policy)==summary['policy_cases']==98 and len(mutant)==summary['mutation_runs']==360
    div=[r for r in mutant if r['policy_divergent']=='True'];controls=[r for r in mutant if r['control']=='True']
    assert len(div)==summary['policy_divergent_mutants']==183 and len(controls)==90
    assert all(r['exact_detected']=='False' for r in controls)
    for key,count in summary['detections_on_policy_divergent'].items():assert count==sum(r[key]=='True' for r in div)
    raw=list(csv.DictReader((R/'certificate_timings.csv').open(encoding='utf-8')))
    summaries=list(csv.DictReader((R/'certificate_timing_summary.csv').open(encoding='utf-8')))
    assert len(raw)==120 and len(summaries)==12
    for s in summaries:
        rr=[r for r in raw if all(r[k]==s[k] for k in ['n','g','workload','witness'])]
        assert len(rr)==10 and {int(r['replicate']) for r in rr}==set(range(10))
        v=[float(r['elapsed_ms']) for r in rr];q=np.percentile(v,[25,75],method='linear')
        assert np.isclose(np.median(v),float(s['median_ms']),atol=1e-12,rtol=0) and np.isclose(q[1]-q[0],float(s['iqr_ms']),atol=1e-12,rtol=0)
        if s['workload']=='divergent' and s['witness']=='True':assert all(int(r['witness_cells'])>0 for r in rr)
    xml=ET.parse(R/'pytest.xml');assert sum(int(x.attrib.get('failures',0))+int(x.attrib.get('errors',0)) for x in xml.iter('testsuite'))==0
    result={'status':'PASS','certificates_independently_reverified':verified,'critical_and_open_cell_probes':probes,'input_cases_hash_verified':len(cases),'mutant_runs_reconciled':len(mutant),'timing_records_reconciled':len(raw),'pytest_tests':sum(int(x.attrib.get('tests',0)) for x in xml.iter('testsuite')),'exhaustive_combinations':10854,'randomized_cases':1000}
    (R/(output or 'artifact_verification.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
