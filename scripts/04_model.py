import numpy as np, pandas as pd, rasterio, glob, json, xgboost as xgb, shap
from rasterio.warp import reproject, Resampling
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error
D='/workspace/soil_global/data'; O='/workspace/soil_global/out'
ref=rasterio.open(f'{D}/grids/kg_present.tif'); H,W=ref.shape; tr=ref.transform; crs=ref.crs
def rd(f,b=None):
    with rasterio.open(f) as r:
        x=r.read().astype('float32') if b is None else r.read(b).astype('float32')
        if r.nodata is not None: x[x==r.nodata]=np.nan
    x[x<-1e30]=np.nan; return x
bio=np.stack([rd(f'{D}/wc2.1_10m_bio/wc2.1_10m_bio_{i}.tif')[0] for i in range(1,20)])
elev=rd(glob.glob(f'{D}/wc2.1_10m_elev/*.tif')[0])[0]
gy,gx=np.gradient(np.nan_to_num(elev)); lat=np.linspace(90,-90,H+1)[:-1]-90/H
dx=(1/6)*111320*np.cos(np.deg2rad(lat))[:,None]; slope=np.degrees(np.arctan(np.hypot(gx/dx,gy/(111320/6))))
def sg(v):
    with rasterio.open(f'{D}/sg_{v}.tif') as r:
        a=r.read(1).astype('float32'); a[a==r.nodata]=np.nan; a[a<=0]=np.nan
        out=np.full((H,W),np.nan,'float32')
        reproject(a,out,src_transform=r.transform,src_crs=r.crs,dst_transform=tr,dst_crs=crs,resampling=Resampling.average,src_nodata=np.nan,dst_nodata=np.nan)
    return out/10
clay,sand=sg('clay'),sg('sand')
names=[f'bio{i}' for i in range(1,20)]+['elev','slope','clay','sand']
def stack(b): return np.concatenate([b,elev[None],slope[None],clay[None],sand[None]])
S0=stack(bio); np.save(f'{O}/S0.npy',S0)
kg=ref.read(1)
mask=(kg>0)&(kg!=30)&(lat[:,None]>-60)&np.all(np.isfinite(S0),0)
# points
p=pd.read_csv(f'{D}/points_topsoil.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1); c_=((p.X+180)*6).astype(int).clip(0,W-1)
X=S0[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
blk=(np.floor(p.X/5)*100+np.floor(p.Y/5)).values
targets={'phaq':('phaq',False),'sic':('sic',True),'soc':('soc',True),'bd':('bdfiod',False),'cf':('cfvo',False)}
res={}; models={}
for t,(col,lg) in targets.items():
    y=p[col].values; m=ok&np.isfinite(y)
    if t=='bd': m&=(y>0.2)&(y<2.2)
    if t=='cf': m&=(y>=0)&(y<=100)
    if t in('soc','sic'): m&=(y>=0)&(y<600)
    Xt,yt,gt=X[m],(np.log1p(y[m]) if lg else y[m]),blk[m]
    par=dict(n_estimators=500,max_depth=7,learning_rate=0.05,subsample=0.8,colsample_bytree=0.8,n_jobs=8,tree_method='hist')
    pred=np.zeros_like(yt)
    for tri,tei in GroupKFold(5).split(Xt,yt,gt):
        mm=xgb.XGBRegressor(**par).fit(Xt[tri],yt[tri]); pred[tei]=mm.predict(Xt[tei])
    yo,po=(np.expm1(yt),np.expm1(pred)) if lg else (yt,pred)
    res[t]=dict(n=int(m.sum()),r2_cv=float(r2_score(yo,po)),rmse_cv=float(mean_squared_error(yo,po)**.5),r2_cv_transformed=float(r2_score(yt,pred)))
    mod=xgb.XGBRegressor(**par).fit(Xt,yt); models[t]=(mod,lg)
    if t in ('phaq','sic','soc'):
        idx=np.random.default_rng(0).choice(len(Xt),min(3000,len(Xt)),replace=False)
        sv=shap.TreeExplainer(mod).shap_values(Xt[idx]); np.save(f'{O}/shap_{t}.npy',sv); np.save(f'{O}/shapX_{t}.npy',Xt[idx])
    print(t,res[t],flush=True)
json.dump(res,open(f'{O}/cv_metrics.json','w'),indent=1); json.dump(names,open(f'{O}/names.json','w'))
def predict(S):
    F=S[:,mask].T; outd={}
    for t,(mod,lg) in models.items():
        v=mod.predict(F); v=np.expm1(v) if lg else v
        a=np.full((H,W),np.nan,'float32'); a[mask]=np.clip(v,0,None); outd[t]=a
    return outd
P0=predict(S0); np.savez_compressed(f'{O}/pred_present.npz',**P0)
for f in sorted(glob.glob(f'{D}/wc2.1_10m_bioc_MPI*.tif')):
    tag=f.split('HR_')[1][:-4]; b=rd(f); b=np.where(np.isfinite(b),b,bio)
    Pf=predict(stack(b)); np.savez_compressed(f'{O}/pred_{tag}.npz',phaq=Pf['phaq'],sic=Pf['sic'],soc=Pf['soc']); print(tag,flush=True)
np.save(f'{O}/mask.npy',mask)
