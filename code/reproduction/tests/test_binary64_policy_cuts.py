from fractions import Fraction as F
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from second_project_evaluation import float_cut,actual,tables,guarded
from independent_oracle import select
from policy_exact import DEFAULT

def test_binary64_boundary_ownership_and_both_neighbor_cells():
    for value in [.3,np.nextafter(.3,np.inf),.5,np.nextafter(.5,np.inf),2/3,.9]:
        cut,closed=float_cut(value);lower=(F.from_float(float(value))+cut)/2;upper=(cut+F.from_float(float(np.nextafter(value,np.inf))))/2
        assert float(lower)==value and float(upper)>value
        assert (float(cut)<=value)==closed

def test_actual_public_selector_matches_float_cell_model_at_narrow_gap():
    y=np.array([1,0,0]);s=np.array([.9,.8,.7]);gold,guard=tables(y,s)
    for cut,closed,k,n,bits in guard:
        for a in [cut,(F(k,n)+cut)/2]:assert actual(y,s,a)==guarded(guard,a)

def test_semantic_difference_can_exist_at_a_representable_binary64_policy():
    y=np.array([1,1,0,0,0]);s=np.array([.9,.8,.7,.6,.5]);gold,guard=tables(y,s);a=F.from_float(.4)
    assert a>F(2,5) and actual(y,s,a)!=select(gold,a,True,DEFAULT)[2]
    assert actual(y,s,a)==guarded(guard,a)
