# v2: Beck V3 zones, Hargreaves aridity, hurdle SIC, smearing SOC, BD-PTF with SOC, AOA, bootstrap x 6-GCM ensemble
import numpy as np, pandas as pd, rasterio, glob, json, os, xgboost as xgb, shap
from rasterio.warp import reproject, Resampling
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from sklearn.neighbors import NearestNeighbors
D='/workspace/soil_global/data'; O='/workspace/soil_global/out/v3'; os.makedirs(O,exist_ok=True)
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


# ===== v3: lessons from Huang et al. 2024 Science (doi:10.1126/science.adi7918)
from sklearn.model_selection import KFold
cec=warp(f'{D}/sg_cec.tif'); cec[cec<=0]=np.nan; cec=cec/10   # cmol(c)/kg
silt=100-clay-sand
S0x=np.concatenate([S0,cec[None],silt[None]]); namesx=names+['CEC','silt']
mask=mask&np.all(np.isfinite(S0x),0)
p=pd.read_csv(f'{D}/points_topsoil.csv')
# --- outlier / QC rules
n0=len(p)
p=p[(p.phaq.isna())|((p.phaq>=3)&(p.phaq<=11))]
p=p[(p.tceq.isna())|((p.tceq>=0)&(p.tceq<=1000))]
p['dupkey']=p[['X','Y','tceq','phaq','soc']].round(4).fillna(-999).astype(str).agg('_'.join,axis=1)
p=p.drop_duplicates('dupkey')
# physically inconsistent: carbonate present but strongly acid
bad=(p.tceq>10)&(p.phaq<5.5); p=p[~bad]
# robust per-zone screen on log SIC (MAD > 5)
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
p['kg']=kg0[r_,c_]
pos=p.tceq>0; ls=np.log(p.tceq.where(pos)*0.12)
med=ls.groupby(p.kg).transform('median'); mad=(ls-med).abs().groupby(p.kg).transform('median')
z=((ls-med).abs()/(1.4826*mad.clip(lower=0.1)))
madout=(pos&(z>5)).fillna(False); p=p[~madout]
qc=dict(n_in=n0,n_after=len(p),acid_with_carbonate_removed=int(bad.sum()),mad_outliers_removed=int(madout.sum()),sic_rows=int(p.sic.notna().sum()))
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
blk=(np.floor(p.X.values/5)*100+np.floor(p.Y.values/5))
par=dict(n_estimators=400,max_depth=7,learning_rate=0.06,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
yP=p.phaq.values; mP=ok&np.isfinite(yP)
# OOF pH (spatial) as a covariate for SIC, mirroring Huang et al.'s use of soil pH
sp_folds=list(GroupKFold(5).split(X,groups=blk))
phoof=np.full(len(p),np.nan)
for tr,te in sp_folds:
    t=tr[mP[tr]]; m=xgb.XGBRegressor(**par).fit(X[t],yP[t]); phoof[te]=m.predict(X[te])
MpH=xgb.XGBRegressor(**par).fit(X[mP],yP[mP])
cvpH=dict(r2_spatial=float(r2_score(yP[mP],phoof[mP])))
XpH=np.column_stack([X,phoof])
sic_imp=p.sic.values                  # v2 rule: TCEQ missing & pH<6.5 -> 0
sic_meas=(p.tceq*0.12).values         # measured only (Huang et al. use measured zeros)
variants={'V2_base':(X[:,:len(names)],sic_imp),'V3a_+CEC_silt':(X,sic_imp),'V3b_+CEC_silt_pH':(XpH,sic_imp),'V3c_measured_only':(XpH,sic_meas)}
def hurdle_cv(XX,y,folds):
    m=ok&np.isfinite(y); pr=np.full(len(y),np.nan); pb=np.full(len(y),np.nan)
    for tr,te in folds:
        tr=tr[m[tr]]; te=te[m[te]]
        c=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XX[tr],(y[tr]>0.1).astype(int))
        j=tr[y[tr]>0.1]; r=xgb.XGBRegressor(**par).fit(XX[j],np.log(y[j])); s=np.mean(np.exp(np.log(y[j])-r.predict(XX[j])))
        pb[te]=c.predict_proba(XX[te])[:,1]; pr[te]=pb[te]*np.exp(r.predict(XX[te]))*s
    yy,pp,bb=y[m],pr[m],pb[m]; pos=yy>0.1
    return dict(n=int(m.sum()),zero_frac=float((~pos).mean()),AUC=float(roc_auc_score(pos,bb)),r2=float(r2_score(yy,pp)),r2_log=float(r2_score(np.log1p(yy),np.log1p(pp))),rmse=float(np.sqrt(np.mean((yy-pp)**2))),
                r2_pos_log=float(r2_score(np.log(yy[pos]),np.log(np.maximum(pp[pos],1e-3)))))
rnd_folds=list(KFold(10,shuffle=True,random_state=0).split(X))
res={'qc':qc,'pH':cvpH,'variants':{}}
for k,(XX,y) in variants.items():
    res['variants'][k]={'spatial_5deg_5fold':hurdle_cv(XX,y,sp_folds),'random_10fold':hurdle_cv(XX,y,rnd_folds)}
    print(k,json.dumps(res['variants'][k]),flush=True)
    json.dump(res,open(f'{O}/cv_v3.json','w'),indent=1)
# ---- full models (V3b and V3c), maps, futures
Fg=S0x[:,mask].T; phg=MpH.predict(Fg)
bd=np.mean([np.load(f)['bd'] for f in sorted(glob.glob('/workspace/soil_global/out/v2/boot*_present.npz'))],0)
m2=np.load('/workspace/soil_global/out/v2/mask.npy'); bdg=np.full((H,W),np.nan,'float32'); bdg[m2]=bd; bdm=bdg[mask]
bdm=np.where(np.isfinite(bdm),bdm,np.nanmedian(bdm))
pts_cf=pd.Series(p.cfvo.values,index=p.kg.values).groupby(level=0).median(); cfz=np.full(31,np.nanmedian(p.cfvo)); cfz[pts_cf.index.values]=pts_cf.values
CF=cfz[kg0[mask]]
lat2=np.linspace(90,-90,H+1)[:-1]-90/H; area=((111.32/6)**2*np.cos(np.deg2rad(lat2))[:,None]*np.ones((1,W))*100)[mask]
Pg=lambda c,m=None: float(np.nansum((c*bdm*(1-CF/100)*3*area) if m is None else (c*bdm*(1-CF/100)*3*area)[m])*1e-9)
GCMS=['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']
out={}
for vk in ['V3b_+CEC_silt_pH','V3c_measured_only']:
    XX,y=variants[vk]; m=ok&np.isfinite(y)
    C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XX[m],(y[m]>0.1).astype(int)); j=np.where(m&(y>0.1))[0]
    R=xgb.XGBRegressor(**par).fit(XX[j],np.log(y[j])); s=float(np.mean(np.exp(np.log(y[j])-R.predict(XX[j]))))
    f=lambda F,ph: C.predict_proba(np.column_stack([F,ph]))[:,1]*np.exp(R.predict(np.column_stack([F,ph])))*s
    sic0=f(Fg,phg); np.save(f'{O}/sic_present_{vk[:3]}.npy',sic0.astype('float32'))
    d={'present_SIC_Pg_0_30':Pg(sic0),'by_group':{g:Pg(sic0,np.isin(kg0[mask],zs)) for g,zs in {'A':[1,2,3],'B':[4,5,6,7],'C':list(range(8,17)),'D':list(range(17,29)),'E':[29]}.items()}}
    imp=shap.TreeExplainer(R).shap_values(XX[np.random.default_rng(0).choice(j,3000,replace=False)])
    impc=shap.TreeExplainer(C).shap_values(XX[np.random.default_rng(0).choice(np.where(m)[0],3000,replace=False)])
    nm=namesx+['pH_pred']
    d['shap_amount_top']=sorted(zip(nm,np.abs(imp).mean(0).round(4).tolist()),key=lambda t:-t[1])[:6]
    d['shap_presence_top']=sorted(zip(nm,np.abs(impc).mean(0).round(4).tolist()),key=lambda t:-t[1])[:6]
    fut={}
    for sc in ('126','245','370','585'):
        for pr in ('2041-2060','2081-2100'):
            tot=[];phonly=[]
            for g in GCMS:
                fn=f'{D}/cmip6/wc2.1_10m_%s_{g}_ssp{sc}_{pr}.tif'
                b=rd(fn%'bioc'); b=np.where(np.isfinite(b),b,bio); ai,pet=arid(rd(fn%'tmin'),rd(fn%'tmax'),rd(fn%'prec'))
                ai=np.where(np.isfinite(ai),ai,ai0); pet=np.where(np.isfinite(pet),pet,pet0)
                Ff=np.concatenate([stack(b,ai,pet),cec[None],silt[None]])[:,mask].T
                phf=MpH.predict(Ff)
                tot.append(Pg(f(Ff,phf)-sic0)); phonly.append(Pg(f(Fg,phf)-sic0))
            fut[f'ssp{sc}_{pr}']=dict(dSIC_total_mean=float(np.mean(tot)),dSIC_total_range=[float(min(tot)),float(max(tot))],dSIC_pH_pathway_mean=float(np.mean(phonly)),dSIC_pH_pathway_range=[float(min(phonly)),float(max(phonly))])
            print(vk,sc,pr,fut[f'ssp{sc}_{pr}'],flush=True)
    d['future']=fut; out[vk]=d
    res['maps']=out; json.dump(res,open(f'{O}/cv_v3.json','w'),indent=1)
np.save(f'{O}/mask.npy',mask); print('DONE')
