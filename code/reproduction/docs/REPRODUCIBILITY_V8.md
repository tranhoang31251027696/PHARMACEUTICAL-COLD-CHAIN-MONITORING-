# V8 execution and interpretation

Use Python 3.13.18 with requirements.txt, including z3-solver 5.3.3.0 and the bundled eval-toolkit wheel. `python run_all.py` executes 31 default stages from frozen inputs without a neighboring original submission or network after dependency setup. Optional retraining and historical binary workers remain separately scoped. Do not use Python -O. Word/PDF generation is separate from scientific execution.

The two added stages are reuse_cost_study.py and validate_v8.py. The protocol is written to results/v8/reuse_protocol.json before measurement. It fixes six existing inputs, two request kinds, batch sizes 1/8/32/128, five repetitions, three methods and seeded randomized order. Certificate setup includes construction, JSON serialization/parsing and full independent checking. Direct masks and incremental Z3 each prepare their own masks once per batch; Z3 keeps its base selected-bitset formula and push/pops request constraints. Unknown/timeout is a failure. All methods start from the same executed interpolation outputs; their common SUT execution, imports, disk I/O and human activity are outside timers.

The output contract is Boolean existence plus a rational witness. The certificate implementation still materializes its intersections before projection. There is no answer memoization; requests within a batch differ. The study records 720 observations and 144 median/IQR groups. 2,028 distinct case/query plans are executed by three methods five times, producing 30,420 repeated answers. The audit replays unique plans against independently enumerated masks, checks every saved witness and output hash, reconciles phase totals/statistics and recalculates observed crossings. A crossing is discrete over the tested batches and may vary by host/run; no monotonic runtime law or deployment threshold is inferred.

The V7 report under evidence/V7_FINAL_RELEASE_EVIDENCE binds exact ZIP a14ac1fc458b1b76e8a6cc25031723597648045dcaae866fd46a9b6a0f806d9a to 29/29 PASS with unchanged before/after hashes. The audit checks the report and every sidecar. Source snapshots for overlap disclosure under provenance/q2_reference are also hash checked. Bibliography source/context checks are documented human-readable provenance, not falsely represented as repeated online audits in run_all.

Verify the frozen V8 archive with a copy of verify_release.py outside it:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V8_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 31
```

The work root must not exist; archive/report/extraction are separate. Send Q1_V8_DELIVERY_20261030.zip and open OPEN_THIS_FIRST.html after extraction. The complete delivery pairs exact V7/V8 archives with their detached reports and reading copies. Scientific rerun timings and rebuilt Markdown are supplied separately from the frozen Word/PDF snapshot. The research ZIP is never repacked after verification. These are author-side local runs, not independent institutional, human-triage or production evaluations.
