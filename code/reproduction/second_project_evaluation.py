"""Execute the unchanged installed eval-toolkit selector, including float cuts.

Binary64 public policy conversion is part of the actual contract; it must not
be silently equated to the exact rational-reference feasibility predicate.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,csv,hashlib,inspect,struct,platform,time
import numpy as np
from sklearn.metrics import precision_recall_curve
import eval_toolkit
from eval_toolkit.thresholds import TargetPrecisionSelector
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import candidates,select
from policy_exact import DEFAULT
from complete_region_comparison import normalize,member

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def float_cut(value):
    v=float(value);successor=float(np.nextafter(v,np.inf));cut=(F.from_float(v)+F.from_float(successor))/2
    closed=not (struct.unpack('>Q',struct.pack('>d',v))[0]&1)
    assert float(cut)==(v if closed else successor),'Expected nearest/even binary64 conversion'
    return cut,closed

def actual(y,s,a):
    try:r=TargetPrecisionSelector(precision=float(a)).select(y,s)
    except RuntimeError as e:
        if not str(e).startswith('No threshold achieves precision'):raise
        return 0
    return int.from_bytes(np.packbits(s>=r.threshold,bitorder='little').tobytes(),'little')

def tables(y,s):
    gold=candidates(y,s,DEFAULT);precisions,recalls,thresholds=precision_recall_curve(y,s);guard=[]
    for p,t in zip(precisions[:-1],thresholds):
        mask=s>=t;n=int(mask.sum());k=int(y[mask].sum());assert float(p)==float(k/n)
        cut,closed=float_cut(p);bits=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little');guard.append((cut,closed,k,n,bits))
    return gold,guard

def guarded(guard,a):
    feasible=[(k,n,bits) for cut,closed,k,n,bits in guard if a<cut or a==cut and closed]
    return max(feasible,key=lambda x:(x[0],x[1]))[2] if feasible else 0

def evidence(y,s,ids):
    gold,guard=tables(y,s);lo,hi=F(3,10),F(9,10)
    br=sorted({lo,hi}|{p for p,*_ in gold if lo<p<hi}|{cut for cut,*_ in guard if lo<cut<hi});pp=sorted(set(br)|{(a+b)/2 for a,b in zip(br,br[1:])});observations=[];truth={}
    for a in pp:
        expected=select(gold,a,True,DEFAULT)[2];model=guarded(guard,a);observed=actual(y,s,a);assert observed==model,'Pinned float-contract model disagrees with actual optimizer'
        xor=expected^observed;truth[a]=bool(xor);w=None
        if xor:
            i=(xor&-xor).bit_length()-1;w={'row_index':i,'row_id':ids[i],'reference_selected':bool(expected>>i&1),'actual_selected':bool(observed>>i&1)}
        observations.append({'alpha':str(a),'public_binary64_policy':float(a).hex(),'reference_bits':hex(expected),'actual_bits':hex(observed),'different':bool(xor),'witness':w})
    cells=[]
    for i,a in enumerate(br):
        if truth[a]:cells.append(dict(lo=str(a),hi=str(a),left_closed=True,right_closed=True))
        if i and truth[(br[i-1]+a)/2]:cells.append(dict(lo=str(br[i-1]),hi=str(a),left_closed=False,right_closed=False))
    regions=normalize(cells);length=sum((b-a for a,b in zip(br,br[1:]) if truth[(a+b)/2]),F(0))
    representable=[]
    float_policies=sorted({F.from_float(float(k/n)) for cut,closed,k,n,bits in guard if lo<=F.from_float(float(k/n))<=hi})
    for a in float_policies:
        expected=select(gold,a,True,DEFAULT)[2];observed=actual(y,s,a)
        representable.append({'alpha':str(a),'public_binary64_policy':float(a).hex(),'reference_bits':hex(expected),'actual_bits':hex(observed),'different':expected!=observed})
    grid=[lo+(hi-lo)*i/12 for i in range(13)];grid_outputs=[actual(y,s,a) for a in grid];grid_detect=any(select(gold,a,True,DEFAULT)[2]!=bits for a,bits in zip(grid,grid_outputs))
    return {'schema':'external-binary64-selector-policy/1','domain':[str(lo),str(hi)],'critical_values':list(map(str,br)),'probes':observations,'representable_policy_probes':representable,'representable_policy_difference':any(r['different'] for r in representable),'equivalent_to_rational_reference':not any(truth.values()),'divergent_regions':regions,'psc_exact':str(length/(hi-lo)),'grid_detected':grid_detect,'snapshot_detected':select(gold,F(1,2),True,DEFAULT)[2]!=actual(y,s,F(1,2)),'candidate_count':len(gold),'guard_count':len(guard),'contract':'Exact rational reference versus the actual public binary64 policy interface; nearest/even rounding-cell cuts included. A semantic differential is not an upstream-confirmed defect.'}

def main():
    assert sys.version_info>=(3,13) and sys.float_info.mant_dig==53 and sys.float_info.rounds==1
    R=Q/'results/v5';folder=R/'second_project_certificates';folder.mkdir(parents=True,exist_ok=True);rows=[];source=Path(inspect.getfile(TargetPrecisionSelector))
    vendor=Q/'vendor/eval_toolkit_full';manifest=json.loads((vendor/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    assert sha(source)==manifest['files']['src/eval_toolkit/thresholds.py']
    for name,digest in manifest['files'].items():assert sha(vendor/name)==digest
    assert 'site-packages' in source.parts,'Execute the installed package, not an extracted class or patched module'
    installed_root=Path(inspect.getfile(eval_toolkit)).parent;installed_files=0
    for name,digest in manifest['files'].items():
        if name.startswith('src/eval_toolkit/'):
            assert sha(installed_root/name.removeprefix('src/eval_toolkit/'))==digest;installed_files+=1
    records=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))['cases']
    for rec in records:
        if 'seed' not in rec:continue
        f=Q/'inputs'/rec['file'];assert sha(f)==rec['sha256'];d=np.load(f);y=d['y'][:64];s=d['old'][:64];ids=d['ids'][:64].tolist();assert len(np.unique(y))==2
        t=time.perf_counter();c=evidence(y,s,ids);elapsed=time.perf_counter()-t
        c.update(case_id=rec['case_id'],source_input_sha256=rec['sha256'],slice='first 64 rows, all 30 pipeline cases',source_module_sha256=sha(source),upstream_commit=manifest['commit'])
        name=rec['case_id']+'.json';(folder/name).write_text(json.dumps(c,indent=2),encoding='utf-8')
        rows.append(dict(case_id=rec['case_id'],n=len(y),candidates=c['candidate_count'],critical_points=len(c['critical_values']),policy_probes=len(c['probes']),representable_probes=len(c['representable_policy_probes']),representable_different=c['representable_policy_difference'],divergent=not c['equivalent_to_rational_reference'],components=len(c['divergent_regions']),psc_exact=c['psc_exact'],grid_detected=c['grid_detected'],snapshot_detected=c['snapshot_detected'],actual_public_calls=len(c['probes'])+len(c['representable_policy_probes'])+14,elapsed_seconds=elapsed,certificate=name))
        print('eval_toolkit',rec['case_id'],len(c['probes']),len(c['divergent_regions']),flush=True)
    assert len(rows)==30
    with (R/'second_project_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'status':'PASS','project':'eval-toolkit','project_version':eval_toolkit.__version__,'upstream_commit':manifest['commit'],'python':platform.python_version(),'source_module_sha256':sha(source),'source_module_path':str(source),'upstream_source_edits':0,'full_package_installed_and_executed':True,'workloads':len(rows),'policy_probes':sum(r['policy_probes'] for r in rows),'public_calls':sum(r['actual_public_calls'] for r in rows),'divergent_workloads':sum(r['divergent'] for r in rows),'grid_detected_workloads':sum(r['grid_detected'] for r in rows),'snapshot_detected_workloads':sum(r['snapshot_detected'] for r in rows),'confirmed_defects_added':0,'external_projects_executed_across_studies':2,'scope':'Actual unmodified TargetPrecisionSelector via its public float API, fixed prefixes of all thirty existing pipelines. Complete coverage includes rational preimages of binary64 rounding boundaries; observed differences from rational semantics are not classified as upstream bugs. No cross-project independence of sklearn dependencies is claimed.'}
    summary.update(installed_source_files_verified=installed_files,representable_policy_probes=sum(r['representable_probes'] for r in rows),representable_policy_divergent_workloads=sum(r['representable_different'] for r in rows))
    (R/'second_project_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
