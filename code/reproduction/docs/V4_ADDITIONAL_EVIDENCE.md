### Onboarding a public external selector beyond the source allowlist

We execute the installed scikit-learn `TunedThresholdClassifierCV` through its documented public API [21]. Its optimizer body is neither extracted nor edited, and it is not admitted by adding another local-program hash. A prefit score-carrier estimator exposes the frozen scores; a custom scorer returns TP*(N+1)+selected_count when the exact rational precision constraint holds and -1 otherwise. The multiplier preserves the lexicographic (TP,N) objective. Complete unique-score thresholds are passed explicitly. The adapter maps an infeasible optimum and the contract's no-positive case to abstention. These are explicit trusted integration choices, not claims about the library's default balanced-accuracy or cross-validation behavior. No predictive generalization or tuning-quality estimate is made from these fixed observations.

The workload rule is fixed before checking outcomes: seed zero from each of the three existing pipeline families, first 48 rows. WDBC, digits and random forest expose respectively 9, 48 and 13 unique thresholds. All 59 critical-point and midpoint policies conform, with 2,150 actual scorer callbacks and zero membership mismatches. The validator independently rebuilds the exact masks and executes all 59 optimizer fits again. Four configurations are explicitly refused: an integer sampled grid, a missing observed threshold, cross-validation resampling, and refitting. Full-domain coverage follows only under the complete finite candidate and exact scorer contract. It does not extend to arbitrary changes of scorer, interpolation, resampling or estimator state.

Observed onboarding effort consists of 76 physical Python lines in the executable study (including its measurement/report code), four public configuration hooks and zero upstream source edits. Source/class hashes, callbacks, decisions and execution times are retained. These are inspectable integration artifacts; programmer hours, independent team effort and maintenance costs were not measured. The scorer, score carrier and abstention mapping remain trusted glue.

We also inspect a second independently authored project, eval-toolkit [22], at commit `a6400e74c4534d6d79f17dee11ad903b6d664980`. Its source, tests, license and packaging metadata are hash-pinned. Its Python >=3.13 requirement is incompatible with our Python 3.12.10 environment. We record unsupported runtime, do not execute its package, and issue no policy certificate. This is a documented onboarding barrier, not a negative correctness result. The completed additional selector case is therefore a new component in the same external scikit-learn project; the executed external-project count remains one and the confirmed-defect count remains one.

### Matched complete-region diagnostics, including certification costs

The Boolean SMT comparison above is extended to the same diagnostic contract as a finite partition adapter: all maximal connected divergent components with exact endpoint ownership, exact PSC, a separate Boolean equivalence flag, and one representative policy/row witness per component. A representative witness is existential at its reported policy; it is not one observation that changes throughout the whole component. A point-only difference retains non-equivalence even when PSC is zero. Two added tests exercise that case and the empty-divergence case.

The second algorithm is an explicit Z3 QF_LRA encoding with finite predicate-cell enumeration. Each SAT model identifies a cell of constant feasibility truth; the algorithm blocks that entire cell and repeats until residual UNSAT. Blocking individual real-valued model points would not establish termination. There are finitely many empirical-ratio cuts, so at most their number plus two solver checks are allowed. This uses established AllSMT-style predicate reasoning [23]; MathSAT's reference documents AllSat over important atoms, but MathSAT itself was not benchmarked. Timeout or unknown prevents certification.

Both implementations receive identical prepared nested threshold tables. They use the same witness representation, serialization and independent membership-based coverage checker. The issue protocol and seed zero of each existing pipeline family provide four fixed representatives; affected and fixed variants yield eight tasks. Three repetitions per algorithm produce 48 measurements. Every complete output agrees; sixteen first-repetition certificates persist and are replayed independently. Rows below are descriptive medians across four workloads times three repetitions per variant/method, not independent defect counts.

| Variant | Method | Region construction + JSON (ms) | Independent checking (ms) |
|---|---|---|---|
| affected | partition | 42.308 | 61.963 |
| affected | smt_all_regions | 677.365 | 61.552 |
| fixed | partition | 69.014 | 97.075 |
| fixed | smt_all_regions | 37.333 | 114.815 |

Per-task raw records retain the differing input sizes, region counts, solver calls, certificate bytes and checker probes. Counts/mask preparation is excluded for both methods; representative witness construction and serialization are included in producer time. Input loading and whole-release validation are excluded. These timings describe the generic external-table partition adapter, not the faster rank-based comparison core. The shared checker can dominate either producer. No universal speed ranking, unique ability to find complete regions, or new general parameter-synthesis principle follows. The remaining contribution is the explicit precision-selector contract and diagnostic format, its checked implementation and scoped software integration.

### Independent certificate consumption at scale

The compact producer timings do not measure the independent verifier. We therefore time certificate consumption separately on invariant and divergent controlled fixtures at N/G=1,000/20, 10,000/100 and 100,000/500. The certificate and input arrays are prepared before measurement. After a warmup, five untraced repetitions time JSON parsing separately from full independent verification, including candidate reconstruction, hashes, coverage, PSC and witness checks. A separate sixth run measures traced peak auxiliary memory. Its time is not pooled with the untraced repetitions. The 36 raw records comprise thirty timings and six memory measurements; medians and linear IQRs are recomputed by the artifact validator.

| N / G | Fixture | Checker median (IQR), ms | JSON median, ms | Separate peak auxiliary MiB |
|---|---|---|---|---|
| 1,000 / 20 | invariant | 7.95 (1.36) | 0.048 | 0.04 |
| 1,000 / 20 | divergent | 20.69 (1.31) | 0.051 | 0.09 |
| 10,000 / 100 | invariant | 97.90 (1.66) | 0.065 | 1.33 |
| 10,000 / 100 | divergent | 934.87 (98.19) | 0.257 | 3.56 |
| 100,000 / 500 | invariant | 4590.68 (108.39) | 0.278 | 61.42 |
| 100,000 / 500 | divergent | 25088.37 (1592.60) | 0.398 | 169.85 |

These costs are materially larger than compact production costs, especially for the divergent 100,000-row fixture. The independent implementation first materializes Boolean threshold masks before bitset packing; its peak scratch therefore includes O(NG) bytes, while packed memberships use O(NG) bits. Python integer operations have operand-size costs. The verifier is deliberately independent of the production heap/rank comparator, but it is not a constant-cost or universally cheap CI consumer. Five repetitions on one host and one separate memory run per group do not support a deployment SLO. A team must budget producer, checker, process startup and its actual case count separately.

### Immutable final-archive reproduction

Earlier evidence described a candidate archive and matching source hashes. That is insufficient to claim execution of a differently hashed final ZIP. We close the historical V3 gap by extracting the exact delivered archive, SHA-256 `e45f431d77bd8102376aafd43c558b01a398cdbf98d9bb919ef079d90a7671c8`, and executing all fifteen stages successfully without an adjacent original submission. The detached report records the environment, each exit status, stage logs, output digests and unchanged archive hash. It verifies 1,219 manifest entries and hashes 1,001 output files. This demonstrates a fresh run of the actual V3 release, not independent human replication or identical wall-clock measurements.

The V4 release follows the same non-circular protocol with nineteen stages. Freeze source, measured tables and rendered reading copies first; package once; execute the extracted final ZIP; then publish its execution evidence outside the archive. `verify_release.py` accepts an archive, new work root, detached report directory and expected stage count. Its report binds the archive hash before and after execution. The new execution's raw timings and rebuilt Markdown are evidence in the extraction, while the frozen reading copy retains its original measured run. Timing values may differ. A report is not inserted into the archive whose hash it records, and the archive is not repackaged after verification. The actual V4 pass/fail outcome and digest belong to the detached release report delivered with the archive, not a self-referential claim in this manuscript.


[21] scikit-learn developers. TunedThresholdClassifierCV API: callable scorer, explicit threshold arrays and prefit configuration. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TunedThresholdClassifierCV.html (accessed 30 October 2026).

[22] Behring, B. eval-toolkit: threshold selection methodology and source. https://brandon-behring.github.io/eval-toolkit/methodology/thresholds.html ; pinned packaging/source at https://github.com/brandon-behring/eval-toolkit/tree/a6400e74c4534d6d79f17dee11ad903b6d664980 (accessed 30 October 2026).

[23] MathSAT developers. API reference: msat_all_sat, enumeration over important atoms. https://mathsat.fbk.eu/apireference.html (accessed 30 October 2026). Used to contextualize predicate enumeration, not as an evaluated implementation.
