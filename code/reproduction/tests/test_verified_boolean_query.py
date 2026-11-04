import copy
from pathlib import Path
import sys
from dataclasses import FrozenInstanceError
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from policy_exact import compare_policies,DEFAULT
from verified_boolean_query import VerifiedBooleanIndex

def fixture():
    y=[1,0];scores=[1.,0.];ids=[8,9]
    cert=compare_policies(y,scores,scores,ids=ids,new_spec={**DEFAULT,'precision':'strict'})
    return y,scores,ids,cert

def test_zero_measure_point_and_open_boundaries():
    y,s,ids,c=fixture();assert c['psc_exact']=='0' and not c['equivalent'];index=VerifiedBooleanIndex(y,s,s,ids,c)
    common=dict(semantics='rational',kind='interval',lo='1/2',hi='9/10',left_closed=False,right_closed=True)
    assert not index.query(common)['affected']
    assert index.query(dict(common,left_closed=True))=={'affected':True,'witness':'1/2'}
    assert index.query(dict(common,kind='lattice',lo='3/10',left_closed=True,decimal_places=2))['affected']
    assert not index.query(dict(semantics='rational',kind='finite',values=['0.4','0.6']))['affected']

def test_input_tamper_rejected_and_index_immutable():
    y,s,ids,c=fixture();bad=copy.deepcopy(c);bad['input_sha256']='0'*64
    with pytest.raises(AssertionError):VerifiedBooleanIndex(y,s,s,ids,bad)
    index=VerifiedBooleanIndex(y,s,s,ids,c);c['cells'].clear()
    assert index.query(dict(semantics='rational',kind='finite',values=['1/2']))['affected']
    with pytest.raises(FrozenInstanceError):index.input_sha256='modified'

def test_semantic_and_empty_lattice_refusals():
    y,s,ids,c=fixture();index=VerifiedBooleanIndex(y,s,s,ids,c)
    for q in [dict(semantics='binary64',kind='finite',values=['0.5']),dict(semantics='rational',kind='finite',values=[0.5]),dict(semantics='rational',kind='finite',values=['1']),dict(semantics='rational',kind='lattice',lo='0.401',hi='0.409',left_closed=True,right_closed=True,decimal_places=2)]:
        with pytest.raises(ValueError):index.query(q)

def test_equal_singleton_hole_is_not_merged_away():
    y=[1,0,0,0];old=[1.,.9,.8,.7];new=[1.,.9,.8,.8];ids=list(range(4))
    c=compare_policies(y,old,new,ids=ids,new_spec={**DEFAULT,'precision':'strict','count_offset':1})
    index=VerifiedBooleanIndex(y,old,new,ids,c)
    q=dict(semantics='rational',kind='finite')
    assert not index.query(dict(q,values=['1/2']))['affected']
    assert index.query(dict(q,values=['49/100']))['affected']
    assert index.query(dict(q,values=['51/100']))['affected']
