"""Verify fresh dependency-version outputs; no assumption that difference is a bug."""
from pathlib import Path
import sys,json,csv,hashlib
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from policy_exact import compare_policies
from independent_oracle import verify

def main():
    m=json.loads((Q/'inputs/version_inputs/manifest.json').read_text(encoding='utf-8'));R=Q/'results/v2';outputs={}
    for ver in ['1.15.3','1.18.1']:
        d=R/('scipy_'+ver);runtime=json.loads((d/'runtime.json').read_text(encoding='utf-8'));assert runtime['scipy']==ver
        assert hashlib.sha256((d/'scores.npz').read_bytes()).hexdigest()==runtime['scores_sha256'];outputs[ver]=np.load(d/'scores.npz')
    rows=[];folder=R/'version_certificates';folder.mkdir(exist_ok=True)
    for rec in m['cases']:
        inp=np.load(Q/'inputs/version_inputs'/rec['file']);y=inp['y'];cid=rec['case_id'];a=outputs['1.15.3'][cid];b=outputs['1.18.1'][cid];ids=list(range(len(y)))
        cert=compare_policies(y,a,b,ids=ids);verify(y,a,b,ids,cert)
        f=folder/(cid+'.json');f.write_text(json.dumps(cert,indent=2),encoding='utf-8')
        rows.append(dict(case_id=cid,old_version='1.15.3',new_version='1.18.1',n=len(y),score_rows_changed=int(np.count_nonzero(a!=b)),max_score_difference=float(np.max(np.abs(a.astype(float)-b.astype(float)))),policy_divergent=not cert['equivalent'],psc_exact=cert['psc_exact'],certificate_file=f.relative_to(Q).as_posix(),confirmed_library_bug=False))
    with (R/'version_comparisons.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    s={'status':'PASS','fresh_version_comparisons':len(rows),'score_different_cases':sum(r['score_rows_changed']>0 for r in rows),'policy_divergent_cases':sum(r['policy_divergent'] for r in rows),'confirmed_real_bugs':0,'scope':'Actual dependency binaries executed locally on inherited fixed inputs; differential behavior, not ground truth of a library defect or an independent deployment.'}
    (R/'version_summary.json').write_text(json.dumps(s,indent=2),encoding='utf-8');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
