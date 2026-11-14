"""Deterministic label-stratified folds in the agreed nested JSON schema."""
import sys,json
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedKFold
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data_prep import ROOT,DATASETS,build,digest
out={'seed':42,'datasets':{}}
for name in DATASETS:
    X,y=build(name);folds=[];seen=np.zeros(len(y),int)
    for tr,te in StratifiedKFold(10,shuffle=True,random_state=42).split(X,y):
        assert not np.intersect1d(tr,te).size
        assert len(np.union1d(tr,te))==len(y)
        seen[te]+=1;folds.append({'train':tr.tolist(),'test':te.tolist()})
    assert np.all(seen==1)
    assert max(len(f['test']) for f in folds)-min(len(f['test']) for f in folds)<=1
    out['datasets'][name]={'n':len(y),'n_folds':10,'array_sha256':digest(X,y),'folds':folds}
p=ROOT/'data/manifests/splits.json';p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(out,sort_keys=True,indent=1)+'\n');print(p)
