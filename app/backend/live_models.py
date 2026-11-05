"""Run frozen research XGBoost variants on uploaded hourly sensor histories."""
from pathlib import Path
import json, hashlib, functools
ROOT = Path(__file__).resolve().parent

@functools.lru_cache(maxsize=1)
def resources():
    import xgboost as xgb
    configs = json.loads((ROOT/'models/manifest.json').read_text())['models']
    out=[]
    for c in configs:
        p=ROOT/'models'/f"{c['model']}_6h.ubj"
        model=xgb.XGBClassifier(); model.load_model(p)
        out.append((c,model,hashlib.sha256(p.read_bytes()).hexdigest()))
    return out

def predict_pair(body):
    import numpy as np
    import pandas as pd
    import live_features as features
    readings=body.get('readings')
    if body.get('history_complete') is not True:
        raise ValueError('Confirm complete batch history before running the local models')
    if not isinstance(readings,list) or not 10<=len(readings)<=100000:
        raise ValueError('Supply 10 to 100000 hourly sensor readings')
    d=pd.DataFrame(readings)
    needed=['Batch_ID','Timestamp','calibrated_temp','Humidity','Shipment_Mode']
    if any(k not in d for k in needed): raise ValueError('Missing sensor fields')
    if d.Batch_ID.isna().any() or d.Batch_ID.nunique()!=1: raise ValueError('Select exactly one batch')
    d['Timestamp']=pd.to_datetime(d.Timestamp,errors='raise')
    if d.Timestamp.dt.tz is not None: raise ValueError('Normalize timestamps to source-local or UTC-naive explicitly')
    d=d.sort_values('Timestamp').reset_index(drop=True)
    if not d.Timestamp.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all(): raise ValueError('Consecutive hourly readings are required')
    for col in ['calibrated_temp','Humidity']:
        d[col]=pd.to_numeric(d[col],errors='raise')
        if not np.isfinite(d[col]).all(): raise ValueError('Sensor values must be finite')
    if not d.calibrated_temp.between(-100,100).all() or not d.Humidity.between(0,100).all(): raise ValueError('Temperature must be within -100 to 100 C; humidity within 0 to 100')
    modes={'Air':0,'Air Charter':1,'Ocean':2,'Truck':3}
    if not d.Shipment_Mode.isin(modes).all(): raise ValueError('Shipment mode must be Air, Air Charter, Ocean or Truck')
    d['actual_temp']=d.calibrated_temp
    d['actual_temp_anomaly_flag']=(~d.actual_temp.between(2,8)).astype(int)
    for k,v in dict(pd=pd,np=np,TARGET_COL='actual_temp',ANOMALY_FLAG_COL='actual_temp_anomaly_flag',TEMP_LOWER=2.,TEMP_UPPER=8.,CAUTION_LO=2.5,CAUTION_HI=7.5,LAGS=[1,2,3,6,12,24],ROLLS=[6,12,24],SM=modes).items(): setattr(features,k,v)
    d,F=features.build_features(d)
    dr=np.exp(-51044.8/8.314*(1/(d.actual_temp+273.15)-1/278.15))
    F['arrhenius_rate_ratio']=dr
    for w in [6,12,24]: F[f'arrhenius_excess_hours_{w}']=(dr-1).groupby(d.Batch_ID).rolling(w,min_periods=1).sum().reset_index(level=0,drop=True)
    F['arrhenius_excess_hours_cum']=(dr-1).groupby(d.Batch_ID).cumsum()
    outside=d.actual_temp_anomaly_flag
    runs=outside.ne(outside.shift()).cumsum()
    onset=outside.eq(1)&outside.shift(fill_value=0).eq(0)&outside.groupby(runs).transform('size').ge(3)
    cs=onset.cumsum();labels=(cs.shift(-6)-cs).gt(0).astype(int)
    eligible=np.flatnonzero(outside.eq(0).to_numpy() & (np.arange(len(d)) < len(d)-9))
    if not len(eligible): raise ValueError('No normal-temperature origins with 9 hours of follow-up')
    chosen=eligible[np.linspace(0,len(eligible)-1,min(2000,len(eligible)),dtype=int)]
    scores=[];provenance=[]
    for c,model,digest in resources():
        raw=model.predict_proba(F[c['columns']].iloc[chosen].to_numpy(np.float32))[:,1]
        calibrated=np.interp(raw,np.asarray(c['iso_x']),np.asarray(c['iso_y']))
        scores.append(calibrated.tolist());provenance.append(dict(model=c['model'],artifact_sha256=digest,threshold=c['threshold']))
    ids=[f"{d.Batch_ID.iloc[i]}@{d.Timestamp.iloc[i].isoformat()}" for i in chosen]
    return dict(kind='regression',modelNames=['XGBoost thermal (6h)','XGBoost thermal + Arrhenius (6h)'],count=len(chosen),payload=dict(ids=ids,labels=labels.iloc[chosen].tolist(),reference_scores=scores[0],actual_scores=scores[1]),rows=[dict(id=rid,y=int(labels.iloc[i]),old_score=scores[0][j],new_score=scores[1][j]) for j,(rid,i) in enumerate(zip(ids,chosen))],warnings=[],live_prediction=dict(source='XGBoost predict_proba executed on uploaded readings in this request',models=provenance,input_sha256=hashlib.sha256(json.dumps(readings,sort_keys=True).encode()).hexdigest(),input_readings=len(d),eligible_origins=len(eligible),selected_origins=len(chosen),label_rule='Derived from uploaded temperatures: onset of >=3 consecutive excursion hours in next 6 hours; normal origins with 9-hour follow-up. Not independently supplied ground truth.',sampling='All eligible origins, or uniformly spaced subset of at most 2000',scope='Frozen research feature variants; not FINAL-1.0; supplied temperature values used without additional calibration'))
