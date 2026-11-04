"""Boolean-only rational-domain queries on independently verified evidence.

Construction verifies and freezes an input-bound certificate, then indexes its
maximal unequal components. Queries emit no intersection lists or finite counts.
Bisect and interval union are established techniques, not new verification theory.
"""
from fractions import Fraction as F
from bisect import bisect_left
from dataclasses import dataclass
import copy,math,json,argparse
from pathlib import Path
import numpy as np
from policy_domain_query import rational,verify

def lattice_bounds(a,b,lc,rc,scale):
    low=a*scale;high=b*scale;first=math.ceil(low);last=math.floor(high)
    if first==low and not lc:first+=1
    if last==high and not rc:last-=1
    return first,last

@dataclass(frozen=True,slots=True,init=False)
class VerifiedBooleanIndex:
    _domain:tuple
    _regions:tuple
    _ends:tuple
    input_sha256:str
    verified_probes:int

    def __init__(self,y,old,new,ids,certificate):
        # Freeze after checking copied inputs, so caller mutation cannot change it.
        cert=copy.deepcopy(certificate)
        audit=verify(np.asarray(y).copy(),np.asarray(old).copy(),np.asarray(new).copy(),list(ids),cert)
        regions=[]
        for c in cert['cells']:
            if c['equal']:continue
            lo,hi=F(c['lo']),F(c['hi']);lc,rc=c['left_closed'],c['right_closed']
            if regions and regions[-1][1]==lo and (regions[-1][3] or lc):
                previous=regions.pop();regions.append((previous[0],hi,previous[2],rc))
            else:regions.append((lo,hi,lc,rc))
        ends=tuple(r[1] for r in regions)
        assert all(a<b for a,b in zip(ends,ends[1:]))
        object.__setattr__(self,'_domain',tuple(map(F,cert['domain'])))
        object.__setattr__(self,'_regions',tuple(regions));object.__setattr__(self,'_ends',ends)
        object.__setattr__(self,'input_sha256',cert['input_sha256']);object.__setattr__(self,'verified_probes',audit['probes'])

    def _witness(self,a,b,lc,rc,scale=None):
        i=bisect_left(self._ends,a)
        while i<len(self._regions):
            l,h,left,right=self._regions[i]
            if l>b:break
            low=max(l,a);high=min(h,b)
            closed_low=(low!=l or left) and (low!=a or lc)
            closed_high=(high!=h or right) and (high!=b or rc)
            if low<high or low==high and closed_low and closed_high:
                if scale is None:return low if closed_low else (low+high)/2
                first,last=lattice_bounds(low,high,closed_low,closed_high,scale)
                if first<=last:return F(first,scale)
            i+=1
        return None

    def query(self,query):
        if query.get('semantics')!='rational':raise ValueError('Explicit rational policy semantics required')
        kind=query['kind'];lo,hi=self._domain;witness=None
        if kind=='finite':
            values=sorted(set(map(rational,query['values'])))
            if not values or any(x<lo or x>hi for x in values):raise ValueError('Empty or out-of-domain policy set')
            for value in values:
                witness=self._witness(value,value,True,True)
                if witness is not None:break
        else:
            if kind not in ['interval','lattice']:raise ValueError('Unsupported policy domain')
            a,b=rational(query['lo']),rational(query['hi'])
            if not lo<=a<=b<=hi:raise ValueError('Policy domain outside verified domain')
            lc,rc=query.get('left_closed'),query.get('right_closed')
            if type(lc) is not bool or type(rc) is not bool:raise ValueError('Explicit Boolean endpoint ownership required')
            if a==b and not(lc and rc):raise ValueError('Empty interval')
            scale=None
            if kind=='lattice':
                digits=query['decimal_places']
                if type(digits) is not int or not 0<=digits<=12:raise ValueError('decimal_places must be an integer from 0 to 12')
                scale=10**digits;first,last=lattice_bounds(a,b,lc,rc,scale)
                if first>last:raise ValueError('No lattice policy in requested domain')
            witness=self._witness(a,b,lc,rc,scale)
        return {'affected':witness is not None,'witness':None if witness is None else str(witness)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--query',type=Path,required=True);args=p.parse_args()
    wrapper=json.loads(args.certificate.read_text(encoding='utf-8'));query=json.loads(args.query.read_text(encoding='utf-8'))
    index=VerifiedBooleanIndex(wrapper['labels'],wrapper['reference_scores'],wrapper['actual_scores'],wrapper['ids'],wrapper['certificate'])
    print(json.dumps({'verification':{'input_sha256':index.input_sha256,'probes':index.verified_probes},'query':query,'result':index.query(query),'scope':'Frozen-input verified Boolean answer; no complete intersection list, finite count, source safety or deployment inference'},indent=2))
if __name__=='__main__':main()
