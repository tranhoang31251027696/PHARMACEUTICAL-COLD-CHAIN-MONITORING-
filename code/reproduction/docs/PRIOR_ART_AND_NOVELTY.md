# Focused prior-art check (29 October 2026)

This is a scoped check of primary publications and official documentation, not a systematic review or proof of absence. The unattributed 2026 developer-adoption statement in the proposal is not used as evidence; an exact source was not supplied. Journal quartile claims from aggregators are not carried into the new manuscript.

| Primary source | Verified relevance | Distinction and remaining question |
|---|---|---|
| Rath & Hughes (2022), *Optimizing Early Warning Classifiers to Control False Alarms via a Minimum Precision Constraint*, AISTATS/PMLR 151:4895–4914. https://proceedings.mlr.press/v151/rath22a.html | Optimizes recall subject to a precision constraint; discusses post-hoc threshold selection versus training objectives. | Constrained precision selection is established. Our task compares fixed versioned selected memberships across policies; a broader search is needed before claiming the certificate itself is novel. |
| Mackey, Luo & Eban (2018), *Constrained Classification and Ranking via Quantiles*. https://arxiv.org/abs/1803.00067 | Explicit threshold modeling for prediction constraints and model-agnostic constrained learning. | A threshold/policy parameter is not a new concept. The finite fixed-input regression contract and exact endpoint-sensitive comparison are the proposed integration. Abstract-level relevance check only. |
| Tasche (2018), *A plug-in approach to maximising precision at the top and recall at the top*. https://arxiv.org/abs/1804.03077 | Gives optimality results for posterior-probability thresholding under constrained classification. | Not a basis for claiming our finite breakpoint lemma is unprecedented. Abstract-level relevance check only. |
| *Assessing the strength of Metamorphic Testing applied to optimisation software—Experience from industry* (2025), IST, DOI 10.1016/j.infsof.2025.107807. https://www.sciencedirect.com/science/article/pii/S0950584925001466 | Publisher-indexed description combines metamorphic relations and traditional mutation testing to assess testing effectiveness. | Supports mutation-based evaluation as an established methodology, not our novelty. Publisher page full retrieval returned HTTP 403; only indexed publisher description was used. No detailed numerical comparison is asserted. |
| scikit-learn, CalibratedClassifierCV documentation, v1.9.1. https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV | Specifies isotonic/sigmoid calibration, disjoint fit/calibration requirements for frozen models, and small-sample isotonic caveats. | Guides our three-way splits and threat statement; does not establish external validity or calibration quality. |

Candidate contribution: endpoint-correct exact policy equivalence with input-bound independently checkable interval/observation witnesses, exact domain-length sensitivity, and a controlled mutation/pipeline evaluation. These parts should be presented together. The partition lemma alone is an elementary consequence of finitely many feasibility comparisons and should not be sold as a broadly new optimization theorem.

Remaining publication work: expand searches across DBLP/ACM/IEEE/Springer for parametric regression testing, multi-parametric optimization, decision equivalence, and robustness certificates; inspect full texts and backward/forward citations; compare any directly matching tools. No claim that this local extension is sufficient for IST/TSE/TOSEM acceptance or any particular JCR category/year is made.


## Revision 2 expanded comparison

Relation to existing verification and testing methods

Parameter-region verification predates this work. Storm's official parametric-model documentation demonstrates region checking and parameter-space partitioning [6]. Junges and colleagues study parameter synthesis and coverage of parameter space for Markov models [7]. Their models, probability properties and region procedures differ from deterministic threshold membership, but they rule out presenting region partitioning itself as our invention. We do not benchmark Storm as though it were a drop-in selected-membership comparator; such a comparison would require a faithful encoding and a common property.

Regression verification also already studies equivalence of closely related program versions [8]. Our restricted finite-input selector contract makes its policy critical values explicit and directly enumerable; it does not solve general program equivalence. The program-output experiment covers a known guard-constrained corpus rather than establishing a general-purpose regression verifier. Treating the old version as a de facto specification may preserve an old bug; applications that require correctness rather than compatibility need an agreed reference contract.

The separation between a producer and a checker is likewise established. Alkassar and colleagues describe verification of certifying computations [9]. Necula and Schneck's proof-carrying-code work studies machine-checkable safety evidence and the trusted checker boundary [10]. Our certificates are concrete finite membership evidence checked by another implementation. They are not machine-checked proofs of arbitrary executable safety, and their Python checker is not a formally verified trusted kernel. An input digest prevents silent accidental mismatches but neither authenticates the original observations nor proves adapter faithfulness.

Testing ML implementations through metamorphic properties and mutation analysis is also established. The 2021 work on stability-derived relations targets linear-classification programs [11], while Xie and colleagues study classifier implementation testing and actual faults in Weka [12]. Those programs and properties differ from our fixed-label threshold selector. Their empirical designs motivate evaluating executed code and avoiding an inference from model accuracy to program correctness. Our expanded corpus addresses direct execution for a local selector, but remains weaker external-validity evidence than a curated set of independently documented, naturally occurring defects.

The comparison below records what is demonstrated or discussed in the checked sources. “Not established here” means no matching capability was established in our inspected material; it is not proof that a tool or research area cannot support it. Complexity statements are for different mathematical objects and are not directly comparable.

| Approach | Domain and boundary treatment | Changed selector code | Checkable evidence | Complexity and comparison scope |
|---|---|---|---|---|
| Snapshot / fixed grid | Only sampled policies; no full-domain guarantee | Observes executable outputs at probes | Output differences | Number of probes times SUT cost |
| Score B4 | Full score-induced candidate family, no alpha-region verdict | Does not inspect selector code | Structural equality Boolean | Structural task rather than policy conformance |
| Storm / parameter synthesis [6,7] | Parametric probabilistic regions; exact setup and coverage depend on procedure | Requires a model of program behavior | Model/property analysis | Not the same selector input problem; no latency ranking claimed |
| Regression verification [8] | Equivalence of related programs, beyond a fixed alpha grid | Central research target | Verification results under its method | General program equivalence is not reduced to our N/G bound |
| Certifying computations / PCC [9,10] | Witness/checker and proof trust design, not this alpha contract | Depends on supplied proofs or verified computation | Core purpose | General framework, not a competing selector benchmark |
| ML metamorphic testing [11,12] | Relations across executions, not this full-domain contract | Executed classifier implementations | Violated relations and mutation evidence | A complementary testing methodology |
| Our declared-semantics certificate | Exact rational endpoints and open cells for fixed candidate contracts | Requires a faithful finite adapter | Input-bound interval and ID witness | O(N log N+G log G+K+ND), unit-cost fraction assumption |
| Our executed-program adapter | Complete for alpha-only-in-guard source corpus | Calls changed source directly; no new_spec | Executable hash and replayable membership probes | Depends on traced guards and executed SUT cost; no arbitrary-code guarantee |

A focused search across these five areas expands the primary-source basis and clarifies the closest conceptual overlap. It is still not a systematic review with exhaustive database coverage and forward/backward citation closure. The appropriate novelty claim is the specialized integration of endpoint-correct finite policy equivalence, verifiable membership evidence and explicitly scoped testing adapters. A first-in-literature claim remains unsupported. The expanded paper and artifact are provided for further technical review rather than labeled ready for acceptance at a particular journal.




[6] Storm project. Running Storm on Parametric Models. Official documentation. https://www.stormchecker.org/documentation/usage/running-storm-on-parametric-models.html

[7] Junges, S.; Ábrahám, E.; Hensel, C.; Jansen, N.; Katoen, J.-P.; Quatmann, T.; Volk, M. Parameter synthesis for Markov models: covering the parameter space. Formal Methods in System Design. https://doi.org/10.1007/s10703-023-00442-x

[8] Godlin, B.; Strichman, O. (2009). Regression Verification. DAC. Author manuscript: https://ofers.dds.technion.ac.il/publications/dac09.pdf

[9] Alkassar, E.; Böhme, S.; Mehlhorn, K.; Rizkallah, C. (2013). A Framework for the Verification of Certifying Computations. https://arxiv.org/abs/1301.7462

[10] Necula, G. C.; Schneck, R. R. (2002). Proof-Carrying Code with Untrusted Proof Rules. International Symposium on Software Security. Author manuscript and formalization: https://people.eecs.berkeley.edu/~necula/ISSS02/

[11] Towards effective metamorphic testing by algorithm stability for linear classification programs. (2021). Journal of Systems and Software, 180, 111012. https://doi.org/10.1016/j.jss.2021.111012

[12] Testing and validating machine learning classifiers by metamorphic testing. (2011). Journal of Systems and Software. https://www.sciencedirect.com/science/article/pii/S0164121210003213

[13] SciPy project. Release news and versions 1.15.3 and 1.18.1. https://scipy.org/news/
