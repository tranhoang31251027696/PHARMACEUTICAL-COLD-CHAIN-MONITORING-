# Frozen snapshot and execution reconciliation (V11)

External read-only audit: extract Evidence ZIP to any directory, then run `python reconcile_evidence.py --archive /path/to/Reproducibility_Artifact.zip --evidence-dir /path/to/extracted-evidence --regenerated-outputs /path/to/extracted-evidence/regenerated_outputs.zip --check-only`. Python standard library only; no pinned research environment, pipeline rerun or original author directory layout is needed. Quote paths containing spaces.

regenerated_outputs.zip distributes the exact 97 changed outputs plus 34 new logs/status records. Its outer hash is bound by EVIDENCE_MANIFEST.json; each inner member is separately checked against output_digests.json. The auditor reads byte-identical outputs from the frozen Artifact, recomputes field comparisons and performance derivations, and requires the result to equal the distributed JSON report. SHA binding alone is not a semantic audit; this command performs the additional comparisons on the distributed bytes. It does not independently regenerate the research outputs or prove their provenance beyond the supplied execution records.

The immutable Artifact ZIP is unchanged. This is an explanation of existing execution evidence, not a new release or pipeline run.

Of 2,982 output digests, 2,851 match the frozen snapshot byte for byte, 97 differ, and 34 are new run_all logs/status records. This does not establish byte-for-byte reproduction of every output.

All 97 differing files were compared field by field (CSV row order retained; JSON keys compared recursively). XML shared test identities/outcomes were checked after excluding timing, timestamp, host and diagnostic streams. Every changed field is recorded in SEMANTIC_RECONCILIATION.json; no unclassified field is accepted.

Diagnostic values, memberships, endpoints and certificate hashes in the compared structured files are unchanged. Timing and memory measurements change, and so do timing-derived speedups, faster-case counts and observed break-even batches; those performance results must not be presented as identical. No new general algorithm or broader detection superiority is inferred.

V8/V9 summary medians and IQRs were recomputed from their raw CSV rows in both snapshots. All 60 break-even/speedup/faster-case claims per snapshot were then recomputed from those summaries and agree with their own measurement records.

## Test inventory

The bundled results/artifact_verification.json and streaming verification summary describe an older 41-test output snapshot. The frozen source includes the additional test_generated_sources_from_crlf_input_and_tamper_detection test. Its exact-archive execution records 42 core tests in results/pytest.xml and stage_logs/run_all_pytest.log. The 41 shared tests retain their outcomes; the added test passes. Both upstream XML records contain 18 passing tests. Historical snapshot counts are retained rather than rewritten as if freshly executed.

## Environment and provenance

Python 3.12.10 versus 3.13.18 changes onboarding status from UNSUPPORTED_RUNTIME to RUNTIME_COMPATIBLE_NOT_EVALUATED. In this onboarding record, full_package_executed and policy_certificate_issued remain false; runtime compatibility is not evidence of full-package execution. CLI stdout differs only in output paths after parsing its embedded JSON.

The frozen benchmark validator contains an older recorded run_experiments.py source hash even though the bundled execution_source_snapshot already has the current bytes. The regenerated validator corrects that provenance hash to match the actual snapshot. Raw benchmark hashes also change with measurement data. Both old and corrected hashes are retained in the JSON reconciliation.

## Changed files

| File | Classified differences |
| --- | --- |
| `results/artifact_verification.json` | test_inventory |
| `results/benchmark_validation.json` | provenance_hash |
| `results/certificate_timing_summary.csv` | timing_or_memory |
| `results/certificate_timings.csv` | timing_or_memory |
| `results/cli_integration_checks.json` | environment_metadata |
| `results/matched_method_summary.csv` | timing_or_memory |
| `results/matched_method_timings.csv` | environment_metadata, timing_or_memory |
| `results/mutations.csv` | timing_or_memory |
| `results/policy_cases.csv` | timing_or_memory |
| `results/pytest.xml` | test_inventory, xml_execution_metadata |
| `results/summary.json` | environment_metadata, timing_or_memory |
| `results/v2/ablation_raw.csv` | timing_or_memory |
| `results/v2/ablation_summary.csv` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_reference_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/digits_svc_sigmoid_seed0_strict_precision_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_reference_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/generated_rf_quantized_seed0_strict_precision_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_reference_0.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_reference_1.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_reference_2.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_strict_precision_0.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_strict_precision_1.json` | timing_or_memory |
| `results/v3/ci_reports/scale100k_strict_precision_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_reference_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_complete_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_complete_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_complete_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_grid_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_grid_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_grid_2.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_snapshot_0.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_snapshot_1.json` | timing_or_memory |
| `results/v3/ci_reports/wdbc_logistic_isotonic_seed0_strict_precision_snapshot_2.json` | timing_or_memory |
| `results/v3/ci_timings.csv` | timing_or_memory |
| `results/v3/external_sut_summary.json` | timing_or_memory |
| `results/v3/failure_and_ci_summary.json` | timing_or_memory |
| `results/v3/smt_results.csv` | timing_or_memory |
| `results/v3/smt_summary.json` | timing_or_memory |
| `results/v4/complete_region_timings.csv` | timing_or_memory |
| `results/v4/onboarding_summary.json` | environment_metadata, runtime_compatibility_status, timing_or_memory |
| `results/v4/onboarding_workloads.csv` | timing_or_memory |
| `results/v5/expanded_region_raw.csv` | timing_or_memory |
| `results/v5/paired_checker_raw.csv` | timing_or_memory |
| `results/v5/paired_checker_summary.csv` | timing_or_memory |
| `results/v5/second_project_results.csv` | timing_or_memory |
| `results/v5/second_project_summary.json` | environment_metadata |
| `results/v5/streaming_artifact_verification.json` | test_inventory |
| `results/v5/upstream_threshold_tests.xml` | xml_execution_metadata |
| `results/v6/large_g_raw.csv` | timing_or_memory |
| `results/v7/domain_query_audits.json` | timing_or_memory |
| `results/v7/domain_query_results.csv` | timing_or_memory |
| `results/v8/reuse_cost_summary.json` | timing_derived_result |
| `results/v8/reuse_raw.csv` | timing_or_memory |
| `results/v8/reuse_summary.csv` | timing_or_memory |
| `results/v9/boolean_cost_summary.json` | timing_derived_result |
| `results/v9/boolean_raw.csv` | timing_or_memory |
| `results/v9/boolean_summary.csv` | timing_or_memory |
