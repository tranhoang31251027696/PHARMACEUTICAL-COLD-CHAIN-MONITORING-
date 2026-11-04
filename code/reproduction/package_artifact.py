"""Freeze the V11 computational artifact without review correspondence."""
from pathlib import Path
import hashlib,json,zipfile,argparse

def package(root,out):
    root=root.resolve();out=out.resolve()
    from build_manuscript import source_audit
    source_audit(root,'');files={}
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        n=p.relative_to(root).as_posix()
        if any(x in p.relative_to(root).parts for x in ['.git','.venv','__pycache__','.pytest_cache','authoring_cache']):continue
        if p.suffix.lower() in ['.zip','.pyc','.pdf','.docx']:continue
        if p.name.startswith('RESPONSE_TO_REVIEW_'):continue
        if p.name in ['ARTIFACT_MANIFEST.json','package_validation.json','READ_ME_FIRST.md','KET_QUA_Q1.md']:continue
        if p.parent==root/'results' and (p.name.startswith('run_all_') or p.name=='reorganization_pytest.xml'):continue
        files[n]=p.read_bytes()
    manifest={n:hashlib.sha256(d).hexdigest() for n,d in files.items()}
    files['ARTIFACT_MANIFEST.json']=json.dumps(manifest,indent=2).encode();out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,d in files.items():z.writestr(n,d)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for n,d in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==d
    return dict(status='PASS',path=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),manifest_files=len(manifest),bytes=out.stat().st_size)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'Reproducibility_Artifact_V11.zip');a=p.parse_args()
    print(json.dumps(package(Path(__file__).resolve().parent,a.out),indent=2))
