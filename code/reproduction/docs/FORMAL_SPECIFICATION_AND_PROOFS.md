# Exact policy equivalence: specification, statements, proofs

## Contract

Let observations have fixed, aligned, unique IDs and binary labels y in {0,1}^N, N>0. Each version has a finite, real-valued score vector. Threshold candidates are the nonempty sets C(t)={i:s_i >= t} at observed score levels; all equal scores are taken together. Candidate j has n_j=|C_j|>0, k_j=sum(y_i:i in C_j), and exact empirical precision p_j=k_j/n_j.

For a rational policy alpha in a closed domain A=[L,H], 0<=L<H<=1, candidate j is feasible iff k_j >= alpha*n_j, including equality. With at least one positive label, choose the feasible candidate maximizing the lexicographic pair (k_j,n_j); abstain (empty selected set) if no candidate is feasible. If no label is positive, always abstain, matching the inherited implementation's explicit convention. This extension also defines alpha=0, though the inherited interface only accepted alpha>0. There is no division by zero for abstention.

The theorem requires an alpha-independent total priority on candidates. It is not a statement about arbitrary selectors, alpha-dependent objectives, unseen future observations, uncertain labels, retraining, or population precision. Our six selector mutants are explicit alternative finite contracts, not automatic inference of arbitrary changed program semantics. Floating scores define exact order/ties as loaded. Rational precision avoids feasibility rounding; it does not claim exact arithmetic for model training or score generation. Decimal policy strings are interpreted as their exact decimal fractions, not the binary expansion of floats.

## Theorem 1: finite policy partition

Let B={L,H} union {p_j from either version: L<p_j<H}. Partition A into every singleton {b}, b in B, and every open interval (b_i,b_{i+1}) between consecutive values. Both selected memberships are constant on each atom. The versions are equivalent on all of A if and only if their selected memberships agree on every singleton and at one point in every nonempty open interval.

Proof. For any candidate j, feasibility is the truth value of alpha<=p_j. On an open interval containing no critical value p_j, that truth value cannot change: if it changed, p_j would lie between the two policies, contradicting the construction. All candidate feasibility vectors are therefore constant there. Candidate priority and the abstention convention are fixed, so the winning candidate, hence membership, is constant. Evaluate each singleton explicitly because alpha=p_j is included. The disjoint atoms cover A, giving both implications. The same argument applies to the strict mutant alpha<p_j, but singleton ownership changes. QED.

Using a midpoint is sound only after completeness of B has been established. A grid that does not contain every critical value has no such guarantee. A verifier must independently derive B, rather than trust the producer's breakpoints.

## Lemma 2: priority and membership

For the reference nested prefix family, k_j is nondecreasing in n_j because labels are nonnegative. Thus the largest feasible prefix maximizes (k_j,n_j). The implementation nevertheless uses an explicit priority heap so that the reverse-secondary-order mutant is handled without assuming this lemma.

For old selected prefix size n and new selected prefix size m, the selected sets are equal iff n=m and max(rank_new(i):i in old prefix n)<n (or both sizes are zero). Proof: with equal finite cardinality n, containment of all old IDs in the new prefix implies equality, and equality implies containment. Inverse ranks and prefix maxima give a constant-time equality query after linear preprocessing. For unequal sets, an ID whose prefix-membership booleans differ is a directly checkable witness. QED.

## Algorithm and complexity

1. Sort each score vector stably, identify complete score groups and accumulate integer TP/N counts. Reduce precision fractions with arbitrary-precision integers.
2. Form and sort the union B, adding both domain endpoints. Evaluate the atoms from left to right: singleton, following open midpoint, next singleton, and so on.
3. A max-priority heap contains all candidates. As alpha increases, pop an infeasible top candidate until its top is feasible or the heap is empty. Feasibility never returns, so no popped candidate is needed again. Each candidate is inserted once and popped at most once. No monotonicity assumption on the empirical precision sequence is made.
4. Compare winning membership using Lemma 2. Cache each distinct winning-prefix pair. Optionally scan N aligned ranks to count differences and select one changed observation as witness for each distinct divergent pair.
5. Merge adjacent atoms only when both selected prefix sizes, equality and witness agree, preserving left/right closed flags. Export the input digest, domain, selector contracts, complete critical values, state intervals, witnesses and exact PSC.

Let G=G_old+G_new, K<=G+2 distinct breakpoints, and D the number of distinct divergent winning pairs. Under unit-cost rational comparisons, core work is O(N log N + G log G + K) and auxiliary memory O(N+G+K). Witness construction adds O(N*D) time, with constant-size witness/count data per state, rather than materializing every selected ID set. Serialization and input hashing are included in measured end-to-end certificate costs. Integer fraction comparison has bit complexity depending on the numerator/denominator lengths; the unit-cost bound is not a claim that arbitrarily large integers are constant-time.

The independent verifier enumerates masks at every observed threshold, constructs exact integer bitsets, derives its own precision values, and checks every critical point and open-interval midpoint. Its cost is deliberately higher: O(N*G+K*G) arithmetic/bitset-related work and O(N*G) bits for packed membership masks, with O(N*G) bytes of Boolean scratch before bitset packing in the current implementation. It uses neither the production priority heap nor its rank-containment comparator. It is independent implementation evidence, not a formal proof assistant or independent human replication.

## Corollary 3: PSC and endpoint-only divergence

Let D_A={alpha in A:S_old(alpha)!=S_new(alpha)}. Its Lebesgue measure is the exact sum of lengths of divergent open atoms. Define PSC=length(D_A)/(H-L). Isolated points contribute zero length. Therefore full equivalence implies PSC=0, but PSC=0 does not imply full equivalence. A certificate must retain its Boolean equivalence and closed-point evidence.

Counterexample: labels [1,0], scores [1,0], A=[1/2,1]. Compare inclusive precision feasibility to a strict-feasibility mutant. At alpha=1/2 the inclusive version selects both rows while the strict version selects only the positive row; at alpha=1 the inclusive version selects that row while the strict version abstains. They agree on (1/2,1), so PSC=0 despite two divergent endpoints. The automated test verifies this example.

PSC is a uniform-domain length fraction. It is not a probability of a production defect, deployment risk, expected clinical harm, or calibration quality. Related inherited cases are not independent samples. A structural frontier difference may be entirely policy-equivalent on the allowed domain and is not by itself a defect.

## Certificate trust boundary

The input SHA-256 binds arrays, row ordering and IDs for accidental-integrity verification. It is not a signature or proof of dataset authenticity. A verifier needs the original arrays and an agreed selector specification; verification of a certificate with a declared mutant specification does not establish conformance of an arbitrary executable to that specification. Invalid or misaligned IDs are contract violations, separately reported from policy divergence. The reference cannot infer hidden row misalignment if a caller supplies misleading IDs. Verification refuses Python optimized mode because this research verifier uses assertions.

## Novelty boundary

Finite critical-point partitioning and constrained threshold selection are established ideas. This document proves the specialized contract and supports an integrated implementation/certificate/evaluation contribution; it does not establish first-in-literature novelty. Prior-art scope and limitations are recorded separately. Journal quartile or acceptance is not inferred from passing these experiments.

