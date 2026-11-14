"""B delivery verification: independent loader, exact folds, deterministic output, figures."""
import json,sys,subprocess,platform
from pathlib import Path
import numpy as np
import sklearn
from sklearn.model_selection import StratifiedKFold
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data_prep import ROOT,DATASETS,build,digest
from src.data import load
sp=json.loads((ROOT/'data/manifests/splits.json').read_text());report={'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__,'checks':{}}
for name in DATASETS:
 X,y=build(name);Xa,ya=load(name);assert np.array_equal(X,Xa) and np.array_equal(y,ya)
 m=json.loads((ROOT/f'data/manifests/{name}.json').read_text());assert digest(X,y)==m['array_sha256']
 with np.load(ROOT/f'data/processed/{name}.npz') as z:assert np.array_equal(z['X'],X) and np.array_equal(z['y'],y)
 folds=sp['datasets'][name]['folds'];assert len(folds)==10;seen=np.zeros(len(y),int)
 for (tr,te),f in zip(StratifiedKFold(10,shuffle=True,random_state=42).split(X,y),folds):
  assert np.array_equal(tr,f['train']) and np.array_equal(te,f['test'])
  assert not np.intersect1d(tr,te).size and np.array_equal(np.union1d(tr,te),np.arange(len(y)))
  seen[te]+=1
 assert np.all(seen==1)
 report['checks'][name]={'status':'PASS','shape':list(X.shape),'max_abs_difference_vs_A':float(np.abs(X-Xa).max()),'labels_equal':True,'array_sha256':digest(X,y),'classes':np.bincount(y).tolist(),'label_map':m['label_map'],'duplicate_rows':m['duplicate_rows'],'folds':'10; true-label stratification; disjoint; test coverage exactly once'}
p=ROOT/'data/manifests/splits.json';before=p.read_bytes();subprocess.run([sys.executable,str(ROOT/'scripts/make_splits.py')],check=True,capture_output=True);assert p.read_bytes()==before;report['split_bytes_deterministic']=True
figs=list((ROOT/'figures/eda').glob('*.png'))+list((ROOT/'figures/results').glob('*.png'));assert len(figs)==6;report['figures']={}
for p in figs:
 with Image.open(p) as im:
  assert im.info.get('dpi',(0,))[0]>=299
  report['figures'][str(p.relative_to(ROOT))]={'pixels':list(im.size),'dpi':list(im.info['dpi'])}
audit_dir=ROOT/'docs/validation/B';audit_dir.mkdir(parents=True,exist_ok=True)
(audit_dir/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
