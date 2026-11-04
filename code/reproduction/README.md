# Exact policy-aware regression diagnosis

Standalone research artifact V11 for precision-constrained threshold selectors.

## Reproduce

Use Python 3.13.18 (the recorded environment). From this directory:

```shell
python -m venv .venv
# Activate .venv using your operating system's command.
python -m pip install -r requirements.txt
python run_all.py
```

The default command runs 33 cumulative study and audit stages, including core tests, 18 packaged upstream tests, certificate checks, upstream source replays, policy-domain queries, benchmarks and Markdown manuscript generation. It may take tens of minutes. It overwrites generated files in results/; timings vary by host.

You do not need any old release ZIP, old project checkout, neighboring Q2 submission, BACKUP directory, or pretrained installation from the authors. Files called validate_v3.py through validate_v9.py and build_v*_revision.py are cumulative experiments/audits/manuscript builders retained for traceability. Historical evidence JSON/log files are bundled audit metadata; no old ZIP is executed by the default entry point. Frozen inputs and the pinned eval-toolkit wheel are included. Historical upstream functions run via documented compatibility bridges, not old binary environments.

Optional --retrain and version_worker.py are separate procedures requiring original training inputs or additional installed dependency versions; they are not part of default reproduction. Word/PDF authoring is also separate; default run_all.py regenerates Markdown, not journal PDF/DOCX. requirements-authoring.txt lists authoring dependencies.

## Layout

- src/: selector algorithms, oracle, checker and query interfaces.
- tests/: focused regression and contract tests.
- inputs/: hash-bound frozen arrays and historical grid input.
- vendor/: attributed dependencies, licenses and offline eval-toolkit wheel.
- results/: recorded outputs plus generated source snapshots needed for integrity checks; reruns overwrite outputs.
- docs/: formal specification, proof arguments, protocols, manuscript sources and reproducibility notes.
- provenance/: source manifests, historical snapshots and the author correction withdrawing a separate-manuscript attribution.
- evidence/: bundled historical audit reports consumed by cumulative audits.

Generated mutant and refusal-fixture Python sources have exact UTF-8/LF bytes. V11 integrity bindings cover repaired sources; archive manifest hashes bind all packaged files. Git attributes disable automatic line-ending conversion so a checkout preserves those bytes.

V11 fixes portability and title punctuation; it adds no dataset family, real defect or benchmark protocol. Two upstream-confirmed defects remain controlled source replays; grid detects every affected workload in both studies. Cost observations on one host are not universal speed guarantees. Native Linux full execution and independent institutional reproduction are not claimed.

## Execution evidence

The exact final ZIP is frozen before execution. Its detached report and logs bind its SHA-256 and are supplied alongside the submission artifact; they cannot be embedded retroactively without changing the verified archive. Read release_evidence/ when supplied with the repository distribution. Repository edits after publication invalidate the recorded archive hash.

Author-owned code uses LICENSE; datasets and vendored dependencies retain their own notices. The existing copyright-holder placeholder has not been replaced with an invented identity.

Current manuscript authority: use docs/MANUSCRIPT_Q1.md, docs/SUPPLEMENT_Q1_V11.md and the corrected Word reading copies. The author clarified that there is no separate inherited Q2 paper; reference [29] is withdrawn. Historical research builders and frozen ZIPs reproduce historical manuscript states, not the corrected Word text. No new PDF was exported for this correction.
