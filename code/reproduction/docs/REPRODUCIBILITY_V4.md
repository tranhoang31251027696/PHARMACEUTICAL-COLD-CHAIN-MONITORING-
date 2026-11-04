# Reproduce the immutable V4 release

Use Python 3.12.10 and the pinned `requirements.txt`. Default execution is offline from frozen inputs and does not need an adjacent original submission. `python run_all.py` executes nineteen stages, including the independent checker scale study. It can take substantially longer than the compact producer benchmarks. Do not use Python optimization flags: assertion checks are required.

Preserve the delivered archive. From a separate directory run:

```powershell
python verify_release.py --archive Q1_RESEARCH_REVISION_V4_20261030.zip --work-root NEW_EMPTY_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 19
```

Copy `verify_release.py` out of the archive first. Paths can be absolute. The work-root must not already exist; report-dir must remain outside the extracted artifact. The delivered verification tool and the standalone verifier in Q1_revision_v4 are identical. Dependencies must already be installed; this command does not install anything or contact the network.

The tool checks ZIP CRC, every ARTIFACT_MANIFEST entry and path containment; extracts; checks absence of a neighboring SUBMISSION_PACKAGE; records package versions; executes the extracted run_all.py; records each exit; hashes result outputs and copies logs. It checks the ZIP hash is unchanged. `RELEASE_VERIFICATION.json`, `output_digests.json`, stage logs and `EVIDENCE_MANIFEST.json` remain outside the archive. Use the report's status and stage count to assess success. Never insert that report into its target ZIP or repackage the ZIP afterward.

The frozen manuscript contains measurements from the pre-packaging execution. A fresh run rebuilds numerical timing tables in Markdown; runtime values naturally differ. Exact policy outcomes, endpoint semantics and independent audits must agree. DOCX/PDF reading-copy rendering uses optional authoring dependencies and Word/Poppler; run_all regenerates the scientific Markdown but does not require Word. Prior reading copies and V2/V3 reports are retained as historical evidence and do not certify the V4 archive hash.

V3's exact delivered ZIP was separately run to completion, fifteen stages, SHA-256 e45f431d77bd8102376aafd43c558b01a398cdbf98d9bb919ef079d90a7671c8. That detached report is `Q1_revision_v4/V3_FINAL_RELEASE_EVIDENCE/RELEASE_VERIFICATION.json` in the delivery workspace. V4 has its own detached evidence; historical reports are not substituted for it.

Scientific addition outputs are under `results/v4`: onboarding inputs/decisions, complete-region certificates and raw timings, checker raw/summary costs and validation. The additional executed optimizer is in scikit-learn, so there is still one executed external project. eval-toolkit's pinned Python >=3.13 metadata is checked, but its package is not executed and no correctness verdict is issued.
