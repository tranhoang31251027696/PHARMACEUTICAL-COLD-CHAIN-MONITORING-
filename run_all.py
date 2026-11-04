"""Run the self-contained study in code/ from the repository root."""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parent/'code/reproduction/run_all.py'),run_name='__main__')
