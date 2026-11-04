"""Exact descriptive PSC and declared-policy-resolution assessment.

No deployment probability, user loss, or global equivalence is inferred from
small interval measure or equivalence on a restricted finite decimal lattice.
"""
from pathlib import Path
from fractions import Fraction as F
import math,json,csv,hashlib
import numpy as np
Q=Path(__file__).resolve().parent

def quantile(values,q):
    values=sorted(values);p=F(len(values)-1)*q;j=p.numerator//p.denominator
    return values[j] if j==len(values)-1 else values[j]+(p-j)*(values[j+1]-values[j])

def lattice_bounds(region,digits):
    scale=10**digits;lo=F(region['lo'])*scale;hi=F(region['hi'])*scale
    lower=math.ceil(lo);upper=math.floor(hi)
    if lower==lo and not region['left_closed']:lower+=1
    if upper==hi and not region['right_closed']:upper-=1
    return lower,upper

def lattice_hits(regions,digits):
    return sum(max(0,upper-lower+1) for lower,upper in (lattice_bounds(r,digits) for r in regions))

def main():
    R=Q/'results/v6';R.mkdir(exist_ok=True);records={r['case_id']:r for r in json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))['cases']};rows=[]
    for path in sorted((Q/'results/v5/second_project_certificates').glob('*.json')):
        c=json.loads(path.read_text(encoding='utf-8'));rec=records[c['case_id']];source=Q/'inputs'/rec['file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==c['source_input_sha256'];d=np.load(source);y=d['y'][:64]
        psc=F(c['psc_exact']);maximum=0;shortfall=F(0);float_differences=0
        for p in c['probes']:
            a=F(p['alpha']);old=int(p['reference_bits'],16);actual=int(p['actual_bits'],16);xor=old^actual;maximum=max(maximum,xor.bit_count())
            if actual:
                n=actual.bit_count();tp=sum(int(y[i]) for i in range(len(y)) if actual>>i&1);shortfall=max(shortfall,a-F(tp,n))
        for p in c['representable_policy_probes']:float_differences+=p['different']
        supremum=shortfall;lookup={F(p['alpha']):p for p in c['probes']};cuts=list(map(F,c['critical_values']))
        for left,right in zip(cuts,cuts[1:]):
            bits=int(lookup[(left+right)/2]['actual_bits'],16)
            if bits:
                tp=sum(int(y[i]) for i in range(len(y)) if bits>>i&1);supremum=max(supremum,right-F(tp,bits.bit_count()))
        row=dict(case_id=c['case_id'],pipeline=rec['pipeline'],psc_exact=str(psc),psc=float(psc),components=len(c['divergent_regions']),max_component_width_exact=str(max((F(r['hi'])-F(r['lo']) for r in c['divergent_regions']),default=F(0))),max_changed_observations=maximum,max_actual_precision_shortfall_exact=str(shortfall),max_actual_precision_shortfall=float(shortfall),precision_shortfall_supremum_exact=str(supremum),precision_shortfall_supremum=float(supremum),representable_policy_differences=float_differences)
        for digits in [2,3,4,6]:row[f'decimal_{digits}_affected_policies']=lattice_hits(c['divergent_regions'],digits)
        rows.append(row)
    assert len(rows)==30;positive=[F(r['psc_exact']) for r in rows if F(r['psc_exact'])>0];assert len(positive)==27
    distribution={name:{'exact':str(quantile(positive,q)),'value':float(quantile(positive,q))} for name,q in [('min',F(0)),('q25',F(1,4)),('median',F(1,2)),('q75',F(3,4)),('max',F(1))]}
    lattice=[]
    for digits in [2,3,4,6]:
        affected=sum(r[f'decimal_{digits}_affected_policies']>0 for r in rows);hits=sum(r[f'decimal_{digits}_affected_policies'] for r in rows)
        lattice.append({'decimal_places':digits,'policies_per_workload':6*10**(digits-1)+1,'affected_workloads':affected,'affected_policy_workload_pairs':hits,'scope':'Exact rational decimal lattice on [0.30,0.90], with interval endpoint ownership respected. Restricted-domain equality does not imply continuous-domain equality.'})
    with (R/'policy_significance_cases.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'status':'PASS','workloads':30,'positive_psc_workloads':len(positive),'zero_psc_workloads':30-len(positive),'positive_psc_distribution':distribution,'decimal_policy_resolution':lattice,'workloads_with_representable_policy_difference':sum(r['representable_policy_differences']>0 for r in rows),'max_changed_observations':max(r['max_changed_observations'] for r in rows),'max_precision_shortfall':max(r['max_actual_precision_shortfall'] for r in rows),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Descriptive numerical-contract sensitivity, not a population frequency, defect rate, deployment risk or tolerance-based continuous equivalence claim. No utility/cost data or operational deployment was observed.'}
    result['max_precision_shortfall_supremum']=max(r['precision_shortfall_supremum'] for r in rows)
    result['shortfall_scope']='max_precision_shortfall is observed at stored probes; the separate supremum includes open-cell endpoint limits and need not be attained.'
    scipy_cases=[]
    with (R/'scipy_defect_results.csv').open(encoding='utf-8') as f:upstream=list(csv.DictReader(f))
    for record in upstream:
        if record['variant']!='affected':continue
        wrapper=json.loads((R/'scipy_defect_certificates'/record['certificate_file']).read_text(encoding='utf-8'));regions=[cell for cell in wrapper['certificate']['cells'] if not cell['equal']]
        entry={'case_id':record['case_id'],'psc_exact':record['psc_exact']}
        for digits in [2,3,4,6]:entry[f'decimal_{digits}_affected_policies']=lattice_hits(regions,digits)
        scipy_cases.append(entry)
    assert len(scipy_cases)==36
    with (R/'scipy_allowed_policy_counts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(scipy_cases[0]));w.writeheader();w.writerows(scipy_cases)
    result['documented_scipy_defect_decimal_resolution']=[{'decimal_places':digits,'workloads':36,'policies_per_workload':6*10**(digits-1)+1,'affected_workloads':sum(r[f'decimal_{digits}_affected_policies']>0 for r in scipy_cases),'affected_policy_workload_pairs':sum(r[f'decimal_{digits}_affected_policies'] for r in scipy_cases)} for digits in [2,3,4,6]]
    (R/'policy_significance_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
