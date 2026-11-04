import time
import numpy as np
import hashlib
import gc
import sys
import tracemalloc
from pathlib import Path

# Force UTF-8 on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Strict authoritative import of decision_regression.py (contract enforcement: zero fallback)
EXPECTED_DECISION_REGRESSION_SHA256 = 'd8156b3c9508d54f960dbb40beefe7390ec06fc7933fd08b616e3558b9d907dd'

candidate_dirs = [
    Path(__file__).parent,
    Path(__file__).parent / '02_Replication_Package' / 'src' / 'research_round13',
    Path(__file__).parent / 'src' / 'research_round13',
    Path('SUBMISSION_PACKAGE').resolve(),
    Path('SUBMISSION_PACKAGE/02_Replication_Package/src/research_round13').resolve(),
    Path('02_Replication_Package/src/research_round13').resolve(),
]
imported = False
for p in candidate_dirs:
    dr_file = p / 'decision_regression.py'
    if dr_file.is_file():
        h = hashlib.sha256(dr_file.read_bytes()).hexdigest()
        if h == EXPECTED_DECISION_REGRESSION_SHA256:
            sys.path.insert(0, str(p.resolve()))
            from decision_regression import frontier, _same_frontier, compare
            imported = True
            break
        else:
            raise RuntimeError(f"Corrupted decision_regression.py at {dr_file}: SHA-256 {h} does not match authoritative checksum {EXPECTED_DECISION_REGRESSION_SHA256}")

if not imported:
    raise ImportError("Cannot find authoritative decision_regression.py (SHA-256: d8156b3c9508d54f960dbb40beefe7390ec06fc7933fd08b616e3558b9d907dd). Fallback execution is disallowed to ensure 100% observation contract fidelity.")

# -----------------------------------------------------------------------------
# Baseline B4: Optimized Generic Inverted-Index / Partition Exact Comparator
# -----------------------------------------------------------------------------
def b4_exact_comparator_workflow(old, new):
    """
    Evaluates exact candidate frontier equivalence by extracting the true
    ranked partitions of observation IDs from both score vectors, without
    relying on arbitrary fixed threshold grids.
    Semantically exact: two continuous score vectors have identical candidate
    frontiers if and only if their ordered distinct score tiers partition the
    exact same subsets of observation IDs.
    """
    old = np.asarray(old, dtype=float)
    new = np.asarray(new, dtype=float)
    if len(old) != len(new):
        return False
    N = len(old)
    order_o = np.argsort(-old, kind='stable')
    order_n = np.argsort(-new, kind='stable')
    ends_o = np.r_[np.flatnonzero(old[order_o][:-1] != old[order_o][1:]) + 1, N]
    ends_n = np.r_[np.flatnonzero(new[order_n][:-1] != new[order_n][1:]) + 1, N]
    if len(ends_o) != len(ends_n) or not np.array_equal(ends_o, ends_n):
        return False
    prev = 0
    for end in ends_o:
        if not np.array_equal(np.sort(order_o[prev:end]), np.sort(order_n[prev:end])):
            return False
        prev = end
    return True

def verify_construct_validity():
    print("=" * 105)
    print("1. CONSTRUCT VALIDITY AUDIT & ORACLE SUITE: FIXED GRID VS. EXACT COMPARATORS")
    print("=" * 105)
    # Part A1: Discretized Fixed Grid vs. Intermediate Candidate Split
    old_fx = np.array([0.2, 0.4, 0.6, 0.6, 0.8, 1.0])
    new_fx = np.array([0.2, 0.4, 0.6, 0.6000001, 0.8, 1.0])
    y_fx = np.array([0, 1, 0, 1, 1, 1], dtype=np.int8)

    fixed_grid = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    union_grid = np.unique(np.concatenate([old_fx, new_fx]))

    fixed_diff = any(not np.array_equal(old_fx >= th, new_fx >= th) for th in fixed_grid)
    union_diff = any(not np.array_equal(old_fx >= th, new_fx >= th) for th in union_grid)

    fa_fx = frontier(y_fx, old_fx, 0.5)
    fb_fx = frontier(y_fx, new_fx, 0.5)
    prop_diff = not _same_frontier(fa_fx, fb_fx)
    b4_diff = not b4_exact_comparator_workflow(old_fx, new_fx)

    print(f"Fixed Grid Detection (G={len(fixed_grid)}) : Diff Detected = {fixed_diff} (BLIND SPOT: misses intermediate candidate set)")
    print(f"Union Cutoff Mapping Diff (G={len(union_grid)})  : Diff Detected = {union_diff} (Detects threshold-to-membership shift)")
    print(f"Baseline B4 (Inverted Partition)   : Diff Detected = {b4_diff} (EXACT: observation-partition altered)")
    print(f"Proposed Compact Scan              : Diff Detected = {prop_diff} (EXACT: candidate-frontier boundary altered)")
    assert not fixed_diff and union_diff and prop_diff and b4_diff

    # Part A2: ULP Tie-Split Detection on Production Benchmark Scale (N=2,000, G=1,000)
    # Demonstrating that fixed-grid baselines (linspace) suffer blind spots under 1-ULP tie splits
    G_bench = 1000
    th_bench = np.linspace(0.0, 1.0, G_bench)
    groups = np.repeat(np.arange(G_bench), 2)
    old_ulp = groups.astype(float) / (G_bench - 1)
    new_ulp = old_ulp.copy()
    target_idx = 1001  # second observation of group 500
    new_ulp[target_idx] = np.nextafter(new_ulp[target_idx], 1.0)
    y_ulp = np.ones(len(old_ulp), dtype=np.int8)

    fixed_diff_ulp = any(not np.array_equal(old_ulp >= th, new_ulp >= th) for th in th_bench)
    b4_diff_ulp = not b4_exact_comparator_workflow(old_ulp, new_ulp)
    prop_diff_ulp = not _same_frontier(frontier(y_ulp, old_ulp, 0.5), frontier(y_ulp, new_ulp, 0.5))

    print(f"\n[PART A2: ULP TIE-SPLIT DETECTION ON PRODUCTION BENCHMARK SCALE (N=2,000, G=1,000)]")
    print(f"Fixed Grid Detection (G=1000 linspace) : Diff Detected = {fixed_diff_ulp} (BLIND SPOT: misses single-ULP tie split)")
    print(f"Baseline B4 (Inverted Partition)       : Diff Detected = {b4_diff_ulp} (EXACT: detects split observation tier)")
    print(f"Proposed Compact Scan                  : Diff Detected = {prop_diff_ulp} (EXACT: detects altered candidate frontier)")
    assert not fixed_diff_ulp and b4_diff_ulp and prop_diff_ulp

    # Part A3: Numeric-Cutoff Mapping Invariance vs. Candidate-Frontier Equivalence on Monotone Shift
    # Clarifying that union cutoffs test threshold mapping invariance, whereas B4 & Proposed test candidate set equivalence
    s_mono_o = np.array([0.2, 0.5, 0.8])
    s_mono_n = np.array([0.3, 0.6, 0.9])
    union_cutoffs = np.unique(np.concatenate([s_mono_o, s_mono_n]))
    union_mapping_diff = any(not np.array_equal(s_mono_o >= th, s_mono_n >= th) for th in union_cutoffs)
    b4_mono_equiv = b4_exact_comparator_workflow(s_mono_o, s_mono_n)
    prop_mono_equiv = bool(_same_frontier(frontier(np.ones(3, dtype=np.int8), s_mono_o, 0.5),
                                          frontier(np.ones(3, dtype=np.int8), s_mono_n, 0.5)))

    print(f"\n[PART A3: NUMERIC-CUTOFF MAPPING VS. CANDIDATE-FRONTIER EQUIVALENCE ON MONOTONE SHIFT]")
    print(f"Union Cutoff Evaluation (G={len(union_cutoffs)}) : Diff Detected = {union_mapping_diff} (CONTRACT A: Threshold-to-membership mapping)")
    print(f"Baseline B4 (Inverted Partition)       : Equivalence  = {b4_mono_equiv} (CONTRACT B: Candidate-frontier collection)")
    print(f"Proposed Compact Scan                  : Equivalence  = {prop_mono_equiv} (CONTRACT B: Candidate-frontier collection)")
    assert union_mapping_diff and b4_mono_equiv and prop_mono_equiv

    # Part B: Comprehensive Oracle Suite (Testing 100% Semantic Equivalence)
    oracle_cases = [
        ("Monotone Shift (Reviewer Case: [0.2,0.5,0.8] vs [0.3,0.6,0.9])", np.array([0.2, 0.5, 0.8]), np.array([0.3, 0.6, 0.9]), True),
        ("Nonlinear Monotone Scaling (s_new = exp(s_old) * 2.5)", np.array([0.1, 0.4, 0.4, 0.7, 0.9]), np.exp(np.array([0.1, 0.4, 0.4, 0.7, 0.9])) * 2.5, True),
        ("Tie Splitting (intermediate candidate created)", np.array([0.1, 0.4, 0.4, 0.7, 0.9]), np.array([0.1, 0.4, 0.41, 0.7, 0.9]), False),
        ("Tie Merging (adjacent candidate collapsed)", np.array([0.1, 0.4, 0.45, 0.7, 0.9]), np.array([0.1, 0.4, 0.4, 0.7, 0.9]), False),
        ("Rank Crossing (observation order inverted)", np.array([0.1, 0.4, 0.6, 0.8]), np.array([0.1, 0.6, 0.4, 0.8]), False),
        ("Intermediate Threshold Split outside fixed grid", np.array([0.2, 0.4, 0.6, 0.6, 0.8, 1.0]), np.array([0.2, 0.4, 0.6, 0.6000001, 0.8, 1.0]), False)
    ]
    print("\n[ORACLE SUITE: SEMANTIC EQUIVALENCE OF B4 AND PROPOSED]")
    for desc, so, sn, expected in oracle_cases:
        y_dummy = np.ones(len(so), dtype=np.int8)
        p_res = bool(_same_frontier(frontier(y_dummy, so, 0.5), frontier(y_dummy, sn, 0.5)))
        b_res = bool(b4_exact_comparator_workflow(so, sn))
        agree = (p_res == b_res == expected)
        print(f" - {desc:<62} | Expected: {str(expected):<5} | B4: {str(b_res):<5} | Prop: {str(p_res):<5} | Agree: {agree}")
        assert agree, f"Mismatch in {desc}"
    print(">> Oracle verification passed: Baseline B4 and Proposed achieve 100% exact semantic agreement.")

    # Part C: Randomized Differential Testing against Independent Exhaustive Set-Union Oracle (100 trials)
    print("\n[PART C: RANDOMIZED DIFFERENTIAL TESTING (100 TRIALS VS EXHAUSTIVE ORACLE)]")
    diff_rng = np.random.default_rng(2026)
    oracle_matches = 0
    num_diff_trials = 100
    for trial in range(num_diff_trials):
        n_trial = int(diff_rng.integers(12, 40))
        # Base scores with realistic tie clusters
        base_scores = diff_rng.choice(np.linspace(0.1, 0.9, 6), size=n_trial)
        trial_type = trial % 4
        if trial_type == 0:
            # Monotone affine scaling -> candidate sets must be identical
            scale = float(diff_rng.uniform(1.2, 3.5))
            shift = float(diff_rng.uniform(0.1, 1.0))
            mutated = base_scores * scale + shift
        elif trial_type == 1:
            # Nonlinear strictly monotonic scaling -> candidate sets must be identical
            mutated = np.exp(base_scores * 1.5)
        elif trial_type == 2:
            # Perturb single tied observation -> splits tie bucket, altering candidate frontier
            mutated = base_scores.copy()
            idx_pert = int(diff_rng.integers(0, n_trial))
            mutated[idx_pert] += 0.05
        else:
            # Observation rank swap
            mutated = base_scores.copy()
            idx1, idx2 = diff_rng.choice(n_trial, size=2, replace=False)
            if mutated[idx1] != mutated[idx2]:
                mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
            else:
                mutated[idx1] += 0.05

        # Independent Exhaustive Candidate Frontier Oracle (Definition 1 Ground Truth)
        sets_old = [frozenset(np.where(base_scores >= th)[0]) for th in np.sort(np.unique(base_scores))[::-1]]
        sets_new = [frozenset(np.where(mutated >= th)[0]) for th in np.sort(np.unique(mutated))[::-1]]
        oracle_eq = (sets_old == sets_new)

        y_dum = np.ones(n_trial, dtype=np.int8)
        p_eq = bool(_same_frontier(frontier(y_dum, base_scores, 0.5), frontier(y_dum, mutated, 0.5)))
        b4_eq = bool(b4_exact_comparator_workflow(base_scores, mutated))

        assert oracle_eq == p_eq == b4_eq, f"Differential mismatch at trial {trial}: Oracle={oracle_eq}, Prop={p_eq}, B4={b4_eq}"
        oracle_matches += 1

    print(f">> Randomized Differential Testing: {oracle_matches}/{num_diff_trials} trials matched 100% identically across Exhaustive Oracle, B4, and Proposed.\n")


    # Part D: Observation Contract & Attribution Assertion Regression Tests
    print("[PART D: OBSERVATION CONTRACT & ATTRIBUTION INTEGRITY REGRESSION TESTS]")
    
    # 1. Permuted / unaligned row IDs must raise ValueError
    try:
        compare([1, 0, 1], [0.7, 0.5, 0.2], [0.7, 0.5, 0.2], old_ids=[1, 2, 3], new_ids=[2, 1, 3])
        raise AssertionError("Failed: Permuted row IDs were accepted!")
    except ValueError as e:
        print(f" - Permuted row IDs rejection      : PASS (caught: '{e}')")

    # 2. Duplicate row IDs must raise ValueError
    try:
        compare([1, 0, 1], [0.7, 0.5, 0.2], [0.7, 0.5, 0.2], old_ids=[1, 1, 3], new_ids=[1, 1, 3])
        raise AssertionError("Failed: Duplicate row IDs were accepted!")
    except ValueError as e:
        print(f" - Duplicate row IDs rejection     : PASS (caught: '{e}')")

    # 3. Missing one ID vector must raise ValueError
    try:
        compare([1, 0, 1], [0.7, 0.5, 0.2], [0.7, 0.5, 0.2], old_ids=[1, 2, 3], new_ids=None)
        raise AssertionError("Failed: Missing new_ids was accepted!")
    except ValueError as e:
        print(f" - Asymmetric row IDs rejection    : PASS (caught: '{e}')")

    # 4. Aligned unique row IDs must be accepted
    rep_ok = compare([1, 0, 1], [0.7, 0.5, 0.2], [0.7, 0.5, 0.2], old_ids=[1, 2, 3], new_ids=[1, 2, 3])
    assert rep_ok['regression_flag'] is False
    print(" - Aligned unique row IDs          : PASS (contract verified, regression_flag = False)")

    # 5. Witness consistency under isolated refinement: compare() enforces bool(witness) == bool(changed)
    rep_iso = compare([1, 1, 0], [0.5, 0.5, 0.2], [0.6, 0.5, 0.2], alpha=0.5)
    assert rep_iso['isolated_refinement_assumptions'] is True
    print(f" - Isolated refinement contract    : PASS (isolated={rep_iso['isolated_refinement_assumptions']}, witness={rep_iso['proper_prefix_witness']})")
    print(">> Observation contract verified: Authoritative decision_regression.py enforces 100% sample identity invariants.\n")
def benchmark_divergence_modes(N=100000, G=1000):
    print("=" * 105)
    print("2. MULTI-MODE DIVERGENCE BENCHMARK (Worst-Case Invariant vs. Early vs. Late Divergence)")
    print("=" * 105)
    rng = np.random.default_rng(42)
    group = np.arange(N) % G
    rng.shuffle(group)
    old = group.astype(float) / (G - 1)
    thresholds = np.linspace(0.0, 1.0, G)
    y = (rng.random(N) < 0.25).astype(np.int8)

    new_eq = old.copy()
    new_early = old.copy()
    early_step = max(1, int(0.005 * G))
    idx_early = np.where(group == early_step)[0][0]
    new_early[idx_early] = 0.0

    new_late = old.copy()
    late_step = min(G - 1, int(0.995 * G))
    idx_late = np.where(group == late_step)[0][0]
    new_late[idx_late] = 1.0

    modes = [
        ("Equal Frontier (Exhaustive Invariant Scan)", new_eq),
        (f"Early Divergence (Mismatch at Step g={early_step})", new_early),
        (f"Late Divergence (Mismatch at Step g={late_step})", new_late)
    ]

    for mode_name, new_vec in modes:
        # B1: Dense Matrix
        t0 = time.perf_counter()
        mat_o = np.empty((G, N), dtype=bool); mat_n = np.empty((G, N), dtype=bool)
        for g, th in enumerate(thresholds):
            mat_o[g] = (old >= th); mat_n[g] = (new_vec >= th)
        m_b1 = np.array_equal(mat_o, mat_n)
        t1 = time.perf_counter()
        ms_b1 = (t1 - t0) * 1000.0

        # B2: Streaming Sparse
        t0 = time.perf_counter()
        m_b2 = True
        for th in thresholds:
            if not np.array_equal(old >= th, new_vec >= th):
                m_b2 = False
                break
        t1 = time.perf_counter()
        ms_b2 = (t1 - t0) * 1000.0

        # Proposed: Workflow
        t0 = time.perf_counter()
        fa = frontier(y, old, 0.5)
        fb = frontier(y, new_vec, 0.5)
        m_prop = _same_frontier(fa, fb)
        t1 = time.perf_counter()
        ms_prop = (t1 - t0) * 1000.0

        # Proposed: Isolated Comparator
        t0 = time.perf_counter()
        m_prop_iso = _same_frontier(fa, fb)
        t1 = time.perf_counter()
        ms_prop_iso = (t1 - t0) * 1000.0

        print(f"{mode_name:<44} | B1: {ms_b1:6.2f} ms | B2: {ms_b2:6.2f} ms | Proposed Wf: {ms_prop:5.2f} ms (Iso: {ms_prop_iso:4.2f} ms)")
    print()

def benchmark_all_baselines(N=100000, G=1000, n_reps=5, b3_reps=None):
    rng = np.random.default_rng(13023 + N + G)
    group = np.arange(N) % G
    rng.shuffle(group)
    old = group.astype(float) / (G - 1)
    new = old.copy()
    y = (rng.random(N) < 0.25).astype(np.int8)
    thresholds = np.linspace(0.0, 1.0, G)

    actual_b3_reps = b3_reps if b3_reps is not None else n_reps

    print("=" * 105)
    print(f"3. CANONICAL EXHAUSTIVE BENCHMARK (N = {N:,}, G = {G:,}, Reps = {n_reps}, Mode = Invariant Worst-Case)")
    if actual_b3_reps != n_reps:
        print(f"   [NOTE] Baseline B3 configured with {actual_b3_reps} repetitions; all other baselines use {n_reps} reps.")
    print("=" * 105)

    # 1. Baseline A: Selected Snapshot
    t_a_raw, m_a_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        fa = frontier(y, old, 0.5)
        fb = frontier(y, new, 0.5)
        m_a = np.array_equal(fa['alert'], fb['alert'])
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_a_raw.append((t1 - t0) * 1000.0); m_a_raw.append(peak / (1024 * 1024))

    # 2. Baseline B1: Generic Dense Matrix
    t_b1_raw, m_b1_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        mat_old = np.empty((G, N), dtype=bool)
        mat_new = np.empty((G, N), dtype=bool)
        for g, th in enumerate(thresholds):
            mat_old[g] = (old >= th)
            mat_new[g] = (new >= th)
        m_b1 = np.array_equal(mat_old, mat_new)
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_b1_raw.append((t1 - t0) * 1000.0); m_b1_raw.append(peak / (1024 * 1024))
        del mat_old, mat_new

    # 3. Baseline B2: Optimized Sparse Streaming
    t_b2_raw, m_b2_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        m_b2 = True
        for th in thresholds:
            if not np.array_equal(old >= th, new >= th):
                m_b2 = False
                break
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_b2_raw.append((t1 - t0) * 1000.0); m_b2_raw.append(peak / (1024 * 1024))

    # 4. Baseline B3: Generic Sort-Based Slice Comparator (Naive Implementation) - DYNAMIC EXECUTION
    t_b3_raw, m_b3_raw = [], []
    for _ in range(actual_b3_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        m_b3 = True
        for th in thresholds:
            slice_old = np.sort(np.where(old >= th)[0])
            slice_new = np.sort(np.where(new >= th)[0])
            if not np.array_equal(slice_old, slice_new):
                m_b3 = False
                break
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_b3_raw.append((t1 - t0) * 1000.0); m_b3_raw.append(peak / (1024 * 1024))

    # 5. Baseline B4: Optimized Generic Inverted-Index / Partition Exact Comparator
    t_b4_raw, m_b4_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        m_b4 = b4_exact_comparator_workflow(old, new)
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_b4_raw.append((t1 - t0) * 1000.0); m_b4_raw.append(peak / (1024 * 1024))

    # 6. Proposed (Build Compact Frontier + Equivalence Compare)
    t_prop_raw, m_prop_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        fa = frontier(y, old, 0.5)
        fb = frontier(y, new, 0.5)
        m_prop = _same_frontier(fa, fb)
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_prop_raw.append((t1 - t0) * 1000.0); m_prop_raw.append(peak / (1024 * 1024))

    # 7. Proposed: Full Regression Guard (Frontier + checked Proposition 1 attribution)
    t_guard_raw, m_guard_raw = [], []
    for _ in range(n_reps):
        gc.collect(); tracemalloc.start()
        t0 = time.perf_counter()
        rep = compare(y, old, new, 0.5, mode='full')
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        t_guard_raw.append((t1 - t0) * 1000.0); m_guard_raw.append(peak / (1024 * 1024))

    # Phase 2: Isolated Comparator
    fa_pre = frontier(y, old, 0.5); fb_pre = frontier(y, new, 0.5)
    t_a_iso = []
    for _ in range(n_reps):
        t0 = time.perf_counter()
        m = np.array_equal(fa_pre['alert'], fb_pre['alert'])
        t1 = time.perf_counter()
        t_a_iso.append((t1 - t0) * 1000.0)

    mat_o = np.empty((G, N), dtype=bool); mat_n = np.empty((G, N), dtype=bool)
    for g, th in enumerate(thresholds): mat_o[g] = (old >= th); mat_n[g] = (new >= th)
    t_b1_iso = []
    for _ in range(n_reps):
        t0 = time.perf_counter()
        m = np.array_equal(mat_o, mat_n)
        t1 = time.perf_counter()
        t_b1_iso.append((t1 - t0) * 1000.0)
    del mat_o, mat_n

    # Pre-represented structures for B4
    order_o_pre = np.argsort(-old, kind='stable')
    order_n_pre = np.argsort(-new, kind='stable')
    ends_o_pre = np.r_[np.flatnonzero(old[order_o_pre][:-1] != old[order_o_pre][1:]) + 1, N]
    ends_n_pre = np.r_[np.flatnonzero(new[order_n_pre][:-1] != new[order_n_pre][1:]) + 1, N]
    prev_o, prev_n = 0, 0
    buckets_o, buckets_n = [], []
    for e_o, e_n in zip(ends_o_pre, ends_n_pre):
        buckets_o.append(np.sort(order_o_pre[prev_o:e_o]))
        buckets_n.append(np.sort(order_n_pre[prev_n:e_n]))
        prev_o, prev_n = e_o, e_n

    t_b4_iso = []
    for _ in range(n_reps):
        t0 = time.perf_counter()
        m = (len(ends_o_pre) == len(ends_n_pre) and np.array_equal(ends_o_pre, ends_n_pre) and
             all(np.array_equal(a, b) for a, b in zip(buckets_o, buckets_n)))
        t1 = time.perf_counter()
        t_b4_iso.append((t1 - t0) * 1000.0)

    t_prop_iso = []
    for _ in range(n_reps):
        t0 = time.perf_counter()
        m = _same_frontier(fa_pre, fb_pre)
        t1 = time.perf_counter()
        t_prop_iso.append((t1 - t0) * 1000.0)

    def s(arr): 
        if not arr: return 0.0, 0.0
        return np.median(arr), (np.percentile(arr, 75, method="linear") - np.percentile(arr, 25, method="linear") if len(arr) > 1 else 0.0)

    print("\n[PHASE 1: WORKFLOW TIMING FROM RAW SCORES (Build Representation + Compare)]")
    print(f"{'Testing Paradigm':<46} | {'Median Runtime':>14} | {'IQR':>10} | {'Peak Aux Mem':>12} | {'Attribution Soundness':<30}")
    print("-" * 126)
    
    lbl_a = f"Baseline A (Selected Snapshot) [n={len(t_a_raw)}]"
    print(f"{lbl_a:<46} | {s(t_a_raw)[0]:11.2f} ms | {s(t_a_raw)[1]:7.2f} ms | {np.median(m_a_raw):9.2f} MB | None (selected set only)")
    
    lbl_b1 = f"Baseline B1 (Generic Dense Matrix) [n={len(t_b1_raw)}]"
    print(f"{lbl_b1:<46} | {s(t_b1_raw)[0]:11.2f} ms | {s(t_b1_raw)[1]:7.2f} ms | {np.median(m_b1_raw):9.2f} MB | None (raw array diff)")
    
    lbl_b2 = f"Baseline B2 (Optimized Sparse Streaming) [n={len(t_b2_raw)}]"
    print(f"{lbl_b2:<46} | {s(t_b2_raw)[0]:11.2f} ms | {s(t_b2_raw)[1]:7.2f} ms | {np.median(m_b2_raw):9.2f} MB | None (early stream diff)")
    
    lbl_b3 = f"Baseline B3 (Generic Sort-Slice Naive) [n={len(t_b3_raw)}]"
    print(f"{lbl_b3:<46} | {s(t_b3_raw)[0]:11.2f} ms | {s(t_b3_raw)[1]:7.2f} ms | {np.median(m_b3_raw):9.2f} MB | None (slice index diff)")
    
    lbl_b4 = f"Baseline B4 (Optimized Inverted Partition) [n={len(t_b4_raw)}]"
    print(f"{lbl_b4:<46} | {s(t_b4_raw)[0]:11.2f} ms | {s(t_b4_raw)[1]:7.2f} ms | {np.median(m_b4_raw):9.2f} MB | None (partition bucket diff)")
    
    lbl_prop = f"Proposed: Compact Frontier + Compare [n={len(t_prop_raw)}]"
    print(f"{lbl_prop:<46} | {s(t_prop_raw)[0]:11.2f} ms | {s(t_prop_raw)[1]:7.2f} ms | {np.median(m_prop_raw):9.2f} MB | Frontier Equivalence (Attribution omitted)")
    
    lbl_guard = f"Proposed: Full Regression Guard [n={len(t_guard_raw)}]"
    print(f"{lbl_guard:<46} | {s(t_guard_raw)[0]:11.2f} ms | {s(t_guard_raw)[1]:7.2f} ms | {np.median(m_guard_raw):9.2f} MB | Checked proper-prefix witness (Prop 1)")
    print("-" * 126)

    print("\n[PHASE 2: ISOLATED COMPARATOR LATENCY (On Pre-represented Structures)]")
    print(f"{'Testing Paradigm':<46} | {'Median Runtime':>14} | {'IQR':>10} | {'Input Representation':<30}")
    print("-" * 126)
    
    lbl_a_iso = f"Baseline A (Selected Alert Diff) [n={len(t_a_iso)}]"
    print(f"{lbl_a_iso:<46} | {s(t_a_iso)[0]:11.4f} ms | {s(t_a_iso)[1]:7.4f} ms | Pre-selected boolean alert vector")
    
    lbl_b1_iso = f"Baseline B1 (Dense Matrix Array Diff) [n={len(t_b1_iso)}]"
    print(f"{lbl_b1_iso:<46} | {s(t_b1_iso)[0]:11.2f} ms | {s(t_b1_iso)[1]:7.2f} ms | Pre-materialized (G, N) boolean matrix")
    
    lbl_b4_iso = f"Baseline B4 (Partition Bucket Diff) [n={len(t_b4_iso)}]"
    print(f"{lbl_b4_iso:<46} | {s(t_b4_iso)[0]:11.4f} ms | {s(t_b4_iso)[1]:7.4f} ms | Pre-partitioned observation ID buckets")
    
    lbl_prop_iso = f"Proposed: Core Compact Comparator [n={len(t_prop_iso)}]"
    print(f"{lbl_prop_iso:<46} | {s(t_prop_iso)[0]:11.2f} ms | {s(t_prop_iso)[1]:7.2f} ms | Pre-computed compact 1D frontier arrays")
    print("-" * 126)
    
    print("\nFor chronological CSV measurements and explicit linear-IQR summaries, run run_benchmark_measurements.py.")
    print("B4 and compact comparison test exact frontier equivalence; B1-B3 are fixed-grid checks.")
    print("Compact comparison takes O(N+G) after frontier construction; full attribution is measured separately.")
    print("Former canonical reference series are withdrawn; see raw_timing_data/withdrawn/README.md.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Baseline Benchmark for Precision-Constrained Decision Selectors")
    parser.add_argument('--N', type=int, default=100000, help='Total observations count (default: 100,000)')
    parser.add_argument('--G', type=int, default=1000, help='Number of score groups / evaluated thresholds (default: 1,000)')
    parser.add_argument('--reps', type=int, default=5, help='Number of repetitions for benchmark profiling (default: 5)')
    parser.add_argument('--b3-reps', type=int, default=None, help='Custom repetitions for Baseline B3 (defaults to --reps if omitted)')
    parser.add_argument('--skip-divergence', action='store_true', help='Skip divergence mode benchmark')
    parser.add_argument('--divergence', action='store_true', help='Run divergence mode benchmark (default)')
    args = parser.parse_args()

    verify_construct_validity()
    if not args.skip_divergence:
        benchmark_divergence_modes(N=args.N, G=args.G)
    benchmark_all_baselines(N=args.N, G=args.G, n_reps=args.reps, b3_reps=args.b3_reps)