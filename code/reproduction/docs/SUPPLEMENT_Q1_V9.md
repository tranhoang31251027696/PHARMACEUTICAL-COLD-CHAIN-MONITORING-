# Supplementary experimental protocols and evidence for Q1 V9

These sections retain the earlier experimental detail. They complement the main paper and the formal specification, proofs, raw records and executable audits distributed in the artifact. Timing protocols and cohorts remain separate.

## S1 Fresh dependency version executions

We execute actual SciPy 1.15.3 and 1.18.1 binaries in separate pre-existing Python environments. The worker asserts its loaded SciPy version, records Python and NumPy versions, executable and module paths, extracts and hashes the interpolation implementation, and hashes its generated score arrays. It reads frozen interpolation knots, calibration values, raw tuning scores and labels; those inputs are packaged with individual hashes. The ten cold-chain calibrators and the public WDBC pilot are included without selecting cases on the new result. Training and calibrator fitting are not repeated or changed during this comparison.

Both workers call `scipy.interpolate.interp1d` on the same clipped queries and calibration arrays. Cold-chain outputs are cast to float32 as in the inherited protocol; the public pilot retains its original output dtype. We compare older 1.15.3 outputs to newer 1.18.1 outputs under the same default selector contract on [0.30,0.90]. This direction is explicitly named because the earlier artifact sometimes used the newer environment as its reference. Policy divergence is symmetric, but old/new witness membership and some threshold descriptions are directional.

All eleven worker comparisons exhibit at least one changed score, and nine exhibit some policy divergence over the agreed domain. The exact certificates are independently checked against their actual version-produced arrays. This is fresh execution evidence for sensitivity to real dependency implementations on inherited fixed data. It is stronger provenance than an engineered float32 cast, but it is not eleven independent deployments, eleven new datasets, or nine confirmed library bugs. Different numerical implementations may both satisfy their advertised numerical requirements. In the absence of an upstream issue, specified bug-fix behavior or application requirement forbidding these changes, we report a version differential and a potential application regression, not a defect in SciPy.

Default standalone reproduction re-evaluates the frozen version-worker outputs and their certificates. Re-executing both binaries requires separately installed versions, because a single Python environment cannot load the two distributions reliably as the same module name. The worker commands and environment requirements are explicit. This optional binary-reexecution requirement does not affect regeneration of the main 98-case and mutation studies from the standalone ZIP. We executed both binaries locally in this revision and preserved their fresh logs; a future reproducer is not required to trust that history to re-evaluate the included score arrays.

## S2 Program conformance and the semantic information boundary

The first evaluation verifies declared old/new selector semantics. That question is useful when both implementations have faithful finite contracts, but it does not establish that an actual executable conforms to its advertised contract. We therefore add a separate program-output study. The expected specification remains unchanged for every program: whole-score-group threshold candidates, inclusive empirical precision, and maximum TP followed by maximum selected count. We never pass a mutant specification to the checker in this study.

The system under test is an executable Python module separate from the production policy comparator and independent oracle. Its build routine constructs actual Boolean candidate masks and integer counts. Its selection routine calls its own feasibility guard and uses its own priority code. Six source variants change those executable operations: strict precision, strict score thresholding, reversed secondary priority, omission of a middle group, inside-tie prefixes, and an incremented feasibility TP count. The generated source files and their SHA-256 values are retained. Tests execute the reference and each variant on the same 30 fitted-pipeline inputs. These are source mutants of a local selector, not six pre-existing products or a naturally occurring defect collection.

The adapter instruments calls to the executable feasibility guard and records the actual k/n values it receives. It obtains these values from the running program rather than from a supplied `new_spec`. It combines those events with the unchanged reference oracle's critical ratios and the policy-domain endpoints. It then calls the executable at every resulting critical point and open-cell representative. Expected memberships come from direct threshold-mask enumeration under the reference specification. Snapshot and thirteen-point baselines call that very same executable, receive the same observed output IDs, and use the same expected specification. Their distinction is policy coverage, so this comparison removes the semantic-information asymmetry of comparing score-only tools with a configured mutant model.

This adapter has an explicit and substantial trust boundary. The corpus is audited to use alpha only as an argument to the instrumented guard; an AST check enforces that syntactic restriction for the selection routine. Candidate construction and priority do not depend on alpha. The adapter checks that guard events remain the same at all evaluated policies. Under these conditions, program outcomes cannot change between the collected guard values. The argument would fail for hidden alpha-dependent branches, stateful selection, numerical precision guards not represented by the trace, or an uninstrumented external function. A consistent trace at sampled points alone would not prove event completeness for arbitrary code. We claim coverage for this audited corpus, not a universal dynamic-analysis theorem.

Instruments do not replace the executable's Boolean result: the wrapper records guard inputs and delegates the comparison to the program's original guard. Thus the strict-precision source variant keeps its strict comparison. Candidate-family and objective mutants also run their own changed code. The unchanged oracle specification supplies the desired behavior; it does not supply the changed implementation's semantics. Each certificate records the executable source hash, frozen input hash, collected guard values, complete probe list, expected and actual membership bitsets, and an observation-ID witness when they disagree. A replay audit re-executes every stored observation and verifies the bitsets and source binding.

| Source program | Runs | Nonconforming | Snapshot | Grid | Guard-complete |
|---|---|---|---|---|---|
| drop_middle_group | 30 | 16 | 2 | 7 | 16 |
| reference | 30 | 0 | 0 | 0 | 0 |
| reverse_tie_break | 30 | 30 | 22 | 30 | 30 |
| split_score_ties | 30 | 20 | 20 | 20 | 20 |
| strict_precision | 30 | 30 | 11 | 19 | 30 |
| threshold_gt | 30 | 10 | 0 | 10 | 10 |
| tp_count_plus_one | 30 | 30 | 17 | 25 | 30 |

Across 210 program/input executions, 136 fail reference conformance. The guard-complete adapter detects those 136, the thirteen-point baseline detects 111, and the alpha=0.50 snapshot detects 72. All 30 reference controls conform. The remaining source-mutant runs are equivalent only on their evaluated fixed input and domain; this is not global program equivalence. These totals are separate from, and must not be pooled with, the earlier 183/183 declared-semantics results. This study establishes that the method can consume outputs of real executable variants without being handed the mutant specification. It remains a local source-mutation experiment, and does not answer how well it integrates with an unrelated industrial selector.

## S3 Matched-input implementation costs

| Pipeline seed 0 | Workload | Snapshot | Grid 13 | Score B4 | Current guard | Exact + witness |
| --- | --- | --- | --- | --- | --- | --- |
| digits_svc_sigmoid | invariant | 4.943 (3.331) | 47.287 (26.995) | 2.912 (3.362) | 1.030 (0.540) | 5.844 (4.451) |
| digits_svc_sigmoid | roundoff | 2.347 (1.303) | 37.954 (11.913) | 1.910 (0.564) | 0.661 (0.192) | 7.516 (3.111) |
| digits_svc_sigmoid | strict_selector | 1.935 (0.264) | 28.913 (5.773) | 2.200 (0.202) | 0.538 (0.173) | 6.461 (1.425) |
| generated_rf_quantized | invariant | 0.255 (0.040) | 2.949 (0.227) | 0.315 (0.016) | 0.530 (0.245) | 1.044 (0.103) |
| generated_rf_quantized | roundoff | 0.330 (0.074) | 5.117 (2.382) | 0.076 (0.017) | 0.495 (0.044) | 1.852 (0.062) |
| generated_rf_quantized | strict_selector | 0.266 (0.017) | 3.098 (0.497) | 0.317 (0.027) | 0.561 (0.068) | 1.386 (0.153) |
| wdbc_logistic_isotonic | invariant | 0.092 (0.013) | 1.098 (0.101) | 0.109 (0.006) | 0.360 (0.051) | 0.358 (0.131) |
| wdbc_logistic_isotonic | roundoff | 0.123 (0.013) | 1.346 (0.469) | 0.034 (0.025) | 0.374 (0.205) | 0.592 (0.085) |
| wdbc_logistic_isotonic | strict_selector | 0.108 (0.037) | 1.087 (0.087) | 0.103 (0.014) | 0.344 (0.024) | 0.424 (0.084) |

Entries are median milliseconds (linear IQR), six rounds per group, 270 chronological measurements total. Every invocation rebuilds its input summaries, tracing is disabled, and method order is randomized after one warmup. The snapshot/grid use the declared SUT adapter and scan all 13 targets for the grid. Exact includes witness construction but omits JSON serialization in this comparison. Score B4/current guard flags retain their different scopes, especially for the strict-selector workload. These data describe implementation costs, not an equal-capability speed ranking. Do not pool them with the separate traced end-to-end certificate protocol.

## S4 Algorithmic cost decomposition

End-to-end timings do not identify which part of a certificate computation consumes time. We add a within-invocation ablation with instrumented stage boundaries in the production core. Construction includes input validation, sorting, candidate profiling, exact breakpoint construction and rank summaries. The sweep phase excludes time measured inside witness scans. Witness time records only scans for distinct divergent winning-state pairs. Assembly includes PSC computation and input hashing. Serialization measures JSON encoding outside the core. The certificate returned by an instrumented call is asserted equal to the uninstrumented result on a dedicated test; profiling fields are not inserted into the certificate or used by its logic.

The ablation uses three N/G settings, witness disabled/enabled, and ten rounds per condition, for 60 raw observations. Inputs are prepared outside the timer. Each condition receives a warmup and witness-mode order is randomized within a round. Unlike the original end-to-end traced protocol, this experiment disables tracemalloc. Stage medians below therefore belong to a distinct protocol and should not replace or be pooled with the earlier traced measurements.

| N | Construction | Sweep excluding witness | Witness | Assembly and hash | Serialization | Total |
|---|---|---|---|---|---|---|
| 1000 | 0.735 | 0.619 | 0.107 | 0.233 | 0.044 | 1.881 |
| 10000 | 5.648 | 4.323 | 0.889 | 1.177 | 0.099 | 13.212 |
| 100000 | 59.114 | 16.904 | 1.777 | 10.893 | 0.189 | 92.774 |

Values are milliseconds for witness-enabled divergent workloads. Each record also stores the measured end-to-end total and an unattributed residual. The validation checks that phase sums plus that residual equal the same invocation's total, and that witness-disabled calls record zero witness time. Medians of component stages generally need not sum to the median of totals; we do not force that identity or infer witness overhead by subtracting independent medians. The extra clock reads themselves incur overhead, and scheduler variation affects short phases.

The decomposition exposes both sorting/breakpoint work and output/witness work. Witness scans scale with the number of distinct divergent states, not just observation count. A low-cost invariant scan cannot stand in for successful witness construction. Likewise, an efficient policy sweep does not imply a constant-cost independently checkable certificate: hashing, serialization and an external mask-enumeration checker still consume resources. We keep algorithmic asymptotics, measured Python implementation costs, and the slower independent checker as separate claims.

## S5 Fail closed when program assumptions are unsupported

V2 checked alpha placement inside the selection routine, but that syntactic check alone could not exclude state, indirect policy dependencies or unreviewed helpers. The revised adapter uses explicit source admission before execution. Its registry contains hashes of only seven manually reviewed finite programs: the reference and six previously inspected source variants. The adapter additionally rejects direct alpha uses outside the designated guard, global/nonlocal state, top-level mutable state, and unreviewed decorators/defaults. Unknown source is refused even if it appears syntactically harmless. The registry is an auditable compatibility boundary, not an automatic proof that arbitrary Python is safe and not a security sandbox. Hashes do not inspect the semantics of a newly changed executable; an unreviewed source change requires a new review before it can receive a certificate.

Runtime checks require Boolean, correctly aligned membership vectors and valid integer guard counts. Transformed policy arguments, changed guard-event sets and nondeterministic repeated outputs prevent certification. Unsupported input/program behavior is a distinct outcome, not evidence of policy equivalence or a detected regression. The CLI uses exit 0 for a passing checked mode, exit 1 for observed nonconformance, and exit 2 for unsupported operation. Snapshot/grid passes are labeled only as no failure at their probes and are never marked as full-domain certified.

We test twelve unsupported source fixtures, including hidden state, alpha-dependent candidates/objectives, indirect guard access, dynamic evaluation, random priority, mutable defaults and unreviewed imports. Three additional runtime fixtures test wrong shape, non-Boolean membership and invalid guard arguments. All fifteen are refused without a certificate; all seven reviewed source programs remain admitted. These are designed compatibility/failure tests, not a measured detection rate on adversarial or arbitrary code. A safe refusal may require manual integration work even for a correct third-party program. Source allowlisting limits automation and must be treated as a deployment cost, not hidden behind a claim of general-purpose program verification.

## S6 Local CI execution and frequency context

We execute actual CLI subprocesses for three pipeline representatives, the reference and strict-precision program, three probe modes and three repetitions, then six complete-mode invocations on a separate controlled N=100,000/G=500 input. The sixty timed processes are accompanied by three negative CLI checks that require exit 2 for unsupported source. All reference jobs pass and every complete-mode strict-precision job fails as expected. Partial-mode outcomes reflect only their evaluated points.

For the small pipeline representatives, the across-invocation median process time is 449.36 ms and median in-gate time is 10.29 ms. On the separate 100,000-row fixture, the corresponding medians are 4292.43 ms and 3891.59 ms. Process time includes Python startup, imports, input loading and report writing; in-gate time excludes startup and includes repeated-determinism checks, candidate masks and reference comparison. They are paired measurements from these invocations, not directly comparable to the traced compact-certificate benchmark or an estimate for a remote runner. Only three repetitions per program at this scale were measured.

This is practical local workflow evidence: CI can distinguish pass, regression and unsupported programs and attach a concrete report. It does not establish an acceptable latency budget for every team, the best testing frequency, remote GitHub execution, or a production SLO. A team could choose checks per commit or per release according to its own case count and latency budget; we make no numerical frequency recommendation from one host. Actual deployment across projects remains an external-validity limitation.

## S7 Onboarding a public external selector beyond the source allowlist

We execute the installed scikit-learn `TunedThresholdClassifierCV` through its documented public API [21]. Its optimizer body is neither extracted nor edited, and it is not admitted by adding another local-program hash. A prefit score-carrier estimator exposes the frozen scores; a custom scorer returns TP*(N+1)+selected_count when the exact rational precision constraint holds and -1 otherwise. The multiplier preserves the lexicographic (TP,N) objective. Complete unique-score thresholds are passed explicitly. The adapter maps an infeasible optimum and the contract's no-positive case to abstention. These are explicit trusted integration choices, not claims about the library's default balanced-accuracy or cross-validation behavior. No predictive generalization or tuning-quality estimate is made from these fixed observations.

The workload rule is fixed before checking outcomes: seed zero from each of the three existing pipeline families, first 48 rows. WDBC, digits and random forest expose respectively 9, 48 and 13 unique thresholds. All 59 critical-point and midpoint policies conform, with 2,150 actual scorer callbacks and zero membership mismatches. The validator independently rebuilds the exact masks and executes all 59 optimizer fits again. Four configurations are explicitly refused: an integer sampled grid, a missing observed threshold, cross-validation resampling, and refitting. Full-domain coverage follows only under the complete finite candidate and exact scorer contract. It does not extend to arbitrary changes of scorer, interpolation, resampling or estimator state.

Observed onboarding effort consists of 76 physical Python lines in the executable study (including its measurement/report code), four public configuration hooks and zero upstream source edits. Source/class hashes, callbacks, decisions and execution times are retained. These are inspectable integration artifacts; programmer hours, independent team effort and maintenance costs were not measured. The scorer, score carrier and abstention mapping remain trusted glue.

The preceding public-API study concerns a second component in scikit-learn. V4 additionally inspected eval-toolkit but did not execute it because its Python >=3.13 requirement conflicted with V4's Python 3.12.10 environment. That historical refusal is retained in the V4 results. V5 uses a separate Python 3.13.18 environment and executes the installed second project as described in the main paper; the former compatibility barrier is not represented as an executed case.

## S8 Direct SMT baseline on the same equivalence contract

Beyond broad capability comparisons, we encode the external threshold-consumer task directly in Z3 [16]. Alpha is a real variable in [3/10,9/10]. A candidate is feasible under the exact linear inequality alpha*n <= k. Candidates are ordered by their fixed (TP,N) priority, and nested if-then-else terms compute the winning selected count. For this same-score task, candidates from both versions belong to one chain of score-prefix memberships, so different winning counts are equivalent to different selected memberships. That reduction does not apply to arbitrary score reorderings; we do not use it for them.

The solver asks whether any policy makes the two winning counts unequal. SAT supplies a rational policy witness; UNSAT asserts full-domain equality for the encoded task. Timeout/unknown is never interpreted as equivalence. We independently re-evaluate each SAT model with direct memberships. The complete partition checker separately emits all interval/endpoint evidence and PSC. Both therefore share a Boolean equivalence contract, while their diagnostic outputs differ. The baseline is our explicit finite SMT encoding using an established solver, not a reproduction of a published threshold-testing tool.

Across 93 variant/input tasks and three repetitions, all 279 solver verdicts agree with partition verification; there are 0 unknown outcomes and every SAT policy is independently checked. Persisted SMT-LIB queries are resolved again by the artifact validator. Median encoding time is 8.222 ms and median solving time is 0.576 ms across those queries. Counts/masks are prepared before these timers. These measurements do not establish a speed ranking against full interval construction with input validation, hashing, witnesses and JSON serialization. The direct SMT results demonstrate that full-domain Boolean comparison is also attainable with a general reasoning engine, narrowing the defensible contribution to the selector-specific contract, complete diagnostics, independently checkable output and scoped integration.

## S9 Reproduction and assurance levels

The original standalone failure arose because the experiment driver read a historical 255-row grid CSV from a neighboring submission tree. The corrected driver reads a bundled `inputs/historical/` copy and asserts its checksum from the input manifest before any comparison. Default `run_all.py` works from frozen arrays within the extracted artifact; it does not refit models, reinstall dependency versions or need the old submission directory. Optional model refitting is a separate command with its source-data requirements documented. The distinction prevents the term “standalone” from silently including unbundled training assets.

Assurance has several layers. Unit/exhaustive tests validate finite implementations on small and randomized cases. The independent certificate checker reconstructs actual threshold masks on all stored application and declared-mutant certificates. The program adapter calls a separate executable and checks the unchanged reference contract under an explicit guard-coverage restriction. Fresh version workers establish what two actual dependency binaries computed. Checksummed packaging and a clean extraction run test delivery rather than mathematical correctness. None of these layers, alone or together, establishes authenticity of upstream measurements, population model quality, a universally correct verifier or an industrial real-bug detection rate.

The previous artifact is retained as a historical ZIP. Revised raw records are regenerated rather than mixed with old timings. Source snapshots bind the producer used for those records. A final manifest is generated after documents, evidence and reports have been assembled. The clean-run report names the extracted path, absence of neighboring SUBMISSION_PACKAGE, interpreter, stage exit codes and resulting logical summaries. It is a local clean reproduction, not independent human replication. A broader upstream-confirmed bug corpus and prospective deployment study remain work outside this revision; two isolated-source upstream defect case studies are now included.

## S10 Detailed relation to verification and testing foundations


Parameter-region verification predates this work. Storm's official parametric-model documentation demonstrates region checking and parameter-space partitioning [6]. Junges and colleagues study parameter synthesis and coverage of parameter space for Markov models [7]. Their models, probability properties and region procedures differ from deterministic threshold membership, but they rule out presenting region partitioning itself as our invention. We do not benchmark Storm as though it were a drop-in selected-membership comparator; such a comparison would require a faithful encoding and a common property.

Regression verification also already studies equivalence of closely related program versions [8]. Our restricted finite-input selector contract makes its policy critical values explicit and directly enumerable; it does not solve general program equivalence. The program-output experiment covers a known guard-constrained corpus rather than establishing a general-purpose regression verifier. Treating the old version as a de facto specification may preserve an old bug; applications that require correctness rather than compatibility need an agreed reference contract.

The separation between a producer and a checker is likewise established. Alkassar and colleagues describe verification of certifying computations [9]. Necula and Schneck's proof-carrying-code work studies machine-checkable safety evidence and the trusted checker boundary [10]. Our certificates are concrete finite membership evidence checked by another implementation. They are not machine-checked proofs of arbitrary executable safety, and their Python checker is not a formally verified trusted kernel. An input digest prevents silent accidental mismatches but neither authenticates the original observations nor proves adapter faithfulness.

Testing ML implementations through metamorphic properties and mutation analysis is also established. The 2021 work on stability-derived relations targets linear-classification programs [11], while Xie and colleagues study classifier implementation testing and actual faults in Weka [12]. Those programs and properties differ from our fixed-label threshold selector. Their empirical designs motivate evaluating executed code and avoiding an inference from model accuracy to program correctness. Our expanded corpus addresses direct execution for a local selector, but remains weaker external-validity evidence than a curated set of independently documented, naturally occurring defects.

A focused search across these five areas expands the primary-source basis and clarifies the closest conceptual overlap. It is still not a systematic review with exhaustive database coverage and forward/backward citation closure. The appropriate novelty claim is the specialized integration of endpoint-correct finite policy equivalence, verifiable membership evidence and explicitly scoped testing adapters. A first-in-literature claim remains unsupported. The expanded paper and artifact are provided for further technical review rather than labeled ready for acceptance at a particular journal.



Supplement S8 retains the 93-task Boolean SMT study. The complete-region comparisons and policy-domain query study address richer matched outputs separately.



## S11 Detailed contribution map


General parameter synthesis and AllSMT already supply machinery for exploring property regions; neither the finite partition fact nor complete-region capability is exclusive to this work. The contribution is a concrete verification interface with declared policy semantics, observation identities, endpoint ownership and input-bound diagnostic obligations, plus an independently implemented consumer and explicit integration limits. The strongest evidence is consistency under those obligations and measured engineering tradeoffs, rather than a new general solver principle.

| Closest foundation | What is established there | Specific work instantiated and evaluated here |
|---|---|---|
| Parametric verification and synthesis [6,7,20] | Reasoning about parameter-indexed properties and regions | Fixed empirical selected-ID equivalence, with exact policy/identity/numerical contracts and boundary ownership |
| Predicate enumeration and WMI [23-25] | Complete model-region exploration and integration | Matched selector diagnostics, exact PSC as uniform interval length and representative observation witnesses; no general enumeration novelty claimed |
| Certifying computations [9,17] | Producer/checker separation and evidence validation | A specified membership certificate and separately coded streaming consumer, replayed over 428 certificates with paired cost measurements |
| Rounding preimages [26] | Arithmetic reasoning about rounding cells | A checked mapping from an actual binary64 selector interface to rational cuts, followed by allowed-policy-set significance assessment |

The table identifies the implemented object and evidence; it is not a negative claim that existing tools cannot encode the same task. Our SMT baseline demonstrates that they can. The streaming data structures are established techniques, the source-replay bridges remain trusted integration code, and first-in-literature novelty is not established by this focused comparison. Two independently documented defects strengthen external evidence but do not by themselves prove a broad defect-detection advantage.


## S12 Operator-level mutation records

| Variant | Runs | Policy-divergent | Snapshot | Grid | ID violations |
| --- | --- | --- | --- | --- | --- |
| aligned_permutation_control | 30 | 0 | 0 | 0 | 0 |
| drop_middle_group | 30 | 16 | 2 | 7 | 0 |
| identity_control | 30 | 0 | 0 | 0 | 0 |
| monotone_control | 30 | 0 | 0 | 0 | 0 |
| reverse_tie_break | 30 | 30 | 22 | 30 | 0 |
| round_one_decimal | 30 | 26 | 24 | 26 | 0 |
| roundoff_tie_split | 30 | 21 | 16 | 20 | 0 |
| row_id_misalignment | 30 | 0 | 0 | 0 | 30 |
| split_score_ties | 30 | 20 | 20 | 20 | 0 |
| strict_precision | 30 | 30 | 11 | 19 | 0 |
| threshold_gt | 30 | 10 | 0 | 10 | 0 |
| tp_count_plus_one | 30 | 30 | 17 | 25 | 0 |

## S13 Repeated reuse cost protocol and limits

See results/v8/reuse_protocol.json for the predeclared selection and requests, reuse_raw.csv for 720 chronological observations, reuse_summary.csv for 144 median/IQR groups, reuse_query_plans.json for 2,028 distinct plans and reuse_outputs/ for every saved method answer. Setup includes certificate construction/JSON/full independent verification or independent mask/SMT preparation. The shared interpolation computation is outside all method timers. Request types, endpoints, batch sizes and all six inputs are retained even when a method is slower. Raw observations and deterministic query answers are separately audited. A crossing is defined only on tested batches 1/8/32/128. No developer study, production-policy inventory or universal amortization bound is claimed.

## S14 Earlier V8 request cost protocol


We now test whether reuse pays for certificate setup, rather than treating a large query count as a productivity result. Six inputs are fixed before measurement: the upstream int8 fixture, Unix-second int32 fixture, small-int32 control, and seed zero of each pipeline family. These are existing controlled SciPy propagation inputs, not six new projects or production configurations. Two request types use distinct rational singleton policies or width-1/20 windows spread deterministically over [0.30,0.90], with varying endpoint ownership. Batches contain 1, 8, 32 or 128 requests. The scenarios test computational costs; no application policy-frequency distribution is asserted.

The common output is Boolean existence of a difference plus a rational witness. Direct masks prepare candidate memberships once, then evaluate the requested point or all relevant critical points/open cells for a window, stopping on a difference. Incremental Z3 prepares the independent selected-bitset encoding once per batch and uses push/pop for each request; unknown/timeout fails the study. The certificate route includes construction, a JSON roundtrip and independent full verification once per batch before queries. Its current API materializes intersections before projecting the Boolean answer, so that actual implementation cost remains included. No route memoizes query results; requests within a batch are distinct. All routes reuse the same executed interpolation outputs outside timing. These totals start from frozen score vectors; they exclude common SUT execution, imports, disk I/O and human investigation.

Each case/type has one warmup per method, followed by five fresh setups per batch and method with seeded randomized method order and no allocation tracing. There are 720 timing records, 144 statistical groups and 2,028 distinct case/query plans. All 30,420 method/request answers across methods and repetitions agree, and every reported rational witness is checked against independent selection. These are repeated computational observations, not independent defects or deployment trials. Raw phase costs, query outputs and median/IQR records are retained; medians are not pooled across inputs.

The table reports total median milliseconds (IQR) for batch 128, including setup. The other batch sizes and the separately measured setup/query phases remain in reuse_summary.csv.

| Workload | Request | Checked certificate | Direct masks | Incremental Z3 |
|---|---|---|---|---|
| Upstream int8 | Point | 9.49 (1.84) | 2.65 (3.24) | 125.92 (9.24) |
| Upstream int8 | Window | 26.04 (1.75) | 18.96 (1.72) | 198.72 (26.04) |
| Unix int32 | Point | 11.47 (5.35) | 3.61 (0.35) | 149.92 (41.33) |
| Unix int32 | Window | 20.02 (5.50) | 15.70 (1.66) | 129.55 (29.31) |
| Small int32 control | Point | 9.26 (1.04) | 3.63 (0.87) | 43.07 (8.67) |
| Small int32 control | Window | 8.12 (1.80) | 15.74 (0.33) | 38.59 (3.91) |
| WDBC seed 0 | Point | 17.45 (2.96) | 5.91 (1.27) | 206.53 (21.52) |
| WDBC seed 0 | Window | 100.67 (34.56) | 22.59 (6.40) | 302.73 (47.63) |
| Digits seed 0 | Point | 72.81 (6.03) | 21.45 (1.89) | 366.95 (61.65) |
| Digits seed 0 | Window | 294.57 (59.74) | 42.72 (19.33) | 424.42 (138.27) |
| RF seed 0 | Point | 27.40 (10.63) | 10.77 (0.15) | 334.45 (35.30) |
| RF seed 0 | Window | 52.09 (4.23) | 21.08 (1.96) | 290.38 (52.00) |

At batch 128 the checked certificate is faster than direct masks on 0/6 singleton and 1/6 window inputs; it is faster than this incremental Z3 encoding on 6/6 and 6/6 respectively. Observed sustained crossings against direct masks are Small int32 control / continuous_window at batch 32. A sustained crossing means the first tested batch with a lower certificate total median at that and every larger tested batch; it is a discrete observed comparison, not an inferred exact threshold, significance test or extrapolation beyond 128 requests. Five repetitions on one host do not establish a population advantage.

The mostly negative comparison against direct masks constrains the practical claim. Reuse alone does not justify building a certificate for a small finite decision set or guarantee an advantage even for continuous windows. A separately checkable, persistable diagnostic object may be required for exact localization or handoff, but this experiment does not monetize that requirement or measure a developer's debugging time. It measures a computational tradeoff against specified implementations, including a reused solver, and leaves industrial policies, human triage benefit and superiority over an independently optimized parametric tool unresolved.


## S15 Boolean API study and comparison panels

The exact protocol is results/v9/boolean_protocol.json. Both certificate routes pay construction, JSON roundtrip and the same independent full verification; the indexed route also pays copying/freezing/index construction. This is the assurance-matched API panel. Direct masks and incremental Z3 answer the same Boolean question without emitting/checking a complete diagnostic object, so four-route totals are a separate request-cost panel with unequal evidence obligations. The original six inputs and 2,028 plans are reused: 960 timing records, 192 groups and 40,560 repeated method answers are not new workloads or defects. Full per-phase medians/IQRs and raw observations are retained. A descriptive speed ratio is not a statistical or deployment guarantee. BOOLEAN_QUERY_AND_ASSURANCE.md gives component-merging/endpoint reasoning, asymptotic scope and refusal behavior.
