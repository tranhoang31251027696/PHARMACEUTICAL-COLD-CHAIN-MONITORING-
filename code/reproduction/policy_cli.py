"""Minimal certificate-producing CI adapter for frozen, aligned binary scores."""
import argparse,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from policy_exact import compare_policies
from independent_oracle import verify

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--lo',default='.30');p.add_argument('--hi',default='.90')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--fail-on-divergence',action='store_true')
    a=p.parse_args();d=np.load(a.input,allow_pickle=False);ids=d['ids'].tolist() if 'ids' in d else list(range(len(d['y'])))
    new_ids=d['new_ids'].tolist() if 'new_ids' in d else ids
    c=compare_policies(d['y'],d['old'],d['new'],a.lo,a.hi,ids,new_ids)
    verify(d['y'],d['old'],d['new'],ids,c)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(c,indent=2),encoding='utf-8')
    print(json.dumps({'equivalent':c['equivalent'],'psc_exact':c['psc_exact'],'output':str(a.output)}))
    if a.fail_on_divergence and not c['equivalent']:
        print(json.dumps(next(x for x in c['cells'] if not x['equal'])),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
