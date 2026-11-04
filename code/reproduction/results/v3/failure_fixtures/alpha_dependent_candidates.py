"""Executable SUT, separate from the policy certificate implementation.

Its alpha dependence is confined to _feasible. The adapter records calls to that
guard; this is an instrumented finite program, not arbitrary black-box proof.
"""
from fractions import Fraction
import numpy as np

def masks(scores):
    return [scores >= t for t in sorted(set(scores.tolist()),reverse=True)]

def build(y,scores,alpha):
    rows=[]
    if alpha > 0: return rows
    for mask in masks(scores):
        n=int(mask.sum())
        if n:rows.append((mask,int(y[mask].sum()),n))
    return rows

def _feasible(k,n,alpha):
    return k*alpha.denominator >= n*alpha.numerator

def select(rows,alpha,positive):
    if not positive:return np.zeros(len(rows[0][0]),dtype=bool) if rows else np.zeros(0,dtype=bool)
    best=(0,0);selected=np.zeros(len(rows[0][0]),dtype=bool) if rows else np.zeros(0,dtype=bool)
    for mask,k,n in rows:
        feasible=_feasible(k,n,alpha)
        key=(k,n)
        if feasible and key>best:best=key;selected=mask
    return selected
