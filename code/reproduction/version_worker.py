"""Run real SciPy interpolation code in a separately supplied Python environment."""
from pathlib import Path
import argparse,sys,json,hashlib,inspect,platform
import numpy as np,scipy
from scipy.interpolate import interp1d

def main():
    p=argparse.ArgumentParser();p.add_argument('--expected',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    assert scipy.__version__==a.expected
    Q=Path(__file__).resolve().parent;m=json.loads((Q/'inputs/version_inputs/manifest.json').read_text(encoding='utf-8'));arrays={}
    for rec in m['cases']:
        f=Q/'inputs/version_inputs'/rec['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256'];d=np.load(f)
        result=interp1d(d['x'],d['v'],kind='linear',bounds_error=False,fill_value=(d['v'][0],d['v'][-1]))(np.clip(d['raw'],d['x'][0],d['x'][-1]))
        if rec['cast_float32']:result=result.astype(np.float32)
        arrays[rec['case_id']]=result
    a.out.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.out/'scores.npz',**arrays)
    source=inspect.getsource(interp1d._call_linear);(a.out/'interpolation_source.txt').write_text(source,encoding='utf-8')
    r={'scipy':scipy.__version__,'numpy':np.__version__,'python':sys.version,'platform':platform.platform(),'python_executable':sys.executable,'scipy_path':scipy.__file__,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'arrays':len(arrays),'scores_sha256':hashlib.sha256((a.out/'scores.npz').read_bytes()).hexdigest()}
    (a.out/'runtime.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
