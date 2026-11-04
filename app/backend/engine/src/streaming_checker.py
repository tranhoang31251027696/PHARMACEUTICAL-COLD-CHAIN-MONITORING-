"""Independent certificate consumer with streamed masks and suffix maxima.

No production imports, priority heap, rank-containment or production profile.
Candidate counts use direct threshold masks; only the current winner mask is
packed. Exact suffix-priority maxima answer feasibility queries by bisection.
"""
from fractions import Fraction as F
from bisect import bisect_left,bisect_right
import hashlib,json
import numpy as np

class Family:
    def __init__(self,y,s,spec):
        self.y=y;self.s=s;self.spec=spec;self.last=None;self.bits=0;self.mask_builds=0
        self.order=None;self.entries=[]
        if spec['family']=='split_ties':
            self.order=sorted(range(len(y)),key=lambda i:(-float(s[i]),i));total=0
            for n,i in enumerate(self.order,1):
                total+=int(y[i]);self.entries.append((F(min(n,total+spec['count_offset']),n),total,n,n))
        else:
            levels=sorted(set(float(v) for v in s),reverse=True)
            if spec['family']=='drop_group':levels.pop(len(levels)//2)
            for threshold in levels:
                mask=s>threshold if spec['family']=='gt' else s>=threshold
                n=int(mask.sum())
                if n:
                    k=int(y[mask].sum());self.entries.append((F(min(n,k+spec['count_offset']),n),k,n,threshold))
        # Feasible candidates are a suffix in ascending exact-precision order.
        self.entries.sort(key=lambda e:e[0]);self.ratios=[e[0] for e in self.entries]
        self.suffix=[None]*len(self.entries);best=None
        for j in range(len(self.entries)-1,-1,-1):
            _,k,n,_=self.entries[j];key=(k,n if spec['objective']=='max_tp_max_n' else -n)
            if best is None or key>best[0]:best=(key,j)
            self.suffix[j]=best[1]
        self.positive=bool(y.sum())

    def selected(self,alpha):
        i=(bisect_left if self.spec['precision']=='inclusive' else bisect_right)(self.ratios,alpha)
        if not self.positive or i==len(self.entries):return (0,0,0)
        j=self.suffix[i];_,k,n,descriptor=self.entries[j]
        if j!=self.last:
            if self.order is not None:
                mask=np.zeros(len(self.y),bool);mask[self.order[:n]]=True
            else:mask=self.s>descriptor if self.spec['family']=='gt' else self.s>=descriptor
            self.bits=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little');self.last=j;self.mask_builds+=1
        return k,n,self.bits

def verify(y,old,new,ids,cert):
    if not __debug__:raise RuntimeError('Certificate verification requires assertions enabled (no python -O)')
    assert cert['schema']=='exact-policy-certificate/1' and cert['version']=='1.0.0'
    y=np.asarray(y);old=np.asarray(old);new=np.asarray(new)
    assert y.ndim==1 and len(y) and old.shape==new.shape==y.shape
    assert np.isin(y,[0,1]).all() and np.isfinite(old).all() and np.isfinite(new).all()
    assert len(ids)==len(y) and len(set(ids))==len(y)
    for spec in [cert['old_spec'],cert['new_spec']]:
        assert set(spec)=={'family','precision','objective','count_offset'}
        assert spec['family'] in ['ge','gt','drop_group','split_ties'] and spec['precision'] in ['inclusive','strict']
        assert spec['objective'] in ['max_tp_max_n','max_tp_min_n'] and spec['count_offset'] in [0,1]
    h=hashlib.sha256()
    for array in [y.astype('<i8'),old.astype('<f8'),new.astype('<f8')]:h.update(str(array.shape).encode());h.update(array.tobytes())
    h.update(json.dumps(list(ids),ensure_ascii=False,separators=(',',':')).encode('utf-8'))
    assert h.hexdigest()==cert['input_sha256'],'Input binding mismatch'
    a=Family(y,old,cert['old_spec']);b=Family(y,new,cert['new_spec']);lo,hi=map(F,cert['domain']);assert 0<=lo<hi<=1
    breaks=sorted({lo,hi}|{p for p in a.ratios+b.ratios if lo<p<hi})
    assert cert['critical_values']==list(map(str,breaks)),'Missing/altered critical values'
    cells=cert['cells'];assert cells
    parsed=[]
    for c in cells:
        l,r=F(c['lo']),F(c['hi']);assert lo<=l<=r<=hi
        assert type(c['left_closed']) is bool and type(c['right_closed']) is bool and type(c['equal']) is bool
        if l==r:assert c['left_closed'] and c['right_closed']
        parsed.append((l,r,c))
    assert parsed[0][0]==lo and cells[0]['left_closed'] and parsed[-1][1]==hi and cells[-1]['right_closed']
    for (l,r,x),(ll,rr,z) in zip(parsed,parsed[1:]):assert r==ll and x['right_closed']!=z['left_closed'],'Gap/overlap'
    probes=set(breaks)|{(l+r)/2 for l,r in zip(breaks,breaks[1:])}
    probes|={v for l,r,c in parsed for v in [l,r,(l+r)/2]};truth={};cursor=0
    for alpha in sorted(probes):
        while cursor<len(parsed) and (alpha>parsed[cursor][1] or alpha==parsed[cursor][1] and not parsed[cursor][2]['right_closed']):cursor+=1
        assert cursor<len(parsed),'Coverage error';l,r,c=parsed[cursor]
        assert (alpha>l or alpha==l and c['left_closed']) and (alpha<r or alpha==r and c['right_closed']),'Coverage error'
        va=a.selected(alpha);vb=b.selected(alpha);xor=va[2]^vb[2];eq=not xor;truth[alpha]=eq
        assert (va[1],vb[1],eq)==(c['old_n'],c['new_n'],c['equal']),'Wrong winner/equality'
        if not eq and cert['witness_enabled']:
            w=c['witness'];i=w['row_index'];assert 0<=i<len(y) and w['row_id']==ids[i] and (xor>>i)&1
            assert w['old_selected']==bool(va[2]>>i&1) and w['new_selected']==bool(vb[2]>>i&1)
            assert w['changed_rows']==xor.bit_count()
    length=sum((r-l for l,r in zip(breaks,breaks[1:]) if not truth[(l+r)/2]),F(0))
    assert cert['equivalent']==all(truth.values()) and F(cert['divergent_length'])==length
    assert F(cert['psc_exact'])==length/(hi-lo) and cert['psc']==float(length/(hi-lo))
    assert cert['candidate_counts']==[len(a.entries),len(b.entries)]
    return {'verified':True,'probes':len(probes),'candidate_masks':len(a.entries)+len(b.entries),'winner_mask_builds':a.mask_builds+b.mask_builds,'checker':'streaming-suffix/1'}
