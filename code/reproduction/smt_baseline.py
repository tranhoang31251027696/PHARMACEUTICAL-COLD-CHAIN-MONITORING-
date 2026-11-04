"""Direct QF_LRA equivalence query for the external same-score threshold task."""
from pathlib import Path
from fractions import Fraction
import json,csv,time,sys
import numpy as np
import z3
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from independent_oracle import candidates,select
from policy_exact import DEFAULT
from external_sut_evaluation import upstream_functions,actual_table
from sklearn.metrics import precision_recall_curve

def expression(table,alpha):
    value=z3.IntVal(0)
    # Ascending objective order makes the last feasible update the winner.
    for p,k,n,bits in sorted(table,key=lambda r:(r[1],r[2])):
        value=z3.If(alpha*z3.RealVal(p.denominator)<=z3.RealVal(p.numerator),z3.IntVal(n),value)
    return value

def main():
    R=Q/'results/v3';F=R/'smt_queries';F.mkdir(exist_ok=True);functions=upstream_functions();manifest=json.loads((Q/'inputs/external_sut/manifest.json').read_text(encoding='utf-8'))
    external=list(csv.DictReader((R/'external_sut_results.csv').open(encoding='utf-8')));expected={(r['case_id'],r['variant']):r['policy_divergent']=='True' for r in external};rows=[]
    for rec in manifest['cases']:
        d=np.load(Q/'inputs/external_sut'/rec['file']);y=d['y'];s=d['scores'];gold=candidates(y,s,DEFAULT)
        for variant in ['affected','fixed','installed_current']:
            function=precision_recall_curve if variant=='installed_current' else functions[variant][0];actual,_=actual_table(function,y,s)
            for rep in range(3):
                start=time.perf_counter_ns();alpha=z3.Real('alpha');solver=z3.SolverFor('QF_LRA');solver.set(timeout=5000)
                solver.add(alpha>=z3.RealVal('3/10'),alpha<=z3.RealVal('9/10'),expression(gold,alpha)!=expression(actual,alpha))
                build_ms=(time.perf_counter_ns()-start)/1e6;t=time.perf_counter_ns();out=solver.check();solve_ms=(time.perf_counter_ns()-t)/1e6
                witness=None
                if out==z3.sat:
                    v=solver.model().eval(alpha,model_completion=True);witness=Fraction(v.numerator_as_long(),v.denominator_as_long())
                    assert select(gold,witness,True,DEFAULT)[2]!=select(actual,witness,True,DEFAULT)[2]
                assert out!=z3.unknown,'SMT timeout/unknown must not be treated as equivalent'
                assert (out==z3.sat)==expected[(rec['case_id'],variant)]
                if rep==0:(F/f'{rec["case_id"]}_{variant}.smt2').write_text(solver.to_smt2(),encoding='utf-8')
                rows.append(dict(case_id=rec['case_id'],variant=variant,replicate=rep,z3_result=str(out),divergent=out==z3.sat,model_alpha=None if witness is None else str(witness),encoding_ms=build_ms,solver_ms=solve_ms,total_query_ms=build_ms+solve_ms))
    with (R/'smt_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'status':'PASS','solver_version':z3.get_version_string(),'queries':len(rows),'distinct_equivalence_tasks':len(rows)//3,'repetitions':3,'sat_queries':sum(r['divergent'] for r in rows),'unknown_queries':0,'all_logical_verdicts_match_partition_checker':True,'all_sat_models_independently_rechecked':True,'median_encoding_ms':float(np.median([r['encoding_ms'] for r in rows])),'median_solver_ms':float(np.median([r['solver_ms'] for r in rows])),'scope':'Same finite empirical contract and external threshold lists. Same-score nested prefixes allow size inequality as membership inequality. SAT gives one witness; no full interval certificate/PSC. Not a claim about arbitrary score crossings or arbitrary source programs.'}
    (R/'smt_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
