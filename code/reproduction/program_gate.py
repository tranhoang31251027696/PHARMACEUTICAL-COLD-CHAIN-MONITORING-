"""Local CI gate with distinct conforming, failing, and unsupported outcomes."""
from pathlib import Path
from fractions import Fraction
import sys,argparse,json,types,time,hashlib
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from adapter_admission import admit_source,UnsupportedProgramError
from policy_exact import DEFAULT,inputs
from independent_oracle import candidates,select
from program_evaluation import execute_program

def gate(source,y,s,ids,mode='complete'):
    t=time.perf_counter_ns();admission=admit_source(source);y,s,_,ids=inputs(y,s,s,ids)
    module=types.ModuleType('reviewed_sut');exec(compile(source,'reviewed_sut','exec'),module.__dict__)
    table=module.build(y,s);gold=candidates(y,s,DEFAULT);positive=bool(y.sum())
    lo,hi=Fraction(3,10),Fraction(9,10);_,events=execute_program(module,table,lo,positive,len(y))
    if mode=='snapshot':policies=[Fraction(1,2)]
    elif mode=='grid':policies=[Fraction(v,100) for v in range(30,91,5)]
    elif mode=='complete':
        br=sorted({lo,hi}|{p for p,*_ in gold if lo<p<hi}|{p for p in events if lo<p<hi})
        policies=sorted(set(br)|{(a+b)/2 for a,b in zip(br,br[1:])})
    else:raise UnsupportedProgramError('UNKNOWN_PROBE_MODE')
    failures=[]
    for alpha in policies:
        actual,traced=execute_program(module,table,alpha,positive,len(y))
        if traced!=events:raise UnsupportedProgramError('GUARD_EVENT_DRIFT')
        repeated,repeated_events=execute_program(module,table,alpha,positive,len(y))
        if repeated!=actual or repeated_events!=events:raise UnsupportedProgramError('NONDETERMINISTIC_EXECUTION')
        expected=select(gold,alpha,positive,DEFAULT)[2];xor=actual^expected
        if xor:
            i=(xor&-xor).bit_length()-1;failures.append({'alpha':str(alpha),'witness_row_id':ids[i]})
    return {'status':'NONCONFORMING' if failures else ('CONFORMING' if mode=='complete' else 'NO_FAILURE_AT_PROBES'),'certified':mode=='complete' and not failures,'source_sha256':admission['source_sha256'],'mode':mode,'probes':len(policies),'failures':failures,'gate_ms':(time.perf_counter_ns()-t)/1e6,'scope':'Reviewed-source allowlist and audited guard contract. Not a sandbox or arbitrary-Python proof.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--mode',choices=['snapshot','grid','complete'],default='complete');a=p.parse_args()
    try:
        source=a.source.read_text(encoding='utf-8');d=np.load(a.input,allow_pickle=False);ids=d['ids'].tolist() if 'ids' in d else list(range(len(d['y'])));result=gate(source,d['y'],d['old'],ids,a.mode)
    except (UnsupportedProgramError,ValueError,KeyError,TypeError,RuntimeError) as e:
        result={'status':'UNSUPPORTED','certified':False,'reason':str(e),'mode':a.mode}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'status':result['status'],'certified':result['certified'],'report':str(a.report)}))
    return 2 if result['status']=='UNSUPPORTED' else (1 if result['status']=='NONCONFORMING' else 0)
if __name__=='__main__':raise SystemExit(main())
