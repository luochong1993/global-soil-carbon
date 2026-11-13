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

# ---- points
p=pd.read_csv(f'{D}/points_topsoil.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1); c_=((p.X+180)*6).astype(int).clip(0,W-1)
X=S0[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
blk=(np.floor(p.X/5)*100+np.floor(p.Y/5)).values
par=dict(n_estimators=400,max_depth=7,learning_rate=0.06,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)

m=sel('soc',0,580) if 'sel' in dir() else None
y=p.soc.values; m=ok&np.isfinite(y)&(y>=0)&(y<=580)
M=xgb.XGBRegressor(**par).fit(X[m],np.log1p(y[m])); r=np.log1p(y[m])-M.predict(X[m])
json.dump({'Os_full':float(np.mean(np.exp(r))),'resid_sd':float(r.std())},open(f'{O}/soc_smear.json','w')); print(open(f'{O}/soc_smear.json').read())
