"""B's independent raw-data preparation. Run: python -m src.data_prep --datasets all."""
import argparse, hashlib, json, time, re
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATASETS=['pendigits','coil20']
PAPER_COUNTS={'pendigits':1797,'coil20':1440}
def digest(X,y):
    return hashlib.sha256(np.ascontiguousarray(X,np.float32).tobytes()+np.ascontiguousarray(y,np.int64).tobytes()).hexdigest()
def load_raw(name):
    if name=='pendigits':
        from sklearn.datasets import load_digits
        d=load_digits();return d.data.copy(),d.target.copy()
    if name!='coil20': raise ValueError(name)
    files=[]
    for p in (ROOT/'data/raw/coil20/coil-20-proc').glob('*.png'):
        m=re.fullmatch(r'obj(\d+)__(\d+)\.png',p.name)
        if m: files.append((int(m[1]),int(m[2]),p))
    files.sort(key=lambda t:(t[0],t[1]))
    if len(files)!=1440: raise ValueError('COIL-20 requires 1440 PNGs; run scripts/fetch_data.py')
    images=[]
    for _,_,p in files:
        with Image.open(p) as im: a=np.asarray(im)
        if a.shape!=(128,128) or a.dtype!=np.uint8: raise ValueError(str(p))
        images.append(a.reshape(-1,order='C'))
    return np.stack(images),np.array([c for c,_,_ in files])
def encode(y):
    order=list(dict.fromkeys(map(int,y)))
    mapping={c:i for i,c in enumerate(order)}
    return np.array([mapping[int(c)] for c in y],np.int64),order
def build(name):
    X,y=load_raw(name)
    X=np.ascontiguousarray(X,dtype=np.float32)/(16.0 if name=='pendigits' else 255.0)
    y,_=encode(y)
    if not np.isfinite(X).all() or not np.isfinite(y).all(): raise ValueError('NaN/inf')
    expected=(PAPER_COUNTS[name],64 if name=='pendigits' else 16384)
    if X.shape!=expected or X.min()<0 or X.max()>1: raise ValueError('shape/range')
    return np.ascontiguousarray(X,np.float32),y
def metadata(name,X,y,elapsed):
    _,yr=load_raw(name);_,order=encode(yr)
    # Hash rows without duplicating the high-dimensional matrix.
    hashes=[hashlib.sha256(row.tobytes()).digest() for row in X]
    logpath=ROOT/'data/raw/_fetch_log.json'
    log=json.loads(logpath.read_text()).get(name,{}) if logpath.exists() else {}
    return dict(dataset=name,n=len(y),n_features=X.shape[1],n_classes=len(order),
        class_counts={str(i):int((y==i).sum()) for i in range(len(order))},
        label_map={str(i):(str(c) if name=='pendigits' else f'obj{c}') for i,c in enumerate(order)},
        nan=int(np.isnan(X).sum()),inf=int(np.isinf(X).sum()),duplicate_rows=len(X)-len(set(hashes)),
        min=float(X.min()),max=float(X.max()),array_sha256=digest(X,y),
        source=log.get('url','sklearn.datasets.load_digits()'),source_sha256=log.get('sha256'),
        retrieved_utc=log.get('retrieved_utc'),prepared_utc=datetime.now(timezone.utc).isoformat(),
        prep_seconds=elapsed,notes='float32 before division; C-order; first-appearance label encoding; no standardization, removal or augmentation')
def card_table(manifests):
    rows=['| Dataset | n | Features | Classes | Class count range | Pixel scaling |','|---|---:|---:|---:|---|---|']
    for m in manifests:
        counts=list(m['class_counts'].values())
        rows.append(f"| {m['dataset']} | {m['n']} | {m['n_features']} | {m['n_classes']} | {min(counts)}–{max(counts)} | /{16 if m['dataset']=='pendigits' else 255} |")
    return '\n'.join(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--datasets',nargs='+',default=['all'])
    ap.add_argument('--force',action='store_true');ap.add_argument('--out',type=Path)
    ap.add_argument('--emit-card-table',action='store_true');a=ap.parse_args()
    names=DATASETS if 'all' in a.datasets else a.datasets
    if any(n not in DATASETS for n in names): ap.error('unknown dataset')
    manifests=[]
    for name in names:
        t=time.perf_counter();X,y=build(name);m=metadata(name,X,y,time.perf_counter()-t)
        out=a.out or ROOT/'data/processed';mf=a.out or ROOT/'data/manifests'
        out.mkdir(parents=True,exist_ok=True);mf.mkdir(parents=True,exist_ok=True)
        target=out/f'{name}.npz'
        if target.exists() and not a.force:
            with np.load(target) as z:
                if digest(z['X'],z['y'])!=m['array_sha256']: raise ValueError('existing data differs; use --force')
        else: np.savez_compressed(target,X=X,y=y)
        (mf/f'{name}.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');manifests.append(m)
        if not a.emit_card_table: print(name,X.shape,m['array_sha256'])
    if a.emit_card_table: print(card_table(manifests))
if __name__=='__main__':main()
