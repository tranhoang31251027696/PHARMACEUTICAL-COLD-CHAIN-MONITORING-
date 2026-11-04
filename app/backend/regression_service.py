"""HTTP adapter for the unchanged research producer and independent consumer."""
from pathlib import Path
import sys, math
from fractions import Fraction

ROOT = Path(__file__).resolve().parent / 'engine'
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

MAX_ROWS = 2000

def _policy(value):
    if not isinstance(value, str) or not 0 < len(value) <= 64:
        raise ValueError('Policy values must be rational strings, e.g. "0.5" or "1/2"')
    result = Fraction(value)
    if not 0 <= result <= 1:
        raise ValueError('Policy must be between 0 and 1')
    return value

def _inputs(payload):
    import numpy as np
    if not isinstance(payload, dict):
        raise ValueError('Expected a JSON object')
    y, old, new = (payload.get(k) for k in ('labels', 'reference_scores', 'actual_scores'))
    if not all(isinstance(a, list) for a in (y, old, new)):
        raise ValueError('labels, reference_scores and actual_scores must be arrays')
    if not 1 <= len(y) <= MAX_ROWS or len(old) != len(y) or len(new) != len(y):
        raise ValueError(f'Arrays must have the same length, from 1 to {MAX_ROWS} rows')
    if any(type(v) is not int or v not in (0, 1) for v in y):
        raise ValueError('Labels must be integers 0 or 1')
    if any(type(v) not in (int, float) or not math.isfinite(v) for a in (old, new) for v in a):
        raise ValueError('Scores must be finite numbers')
    ids = payload.get('ids')
    if not isinstance(ids, list) or len(ids) != len(y) or any(not isinstance(v, str) or not v for v in ids):
        raise ValueError('Every row must have a nonempty string ID')
    if len(set(ids)) != len(ids):
        raise ValueError('Observation IDs must be unique')
    new_ids = payload.get('new_ids', ids)
    if new_ids != ids:
        raise ValueError('Reference and actual IDs must be aligned in the same order')
    return np.asarray(y), np.asarray(old), np.asarray(new), ids

def diagnose(payload, check_only=False):
    if not __debug__:
        raise RuntimeError('Independent checking requires Python assertions enabled')
    from policy_exact import compare_policies, DEFAULT
    from streaming_checker import verify
    from policy_domain_query import answer
    from verified_boolean_query import VerifiedBooleanIndex
    y, old, new, ids = _inputs(payload)
    if check_only:
        cert = payload.get('certificate')
        if not isinstance(cert, dict):
            raise ValueError('Missing certificate object')
    else:
        lo, hi = _policy(payload.get('lo', '0.30')), _policy(payload.get('hi', '0.90'))
        specs = []
        for key in ('old_precision', 'new_precision'):
            precision = payload.get(key, 'inclusive')
            if precision not in ('inclusive', 'strict'):
                raise ValueError('Precision contract must be inclusive or strict')
            specs.append(dict(DEFAULT, precision=precision))
        cert = compare_policies(y, old, new, lo=lo, hi=hi, ids=ids,
                                old_spec=specs[0], new_spec=specs[1])
    # The consumer reconstructs memberships; no verdict is issued before it accepts.
    audit = verify(y, old, new, ids, cert)
    query = payload.get('query')
    full = boolean = None
    if query is not None:
        if not isinstance(query, dict):
            raise ValueError('Query must be an object')
        if query.get('kind') == 'finite':
            values = query.get('values')
            if not isinstance(values, list) or not 1 <= len(values) <= 500:
                raise ValueError('Finite query must contain 1 to 500 values')
            for value in values:
                _policy(value)
        else:
            _policy(query.get('lo')); _policy(query.get('hi'))
        full = answer(cert, query)
        boolean = VerifiedBooleanIndex(y, old, new, ids, cert).query(query)
        if full['affected'] != boolean['affected']:
            raise RuntimeError('Query implementations disagree')
    wrapper = {'labels': y.tolist(), 'reference_scores': old.tolist(),
               'actual_scores': new.tolist(), 'ids': ids, 'certificate': cert}
    return {'status': 'EQUIVALENT' if cert['equivalent'] else 'DIVERGENT',
            'verified': True, 'verification': audit, 'certificate': cert,
            'query_result': full, 'boolean_result': boolean, 'download': wrapper,
            'scope': 'Fixed labeled observations and declared selector contracts; '
                     'not proof of arbitrary program implementation or operational safety'}
