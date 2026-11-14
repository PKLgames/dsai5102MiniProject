"""Test the actual split-reader function with controlled tiny datasets."""
import ast,json,hashlib
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
def reader(tmp_path):
 tree=ast.parse((ROOT/'scripts/run_grid.py').read_text())
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_splits')
 mod=ast.Module(body=[fn],type_ignores=[])
 import src.data as canonical
 X=np.arange(40,dtype=np.float32).reshape(20,2);y=np.repeat([0,1],10).astype(np.int64)
 old=canonical.load;canonical.load=lambda _: (X,y)
 ns={'np':np,'PROJECT':tmp_path,'N_FOLDS':10,'load':canonical.load, 'SEED':42, 'StratifiedKFold':__import__('sklearn.model_selection',fromlist=['StratifiedKFold']).StratifiedKFold}
 exec(compile(mod,'split_reader','exec'),ns)
 canonical.load=old
 return ns['load_splits'],X,y,canonical.array_sha256

def write(tmp_path,X,y,digest):
 from sklearn.model_selection import StratifiedKFold
 folds=[{'train':tr.tolist(),'test':te.tolist()} for tr,te in StratifiedKFold(10,shuffle=True,random_state=42).split(X,y)]
 d={'seed':42,'datasets':{'tiny':{'n':20,'n_folds':10,'array_sha256':digest(X,y),'folds':folds}}}
 p=tmp_path/'data/manifests/splits.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(d));return p,d

def test_reads_agreed_nested_schema(tmp_path):
 f,X,y,h=reader(tmp_path);write(tmp_path,X,y,h);folds=f('tiny',20)
 assert len(folds)==10
 assert all(set(y[te])=={0,1} for _,te in folds)

def test_missing_file_fails_instead_of_zero_label_fallback(tmp_path):
 f,*_=reader(tmp_path)
 with pytest.raises(FileNotFoundError):f('tiny',20)

def test_hash_mismatch_rejected(tmp_path):
 f,X,y,h=reader(tmp_path);p,d=write(tmp_path,X,y,h);d['datasets']['tiny']['array_sha256']='wrong';p.write_text(json.dumps(d))
 with pytest.raises(ValueError,match='hash'):f('tiny',20)

def test_overlap_rejected(tmp_path):
 f,X,y,h=reader(tmp_path);p,d=write(tmp_path,X,y,h);d['datasets']['tiny']['folds'][0]['train'].append(d['datasets']['tiny']['folds'][0]['test'][0]);p.write_text(json.dumps(d))
 with pytest.raises(ValueError,match='Invalid split'):f('tiny',20)


def test_duplicate_train_index_rejected(tmp_path):
 f,X,y,h=reader(tmp_path);p,d=write(tmp_path,X,y,h)
 d['datasets']['tiny']['folds'][0]['train'].append(d['datasets']['tiny']['folds'][0]['train'][0])
 p.write_text(json.dumps(d))
 with pytest.raises(ValueError,match='Invalid split'):f('tiny',20)

def test_unstratified_partition_rejected(tmp_path):
 from sklearn.model_selection import KFold
 f,X,y,h=reader(tmp_path);p,d=write(tmp_path,X,y,h)
 d['datasets']['tiny']['folds']=[{'train':tr.tolist(),'test':te.tolist()} for tr,te in KFold(10).split(X)]
 p.write_text(json.dumps(d))
 with pytest.raises(ValueError,match='stratified'):f('tiny',20)
