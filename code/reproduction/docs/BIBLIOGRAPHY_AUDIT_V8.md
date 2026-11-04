# Primary source and metadata check for the 28 references

Checked on 30 October 2026. This audit checks source identity, displayed metadata and the bounded claim assigned to each citation. It is not an exhaustive prior-art search, independent replication of cited work, or a full-text methodological review of all 28 works. Some publisher direct fetches returned 403 or redirect/cache errors; primary author/institution copies or indexed publisher content were used as stated. No inaccessible full text is represented as read.

| Ref | Primary source checked | Scope and action |
|---|---|---|
| 1 | https://proceedings.mlr.press/v151/rath22a.html | Title, authors, 2022, PMLR 151:4895–4914 and precision-constrained training/threshold context. Does not establish our originality. |
| 2 | https://arxiv.org/abs/1803.00067 | Author-deposited title/authors/2018 abstract: constrained classification with explicit threshold modeling. Abstract-level context. |
| 3 | https://arxiv.org/abs/1804.03077 | Author-deposited title/author/2018 abstract: optimal thresholding under related constrained objectives. |
| 4 | https://www.sciencedirect.com/science/article/pii/S0950584925001466 | Indexed publisher title, volume 186, article 107807 and CRediT names. Add Duque-Torres, Klammer, Fischer, Pfahl and Ramler. Direct fetch blocked; indexed content supports bounded metamorphic/mutation context, not a full-text comparison. |
| 5 | https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html | Official 1.9.1 API page; repair canonical .html URL. Runtime package/source remains separately pinned. |
| 6 | https://www.stormchecker.org/documentation/usage/running-storm-on-parametric-models | Official region checking/partitioning documentation. Canonical URL updated. No claim Storm lacks endpoint/region capabilities. |
| 7 | https://link.springer.com/article/10.1007/s10703-023-00442-x and https://publications.rwth-aachen.de/record/985754/ | Primary publisher/institution metadata: published 2024, Formal Methods in System Design 62:181–259. Add year/volume/pages; DOI's 2023 string is not publication year. |
| 8 | https://ofers.dds.technion.ac.il/publications/dac09.pdf | Author PDF identifies Godlin/Strichman, Regression Verification and closely related version equivalence. No unrestricted program equivalence claim for this artifact. |
| 9 | https://arxiv.org/abs/1301.7462 | Author-deposited 2013 manuscript and producer/checker framework. Keep cited arXiv year; do not silently relabel it as a journal version. |
| 10 | https://people.eecs.berkeley.edu/~necula/ISSS02/ | Author companion confirms Necula/Schneck, ISSS 2002 and Coq formalization. Our checker is not claimed formally verified PCC. |
| 11 | https://cs.nju.edu.cn/_upload/tpl/01/55/341/template341/1_publications/21/JSS21.pdf and publisher DOI 10.1016/j.jss.2021.111012 | Add full authors Yang, Li, Wang, Xu and Ma; 2021 JSS 180:111012. Author copy supports stability-derived metamorphic context. |
| 12 | https://www.cs.columbia.edu/wp-content/uploads/sites/7/2016/08/jss2011.pdf | Primary author copy identifies Xie, Ho, Murphy, Kaiser, Xu and Chen; JSS 84(4):544–558, DOI 10.1016/j.jss.2010.11.920. Add authors/pages/DOI. |
| 13 | https://scipy.org/news/ | Official releases 1.15.3 and 1.18.1. Release identity is not evidence that a numerical difference is a bug. |
| 14 | https://github.com/scikit-learn/scikit-learn/issues/23213 | Official issue identity; pinned historical source and source-replay protocol carry executable evidence separately. |
| 15 | https://github.com/scikit-learn/scikit-learn/pull/23214 | Official fix identity. Saved merge/source provenance and executed affected/fixed controls remain the evidence for the case. |
| 16 | https://www.microsoft.com/en-us/research/publication/z3-an-efficient-smt-solver/ | Primary research page confirms de Moura/Bjørner, TACAS 2008 and SMT solver context; not evidence of optimality of our encoding. |
| 17 | https://researchportalplus.anu.edu.au/en/publications/certifying-algorithms/ | Coauthor institution confirms 2011 journal version, CSR 5(2):119–161 and DOI. General certifying-algorithm foundation only. |
| 18 | https://arxiv.org/abs/cs/0009007 | Author-deposited title/authors/operating-condition context; linked journal version is 2001. Different object from finite membership regression. |
| 19 | https://experts.illinois.edu/en/publications/parametric-trace-slicing-and-monitoring/ | Author institution confirms Chen/Rosu, TACAS 2009, 246–261 and parameter-indexed trace properties. |
| 20 | https://www.cs.ru.nl/personal/nilsjansen/files/publications/dehnert-et-al-cav-2015.pdf | Author PDF confirms eight authors and incremental parameter synthesis. Expand Dehnert et al. to the author list; CAV 2015, LNCS 9206:214–231. |
| 21 | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TunedThresholdClassifierCV.html | Official 1.9.1 API; actual integration and unsupported configurations separately tested locally. |
| 22 | https://brandon-behring.github.io/eval-toolkit/methodology/thresholds.html | Official methodology retrieved. Live pinned commit-tree fetch unavailable; installed complete source is instead bound to the bundled source manifest and wheel hash. No production-policy requirement inferred from examples/tests. |
| 23 | https://mathsat.fbk.eu/apireference.html | Official API includes msat_all_sat and important-atom enumeration. Capability context only; MathSAT is not benchmarked here. |
| 24 | https://www.ijcai.org/proceedings/2017/100 | Official proceedings confirm Morettin/Passerini/Sebastiani, 2017, 720–728, DOI 10.24963/ijcai.2017/100. Replace unavailable author-copy URL with proceedings URL. |
| 25 | https://disi.unitn.it/rseba/papers/AIJ25.pdf | Author copy confirms Spallitta/Sebastiani/Biere, AI 345 (2025):104346, AllSAT/AllSMT and disjoint projected enumeration. Their optimized solver is not reproduced by our direct Z3 baseline. |
| 26 | https://link.springer.com/article/10.1007/s10817-023-09659-1 | Publisher title/author/2023 article 11 and rounding preimages in floating-point-factor reasoning. Context for established rounding reasoning, not a proof of our selector-specific mapping. |
| 27 | https://github.com/scipy/scipy/issues/6318 | Official nearest integer-axis overflow issue identity. Scope of replay stays restricted. |
| 28 | https://github.com/scipy/scipy/pull/6351 | Official fix identity; source/AST hashes and original regression-test replay supply the artifact evidence. |

Full metadata corrections are applied by build_v8_revision.py. Reference count stays 28; the supplied inherited manuscript is identified by title and hash-bound source mapping rather than by an invented publication entry. The exact-current-release verdict remains in a detached report and is not a bibliographic claim.
