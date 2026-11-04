"""Independent threshold-mask enumeration, with no production profile/rank logic."""
from fractions import Fraction
import json,hashlib
import numpy as np

def candidates(y,s,spec):
    y=np.asarray(y);s=np.asarray(s);out=[]
    if spec['family']=='split_ties':
        # Independent stable Python sorting (the mutant permits inside-tie prefixes).
        order=sorted(range(len(y)),key=lambda i:(-float(s[i]),i))
        masks=[]
        for n in range(1,len(y)+1):
            mask=np.zeros(len(y),bool);mask[order[:n]]=True;masks.append(mask)
    else:
        levels=sorted(set(float(x) for x in s),reverse=True)
        if spec['family']=='drop_group':levels.pop(len(levels)//2)
        masks=[s>t if spec['family']=='gt' else s>=t for t in levels]
    for mask in masks:
        n=int(mask.sum())
        if not n:continue
        k=int(y[mask].sum());fk=min(n,k+spec['count_offset'])
        bits=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little')
        out.append((Fraction(fk,n),k,n,bits))
    return out

def select(table,alpha,positive,spec):
    if not positive:return (0,0,0)
    best=None
    for p,k,n,bits in table:
        if p>alpha or p==alpha and spec['precision']=='inclusive':
            key=(k,n if spec['objective']=='max_tp_max_n' else -n)
            if best is None or key>best[0]:best=(key,k,n,bits)
    return (0,0,0) if best is None else (best[1],best[2],best[3])

def verify(y,old,new,ids,cert):
    """Checks coverage, all critical points, all open cells, winners, PSC, and IDs.

    A midpoint alone is not sufficient: the verifier independently derives its
    own critical points and rejects any certificate omitting a needed partition.
    """
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
    for a in [y.astype('<i8'),old.astype('<f8'),new.astype('<f8')]:h.update(str(a.shape).encode());h.update(a.tobytes())
    h.update(json.dumps(list(ids),ensure_ascii=False,separators=(',',':')).encode('utf-8'))
    assert h.hexdigest()==cert['input_sha256'],'Input binding mismatch'
    a=candidates(y,old,cert['old_spec']);b=candidates(y,new,cert['new_spec']);pos=bool(y.sum())
    lo,hi=map(Fraction,cert['domain']);assert 0<=lo<hi<=1
    breaks=sorted({lo,hi}|{x[0] for x in a+b if lo<x[0]<hi})
    assert cert['critical_values']==list(map(str,breaks)),'Missing/altered critical values'
    cells=cert['cells'];assert cells and Fraction(cells[0]['lo'])==lo and cells[0]['left_closed'] and Fraction(cells[-1]['hi'])==hi and cells[-1]['right_closed']
    for c in cells:
        l,r=Fraction(c['lo']),Fraction(c['hi']);assert lo<=l<=r<=hi
        if l==r:assert c['left_closed'] and c['right_closed']
    for x,z in zip(cells,cells[1:]):
        assert x['hi']==z['lo'] and (x['right_closed']!=z['left_closed']),'Gap/overlap'
    probes=set(breaks)|{(l+r)/2 for l,r in zip(breaks,breaks[1:])}
    probes|={Fraction(c[k]) for c in cells for k in ['lo','hi']}
    probes|={(Fraction(c['lo'])+Fraction(c['hi']))/2 for c in cells}
    length=Fraction(0);truth=[]
    for alpha in sorted(probes):
        matches=[c for c in cells if (alpha>Fraction(c['lo']) or alpha==Fraction(c['lo']) and c['left_closed']) and (alpha<Fraction(c['hi']) or alpha==Fraction(c['hi']) and c['right_closed'])]
        assert len(matches)==1,'Coverage error';c=matches[0]
        va=select(a,alpha,pos,cert['old_spec']);vb=select(b,alpha,pos,cert['new_spec']);eq=va[2]==vb[2];truth.append(eq)
        assert (va[1],vb[1],eq)==(c['old_n'],c['new_n'],c['equal']),'Wrong winner/equality'
        if not eq and cert['witness_enabled']:
            w=c['witness'];i=w['row_index'];xor=va[2]^vb[2]
            assert 0<=i<len(y) and w['row_id']==ids[i] and ((xor>>i)&1)
            assert w['old_selected']==bool((va[2]>>i)&1) and w['new_selected']==bool((vb[2]>>i)&1)
            assert w['changed_rows']==xor.bit_count()
    for l,r in zip(breaks,breaks[1:]):
        if select(a,(l+r)/2,pos,cert['old_spec'])[2]!=select(b,(l+r)/2,pos,cert['new_spec'])[2]:length+=r-l
    assert cert['equivalent']==all(truth)
    assert Fraction(cert['divergent_length'])==length and Fraction(cert['psc_exact'])==length/(hi-lo)
    assert cert['psc']==float(length/(hi-lo))
    assert cert['candidate_counts']==[len(a),len(b)]
    return {'verified':True,'probes':len(probes),'candidate_masks':len(a)+len(b)}
