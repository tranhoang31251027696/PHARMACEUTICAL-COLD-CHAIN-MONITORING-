import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from fractions import Fraction
from itertools import product
from copy import deepcopy
import numpy as np
import pytest
from policy_exact import compare_policies,at,assert_policy_equivalent
from independent_oracle import verify

def check(y,a,b,**kw):
    c=compare_policies(y,a,b,**kw)
    verify(y,a,b,list(range(len(y))),c)
    return c

def test_exhaustive_binary_scores():
    count=0
    for n in range(1,5):
        for y in product([0,1],repeat=n):
            for a in product([0.,1.],repeat=n):
                for b in product([0.,1.],repeat=n):
                    check(y,a,b,lo=0,hi=1);count+=1
    assert count==4680

def test_exhaustive_ternary_scores():
    count=0
    for n in range(1,4):
        for y in product([0,1],repeat=n):
            for a in product([0.,.5,1.],repeat=n):
                for b in product([0.,.5,1.],repeat=n):
                    check(y,a,b,lo='1/7',hi='6/7');count+=1
    assert count==6174

def test_randomized_variants():
    rng=np.random.default_rng(20261029)
    specs=[{}, {'precision':'strict'},{'family':'gt'},{'family':'drop_group'},
           {'family':'split_ties'},{'objective':'max_tp_min_n'},{'count_offset':1}]
    for i in range(1000):
        n=int(rng.integers(2,41));y=rng.integers(0,2,n);a=rng.integers(0,8,n)/7;b=a+rng.choice([0,1e-8,-1e-8],n)
        check(y,a,b,lo=0,hi=1,new_spec=specs[i%len(specs)])

def test_endpoint_only_inequivalence_has_zero_psc():
    c=check([1,0],[1.,0.],[1.,0.],lo='.5',hi=1,new_spec={'precision':'strict'})
    assert not c['equivalent'] and c['psc_exact']=='0'
    assert not at(c,Fraction(1,2))['equal'] and not at(c,1)['equal']
    assert at(c,Fraction(3,4))['equal']

def test_abstention_identity_monotone():
    for y in [[0,0,0],[1,1,1],[0,1,0]]:
        c=check(y,[.1,.2,.2],[1.2,1.4,1.4],lo=0,hi=1)
        assert c['equivalent'] and c['psc_exact']=='0'

@pytest.mark.parametrize('bad', ['winner','coverage','psc','critical','witness','binding','spec'])
def test_tampered_certificate_rejected(bad):
    y=[1,0,1];a=[.9,.5,.2];b=[.1,.6,.9];c=compare_policies(y,a,b,lo=0,hi=1);d=deepcopy(c)
    if bad=='winner':d['cells'][0]['old_n']=100
    if bad=='coverage':d['cells'][0]['left_closed']=False
    if bad=='psc':d['psc_exact']='17/99'
    if bad=='critical':d['critical_values']=[]
    if bad=='witness':next(x for x in d['cells'] if not x['equal'])['witness']['row_id']='forged'
    if bad=='binding':d['input_sha256']='0'*64
    if bad=='spec':d['new_spec']['precision']='strict'
    with pytest.raises(AssertionError):verify(y,a,b,[0,1,2],d)

@pytest.mark.parametrize('args', [([1],[float('nan')],[0]),([2],[0],[0]),([],[],[]),([1,0],[1],[0,1])])
def test_invalid_arrays(args):
    with pytest.raises(ValueError):compare_policies(*args)

def test_id_contract_and_ci_actionable_failure():
    with pytest.raises(ValueError):compare_policies([1,0],[1,0],[1,0],ids=['a','b'],new_ids=['b','a'])
    with pytest.raises(ValueError):compare_policies([1,0],[1,0],[1,0],ids=['a','a'])
    assert_policy_equivalent([1,0],[1,0],[2,0])
    with pytest.raises(AssertionError,match='row_id'):assert_policy_equivalent([1,0],[1,0],[0,1])
