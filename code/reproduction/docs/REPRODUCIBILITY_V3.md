# Revision 3 reproduction

Install requirements.txt, including the pinned z3-solver distribution, under Python 3.12. Default `python run_all.py` now has fifteen scientific/document stages. It uses the bundled historical CSV, frozen arrays, reviewed-source registry and pinned upstream source snapshots. No network access or neighboring SUBMISSION_PACKAGE is required by the default path. Model retraining remains a separate optional path documented in V2.

New stages are external_sut_evaluation.py, failure_and_ci_evaluation.py, smt_baseline.py and validate_v3.py. They respectively replay the external upstream function bodies, exercise safe rejection plus local CI subprocesses, solve the matched finite equivalence encoding, and audit all new evidence. Affected/fixed/current certificates and SMT tasks are replayed; unknown/unsupported outcomes must not be treated as equivalence.

External source replay is intentionally distinguished from historical binary installation. SHA-256 values refer to full upstream files fetched at immutable commits. Only the original precision_recall_curve function node is compiled, without body edits, using the installed counting API through a compatibility bridge. Counts are checked against direct masks. The installed current implementation is separately called. This isolates the documented truncation bug but does not reproduce every dependency or binary behavior of old releases.

The program gate refuses unknown source before execution. It supports a hash-bound reviewed corpus and is not a sandbox for arbitrary untrusted Python. `program_gate.py --source ... --input ... --report ... --mode complete` returns 0 for conformance, 1 for observed nonconformance, and 2 for unsupported operation. Sampled modes do not issue full-domain certification. CLI timing reports include process startup; scalar in-gate times are reported separately.

V2 reports remain historical evidence for that release. The V3 clean-run report names the candidate archive, source hashes, stage exits and any later document-only additions. Reproduction changes timings and solver-selected witnesses; logical verdicts and rational membership evidence are checked rather than requiring identical measured values or identical SAT models. Old and new timing runs are kept separate.

The author-owned MIT license does not cover vendored scikit-learn snapshots. Their BSD COPYING and NOTICE accompany them. A default reproduction sends no issue, PR, message, deployment or remote CI action.
