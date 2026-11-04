"""Onboard the installed scikit-learn threshold optimizer through its public API.

No optimizer body is copied or modified. The custom scorer defines our contract;
finite threshold coverage and no-feasible mapping are explicit adapter duties.
"""
from pathlib import Path
from fractions import Fraction
import json,csv,sys,time,hashlib,inspect,ast
import numpy as np,sklearn
from sklearn.base import ClassifierMixin,BaseEstimator
from sklearn.metrics import make_scorer
from sklearn.model_selection import TunedThresholdClassifierCV
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import candidates,select
from policy_exact import DEFAULT

class ScoreCarrier(ClassifierMixin,BaseEstimator):
    def fit(self,X,y):self.classes_=np.array([0,1]);self.n_features_in_=1;return self
    def predict_proba(self,X):return np.column_stack([1-X[:,0],X[:,0]])

def admission(scores,thresholds,cv='prefit',refit=False):
    if cv!='prefit' or refit:raise ValueError('UNSUPPORTED_RESAMPLING_CONTRACT')
    if isinstance(thresholds,(int,np.integer)):raise ValueError('UNSUPPORTED_SAMPLED_THRESHOLD_GRID')
    if not np.array_equal(np.asarray(thresholds),np.unique(scores)):
        raise ValueError('INCOMPLETE_OR_DIFFERENT_CANDIDATE_SET')

def execute(y,s,alpha):
    thresholds=np.unique(s);admission(s,thresholds);n=len(y);calls=[]
    def utility(yy,pred):
        count=int(np.count_nonzero(pred));tp=int(np.asarray(yy)[np.asarray(pred,dtype=bool)].sum())
        feasible=count>0 and tp*alpha.denominator>=count*alpha.numerator
        calls.append((tp,count,bool(feasible)))
        return float(tp*(n+1)+count) if feasible else -1.0
    X=s.reshape(-1,1);carrier=ScoreCarrier().fit(X,y)
    model=TunedThresholdClassifierCV(carrier,scoring=make_scorer(utility),thresholds=thresholds,cv='prefit',refit=False,store_cv_results=True,n_jobs=1)
    model.fit(X,y)
    if not np.array_equal(model.cv_results_['thresholds'],thresholds):raise ValueError('OPTIMIZER_CHANGED_CANDIDATE_GRID')
    mask=np.zeros(n,bool) if model.best_score_<0 or not y.sum() else model.predict(X).astype(bool)
    return int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little'),calls

def main():
    R=Q/'results/v4';R.mkdir(exist_ok=True);t=time.perf_counter();source=inspect.getsource(TunedThresholdClassifierCV);sourcefile=Path(inspect.getfile(TunedThresholdClassifierCV));rows=[];certs=[]
    records=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))['cases']
    for rec in records:
        if rec.get('seed')!=0:continue
        input_file=Q/'inputs'/rec['file'];assert hashlib.sha256(input_file.read_bytes()).hexdigest()==rec['sha256']
        d=np.load(input_file);y=d['y'][:48];s=d['old'][:48];ids=d['ids'][:48].tolist()
        if len(np.unique(y))<2:raise ValueError('Chosen prefix lacks both labels; report unsupported instead of selecting another outcome')
        gold=candidates(y,s,DEFAULT);lo=Fraction(3,10);hi=Fraction(9,10);breaks=sorted({lo,hi}|{p for p,*_ in gold if lo<p<hi});probes=sorted(set(breaks)|{(a+b)/2 for a,b in zip(breaks,breaks[1:])});failures=0;callback_calls=0;observations=[]
        started=time.perf_counter_ns()
        for a in probes:
            actual,calls=execute(y,s,a);expected=select(gold,a,True,DEFAULT)[2];callback_calls+=len(calls)
            if actual!=expected:failures+=1
            observations.append({'alpha':str(a),'expected_bits':hex(expected),'actual_bits':hex(actual),'scorer_calls':len(calls)})
        assert failures==0
        cert={'schema':'external-threshold-optimizer-integration/1','case_id':rec['case_id'],'source_input_sha256':rec['sha256'],'slice':'first 48 fixed rows','source_class_sha256':hashlib.sha256(source.encode()).hexdigest(),'sklearn':sklearn.__version__,'ids':ids,'policy_probes':observations,'conforms':True,'adapter_scope':'Exact finite thresholds via public API, custom exact-ratio scorer, prefit and no-feasible abstention mapping. Not the library default tuning objective or cross-validation configuration.'}
        f=R/(rec['case_id']+'_optimizer.json');f.write_text(json.dumps(cert,indent=2),encoding='utf-8');certs.append(f.name)
        rows.append({'pipeline':rec['pipeline'],'observations':len(y),'thresholds':len(np.unique(s)),'policy_probes':len(probes),'optimizer_fit_calls':len(probes),'scorer_callbacks':callback_calls,'mismatches':failures,'elapsed_ms':(time.perf_counter_ns()-started)/1e6})
    rejected=[];sample=np.array([.1,.1,.3,.8])
    for label,thresholds,cv,refit in [('default_grid',100,'prefit',False),('missing_threshold',np.array([.1,.8]),'prefit',False),('cross_validation',np.unique(sample),3,False),('refit',np.unique(sample),'prefit',True)]:
        try:admission(sample,thresholds,cv,refit)
        except ValueError as e:rejected.append({'case':label,'status':'UNSUPPORTED','reason':str(e)})
        else:raise AssertionError('Unsupported configuration admitted')
    # A second project's current packaging constraint is an onboarding barrier,
    # not evidence that its selector is wrong. Do not silently bypass it.
    project=Q/'vendor/external_eval_toolkit/pyproject.toml'
    import tomllib,platform
    from packaging.specifiers import SpecifierSet
    meta=tomllib.loads(project.read_text(encoding='utf-8'));requirement=meta['project']['requires-python'];compatible=SpecifierSet(requirement).contains(platform.python_version())
    second={'project':'eval-toolkit','requires_python':requirement,'runtime_python':platform.python_version(),'status':'RUNTIME_COMPATIBLE_NOT_EVALUATED' if compatible else 'UNSUPPORTED_RUNTIME','full_package_executed':False,'policy_certificate_issued':False}
    with (R/'onboarding_workloads.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    own=Path(__file__).read_text(encoding='utf-8');tree=ast.parse(own);functions=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    summary={'status':'PASS','external_selector':'sklearn.model_selection.TunedThresholdClassifierCV','library_version':sklearn.__version__,'source_file_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'source_class_sha256':hashlib.sha256(source.encode()).hexdigest(),'upstream_source_edits':0,'public_configuration_hooks':['prefit score carrier','custom objective scorer','complete candidate threshold array','explicit infeasible abstention mapping'],'workloads':rows,'total_policy_probes':sum(r['policy_probes'] for r in rows),'mismatches':sum(r['mismatches'] for r in rows),'unsupported_configurations':rejected,'second_project':second,'adapter_physical_lines':len(own.splitlines()),'adapter_top_level_definitions':functions,'elapsed_seconds':time.perf_counter()-t,'effort_scope':'Observed code/configuration artifacts and timed execution, not measured programmer-hours or a multi-team usability study. Custom scorer and wrapper remain trusted integration code.'}
    (R/'onboarding_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
