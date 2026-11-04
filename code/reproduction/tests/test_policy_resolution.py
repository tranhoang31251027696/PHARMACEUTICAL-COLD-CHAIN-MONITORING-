from pathlib import Path
from fractions import Fraction as F
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from policy_significance import lattice_hits,quantile

def test_decimal_lattice_respects_zero_measure_points_and_endpoint_ownership():
    point={'lo':'1/2','hi':'1/2','left_closed':True,'right_closed':True}
    assert lattice_hits([point],2)==1
    gap={'lo':'1/2','hi':'51/100','left_closed':False,'right_closed':False}
    assert lattice_hits([gap],2)==0 and lattice_hits([gap],3)==9
    gap['right_closed']=True;assert lattice_hits([gap],2)==1 and lattice_hits([gap],3)==10

def test_quantiles_preserve_exact_fractional_arithmetic():
    assert quantile([F(1,3),F(2,3)],F(1,2))==F(1,2)
    assert quantile([F(1,3)],F(3,4))==F(1,3)
