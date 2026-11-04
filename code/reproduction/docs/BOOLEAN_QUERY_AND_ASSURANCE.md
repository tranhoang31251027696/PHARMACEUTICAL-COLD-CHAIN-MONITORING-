# Boolean query contract and evidence obligations

VerifiedBooleanIndex takes labels, old/new scores, unique aligned IDs and a core certificate. Construction copies the inputs and certificate, invokes the same independent streaming checker used by the full query route, then freezes an exact interval index and the verified input digest. Queries cannot alter the frozen dataclass fields. This prevents ordinary caller mutation of the original certificate from changing answers after verification; it is not a Python security sandbox or a formally verified kernel.

## Evidence obligations

| Route | Preparation included in the experiment | Complete certificate independently checked | Per-query answer |
|---|---|---|---|
| Full certificate API | Construction, JSON roundtrip, independent full check | Yes | Full finite-count/intersection API is called, then projected to Boolean and rational witness |
| Boolean certificate API | Construction, JSON roundtrip, same independent full check, frozen component index | Yes | Boolean and rational witness, no intersection list or affected count |
| Direct masks | Independent candidate masks and critical ratios once per batch | No complete certificate emitted or checked | Exact query evaluation with early exit on a difference, plus witness |
| Incremental Z3 | Independent masks and selected-bitset base constraints once per batch; push/pop per query | No complete certificate or solver proof object emitted/independently checked | SAT/UNSAT query verdict, rational SAT witness |

All four routes answer the same selected-ID existence question under their stated frozen-input contract. Absence of a persisted certificate does not by itself make an answer inexact. The obligations to produce a global diagnostic object, bind it to inputs, and independently check that object are different. All saved positive witnesses are rechecked outside the timers. That postcheck does not turn a direct negative result or a solver UNSAT result into a separately checked full-domain certificate.

The assurance-matched comparison is between the two certificate APIs. Construction and full independent checking are present in both; the Boolean API additionally includes freezing, component merging and index construction in setup. Their measured difference isolates query API costs under the same certificate obligations. Four-route comparisons are implementation request-cost studies with explicitly unequal evidence obligations, not a verification-guarantee speed ranking. V8 raw timings remain a separate protocol and are not pooled with the new measurements.

## Index reasoning

After full verification, the certificate's unequal cells exactly cover its divergent set, with correct endpoint ownership. Adjacent unequal cells are merged only if their shared boundary belongs to at least one of them. Their union then has no omitted boundary point. When both sides exclude the shared boundary, a matching singleton hole must remain and the components are kept separate. Isolated unequal singletons also remain representable. Exact Fractions are retained throughout.

The resulting maximal components have strictly increasing right endpoints. For an interval query, binary search finds the first component whose right endpoint is at least the requested lower bound. Earlier components cannot intersect. Endpoint predicates determine whether this component intersects; if only its boundary is excluded, the following candidate is checked. No complete intersection list is materialized. A closed lower bound supplies a witness; otherwise an exact interior midpoint does. These are elementary ordered-set operations, not a new region-enumeration or parameter-synthesis primitive.

A singleton query uses the same endpoint-aware search. A finite set is validated/deduplicated and queried point by point. A decimal lattice uses exact integer bounds on candidate intersections and returns the first lattice member when one exists. Lattice emptiness is validated even when the divergent set is empty. JSON floating-point numbers, undeclared/non-rational semantics, out-of-domain inputs and empty requested domains are refused as in the earlier interface. The CLI is:

```powershell
python verified_boolean_query.py --certificate results/v6/scipy_defect_certificates/upstream_int8_affected.json --query docs/policy_query_example.json
```

## Costs and verification scope

Index construction retains O(C) component descriptors after O(C) merging, in addition to the existing full certificate verification cost. An interval/singleton query uses O(log C) rational comparisons plus constant candidate/endpoint work for maximal disjoint components. A set of M policies also incurs validation/deduplication costs and up to M such searches. A lattice may scan O(C) components if none contains an allowed lattice point; its worst-case bound is not logarithmic. Arbitrary-precision operand size matters in all these counts. The Boolean answer intentionally omits exact affected counts and complete intersection output.

Four targeted tests cover a divergent zero-measure singleton, an equal singleton hole between unequal open regions, input tamper/refusal, immutable reuse and invalid/empty policy domains. The new study reuses the existing six cases and 2,028 plans, rather than claiming a larger empirical corpus. validate_v9.py also replays all 288 earlier finite/lattice/interval scenarios and validates the saved rational witnesses. These checks establish implementation consistency on the stated finite evidence; they do not supply independent developer, production-policy or industrial defect-rate evidence.
