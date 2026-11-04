from pathlib import Path
import sys,itertools,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np,pytest
from policy_exact import compare_policies,DEFAULT
from independent_oracle import verify as legacy
from streaming_checker import verify

def test_streamed_checker_all_binary_cases_through_n3_and_mutant_specs():
    specs=[{},dict(family='gt'),dict(family='drop_group'),dict(family='split_ties'),dict(precision='strict'),dict(objective='max_tp_min_n'),dict(count_offset=1)]
    for n in range(1,4):
        for y in itertools.product([0,1],repeat=n):
            for a in itertools.product([0.,1.],repeat=n):
                for b in itertools.product([0.,1.],repeat=n):
                    for spec in specs:
                        c=compare_policies(y,a,b,lo=0,hi=1,new_spec=spec);ids=list(range(n));x=verify(y,a,b,ids,c)
                        assert x['probes']==legacy(y,a,b,ids,c)['probes']

def test_streamed_checker_rejects_tampering_with_every_certified_obligation():
    y=np.array([1,0,1,0,0]);a=np.array([.9,.8,.7,.7,.1]);b=np.array([.9,.7,.8,.7,.1]);ids=list(range(5));base=compare_policies(y,a,b,ids=ids,lo=0,hi=1)
    verify(y,a,b,ids,base)
    mutations=[]
    for key,value in [('input_sha256','0'*64),('critical_values',['0','1']),('equivalent',not base['equivalent']),('psc_exact','99'),('divergent_length','99'),('candidate_counts',[0,0])]:
        c=copy.deepcopy(base);c[key]=value;mutations.append(c)
    for key,value in [('old_n',999),('equal',None),('left_closed',False)]:
        c=copy.deepcopy(base);c['cells'][0][key]=value;mutations.append(c)
    c=copy.deepcopy(base);c['cells']=[c['cells'][0]];mutations.append(c)
    for c in mutations:
        with pytest.raises((AssertionError,KeyError,ValueError)):verify(y,a,b,ids,c)

def test_streamed_checker_preserves_zero_measure_endpoint_difference():
    c=compare_policies([1,0],[1.,0.],[1.,0.],lo='1/2',hi=1,new_spec={'precision':'strict'})
    assert not c['equivalent'] and c['psc_exact']=='0';verify([1,0],[1.,0.],[1.,0.],[0,1],c)
