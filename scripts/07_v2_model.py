# v2: Beck V3 zones, Hargreaves aridity, hurdle SIC, smearing SOC, BD-PTF with SOC, AOA, bootstrap x 6-GCM ensemble
import numpy as np, pandas as pd, rasterio, glob, json, os, xgboost as xgb, shap
from rasterio.warp import reproject, Resampling
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from sklearn.neighbors import NearestNeighbors
D='/workspace/soil_global/data'; O='/workspace/soil_global/out/v2'; os.makedirs(O,exist_ok=True)
ref=rasterio.open(f'{D}/grids/kg_present.tif'); H,W=ref.shape; TR=ref.transform; CRS=ref.crs
lat=np.linspace(90,-90,H+1)[:-1]-90/H
def rd(f):
    with rasterio.open(f) as r:
        x=r.read().astype('float32'); nd=r.nodata
    if nd is not None: x[x==nd]=np.nan
    x[x<-1e30]=np.nan; return x
def warp(f,res=Resampling.average,dtype='float32',nod=np.nan):
    with rasterio.open(f) as r:
        a=r.read(1).astype(dtype); src_nd=r.nodata
        if dtype=='float32' and src_nd is not None: a[a==src_nd]=np.nan
        out=np.full((H,W),nod,dtype)
        reproject(a,out,src_transform=r.transform,src_crs=r.crs,dst_transform=TR,dst_crs=CRS,resampling=res,src_nodata=(np.nan if dtype=='float32' else 0),dst_nodata=nod)
    return out
# ---- Beck V3 zones (koppenmap.com COG mirror of Beck 2023 V3, 0.1 deg reprojected to EPSG:3857)
KG={}
for f in sorted(glob.glob(f'{D}/beckv3/*.tif')):
    KG[os.path.basename(f)[:-4]]=warp(f,Resampling.mode,'uint8',0)
np.savez_compressed(f'{O}/kg_beck.npz',**KG)
# ---- aridity (Hargreaves PET)
doy=np.array([15,46,75,105,135,162,198,228,258,288,318,344])
def Ra():
    ph=np.deg2rad(lat)[None,:]; J=doy[:,None]
    dr=1+0.033*np.cos(2*np.pi*J/365); de=0.409*np.sin(2*np.pi*J/365-1.39)
    ws=np.arccos(np.clip(-np.tan(ph)*np.tan(de),-1,1))
    ra=24*60/np.pi*0.082*dr*(ws*np.sin(ph)*np.sin(de)+np.cos(ph)*np.cos(de)*np.sin(ws))
    return (ra*0.408)[:,:,None]  # mm/day, (12,H,1)
RA=Ra(); ND=np.array([31,28,31,30,31,30,31,31,30,31,30,31])[:,None,None]
def arid(tn,tx,p):
    pet=(0.0023*RA*((tn+tx)/2+17.8)*np.sqrt(np.clip(tx-tn,0,None))*ND).sum(0)
    return np.log1p(p.sum(0)/np.maximum(pet,1)), pet
def mon(v): return np.concatenate([rd(f) for f in sorted(glob.glob(f'{D}/wc2.1_10m_{v}/*.tif'),key=lambda f:int(f.split('_')[-1][:-4]))])
tn0,tx0,p0=mon('tmin'),mon('tmax'),mon('prec')
ai0,pet0=arid(tn0,tx0,p0); del tn0,tx0,p0
bio=np.stack([rd(f'{D}/wc2.1_10m_bio/wc2.1_10m_bio_{i}.tif')[0] for i in range(1,20)])
elev=rd(glob.glob(f'{D}/wc2.1_10m_elev/*.tif')[0])[0]
e=np.nan_to_num(elev); gy,gx=np.gradient(e); dx=(1/6)*111320*np.cos(np.deg2rad(lat))[:,None]
slope=np.degrees(np.arctan(np.hypot(gx/dx,gy/(111320/6))))
from scipy.ndimage import uniform_filter
tpi=e-uniform_filter(e,5)
def sg(v):
    a=warp(f'{D}/sg_{v}.tif'); a[a<=0]=np.nan; return a/10
clay,sand=sg('clay'),sg('sand')
names=[f'bio{i}' for i in range(1,20)]+['logAI','PET','elev','slope','TPI','clay','sand']
def stack(b,ai,pet): return np.concatenate([b,ai[None],pet[None],elev[None],slope[None],tpi[None],clay[None],sand[None]]).astype('float32')
S0=stack(bio,ai0,pet0)
kg0=KG['1991-2020']
mask=(kg0>0)&(kg0!=30)&(lat[:,None]>-60)&np.all(np.isfinite(S0),0)
np.save(f'{O}/mask.npy',mask)
# ---- points
p=pd.read_csv(f'{D}/points_topsoil.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1); c_=((p.X+180)*6).astype(int).clip(0,W-1)
X=S0[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
blk=(np.floor(p.X/5)*100+np.floor(p.Y/5)).values
par=dict(n_estimators=400,max_depth=7,learning_rate=0.06,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
cv={}
def sel(col,lo,hi):
    y=p[col].values; return ok&np.isfinite(y)&(y>=lo)&(y<=hi)
mP=sel('phaq',2,11); mS=sel('sic',0,150); mO=sel('soc',0,580); mB=sel('bdfiod',0.1,2.2)&np.isfinite(p.soc.values)
yP=p.phaq.values; yS=p.sic.values; yO=p.soc.values; yB=p.bdfiod.values
XB=np.column_stack([X,np.log1p(np.nan_to_num(yO))])
def fitset(idx_boot=None):
    """fit pH, SIC hurdle (clf+reg), SOC log + smearing, BD PTF; idx_boot: dict of index arrays"""
    M={}
    i=idx_boot['P']; M['P']=xgb.XGBRegressor(**par).fit(X[i],yP[i])
    i=idx_boot['S']; M['Sc']=xgb.XGBClassifier(**par,eval_metric='logloss').fit(X[i],(yS[i]>0.1).astype(int))
    j=i[yS[i]>0.1]; M['Sr']=xgb.XGBRegressor(**par).fit(X[j],np.log(yS[j])); M['Ss']=float(np.mean(np.exp(np.log(yS[j])-M['Sr'].predict(X[j]))))
    i=idx_boot['O']; M['O']=xgb.XGBRegressor(**par).fit(X[i],np.log1p(yO[i])); M['Os']=float(np.mean(np.exp(np.log1p(yO[i])-M['O'].predict(X[i]))))
    i=idx_boot['B']; M['B']=xgb.XGBRegressor(**par).fit(XB[i],yB[i])
    return M
def pred(M,F):
    ph=M['P'].predict(F)
    sic=M['Sc'].predict_proba(F)[:,1]*np.exp(M['Sr'].predict(F))*M['Ss']
    soc=np.clip((1+np.expm1(M['O'].predict(F)))*M['Os']-1,0,580)
    bd=np.clip(M['B'].predict(np.column_stack([F,np.log1p(soc)])),0.1,2.0)
    return ph,sic,soc,bd
# ---- spatial block CV (5 deg) for the full v2 pipeline
allidx={'P':np.where(mP)[0],'S':np.where(mS)[0],'O':np.where(mO)[0],'B':np.where(mB)[0]}
gkf=GroupKFold(5); folds=list(gkf.split(np.arange(len(p)),groups=blk))
cvp={k:np.full(len(p),np.nan) for k in ['P','S','O','B','Sprob']}
for tri,tei in folds:
    trs=set(tri); idx={k:np.array([i for i in v if i in trs]) for k,v in allidx.items()}
    M=fitset(idx); F=X[tei]; ph,sic,soc,bd=pred(M,F)
    cvp['P'][tei]=ph; cvp['S'][tei]=sic; cvp['O'][tei]=soc; cvp['Sprob'][tei]=M['Sc'].predict_proba(F)[:,1]
    cvp['B'][tei]=M['B'].predict(np.column_stack([F,np.log1p(np.nan_to_num(yO[tei]))]))
def met(m,y,pr,lg=False):
    y,pr=y[m],pr[m]; d=dict(n=int(m.sum()),r2=float(r2_score(y,pr)),rmse=float(mean_squared_error(y,pr)**.5),bias=float(np.mean(pr-y)))
    if lg: d['r2_log']=float(r2_score(np.log1p(y),np.log1p(np.clip(pr,0,None))))
    return d
cv['pH']=met(mP,yP,cvp['P']); cv['SIC']=met(mS,yS,cvp['S'],True); cv['SOC']=met(mO,yO,cvp['O'],True); cv['BD']=met(mB,yB,cvp['B'])
cv['SIC_presence_AUC']=float(roc_auc_score((yS[mS]>0.1).astype(int),cvp['Sprob'][mS]))
print(json.dumps(cv,indent=1),flush=True); json.dump(cv,open(f'{O}/cv_metrics_v2.json','w'),indent=1)
# ---- full model + SHAP + AOA
Mfull=fitset(allidx)
imp={}
for k,mod,ii in [('pH',Mfull['P'],allidx['P']),('SIC_presence',Mfull['Sc'],allidx['S']),('SIC_amount',Mfull['Sr'],allidx['S'][yS[allidx['S']]>0.1]),('SOC',Mfull['O'],allidx['O'])]:
    sidx=np.random.default_rng(1).choice(ii,min(3000,len(ii)),replace=False)
    sv=shap.TreeExplainer(mod).shap_values(X[sidx]); sv=sv if sv.ndim==2 else sv[...,1]
    np.save(f'{O}/shap_{k}.npy',sv); np.save(f'{O}/shapX_{k}.npy',X[sidx]); imp[k]=np.abs(sv).mean(0)
json.dump({k:dict(zip(names,map(float,v))) for k,v in imp.items()},open(f'{O}/shap_importance.json','w'),indent=1)
json.dump(names,open(f'{O}/names.json','w'))
# AOA (Meyer & Pebesma 2021) on union of training points, weights = mean of normalized SHAP importances
wts=np.mean([v/v.sum() for v in imp.values()],0)
tr=np.unique(np.concatenate(list(allidx.values()))); mu=X[tr].mean(0); sd=X[tr].std(0)+1e-9
Z=(X[tr]-mu)/sd*wts
sub=np.random.default_rng(2).choice(len(tr),min(20000,len(tr)),replace=False)
dbar=np.mean(np.linalg.norm(Z[sub[:2000],None,:]-Z[None,sub[:2000],:],axis=2))
foldof=np.zeros(len(p),int)
for k,(a,b) in enumerate(folds): foldof[b]=k
nnall=NearestNeighbors(n_neighbors=1).fit(Z)
cvdi=[]
for k in range(5):
    a=np.where(foldof[tr]!=k)[0]; b=np.where(foldof[tr]==k)[0]
    bb=np.random.default_rng(k).choice(b,min(3000,len(b)),replace=False)
    cvdi.append(NearestNeighbors(n_neighbors=1).fit(Z[a]).kneighbors(Z[bb])[0][:,0])
cvdi=np.concatenate(cvdi)/dbar; q1,q3=np.percentile(cvdi,[25,75]); thr=q3+1.5*(q3-q1)
Fg=S0[:,mask].T; DI=nnall.kneighbors((Fg-mu)/sd*wts)[0][:,0]/dbar
aoa=np.zeros((H,W),bool); aoa[mask]=DI<=thr; np.save(f'{O}/aoa.npy',aoa)
print('AOA thr',thr,'frac inside',aoa[mask].mean(),flush=True)
# ---- bootstrap (spatial-block resampling) x GCM ensemble
B=int(os.environ.get('NBOOT',10)); ub=np.unique(blk)
GCMS=['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']
SC=[(s,pr) for s in ('126','245','370','585') for pr in ('2041-2060','2081-2100')]
def futstack(g,s,pr):
    f=f'{D}/cmip6/wc2.1_10m_%s_{g}_ssp{s}_{pr}.tif'
    if not all(os.path.exists(f%v) for v in ['bioc','tmin','tmax','prec']): return None
    b=rd(f%'bioc'); b=np.where(np.isfinite(b),b,bio); ai,pet=arid(rd(f%'tmin'),rd(f%'tmax'),rd(f%'prec'))
    ai=np.where(np.isfinite(ai),ai,ai0); pet=np.where(np.isfinite(pet),pet,pet0)
    return stack(b,ai,pet)[:,mask].T
FUT={}
for g in GCMS:
    for s,pr in SC:
        F=futstack(g,s,pr)
        if F is not None: FUT[(g,s,pr)]=F
print('future stacks',len(FUT),flush=True)
np.save(f'{O}/fut_keys.npy',np.array([f'{g}|{s}|{pr}' for g,s,pr in FUT]))
area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
pts_cf=pd.Series(p.cfvo.values,index=kg0[r_,c_]).groupby(level=0).median()
cfz=np.full(31,np.nanmedian(p.cfvo)); cfz[pts_cf.index.values]=pts_cf.values; CF=cfz[kg0[mask]]
for b in range(B):
    rng=np.random.default_rng(100+b); chosen=rng.choice(ub,len(ub),replace=True)
    cnt=pd.Series(chosen).value_counts()
    rep=np.repeat(np.arange(len(p)),pd.Series(blk).map(cnt).fillna(0).astype(int).values)
    idx={k:rep[np.isin(rep,v)] for k,v in allidx.items()}
    M=fitset(idx); ph,sic,soc,bd=pred(M,Fg)
    np.savez_compressed(f'{O}/boot{b:02d}_present.npz',ph=ph.astype('float32'),sic=sic.astype('float32'),soc=soc.astype('float32'),bd=bd.astype('float32'))
    out={}
    for key,F in FUT.items():
        fph,fsic,fsoc,_=pred(M,F)
        out['|'.join(key)]=np.stack([fph,fsic,fsoc]).astype('float16')
    np.savez_compressed(f'{O}/boot{b:02d}_future.npz',**out); print('boot',b,flush=True)
np.save(f'{O}/area.npy',area); np.save(f'{O}/CF.npy',CF)
print('DONE')
