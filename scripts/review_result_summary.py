"""Descriptive paper comparison; never silently certifies reproduction."""
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'results/paper_vs_ours.csv';d=pd.read_csv(p)
 d['signed_gap']=d.our_acc-d.paper_acc
 d['tolerance']=d.dataset.map({'pendigits':0.03,'coil20':0.10})
 d['within_amplitude_tolerance']=d.signed_gap.abs()<=d.tolerance+1e-12
 base=d[d.method=='tsne'].set_index(['dataset','k']).our_acc
 d['umap_minus_tsne']=[float(r.our_acc-base.loc[(r.dataset,r.k)]) if r.method in ('umap_ref','umap_ours') else np.nan for r in d.itertuples()]
 proto=ROOT/'results/evaluation_protocol.json'
 status='recomputed against data/manifests/splits.json'
 if proto.exists():
  _p=json.loads(proto.read_text())
  _digest=hashlib.sha256(json.dumps(_p,sort_keys=True).encode()).hexdigest()[:12]
  status+=' (protocol %s digest %s)'%(_p.get('schema',''),_digest)
 d['evaluation_status']=status
 d.to_csv(ROOT/'results/review_comparison.csv',index=False)
 print('Wrote review_comparison.csv: numerical closeness is not a reproduction verdict.')
if __name__=='__main__':main()
