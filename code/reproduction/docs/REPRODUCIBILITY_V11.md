# Reproduction V11

Run `python run_all.py` from the artifact root after installing requirements.txt in Python 3.13.18. All 33 stages use the one current artifact. Earlier revision numbers name cumulative stages, not required old releases. Bundled historical reports are read as provenance, not executed. Default execution uses frozen scores, the included historical CSV and offline eval-toolkit wheel.

V11 changes program_evaluation.py and failure_and_ci_evaluation.py to write generated Python snapshots as UTF-8 bytes with LF. The renderer preserves the canonical title punctuation. A focused CRLF-input and tamper regression is added. The repaired binding manifest is provenance/v11_source_bindings.json. V10's 138 strict + 1 controlled binding classification is historical, not a statement that all V11 source is unchanged.

The exact submission artifact is packaged once, then extracted to a fresh isolated directory and run. Detached RELEASE_VERIFICATION.json records its exact SHA-256, interpreter, environment, all stage exit codes and outputs; the archive is not rewritten afterwards. Execution is local Windows unless explicitly recorded otherwise. LF/CRLF tests simulate portability; they do not establish a native Linux full run.

Main and supplement PDF/DOCX are separate submission documents. Word/PDF production is outside the computational reproduction entry point. The main reading copy uses recorded benchmark snapshots; fresh timing outputs and regenerated Markdown remain separate records.

The detached Evidence ZIP now includes SEMANTIC_RECONCILIATION.md and its JSON field-level record. Of 2,982 execution output digests, 2,851 match the bundled frozen snapshot, 97 differ, and 34 are new execution logs/status records. This is not byte-for-byte reproduction of every output. Differences include timing/memory, timing-derived performance summaries, paths/environment, runtime-compatibility status, provenance hashes and test inventory. Diagnostic fields in the compared structured outputs remain unchanged; performance measurements are distinct records.

Bundled artifact_verification.json retains an older 41-test snapshot; streaming_artifact_verification.json retains an older 31-test snapshot. Exact-archive execution reports 42 core tests, including the added test_generated_sources_from_crlf_input_and_tamper_detection test; stage_logs/run_all_pytest.log and results/pytest.xml are the execution sources. The upstream suite has 18 tests. Historical snapshots are not rewritten to imply a new run. EVIDENCE_MANIFEST.json covers all detached payload members, including README.md and verify_release.py, excluding only itself.

The contribution remains exact policy-aware regression diagnosis: localization, endpoint correctness and independently checked certificates. Both documented upstream defects have all affected workloads detected by the thirteen-point grid; no additional external detection advantage or new general verification algorithm is claimed. Journal-specific formatting must be checked against the selected journal's author instructions; having separate Main/Supplement files does not itself establish compliance.

For external audit, the Evidence ZIP also distributes regenerated_outputs.zip containing the exact 97 changed files and 34 new execution records. Extract Evidence to any directory and run its bundled reconciler with explicit paths:

```shell
python reconcile_evidence.py --archive "../Reproducibility_Artifact.zip" --evidence-dir "." --regenerated-outputs "regenerated_outputs.zip" --check-only
```

Adjust the paths to the chosen locations. This read-only mode uses only Python's standard library, independently recomputes the comparisons on the supplied bytes and checks them against the distributed reconciliation JSON. It does not need the author's workspace layout or the pinned research environment. Alternatively, --run-root can point to a recorded extraction containing results/. SHA binding alone is distinct from these field-level checks; neither substitutes for independently executing the research pipeline. The amendment does not change novelty, generalizability or external validation of the underlying research.

