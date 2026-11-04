"""Replay unmodified upstream SciPy #6318/#6351 nearest-axis overflow code.

Historical class source, modern base helper and a removed NumPy alias bridge;
not an old SciPy binary installation or the original reporter's full dataset.
"""
from pathlib import Path
from fractions import Fraction as F
import ast,json,csv,sys,hashlib,inspect
import numpy as np,scipy
from scipy.interpolate import interp1d as current_interp1d
from scipy.interpolate._polyint import _Interpolator1D
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from policy_exact import compare_policies,DEFAULT
from streaming_checker import verify
from independent_oracle import candidates,select

class NumpyCompat:
    def __getattr__(self,name):return np.float64 if name=='float_' else getattr(np,name)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def functions():
    root=Q/'vendor/external_scipy';m=json.loads((root/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    for name,r in m['files'].items():assert sha(root/name)==r['sha256']
    result={};nodes={}
    for variant in ['affected','fixed']:
        path=root/(variant+'__scipy__interpolate__interpolate.py');tree=ast.parse(path.read_text(encoding='utf-8'));selected=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['interp1d','_do_extrapolate','_check_broadcast_up_to']]
        assert len(selected)==3;namespace={'__name__':'q1_scipy_'+variant,'np':NumpyCompat(),'array':np.array,'asarray':np.asarray,'searchsorted':np.searchsorted,'intp':np.intp,'string_types':(str,),'_Interpolator1D':_Interpolator1D}
        before=ast.dump(ast.Module(body=selected,type_ignores=[]),include_attributes=False)
        exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace)
        assert ast.dump(ast.Module(body=selected,type_ignores=[]),include_attributes=False)==before
        result[variant]=namespace['interp1d'];nodes[variant]=hashlib.sha256(before.encode()).hexdigest()
    result['current']=current_interp1d;return result,m,nodes

def regression_test(fn):
    path=Q/'vendor/external_scipy/fixed__scipy__interpolate__tests__test_interpolate.py';tree=ast.parse(path.read_text(encoding='utf-8'));node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='test_overflow_nearest')
    ns={'np':np,'interp1d':fn,'assert_array_almost_equal':np.testing.assert_array_almost_equal};exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    try:ns['test_overflow_nearest'](None)
    except AssertionError:return 'FAIL_EXPECTED_REGRESSION'
    return 'PASS'

def cases():
    for name,x in [('upstream_int8',np.array([0,50,127],dtype=np.int8)),('derived_int16',np.array([0,15000,32767],dtype=np.int16)),('unix_seconds_int32',np.array([1500000000,1500000050,1500000127],dtype=np.int32)),('aligned_large_int64',np.array([2**62,2**62+2**20,2**62+3*2**20],dtype=np.int64)),('small_int32_control',np.array([0,50,127],dtype=np.int32)),('float64_control',np.array([0.,50.,127.]))]:
        yield name,x,np.array([.05,.6,.95]),np.array([0,1,1]),list(range(3)),None
    records=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))['cases']
    for rec in records:
        if 'seed' not in rec:continue
        file=Q/'inputs'/rec['file'];assert sha(file)==rec['sha256'];d=np.load(file);y=d['y'][:64];s=d['old'][:64];x=(1500000000+np.arange(len(y))).astype(np.int32)
        yield 'pipeline_axis_'+rec['case_id'],x,s,y,d['ids'][:64].tolist(),rec

def main():
    R=Q/'results/v6';folder=R/'scipy_defect_certificates';folder.mkdir(parents=True,exist_ok=True);funcs,m,nodes=functions();tests={v:regression_test(fn) for v,fn in funcs.items()}
    assert tests=={'affected':'FAIL_EXPECTED_REGRESSION','fixed':'PASS','current':'PASS'};rows=[];work=[]
    for name,x,knots,y,ids,rec in cases():
        assert np.all(np.diff(x.astype(object))>0)
        outputs={v:np.asarray(fn(x,knots,kind='nearest')(x),dtype=float) for v,fn in funcs.items()}
        # At the observed knots, nearest interpolation must reproduce values.
        assert np.array_equal(outputs['fixed'],knots) and np.array_equal(outputs['current'],knots)
        reference=knots;gold=candidates(y,reference,DEFAULT);changed=not np.array_equal(outputs['affected'],reference)
        for variant,scores in outputs.items():
            cert=compare_policies(y,reference,scores,ids=ids);check=verify(y,reference,scores,ids,cert);actual=candidates(y,scores,DEFAULT)
            snap=select(gold,F(1,2),True,DEFAULT)[2]!=select(actual,F(1,2),True,DEFAULT)[2]
            grid=any(select(gold,F(3,10)+F(3,5)*i/12,True,DEFAULT)[2]!=select(actual,F(3,10)+F(3,5)*i/12,True,DEFAULT)[2] for i in range(13))
            wrapper={'case_id':name,'variant':variant,'source_commit':m.get(variant+'_commit'),'source_ast_sha256':nodes.get(variant),'axis_dtype':str(x.dtype),'axis_values':x.tolist(),'knot_scores':knots.tolist(),'labels':y.tolist(),'ids':ids,'reference_scores':reference.tolist(),'actual_scores':scores.tolist(),'source_input_sha256':rec['sha256'] if rec else None,'certificate':cert,'independent_probes':check['probes']}
            target=folder/(name+'_'+variant+'.json');target.write_text(json.dumps(wrapper,indent=2),encoding='utf-8')
            rows.append(dict(case_id=name,variant=variant,n=len(y),axis_dtype=str(x.dtype),score_changed=not np.array_equal(scores,reference),policy_divergent=not cert['equivalent'],snapshot_detected=bool(snap),grid_detected=bool(grid),psc_exact=cert['psc_exact'],independent_probes=check['probes'],certificate_file=target.name))
            if variant!='affected':assert cert['equivalent']
        work.append({'case_id':name,'score_changed':changed})
        print('scipy_source_replay',name,changed,flush=True)
    with (R/'scipy_defect_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    affected=[r for r in rows if r['variant']=='affected'];div=[r for r in affected if r['policy_divergent']]
    result={'status':'PASS','documented_defect':'scipy/scipy#6318','merged_fix':'scipy/scipy#6351','affected_commit':m['affected_commit'],'fixed_commit':m['fixed_commit'],'upstream_regression_test':tests,'workloads':len(work),'variant_workload_pairs':len(rows),'affected_score_changed':sum(r['score_changed'] for r in affected),'affected_policy_divergent':len(div),'snapshot_detected':sum(r['snapshot_detected'] for r in div),'grid_detected':sum(r['grid_detected'] for r in div),'complete_detected':len(div),'fixed_or_current_false_alarms':sum(r['policy_divergent'] for r in rows if r['variant']!='affected'),'positive_divergent_psc_min':min((float(F(r['psc_exact'])) for r in div),default=0),'positive_divergent_psc_max':max((float(F(r['psc_exact'])) for r in div),default=0),'confirmed_defects_added':1,'confirmed_defects_across_studies':2,'external_projects_across_studies':3,'scipy_runtime':scipy.__version__,'compatibility_base_sha256':sha(Path(inspect.getfile(_Interpolator1D))),'upstream_source_edits':0,'source_sha256':sha(Path(__file__)),'scope':'Unmodified historical nearest-interpolator class/helpers with modern base helper and np.float_ alias bridge. Original upstream regression test reproduced; not an old binary or original full reporter dataset. Six axis fixtures and thirty fixed pipeline prefixes with synthetic integer-time carriers. One additional documented defect, not thirty-four independent bugs/deployments. Fixed/current identity at observed knots checked directly.'}
    (R/'scipy_defect_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
