"""Run the local Q1 research stages consecutively, with no weekly schedule."""
from pathlib import Path
import argparse,subprocess,sys,json,time,datetime
Q=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--retrain',action='store_true',help='Rebuild inputs and retrain all 30 pipeline instances; needs adjacent original submission')
    p.add_argument('--package',action='store_true',help='Package after validation; original-submission preservation check is optional when absent')
    a=p.parse_args()
    stages=[]
    if a.retrain:stages.append(('prepare_inputs',[sys.executable,'prepare_inputs.py']))
    stages += [('pytest',[sys.executable,'-m','pytest','-q','--junitxml=results/pytest.xml']),
               ('policy_mutation_certificate_benchmarks',[sys.executable,'run_experiments.py']),
               ('matched_method_benchmark',[sys.executable,'benchmark_test_methods.py']),
               ('independent_certificate_audit',[sys.executable,'verify_artifact.py']),
               ('benchmark_audit',[sys.executable,'validate_all.py','--section','benchmark']),
               ('cli_integration',[sys.executable,'check_cli_integration.py']),
               ('program_evaluation',[sys.executable,'program_evaluation.py']),
               ('version_output_evaluation',[sys.executable,'version_evaluation.py']),
               ('phase_ablation',[sys.executable,'run_ablation.py']),
               ('revision_audit',[sys.executable,'validate_all.py','--section','program_results']),
               ('external_upstream_case',[sys.executable,'external_sut_evaluation.py']),
               ('fail_closed_and_ci',[sys.executable,'failure_and_ci_evaluation.py']),
               ('smt_same_contract_baseline',[sys.executable,'smt_baseline.py']),
               ('revision_v3_audit',[sys.executable,'validate_all.py','--section','program_admission']),
               ('external_selector_onboarding',[sys.executable,'external_selector_integration.py']),
               ('complete_region_comparison',[sys.executable,'complete_region_comparison.py']),
               ('revision_v4_audit',[sys.executable,'validate_all.py','--section','complete_regions']),
               ('upstream_selector_tests',[sys.executable,'-m','pytest','vendor/eval_toolkit_full/tests/test_thresholds.py','-q','--junitxml=results/v5/upstream_threshold_tests.xml']),
               ('second_external_project',[sys.executable,'second_project_evaluation.py']),
               ('expanded_complete_regions',[sys.executable,'expanded_region_benchmark.py']),
               ('paired_independent_checkers',[sys.executable,'streaming_checker_study.py']),
               ('revision_v5_audit',[sys.executable,'validate_all.py','--section','external_project_and_checkers']),
               ('second_documented_defect',[sys.executable,'scipy_documented_defect.py']),
               ('policy_significance',[sys.executable,'policy_significance.py']),
               ('larger_candidate_regions',[sys.executable,'large_g_region_benchmark.py']),
               ('revision_v6_audit',[sys.executable,'validate_all.py','--section','documented_defect_and_policy']),
               ('declared_policy_domain_queries',[sys.executable,'domain_query_study.py']),
               ('revision_v7_audit',[sys.executable,'validate_all.py','--section','allowed_domains']),
               ('measured_certificate_reuse',[sys.executable,'reuse_cost_study.py']),
               ('revision_v8_audit',[sys.executable,'validate_all.py','--section','reuse_costs']),
               ('boolean_certificate_api_cost',[sys.executable,'boolean_query_study.py']),
               ('revision_v9_audit',[sys.executable,'validate_all.py','--section','boolean_api']),
               ('manuscript',[sys.executable,'build_manuscript.py'])]
    if a.package:stages.append(('package',[sys.executable,'package_artifact.py']))
    result=[]
    for name,cmd in stages:
        print('Running',name,flush=True);t=time.perf_counter()
        with (Q/'results'/f'run_all_{name}.log').open('w',encoding='utf-8') as f:
            r=subprocess.run(cmd,cwd=Q,stdout=f,stderr=subprocess.STDOUT)
        result.append({'stage':name,'exit_code':r.returncode,'seconds':time.perf_counter()-t})
        (Q/'results/run_all_status.json').write_text(json.dumps({'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stages':result},indent=2),encoding='utf-8')
        if r.returncode:return r.returncode
    print('All requested stages PASS');return 0
if __name__=='__main__':raise SystemExit(main())



