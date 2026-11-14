"""Retrieve official COIL-20 archive and record content hashes; digits are bundled."""
import argparse,hashlib,json,sys,zipfile,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data_prep import ROOT,load_raw
URL='https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--datasets',nargs='+',default=['all']);args=ap.parse_args()
    names=['pendigits','coil20'] if 'all' in args.datasets else args.datasets
    if any(n not in ['pendigits','coil20'] for n in names):ap.error('unknown dataset')
    dest=ROOT/'data/raw';dest.mkdir(parents=True,exist_ok=True);lp=dest/'_fetch_log.json'
    log=json.loads(lp.read_text()) if lp.exists() else {}
    for name in names:
        if name=='coil20':
            folder=dest/'coil20';folder.mkdir(exist_ok=True);archive=folder/'coil-20-proc.zip'
            if not archive.exists():
                tmp=archive.with_suffix('.partial')
                with urllib.request.urlopen(URL,timeout=60) as response,tmp.open('wb') as f:
                    import shutil;shutil.copyfileobj(response,f)
                tmp.replace(archive)
            with zipfile.ZipFile(archive) as z:
                for item in z.infolist():
                    p=(folder/item.filename).resolve()
                    if not p.is_relative_to(folder.resolve()):raise ValueError('unsafe ZIP path')
                if len(list((folder/'coil-20-proc').glob('obj*__*.png')))!=1440:z.extractall(folder)
            blob=archive.read_bytes();url=URL
        else:
            X,y=load_raw(name);blob=X.tobytes()+y.tobytes();url='https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html'
        sha=hashlib.sha256(blob).hexdigest();old=log.get(name,{})
        log[name]=dict(url=url,sha256=sha,bytes=len(blob),retrieved_utc=old.get('retrieved_utc') if old.get('sha256')==sha else datetime.now(timezone.utc).isoformat(),hash_scope='archive bytes' if name=='coil20' else 'bundled raw X float64 + y int64 bytes')
        print(name,sha)
    lp.write_text(json.dumps(log,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
