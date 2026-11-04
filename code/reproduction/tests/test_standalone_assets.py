from pathlib import Path
import hashlib,json

def test_historical_grid_is_internal_and_hash_bound():
    q=Path(__file__).resolve().parents[1];m=json.loads((q/'inputs/manifest.json').read_text(encoding='utf-8'))
    name='historical/counterfactual_policy_sensitivity_255_configs.csv'
    assert hashlib.sha256((q/'inputs'/name).read_bytes()).hexdigest()==m['assets'][name]

def test_instrumented_phases_preserve_certificate():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
    from policy_exact import compare_policies
    args=([1,0,1],[.9,.5,.2],[.1,.5,.9]);plain=compare_policies(*args);timings={}
    assert compare_policies(*args,stage_timings=timings)==plain
    assert set(timings)=={'construction_ms','witness_ms','sweep_excluding_witness_ms','assembly_and_hash_ms'}
    assert all(v>=0 for v in timings.values())
