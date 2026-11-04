"""Program-output conformance against one unchanged reference specification.

The checker is never passed new_spec. Source-level mutants execute their own
candidate construction, guard and winner code, instrumented at the guard API.
"""
from pathlib import Path
from fractions import Fraction
import sys,json,csv,hashlib,ast,types
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from policy_exact import DEFAULT
from independent_oracle import candidates,select
from adapter_admission import admit_source,UnsupportedProgramError

def modules():
    source=(Q/'src/selector_program.py').read_text(encoding='utf-8')
    variants={'reference':source,
      'strict_precision':source.replace('k*alpha.denominator >= n*alpha.numerator','k*alpha.denominator > n*alpha.numerator'),
      'threshold_gt':source.replace('scores >= t','scores > t'),
      'reverse_tie_break':source.replace('best=(0,0)','best=(-1,0)').replace('key=(k,n)','key=(k,-n)'),
      'drop_middle_group':source.replace('sorted(set(scores.tolist()),reverse=True)','[t for j,t in enumerate(sorted(set(scores.tolist()),reverse=True)) if j != len(set(scores.tolist()))//2]'),
      'split_score_ties':source.replace('return [scores >= t for t in sorted(set(scores.tolist()),reverse=True)]','order=np.argsort(-scores,kind="stable")\n    return [np.isin(np.arange(len(scores)),order[:n]) for n in range(1,len(scores)+1)]'),
      'tp_count_plus_one':source.replace('_feasible(k,n,alpha)\n        key','_feasible(min(n,k+1),n,alpha)\n        key')}
    out={};folder=Q/'results/v2/program_sources';folder.mkdir(parents=True,exist_ok=True)
    for name,text in variants.items():
        if name!='reference':assert text!=source
        # Corpus guarantee: select uses alpha only as a direct _feasible argument.
        tree=ast.parse(text)
        for f in tree.body:
            if isinstance(f,ast.FunctionDef) and f.name=='select':
                allowed={id(a) for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_feasible' for a in n.args if isinstance(a,ast.Name) and a.id=='alpha'}
                assert all(id(n) in allowed for n in ast.walk(f) if isinstance(n,ast.Name) and n.id=='alpha')
        admit_source(text)
        module=types.ModuleType(name);exec(compile(text,str(folder/(name+'.py')),'exec'),module.__dict__)
        (folder/(name+'.py')).write_bytes(text.encode('utf-8'));out[name]=(module,hashlib.sha256(text.encode()).hexdigest())
    return out

def execute_program(module,rows,alpha,positive,expected_n):
    seen=set();guard=module._feasible
    def traced(k,n,a):
        if a!=alpha or not isinstance(k,(int,np.integer)) or not isinstance(n,(int,np.integer)) or n<=0 or not 0<=k<=n:
            raise UnsupportedProgramError('INVALID_OR_TRANSFORMED_GUARD_ARGUMENT')
        seen.add(Fraction(int(k),int(n)));return guard(k,n,a)
    module._feasible=traced
    try:mask=module.select(rows,alpha,positive)
    finally:module._feasible=guard
    # Empty candidate tables still mean abstention for the full observation set.
    mask=np.asarray(mask)
    if mask.ndim!=1 or mask.dtype!=np.dtype(bool):raise UnsupportedProgramError('NON_BOOLEAN_MEMBERSHIP_OUTPUT')
    if len(mask)==0 and not rows:mask=np.zeros(expected_n,dtype=bool)
    if mask.shape!=(expected_n,):raise UnsupportedProgramError('MISALIGNED_MEMBERSHIP_OUTPUT')
    bits=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little')
    return bits,seen

def main():
    manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'));mods=modules();results=[];totalprobes=0
    certs=Q/'results/v2/program_certificates';certs.mkdir(exist_ok=True)
    for rec in manifest['cases']:
        if rec['cohort']!='Independent_pipeline':continue
        d=np.load(Q/'inputs'/rec['file']);y=d['y'];s=d['old'];ids=d['ids'].tolist();positive=bool(y.sum())
        expected=candidates(y,s,DEFAULT);lo=Fraction(3,10);hi=Fraction(9,10)
        for name,(sut,sourcehash) in mods.items():
            table=sut.build(y,s)
            _,events=execute_program(sut,table,lo,positive,len(y))
            breaks=sorted({lo,hi}|{p for p,*_ in expected if lo<p<hi}|{p for p in events if lo<p<hi})
            probes=sorted(set(breaks)|{(a+b)/2 for a,b in zip(breaks,breaks[1:])});findings=[];lookup={}
            for alpha in probes:
                actual,traced=execute_program(sut,table,alpha,positive,len(y));assert traced==events
                reference=select(expected,alpha,positive,DEFAULT)[2];bad=actual!=reference;lookup[alpha]=bad
                xor=actual^reference;i=(xor&-xor).bit_length()-1 if xor else None
                findings.append({'alpha':str(alpha),'conforms':not bad,'expected_bits_hex':hex(reference),'actual_bits_hex':hex(actual),'witness_row_id':None if i is None else ids[i]})
            snap=lookup.get(Fraction(1,2))
            if snap is None:
                actual,_=execute_program(sut,table,Fraction(1,2),positive,len(y));snap=actual!=select(expected,Fraction(1,2),positive,DEFAULT)[2]
            grid=False
            for v in range(30,91,5):
                a=Fraction(v,100);actual,_=execute_program(sut,table,a,positive,len(y));grid |= actual!=select(expected,a,positive,DEFAULT)[2]
            divergent=any(lookup.values());length=sum((b-a for a,b in zip(breaks,breaks[1:]) if lookup[(a+b)/2]),Fraction(0))
            certificate={'schema':'instrumented-program-conformance/1','case_id':rec['case_id'],'source_sha256':sourcehash,'frozen_input_sha256':rec['sha256'],'expected_contract':DEFAULT,'guard_events':list(map(str,sorted(events))),'critical_values':list(map(str,breaks)),'probes':findings,'conforms':not divergent,'psc_exact':str(length/(hi-lo)),'scope':'Complete for this audited alpha-only-in-guard corpus; not arbitrary program verification.'}
            f=certs/f'{rec["file"][:-4]}_{name}.json';f.write_text(json.dumps(certificate,indent=2),encoding='utf-8')
            results.append(dict(case_id=rec['case_id'],pipeline=rec['pipeline'],seed=rec['seed'],program=name,source_sha256=sourcehash,conformance_failure=divergent,snapshot_detected=bool(snap),grid_detected=bool(grid),guard_complete_detected=divergent,psc_exact=str(length/(hi-lo)),probes=len(probes),certificate_file=str(f.relative_to(Q)).replace('\\','/')))
            totalprobes+=len(probes)
        print('program',rec['case_id'],flush=True)
    R=Q/'results/v2'
    with (R/'program_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    div=[r for r in results if r['conformance_failure']]
    summary={'status':'PASS','program_runs':len(results),'source_mutants':6,'reference_controls':30,'reference_false_alarms':sum(r['conformance_failure'] for r in results if r['program']=='reference'),'nonconforming_runs':len(div),'snapshot_detected':sum(r['snapshot_detected'] for r in div),'grid_detected':sum(r['grid_detected'] for r in div),'guard_complete_detected':len(div),'policy_probes':totalprobes,'new_spec_passed_to_checker':False,'limitation':'Known source-mutant corpus, instrumented guard coverage, locally built SUT. No naturally occurring bug corpus.'}
    assert summary['reference_false_alarms']==0
    (R/'program_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
