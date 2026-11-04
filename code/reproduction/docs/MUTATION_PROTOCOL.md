# Mutation and pipeline protocol

Thirty newly fitted pipelines: ten seeds each for (i) WDBC logistic regression + isotonic calibration, (ii) digits, zero vs rest, LinearSVC + sigmoid/Platt calibration, (iii) generated imbalanced classification + random forest + score quantization to 0.01. Families vary data, learner, score shape, prevalence and ties. These are three local benchmark families, not independent organizations, deployers or naturally occurring software versions.

Split: 50% model fitting, 25% calibration (reserved and unused for uncalibrated RF), 25% evaluation, stratified, with explicit indices and disjointness assertions. No test label enters training or calibration. Evaluation labels do enter the *empirical policy selector*, as in the original finite-input contract: this verifies that selector on fixed labeled data, not a deployable test-label-free operating procedure. WDBC isotonic calibration is small; no calibrated-probability superiority is claimed.

The base old/new pipeline comparison casts scores to float32 then back to float64 as a controlled numerical change. This is not evidence of an actual dependency-release regression. Existing frozen cold-chain and public pilot comparisons remain inherited evidence with their own provenance.

For each newly fitted base pipeline, run these twelve executable functional variants/controls on [0.30,0.90]:

| Variant | Executable change | Classification |
|---|---|---|
| strict_precision | Candidate precision >= alpha becomes > alpha | Selector fault model |
| threshold_gt | Candidate membership >= threshold becomes > threshold at the original observed levels; full-set candidate is omitted | Selector fault model |
| reverse_tie_break | Prefer fewer rows when TP counts tie | Selector fault model |
| drop_middle_group | Remove the middle distinct-score candidate | Selector fault model |
| split_score_ties | Permit stable inside-tie prefixes | Selector fault model |
| tp_count_plus_one | Add one to feasibility TP, capped at selected N, while objective uses actual TP | Count fault model |
| round_one_decimal | Quantize original probabilities to one decimal | Controlled numerical change; not automatically a defect |
| roundoff_tie_split | Add seeded -u,0,+u at float32 half-epsilon scale | Controlled numerical change; not automatically a defect |
| row_id_misalignment | Reverse new scores and new IDs without aligning old inputs | Input-contract violation, not PSC event |
| identity_control | Keep scores unchanged | Valid policy-equivalence control |
| monotone_control | Apply exactly represented 3*s+2 floating transformation to this workload; verify resulting equality rather than assume | Valid control on observed data |
| aligned_permutation_control | Apply the same permutation to labels, old/new scores and IDs | Valid policy-equivalence control |

Mutants are hand-designed executable semantic variants, not a source-code mutation engine or a random sample of real faults. Equivalent-mutant claims are restricted to the observed input/domain; global program equivalence is not established. Numerical changes with frontier differences are not labeled defects unless an agreed contract requires policy invariance. The detection denominator is independently observed policy divergence on that finite workload; ID violations are counted separately.

Baselines: snapshot compares actual old/mutant selected membership at alpha=0.50; grid compares the same at thirteen targets 0.30,...,0.90; B4 compares score-induced candidate families; current full guard receives the same score arrays at alpha=0.50. B4 and the current guard do not inspect changed selector implementations when scores remain identical. Therefore their low totals on selector mutants reflect scope limits, not a claim of inferiority for their original structural contracts. Report their structural flags separately from policy false alarms.

Exact method and verifier are configured with the explicit old/new selector contract. This assumes an adapter faithful to each variant's semantics. It does not reverse engineer arbitrary changed code. A future industrial study needs a separately validated real-SUT adapter and naturally occurring defects.

All exact certificates are checked by threshold-mask enumeration and exact fraction tests at independently reconstructed breakpoints and midpoints. Certificates retain endpoint-only changes even if PSC=0. Valid controls measure observed false alarms only; zero in 90 runs is not a population guarantee.

Latency experiments use one host and 10 rounds per N/G/workload/mode, an unrecorded warmup, and randomized mode order each round. All full certificate construction, input validation/hashing and JSON serialization are timed under tracemalloc. Inputs are allocated before tracing; peak is auxiliary MiB, not RSS. Witness-disabled and witness-enabled paths share the same policy algorithm. Invariant and divergent paths are measured separately; divergent witness-enabled paths actually emit witnesses. IQR uses NumPy's linear quartiles. These timings do not isolate witness cost by subtracting noisy medians and do not compare directly to prior one-alpha guard timings.
