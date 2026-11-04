"""Query allowed rational policies after independent input-bound verification.

This is conditional reuse of a finite-input certificate, not verification of
arbitrary source or of the application's choice of numerical interface.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,argparse,math
import numpy as np
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'src'))
from streaming_checker import verify

def rational(x):
    if not isinstance(x,(str,int)) or isinstance(x,bool):
        raise ValueError('Policies must be rational strings or integers; binary64 JSON numbers are not this contract')
    return F(x)

def intersection(a,b):
    lo=max(F(a['lo']),F(b['lo']));hi=min(F(a['hi']),F(b['hi']))
    lc=all(lo!=F(r['lo']) or r['left_closed'] for r in [a,b])
    rc=all(hi!=F(r['hi']) or r['right_closed'] for r in [a,b])
    if lo>hi or lo==hi and not(lc and rc):return None
    return dict(lo=str(lo),hi=str(hi),left_closed=lc,right_closed=rc)

def contains(r,x):
    return (x>F(r['lo']) or x==F(r['lo']) and r['left_closed']) and (x<F(r['hi']) or x==F(r['hi']) and r['right_closed'])

def answer(cert,query):
    """Consume cells from an ALREADY verified core certificate; no solver claim."""
    if query.get('semantics')!='rational':raise ValueError('Explicit rational policy semantics required')
    kind=query['kind'];lo,hi=map(F,cert['domain'])
    if kind=='finite':
        values=sorted(set(map(rational,query['values'])))
        if not values or any(x<lo or x>hi for x in values):raise ValueError('Empty or out-of-domain policy set')
        regions=[c for c in cert['cells'] if not c['equal']]
        bad=[x for x in values if any(contains(r,x) for r in regions)]
        return dict(kind=kind,allowed_count=len(values),affected_count=len(bad),affected=bool(bad),witness=str(bad[0]) if bad else None,affected_values=list(map(str,bad)))
    if kind not in ['interval','lattice']:raise ValueError('Unsupported policy domain')
    a,b=rational(query['lo']),rational(query['hi'])
    if not lo<=a<=b<=hi:raise ValueError('Policy domain outside verified domain')
    for key in ['left_closed','right_closed']:
        if type(query.get(key)) is not bool:raise ValueError('Explicit Boolean endpoint ownership required')
    domain=dict(lo=str(a),hi=str(b),left_closed=query['left_closed'],right_closed=query['right_closed'])
    if a==b and not(query['left_closed'] and query['right_closed']):raise ValueError('Empty interval')
    parts=[r for c in cert['cells'] if not c['equal'] if (r:=intersection(c,domain)) is not None]
    result=dict(kind=kind,affected=bool(parts),witness=None,divergent_intersections=parts)
    if kind=='interval':
        if parts:
            r=parts[0];result['witness']=r['lo'] if r['left_closed'] else str((F(r['lo'])+F(r['hi']))/2)
        return result
    digits=query['decimal_places']
    if type(digits) is not int or not 0<=digits<=12:raise ValueError('decimal_places must be an integer from 0 to 12')
    scale=10**digits
    def bounds(r):
        a=F(r['lo'])*scale;b=F(r['hi'])*scale;l=math.ceil(a);h=math.floor(b)
        if l==a and not r['left_closed']:l+=1
        if h==b and not r['right_closed']:h-=1
        return l,h
    l,h=bounds(domain);result['allowed_count']=max(0,h-l+1)
    if not result['allowed_count']:raise ValueError('No lattice policy in requested domain')
    blocks=[(l,h) for r in parts if (pair:=bounds(r)) and (l:=pair[0])<=(h:=pair[1])]
    result['affected_count']=sum(h-l+1 for l,h in blocks);result['affected']=bool(blocks)
    result['witness']=str(F(blocks[0][0],scale)) if blocks else None
    return result

def verified_answer(wrapper,query):
    audit=verify(np.array(wrapper['labels']),np.array(wrapper['reference_scores']),np.array(wrapper['actual_scores']),wrapper['ids'],wrapper['certificate'])
    return dict(verification=audit,query=query,result=answer(wrapper['certificate'],query),scope='Frozen inputs and exact rational policy contract; no deployment inference')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--query',type=Path,required=True);a=p.parse_args()
    print(json.dumps(verified_answer(json.loads(a.certificate.read_text(encoding='utf-8')),json.loads(a.query.read_text(encoding='utf-8'))),indent=2))
if __name__=='__main__':main()
