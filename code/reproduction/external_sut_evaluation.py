"""Documented scikit-learn #23213 case using pinned upstream function bodies.

Historical functions run with the installed counting backend, validated against
direct masks. This is isolated source replay, not historical binary execution.
"""
from pathlib import Path
from fractions import Fraction
import ast,json,hashlib,sys,csv,warnings,time
import numpy as np
import sklearn
from sklearn.metrics import precision_recall_curve,confusion_matrix_at_thresholds
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import candidates,select
from policy_exact import DEFAULT

def _binary_clf_curve(y,s,**kwargs):
    # Compatibility bridge: sklearn 1.9 exposes the counting backend publicly.
    # The upstream historical PR-curve function body is not modified.
    _,fps,_,tps,thresholds=confusion_matrix_at_thresholds(y,s,**kwargs)
    return fps,tps,thresholds

def upstream_functions():
    folder=Q/'vendor/external_sklearn';m=json.loads((folder/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'));out={}
    for version,key in [('affected','1.0.2'),('fixed','23214_merged')]:
        name=next(n for n in m[key]['files'] if n.endswith('_ranking.py'))
        source=(folder/name).read_bytes();assert hashlib.sha256(source).hexdigest()==m[key]['files'][name]['sha256']
        tree=ast.parse(source.decode());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='precision_recall_curve')
        assert not f.decorator_list
        ns={'np':np,'warnings':warnings,'_binary_clf_curve':_binary_clf_curve}
        exec(compile(ast.Module(body=[f],type_ignores=[]),str(folder/name),'exec'),ns)
        out[version]=(ns['precision_recall_curve'],m[key]['files'][name]['sha256'],m[key]['commit'])
    return out

def actual_table(function,y,s):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',FutureWarning)
        p,r,thresholds=function(y,s)
    table=[]
    for j,t in enumerate(thresholds):
        mask=s>=t;n=int(mask.sum());k=int(y[mask].sum())
        if not n:raise ValueError('Unexpected empty threshold candidate')
        assert np.isclose(p[j],k/n,rtol=0,atol=1e-14)
        assert np.isclose(r[j],k/int(y.sum()),rtol=0,atol=1e-14)
        bits=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little')
        table.append((Fraction(k,n),k,n,bits))
    return table,np.asarray(thresholds)

def evaluate(y,s,ids,record,functions):
    expected=candidates(y,s,DEFAULT);pos=bool(y.sum());lo=Fraction(3,10);hi=Fraction(9,10);rows=[]
    fixed_thresholds=None
    for variant in ['fixed','affected','installed_current']:
        if variant=='installed_current':function=precision_recall_curve;sourcehash=None;commit=None
        else:function,sourcehash,commit=functions[variant]
        actual,thresholds=actual_table(function,y,s)
        if variant=='fixed':fixed_thresholds=thresholds
        if variant=='installed_current':assert np.array_equal(thresholds,fixed_thresholds)
        events=sorted({lo,hi}|{p for p,*_ in expected+actual if lo<p<hi});probes=sorted(set(events)|{(a+b)/2 for a,b in zip(events,events[1:])})
        findings=[];bad={}
        for alpha in probes:
            gold=select(expected,alpha,pos,DEFAULT);observed=select(actual,alpha,pos,DEFAULT);xor=gold[2]^observed[2];i=(xor&-xor).bit_length()-1 if xor else None;bad[alpha]=bool(xor)
            findings.append(dict(alpha=str(alpha),equal=not bool(xor),expected_n=gold[1],actual_n=observed[1],witness_id=None if i is None else ids[i],expected_bits=hex(gold[2]),actual_bits=hex(observed[2])))
        length=sum((b-a for a,b in zip(events,events[1:]) if bad[(a+b)/2]),Fraction(0))
        def differs(alpha):return select(expected,alpha,pos,DEFAULT)[2]!=select(actual,alpha,pos,DEFAULT)[2]
        divergent=any(bad.values());snapshot=differs(Fraction(1,2));grid=any(differs(Fraction(v,100)) for v in range(30,91,5))
        cert={'schema':'external-upstream-candidate-conformance/1','issue':'scikit-learn#23213','case_id':record['case_id'],'variant':variant,'source_sha256':sourcehash,'upstream_commit':commit,'input_sha256':record['sha256'],'domain':['3/10','9/10'],'critical_values':list(map(str,events)),'probes':findings,'equivalent':not divergent,'psc_exact':str(length/(hi-lo)),'historical_binary_execution':False,'backend_sklearn':sklearn.__version__}
        f=Q/'results/v3/external_certificates'/f'{record["case_id"]}_{variant}.json';f.parent.mkdir(exist_ok=True);f.write_text(json.dumps(cert,indent=2),encoding='utf-8')
        rows.append(dict(case_id=record['case_id'],origin=record['origin'],variant=variant,n=len(y),returned_thresholds=len(thresholds),complete_thresholds=len(expected),policy_divergent=divergent,snapshot_detected=snapshot,grid_detected=bool(grid),complete_detected=divergent,psc_exact=cert['psc_exact'],policy_probes=len(probes),certificate_file=f.relative_to(Q).as_posix()))
        if variant!='affected':assert not divergent,'Fixed/current upstream output violates reference contract'
    return rows

def main():
    functions=upstream_functions();m=json.loads((Q/'inputs/external_sut/manifest.json').read_text(encoding='utf-8'));rows=[];t=time.perf_counter()
    for record in m['cases']:
        f=Q/'inputs/external_sut'/record['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==record['sha256'];d=np.load(f);rows+=evaluate(d['y'],d['scores'],d['ids'].tolist(),record,functions)
    R=Q/'results/v3'
    with (R/'external_sut_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    bad=[r for r in rows if r['variant']=='affected' and r['policy_divergent']]
    s={'status':'PASS','external_projects':1,'upstream_confirmed_defects':1,'issue':'https://github.com/scikit-learn/scikit-learn/issues/23213','merged_fix':'https://github.com/scikit-learn/scikit-learn/pull/23214','input_cases':len(m['cases']),'executed_variant_input_pairs':len(rows),'affected_policy_divergent_inputs':len(bad),'snapshot_detected':sum(r['snapshot_detected'] for r in bad),'grid_detected':sum(r['grid_detected'] for r in bad),'complete_detected':len(bad),'fixed_or_current_false_alarms':sum(r['policy_divergent'] for r in rows if r['variant']!='affected'),'elapsed_seconds':time.perf_counter()-t,'historical_mode':'Unmodified upstream function AST replay with sklearn '+sklearn.__version__+' counting backend, checked against direct masks; not old release binary installation','scope':'One confirmed upstream curve-truncation defect, propagated through a common local precision-policy selection adapter. Repeated workloads are not independent bugs. No new upstream issue or message sent.'}
    (R/'external_sut_summary.json').write_text(json.dumps(s,indent=2),encoding='utf-8');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
