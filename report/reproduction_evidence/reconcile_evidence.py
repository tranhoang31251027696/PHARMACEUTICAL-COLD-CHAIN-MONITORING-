"""Reconcile existing V11 evidence without rewriting the frozen research ZIP.

Uses only the Python standard library. Run from any directory; no pipeline rerun.
Every changed field is retained, including timing-derived changes and environment
status changes. Unknown differences fail closed before packaging.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import io
import json
import math
import shutil
import statistics
import xml.etree.ElementTree as ET
import zipfile

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'src/release_tools').is_dir() and (p / 'SUBMISSION_PACKAGE').is_dir()), Path.cwd())
EVIDENCE = ROOT / 'outputs/V11/FINAL_RELEASE_EVIDENCE'
RUN = ROOT / 'outputs/V11/final_verified_run/artifact'
ARCHIVE = ROOT / 'SUBMISSION_PACKAGE/Reproducibility_Artifact.zip'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def changes(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b:
                yield path + '/' + k, a.get(k), b.get(k)
            else:
                yield from changes(a[k], b[k], path + '/' + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield path + '/length', len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from changes(x, y, path + '/' + str(i))
    elif a != b:
        yield path, a, b


def category(name, path):
    key = path.rsplit('/', 1)[-1]
    if key.endswith('_ms') or key.endswith('_mib') or key == 'elapsed_seconds':
        return 'timing_or_memory'
    if name in ('results/v8/reuse_cost_summary.json', 'results/v9/boolean_cost_summary.json') and key in (
        'first_observed_sustained_batch', 'query_phase_speedup', 'total_speedup',
        'boolean_certificate_faster_total_cases'):
        return 'timing_derived_result'
    if name == 'results/benchmark_validation.json' and path.startswith(('/raw_record_sha256/', '/measurement_source_sha256/')):
        return 'provenance_hash'
    if key == 'pytest_tests':
        return 'test_inventory'
    if name == 'results/summary.json' and (path.startswith('/environment/') or path == '/frozen_input_generation_environment'):
        return 'environment_metadata'
    if key in ('started_utc', 'ended_utc', 'source_module_path', 'runtime_python'):
        return 'environment_metadata'
    if name == 'results/v4/onboarding_summary.json' and path == '/second_project/status':
        return 'runtime_compatibility_status'
    if name == 'results/cli_integration_checks.json' and key == 'output':
        return 'environment_metadata'
    return 'UNRESOLVED'


def xml_record(data):
    root = ET.fromstring(data)
    # Preserve all semantic test identity/outcomes. Strip only measured timing,
    # execution timestamp, host and diagnostic streams (retained in originals).
    def node(e):
        return {'tag': e.tag,
                'attributes': {k: v for k, v in e.attrib.items()
                               if k not in ('time', 'timestamp', 'hostname')},
                'text': (e.text or '').strip(),
                'children': [node(c) for c in e if c.tag not in ('system-out', 'system-err')]}
    return node(root)


def verify_performance_derivations(read):
    """Recompute the changing V8/V9 performance claims from each record's CSVs."""
    checked = 0
    for version, stem in [('v8', 'reuse'), ('v9', 'boolean')]:
        prefix = 'results/' + version + '/'
        raw = list(csv.DictReader(io.StringIO(read(prefix + stem + '_raw.csv').decode('utf-8-sig'))))
        groups = list(csv.DictReader(io.StringIO(read(prefix + stem + '_summary.csv').decode('utf-8-sig'))))
        summary = json.loads(read(prefix + stem + '_cost_summary.json'))
        lookup = {(r['case_id'], r['kind'], int(r['batch']), r['method']): r for r in groups}
        cases = sorted({r['case_id'] for r in groups})
        for row in groups:
            selected = [r for r in raw if all(r[k] == row[k] for k in ('case_id', 'kind', 'batch', 'method'))]
            assert len(selected) == 5
            for phase in ('setup_ms', 'queries_ms', 'total_ms'):
                values = sorted(float(r[phase]) for r in selected)
                assert math.isclose(float(row['median_' + phase]), statistics.median(values), rel_tol=1e-12)
                assert math.isclose(float(row['iqr_' + phase]), values[3] - values[1], rel_tol=1e-12, abs_tol=1e-12)
        if version == 'v8':
            for row in summary['observed_crossings']:
                batches = summary['batch_sizes']
                def value(batch, method):
                    return float(lookup[row['case_id'], row['kind'], batch, method]['median_total_ms'])
                expected = next((b for b in batches if all(value(t, 'checked_certificate') < value(t, row['comparator']) for t in batches if t >= b)), None)
                assert expected == row['first_observed_sustained_batch']
                checked += 1
        else:
            for row in summary['paired_certificate_comparisons']:
                key = row['case_id'], row['kind'], row['batch']
                old, new = lookup[(*key, 'checked_certificate')], lookup[(*key, 'boolean_certificate')]
                assert row['query_phase_speedup'] == float(old['median_queries_ms']) / float(new['median_queries_ms'])
                assert row['total_speedup'] == float(old['median_total_ms']) / float(new['median_total_ms'])
                checked += 1
            for row in summary['workflow_comparisons']:
                expected = sum(float(lookup[c, row['kind'], row['batch'], 'boolean_certificate']['median_total_ms']) < float(lookup[c, row['kind'], row['batch'], row['comparator']]['median_total_ms']) for c in cases)
                assert expected == row['boolean_certificate_faster_total_cases']
                checked += 1
    return checked


def main():
    if not __debug__:
        raise RuntimeError('Reconciliation requires assertions enabled; do not use Python -O')
    global ARCHIVE, RUN, EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ARCHIVE, help='Frozen Artifact ZIP')
    parser.add_argument('--run-root', type=Path, default=RUN, help='Recorded execution root containing results/')
    parser.add_argument('--evidence-dir', type=Path, default=EVIDENCE, help='Extracted detached evidence directory')
    parser.add_argument('--regenerated-outputs', type=Path, help='Bundled regenerated_outputs.zip (audit mode)')
    parser.add_argument('--check-only', action='store_true', help='Read-only audit; no original workspace or pipeline dependencies needed with --regenerated-outputs')
    args = parser.parse_args()
    ARCHIVE, RUN, EVIDENCE = args.archive.resolve(), args.run_root.resolve(), args.evidence_dir.resolve()
    if args.regenerated_outputs and not args.check_only:
        parser.error('--regenerated-outputs requires --check-only')
    delta = zipfile.ZipFile(args.regenerated_outputs) if args.regenerated_outputs else None
    original_sha = sha(ARCHIVE.read_bytes())
    digests = json.loads((EVIDENCE / 'output_digests.json').read_text())
    verification = json.loads((EVIDENCE / 'RELEASE_VERIFICATION.json').read_text())
    assert original_sha == verification['archive_sha256_before'] == verification['archive_sha256_after']
    # Validate old detached evidence before updating its coverage.
    old_manifest = json.loads((EVIDENCE / 'EVIDENCE_MANIFEST.json').read_text())
    assert {p.relative_to(EVIDENCE).as_posix() for p in EVIDENCE.rglob('*') if p.is_file()} == set(old_manifest) | {'EVIDENCE_MANIFEST.json'}
    for name, digest in old_manifest.items():
        assert sha((EVIDENCE / name).read_bytes()) == digest, name
    records = []
    with zipfile.ZipFile(ARCHIVE) as frozen:
        def read_run(name):
            if delta is not None:
                return delta.read(name) if name in delta.namelist() else frozen.read(name)
            return (RUN / name).read_bytes()
        if delta is not None:
            expected = {n for n, h in digests.items() if n not in frozen.namelist() or sha(frozen.read(n)) != h}
            assert len(delta.namelist()) == len(set(delta.namelist()))
            assert set(delta.namelist()) == expected, 'Delta membership does not match differing/new output digests'
            assert delta.testzip() is None
            for n in expected:
                assert sha(delta.read(n)) == digests[n], 'Delta digest mismatch: ' + n
        performance_checks = {'frozen_claims_recomputed': verify_performance_derivations(frozen.read),
                              'execution_claims_recomputed': verify_performance_derivations(read_run)}
        members = set(frozen.namelist())
        manifest = json.loads(frozen.read('ARTIFACT_MANIFEST.json'))
        assert members == set(manifest) | {'ARTIFACT_MANIFEST.json'}
        for name, digest in manifest.items():
            assert sha(frozen.read(name)) == digest, name
        for name, digest in sorted(digests.items()):
            if name in members and sha(frozen.read(name)) == digest:
                records.append({'file': name, 'comparison': 'byte_identical'})
                continue
            data = read_run(name)
            assert sha(data) == digest, 'Extraction no longer matches execution evidence: ' + name
            if name not in members:
                assert name.startswith('results/run_all_'), name
                records.append({'file': name, 'comparison': 'new_execution_record', 'execution_sha256': digest})
                continue
            before = frozen.read(name)
            if name.endswith('.json'):
                a, b = json.loads(before), json.loads(data)
                if name == 'results/cli_integration_checks.json':
                    for obj in (a, b):
                        for check in obj['checks']:
                            if check.get('stdout', '').startswith('{'):
                                check['stdout'] = json.loads(check['stdout'])
            elif name.endswith('.csv'):
                a = list(csv.DictReader(io.StringIO(before.decode('utf-8-sig'))))
                b = list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
            elif name.endswith('.xml'):
                a, b = xml_record(before), xml_record(data)
                old_tests = {(t.get('classname'), t.get('name')): t for t in ET.fromstring(before).iter('testcase')}
                new_tests = {(t.get('classname'), t.get('name')): t for t in ET.fromstring(data).iter('testcase')}
                assert set(old_tests) <= set(new_tests)
                assert all(xml_record(ET.tostring(t)) == xml_record(ET.tostring(new_tests[k])) for k, t in old_tests.items())
                added = sorted(k[1] for k in set(new_tests) - set(old_tests))
                assert added == (['test_generated_sources_from_crlf_input_and_tamper_detection'] if name == 'results/pytest.xml' else [])
                assert not any(t.tag in ('failure', 'error', 'skipped') for t in ET.fromstring(data).iter())
                records.append({'file': name, 'comparison': 'changed', 'categories': ['test_inventory', 'xml_execution_metadata'] if added else ['xml_execution_metadata'],
                                'frozen_sha256': sha(before), 'execution_sha256': digest,
                                'old_tests': len(old_tests), 'new_tests': len(new_tests), 'added_tests': added,
                                'shared_test_semantics_equal': True})
                continue
            else:
                raise AssertionError('Unclassified file: ' + name)
            diffs = [{'path': p, 'frozen': x, 'execution': y, 'category': category(name, p)} for p, x, y in changes(a, b)]
            assert diffs and all(d['category'] != 'UNRESOLVED' for d in diffs), (name, [d for d in diffs if d['category'] == 'UNRESOLVED'][:3])
            records.append({'file': name, 'comparison': 'changed', 'frozen_sha256': sha(before),
                            'execution_sha256': digest, 'categories': sorted({d['category'] for d in diffs}), 'differences': diffs})
        frozen_count = json.loads(frozen.read('results/artifact_verification.json'))['pytest_tests']
        assert frozen_count == 41
        assert json.loads(read_run('results/artifact_verification.json'))['pytest_tests'] == 42
        assert '42 passed' in (EVIDENCE / 'stage_logs/run_all_pytest.log').read_text()
        # The frozen source snapshot is current; its old validator hash is stale.
        source_name = 'results/execution_source_snapshot/run_experiments.py'
        provenance = {'source_snapshot_sha256': sha(frozen.read(source_name)),
                      'frozen_validator_recorded_sha256': json.loads(frozen.read('results/benchmark_validation.json'))['measurement_source_sha256'][source_name],
                      'execution_validator_recorded_sha256': json.loads(read_run('results/benchmark_validation.json'))['measurement_source_sha256'][source_name]}
        assert provenance['source_snapshot_sha256'] == provenance['execution_validator_recorded_sha256']
    counts = Counter(r['comparison'] for r in records)
    assert dict(counts) == {'changed': 97, 'byte_identical': 2853, 'new_execution_record': 34}, counts
    result = {'scope': 'Existing V11 frozen snapshot versus recorded exact-archive execution; no new pipeline execution.',
              'artifact_sha256': original_sha, 'counts': dict(counts), 'total': len(records),
              'all_changed_fields_classified': True, 'byte_for_byte_reproduction': False,
              'test_count': {'frozen_snapshot': frozen_count, 'recorded_execution': 42,
                             'added_test': 'test_generated_sources_from_crlf_input_and_tamper_detection'},
              'performance_derivation_checks': performance_checks,
              'source_provenance_reconciliation': provenance, 'outputs': records}
    if args.check_only:
        assert result == json.loads((EVIDENCE / 'SEMANTIC_RECONCILIATION.json').read_text()), 'Recomputed reconciliation differs from distributed report'
        if delta is not None:
            delta.close()
        print(json.dumps({'status': 'PASS', 'read_only': True, 'counts': dict(counts),
                          'all_97_differences_recomputed_from_distributed_bytes': delta is not None,
                          'pipeline_rerun': False}, indent=2))
        return
    (EVIDENCE / 'SEMANTIC_RECONCILIATION.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    lines = ['# Frozen snapshot and execution reconciliation (V11)', '',
             'External read-only audit: extract Evidence ZIP to any directory, then run `python reconcile_evidence.py --archive /path/to/Reproducibility_Artifact.zip --evidence-dir /path/to/extracted-evidence --regenerated-outputs /path/to/extracted-evidence/regenerated_outputs.zip --check-only`. Python standard library only; no pinned research environment, pipeline rerun or original author directory layout is needed. Quote paths containing spaces.', '',
             'regenerated_outputs.zip distributes the exact 97 changed outputs plus 34 new logs/status records. Its outer hash is bound by EVIDENCE_MANIFEST.json; each inner member is separately checked against output_digests.json. The auditor reads byte-identical outputs from the frozen Artifact, recomputes field comparisons and performance derivations, and requires the result to equal the distributed JSON report. SHA binding alone is not a semantic audit; this command performs the additional comparisons on the distributed bytes. It does not independently regenerate the research outputs or prove their provenance beyond the supplied execution records.', '',
             'The immutable Artifact ZIP is unchanged. This is an explanation of existing execution evidence, not a new release or pipeline run.', '',
             'Of 2,982 output digests, 2,851 match the frozen snapshot byte for byte, 97 differ, and 34 are new run_all logs/status records. This does not establish byte-for-byte reproduction of every output.', '',
             'All 97 differing files were compared field by field (CSV row order retained; JSON keys compared recursively). XML shared test identities/outcomes were checked after excluding timing, timestamp, host and diagnostic streams. Every changed field is recorded in SEMANTIC_RECONCILIATION.json; no unclassified field is accepted.', '',
             'Diagnostic values, memberships, endpoints and certificate hashes in the compared structured files are unchanged. Timing and memory measurements change, and so do timing-derived speedups, faster-case counts and observed break-even batches; those performance results must not be presented as identical. No new general algorithm or broader detection superiority is inferred.', '',
             'V8/V9 summary medians and IQRs were recomputed from their raw CSV rows in both snapshots. All 60 break-even/speedup/faster-case claims per snapshot were then recomputed from those summaries and agree with their own measurement records.', '',
             '## Test inventory', '',
             'The bundled results/artifact_verification.json and streaming verification summary describe an older 41-test output snapshot. The frozen source includes the additional test_generated_sources_from_crlf_input_and_tamper_detection test. Its exact-archive execution records 42 core tests in results/pytest.xml and stage_logs/run_all_pytest.log. The 41 shared tests retain their outcomes; the added test passes. Both upstream XML records contain 18 passing tests. Historical snapshot counts are retained rather than rewritten as if freshly executed.', '',
             '## Environment and provenance', '',
             'Python 3.12.10 versus 3.13.18 changes onboarding status from UNSUPPORTED_RUNTIME to RUNTIME_COMPATIBLE_NOT_EVALUATED. In this onboarding record, full_package_executed and policy_certificate_issued remain false; runtime compatibility is not evidence of full-package execution. CLI stdout differs only in output paths after parsing its embedded JSON.', '',
             'The frozen benchmark validator contains an older recorded run_experiments.py source hash even though the bundled execution_source_snapshot already has the current bytes. The regenerated validator corrects that provenance hash to match the actual snapshot. Raw benchmark hashes also change with measurement data. Both old and corrected hashes are retained in the JSON reconciliation.', '',
             '## Changed files', '', '| File | Classified differences |', '| --- | --- |']
    for rec in records:
        if rec['comparison'] == 'changed':
            lines.append('| `' + rec['file'] + '` | ' + ', '.join(rec['categories']) + ' |')
    (EVIDENCE / 'SEMANTIC_RECONCILIATION.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    readme = ('# Detached V11 execution evidence\n\n'
              'Artifact SHA-256: ' + original_sha + '\n\n'
              'Local Windows execution: 33 stages, 42 core tests and 18 upstream tests. Not native Linux or independent institutional reproduction.\n\n'
              'The Artifact contains historical 41-test result snapshots; see SEMANTIC_RECONCILIATION.md and its machine-readable JSON for test inventory, all 97 changed output files, and 34 new execution records. Only 2,853 of 2,984 output digests are byte-identical to the snapshot.\n\n'
              'External audit without the original workspace or pinned environment: extract this ZIP, then run (Python standard library only):\n\n'
              '```shell\npython reconcile_evidence.py --archive "../Reproducibility_Artifact.zip" --evidence-dir "." --regenerated-outputs "regenerated_outputs.zip" --check-only\n```\n\n'
              'Adjust --archive and --evidence-dir to your chosen paths. The command is read-only. --run-root can instead point to an existing recorded extraction containing results/. The compressed outputs include all 97 changed files and 34 new logs/status records; their digests, field comparisons and timing-derived claims are rechecked, not merely trusted from the reconciliation JSON. This verifies supplied records, not an independent research execution. Do not use Python -O.\n\n'
              'The scientific scope is exact policy-aware regression diagnosis: localization, endpoint correctness and independently checked certificates. Both documented upstream defects have all affected workloads detected by the thirteen-point grid; no additional external detection advantage or new general verification algorithm is claimed.\n\n'
              'Main/Supplement PDF and DOCX are separate submission files, outside both reproducibility ZIPs. See SUBMISSION_PACKAGE/README.md for submission scope.\n\n'
              'EVIDENCE_MANIFEST.json covers every payload member, including this README and verify_release.py. The manifest excludes itself to avoid self-reference. Reconciliation describes existing evidence and does not change the recorded archive hash or original execution outputs.\n')
    (EVIDENCE / 'README.md').write_text(readme, encoding='utf-8')
    with zipfile.ZipFile(EVIDENCE / 'regenerated_outputs.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for rec in records:
            if rec['comparison'] != 'byte_identical':
                z.write(RUN / rec['file'], rec['file'])
    shutil.copy2(Path(__file__), EVIDENCE / Path(__file__).name)
    shutil.copy2(ROOT / 'src/release_tools/verify_release.py', EVIDENCE / 'verify_release.py')
    manifest = {p.relative_to(EVIDENCE).as_posix(): sha(p.read_bytes()) for p in sorted(EVIDENCE.rglob('*')) if p.is_file() and p.name != 'EVIDENCE_MANIFEST.json'}
    (EVIDENCE / 'EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    target = ROOT / 'SUBMISSION_PACKAGE/Reproducibility_Evidence.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(EVIDENCE.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(EVIDENCE).as_posix())
    mirror = ROOT / 'GITHUB_UPLOAD/report/reproduction_evidence'
    for p in EVIDENCE.rglob('*'):
        if p.is_file():
            dest = mirror / p.relative_to(EVIDENCE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
    assert sha(ARCHIVE.read_bytes()) == original_sha
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(manifest) | {'EVIDENCE_MANIFEST.json'}
        for name, digest in manifest.items():
            assert sha(z.read(name)) == digest, name
    print(json.dumps({'status': 'PASS', 'counts': dict(counts), 'manifest_payload_files': len(manifest), 'artifact_unchanged': True}, indent=2))


if __name__ == '__main__':
    main()
