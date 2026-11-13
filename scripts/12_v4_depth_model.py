# v2: Beck V3 zones, Hargreaves aridity, hurdle SIC, smearing SOC, BD-PTF with SOC, AOA, bootstrap x 6-GCM ensemble
import numpy as np, pandas as pd, rasterio, glob, json, os, xgboost as xgb, shap
from rasterio.warp import reproject, Resampling
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from sklearn.neighbors import NearestNeighbors
D='/workspace/soil_global/data'; O='/workspace/soil_global/out/v4'; os.makedirs(O,exist_ok=True); os.makedirs(O+'/futstack',exist_ok=True)
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


from sklearn.model_selection import KFold
cec=warp(f'{D}/sg_cec.tif'); cec[cec<=0]=np.nan; cec=cec/10; silt=100-clay-sand
# GLiM 0.5 deg (Hartmann & Moosdorf 2012, doi:10.1594/PANGAEA.788537)
with open(f'{D}/glim_wgs84_0point5deg.txt.asc') as fh:
    hdr={}; 
    for _ in range(6):
        k,v=fh.readline().split(); hdr[k.lower()]=float(v)
    g=np.loadtxt(fh)
g[g==hdr.get('nodata_value',-9999)]=0
# nearest mapping to 10' grid
yy=((90-(np.arange(H)+0.5)/6 - (hdr['yllcorner']))/hdr['cellsize']).astype(int); yy=g.shape[0]-1-yy
xx=(((np.arange(W)+0.5)/6-180-hdr['xllcorner'])/hdr['cellsize']).astype(int)
yy=yy.clip(0,g.shape[0]-1); xx=xx.clip(0,g.shape[1]-1); glim=g[yy][:,xx].astype('float32')
carb=(glim==6).astype('float32'); evap=(glim==14).astype('float32'); unc=(glim==1).astype('float32')
S0x=np.concatenate([S0,cec[None],silt[None],glim[None],carb[None],evap[None],unc[None]]).astype('float32')
namesx=names+['CEC','silt','GLiM','carbonate_rock','evaporite','unconsolidated']
mask=mask&np.all(np.isfinite(S0x),0); np.save(f'{O}/mask.npy',mask); np.save(f'{O}/glim.npy',glim)
json.dump(namesx,open(f'{O}/names.json','w'))
GCMS=['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']
SC=[(s,pr) for s in ('126','245','370','585') for pr in ('2041-2060','2081-2100')]
extra=np.stack([cec,silt,glim,carb,evap,unc])
def futF(g,s,pr):
    fn=f'{O}/futstack/{g}_{s}_{pr}.npy'
    if os.path.exists(fn): return np.load(fn).astype('float32')
    f=f'{D}/cmip6/wc2.1_10m_%s_{g}_ssp{s}_{pr}.tif'
    b=rd(f%'bioc'); b=np.where(np.isfinite(b),b,bio); ai,pet=arid(rd(f%'tmin'),rd(f%'tmax'),rd(f%'prec'))
    ai=np.where(np.isfinite(ai),ai,ai0); pet=np.where(np.isfinite(pet),pet,pet0)
    F=np.concatenate([stack(b,ai,pet),extra])[:,mask].T; np.save(fn,F.astype('float16')); return F
Fg=S0x[:,mask].T
p=pd.read_csv(f'{D}/points_v4_depths.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1); blk=(np.floor(p.X.values/5)*100+np.floor(p.Y.values/5))
pts_kg=kg0[r_,c_]
par=dict(n_estimators=350,max_depth=7,learning_rate=0.07,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
spf=list(GroupKFold(5).split(X,groups=blk)); rnf=list(KFold(5,shuffle=True,random_state=0).split(X))
def mets(y,pr,lg=False):
    d=dict(n=int(len(y)),r2=float(r2_score(y,pr)),rmse=float(np.sqrt(np.mean((y-pr)**2))))
    if lg: d['r2_log']=float(r2_score(np.log1p(y),np.log1p(np.clip(pr,0,None))))
    return d
for a,b in [(0,30),(30,100),(100,200)]:
    sfx=f'_{a}_{b}'; ck=f'{O}/depth{sfx}.npz'
    if os.path.exists(ck): print('skip',sfx); continue
    ph=p['phaq'+sfx].values.copy(); tq=p['tceq'+sfx].values; sic=p['sic'+sfx].values.copy(); soc=p['soc'+sfx].values.copy(); bd=p['bdfiod'+sfx].values.copy()
    ph[(ph<3)|(ph>11)]=np.nan; sic[(tq<0)|(tq>1000)]=np.nan; sic[(tq>10)&(ph<5.5)]=np.nan
    soc[(soc<0)|(soc>580)]=np.nan; bd[(bd<0.1)|(bd>2.2)]=np.nan
    mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic); mO=ok&np.isfinite(soc); mB=ok&np.isfinite(bd)&np.isfinite(soc)
    cv={}
    phoof=np.full(len(p),np.nan)
    for tr,te in spf:
        t=tr[mP[tr]]; phoof[te]=xgb.XGBRegressor(**par).fit(X[t],ph[t]).predict(X[te])
    cv['pH_spatial']=mets(ph[mP],phoof[mP])
    XS=np.column_stack([X,phoof])
    def cvrun(folds):
        o={}
        pr=np.full(len(p),np.nan)
        for tr,te in folds:
            t=tr[mP[tr]]; pr[te]=xgb.XGBRegressor(**par).fit(X[t],ph[t]).predict(X[te])
        o['pH']=mets(ph[mP],pr[mP])
        pS=np.full(len(p),np.nan); pb=np.full(len(p),np.nan)
        for tr,te in folds:
            t=tr[mS[tr]]; c=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[t],(sic[t]>0.1).astype(int))
            j=t[sic[t]>0.1]; r=xgb.XGBRegressor(**par).fit(XS[j],np.log(sic[j])); sm=np.mean(np.exp(np.log(sic[j])-r.predict(XS[j])))
            pb[te]=c.predict_proba(XS[te])[:,1]; pS[te]=pb[te]*np.exp(r.predict(XS[te]))*sm
        o['SIC']=mets(sic[mS],pS[mS],True); o['SIC']['AUC']=float(roc_auc_score(sic[mS]>0.1,pb[mS])); o['SIC']['zero_frac']=float((sic[mS]<=0.1).mean())
        pO=np.full(len(p),np.nan)
        for tr,te in folds:
            t=tr[mO[tr]]; pO[te]=np.expm1(xgb.XGBRegressor(**par).fit(X[t],np.log1p(soc[t])).predict(X[te]))
        o['SOC']=mets(soc[mO],pO[mO],True)
        pB=np.full(len(p),np.nan); XB=np.column_stack([X,np.log1p(np.nan_to_num(soc))])
        for tr,te in folds:
            t=tr[mB[tr]]; pB[te]=xgb.XGBRegressor(**par).fit(XB[t],bd[t]).predict(XB[te])
        o['BD']=mets(bd[mB],pB[mB]); return o
    cv['spatial_5deg']=cvrun(spf); cv['random_5fold']=cvrun(rnf)
    print(sfx,json.dumps(cv),flush=True); json.dump(cv,open(f'{O}/cv{sfx}.json','w'),indent=1)
    MpH=xgb.XGBRegressor(**par).fit(X[mP],ph[mP])
    C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int)); j=np.where(mS&(sic>0.1))[0]
    R=xgb.XGBRegressor(**par).fit(XS[j],np.log(sic[j])); sm=float(np.mean(np.exp(np.log(sic[j])-R.predict(XS[j]))))
    MO=xgb.XGBRegressor(**par).fit(X[mO],np.log1p(soc[mO]))
    MB=xgb.XGBRegressor(**par).fit(np.column_stack([X,np.log1p(np.nan_to_num(soc))])[mB],bd[mB])
    fS=lambda F,phv: C.predict_proba(np.column_stack([F,phv]))[:,1]*np.exp(R.predict(np.column_stack([F,phv])))*sm
    ph0=MpH.predict(Fg); sic0=fS(Fg,ph0); soc0=np.expm1(MO.predict(Fg)).clip(0,580); bd0=np.clip(MB.predict(np.column_stack([Fg,np.log1p(soc0)])),0.1,2.0)
    cf=pd.Series(p['cfvo'+sfx].values,index=pts_kg).groupby(level=0).median(); cfz=np.full(31,np.nanmedian(p['cfvo'+sfx])); cfz[cf.index.values]=cf.values
    CF=np.nan_to_num(cfz[kg0[mask]],nan=5.0)
    # SHAP
    for nm,mod,XX,ii in [('SICpres',C,XS,np.where(mS)[0]),('SICamt',R,XS,j),('SOC',MO,X,np.where(mO)[0]),('pH',MpH,X,np.where(mP)[0])]:
        si=np.random.default_rng(0).choice(ii,min(2000,len(ii)),replace=False); sv=shap.TreeExplainer(mod).shap_values(XX[si]); sv=sv if sv.ndim==2 else sv[...,1]
        imp=np.abs(sv).mean(0); nn=namesx+(['pH_pred'] if XX.shape[1]>len(namesx) else [])
        cv.setdefault('shap',{})[nm]=sorted(zip(nn,imp.round(4).tolist()),key=lambda t:-t[1])[:8]
    json.dump(cv,open(f'{O}/cv{sfx}.json','w'),indent=1)
    out=dict(ph0=ph0,sic0=sic0,soc0=soc0,bd0=bd0,CF=CF)
    for s,pr in SC:
        acc={k:[] for k in ['ph','sic','sicph','soc']}
        for g in GCMS:
            F=futF(g,s,pr); phf=MpH.predict(F)
            acc['ph'].append(phf-ph0); acc['sic'].append(fS(F,phf)-sic0); acc['sicph'].append(fS(Fg,phf)-sic0); acc['soc'].append(np.expm1(MO.predict(F)).clip(0,580)-soc0)
        for k,v in acc.items():
            v=np.array(v,dtype='float32'); out[f'{k}_{s}_{pr}_mean']=v.mean(0); out[f'{k}_{s}_{pr}_npos']=(v>0).sum(0).astype('uint8')
            out[f'{k}_{s}_{pr}_gcm']=v.astype('float16')
        print(sfx,s,pr,flush=True)
    np.savez(ck,**out); print('saved',ck,flush=True)
print('DONE')
