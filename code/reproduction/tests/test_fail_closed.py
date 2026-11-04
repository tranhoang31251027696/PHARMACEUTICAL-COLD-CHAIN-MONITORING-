from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parents[1])]
import pytest
from adapter_admission import admit_source,admission_result
from program_gate import gate

def test_reviewed_source_admitted_and_complete_gate_conforms():
    source=(Path(__file__).resolve().parents[1]/'src/selector_program.py').read_text(encoding='utf-8')
    assert admit_source(source)['status']=='ADMITTED'
    assert gate(source,[1,0],[1.,0.],['p','n'])['certified']

@pytest.mark.parametrize('alteration',['alpha','state','unknown'])
def test_unreviewed_programs_cannot_receive_certificate(alteration):
    source=(Path(__file__).resolve().parents[1]/'src/selector_program.py').read_text(encoding='utf-8')
    if alteration=='alpha':source=source.replace('key=(k,n)','key=(k,n if alpha > 0 else -n)')
    elif alteration=='state':source+='\nvisits=0\n'
    else:source=source.replace('key=(k,n)','key=(k,n,0)')
    r=admission_result(source);assert r['status']=='UNSUPPORTED' and r['certified'] is False
