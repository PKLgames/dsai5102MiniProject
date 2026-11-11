# 用途：预估 Kovács(2019) 基准矩阵的 CPU 成本（每个 split = 1 次过采样 + 4 次拟合）
# 跑法：PYTHONPATH=/tmp/sv NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/probe_kovacs_runtime.py
# 依赖：smote_variants==1.0.1 (--target /tmp/sv --no-deps) + metric-learn/minisom/seaborn

import sys, time, warnings, numpy as np
warnings.filterwarnings("ignore")
sys.path.insert(0,'/tmp/sv')
import smote_variants as sv
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, f1_score, recall_score

def load_keel(path):
    rows=[]; started=False
    for line in open(path, encoding='utf-8'):
        line=line.strip()
        if line.lower().startswith('@data'): started=True; continue
        if not started or not line: continue
        parts=[p.strip().strip("'") for p in line.split(',')]
        rows.append(parts)
    X=np.array([[float(v) for v in r[:-1]] for r in rows]); lab=[r[-1] for r in rows]
    uniq=sorted(set(lab)); y=np.array([0 if l==uniq[0] else 1 for l in lab])
    return X,y

def gmean(y,p):
    r=recall_score(y,p,pos_label=1,zero_division=0); s=recall_score(y,p,pos_label=0,zero_division=0)
    return float(np.sqrt(r*s))

CLFS = {
 'kNN': lambda: KNeighborsClassifier(n_neighbors=5),
 'SVM': lambda: SVC(C=1.0, gamma='scale', probability=False),
 'DT' : lambda: DecisionTreeClassifier(random_state=1),
 'MLP': lambda: MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=1),
}

def bench(name, path, n_repeats=1):
    X,y=load_keel(path)
    print(f"== {name}: {X.shape}, minority={int(y.sum())}, IR={ (y==0).sum()/max(1,y.sum()):.2f}")
    methods = ['SMOTE','polynom_fit_SMOTE','ProWSyn','SMOTE_IPF']
    rskf=RepeatedStratifiedKFold(n_splits=5, n_repeats=n_repeats, random_state=42)
    for mname in methods:
        cls=getattr(sv, mname, None)
        if cls is None: print(mname,'MISSING'); continue
        ov=cls()
        t_ov=t_fit=0.0; n=0
        try:
            for tr,te in rskf.split(X,y):
                t0=time.time()
                try: Xr,yr=ov.sample(X[tr],y[tr])
                except Exception as e: print(f"  {mname} sample failed: {type(e).__name__}: {str(e)[:90]}"); raise
                t_ov+=time.time()-t0; n+=1
                for cn,cf in CLFS.items():
                    t1=time.time(); c=cf(); c.fit(Xr,yr); c.predict(X[te]); t_fit+=time.time()-t1
        except Exception as e:
            print(f"  {mname}: ERROR {type(e).__name__}"); continue
        print(f"  {mname:18s} splits={n} sample={t_ov/n*1000:7.1f} ms  clf4={t_fit/n*1000:7.1f} ms  per-split-total={(t_ov+t_fit)/n*1000:7.1f} ms")

bench('glass1','/tmp/g1/glass1.dat')
bench('pima','/tmp/pima/pima.dat')
