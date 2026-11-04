from pathlib import Path
import subprocess,json,sys
Q=Path(__file__).resolve().parent

def main():
    manifest=json.loads((Q/'inputs/manifest.json').read_text(encoding='utf-8'))
    public=next(r for r in manifest['cases'] if r['cohort']=='Public_WDBC');checks=[]
    for label,filename,expected in [('equivalent','case_000.npz',0),('divergent',public['file'],1)]:
        r=subprocess.run([sys.executable,str(Q/'policy_cli.py'),str(Q/'inputs'/filename),'--output',str(Q/'results'/f'ci_{label}_certificate.json'),'--fail-on-divergence'],capture_output=True,text=True)
        assert r.returncode==expected,(label,r.stderr)
        if expected:assert 'row_id' in r.stderr
        checks.append({'case':label,'expected_exit':expected,'actual_exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (Q/'results/cli_integration_checks.json').write_text(json.dumps({'status':'PASS','checks':checks},indent=2),encoding='utf-8');print('CLI PASS')
if __name__=='__main__':main()
