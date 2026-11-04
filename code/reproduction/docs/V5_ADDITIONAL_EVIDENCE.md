### RQ6 Streaming certificate consumption

The legacy verifier first materializes all Boolean threshold masks. Its independently measured cost motivated a second consumer, not a change to the producer or finite partition theorem. The new implementation imports neither production code nor the legacy checker. It counts one threshold mask at a time, retaining only exact ratios, actual TP/N and candidate descriptors. A reverse suffix-maximum table over ascending feasibility ratios supplies exhaustive-priority winners by exact bisection. It reconstructs and packs only the current winning mask for each version. It uses no production priority heap or rank-containment comparator and retains no all-candidate bitset cache.

The suffix winner argument is direct: feasible candidates form a suffix (lower bound for inclusive feasibility, upper bound for strict feasibility), and reverse induction computes that suffix's maximum fixed priority. Independent critical-point construction, ordered certificate coverage and endpoint ownership then justify checking all atom representatives. A forward cell cursor validates each probe; actual bitsets validate equality, witness IDs/memberships and changed-row counts. Exact divergent length and PSC are independently recomputed. Detailed lemmas and conditional soundness are in STREAMING_CHECKER_AND_FLOAT_CUT_PROOFS.md. These are mathematical arguments plus tests, not a machine-checked proof or independent human replication.

The consumer uses O(N+G+K+C) auxiliary descriptors/probes and current-mask storage, excluding arbitrary-precision operand sizes, for K critical values and C certificate cells. Direct counting and winner reconstruction retain worst-case O(NG) work; split-tie ordering adds O(N log N), with ratio/query/probe sorting costs stated in the proof supplement. In particular, G=N can still be quadratic. Suffix maxima, bisection and streaming are established techniques [17], not new general primitives.

All 428 frozen application/mutation certificates are accepted under the same obligations as the legacy checker, covering 41,348 probes. New exhaustive small-input comparisons exercise seven specifications; tamper tests reject altered bindings, partitions, winners and metrics, and retain point-only non-equivalence. Thirty core tests pass; the upstream project's eighteen tests are counted separately.

The paired experiment regenerates the same six N/G fixtures as the earlier checker study, prepares an identical certificate/payload outside timing, warms up both consumers, and randomizes their order within each of five repetitions. JSON parsing is recorded separately. A sixth invocation per consumer/group traces memory independently. The sixty untraced timing records and twelve separate memory records are never pooled. Each row below compares identical inputs, policies, coverage, hash and witness obligations; these are not ratios against the differently instrumented producer benchmark.

| N / fixture | Legacy median (IQR), ms | Streaming median (IQR), ms | Legacy peak MiB | Streaming peak MiB |
|---|---|---|---|---|
| 1,000 / invariant | 6.41 (0.67) | 2.56 (0.15) | 0.04 | 0.04 |
| 1,000 / divergent | 26.98 (1.38) | 6.24 (0.46) | 0.09 | 0.04 |
| 10,000 / invariant | 130.23 (12.14) | 27.72 (6.19) | 1.33 | 0.63 |
| 10,000 / divergent | 1859.66 (59.43) | 145.62 (22.20) | 3.56 | 0.63 |
| 100,000 / invariant | 7097.14 (759.47) | 1843.19 (48.92) | 61.42 | 6.00 |
| 100,000 / divergent | 35034.92 (360.42) | 3557.72 (139.89) | 169.85 | 6.00 |

Memory peaks are auxiliary allocations with inputs/certificate prepared in advance and one traced run per group. Five timings on one host do not establish a universal CI budget. The implementation preserves a deliberately different verification route while reducing retained masks; shared dependencies and mathematical assumptions remain trusted. Results show an implementation tradeoff under this contract, not a general theorem that checking is always cheaper than production.

### RQ5 Diagnostic-complete comparison across workload structure

Both implementations must return the same maximal divergent components, exact endpoint ownership, exact PSC, separate Boolean equivalence and one representative policy/row witness per component. A representative witness is existential at its reported policy, not one observation changing throughout a component. SMT repeatedly finds a QF_LRA model, expands it to its complete feasibility-predicate cell, blocks that cell, and finishes only at residual UNSAT. Unknown/timeout prevents certification. General predicate enumeration is established [23-25]; complete diagnostics are not a unique capability of our partition method.

The eight V4 external affected/fixed tasks remain a separate check and still agree. We add a prespecified factorial design: N in {1,000,10,000,100,000}, G in {10,30,90}, and no, one-middle, or alternating candidate omission. Scores form G tied groups with gradually decreasing group-positive proportions; fixed-seed permutations remove dependence on row order. These designed families yield 0–39 divergent components. They are controlled tasks, not new upstream defects or independent deployments. Every one of the 27 tasks is retained, including empty-divergence controls.

Five repetitions per method/task, with randomized method order inside each repetition, produce 270 timing records and 54 saved certificates. Both methods receive the same candidate family, regenerate counts/masks during each timed preparation, emit the same diagnostic JSON and invoke the same independent region checker. All complete outputs agree and every saved certificate is replayed. Preparation, producer plus serialization, checker, total checked cost, candidate counts, exact critical-point count, divergent components, probes, bytes and solver calls are retained separately. Thus input-size effects are not inferred from a preparation-excluded timer alone.

The table shows N=100,000; the raw factorial records preserve the other scales. Total includes fresh preparation, complete diagnostic production/JSON and independent checking. Entries are within-task medians of five runs, not pooled medians across heterogeneous tasks.

| G / omission | Critical points | Components | Partition total ms | SMT total ms |
|---|---|---|---|---|
| 10 / alternating | 10 | 5 | 59.26 | 78.39 |
| 10 / none | 10 | 0 | 52.90 | 65.71 |
| 10 / one | 10 | 1 | 58.68 | 64.17 |
| 30 / alternating | 27 | 13 | 111.01 | 193.82 |
| 30 / none | 27 | 0 | 100.06 | 109.05 |
| 30 / one | 27 | 1 | 103.76 | 129.67 |
| 90 / alternating | 79 | 39 | 494.01 | 1058.73 |
| 90 / none | 79 | 0 | 323.85 | 317.51 |
| 90 / one | 79 | 1 | 329.47 | 391.97 |

Across all 27 designed tasks, partition has the smaller total median on 25; the other 2 have an equal or smaller SMT median. These descriptive comparisons do not establish statistical significance, superiority for arbitrary selectors or parity with an optimized general AllSMT solver. This is our direct Z3 encoding and generic external-table partition adapter, not a reproduction of TabularAllSMT or a benchmark of the compact rank-based producer. The region checker still enumerates prepared memberships and is distinct from the new streaming consumer for the core certificate format. Evidence supports scoped cost characterization and common diagnostic correctness; broader performance claims remain unsupported.

### RQ7 An executed second project and its actual policy semantics

We build a wheel from the complete, unmodified eval-toolkit 1.12.0 source at commit `a6400e74c4534d6d79f17dee11ad903b6d664980`, retaining hashes, its MIT license and package metadata. Python 3.13.18 satisfies its >=3.13 requirement. The installed TargetPrecisionSelector is called through its actual public API; no method body is extracted, patched or replaced with a custom scorer. All eighteen packaged upstream threshold tests pass. The package and source are distributed for offline installation. The two externally authored projects executed across the studies are now scikit-learn and eval-toolkit, although the latter depends on scikit-learn's precision-recall routine; this is not independent numerical infrastructure or independent institutional deployment.

The workload rule is fixed: first 64 rows of all thirty existing pipeline inputs, with no positive-case filtering. The wrapper passes float(alpha) to the public precision parameter and maps only the documented no-feasible RuntimeError to abstention. Its exact-reference objective is still maximum (TP,N); in the same nested family, this equals the project's smallest-feasible-threshold objective. Input validation, source identity and candidate counts are checked. Actual floating precision values are compared against direct integer membership counts.

It would be unsound to assume a binary64 guard changes exactly at the rational ratio k/n. For an actual binary64 precision p, let q=nextafter(p,+infinity) and c=(exact(p)+exact(q))/2. The public predicate p >= float(alpha) changes at c, including equality exactly when p has the even significand. The proof follows monotone nearest/even rounding and is a selector-specific application of established rounding-preimage reasoning [26]. We explicitly check midpoint ownership and both neighboring cells on the runtime. The complete critical set is the union of rational-reference cuts, these rounding-cell cuts and domain endpoints. A model of these guards is checked against every actual public-API output, including all endpoints; unsupported numerical behavior must prevent certification.

Across thirty workloads, 884 critical-point/midpoint policies and 1500 public invocations (including the grid/snapshot baselines) are executed. The guard model matches every actual output. Twenty-seven workloads have narrow differences from the exact rational reference; neither snapshot nor the thirteen-point grid detects any of them. These are twenty-seven semantic differentials, not twenty-seven bugs or regressions between upstream releases. The library documents a floating policy interface, so the rational reference is a caller-selected stronger/different contract, not an upstream requirement it is shown to violate. The upstream-confirmed defect count remains one; on that documented scikit-learn defect, incremental detection over grid remains zero.

Each input-bound certificate preserves exact rounding-cut fractions, ownership, actual/reference bitsets, row witnesses, complete divergent regions and PSC. The validator calls the installed selector again at all 884 policies and checks every stored field. We additionally probe actual representable binary64 precision policies: 196 such probes expose differences on 19 workloads. Grid/snapshot targets are exact rational fractions, whereas this additional group embeds each binary64 value by its exact integer ratio; it does not reinterpret a decimal grid target as its binary approximation. Thus the continuous-domain finding is not automatically equated to a difference at a policy the float API can represent. With labels [1,1,0,0,0] ordered by decreasing distinct score, the representable float 0.4 exceeds exact 2/5: at the exact rational embedding of that float, the float selector admits all five while the rational reference admits four. At exact decimal 2/5 both admit five. This is a designed explanation of distinct policy contracts, not a newly documented upstream bug. Tiny interval length is not a deployment probability or impact estimate. Adoption should decide whether binary64 semantics are acceptable, rather than treating every differential as a release-blocking defect.

### Closest algorithmic overlap and remaining contribution

The closest overlap is concrete. Morettin et al. [24] use SMT predicate abstraction to enumerate models for weighted integration; our uniform one-dimensional PSC is not a new general integration principle. Spallitta et al. [25] develop disjoint projected enumeration with more sophisticated solver techniques than our blocking-cell baseline. We therefore do not interpret a win over our encoding as a win over state-of-the-art AllSMT. Andrlon's rounding-preimage analysis [26] establishes a wider arithmetic foundation than the single guard mapping used here. Certifying-computation frameworks [9,17] already motivate a simple independent consumer. Suffix maxima and one-mask-at-a-time processing are implementation choices within that tradition. These sources narrow the proposed contribution to the fully specified precision-selector contract, exact boundary-aware diagnostic artifacts, an independently implemented consumer with measured tradeoffs, and checked integration on two external projects. They do not establish first-in-literature novelty of partitioning, rounding preimages, enumeration or streaming.


[24] Morettin, P.; Passerini, A.; Sebastiani, R. (2017). Efficient Weighted Model Integration via SMT-Based Predicate Abstraction. IJCAI. Author manuscript: https://sml.disi.unitn.it/papers/ijcai17.pdf

[25] Spallitta, G.; Sebastiani, R.; Biere, A. (2025). Disjoint projected enumeration for SAT and SMT without blocking clauses. Artificial Intelligence, 345, 104346. https://doi.org/10.1016/j.artint.2025.104346

[26] Andrlon, M. (2023). Finding Normal Binary Floating-Point Factors Efficiently. Journal of Automated Reasoning, 67, article 11. https://doi.org/10.1007/s10817-023-09659-1
