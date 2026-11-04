# Reproducing V9 and interpreting the two cost panels

Use Python 3.13.18 and requirements.txt, including z3-solver 5.3.3.0 and the bundled unmodified eval-toolkit wheel. `python run_all.py` runs 33 default scientific stages from frozen inputs without an adjacent original submission or network after dependency installation. Optional retraining/historical binary workers remain separate. Never use Python -O; assertions are part of the evidence checks. Word/PDF authoring is separate from scientific reproduction.

V9 adds boolean_query_study.py and validate_v9.py. The four additional core test items exercise the new index's endpoint/tamper/refusal behavior. The study keeps the exact V8 six cases and 2,028 plans. Four methods, four batch sizes, five repetitions, warmups and seeded randomized method order produce 960 raw observations and 192 groups. 40,560 answers count repeated method/replicate execution, not unique workloads or new bugs.

Both certificate routes construct the complete core certificate, perform a JSON roundtrip and independently verify it once per batch. Boolean construction also pays input/certificate copying, component merging, freezing and index setup. Their comparison has matched certificate obligations. Direct masks and incremental Z3 reuse their V8 implementations, preparing their independent masks/constraints once per batch. They do not emit/independently check a complete certificate. Four-route comparisons therefore measure request costs with unequal evidence obligations. All saved positive witnesses are checked outside timing; a witness check alone does not verify negative/UNSAT results or a global diagnostic object. See BOOLEAN_QUERY_AND_ASSURANCE.md.

Setup, query and total phases are retained. Timings are untraced, from common executed score vectors; imports, SUT interpolation, disk I/O and human work are outside all method timers. Every batch contains distinct requests and no method memoizes answers. New/old timing protocols are separate. Medians/IQRs and any speed ratios or counts of faster cases must be reconstructed from the raw records of the corresponding run; they may change by host/load. No statistical significance, universal speed, production policy frequency or developer productivity follows from the study.

The exact V8 31-stage report and all sidecars are included under evidence/V8_FINAL_RELEASE_EVIDENCE. Its archive SHA-256 is c196b5f591c9ee48e9e7d8fa6e72431204e05195b7ee7ed5365ed7742d6735ab and its independent_certificate_audit stage records exit 0. validate_v9.py checks archive identity, all 31 exit codes and every sidecar hash. This is author-side local evidence, distinct from partial external review execution.

Verify an immutable V9 ZIP using verify_release.py copied outside it:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V9_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 33
```

Archive, extraction and report must be separate; work root must not exist. The complete upload-ready file is Q1_RESEARCH_V9_COMPLETE_WITH_EXECUTION_EVIDENCE_20261030.zip in SEND_TO_REVIEWER. It pairs the exact scientific ZIPs and detached reports; open OPEN_THIS_FIRST.html after extraction. The frozen reading copy is a measured snapshot, while fresh raw timings and rebuilt Markdown from the final extraction are supplied separately. The scientific ZIP is never repacked after verification. No remote CI or independent developer deployment is claimed.
