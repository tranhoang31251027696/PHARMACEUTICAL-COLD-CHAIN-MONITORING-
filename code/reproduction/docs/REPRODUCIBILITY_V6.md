# Reproduce V6 and deliver matching final-release evidence

Use Python 3.13.18 with the pinned requirements.txt and bundled eval-toolkit wheel. From the extracted research root:

```powershell
python -m pip install -r requirements.txt
python run_all.py
```

The default has 27 stages. It adds policy-significance analysis, G=250/500 matched-region tasks, SciPy #6318 source replay and a V6 audit to V5's twenty-three stages. After dependencies are prepared, all default stages are network-free and need no neighboring SUBMISSION_PACKAGE. Optional training and old SciPy binary-worker execution remain separately scoped as in the earlier reproduction documents. No Word/Matplotlib authoring installation is needed for the scientific run_all command.

The SciPy study uses the complete pinned historical source files but executes only the unmodified interp1d class plus two fill-value helpers, with current _Interpolator1D and a namespace alias np.float_ -> float64. It evaluates nearest interpolation on declared finite axes. The original upstream regression-test body is replayed; affected-source failure is an expected reproduction of the defect, not a failed research stage. Fixed-source/current must pass and reproduce knot scores. AST/source hashes, modern-helper digest and BSD notices are retained. This is not an old SciPy binary or unrestricted execution of all historical interpolation branches.

`policy_significance.py` computes fraction-based PSC quantiles and intersects complete regions with explicitly declared decimal lattices using exact integer bounds. It does not enumerate millions of public calls. Changed-ID counts, observed probe shortfall and the separate open-cell supremum have distinct meanings. No deployment probability or risk is estimated. Larger-G timing is a separate three-repetition protocol, not pooled with the earlier five-repetition factorial. Z3 unknown/timeout prevents a complete certificate.

To verify a frozen final V6 release, copy verify_release.py outside the ZIP and run with an already prepared environment:

```powershell
python verify_release.py --archive PATH_TO_FINAL_V6_ZIP --work-root NEW_PARENT/artifact --report-dir DETACHED_EVIDENCE --expected-stages 27
```

The work root must not exist; archive, extraction and report directories must be separate. Do not use Python -O. The verifier checks CRC and complete manifest coverage, records dependencies, executes the extracted driver, preserves every exit/log and output digest, and asserts the ZIP hash is unchanged. Final evidence remains outside the research ZIP. Deliver the complete DELIVERY bundle and its OPEN_THIS_FIRST.html index so the reviewer receives both archive and report together. Do not repack the research ZIP after verification.

The exact V5 final-release report is already included under evidence/V5_FINAL_RELEASE_EVIDENCE and validated by V6. It has 23/23 successful stages for ZIP 4a580830ee0a2c4d5cf78290b80312c28e8cc4a2f66fabfcc40568432492a2c1. V6 requires its own 27-stage report; no earlier report is substituted. A fresh run regenerates Markdown/timings in the extraction; the frozen PDF retains its pre-packaging measured snapshot. Both sets are delivered with their scope and hashes.
