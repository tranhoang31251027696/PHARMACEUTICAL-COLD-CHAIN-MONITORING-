from fractions import Fraction as F
import pytest
from policy_domain_query import answer,intersection

def cert():
    return {'domain':['0','1'],'cells':[dict(lo='1/2',hi='1/2',left_closed=True,right_closed=True,equal=False)]}

def test_singleton_affects_finite_lattice_despite_zero_length():
    q=dict(semantics='rational',kind='lattice',lo='0',hi='1',left_closed=True,right_closed=True,decimal_places=2)
    r=answer(cert(),q);assert r['affected_count']==1 and r['allowed_count']==101 and r['witness']=='1/2'

def test_open_boundary_excludes_point():
    q=dict(semantics='rational',kind='interval',lo='1/2',hi='1',left_closed=False,right_closed=True)
    assert not answer(cert(),q)['affected']

def test_numeric_semantics_and_domain_fail_closed():
    for q in [dict(kind='finite',semantics='binary64',values=['0.5']),dict(kind='finite',semantics='rational',values=[0.5]),dict(kind='finite',semantics='rational',values=['2'])]:
        with pytest.raises(ValueError):answer(cert(),q)

def test_finite_set_deduplication():
    r=answer(cert(),dict(kind='finite',semantics='rational',values=['1/2','0.5','0']))
    assert r['allowed_count']==2 and r['affected_values']==['1/2']
