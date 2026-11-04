"""Adverse admission fixtures and real local subprocess CI gate measurements."""
from pathlib import Path
import json,sys,csv,time,subprocess,types
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from adapter_admission import admission_result,UnsupportedProgramError
from program_evaluation import modules,execute_program
from program_gate import gate
from fractions import Fraction

def main():
    R=Q/'results/v3';F=R/'failure_fixtures';F.mkdir(exist_ok=True)
    src=(Q/'src/selector_program.py').read_text(encoding='utf-8')
    fixtures={
      'alpha_branch':src.replace('best=(0,0)','best=(0,0)\n    if alpha > Fraction(2,3): return rows[0][0]'),
      'alpha_dependent_objective':src.replace('key=(k,n)','key=(k,n if alpha < Fraction(2,3) else -n)'),
      'alpha_dependent_candidates':src.replace('def build(y,scores):','def build(y,scores,alpha):').replace('rows=[]','rows=[]\n    if alpha > 0: return rows'),
      'hidden_global_state':src.replace('def select(rows,alpha,positive):','def select(rows,alpha,positive):\n    global visits\n    visits += 1'),
      'top_level_state':src+'\ncounter=0\n',
      'indirect_alpha_helper':src.replace('feasible=_feasible(k,n,alpha)','feasible=other_guard(k,n,alpha)'),
      'dynamic_eval':src.replace('key=(k,n)','key=eval("(k,n)")'),
      'random_priority':src.replace('key=(k,n)','key=(k,float(np.random.random()))'),
      'mutable_default_state':src.replace('def select(rows,alpha,positive):','def select(rows,alpha,positive,history=[]):'),
      'unreviewed_priority':src.replace('key=(k,n)','key=(k,n,1)'),
      'invalid_syntax':src+'\nthis is invalid python !!',
      'unreviewed_import':src+'\nimport threading\n'}
    results=[]
    for name,text in fixtures.items():
        f=F/(name+'.py');f.write_bytes(text.encode('utf-8'));r=admission_result(text);assert r['status']=='UNSUPPORTED' and not r['certified'];results.append(dict(fixture=name,**r))
    admitted=modules();assert len(admitted)==7
    for name,(mod,_) in admitted.items():assert admission_result((Q/'results/v2/program_sources'/f'{name}.py').read_text(encoding='utf-8'))['status']=='ADMITTED'
    # Runtime shape/dtype and transformed-guard violations cannot produce a
    # certificate even after a reviewed module has been instantiated.
    mod=types.ModuleType('runtime');exec(compile(src,'runtime','exec'),mod.__dict__);y=np.array([1,0]);s=np.array([1.,0.]);rows=mod.build(y,s)
    for name,func in [('wrong_shape',lambda *x:np.array([True])),('non_boolean',lambda *x:np.array([1.,0.])),('invalid_guard',lambda rows,a,pos: (mod._feasible(1,0,a) or np.array([True,False])))]:
        mod.select=func
        try:execute_program(mod,rows,Fraction(1,2),True,2)
        except UnsupportedProgramError as e:results.append(dict(fixture=name,status='UNSUPPORTED',certified=False,reason=str(e)))
        else:raise AssertionError('Unsafe runtime output accepted')
    records=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))['cases'];cases=[r for r in records if r.get('seed')==0];assert len(cases)==3
    timings=[];reports=R/'ci_reports';reports.mkdir(exist_ok=True)
    for rec in cases:
        for name in ['reference','strict_precision']:
            for mode in ['snapshot','grid','complete']:
                for rep in range(3):
                    f=reports/f'{rec["case_id"]}_{name}_{mode}_{rep}.json';command=[sys.executable,str(Q/'program_gate.py'),'--source',str(Q/'results/v2/program_sources'/f'{name}.py'),'--input',str(Q/'inputs'/rec['file']),'--report',str(f),'--mode',mode]
                    t=time.perf_counter_ns();p=subprocess.run(command,capture_output=True,text=True);wall=(time.perf_counter_ns()-t)/1e6;r=json.loads(f.read_text(encoding='utf-8'))
                    assert p.returncode in [0,1] and r['status']!='UNSUPPORTED'
                    if name=='reference':assert p.returncode==0
                    elif mode=='complete':assert p.returncode==1
                    timings.append(dict(pipeline=rec['pipeline'],n=rec['n'],program=name,mode=mode,replicate=rep,exit_code=p.returncode,status=r['status'],process_ms=wall,gate_ms=r['gate_ms'],probes=r['probes']))
    # A real subprocess integration check at the paper's 100k-observation scale,
    # measured separately from the three fitted-pipeline representatives.
    rng=np.random.default_rng(1523);n=100000;g=500;s=rng.integers(0,g,n)/(g-1);y=rng.integers(0,2,n)
    scale=Q/'inputs/ci_scale_fixture.npz';np.savez_compressed(scale,y=y,old=s,new=s,ids=np.arange(n).astype(str))
    for name in ['reference','strict_precision']:
        for rep in range(3):
            f=reports/f'scale100k_{name}_{rep}.json';cmd=[sys.executable,str(Q/'program_gate.py'),'--source',str(Q/'results/v2/program_sources'/f'{name}.py'),'--input',str(scale),'--report',str(f)]
            t=time.perf_counter_ns();p=subprocess.run(cmd,capture_output=True,text=True);wall=(time.perf_counter_ns()-t)/1e6;r=json.loads(f.read_text(encoding='utf-8'))
            assert p.returncode==(0 if name=='reference' else 1)
            timings.append(dict(pipeline='controlled_100k_G500',n=n,program=name,mode='complete',replicate=rep,exit_code=p.returncode,status=r['status'],process_ms=wall,gate_ms=r['gate_ms'],probes=r['probes']))
    rec=cases[0]
    for name in ['alpha_branch','hidden_global_state','alpha_dependent_objective']:
        f=reports/(name+'.json');p=subprocess.run([sys.executable,str(Q/'program_gate.py'),'--source',str(F/(name+'.py')),'--input',str(Q/'inputs'/rec['file']),'--report',str(f)],capture_output=True,text=True)
        r=json.loads(f.read_text(encoding='utf-8'));assert p.returncode==2 and not r['certified']
    with (R/'ci_timings.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(timings[0]));w.writeheader();w.writerows(timings)
    small=[r for r in timings if r['n']<100000];large=[r for r in timings if r['n']==100000]
    s={'status':'PASS','unsupported_source_fixtures':len(fixtures),'runtime_rejections':3,'approved_sources_admitted':len(admitted),'ci_timing_invocations':len(timings),'unsupported_cli_exit2_checks':3,'small_pipeline_median_process_ms':float(np.median([r['process_ms'] for r in small])),'small_pipeline_median_gate_ms':float(np.median([r['gate_ms'] for r in small])),'scale_100k_median_process_ms':float(np.median([r['process_ms'] for r in large])),'scale_100k_median_gate_ms':float(np.median([r['gate_ms'] for r in large])),'scope':'Local subprocess checks, three fitted-pipeline representatives and a separate controlled 100k fixture. Not remote CI or deployment-frequency evidence. Unsupported never means equivalent.'}
    (R/'failure_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8');(R/'failure_and_ci_summary.json').write_text(json.dumps(s,indent=2),encoding='utf-8');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
