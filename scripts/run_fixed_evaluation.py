"""Back up historical outputs, then run the repaired evaluation with unchanged settings."""
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    env = os.environ.copy()
    env['NUMBA_NUM_THREADS'] = '1'
    def run(*args):
        subprocess.run([sys.executable, *args], cwd=ROOT, env=env, check=True)
    # No model fitting or output replacement if these checks fail.
    run('-m', 'pytest', '-q', 'tests/test_reviewed_split_reader.py')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = ROOT / 'results_backup' / stamp
    backup.mkdir(parents=True, exist_ok=False)
    for relative in ('results', 'figures/results', 'report/DSAI5102_Group16_Report_V3.md'):
        source = ROOT / relative
        if source.exists():
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
    print(f'Historical outputs backed up to {backup}', flush=True)
    run('scripts/fetch_data.py', '--datasets', 'all')
    run('-m', 'src.data_prep', '--datasets', 'all', '--force')
    run('-m', 'pytest', '-q', 'tests/test_data_contract.py')
    run('scripts/make_splits.py')
    run('scripts/run_grid.py', '--recompute')
    run('scripts/review_result_summary.py')
    run('scripts/make_figures.py')
    run('scripts/validate_b.py')
    print('Evaluation and figures regenerated. Update V3 Tables 2a/2b/3 and numerical conclusions from the new CSVs. Timing Table 4 was not rerun.')

if __name__ == '__main__':
    main()
