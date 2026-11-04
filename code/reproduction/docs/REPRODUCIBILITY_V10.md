# V10 editorial revision and exact release execution

Use Python 3.13.18 and requirements.txt, including z3-solver 5.3.3.0 and the bundled eval-toolkit wheel. `python run_all.py` retains the same 33 default scientific stages as V9. No new algorithm, test corpus, dataset family or experimental protocol is introduced. After dependencies are installed, the default run uses frozen inputs without network or an adjacent original submission. Do not use Python -O. Optional retraining and historical binary workers remain separately documented.

provenance/v9_science_source_hashes.json binds 139 scientific Python source files to exact V9 archive 7cef6e2f0355f701c044f3a1e46239ccc016325706ad2f0aca48a807bda03340. Scientific sources include the unchanged run_all.py. Root manuscript builders, renderer and packager are editorial/release code and are excluded from that binding. The V10 manuscript builder validates those hashes and the complete V9 detached evidence while writing results/v10/editorial_context_validation.json. This is release-context/editorial validation, not a new scientific experiment or added driver stage.

The included evidence/V9_FINAL_RELEASE_EVIDENCE records 33/33 PASS, 3,475 manifest entries, unchanged archive hashes and certificate-audit exit 0. Every sidecar hash and stage exit is checked. The record remains local author-side evidence, separate from the partial independent review.

The related manuscript is cited as unpublished [29] using direct user confirmation. Its source snapshots are unchanged. References 1–28 retain their earlier audit scope; BIBLIOGRAPHY_ADDENDUM_V10.md explains why the added unpublished reference is not an expanded external literature search.

To execute the exact frozen V10 archive, copy verify_release.py outside it and use:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V10_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 33
```

The work root must not exist. Archive, extraction and report directories must be separate. Scientific timing records will be regenerated and may differ from the frozen reading-copy snapshot; logical verdicts and audits must remain consistent. Word/PDF authoring is separate from scientific execution. The complete upload-ready file in SEND_TO_REVIEWER pairs exact V9/V10 ZIPs with their detached reports and reading copies, including flat root report filenames. Open OPEN_THIS_FIRST.html after extracting it. No scientific ZIP is repacked after verification.
