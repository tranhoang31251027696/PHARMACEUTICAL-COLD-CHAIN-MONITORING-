"""Consolidated study logic; isolated sections preserve each check's local state."""
from types import SimpleNamespace as _Namespace
_sections = {}


def _make_validate_benchmarks():
    """Audit timing summaries and reconstruct each timed certificate workload."""
    from pathlib import Path
    import sys, json, csv, hashlib
    import numpy as np
    Q = Path(__file__).resolve().parent
    sys.path.insert(0, str(Q / 'src'))
    from policy_exact import compare_policies
    from independent_oracle import verify

    def main():
        R = Q / 'results'
        read = lambda name: list(csv.DictReader((R / name).open(encoding='utf-8')))
        raw = read('certificate_timings.csv')
        count = 0
        hashes = []
        for n, g in [(1000, 20), (10000, 100), (100000, 500)]:
            rng = np.random.default_rng(n + g)
            a = rng.integers(0, g, n) / (g - 1)
            y = rng.integers(0, 2, n)
            ids = list(range(n))
            for workload in ['invariant', 'divergent']:
                b = a.copy() if workload == 'invariant' else a + rng.choice([-1, 0, 1], n) * 1e-08
                c = compare_policies(y, a, b, ids=ids)
                v = verify(y, a, b, ids, c)
                count += 1
                hashes.append({'n': n, 'g': g, 'workload': workload, 'input_sha256': c['input_sha256'], 'oracle_probes': v['probes']})
                for mode in [False, True]:
                    cc = c if mode else compare_policies(y, a, b, ids=ids, with_witness=False)
                    rr = [r for r in raw if r['n'] == str(n) and r['workload'] == workload and (r['witness'] == str(mode))]
                    assert len(rr) == 10
                    for row in rr:
                        assert int(row['cells']) == len(cc['cells']) and float(row['psc']) == cc['psc']
                        assert int(row['bytes']) == len(json.dumps(cc).encode())
                        assert int(row['witness_cells']) == sum((x['witness'] is not None for x in cc['cells']))
                for _ in range(10):
                    rng.permutation([False, True])
        matched = read('matched_method_timings.csv')
        summaries = read('matched_method_summary.csv')
        assert len(matched) == 270 and len(summaries) == 45
        for s in summaries:
            rr = [r for r in matched if all((r[k] == s[k] for k in ['pipeline', 'workload', 'method']))]
            assert len(rr) == 6 and {int(r['replicate']) for r in rr} == set(range(6))
            v = [float(r['elapsed_ms']) for r in rr]
            q = np.percentile(v, [25, 75], method='linear')
            assert np.isclose(np.median(v), float(s['median_ms']), atol=1e-12, rtol=0)
            assert np.isclose(q[1] - q[0], float(s['iqr_ms']), atol=1e-12, rtol=0)
        metadata = json.loads((R / 'matched_method_metadata.json').read_text(encoding='utf-8'))
        for name, digest in metadata['source_sha256'].items():
            assert hashlib.sha256((Q / name.replace('\\', '/')).read_bytes()).hexdigest() == digest
        sourcefiles = [R / 'execution_source_snapshot/run_experiments.py', R / 'execution_source_snapshot/policy_exact.py']
        result = {'status': 'PASS', 'certificate_timing_rows': len(raw), 'reconstructed_workloads': count, 'workload_hashes': hashes, 'matched_method_rows': len(matched), 'matched_method_groups': len(summaries), 'measurement_source_sha256': {f.relative_to(Q).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sourcefiles}, 'raw_record_sha256': {name: hashlib.sha256((R / name).read_bytes()).hexdigest() for name in ['certificate_timings.csv', 'certificate_timing_summary.csv', 'matched_method_timings.csv', 'matched_method_summary.csv']}}
        (R / 'benchmark_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_benchmarks'] = _make_validate_benchmarks()

def _make_validate_revision():
    """Replay program certificates, version evidence and phase-level measurements."""
    from pathlib import Path
    from fractions import Fraction
    import sys, json, csv, hashlib
    import numpy as np
    Q = Path(__file__).resolve().parent
    sys.path.insert(0, str(Q / 'src'))
    from independent_oracle import candidates, select, verify
    from policy_exact import DEFAULT
    from program_evaluation import modules, execute_program

    def main():
        R = Q / 'results/v2'
        m = json.loads((Q / 'inputs/manifest.json').read_text(encoding='utf-8'))
        records = {r['case_id']: r for r in m['cases']}
        mods = modules()
        count = 0
        probes = 0
        rows = list(csv.DictReader((R / 'program_results.csv').open(encoding='utf-8')))
        for row in rows:
            rec = records[row['case_id']]
            d = np.load(Q / 'inputs' / rec['file'])
            y = d['y']
            s = d['old']
            ids = d['ids'].tolist()
            sut, h = mods[row['program']]
            table = sut.build(y, s)
            positive = bool(y.sum())
            c = json.loads((Q / row['certificate_file']).read_text(encoding='utf-8'))
            assert c['source_sha256'] == h and c['frozen_input_sha256'] == rec['sha256']
            expected = candidates(y, s, DEFAULT)
            _, events = execute_program(sut, table, Fraction(3, 10), positive, len(y))
            assert c['guard_events'] == list(map(str, sorted(events)))
            br = sorted({Fraction(3, 10), Fraction(9, 10)} | {p for p, *_ in expected if Fraction(3, 10) < p < Fraction(9, 10)} | {p for p in events if Fraction(3, 10) < p < Fraction(9, 10)})
            pp = sorted(set(br) | {(a + b) / 2 for a, b in zip(br, br[1:])})
            assert list(map(str, pp)) == [r['alpha'] for r in c['probes']]
            bad = False
            for p in c['probes']:
                alpha = Fraction(p['alpha'])
                actual, traced = execute_program(sut, table, alpha, positive, len(y))
                ref = select(expected, alpha, positive, DEFAULT)[2]
                assert traced == events and hex(actual) == p['actual_bits_hex'] and (hex(ref) == p['expected_bits_hex'])
                assert p['conforms'] == (actual == ref)
                bad |= actual != ref
                probes += 1
                if actual != ref:
                    xor = actual ^ ref
                    i = (xor & -xor).bit_length() - 1
                    assert p['witness_row_id'] == ids[i]
            assert c['conforms'] == (not bad) and bad == (row['conformance_failure'] == 'True')
            count += 1
        ps = json.loads((R / 'program_summary.json').read_text())
        assert count == ps['program_runs'] == 210 and probes == ps['policy_probes']
        assert sum((r['conformance_failure'] == 'True' for r in rows)) == ps['nonconforming_runs'] == 136
        versions = json.loads((Q / 'inputs/version_inputs/manifest.json').read_text())
        version_count = 0
        outs = {v: np.load(R / f'scipy_{v}/scores.npz') for v in ['1.15.3', '1.18.1']}
        for rec in versions['cases']:
            f = Q / 'inputs/version_inputs' / rec['file']
            assert hashlib.sha256(f.read_bytes()).hexdigest() == rec['sha256']
            d = np.load(f)
            cid = rec['case_id']
            c = json.loads((R / 'version_certificates' / f'{cid}.json').read_text())
            verify(d['y'], outs['1.15.3'][cid], outs['1.18.1'][cid], list(range(len(d['y']))), c)
            version_count += 1
        raw = list(csv.DictReader((R / 'ablation_raw.csv').open()))
        summary = list(csv.DictReader((R / 'ablation_summary.csv').open()))
        assert len(raw) == 60
        for row in raw:
            phase = sum((float(row[k]) for k in ['construction_ms', 'sweep_excluding_witness_ms', 'witness_ms', 'assembly_and_hash_ms', 'serialization_ms']))
            assert abs(phase + float(row['unattributed_ms']) - float(row['total_ms'])) < 1e-08
            if row['witness'] == 'False':
                assert float(row['witness_ms']) == 0
        for s in summary:
            rr = [r for r in raw if r['n'] == s['n'] and r['witness'] == s['witness']]
            vals = [float(r[s['phase']]) for r in rr]
            q = np.percentile(vals, [25, 75], method='linear')
            assert len(rr) == 10 and np.isclose(np.median(vals), float(s['median_ms']), rtol=0, atol=1e-12) and np.isclose(q[1] - q[0], float(s['iqr_ms']), rtol=0, atol=1e-12)
        result = {'status': 'PASS', 'program_certificates_replayed': count, 'program_policy_probes': probes, 'real_version_certificates_reverified': version_count, 'ablation_records_reconciled': len(raw), 'new_spec_provided': False}
        (R / 'revision_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_revision'] = _make_validate_revision()

def _make_validate_v3():
    """Replay all external certificates and cross-check adverse/SMT/CI evidence."""
    from pathlib import Path
    from fractions import Fraction
    import sys, json, csv, hashlib
    import numpy as np
    import z3
    from sklearn.metrics import precision_recall_curve
    Q = Path(__file__).resolve().parent
    sys.path.insert(0, str(Q / 'src'))
    from external_sut_evaluation import upstream_functions, actual_table
    from independent_oracle import candidates, select
    from policy_exact import DEFAULT
    from adapter_admission import admission_result

    def main():
        R = Q / 'results/v3'
        manifest = json.loads((Q / 'inputs/external_sut/manifest.json').read_text(encoding='utf-8'))
        records = {r['case_id']: r for r in manifest['cases']}
        functions = upstream_functions()
        results = list(csv.DictReader((R / 'external_sut_results.csv').open()))
        certificates = 0
        probes = 0
        for row in results:
            rec = records[row['case_id']]
            f = Q / 'inputs/external_sut' / rec['file']
            assert hashlib.sha256(f.read_bytes()).hexdigest() == rec['sha256']
            d = np.load(f)
            y = d['y']
            s = d['scores']
            ids = d['ids'].tolist()
            c = json.loads((Q / row['certificate_file']).read_text(encoding='utf-8'))
            assert c['input_sha256'] == rec['sha256']
            fn = precision_recall_curve if row['variant'] == 'installed_current' else functions[row['variant']][0]
            actual, _ = actual_table(fn, y, s)
            gold = candidates(y, s, DEFAULT)
            lo = Fraction(3, 10)
            hi = Fraction(9, 10)
            br = sorted({lo, hi} | {p for p, *_ in actual + gold if lo < p < hi})
            pp = sorted(set(br) | {(a + b) / 2 for a, b in zip(br, br[1:])})
            assert c['critical_values'] == list(map(str, br)) and [r['alpha'] for r in c['probes']] == list(map(str, pp))
            lookup = {}
            for r in c['probes']:
                a = Fraction(r['alpha'])
                e = select(gold, a, True, DEFAULT)
                v = select(actual, a, True, DEFAULT)
                xor = e[2] ^ v[2]
                lookup[a] = bool(xor)
                assert r['expected_bits'] == hex(e[2]) and r['actual_bits'] == hex(v[2]) and (r['equal'] == (not xor))
                assert r['expected_n'] == e[1] and r['actual_n'] == v[1]
                if xor:
                    i = (xor & -xor).bit_length() - 1
                    assert r['witness_id'] == ids[i]
                else:
                    assert r['witness_id'] is None
                probes += 1
            length = sum((b - a for a, b in zip(br, br[1:]) if lookup[(a + b) / 2]), Fraction(0))
            assert Fraction(c['psc_exact']) == length / (hi - lo) and c['equivalent'] == (not any(lookup.values()))
            assert (not c['equivalent']) == (row['policy_divergent'] == 'True')
            certificates += 1
        failures = json.loads((R / 'failure_results.json').read_text())
        assert len(failures) == 15
        for f in (R / 'failure_fixtures').glob('*.py'):
            out = admission_result(f.read_text(encoding='utf-8'))
            assert out['status'] == 'UNSUPPORTED' and (not out['certified'])
        assert all((f['status'] == 'UNSUPPORTED' and (not f['certified']) for f in failures))
        ci = list(csv.DictReader((R / 'ci_timings.csv').open()))
        assert len(ci) == 60 and all((int(r['exit_code']) in [0, 1] and float(r['process_ms']) >= float(r['gate_ms']) for r in ci))
        smt = list(csv.DictReader((R / 'smt_results.csv').open()))
        assert len(smt) == 279
        verdict = {(r['case_id'], r['variant']): r['policy_divergent'] == 'True' for r in results}
        for (cid, variant), bad in verdict.items():
            solver = z3.SolverFor('QF_LRA')
            solver.set(timeout=5000)
            solver.from_string((R / 'smt_queries' / f'{cid}_{variant}.smt2').read_text(encoding='utf-8'))
            answer = solver.check()
            assert answer != z3.unknown and (answer == z3.sat) == bad
        for r in smt:
            assert (r['z3_result'] == 'sat') == verdict[r['case_id'], r['variant']]
            if r['model_alpha']:
                rec = records[r['case_id']]
                d = np.load(Q / 'inputs/external_sut' / rec['file'])
                gold = candidates(d['y'], d['scores'], DEFAULT)
                fn = precision_recall_curve if r['variant'] == 'installed_current' else functions[r['variant']][0]
                actual, _ = actual_table(fn, d['y'], d['scores'])
                a = Fraction(r['model_alpha'])
                assert select(gold, a, True, DEFAULT)[2] != select(actual, a, True, DEFAULT)[2]
        result = {'status': 'PASS', 'external_certificates_replayed': certificates, 'external_policy_probes': probes, 'failure_modes_rejected': len(failures), 'ci_process_measurements': len(ci), 'smt_records_verified': len(smt), 'smtlib_tasks_resolved': len(verdict), 'old_v2_status': 'The unchanged core results remain separate; executed-program adapter has additionally been hardened and rerun.'}
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v3'] = _make_validate_v3()

def _make_validate_v4():
    """Reconcile V4 raw measurements and independently replay diagnostic outputs."""
    from pathlib import Path
    from fractions import Fraction as F
    import json, csv, hashlib, inspect
    import numpy as np
    from sklearn.model_selection import TunedThresholdClassifierCV
    from external_selector_integration import execute, admission
    from complete_region_comparison import Q, candidates, select, DEFAULT, upstream_functions, actual_table, verify_regions

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def rows(p):
        return list(csv.DictReader(p.open(encoding='utf-8')))

    def main():
        R = Q / 'results/v4'
        on = read(R / 'onboarding_summary.json')
        assert on['status'] == 'PASS' and on['mismatches'] == 0 and (on['upstream_source_edits'] == 0)
        source = hashlib.sha256(inspect.getsource(TunedThresholdClassifierCV).encode()).hexdigest()
        assert source == on['source_class_sha256']
        records = read(Q / 'inputs/manifest.json')['cases']
        probes = 0
        callbacks = 0
        count = 0
        for rec in records:
            if rec.get('seed') != 0:
                continue
            f = Q / 'inputs' / rec['file']
            assert sha(f) == rec['sha256']
            d = np.load(f)
            y = d['y'][:48]
            s = d['old'][:48]
            c = read(R / (rec['case_id'] + '_optimizer.json'))
            assert c['source_input_sha256'] == rec['sha256'] and c['source_class_sha256'] == source and (c['ids'] == d['ids'][:48].tolist())
            gold = candidates(y, s, DEFAULT)
            br = sorted({F(3, 10), F(9, 10)} | {p for p, *_ in gold if F(3, 10) < p < F(9, 10)})
            pp = sorted(set(br) | {(a + b) / 2 for a, b in zip(br, br[1:])})
            assert [r['alpha'] for r in c['policy_probes']] == list(map(str, pp))
            for a, r in zip(pp, c['policy_probes']):
                actual, calls = execute(y, s, a)
                expected = select(gold, a, True, DEFAULT)[2]
                assert r['expected_bits'] == hex(expected) == r['actual_bits'] == hex(actual) and r['scorer_calls'] == len(calls)
                probes += 1
                callbacks += len(calls)
            count += 1
        assert count == 3 and probes == on['total_policy_probes'] == 59 and (callbacks == sum((r['scorer_callbacks'] for r in on['workloads'])))
        assert len(on['unsupported_configurations']) == 4 and all((r['status'] == 'UNSUPPORTED' for r in on['unsupported_configurations']))
        sample = np.array([0.1, 0.1, 0.3, 0.8])
        rejected = 0
        for th, cv, refit in [(100, 'prefit', False), (np.array([0.1, 0.8]), 'prefit', False), (np.unique(sample), 3, False), (np.unique(sample), 'prefit', True)]:
            try:
                admission(sample, th, cv, refit)
            except ValueError:
                rejected += 1
        assert rejected == 4
        vendor = Q / 'vendor/external_eval_toolkit'
        vm = read(vendor / 'SOURCE_MANIFEST.json')
        for name, rec in vm['files'].items():
            assert sha(vendor / name) == rec['sha256']
        assert on['second_project']['full_package_executed'] is False and on['second_project']['policy_certificate_issued'] is False
        region = read(R / 'complete_region_summary.json')
        assert region['status'] == 'PASS' and region['source_sha256'] == sha(Q / 'complete_region_comparison.py')
        records = {r['case_id']: r for r in read(Q / 'inputs/external_sut/manifest.json')['cases']}
        functions = upstream_functions()
        certs = {}
        checked = 0
        for f in sorted((R / 'region_certificates').glob('*.json')):
            r = read(f)
            rec = records[r['case_id']]
            p = Q / 'inputs/external_sut' / rec['file']
            assert sha(p) == rec['sha256']
            d = np.load(p)
            gold = candidates(d['y'], d['scores'], DEFAULT)
            actual, _ = actual_table(functions[r['variant']][0], d['y'], d['scores'])
            c = r['certificate']
            assert len(c['representative_witnesses']) == len(c['divergent_regions'])
            verify_regions(gold, actual, c)
            key = (r['case_id'], r['variant'])
            assert key not in certs or certs[key] == c
            certs[key] = c
            checked += 1
            if r['method'] == 'smt_all_regions':
                assert r['algorithm_stats']['residual_result'] == 'unsat'
        rr = rows(R / 'complete_region_timings.csv')
        assert len(rr) == 48 and checked == 16 and (len(certs) == 8)
        for key, c in certs.items():
            for method in ['partition', 'smt_all_regions']:
                group = [r for r in rr if (r['case_id'], r['variant']) == key and r['method'] == method]
                assert sorted((int(r['replicate']) for r in group)) == [0, 1, 2]
                for r in group:
                    assert int(r['regions']) == len(c['divergent_regions']) and r['psc_exact'] == c['psc_exact'] and (float(r['independent_checker_ms']) > 0) and (float(r['producer_and_serialization_ms']) > 0)
        raw = rows(R / 'checker_cost_raw.csv')
        summary = rows(R / 'checker_cost_summary.csv')
        meta = read(R / 'checker_cost_metadata.json')
        assert len(raw) == 36 and len(summary) == 6 and (meta['status'] == 'PASS')
        assert meta['checker_source_sha256'] == sha(Q / 'src/independent_oracle.py') and meta['timing_tracemalloc'] is False and (meta['memory_timing_pooled'] is False)
        for s in summary:
            group = [r for r in raw if (r['n'], r['g'], r['workload']) == (s['n'], s['g'], s['workload'])]
            timing = [r for r in group if r['phase'] == 'untraced_consumer']
            memory = [r for r in group if r['phase'] == 'separate_memory_run']
            assert len(memory) == 1 and sorted((int(r['replicate']) for r in timing)) == list(range(5))
            assert all((not r['peak_aux_mib'] for r in timing)) and (not memory[0]['checker_ms']) and (not memory[0]['parse_ms'])
            assert len({r['input_sha256'] for r in group}) == 1 and len({r['policy_probes'] for r in group}) == 1
            v = [float(r['checker_ms']) for r in timing]
            q = np.percentile(v, [25, 75], method='linear')
            for a, b in [(float(s['checker_median_ms']), np.median(v)), (float(s['checker_iqr_ms']), q[1] - q[0]), (float(s['parse_median_ms']), np.median([float(r['parse_ms']) for r in timing])), (float(s['separate_peak_aux_mib']), float(memory[0]['peak_aux_mib']))]:
                assert np.isclose(a, b, rtol=1e-12, atol=1e-12)
            assert float(s['separate_peak_aux_mib']) > 0
        result = {'status': 'PASS', 'external_optimizer_workloads_replayed': count, 'external_optimizer_policies_replayed': probes, 'scorer_callbacks_replayed': callbacks, 'unsupported_configurations_rejected': rejected, 'region_certificates_replayed': checked, 'matched_region_tasks': len(certs), 'complete_region_timing_records': len(rr), 'checker_raw_records_reconciled': len(raw), 'checker_groups_reconciled': len(summary), 'second_project_executed': False, 'scope': 'Executed optimizer replay, independent exact membership/region checks, raw timing reconciliation and pinned-source bindings. No second executed project or additional confirmed defect is inferred.'}
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v4'] = _make_validate_v4()

def _make_validate_v5():
    """Replay the second project and extended diagnostics; reconcile paired costs."""
    from pathlib import Path
    import json, csv, hashlib, sys, ast, xml.etree.ElementTree as ET
    import numpy as np
    from second_project_evaluation import Q, evidence, sha
    from expanded_region_benchmark import fixture, prepare
    from complete_region_comparison import verify_regions

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def rows(p):
        return list(csv.DictReader(p.open(encoding='utf-8')))

    def main():
        prior = Q / 'evidence/V4_FINAL_RELEASE_EVIDENCE'
        pr = read(prior / 'RELEASE_VERIFICATION.json')
        assert pr['status'] == 'PASS' and len(pr['stages']) == 19 and (pr['archive_sha256_before'] == pr['archive_sha256_after'] == 'f45403ce8011adc3d084af2b432953286072fd8b6302e134ab1e087d4075b835')
        for name, digest in read(prior / 'EVIDENCE_MANIFEST.json').items():
            assert sha(prior / name) == digest
        R = Q / 'results/v5'
        second = read(R / 'second_project_summary.json')
        assert second['status'] == 'PASS' and second['full_package_installed_and_executed'] and (second['confirmed_defects_added'] == 0)
        records = {r['case_id']: r for r in read(Q / 'inputs/manifest.json')['cases']}
        observed = 0
        div = 0
        grids = 0
        visible = 0
        visible_probes = 0
        rr = rows(R / 'second_project_results.csv')
        assert len(rr) == 30
        for r in rr:
            rec = records[r['case_id']]
            path = Q / 'inputs' / rec['file']
            assert sha(path) == rec['sha256']
            d = np.load(path)
            saved = read(R / 'second_project_certificates' / r['certificate'])
            rebuilt = evidence(d['y'][:64], d['old'][:64], d['ids'][:64].tolist())
            for k, v in rebuilt.items():
                assert saved[k] == v, (r['case_id'], k)
            assert saved['source_input_sha256'] == rec['sha256'] and saved['source_module_sha256'] == second['source_module_sha256']
            assert len(saved['probes']) == int(r['policy_probes']) and len(saved['divergent_regions']) == int(r['components']) and (saved['psc_exact'] == r['psc_exact'])
            observed += len(saved['probes'])
            div += not saved['equivalent_to_rational_reference']
            grids += saved['grid_detected']
            visible += saved['representable_policy_difference']
            visible_probes += len(saved['representable_policy_probes'])
        assert observed == second['policy_probes'] == 884 and div == second['divergent_workloads'] == 27 and (grids == second['grid_detected_workloads'] == 0)
        assert visible == second['representable_policy_divergent_workloads'] == 19 and visible_probes == second['representable_policy_probes'] == 196
        expanded = read(R / 'expanded_region_summary.json')
        assert expanded['status'] == 'PASS' and expanded['source_sha256'] == sha(Q / 'expanded_region_benchmark.py')
        pairs = {}
        certcount = 0
        bycase = {t['case_id']: t for t in expanded['tasks']}
        for p in (R / 'expanded_region_certificates').glob('*.json'):
            saved = read(p)
            y, s = fixture(saved['n'], saved['g'])
            assert hashlib.sha256(y.astype('<i8').tobytes() + s.astype('<f8').tobytes()).hexdigest() == saved['input_sha256']
            gold, actual = prepare(y, s, saved['pattern'])
            c = saved['certificate']
            verify_regions(gold, actual, c)
            if saved['case_id'] in pairs:
                assert c == pairs[saved['case_id']]
            pairs[saved['case_id']] = c
            certcount += 1
            if saved['method'] == 'smt_all_regions':
                assert saved['algorithm_stats']['residual_result'] == 'unsat'
        raw = rows(R / 'expanded_region_raw.csv')
        assert len(pairs) == 27 and certcount == 54 and (len(raw) == 270)
        for case, c in pairs.items():
            for method in ['partition', 'smt_all_regions']:
                group = [r for r in raw if r['case_id'] == case and r['method'] == method]
                assert sorted((int(r['replicate']) for r in group)) == list(range(5))
                for r in group:
                    assert int(r['divergent_components']) == len(c['divergent_regions']) and r['psc_exact'] == c['psc_exact']
                    assert np.isclose(float(r['total_checked_ms']), sum((float(r[k]) for k in ['preparation_ms', 'producer_serialization_ms', 'checker_ms'])), rtol=1e-12)
                    assert all((float(r[k]) > 0 for k in ['preparation_ms', 'producer_serialization_ms', 'checker_ms']))
        raw = rows(R / 'paired_checker_raw.csv')
        summary = rows(R / 'paired_checker_summary.csv')
        meta = read(R / 'paired_checker_metadata.json')
        assert meta['status'] == 'PASS' and len(raw) == 72 and (len(summary) == 12)
        for source, digest in meta['source_sha256'].items():
            assert sha(Q / source) == digest
        for s in summary:
            group = [r for r in raw if all((r[k] == s[k] for k in ['n', 'g', 'workload', 'method']))]
            timing = [r for r in group if r['phase'] == 'untraced']
            memory = [r for r in group if r['phase'] == 'separate_memory']
            assert len(memory) == 1 and sorted((int(r['replicate']) for r in timing)) == list(range(5)) and (len({r['input_sha256'] for r in group}) == 1)
            assert all((not r['peak_aux_mib'] for r in timing)) and (not memory[0]['checker_ms']) and (not memory[0]['parse_ms'])
            v = [float(r['checker_ms']) for r in timing]
            q = np.percentile(v, [25, 75], method='linear')
            for a, b in [(float(s['median_ms']), np.median(v)), (float(s['iqr_ms']), q[1] - q[0]), (float(s['peak_aux_mib']), float(memory[0]['peak_aux_mib']))]:
                assert np.isclose(a, b, rtol=1e-12, atol=1e-12)
            opposite = [r for r in raw if all((r[k] == s[k] for k in ['n', 'g', 'workload']))]
            assert len({r['input_sha256'] for r in opposite}) == len({r['probes'] for r in opposite}) == 1
        audit = read(R / 'streaming_artifact_verification.json')
        assert audit['status'] == 'PASS' and audit['certificates_independently_reverified'] == 428 and (audit['critical_and_open_cell_probes'] == 41348)
        tree = ast.parse((Q / 'src/streaming_checker.py').read_text(encoding='utf-8'))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)] + [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        assert not any((v and ('policy_exact' in v or 'independent_oracle' in v or 'heapq' in v) for v in imports))
        upstream = ET.parse(R / 'upstream_threshold_tests.xml')
        assert sum((int(t.get('tests', 0)) for t in upstream.iter('testsuite'))) == 18 and all((int(t.get('failures', 0)) + int(t.get('errors', 0)) == 0 for t in upstream.iter('testsuite')))
        result = {'status': 'PASS', 'second_project_workloads_replayed': len(rr), 'second_project_policy_probes_replayed': observed, 'second_project_semantic_differentials': int(div), 'additional_confirmed_defects': 0, 'expanded_region_tasks': len(pairs), 'expanded_certificates_replayed': certcount, 'expanded_timing_records_reconciled': 270, 'paired_checker_raw_records_reconciled': len(raw), 'paired_checker_groups_reconciled': len(summary), 'streaming_corpus_certificates': 428, 'upstream_threshold_tests': 18, 'independent_checker_has_no_production_import': True}
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v5'] = _make_validate_v5()

def _make_validate_v6():
    """Replay the additional documented defect and reconcile targeted V6 evidence."""
    from pathlib import Path
    from fractions import Fraction as F
    import json, csv, math, hashlib
    import numpy as np
    from scipy_documented_defect import Q, functions, regression_test, sha, cases
    from streaming_checker import verify
    from independent_oracle import candidates, select
    from policy_exact import DEFAULT
    from expanded_region_benchmark import fixture, prepare
    from complete_region_comparison import verify_regions, member
    from policy_significance import lattice_hits

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def rows(p):
        return list(csv.DictReader(p.open(encoding='utf-8')))

    def main():
        R = Q / 'results/v6'
        prior = Q / 'evidence/V5_FINAL_RELEASE_EVIDENCE'
        pr = read(prior / 'RELEASE_VERIFICATION.json')
        assert pr['status'] == 'PASS' and len(pr['stages']) == 23 and (pr['archive_sha256_before'] == pr['archive_sha256_after'] == '4a580830ee0a2c4d5cf78290b80312c28e8cc4a2f66fabfcc40568432492a2c1')
        for name, digest in read(prior / 'EVIDENCE_MANIFEST.json').items():
            assert sha(prior / name) == digest
        sig = read(R / 'policy_significance_summary.json')
        assert sig['status'] == 'PASS' and sig['source_sha256'] == sha(Q / 'policy_significance.py')
        rr = rows(R / 'policy_significance_cases.csv')
        assert len(rr) == 30
        values = []
        visible = 0
        records = {r['case_id']: r for r in read(Q / 'inputs/manifest.json')['cases']}
        observed_max = F(0)
        supremum_max = F(0)
        for row in rr:
            c = read(Q / 'results/v5/second_project_certificates' / (row['case_id'] + '.json'))
            psc = F(c['psc_exact'])
            assert row['psc_exact'] == str(psc)
            if psc > 0:
                values.append(psc)
            assert int(row['max_changed_observations']) == max(((int(p['reference_bits'], 16) ^ int(p['actual_bits'], 16)).bit_count() for p in c['probes']))
            assert F(row['precision_shortfall_supremum_exact']) >= F(row['max_actual_precision_shortfall_exact'])
            data = np.load(Q / 'inputs' / records[row['case_id']]['file'])
            y = data['y'][:64]
            observed = F(0)
            supremum = F(0)
            lookup = {F(p['alpha']): int(p['actual_bits'], 16) for p in c['probes']}
            cuts = list(map(F, c['critical_values']))

            def precision(bits):
                return F(sum((int(y[i]) for i in range(len(y)) if bits >> i & 1)), bits.bit_count())
            for a, bits in lookup.items():
                if bits:
                    observed = max(observed, a - precision(bits))
            supremum = observed
            for left, right in zip(cuts, cuts[1:]):
                bits = lookup[(left + right) / 2]
                if bits:
                    supremum = max(supremum, right - precision(bits))
            assert F(row['max_actual_precision_shortfall_exact']) == observed and F(row['precision_shortfall_supremum_exact']) == supremum
            observed_max = max(observed_max, observed)
            supremum_max = max(supremum_max, supremum)
            visible += int(row['representable_policy_differences']) > 0
            for digits in [2, 3, 4, 6]:
                count = 0
                scale = 10 ** digits
                for r in c['divergent_regions']:
                    lo = F(r['lo']) * scale
                    hi = F(r['hi']) * scale
                    first = math.floor(lo) + 1
                    last = math.ceil(hi) - 1
                    if r['left_closed'] and lo.denominator == 1:
                        first = int(lo)
                    if r['right_closed'] and hi.denominator == 1:
                        last = int(hi)
                    count += max(0, last - first + 1)
                assert count == int(row[f'decimal_{digits}_affected_policies']) == 0
                if digits == 2:
                    brute = sum((any((member(r, F(i, scale)) for r in c['divergent_regions'])) for i in range(3 * scale // 10, 9 * scale // 10 + 1)))
                    assert brute == count
        assert len(values) == 27 and visible == 19
        assert sig['max_precision_shortfall'] == float(observed_max) and sig['max_precision_shortfall_supremum'] == float(supremum_max)
        for key, q in [('min', 0), ('q25', 0.25), ('median', 0.5), ('q75', 0.75), ('max', 1)]:
            assert np.isclose(float(F(sig['positive_psc_distribution'][key]['exact'])), np.quantile([float(v) for v in values], q, method='linear'), rtol=1e-12, atol=1e-30)
        funcs, manifest, nodes = functions()
        assert regression_test(funcs['affected']) == 'FAIL_EXPECTED_REGRESSION' and regression_test(funcs['fixed']) == regression_test(funcs['current']) == 'PASS'
        sr = rows(R / 'scipy_defect_results.csv')
        assert len(sr) == 108
        div = 0
        grid = 0
        snapshot = 0
        inputs = {name: (x, knots, y, ids, rec) for name, x, knots, y, ids, rec in cases()}
        assert len(inputs) == 36
        for row in sr:
            saved = read(R / 'scipy_defect_certificates' / row['certificate_file'])
            x = np.asarray(saved['axis_values'], dtype=saved['axis_dtype'])
            knots = np.asarray(saved['knot_scores'])
            y = np.asarray(saved['labels'])
            ids = saved['ids']
            scores = np.asarray(funcs[row['variant']](x, knots, kind='nearest')(x), dtype=float)
            xx, kk, yy, ii, rec = inputs[row['case_id']]
            assert x.dtype == xx.dtype and np.array_equal(x, xx) and np.array_equal(knots, kk) and np.array_equal(y, yy) and (ids == ii)
            assert saved['source_input_sha256'] == (rec['sha256'] if rec else None)
            assert np.array_equal(scores, saved['actual_scores']) and np.array_equal(knots, saved['reference_scores'])
            if row['variant'] != 'current':
                assert saved['source_ast_sha256'] == nodes[row['variant']]
            c = saved['certificate']
            v = verify(y, knots, scores, ids, c)
            assert v['probes'] == int(row['independent_probes'])
            gold = candidates(y, knots, DEFAULT)
            actual = candidates(y, scores, DEFAULT)
            snap = select(gold, F(1, 2), True, DEFAULT)[2] != select(actual, F(1, 2), True, DEFAULT)[2]
            gr = any((select(gold, F(3, 10) + F(3, 5) * i / 12, True, DEFAULT)[2] != select(actual, F(3, 10) + F(3, 5) * i / 12, True, DEFAULT)[2] for i in range(13)))
            assert str(snap) == row['snapshot_detected'] and str(gr) == row['grid_detected'] and (c['psc_exact'] == row['psc_exact']) and (str(not c['equivalent']) == row['policy_divergent'])
            if row['variant'] == 'affected':
                div += not c['equivalent']
                grid += gr
                snapshot += snap
            else:
                assert c['equivalent']
        sm = read(R / 'scipy_defect_summary.json')
        assert sm['status'] == 'PASS' and sm['source_sha256'] == sha(Q / 'scipy_documented_defect.py') and (div == sm['affected_policy_divergent'] == 31) and (grid == sm['grid_detected'] == 31) and (snapshot == sm['snapshot_detected'] == 26)
        allowed = rows(R / 'scipy_allowed_policy_counts.csv')
        assert len(allowed) == 36
        for row in allowed:
            wrapper = read(R / 'scipy_defect_certificates' / (row['case_id'] + '_affected.json'))
            regions = [c for c in wrapper['certificate']['cells'] if not c['equal']]
            for digits in [2, 3, 4, 6]:
                assert int(row[f'decimal_{digits}_affected_policies']) == lattice_hits(regions, digits)
        for summary in sig['documented_scipy_defect_decimal_resolution']:
            key = f"decimal_{summary['decimal_places']}_affected_policies"
            assert summary['affected_workloads'] == sum((int(r[key]) > 0 for r in allowed)) == 31 and summary['affected_policy_workload_pairs'] == sum((int(r[key]) for r in allowed))
        lm = read(R / 'large_g_summary.json')
        assert lm['status'] == 'PASS' and lm['source_sha256'] == sha(Q / 'large_g_region_benchmark.py')
        raw = rows(R / 'large_g_raw.csv')
        assert len(raw) == 36
        certs = {}
        checks = 0
        for p in (R / 'large_g_certificates').glob('*.json'):
            c = read(p)
            y, s = fixture(c['n'], c['g'])
            assert hashlib.sha256(y.astype('<i8').tobytes() + s.astype('<f8').tobytes()).hexdigest() == c['input_sha256']
            gold, actual = prepare(y, s, c['pattern'])
            verify_regions(gold, actual, c['certificate'])
            if c['case_id'] in certs:
                assert certs[c['case_id']] == c['certificate']
            certs[c['case_id']] = c['certificate']
            checks += 1
            if c['method'] == 'smt_all_regions':
                assert c['algorithm_stats']['residual_result'] == 'unsat'
        assert checks == 12 and len(certs) == 6
        for case, c in certs.items():
            for method in ['partition', 'smt_all_regions']:
                group = [r for r in raw if r['case_id'] == case and r['method'] == method]
                assert sorted((int(r['replicate']) for r in group)) == [0, 1, 2]
                for r in group:
                    assert int(r['components']) == len(c['divergent_regions']) and r['psc_exact'] == c['psc_exact'] and np.isclose(float(r['total_checked_ms']), sum((float(r[k]) for k in ['preparation_ms', 'producer_serialization_ms', 'checker_ms'])), rtol=1e-12)
        result = {'status': 'PASS', 'prior_v5_final_stages': 23, 'significance_workloads_reconciled': len(rr), 'decimal_policy_resolutions_checked': [2, 3, 4, 6], 'scipy_certificates_replayed': len(sr), 'scipy_affected_policy_divergent': int(div), 'scipy_grid_detections': int(grid), 'scipy_snapshot_detections': int(snapshot), 'additional_documented_defects': 1, 'larger_g_tasks': 6, 'larger_g_certificates_replayed': checks, 'larger_g_timing_records_reconciled': len(raw)}
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v6'] = _make_validate_v6()

def _make_validate_v7():
    """Audit query evidence, exact prior-release evidence and interface refusals."""
    from pathlib import Path
    from fractions import Fraction as F
    import json, csv, hashlib, copy
    from policy_domain_query import answer, verified_answer
    from domain_query_study import queries
    Q = Path(__file__).resolve().parent

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def main():
        R = Q / 'results/v7'
        prior = Q / 'evidence/V6_FINAL_RELEASE_EVIDENCE'
        p = read(prior / 'RELEASE_VERIFICATION.json')
        assert p['status'] == 'PASS' and len(p['stages']) == 27 and all((s['exit_code'] == 0 for s in p['stages']))
        assert p['archive_sha256_before'] == p['archive_sha256_after'] == 'ec708e725b6ee0f369c156ddaec401f6bdcc8d8ad0681d1e8026638096128de0'
        for name, digest in read(prior / 'EVIDENCE_MANIFEST.json').items():
            assert sha(prior / name) == digest
        summary = read(R / 'domain_query_summary.json')
        assert summary['status'] == 'PASS' and summary['smt_unknown'] == 0
        assert summary['study_source_sha256'] == sha(Q / 'domain_query_study.py') and summary['query_source_sha256'] == sha(Q / 'policy_domain_query.py')
        rows = list(csv.DictReader((R / 'domain_query_results.csv').open(encoding='utf-8')))
        protocol = dict(queries())
        assert len(rows) == 288 and len({(r['case_id'], r['query']) for r in rows}) == 288
        for row in rows:
            w = read(Q / 'results/v6/scipy_defect_certificates' / (row['case_id'] + '_affected.json'))
            q = protocol[row['query']]
            r = answer(w['certificate'], q)
            assert r['affected'] == (row['affected'] == 'True') == (row['smt_verdict'] == 'sat')
            assert row['certificate_witness'] == (r['witness'] or '') and row['affected_count'] == str(r.get('affected_count', ''))
            if int(row['direct_policies']):
                assert int(row['direct_affected']) == r['affected_count'] and int(row['direct_policies']) == r['allowed_count']
            assert float(row['certificate_query_ms']) >= 0 and float(row['smt_build_solve_ms']) >= 0
        assert sum((int(r['direct_policies']) for r in rows)) == summary['direct_policies_enumerated']
        for group in summary['by_query']:
            selected = [r for r in rows if r['query'] == group['query']]
            assert len(selected) == 36 and group['affected_workloads'] == sum((r['affected'] == 'True' for r in selected))
            if group['affected_policy_workload_pairs'] is not None:
                assert group['affected_policy_workload_pairs'] == sum((int(r['affected_count']) for r in selected))
        w = read(Q / 'results/v6/scipy_defect_certificates/upstream_int8_affected.json')
        q = protocol['declared_three']
        assert verified_answer(w, q)['verification']['verified']
        bad = copy.deepcopy(w)
        bad['actual_scores'][0] += 0.125
        try:
            verified_answer(bad, q)
        except AssertionError:
            pass
        else:
            raise AssertionError('Tampered input was accepted')
        result = {'status': 'PASS', 'prior_v6_exact_stages': 27, 'prior_v6_archive_sha256': p['archive_sha256_before'], 'query_answers_reconciled': len(rows), 'direct_policy_checks': summary['direct_policies_enumerated'], 'smt_answers_agree': 288, 'tampered_input_rejected_before_query': True, 'scope': 'Local controlled functional validation, not independent developer evaluation or new bug corpus'}
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v7'] = _make_validate_v7()

def _make_validate_v8():
    """Reconcile reuse costs, saved query answers and inherited-source bindings."""
    from pathlib import Path
    from fractions import Fraction as F
    import csv, json, hashlib, statistics
    import numpy as np
    from reuse_cost_study import CASE_IDS, BATCHES, REPEATS, plans, direct_answer
    from scipy_documented_defect import functions, cases
    from independent_oracle import candidates, select
    from policy_exact import DEFAULT
    from policy_domain_query import contains
    Q = Path(__file__).resolve().parent

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def rows(p):
        return list(csv.DictReader(p.open(encoding='utf-8')))

    def main():
        R = Q / 'results/v8'
        prior = Q / 'evidence/V7_FINAL_RELEASE_EVIDENCE'
        p = read(prior / 'RELEASE_VERIFICATION.json')
        assert p['status'] == 'PASS' and len(p['stages']) == 29 and all((s['exit_code'] == 0 for s in p['stages']))
        assert p['archive_sha256_before'] == p['archive_sha256_after'] == 'a14ac1fc458b1b76e8a6cc25031723597648045dcaae866fd46a9b6a0f806d9a'
        for name, digest in read(prior / 'EVIDENCE_MANIFEST.json').items():
            assert sha(prior / name) == digest
        raw = rows(R / 'reuse_raw.csv')
        groups = rows(R / 'reuse_summary.csv')
        summary = read(R / 'reuse_cost_summary.json')
        protocol = read(R / 'reuse_protocol.json')
        saved_plans = read(R / 'reuse_query_plans.json')
        assert len(raw) == 720 and len(groups) == 144 and (summary['source_sha256'] == sha(Q / 'reuse_cost_study.py'))
        assert summary['status'] == 'PASS' and summary['smt_unknown'] == 0 and (summary['matched_answers'] == 30420)
        assert protocol['case_ids'] == CASE_IDS and protocol['batch_sizes'] == BATCHES and (protocol['repetitions'] == REPEATS)
        assert len({(r['case_id'], r['kind'], r['batch'], r['replicate'], r['method']) for r in raw}) == 720
        for r in raw:
            phase = [float(r[k]) for k in ['setup_ms', 'queries_ms', 'total_ms']]
            assert all((v >= 0 for v in phase)) and abs(phase[0] + phase[1] - phase[2]) < 1e-08
            output = R / 'reuse_outputs' / r['output_file']
            assert sha(output) == r['output_sha256']
            out = read(output)
            assert len(out) == int(r['batch'])
            key = f"{r['case_id']}__{r['kind']}__b{r['batch']}"
            plan = saved_plans[key]
            assert [v['affected'] for v in out] == plan['expected'] and int(r['affected_queries']) == sum(plan['expected'])
        for r in groups:
            selected = [v for v in raw if all((v[k] == r[k] for k in ['case_id', 'kind', 'batch', 'method']))]
            assert len(selected) == 5 and {int(v['replicate']) for v in selected} == set(range(5))
            for phase in ['setup_ms', 'queries_ms', 'total_ms']:
                values = [float(v[phase]) for v in selected]
                assert float(r['median_' + phase]) == statistics.median(values)
                assert float(r['iqr_' + phase]) == float(np.quantile(values, 0.75) - np.quantile(values, 0.25))
        lookup = {(r['case_id'], r['kind'], int(r['batch']), r['method']): float(r['median_total_ms']) for r in groups}
        for row in summary['observed_crossings']:
            name, kind, other = (row['case_id'], row['kind'], row['comparator'])
            expected = next((b for b in BATCHES if all((lookup[name, kind, t, 'checked_certificate'] < lookup[name, kind, t, other] for t in BATCHES if t >= b))), None)
            assert expected == row['first_observed_sustained_batch']
        funcs, _, _ = functions()
        source_cases = {v[0]: v for v in cases()}
        checks = 0
        for name in CASE_IDS:
            _, x, scores, y, ids, rec = source_cases[name]
            old = funcs['fixed'](x, scores, kind='nearest')(x)
            new = funcs['affected'](x, scores, kind='nearest')(x)
            a = candidates(y, old, DEFAULT)
            b = candidates(y, new, DEFAULT)
            positive = bool(y.sum())
            breaks = sorted({p for p, k, n, bits in a + b})
            for kind in ['singleton', 'continuous_window']:
                for batch in BATCHES:
                    key = f'{name}__{kind}__b{batch}'
                    plan = saved_plans[key]
                    assert plan['requests'] == plans(kind, batch)
                    truth = [direct_answer(a, b, positive, q, breaks)['affected'] for q in plan['requests']]
                    assert truth == plan['expected']
                    checks += len(truth)
                    for method in ['checked_certificate', 'direct_masks', 'incremental_z3']:
                        for rep in range(5):
                            out = read(R / 'reuse_outputs' / f'{key}__r{rep}__{method}.json')
                            for q, r in zip(plan['requests'], out):
                                if r['witness'] is not None:
                                    v = F(r['witness'])
                                    assert select(a, v, positive, DEFAULT)[2] != select(b, v, positive, DEFAULT)[2]
                                    assert v in map(F, q['values']) if q['kind'] == 'finite' else contains(q, v)
        manifest = read(Q / 'provenance/q2_reference/manifest.json')
        for name, item in manifest['files'].items():
            assert sha(Q / 'provenance/q2_reference' / name) == item['sha256']
        manuscript = (Q / 'provenance/q2_reference/main.tex').read_text(encoding='utf-8')
        assert 'Exact Candidate Frontier Comparison for Decision Regression Testing of Precision-Constrained Selectors' in manuscript
        assert '255' in manuscript and 'proper-prefix' in manuscript and ('B4' in manuscript)
        result = dict(status='PASS', prior_v7_exact_stages=29, raw_measurements_reconciled=720, summary_groups_reconciled=144, unique_case_query_plans_replayed=checks, saved_method_query_answers_reconciled=30420, smt_unknown=0, q2_source_snapshot_hashes_verified=len(manifest['files']), scope='Measured computational reuse, not developer productivity or real production policy requirements; observed crossings may change with host/run.')
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v8'] = _make_validate_v8()

def _make_validate_v9():
    """Reconcile paired API costs and verify the Boolean index's domain semantics."""
    from pathlib import Path
    from fractions import Fraction as F
    import json, csv, hashlib, statistics
    import numpy as np
    from boolean_query_study import METHODS
    from reuse_cost_study import CASE_IDS, BATCHES, plans, direct_answer
    from scipy_documented_defect import functions, cases
    from independent_oracle import candidates, select
    from policy_exact import DEFAULT
    from policy_domain_query import answer, contains
    from domain_query_study import queries
    from verified_boolean_query import VerifiedBooleanIndex
    Q = Path(__file__).resolve().parent

    def read(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def rows(p):
        return list(csv.DictReader(p.open(encoding='utf-8')))

    def allowed(q, value):
        if q['kind'] == 'finite':
            return value in map(F, q['values'])
        return contains(q, value) and (q['kind'] != 'lattice' or (value * 10 ** q['decimal_places']).denominator == 1)

    def main():
        R = Q / 'results/v9'
        prior = Q / 'evidence/V8_FINAL_RELEASE_EVIDENCE'
        report = read(prior / 'RELEASE_VERIFICATION.json')
        assert report['status'] == 'PASS' and len(report['stages']) == 31 and all((s['exit_code'] == 0 for s in report['stages']))
        assert report['archive_sha256_before'] == report['archive_sha256_after'] == 'c196b5f591c9ee48e9e7d8fa6e72431204e05195b7ee7ed5365ed7742d6735ab'
        certificate_stage = next((s for s in report['stages'] if s['stage'] == 'independent_certificate_audit'))
        assert certificate_stage['exit_code'] == 0
        for name, digest in read(prior / 'EVIDENCE_MANIFEST.json').items():
            assert sha(prior / name) == digest
        summary = read(R / 'boolean_cost_summary.json')
        raw = rows(R / 'boolean_raw.csv')
        groups = rows(R / 'boolean_summary.csv')
        saved_plans = read(R / 'boolean_query_plans.json')
        assert summary['status'] == 'PASS' and summary['smt_unknown'] == 0 and (len(raw) == 960) and (len(groups) == 192) and (summary['matched_method_answers'] == 40560)
        for key, file in [('source_sha256', 'boolean_query_study.py'), ('index_source_sha256', 'verified_boolean_query.py'), ('v8_baseline_source_sha256', 'reuse_cost_study.py')]:
            assert summary[key] == sha(Q / file)
        assert len({(r['case_id'], r['kind'], r['batch'], r['replicate'], r['method']) for r in raw}) == 960
        for row in raw:
            a, b, t = map(float, [row['setup_ms'], row['queries_ms'], row['total_ms']])
            assert min(a, b, t) >= 0 and abs(a + b - t) < 1e-08
            p = R / 'boolean_outputs' / row['output_file']
            assert sha(p) == row['output_sha256']
            out = read(p)
            key = f"{row['case_id']}__{row['kind']}__b{row['batch']}"
            assert len(out) == int(row['batch']) and [r['affected'] for r in out] == saved_plans[key]['expected']
            assert int(row['affected_queries']) == sum(saved_plans[key]['expected'])
        for row in groups:
            selected = [r for r in raw if all((r[k] == row[k] for k in ['case_id', 'kind', 'batch', 'method']))]
            assert len(selected) == 5 and {int(r['replicate']) for r in selected} == set(range(5))
            for phase in ['setup_ms', 'queries_ms', 'total_ms']:
                values = [float(r[phase]) for r in selected]
                assert float(row['median_' + phase]) == statistics.median(values) and float(row['iqr_' + phase]) == float(np.quantile(values, 0.75) - np.quantile(values, 0.25))
        lookup = {(r['case_id'], r['kind'], int(r['batch']), r['method']): r for r in groups}
        for r in summary['paired_certificate_comparisons']:
            old = lookup[r['case_id'], r['kind'], 128, 'checked_certificate']
            new = lookup[r['case_id'], r['kind'], 128, 'boolean_certificate']
            assert r['query_phase_speedup'] == float(old['median_queries_ms']) / float(new['median_queries_ms'])
            assert r['total_speedup'] == float(old['median_total_ms']) / float(new['median_total_ms'])
        for r in summary['workflow_comparisons']:
            wins = sum((float(lookup[name, r['kind'], r['batch'], 'boolean_certificate']['median_total_ms']) < float(lookup[name, r['kind'], r['batch'], r['comparator']]['median_total_ms']) for name in CASE_IDS))
            assert wins == r['boolean_certificate_faster_total_cases'] and r['assurance_matched'] == (r['comparator'] == 'checked_certificate')
        funcs, _, _ = functions()
        count = 0
        witnesses = 0
        for name, x, scores, y, ids, rec in cases():
            old = funcs['fixed'](x, scores, kind='nearest')(x)
            new = funcs['affected'](x, scores, kind='nearest')(x)
            wrapper = read(Q / 'results/v6/scipy_defect_certificates' / (name + '_affected.json'))
            index = VerifiedBooleanIndex(y, old, new, ids, wrapper['certificate'])
            a = candidates(y, old, DEFAULT)
            b = candidates(y, new, DEFAULT)
            positive = bool(y.sum())
            breaks = sorted({p for p, k, n, bits in a + b})
            for label, q in queries():
                actual = index.query(q)
                expected = answer(wrapper['certificate'], q)
                assert actual['affected'] == expected['affected']
                count += 1
                if actual['witness'] is not None:
                    value = F(actual['witness'])
                    assert allowed(q, value) and select(a, value, positive, DEFAULT)[2] != select(b, value, positive, DEFAULT)[2]
            if name not in CASE_IDS:
                continue
            for kind in ['singleton', 'continuous_window']:
                for batch in BATCHES:
                    key = f'{name}__{kind}__b{batch}'
                    plan = saved_plans[key]
                    assert plan['requests'] == plans(kind, batch)
                    expected = [direct_answer(a, b, positive, q, breaks)['affected'] for q in plan['requests']]
                    assert expected == plan['expected']
                    assert [index.query(q)['affected'] for q in plan['requests']] == expected
                    for method in METHODS:
                        for rep in range(5):
                            out = read(R / 'boolean_outputs' / f'{key}__r{rep}__{method}.json')
                            for q, r in zip(plan['requests'], out):
                                if r['witness'] is not None:
                                    value = F(r['witness'])
                                    assert allowed(q, value) and select(a, value, positive, DEFAULT)[2] != select(b, value, positive, DEFAULT)[2]
                                    witnesses += 1
        result = dict(status='PASS', prior_v8_exact_stages=31, prior_certificate_audit_exit_code=0, raw_measurements_reconciled=960, statistical_groups_reconciled=192, reused_unique_case_query_plans=2028, saved_method_query_answers_reconciled=40560, boolean_existing_domain_queries_replayed=count, saved_rational_witnesses_rechecked=witnesses, smt_unknown=0, scope='Paired certificate API comparison has matched certificate construction/checking obligations; comparisons to direct/SMT are implementation request costs with unequal assurance. No new bug/deployment/developer evidence.')
        (R / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_v9'] = _make_validate_v9()

def _make_validate_external_bindings():
    """Additional explicit provenance checks for each external certificate."""
    from pathlib import Path
    import json, csv, hashlib
    Q = Path(__file__).resolve().parent

    def main():
        source = Q / 'vendor/external_sklearn'
        m = json.loads((source / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
        for rec in m.values():
            for name, meta in rec['files'].items():
                assert hashlib.sha256((source / name).read_bytes()).hexdigest() == meta['sha256']
        variants = {'affected': '1.0.2', 'fixed': '23214_merged'}
        rows = list(csv.DictReader((Q / 'results/v3/external_sut_results.csv').open(encoding='utf-8')))
        for row in rows:
            c = json.loads((Q / row['certificate_file']).read_text(encoding='utf-8'))
            assert c['schema'] == 'external-upstream-candidate-conformance/1' and c['issue'] == 'scikit-learn#23213'
            assert c['case_id'] == row['case_id'] and c['variant'] == row['variant'] and (c['domain'] == ['3/10', '9/10'])
            assert c['historical_binary_execution'] is False
            if row['variant'] == 'installed_current':
                assert c['source_sha256'] is None and c['upstream_commit'] is None
            else:
                rec = m[variants[row['variant']]]
                name = next((n for n in rec['files'] if n.endswith('_ranking.py')))
                assert c['source_sha256'] == rec['files'][name]['sha256'] and c['upstream_commit'] == rec['commit']
        result = {'status': 'PASS', 'external_certificates_source_and_domain_bound': len(rows), 'upstream_snapshots_hash_checked': len(m), 'historical_binary_execution_claimed': False}
        (Q / 'results/v3/external_binding_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    return _Namespace(**locals())

_sections['validate_external_bindings'] = _make_validate_external_bindings()

CHECKS = {'benchmark': 'validate_benchmarks', 'program_results': 'validate_revision', 'program_admission': 'validate_v3', 'complete_regions': 'validate_v4', 'external_project_and_checkers': 'validate_v5', 'documented_defect_and_policy': 'validate_v6', 'allowed_domains': 'validate_v7', 'reuse_costs': 'validate_v8', 'boolean_api': 'validate_v9', 'external_bindings': 'validate_external_bindings'}

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section',choices=tuple(CHECKS),help='Run one check at its original position in the experiment pipeline; omit to run all checks on existing outputs.')
    args=parser.parse_args()
    for name in ([args.section] if args.section else CHECKS):
        print('Checking '+name,flush=True)
        _sections[CHECKS[name]].main()

if __name__ == '__main__':
    main()
