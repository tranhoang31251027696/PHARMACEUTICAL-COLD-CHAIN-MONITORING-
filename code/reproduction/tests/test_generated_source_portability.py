"""The source writer must bind the executed text to portable on-disk bytes."""
from pathlib import Path
import importlib.util,hashlib,json
import pytest

def test_generated_sources_from_crlf_input_and_tamper_detection(tmp_path):
    q=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('portable_program_writer',q/'program_evaluation.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    (tmp_path/'src').mkdir()
    source=(q/'src/selector_program.py').read_text(encoding='utf-8')
    (tmp_path/'src/selector_program.py').write_bytes(source.replace('\n','\r\n').encode())
    module.Q=tmp_path;generated=module.modules()
    hashes={}
    for name,(_,digest) in generated.items():
        p=tmp_path/'results/v2/program_sources'/f'{name}.py'
        assert b'\r' not in p.read_bytes()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
        hashes[p.relative_to(tmp_path).as_posix()]=digest
    (tmp_path/'provenance').mkdir()
    (tmp_path/'provenance/v11_source_bindings.json').write_text(json.dumps({'files':hashes,'generated_lf_sources':list(hashes)}))
    spec=importlib.util.spec_from_file_location('portable_source_audit',q/'build_manuscript.py')
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    source_audit=audit.source_audit
    assert source_audit(tmp_path,'')['status']=='PASS'
    victim=tmp_path/next(iter(hashes));victim.write_bytes(victim.read_bytes()+b'# tamper\n')
    with pytest.raises(AssertionError,match='Source binding mismatch'):source_audit(tmp_path,'')
