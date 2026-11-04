"""Exact finite binary decision regression. Input row identity is a caller contract."""
from fractions import Fraction
import numpy as np

def _precision_feasible(k,n,ratio):
 # Arbitrary decimal alpha may have a large denominator; avoid int64 overflow.
 if ratio.denominator*int(np.max(n))>np.iinfo(np.int64).max:
  return np.asarray([int(K)*ratio.denominator>=int(N)*ratio.numerator for K,N in zip(k,n)],dtype=bool)
 return k*ratio.denominator>=n*ratio.numerator

def frontier(y,s,alpha=.5):
 y=np.asarray(y);s=np.asarray(s,dtype=float)
 if y.ndim!=1 or s.shape!=y.shape or not len(y) or not np.isfinite(s).all() or not np.isin(y,[0,1]).all():raise ValueError('Require aligned finite vectors and binary labels')
 if not 0<alpha<=1:raise ValueError('alpha must lie in (0,1]')
 y=y.astype(np.int64);order=np.argsort(-s,kind='stable');ordered=s[order]
 ends=np.r_[np.flatnonzero(ordered[:-1]!=ordered[1:])+1,len(y)]
 k=np.cumsum(y[order])[ends-1];ratio=Fraction(str(alpha));feasible=_precision_feasible(k,ends,ratio)
 ok=np.flatnonzero(feasible);winner=None
 if len(ok) and y.sum()>0:
  best=k[ok].max();winner=int(ok[k[ok]==best][-1])
 tau=None if winner is None else float(ordered[ends[winner]-1]);alert=np.zeros(len(y),bool) if tau is None else s>=tau
 return dict(order=order,ends=ends,TP=k,N=ends,feasible=feasible,threshold=tau,alert=alert,selected_TP=int(y[alert].sum()),selected_N=int(alert.sum()))

def _same_frontier(a,b,feasible_only=False):
 na=a['ends'][a['feasible']] if feasible_only else a['ends'];nb=b['ends'][b['feasible']] if feasible_only else b['ends']
 if not np.array_equal(na,nb):return False
 if not len(na):return True
 # A size-n old prefix equals the size-n new prefix iff all its new ranks are < n.
 rank=np.empty(len(b['order']),dtype=np.int64);rank[b['order']]=np.arange(len(rank))
 prefixmax=np.maximum.accumulate(rank[a['order']])
 return bool(np.all(prefixmax[na-1]<na))

def compare(y,old,new,alpha=.5,atol=1e-6,mode='full',old_ids=None,new_ids=None):
 if mode not in ['selection_only','full']:raise ValueError('Unknown mode')
 y=np.asarray(y);old=np.asarray(old,dtype=float);new=np.asarray(new,dtype=float)
 a=frontier(y,old,alpha);b=frontier(y,new,alpha)
 if old_ids is not None or new_ids is not None:
  if old_ids is None or new_ids is None:raise ValueError('Provide both row ID vectors')
  oi=np.asarray(old_ids);ni=np.asarray(new_ids)
  if oi.shape!=y.shape or ni.shape!=y.shape or len(np.unique(oi))!=len(y) or len(np.unique(ni))!=len(y) or not np.array_equal(oi,ni):raise ValueError('Require identical aligned unique row IDs')
 changed=int(np.count_nonzero(a['alert']!=b['alert']));fixed=0 if a['threshold'] is None else int(np.count_nonzero((old>=a['threshold'])!=(new>=a['threshold'])))
 report=dict(mode=mode,maximum_score_difference=float(np.max(np.abs(old-new))),tolerance_pass=bool(np.allclose(old,new,atol=atol,rtol=0)),old_threshold=a['threshold'],new_threshold=b['threshold'],threshold_changed=a['threshold']!=b['threshold'],old_TP=a['selected_TP'],old_N=a['selected_N'],new_TP=b['selected_TP'],new_N=b['selected_N'],reselected_decisions_changed=changed,fixed_decisions_changed=fixed)
 if mode=='selection_only':
  report.update(frontier_changed=None,feasibility_frontier_changed=None,isolated_refinement_assumptions=None,proper_prefix_witness=None,attribution='Not assessed in selection_only mode',regression_flag=bool(changed or fixed or report['threshold_changed']));return report
 lv,ix=np.unique(old,return_inverse=True);nl,ni=np.unique(new,return_inverse=True)
 low=np.full(len(lv),len(nl),dtype=np.int64);high=np.full(len(lv),-1,dtype=np.int64);np.minimum.at(low,ix,ni);np.maximum.at(high,ix,ni);split=np.flatnonzero(low!=high)
 ml=np.full(len(nl),len(lv),dtype=np.int64);mh=np.full(len(nl),-1,dtype=np.int64);np.minimum.at(ml,ni,ix);np.maximum.at(mh,ni,ix);merges=int((ml!=mh).sum())
 mins=np.full(len(lv),np.inf);maxs=np.full(len(lv),-np.inf);np.minimum.at(mins,ix,new);np.maximum.at(maxs,ix,new)
 crossing=bool(np.any(np.maximum.accumulate(maxs)[:-1]>mins[1:])) if len(lv)>1 else False
 isolated=False;witness=False;prefixes=[]
 if len(split)==1 and merges==0 and not crossing:
  j=int(split[0]);tie=ix==j;isolated=bool(np.array_equal(old[~tie],new[~tie]) and (j==0 or maxs[j-1]<mins[j]) and (j==len(lv)-1 or maxs[j]<mins[j+1]))
  if isolated:
   above=old>lv[j];ratio=Fraction(str(alpha));levels,bi=np.unique(new[tie],return_inverse=True)
   ns=np.bincount(bi)[::-1].cumsum()+int(above.sum());ks=np.bincount(bi,weights=y[tie])[::-1].cumsum().astype(np.int64)+int(y[above].sum())
   for level,T,N in zip(levels[::-1][:-1],ks[:-1],ns[:-1]):
    T=int(T);N=int(N);feasible=T*ratio.denominator>=N*ratio.numerator;beats=(T,N)>(a['selected_TP'],a['selected_N']);witness |= feasible and beats
    prefixes.append(dict(score=float(level),TP=T,N=N,feasible=bool(feasible),beats_old_winner=bool(beats)))
   if bool(witness)!=bool(changed):raise AssertionError('Prefix condition disagrees with selected sets')
 full_changed=not _same_frontier(a,b);feasible_changed=not _same_frontier(a,b,True)
 report.update(old_groups=len(lv),new_groups=len(nl),split_groups=len(split),merged_groups=merges,between_group_order_crossing=crossing,frontier_changed=full_changed,feasibility_frontier_changed=feasible_changed,isolated_refinement_assumptions=isolated,proper_prefix_witness=bool(witness),prefix_certificate=prefixes,attribution='isolated refinement with checked prefix condition' if isolated else ('identical score vector' if np.array_equal(old,new) else 'other perturbation; no Proposition 1 attribution'),regression_flag=bool(changed or fixed or full_changed or report['threshold_changed']))
 return report
