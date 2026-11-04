"""Re-execute both actual SciPy versions using user-provided Python environments."""
from pathlib import Path
import argparse,subprocess
Q=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-python',required=True,type=Path);p.add_argument('--new-python',required=True,type=Path);a=p.parse_args()
    for version,exe in [('1.15.3',a.old_python),('1.18.1',a.new_python)]:
        subprocess.run([str(exe.resolve()),str(Q/'version_worker.py'),'--expected',version,'--out',str(Q/'results/v2'/('scipy_'+version))],check=True,cwd=Q)
    subprocess.run([str(a.new_python.resolve()),str(Q/'version_evaluation.py')],check=True,cwd=Q)
if __name__=='__main__':main()
