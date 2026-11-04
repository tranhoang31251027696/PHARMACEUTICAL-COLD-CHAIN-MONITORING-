"""Exact policy equivalence for finite binary threshold selectors.

The policy domain is rational [lo, hi]. Fractions describe decimal strings exactly;
binary score values define ordering/ties and are not rounded by this module.
"""
from fractions import Fraction
import hashlib
import heapq
import json
from time import perf_counter_ns
import numpy as np

VERSION = '1.0.0'
DEFAULT = {'family':'ge', 'precision':'inclusive', 'objective':'max_tp_max_n', 'count_offset':0}

def rational(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))

def inputs(y, old, new, ids=None, new_ids=None):
    y=np.asarray(y); old=np.asarray(old,dtype=float); new=np.asarray(new,dtype=float)
    if y.ndim!=1 or not len(y) or old.shape!=y.shape or new.shape!=y.shape:
        raise ValueError('Require nonempty aligned one-dimensional arrays')
    if not np.isin(y,[0,1]).all() or not np.isfinite(old).all() or not np.isfinite(new).all():
        raise ValueError('Require binary labels and finite scores')
    ids=list(range(len(y))) if ids is None else list(ids)
    new_ids=ids if new_ids is None else list(new_ids)
    if len(ids)!=len(y) or len(set(ids))!=len(y) or ids!=new_ids:
        raise ValueError('Row identity contract: require identical aligned unique IDs')
    if not all(isinstance(i,(str,int)) and not isinstance(i,bool) for i in ids):
        raise ValueError('IDs must be JSON string or integer values')
    return y.astype(np.int64),old,new,ids

def profile(y, scores, spec=None):
    spec={**DEFAULT,**(spec or {})}
    if spec['family'] not in ['ge','gt','drop_group','split_ties'] or spec['precision'] not in ['inclusive','strict'] or spec['objective'] not in ['max_tp_max_n','max_tp_min_n'] or spec['count_offset'] not in [0,1]:
        raise ValueError('Unsupported selector specification')
    order=np.argsort(-scores,kind='stable')
    ends=np.r_[np.flatnonzero(scores[order][:-1]!=scores[order][1:])+1,len(y)]
    if spec['family']=='gt':ends=ends[:-1]  # s > observed thresholds omits the full set
    if spec['family']=='drop_group' and len(ends):ends=np.delete(ends,len(ends)//2)
    if spec['family']=='split_ties':ends=np.arange(1,len(y)+1)
    cumulative=np.cumsum(y[order]); candidates=[]
    for n in ends:
        n=int(n); actual=int(cumulative[n-1]);k=min(n,actual+spec['count_offset'])
        candidates.append({'n':n,'tp':actual,'feasibility_tp':k,'p':Fraction(k,n)})
    # Each candidate enters the priority queue once and is popped at most once.
    heap=[(-c['tp'], -c['n'] if spec['objective']=='max_tp_max_n' else c['n'],j) for j,c in enumerate(candidates)]
    heapq.heapify(heap)
    return {'order':order,'candidates':candidates,'heap':heap,'spec':spec,'has_positive':bool(y.sum())}

def winner(p, alpha):
    while p['heap']:
        j=p['heap'][0][2];c=p['candidates'][j]
        valid=c['p']>=alpha if p['spec']['precision']=='inclusive' else c['p']>alpha
        if valid:return c['n'] if p['has_positive'] else 0
        heapq.heappop(p['heap'])
    return 0

def digest_inputs(y,old,new,ids):
    h=hashlib.sha256()
    for a in [y.astype('<i8'),old.astype('<f8'),new.astype('<f8')]:
        h.update(str(a.shape).encode());h.update(a.tobytes())
    h.update(json.dumps(ids,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
    return h.hexdigest()

def compare_policies(y, old, new, lo='0.30', hi='0.90', ids=None, new_ids=None,
                     old_spec=None,new_spec=None,with_witness=True,stage_timings=None):
    phase_start=perf_counter_ns() if stage_timings is not None else 0
    y,old,new,ids=inputs(y,old,new,ids,new_ids);lo=rational(lo);hi=rational(hi)
    if not 0<=lo<hi<=1:raise ValueError('Require 0 <= lo < hi <= 1')
    a=profile(y,old,old_spec);b=profile(y,new,new_spec)
    breaks=sorted({lo,hi}|{c['p'] for p in [a,b] for c in p['candidates'] if lo<c['p']<hi})
    rank_a=np.empty(len(y),int);rank_a[a['order']]=np.arange(len(y))
    rank_b=np.empty(len(y),int);rank_b[b['order']]=np.arange(len(y))
    prefixmax=np.maximum.accumulate(rank_b[a['order']]);cache={};cells=[]
    if stage_timings is not None:
        stage_timings['construction_ms']=(perf_counter_ns()-phase_start)/1e6
        stage_timings['witness_ms']=0.0
        phase_start=perf_counter_ns()
    def append(l,r,closed,alpha):
        na=winner(a,alpha);nb=winner(b,alpha);key=(na,nb)
        if key not in cache:
            equal=na==nb and (na==0 or int(prefixmax[na-1])<na)
            w=None
            if not equal and with_witness:
                witness_start=perf_counter_ns() if stage_timings is not None else 0
                changed=np.flatnonzero((rank_a<na)!=(rank_b<nb));i=int(changed[0])
                w={'row_index':i,'row_id':ids[i],'old_selected':bool(rank_a[i]<na),'new_selected':bool(rank_b[i]<nb),'changed_rows':len(changed)}
                if stage_timings is not None:stage_timings['witness_ms']+=(perf_counter_ns()-witness_start)/1e6
            cache[key]=(bool(equal),w)
        equal,w=cache[key]
        cell={'lo':str(l),'hi':str(r),'left_closed':closed,'right_closed':closed,
              'old_n':na,'new_n':nb,'equal':equal,'witness':w}
        # Merge only identical selected-set states, preserving endpoint ownership.
        if cells and all(cells[-1][k]==cell[k] for k in ['old_n','new_n','equal','witness']) and cells[-1]['hi']==cell['lo'] and (cells[-1]['right_closed'] or cell['left_closed']):
            cells[-1]['hi']=cell['hi'];cells[-1]['right_closed']=cell['right_closed']
        else:cells.append(cell)
    for i,x in enumerate(breaks):
        if i:append(breaks[i-1],x,False,(breaks[i-1]+x)/2)
        append(x,x,True,x)
    if stage_timings is not None:
        stage_timings['sweep_excluding_witness_ms']=(perf_counter_ns()-phase_start)/1e6-stage_timings['witness_ms']
        phase_start=perf_counter_ns()
    length=sum((rational(c['hi'])-rational(c['lo']) for c in cells if not c['equal']),Fraction(0))
    result={'schema':'exact-policy-certificate/1','version':VERSION,'input_sha256':digest_inputs(y,old,new,ids),
            'domain':[str(lo),str(hi)],'old_spec':a['spec'],'new_spec':b['spec'],
            'critical_values':[str(x) for x in breaks],'cells':cells,
            'equivalent':all(c['equal'] for c in cells),'divergent_length':str(length),
            'psc_exact':str(length/(hi-lo)),'psc':float(length/(hi-lo)),
            'candidate_counts':[len(a['candidates']),len(b['candidates'])],
            'witness_enabled':bool(with_witness),'distinct_state_pairs':len(cache)}
    if stage_timings is not None:stage_timings['assembly_and_hash_ms']=(perf_counter_ns()-phase_start)/1e6
    return result

def at(certificate, alpha):
    alpha=rational(alpha)
    for c in certificate['cells']:
        l=rational(c['lo']);h=rational(c['hi'])
        if (alpha>l or alpha==l and c['left_closed']) and (alpha<h or alpha==h and c['right_closed']):return c
    raise ValueError('Policy outside certified domain')

def assert_policy_equivalent(y,old,new,**kwargs):
    cert=compare_policies(y,old,new,**kwargs)
    if not cert['equivalent']:
        c=next(c for c in cert['cells'] if not c['equal'])
        raise AssertionError('Policy regression: '+json.dumps(c,ensure_ascii=False))
    return cert
