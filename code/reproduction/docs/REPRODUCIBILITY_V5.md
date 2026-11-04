# Reproduce V5 and locate the final-release evidence

Use Python 3.13.18. eval-toolkit requires >=3.13; the previous Python 3.12 environment cannot execute the full V5 study. From the extracted research root, install requirements.txt using that interpreter. The upstream eval-toolkit wheel is included under vendor/wheels and is built from the unmodified pinned source under vendor/eval_toolkit_full. Other pinned scientific dependencies must be installed separately; no claim is made that all their binary wheels are bundled.

```powershell
python -m pip install -r requirements.txt
python run_all.py
```

Default execution has 23 stages, uses frozen inputs and requires no adjacent original submission or network after dependencies are installed. It runs 31 core tests and eighteen upstream tests separately, then actual installed selectors, complete-region algorithms and paired checker costs. The paired checker study replaces repetition of the old standalone V4 checker-cost stage; it measures both old and new consumers on the same six fixtures. The old V4 six-group table remains explicitly historical and is arithmetically audited. Optional --retrain still requires the original source-data tree. Default SciPy version evaluation rechecks frozen prior binary-worker outputs; it does not install/re-execute the old SciPy environment.

Use the DELIVERY bundle, which includes release ZIP, reading copy, and detached final-release evidence together. Its README and manifest point to the matching hash/report. `evidence/V4_FINAL_RELEASE_EVIDENCE` inside the V5 research artifact already contains V4's completed 19-stage report for ZIP f45403ce8011adc3d084af2b432953286072fd8b6302e134ab1e087d4075b835. A historical status file is not substituted for that report.

To verify a frozen V5 ZIP independently, copy verify_release.py to a separate directory and run it with an already prepared environment:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V5_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 23
```

The work root must not exist. Archive, extraction and report directories must be separate. Do not use Python -O. The verifier checks CRC and complete manifest coverage, safely extracts, records installed versions, executes the extracted run_all.py, captures every exit/log, hashes the results tree and asserts unchanged archive SHA-256. It writes RELEASE_VERIFICATION.json and EVIDENCE_MANIFEST.json outside the research ZIP. Do not repackage the research ZIP after this run. Root stale run_all status/log files are excluded from packaging; the fresh execution creates its own.

The frozen PDF/DOCX use the retained base measurements plus pre-packaging V5 additions. A rerun rebuilds Markdown from that run's results, including newly measured base timings with the actual runtime recorded separately from the frozen-input generation environment. Exact logical outcomes must agree, timing values need not. Original base producer measurements under Python 3.12 and paired V5 consumer costs under Python 3.13 are distinct protocols and must not be divided into a claimed producer/checker speed ratio. Optional Word/Matplotlib/Poppler reading-copy authoring is separate from the scientific run_all command.

`results/v5/` holds paired raw/summary costs, 30 second-project certificates, 54 additional region certificates, upstream test XML and validation. Source/hash admission is scoped; neither checker establishes arbitrary-program correctness. The second-project study models actual nearest/even binary64 conversion and distinguishes 27 continuous-domain differentials from nineteen with a representable-policy example. No new confirmed upstream defect is inferred.
