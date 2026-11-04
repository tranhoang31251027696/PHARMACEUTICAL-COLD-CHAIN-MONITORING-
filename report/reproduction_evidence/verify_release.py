"""Verify an immutable release ZIP; write all new evidence as detached sidecars."""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess,sys,time,datetime,platform

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if not __debug__:raise RuntimeError('Release verification requires assertions enabled')
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--work-root',type=Path,required=True);p.add_argument('--report-dir',type=Path,required=True);p.add_argument('--expected-stages',type=int,required=True);a=p.parse_args()
    archive=a.archive.resolve();work=a.work_root.resolve();report=a.report_dir.resolve()
    assert not report.is_relative_to(work) and not work.is_relative_to(report),'Report and extraction must be separate'
    assert not archive.is_relative_to(work) and not archive.is_relative_to(report),'Archive must remain outside generated evidence/extraction'
    work.mkdir(parents=True,exist_ok=False);report.mkdir(parents=True,exist_ok=True)
    before=sha(archive);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('ARTIFACT_MANIFEST.json'))
        assert set(z.namelist())==set(manifest)|{'ARTIFACT_MANIFEST.json'},'Manifest must cover every release member'
        for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
        for name in z.namelist():assert (work/name).resolve().is_relative_to(work)
        z.extractall(work)
    assert not (work.parent/'SUBMISSION_PACKAGE').exists()
    envcode="import sys,platform,json,numpy,scipy,sklearn,pytest,z3,eval_toolkit,importlib.metadata;print(json.dumps(dict(python=sys.version,executable=sys.executable,platform=platform.platform(),numpy=numpy.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__,pytest=pytest.__version__,z3=z3.get_version_string(),eval_toolkit=eval_toolkit.__version__,packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions()})))"
    env=json.loads(subprocess.check_output([sys.executable,'-c',envcode],cwd=work,text=True))
    t=time.perf_counter()
    with (report/'run_all.log').open('w',encoding='utf-8') as f:r=subprocess.run([sys.executable,'run_all.py'],cwd=work,stdout=f,stderr=subprocess.STDOUT)
    status=json.loads((work/'results/run_all_status.json').read_text(encoding='utf-8'));assert sha(archive)==before
    passed=r.returncode==0 and len(status['stages'])==a.expected_stages and all(s['exit_code']==0 for s in status['stages'])
    outputs={f.relative_to(work).as_posix():sha(f) for f in sorted((work/'results').rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc'}
    (report/'output_digests.json').write_text(json.dumps(outputs,indent=2),encoding='utf-8')
    logs=report/'stage_logs';logs.mkdir(exist_ok=True)
    for f in (work/'results').glob('run_all_*.log'):
        (logs/f.name).write_bytes(f.read_bytes())
    result={'status':'PASS' if passed else 'FAIL','archive_path':str(archive),'archive_sha256_before':before,'archive_sha256_after':sha(archive),'archive_unchanged':True,'manifest_files_verified':len(manifest),'clean_extraction_path':str(work),'neighboring_submission_absent':True,'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-t,'environment':env,'exit_code':r.returncode,'stages':status['stages'],'output_files_hashed':len(outputs),'output_digest_manifest_sha256':sha(report/'output_digests.json'),'scope':'Execution of the exact frozen archive, not a candidate-source comparison. Evidence is intentionally outside the archive to avoid self-reference and changing its hash.'}
    (report/'RELEASE_VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    sidecars={f.relative_to(report).as_posix():sha(f) for f in report.rglob('*') if f.is_file() and f.name!='EVIDENCE_MANIFEST.json'}
    (report/'EVIDENCE_MANIFEST.json').write_text(json.dumps(sidecars,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
