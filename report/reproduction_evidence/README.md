# Detached V11 execution evidence

Artifact SHA-256: 552d7fd41f2eddf1737c7dcf64c04ccac598c587c014b765c818dfc04da29bd8

Local Windows execution: 33 stages, 42 core tests and 18 upstream tests. Not native Linux or independent institutional reproduction.

The Artifact contains historical 41-test result snapshots; see SEMANTIC_RECONCILIATION.md and its machine-readable JSON for test inventory, all 97 changed output files, and 34 new execution records. Only 2,853 of 2,984 output digests are byte-identical to the snapshot.

External audit without the original workspace or pinned environment: extract this ZIP, then run (Python standard library only):

```shell
python reconcile_evidence.py --archive "../Reproducibility_Artifact.zip" --evidence-dir "." --regenerated-outputs "regenerated_outputs.zip" --check-only
```

Adjust --archive and --evidence-dir to your chosen paths. The command is read-only. --run-root can instead point to an existing recorded extraction containing results/. The compressed outputs include all 97 changed files and 34 new logs/status records; their digests, field comparisons and timing-derived claims are rechecked, not merely trusted from the reconciliation JSON. This verifies supplied records, not an independent research execution. Do not use Python -O.

The scientific scope is exact policy-aware regression diagnosis: localization, endpoint correctness and independently checked certificates. Both documented upstream defects have all affected workloads detected by the thirteen-point grid; no additional external detection advantage or new general verification algorithm is claimed.

Main/Supplement PDF and DOCX are separate submission files, outside both reproducibility ZIPs. See SUBMISSION_PACKAGE/README.md for submission scope.

EVIDENCE_MANIFEST.json covers every payload member, including this README and verify_release.py. The manifest excludes itself to avoid self-reference. Reconciliation describes existing evidence and does not change the recorded archive hash or original execution outputs.
