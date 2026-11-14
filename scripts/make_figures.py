"""B figures. Existing A results are read-only; no success flags are inferred."""
import sys,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data_prep import ROOT,build,load_raw,encode
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white'})
EDA=ROOT/'figures/eda';RES=ROOT/'figures/results'
EDA.mkdir(parents=True,exist_ok=True);RES.mkdir(parents=True,exist_ok=True)
def save(fig,path,dpi=300):
    fig.savefig(path,dpi=dpi,bbox_inches='tight');plt.close(fig)
def main():
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,name in zip(axes,['pendigits','coil20']):
        X,y=build(name);_,yr=load_raw(name);_,order=encode(yr)
        labels=[str(c) if name=='pendigits' else str(c) for c in order]
        ax.bar(range(len(order)),np.bincount(y),color='#287e8d');ax.set_xticks(range(len(order)),labels,rotation=0)
        ax.set(title=f'{name}: {len(y):,} samples',xlabel='Digit' if name=='pendigits' else 'Object ID',ylabel='Number of images');ax.grid(axis='y',alpha=.15)
    save(fig,EDA/'eda_01_class_counts.png')
    raw,yr=load_raw('coil20');objects=sorted(np.unique(yr));fig,axes=plt.subplots(20,5,figsize=(7,23))
    for row,c in enumerate(objects):
        ids=np.flatnonzero(yr==c);chosen=ids[np.linspace(0,len(ids)-1,5,dtype=int)]
        for col,i in enumerate(chosen):
            ax=axes[row,col];ax.imshow(raw[i].reshape(128,128),cmap='gray',vmin=0,vmax=255);ax.set_xticks([]);ax.set_yticks([])
            if col==0:ax.set_ylabel(f'Object {c}',rotation=0,labelpad=30,va='center')
    fig.suptitle('COIL-20: five views per object',y=.995);fig.subplots_adjust(hspace=.08,wspace=.05)
    save(fig,EDA/'eda_02_sample_grid.png')
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    for row,name in enumerate(['pendigits','coil20']):
        X,y=load_raw(name);scale=16 if name=='pendigits' else 255
        hist,edges=np.histogram(X,bins=np.arange(scale+2)-.5);prob=hist/hist.sum()
        for col in range(2):
            centers=(edges[:-1]+edges[1:])/2/(scale if col else 1)
            axes[row,col].bar(centers,prob,width=.9/(scale if col else 1),color='#287e8d')
            axes[row,col].set(title=f"{name}: {'scaled' if col else 'raw'}",xlabel='Pixel intensity',ylabel='Fraction of pixels (log scale)',yscale='log')
    fig.tight_layout();save(fig,EDA/'eda_03_pixel_hist.png')
    fig,axes=plt.subplots(1,2,figsize=(12,6));colors=plt.get_cmap('tab20')
    handles=[]
    for ax,tag,title in zip(axes,['umapours','tsne'],['UMAP (ours)','t-SNE']):
        with np.load(ROOT/f'results/embeddings/coil20_{tag}.npz') as z:E,y=z['E'],z['y']
        assert E.shape==(1440,2) and len(y)==1440 and np.isfinite(E).all()
        for c in range(20):
            ax.scatter(*E[y==c].T,s=9,color=colors(c),alpha=.8,rasterized=True)
        ax.set(title=title,xlabel='Embedding coordinate 1',ylabel='Embedding coordinate 2');ax.set_xticks([]);ax.set_yticks([])
    handles=[Line2D([],[],marker='o',linestyle='',color=colors(c),label=f'Object {c+1}',markersize=5) for c in range(20)]
    fig.legend(handles=handles,ncol=10,loc='lower center',bbox_to_anchor=(.5,-.025),fontsize=8)
    fig.subplots_adjust(bottom=.18,wspace=.18);save(fig,RES/'fig2_qualitative_coil20.png')
    df=pd.read_csv(ROOT/'results/paper_vs_ours.csv');fig,ax=plt.subplots(figsize=(8,7))
    palette={'pca':'#677786','tsne':'#dd8c35','umap_ref':'#3b8f82','umap_ours':'#815aa0'}
    for (ds,m),g in df.groupby(['dataset','method']):
        ax.scatter(g.paper_acc,g.our_acc,s=48,marker='o' if ds=='pendigits' else '^',color=palette[m],edgecolor='white',linewidth=.5,label=f'{ds} / {m}')
    ax.plot([0,1],[0,1],'--',color='#87929b',lw=1);ax.set(xlim=(.3,1.01),ylim=(.3,1.01),xlabel='Published kNN accuracy',ylabel='Current snapshot kNN accuracy',title='Published vs supplied results (40 comparisons)')
    ax.text(.02,.97,'Descriptive comparison; reproduction verdicts require protocol review.',transform=ax.transAxes,va='top',fontsize=8)
    ax.grid(alpha=.15);ax.legend(fontsize=8,loc='lower right');save(fig,RES/'fig3_paper_vs_ours.png')
    # Supplement makes the central research question directly visible.
    sm=pd.read_csv(ROOT/'results/grid_knn_summary.csv');fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for ax,ds in zip(axes,['pendigits','coil20']):
        for m,g in sm[sm.dataset==ds].groupby('method'):
            g=g.sort_values('k');ax.errorbar(g.k,g['mean'],yerr=g['std'],marker='o',capsize=2,label=m,color=palette[m])
        ax.set(xscale='log',xticks=[10,20,40,80,160],ylim=(.3,1.02),title=ds,xlabel='kNN classifier neighbours (k)',ylabel='Accuracy (mean ± fold SD)')
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter());ax.grid(alpha=.15)
    axes[1].legend(fontsize=8);fig.tight_layout();save(fig,RES/'fig4_knn_accuracy_by_k.png')
    print('Saved 3 EDA + 2 required result figures + 1 supplementary curve.')
if __name__=='__main__':main()
