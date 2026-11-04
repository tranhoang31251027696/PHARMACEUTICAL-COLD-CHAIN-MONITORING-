from pathlib import Path
from fractions import Fraction as F
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from complete_region_comparison import intervals_partition,intervals_smt,certificate,verify_regions

def test_full_region_methods_preserve_isolated_domain_endpoint():
    # Largest candidate is feasible only at the lower endpoint of this domain.
    a=[(F(1),3,3,0b111),(F(3,10),3,10,0b1111111111)]
    b=[(F(1),3,3,0b111)]
    x,_=intervals_partition(a,b);y,_=intervals_smt(a,b)
    assert x==y==[{'lo':'3/10','hi':'3/10','left_closed':True,'right_closed':True}]
    c=certificate(a,b,x);assert c['psc_exact']=='0' and c['equivalent'] is False
    verify_regions(a,b,c)

def test_complete_empty_region_has_unsat_residual_and_zero_psc():
    a=[(F(1,2),1,2,3),(F(1),1,1,1)]
    x,stats=intervals_smt(a,a);assert not x and stats['residual_result']=='unsat'
    c=certificate(a,a,x);assert c['equivalent'] and c['psc_exact']=='0'
    verify_regions(a,a,c)
