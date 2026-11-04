"""Freeze inherited arrays and train three distinct, split-safe pipeline families."""
from pathlib import Path
import sys,json,csv,hashlib,platform
import numpy as np
from sklearn.datasets import load_digits,make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
import sklearn,scipy

Q=Path(__file__).resolve().parent;P=Q.parent/'SUBMISSION_PACKAGE'
OUT=Q/'inputs';OUT.mkdir(exist_ok=True)
records=[];source_hashes={}
def source(p):
    source_hashes[str(p.relative_to(Q.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
def save(cid,cohort,y,a,b,**meta):
    idx=len(records);fn=f'case_{idx:03}.npz';ids=np.arange(len(y)).astype(str)
    np.savez_compressed(OUT/fn,y=y,old=a,new=b,ids=ids)
    records.append(dict(case_id=cid,cohort=cohort,file=fn,n=len(y),sha256=hashlib.sha256((OUT/fn).read_bytes()).hexdigest(),**meta))

def main():
    rd=P/'02_Replication_Package/src/research_round9/results'
    index=rd/'calibrator_index.json';source(index);npz=rd/'numerical_inputs.npz';source(npz);data=np.load(npz)
    table=P/'02_Replication_Package/outputs/13_compared_csv_tables/08_retained_hierarchy.csv';source(table)
    rows=list(csv.DictReader(table.open(encoding='utf-8-sig')))
    for c in json.loads(index.read_text(encoding='utf-8'))['calibrators']:
        sf=rd/(c['id']+'_settings.npz')
        if not sf.exists():continue
        source(sf);scores=np.load(sf);y=data[c['prefix']+'_tuning_y'];a=scores['scipy_1.18.1_float32__tuning']
        for row in rows:
            if row['calibrator']!=c['id'] or row['setting']=='scipy_1.18.1_float32':continue
            save(c['id']+'__'+row['setting'],'Retained',y,a,scores[row['setting']+'__tuning'],previous_frontier_only=row['frontier_changed']=='True' and row['reselected_decisions_changed']=='0')
    sf=P/'03_Evaluation_Datasets/02_Synthetic_Boundary_Fixtures/perturbation_fixtures.json';source(sf)
    for item in json.loads(sf.read_text(encoding='utf-8')):
        save(item['id'],'Synthetic',np.array(item['y']),np.array(item['old']),np.array(item['new']))
    f=P/'03_Evaluation_Datasets/03_Public_WDBC_Benchmark/public_pilot_inputs.npz';source(f);y=np.load(f)['y']
    files=[P/f'02_Replication_Package/src/research_round12/results/public_scipy_{v}.npy' for v in ['1.18.1','1.15.3']]
    for f in files:source(f)
    save('public_wdbc_pilot','Public_WDBC',y,np.load(files[0]),np.load(files[1]))
    # Each family uses independent fit/calibration/evaluation rows. Seeds are
    # repeated splits, not independent datasets or real software releases.
    wdbc=P/'03_Evaluation_Datasets/03_Public_WDBC_Benchmark/public_wdbc_snapshot.csv';source(wdbc)
    arr=np.loadtxt(wdbc,delimiter=',',skiprows=1);digits=load_digits()
    for family in ['wdbc_logistic_isotonic','digits_svc_sigmoid','generated_rf_quantized']:
        for seed in range(10):
            if family.startswith('wdbc'):X,y=arr[:,:-1],arr[:,-1].astype(int);method='isotonic';base=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed))
            elif family.startswith('digits'):X,y=digits.data,(digits.target==0).astype(int);method='sigmoid';base=make_pipeline(StandardScaler(),LinearSVC(random_state=seed,max_iter=5000))
            else:
                X,y=make_classification(n_samples=2400,n_features=16,n_informative=8,n_redundant=4,weights=[.92,.08],class_sep=.9,flip_y=.02,random_state=seed)
                base=RandomForestClassifier(n_estimators=50,max_depth=6,random_state=seed,n_jobs=1);method=None
            fit,rest=train_test_split(np.arange(len(y)),test_size=.5,stratify=y,random_state=seed)
            cal,ev=train_test_split(rest,test_size=.5,stratify=y[rest],random_state=seed+100)
            assert not(set(fit)&set(cal) or set(fit)&set(ev) or set(cal)&set(ev))
            base.fit(X[fit],y[fit])
            model=base if method is None else CalibratedClassifierCV(FrozenEstimator(base),method=method)
            if method:model.fit(X[cal],y[cal])
            a=model.predict_proba(X[ev])[:,1]
            if method is None:a=np.round(a,2)
            b=a.astype(np.float32).astype(float)
            save(f'{family}_seed{seed}','Independent_pipeline',y[ev],a,b,pipeline=family,seed=seed,fit_n=len(fit),calibration_n=len(cal) if method else 0,reserved_n=0 if method else len(cal),eval_n=len(ev),positive_n=int(y[ev].sum()),groups=len(np.unique(a)),split_indices={'fit':fit.tolist(),'calibration_or_reserved':cal.tolist(),'evaluation':ev.tolist()},warning='Small isotonic calibration set; this is a structural verification workload, not a calibration-quality claim.' if method=='isotonic' else '')
            print('trained',family,seed,flush=True)
    manifest={'cases':records,'source_sha256':source_hashes,'environment':{'python':sys.version,'numpy':np.__version__,'sklearn':sklearn.__version__,'scipy':scipy.__version__,'platform':platform.platform()},'assets':{'historical/counterfactual_policy_sensitivity_255_configs.csv':hashlib.sha256((OUT/'historical/counterfactual_policy_sensitivity_255_configs.csv').read_bytes()).hexdigest()},'scope':'Frozen inherited arrays and newly trained local benchmark pipelines; not blind external or deployment validation.'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Frozen cases:',len(records),flush=True)
if __name__=='__main__':main()
