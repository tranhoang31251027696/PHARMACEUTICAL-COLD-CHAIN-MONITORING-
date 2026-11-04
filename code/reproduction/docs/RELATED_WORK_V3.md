### Direct SMT baseline on the same equivalence contract

Beyond broad capability comparisons, we encode the external threshold-consumer task directly in Z3 [16]. Alpha is a real variable in [3/10,9/10]. A candidate is feasible under the exact linear inequality alpha*n <= k. Candidates are ordered by their fixed (TP,N) priority, and nested if-then-else terms compute the winning selected count. For this same-score task, candidates from both versions belong to one chain of score-prefix memberships, so different winning counts are equivalent to different selected memberships. That reduction does not apply to arbitrary score reorderings; we do not use it for them.

The solver asks whether any policy makes the two winning counts unequal. SAT supplies a rational policy witness; UNSAT asserts full-domain equality for the encoded task. Timeout/unknown is never interpreted as equivalence. We independently re-evaluate each SAT model with direct memberships. The complete partition checker separately emits all interval/endpoint evidence and PSC. Both therefore share a Boolean equivalence contract, while their diagnostic outputs differ. The baseline is our explicit finite SMT encoding using an established solver, not a reproduction of a published threshold-testing tool.

Across 93 variant/input tasks and three repetitions, all 279 solver verdicts agree with partition verification; there are 0 unknown outcomes and every SAT policy is independently checked. Persisted SMT-LIB queries are resolved again by the artifact validator. Median encoding time is 8.222 ms and median solving time is 0.576 ms across those queries. Counts/masks are prepared before these timers. These measurements do not establish a speed ranking against full interval construction with input validation, hashing, witnesses and JSON serialization. The direct SMT results demonstrate that full-domain Boolean comparison is also attainable with a general reasoning engine, narrowing the defensible contribution to the selector-specific contract, complete diagnostics, independently checkable output and scoped integration.

### Closest method comparison and remaining novelty boundary

The certifying-algorithm literature explicitly separates an algorithm's mathematical correctness from correctness of a particular computed output [17]. Parameter synthesis in PROPhESY [20] and Storm studies regions for probabilistic properties; parametric monitoring [19] studies parameter-indexed runtime properties; robust classification under uncertain operating conditions [18] studies selection across varying environments. These works establish relevant foundations, not negative capability claims. None should be described as lacking endpoint handling merely because our inspected example targets a different property. A broader systematic search may still uncover a closer selector-specific tool.

| Method considered | Matched question here | Evidence actually compared | Remaining distinction |
|---|---|---|---|
| Snapshot and thirteen-point probes | Membership compatibility at chosen policies | Executed on identical SUT outputs and contract | Cannot certify unprobed policies |
| Direct Z3 encoding | Existence of any divergent policy on finite nested candidates | 93 actual equivalence tasks, rational counterexample rechecks | One counterexample/Boolean rather than all intervals and PSC |
| Our partition and checker | Same Boolean task plus full divergence localization | Exact endpoints, intervals and independently replayed memberships | Specialized finite contract and explicit adapter assumptions |
| Certifying computations [9,17] | Trust in a particular computation and checker | Primary-source conceptual comparison | General foundation, not an empirical competing selector tool |
| PROPhESY/Storm [6,7,20] | Parameter-region property verification | Primary-source property/input-model comparison | No faithful probabilistic encoding benchmark claimed |
| Parametric monitoring [19] | Monitoring properties across parameter instances | Primary-source semantic comparison | Object/trace parameters differ from empirical precision breakpoints |
| Robust classification [18] | Classifier choice as operating conditions vary | Primary-source objective comparison | Does not make the finite-breakpoint idea novel |

We consequently make no first-in-literature claim for parameter partitioning, regression equivalence or producer/checker separation. The additional same-task SMT experiment is a useful check against overstating novelty: a general solver reaches the same Boolean answers. The proposed research contribution remains the integrated finite selector contract and its endpoint-sensitive diagnostic certificates, scoped executable adapters, and evidence across controlled and one independently documented upstream case. This is stronger substantiation than a scope-only table, but does not certify novelty at a particular journal tier.



[14] scikit-learn issue #23213 (2022). precision_recall_curve is not returning the full curve at high recall. Upstream bug report and maintainer discussion. https://github.com/scikit-learn/scikit-learn/issues/23213

[15] scikit-learn PR #23214 (2022). FIX compute precision-recall at 100% recall. Merged 2 May 2022. https://github.com/scikit-learn/scikit-learn/pull/23214

[16] de Moura, L.; Bjørner, N. (2008). Z3: an efficient SMT solver. TACAS. https://www.microsoft.com/en-us/research/publication/z3-an-efficient-smt-solver/

[17] McConnell, R. M.; Mehlhorn, K.; Näher, S.; Schweitzer, P. (2011). Certifying algorithms. Computer Science Review, 5(2), 119–161. https://doi.org/10.1016/j.cosrev.2010.09.009

[18] Provost, F.; Fawcett, T. (2001). Robust Classification for Imprecise Environments. Machine Learning, 42, 203–231. https://arxiv.org/abs/cs/0009007

[19] Chen, F.; Roşu, G. (2009). Parametric trace slicing and monitoring. TACAS, 246–261. https://experts.illinois.edu/en/publications/parametric-trace-slicing-and-monitoring/

[20] Dehnert et al. (2015). PROPhESY: A PRObabilistic ParamEter SYnthesis Tool. CAV. Author manuscript: https://www.cs.ru.nl/personal/nilsjansen/files/publications/dehnert-et-al-cav-2015.pdf
