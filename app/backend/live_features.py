def _runlen(s, batch):
    rid = (s.ne(s.shift()) | batch.ne(batch.shift())).cumsum()
    return s.groupby(rid).cumcount().add(1) * s.astype(int)

def build_features(d):
    d = d.sort_values(['Batch_ID', 'Timestamp']).reset_index(drop=True)
    g = d.groupby('Batch_ID', sort=False)
    F = pd.DataFrame(index=d.index)
    T = d[TARGET_COL]
    b = d['Batch_ID']
    F['temp_now'] = T
    for k in LAGS:
        F[f'lag_{k}'] = g[TARGET_COL].shift(k)
    for w in ROLLS:
        r = g[TARGET_COL].rolling(w, min_periods=1)
        F[f'rolling_mean_{w}'] = r.mean().reset_index(level=0, drop=True)
        F[f'rolling_std_{w}'] = r.std().reset_index(level=0, drop=True)
        F[f'rolling_min_{w}'] = r.min().reset_index(level=0, drop=True)
        F[f'rolling_max_{w}'] = r.max().reset_index(level=0, drop=True)
    F['diff_1'] = F['temp_now'] - F['lag_1']
    F['dev_from_24h'] = F['temp_now'] - F['rolling_mean_24']
    F['batch_mean_sofar'] = g[TARGET_COL].expanding().mean().reset_index(level=0, drop=True)
    order = g.cumcount()
    F['hours_since_start'] = order
    F['humidity'] = d['Humidity']
    F['humidity_rmean6'] = g['Humidity'].rolling(6, min_periods=1).mean().reset_index(level=0, drop=True)
    F['transport_mode'] = d['Shipment_Mode'].map(SM)
    F['hour'] = d['Timestamp'].dt.hour
    F['day_of_week'] = d['Timestamp'].dt.dayofweek
    F['hour_sin'] = np.sin(2 * np.pi * F['hour'] / 24)
    F['hour_cos'] = np.cos(2 * np.pi * F['hour'] / 24)
    a = d[ANOMALY_FLAG_COL]
    ga = a.groupby(b)
    F['n_anom_sofar'] = ga.cumsum()
    last = pd.Series(np.where(a == 1, order, np.nan), index=d.index).groupby(b).ffill()
    F['hours_since_anom'] = order - last
    F['anom_last6'] = ga.rolling(6, min_periods=1).sum().reset_index(level=0, drop=True)
    outside_core = (T < CAUTION_LO) | (T > CAUTION_HI)
    caution = outside_core & (a == 0)
    exc = np.maximum(T - TEMP_UPPER, 0) + np.maximum(TEMP_LOWER - T, 0)
    cload = np.maximum(T - CAUTION_HI, 0) + np.maximum(CAUTION_LO - T, 0)
    margin = np.minimum(T - TEMP_LOWER, TEMP_UPPER - T)
    F['margin_now'] = margin
    for w in ROLLS:
        F[f'margin_min_{w}'] = margin.groupby(b).rolling(w, min_periods=1).min().reset_index(level=0, drop=True)
    F['margin_slope_6'] = margin - margin.groupby(b).shift(6)
    F['consec_outside_core_h'] = _runlen(outside_core, b)
    F['consec_caution_h'] = _runlen(caution, b)
    for w in ROLLS:
        F[f'caution_hours_{w}'] = caution.astype(int).groupby(b).rolling(w, min_periods=1).sum().reset_index(level=0, drop=True)
        F[f'aulc_caution_{w}'] = cload.groupby(b).rolling(w, min_periods=1).sum().reset_index(level=0, drop=True)
    F['aulc_excursion_24'] = exc.groupby(b).rolling(24, min_periods=1).sum().reset_index(level=0, drop=True)
    F['aulc_caution_cum'] = cload.groupby(b).cumsum()
    F['aulc_excursion_cum'] = exc.groupby(b).cumsum()
    F['caution_hours_cum'] = caution.astype(int).groupby(b).cumsum()
    lastc = pd.Series(np.where(outside_core, order, np.nan), index=d.index).groupby(b).ffill()
    F['hours_since_outside_core'] = order - lastc
    return (d, F)