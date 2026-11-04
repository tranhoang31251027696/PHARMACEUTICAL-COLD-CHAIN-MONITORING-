# Reproducing the V7 release

Use Python 3.13.18 and the exact requirements.txt, including z3-solver 5.3.3.0 and the bundled unmodified eval-toolkit wheel. Run `python run_all.py` for all 29 default scientific stages. No neighboring original submission or network access is needed after dependencies are installed. Optional retraining and historical binary workers remain separately documented. Do not run Python with -O; assertions are required by certificate audits.

V7 adds domain_query_study.py and validate_v7.py to V6. The query study executes the historical affected/fixed SciPy interpolation on the existing 36 cases, verifies their input-bound core certificates, then evaluates eight predeclared rational-policy scenarios per case. A separate Z3 encoding from independently enumerated masks must agree. Unknown/timeout is a study failure. Direct enumeration on finite scenarios and 2/3-place decimal lattices must reproduce counts. Higher-resolution counts are exact integer intersections. Query times are single descriptive observations, not a repeated performance benchmark.

Example checked query:

```powershell
python policy_domain_query.py --certificate results/v6/scipy_defect_certificates/upstream_int8_affected.json --query docs/policy_query_example.json
```

The CLI verifies frozen labels, score vectors, IDs, critical-point coverage, winners, witnesses and metrics before answering. It does not certify arbitrary upstream source, a changed input, or an unspecified numerical interface. The example wrapper carries the SciPy-study vectors; other integrations must supply the same core verification inputs and certificate contract.

The V6 exact final-release report and all its detached sidecars are included under evidence/V6_FINAL_RELEASE_EVIDENCE. Its ZIP SHA-256 is ec708e725b6ee0f369c156ddaec401f6bdcc8d8ad0681d1e8026638096128de0; report status is PASS 27/27, unchanged archive hash. validate_v7.py checks that report and every sidecar digest. This is local author-side evidence, not an independent institution's full reproduction.

To verify the final V7 ZIP, copy verify_release.py outside it and run:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V7_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 29
```

The work root must not exist. The report, extraction and archive must be separate. Send the complete Q1_V7_DELIVERY_20261030.zip, which pairs the exact V6/V7 research archives with their reports and reading copies. Open OPEN_THIS_FIRST.html after extracting it. The research ZIP is never repacked after verification.
