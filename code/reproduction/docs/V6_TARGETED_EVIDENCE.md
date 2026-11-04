### Additional documented defect in an independent upstream project

SciPy issue #6318 [27] reports incorrect nearest-neighbor interpolation for integer axes; merged PR #6351 [28] fixes overflow in midpoint construction by dividing before addition. We freeze the exact pre-merge parent `3565a801587a699d2f320a6406d0f38f86c0c4b0` and merge `7a46deb6b272fb8cdf4348cb3db45ca0ef3b2636`, with source, upstream tests, SHA-256 values and BSD license. The original regression test uses int8 knots [0,50,127] and requires interpolation at those knots to reproduce their values. Executing its unchanged test body fails on affected source and passes on fixed source and installed SciPy 1.18.1.

We compile the original interp1d class and its two fill-value helpers without rewriting method bodies. A compatibility namespace maps the removed NumPy float_ alias to float64 and supplies the modern _Interpolator1D base helper. Only the nearest branch on the stated finite one-dimensional inputs is evaluated. AST/source digests and the helper hash are recorded. This is isolated historical-source replay with a transparent bridge, not installation of an old SciPy binary, the reporter's complete original time series, or general equivalence of the historical and modern libraries. The overflow-causing integer addition remains unchanged; the matched fixed/current controls reproduce knot scores exactly.

The six prespecified axis fixtures include the upstream int8 axis, derived int16, Unix-second int32 and aligned large int64 axes, plus small-int32 and float64 controls. We additionally attach synthetic int32 Unix-second axes to the first 64 rows of all thirty existing pipeline score vectors and query at the observed knots. The scores/labels remain frozen; these row-index time carriers are constructed propagation fixtures, not independently collected time-series applications. Correct interpolation at observed knots is an identity requirement. The unchanged downstream consumer then compares selected IDs under the same rational precision objective.

| Evidence | Result |
|---|---|
| Workloads / variant-workload executions | 36 / 108 |
| Affected-source score changes / policy-divergent workloads | 34 / 31 |
| Snapshot / grid / full-domain detections on divergent workloads | 26 / 31 / 31 |
| Fixed-source and current policy false alarms | 0 |

The 108 input-bound core certificates are independently replayed using actual interpolation outputs, exact membership checking and source/input bindings. Among the 31 affected workloads, PSC ranges from 0.055556 to 1.000000, markedly wider than the binary64 contract differences below. Five affected workloads are missed by snapshot; grid and full-domain both detect all 31. Thus incremental real-defect workload detection over grid remains zero; complete diagnostics add localization and replayable membership evidence. Thirty-four changed score vectors do not imply thirty-four policy regressions, and thirty-one divergent workloads remain one documented defect. Across studies, the confirmed-defect count is now two, in scikit-learn and SciPy; eval-toolkit remains a separate contract-differential case. These projects share numerical dependencies and provide no multi-team deployment or real-bug detection-rate estimate.

### RQ-D Policy width and practical significance

The twenty-seven numerical-contract differentials have extremely small policy measure. We compute all quantiles using exact fractions and linear interpolation before converting only display values to scientific notation. Three further workloads have zero PSC; Boolean equivalence and endpoint evidence remain separate properties. The distribution below is conditional on the 27 positive-PSC workloads, not all thirty observations and not a probability distribution of deployed policies.

| Positive-PSC statistic | Value |
|---|---|
| min | 1.541976e-17 |
| q25 | 1.659852e-16 |
| median | 3.747190e-16 |
| q75 | 6.795052e-16 |
| max | 1.660140e-15 |

At individual verified policies, membership can still change: across these fixtures the maximum changed-ID count is 41 of 64. The largest precision shortfall observed at stored probes is 1.048544e-16; separately, the exact supremum across all covered cells is 1.048544e-16. That supremum includes limits at open cell endpoints and need not be attained. These quantities do not turn a tiny arithmetic discrepancy into demonstrated harm. The observed labels provide no deployment-frequency, utility, monetary loss or human-outcome data.

We intersect the exact divergent components with four explicitly declared policy lattices on [0.30,0.90]. Policies are rational decimal targets, not exact embeddings of their binary64 approximations. Intersection is computed algebraically from integer bounds and endpoint ownership; it does not claim to make millions of public-API calls. Earlier complete partition validation supplies coverage of the intervals, and the validator cross-checks closed/open lattice boundaries.

| Decimal places | Allowed policies per workload | Workloads with an affected policy | Affected policy/workload pairs |
|---|---|---|---|
| 2 | 61 | 0 / 30 | 0 |
| 3 | 601 | 0 / 30 | 0 |
| 4 | 6,001 | 0 / 30 | 0 |
| 6 | 600,001 | 0 / 30 | 0 |

For these measured workloads, applications restricted to any one of those decimal lattices have no affected allowed policy under the declared reference/interface mapping. That is equality on a specified finite policy set, not continuous-domain equivalence or a proof that arbitrary workloads are safe. Conversely, zero interval length can still include an allowed singleton; a dedicated boundary test prevents confusing PSC=0 with finite-set equality. The nineteen representable-binary64 examples use a different exact policy embedding, as explained above, and are not silently substituted for decimal targets.

The practical role of the tiny-region certificates is therefore narrow: auditing a strict numerical contract, documenting a numerical-interface migration, or deciding whether an explicitly permitted policy set intersects a difference. They do not demonstrate an extra bug or justify blocking every routine CI job. An application may accept the binary64 contract or define a restricted decimal policy set; such a choice must be declared before interpreting a report. We preserve the exact diagnostic result rather than erasing small regions with a tolerance and calling the versions universally equivalent. The separate SciPy defect study shows broad policy effects, but its constructed propagation cases likewise do not supply operational impact or deployment rates.

If an application already declares a small finite allowed set, exhaustive checking of every member is itself complete for that set. This study does not show that a continuous-domain certificate is cheaper or necessary in that setting. Its additional value is the reusable exact region description and contract-localized explanation; the actual frequency and utility of such reuse were not measured.

The same exact permitted-set assessment is applied separately to the SciPy defect fixtures: at two decimal places, 31 of 36 workloads have affected targets, comprising 1,611 of 2,196 allowed policy/workload pairs. Per-case counts for all four resolutions are retained in scipy_allowed_policy_counts.csv. These are constructed-fixture coverage counts, not observed deployment frequencies or independent defect counts.

### RQ-B Extension to larger candidate counts

The previous G<=90 factorial is extended with six additional prespecified tasks at N=10,000, G in {250,500} and the same none/one/alternating omission patterns. Both algorithms still produce identical complete diagnostics. Three repetitions per method, randomized within each replicate, yield 36 raw timing records and twelve independently replayed certificates. No task is dropped for being unfavorable. Residual UNSAT is required for SMT completion; unknown or timeout would prevent certification.

| G / omission | Critical points | Components | Partition total ms | SMT total ms |
|---|---|---|---|---|
| 250 / none | 215 | 0 | 986.40 | 797.28 |
| 250 / one | 215 | 1 | 735.13 | 918.14 |
| 250 / alternating | 215 | 107 | 973.93 | 3649.18 |
| 500 / none | 430 | 0 | 3618.14 | 2268.31 |
| 500 / one | 430 | 1 | 3993.99 | 4715.14 |
| 500 / alternating | 430 | 215 | 5291.80 | 21336.96 |

Totals include fresh candidate preparation, complete region/witness production plus JSON and the same region checker. The new cases reach 430 critical points and 215 divergent components. Three repetitions are descriptive and are not pooled with the older five-repetition protocol. The prepared-membership region checker is distinct from the streaming consumer for the core certificate schema. These results extend the evaluated candidate range, but do not establish asymptotic superiority, a deployment SLO, or a win over an independently optimized AllSMT implementation. The baseline remains our direct Z3 encoding; modern enumeration methods [25] retain capabilities and optimizations this study does not benchmark.

### Precise contribution relative to nearby methods

General parameter synthesis and AllSMT already supply machinery for exploring property regions; neither the finite partition fact nor complete-region capability is exclusive to this work. The contribution is a concrete verification interface with declared policy semantics, observation identities, endpoint ownership and input-bound diagnostic obligations, plus an independently implemented consumer and explicit integration limits. The strongest evidence is consistency under those obligations and measured engineering tradeoffs, rather than a new general solver principle.

| Closest foundation | What is established there | Specific work instantiated and evaluated here |
|---|---|---|
| Parametric verification and synthesis [6,7,20] | Reasoning about parameter-indexed properties and regions | Fixed empirical selected-ID equivalence, with exact policy/identity/numerical contracts and boundary ownership |
| Predicate enumeration and WMI [23-25] | Complete model-region exploration and integration | Matched selector diagnostics, exact PSC as uniform interval length and representative observation witnesses; no general enumeration novelty claimed |
| Certifying computations [9,17] | Producer/checker separation and evidence validation | A specified membership certificate and separately coded streaming consumer, replayed over 428 certificates with paired cost measurements |
| Rounding preimages [26] | Arithmetic reasoning about rounding cells | A checked mapping from an actual binary64 selector interface to rational cuts, followed by allowed-policy-set significance assessment |

The table identifies the implemented object and evidence; it is not a negative claim that existing tools cannot encode the same task. Our SMT baseline demonstrates that they can. The streaming data structures are established techniques, the source-replay bridges remain trusted integration code, and first-in-literature novelty is not established by this focused comparison. Two independently documented defects strengthen external evidence but do not by themselves prove a broad defect-detection advantage.


[27] SciPy issue #6318 (2016). Scipy interp1d nearest not working for high values on x-axis. Upstream defect report. https://github.com/scipy/scipy/issues/6318

[28] SciPy PR #6351 (2016). BUG: #6318 Interp1d nearest integer x-axis overflow issue fixed. Merged 6 July 2016. https://github.com/scipy/scipy/pull/6351
