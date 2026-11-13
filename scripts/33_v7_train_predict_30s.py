# Train final models with best HP (or defaults); predict present maps at 30 arcsec in tiles.
# Climate: WorldClim 30s bio via /vsizip; topo: elev 30s; soil: SoilGrids 1000m warped to 30s tile;
# GLiM/aridity from 10' bilinear. Future: 30s present + 10' CMIP6 anomalies (delta method).
import numpy as np, pandas as pd, json, os, xgboost as xgb, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.windows import Window
O='/workspace/soil_global/out/v7'; D='/workspace/soil_global/data'; os.makedirs(O+'/maps30s',exist_ok=True)
# load HP
hp=json.load(open(f'{O}/hp_cv.json')) if os.path.exists(f'{O}/hp_cv.json') else (json.load(open(f'{O}/hp_cv_interim.json')) if os.path.exists(f'{O}/hp_cv_interim.json') else json.load(open(f'{O}/hp_cv_checkpoint.json')))
# defaults if missing
def pget(depth,key,default):
  try: return hp['results'][depth][key]['params'] if 'params' in hp['results'][depth][key] else hp['results'][depth][key].get('params_amt',default)
  except: return default
DEF=dict(n_estimators=400,max_depth=7,learning_rate=0.08,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,n_jobs=4,tree_method='hist')

# --- build 10' covariate stack for training (same as v4) + optional SG
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
p=pd.read_csv(f'{D}/points_v7_qc.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
# cell declustering weights (1/n in 0.5° cells) for SOC bias
cell=(np.floor(p.X.values*2).astype(int)*10000+np.floor(p.Y.values*2).astype(int))
cnt=pd.Series(cell).value_counts(); w_cell=pd.Series(cell).map(1.0/cnt).values

ORG=120.0; models={}; meta={}
for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'
  ph=p['phaq'+s].values.astype(float); sic=p['sic'+s].values.astype(float)
  soc=p['soc'+s].values.astype(float); bd=p['bdfiod'+s].values.astype(float); cf=p['cfvo'+s].values.astype(float)
  ph[(ph<3)|(ph>11)]=np.nan; sic[(sic<0)|(sic>120)]=np.nan; soc[(soc<0)|(soc>580)]=np.nan
  bd[(bd<0.05)|(bd>2.5)]=np.nan; cf[(cf<0)|(cf>90)]=np.nan
  org=np.isfinite(soc)&(soc>ORG); mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic); mO=ok&np.isfinite(soc); mM=mO&~org; mB=mM&np.isfinite(bd)
  # params
  try: pp=hp['results'][s]['pH']['params']; 
  except: pp=DEF
  try: pc=hp['results'][s]['SIC'].get('params_clf') or hp['results'][s]['SIC_clf']['params']
  except: pc=DEF
  try: pa=hp['results'][s]['SIC'].get('params_amt') or DEF
  except: pa=DEF
  try: po=hp['results'][s]['SOC_mineral']['params']
  except: po=DEF
  MpH=xgb.XGBRegressor(**{**DEF,**{k:pp[k] for k in pp if k in DEF or k in ['n_estimators','max_depth','learning_rate','subsample','colsample_bytree','min_child_weight']}}).fit(X[mP],ph[mP],sample_weight=w_cell[mP])
  pho=MpH.predict(X); XS=np.column_stack([X,pho])
  C=xgb.XGBClassifier(**{**DEF,**{k:pc[k] for k in pc if k in DEF}},eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int),sample_weight=w_cell[mS])
  j=np.where(mS&(sic>0.1))[0]
  R=xgb.XGBRegressor(**{**DEF,**{k:pa[k] for k in pa if k in DEF}}).fit(XS[j],np.log(sic[j]),sample_weight=w_cell[j])
  sm=float(np.average(np.exp(np.log(sic[j])-R.predict(XS[j])),weights=w_cell[j]))
  Porg=xgb.XGBClassifier(**DEF,eval_metric='logloss').fit(X[mO],org[mO].astype(int),sample_weight=w_cell[mO])
  MO=xgb.XGBRegressor(**{**DEF,**{k:po[k] for k in po if k in DEF}}).fit(X[mM],np.log1p(soc[mM]),sample_weight=w_cell[mM])
  MB=xgb.XGBRegressor(**DEF).fit(np.column_stack([X,np.log1p(np.nan_to_num(soc))])[mB],bd[mB],sample_weight=w_cell[mB])
  # organic C density mean(SOC*BD)
  oo=mO&org&np.isfinite(bd); cd=float((soc[oo]*bd[oo]).mean()) if oo.sum()>30 else 120.0
  bdorg=float(bd[oo].mean()) if oo.sum()>30 else 0.4
  socorg=float(soc[oo].mean()) if oo.sum()>30 else 220.0
  models[s]=dict(MpH=MpH,C=C,R=R,sm=sm,Porg=Porg,MO=MO,MB=MB,cd=cd,bdorg=bdorg,socorg=socorg,CF_med=float(np.nanmedian(cf)))
  meta[s]=dict(n_pH=int(mP.sum()),n_SIC=int(mS.sum()),n_SOC_min=int(mM.sum()),n_org=int(org.sum()),cd=cd,sm=sm)
  print('trained',s,meta[s],flush=True)
json.dump(meta,open(f'{O}/train_meta.json','w'),indent=1)
# PEATMAP scale from 10' quick map first for stocks at 10', then 30s maps
area10=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
Fg=S0x[:,mask].T
stocks10={}
P0=None
for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'; M=models[s]; t=b-a
  ph=M['MpH'].predict(Fg); FS=np.column_stack([Fg,ph])
  sic=M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']
  Po=M['Porg'].predict_proba(Fg)[:,1]
  if P0 is None:
    # scale to PEATMAP 4.23 Mkm2
    k=4.23e6*100/float((Po*area10).sum()); Po=np.clip(Po*k,0,1); P0=Po; meta['Pscale']=k
  else:
    Po=np.minimum(np.clip(Po*meta['Pscale'],0,1),P0); P0=Po
  socm=np.expm1(M['MO'].predict(Fg)).clip(0,ORG); bdm=np.clip(M['MB'].predict(np.column_stack([Fg,np.log1p(socm)])),0.5,2.0)
  # CF: use SoilGrids if available else median
  cf=np.full(Fg.shape[0],M['CF_med'])
  f=(1-np.clip(cf,0,90)/100)*t*0.1
  socS=(Po*M['cd']+(1-Po)*socm*bdm)*f
  sicS=(1-Po)*sic*bdm*f
  stocks10[s]=dict(SOC=float((socS*area10).sum()*1e-9),SIC=float((sicS*area10).sum()*1e-9),
                    SOC_org=float((Po*M['cd']*f*area10).sum()*1e-9),SOC_min=float(((1-Po)*socm*bdm*f*area10).sum()*1e-9))
  np.savez_compressed(f'{O}/maps10_{s}.npz',soc=socS.astype('float32'),sic=sicS.astype('float32'),ph=ph.astype('float32'),
                      P=Po.astype('float32'),socm=socm.astype('float32'),bdm=bdm.astype('float32'))
  print('10\' stocks',s,stocks10[s],flush=True)
json.dump(stocks10,open(f'{O}/stocks10.json','w'),indent=1)
json.dump(meta,open(f'{O}/train_meta.json','w'),indent=1)

# --- 30 arcsec tiled prediction for 0-30 cm (main map); climate from vsizip bio + elev
# Grid: 43200 x 21600, tile 864 cols (2°) x 720 rows
BIOZIP='/vsizip//workspace/soil_global/data/wc30s/bio.zip'
ELEV=f'{D}/wc30s/wc2.1_30s_elev.tif'
# Save models with joblib for tile workers
import joblib
joblib.dump(models,f'{O}/models_v7.joblib')
print('models saved; starting 30s tiles for 0-30cm',flush=True)

# Build static 10' arrays for bilinear lookup
clay10,sand10,cec10=clay,sand,cec  # from exec
glim10=glim; elev10=elev; slope10=slope; tpi10=tpi; ai10_=ai0; pet10_=pet0

def predict_tile(r0,r1,c0,c1,depth='_0_30'):
  """Return soc,sic,ph stock/content arrays for window"""
  M=models[depth]
  # read bios 1-19 and elev
  H=r1-r0; W=c1-c0
  bios=[]
  for i in range(1,20):
    with rasterio.open(f'{BIOZIP}/wc2.1_30s_bio_{i}.tif') as ds:
      a=ds.read(1,window=Window(c0,r0,W,H)).astype('float32'); a[a<-1e30]=np.nan; bios.append(a)
  with rasterio.open(ELEV) as ds:
    ev=ds.read(1,window=Window(c0,r0,W,H)).astype('float32'); ev[ev<-1e30]=np.nan
  # lat/lon of pixel centers
  # WorldClim 30s: transform from_origin(-180,90,1/120,1/120)
  res=1/120.0
  lons=(-180+(np.arange(c0,c1)+0.5)*res)[None,:]
  lats=(90-(np.arange(r0,r1)+0.5)*res)[:,None]
  # map to 10' indices
  rr=((90-lats)*6).astype(int).clip(0,H10-1); cc=((lons+180)*6).astype(int).clip(0,W10-1)
  # stack covariates matching training namesx order: bio1-19, logAI, PET, elev, slope, TPI, clay, sand, CEC, silt, GLiM, carb, evap, unc
  # Approximate AI/PET from 10'
  logAI=ai10_[0][rr,cc] if ai10_.ndim==3 else ai10_[rr,cc]
  PET=pet10_[0][rr,cc] if pet10_.ndim==3 else pet10_[rr,cc]
  sl=slope10[rr,cc]; tp=tpi10[rr,cc]; cl=clay10[rr,cc]; sa=sand10[rr,cc]
  ce=cec10[rr,cc]; si=100-cl-sa; gl=glim10[rr,cc]
  carb=(gl==6).astype('float32'); evap=(gl==14).astype('float32'); unc=(gl==1).astype('float32')
  # use 30s elev where available else 10'
  evu=np.where(np.isfinite(ev),ev,elev10[rr,cc])
  parts=bios+[logAI,PET,evu,sl,tp,cl,sa,ce,si,gl,carb,evap,unc]
  F=np.stack([np.nan_to_num(x,nan=np.nanmedian(x)) for x in parts],0).reshape(len(parts),-1).T.astype('float32')
  land=np.isfinite(bios[0])&(bios[0]>-100)  # rough land
  # also need finite climate
  out_ph=np.full(H*W,np.nan,'float32'); out_sic=out_ph.copy(); out_soc=out_ph.copy()
  if land.sum()==0: return out_ph.reshape(H,W),out_sic.reshape(H,W),out_soc.reshape(H,W),land.reshape(H,W)
  idx=np.where(land.ravel())[0]; Ff=F[idx]
  ph=M['MpH'].predict(Ff); FS=np.column_stack([Ff,ph])
  sic=M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']
  Po=np.clip(M['Porg'].predict_proba(Ff)[:,1]*meta.get('Pscale',0.47),0,1)
  socm=np.expm1(M['MO'].predict(Ff)).clip(0,ORG)
  bdm=np.clip(M['MB'].predict(np.column_stack([Ff,np.log1p(socm)])),0.5,2.0)
  t=int(depth.split('_')[2])-int(depth.split('_')[1]) if False else {' _0_30':30,'_0_30':30,'_30_100':70,'_100_200':100}[depth]
  f=(1-M['CF_med']/100)*t*0.1
  socS=(Po*M['cd']+(1-Po)*socm*bdm)*f
  sicS=(1-Po)*sic*bdm*f
  out_ph[idx]=ph; out_sic[idx]=sicS; out_soc[idx]=socS
  return out_ph.reshape(H,W),out_sic.reshape(H,W),out_soc.reshape(H,W),land.reshape(H,W)

H10,W10=H,W
# Predict a sparse set of tiles for a global mosaic at 30s — full globe is ~50 tiles of 2°×6°; do all land-ish
# For runtime: write COG mosaics by row strips (10° lat)
profile=dict(driver='GTiff',height=21600,width=43200,count=1,dtype='float32',crs='EPSG:4326',
             transform=from_origin(-180,90,1/120,1/120),compress='deflate',tiled=True,predictor=2,zlevel=6,nodata=np.nan)
# Process in 10° latitude strips (1200 rows), 360° width in 6 chunks of 60° (7200 cols) to limit memory
strip_rows=1200; chunk_cols=7200
for var in ['ph030','soc030','sic030']:
  if os.path.exists(f'{O}/maps30s/{var}.tif'): print('skip',var); continue
# Actually write three files strip by strip using mosaic memmap-like append — use rasterio bare create then write windows
paths={k:f'{O}/maps30s/{k}.tif' for k in ['ph_0_30','socstock_0_30','sicstock_0_30']}
for k,path in paths.items():
  if not os.path.exists(path):
    with rasterio.open(path,'w',**profile) as dst: pass
done_flag=f'{O}/maps30s/tiles_done.txt'
done=set(open(done_flag).read().split()) if os.path.exists(done_flag) else set()
for r0 in range(0,21600,strip_rows):
  r1=min(r0+strip_rows,21600)
  for c0 in range(0,43200,chunk_cols):
    c1=min(c0+chunk_cols,43200); key=f'{r0}_{c0}'
    if key in done: continue
    # skip empty polar/ocean strips roughly
    ph,sic,soc,land=predict_tile(r0,r1,c0,c1,'_0_30')
    if land.sum()<100:
      done.add(key); open(done_flag,'a').write(key+'\n'); continue
    win=Window(c0,r0,c1-c0,r1-r0)
    with rasterio.open(paths['ph_0_30'],'r+') as dst: dst.write(ph,1,window=win)
    with rasterio.open(paths['socstock_0_30'],'r+') as dst: dst.write(soc,1,window=win)
    with rasterio.open(paths['sicstock_0_30'],'r+') as dst: dst.write(sic,1,window=win)
    done.add(key); open(done_flag,'a').write(key+'\n')
    print('tile',key,'land',int(land.sum()),flush=True)
print('DONE 30s 0-30')
