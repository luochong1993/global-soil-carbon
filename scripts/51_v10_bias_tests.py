import numpy as np, pandas as pd, json, os, xgboost as xgb, joblib, netCDF4 as nc, glob
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O7='/workspace/soil_global/out/v7'; O10='/workspace/soil_global/out/v10'; D='/workspace/soil_global/data'
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
hp=json.load(open(f'{O7}/hp_cv.json'))['results']; DEF=dict(n_estimators=400,max_depth=7,learning_rate=0.08,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,n_jobs=8,tree_method='hist')
po={**DEF,**{k:v for k,v in (hp['_0_30']['SOC_mineral'].get('params') or {}).items() if k in DEF}}
area10=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
out={}
# ---- LUCAS depth harmonisation (LUCAS 2018 SOC stocks are 0-20 cm; v7 compared them with 0-30 cm predictions)
L=pd.read_csv(f'{D}/lucas2018_socs.csv'); L.columns=[c.strip() for c in L.columns]
obs=pd.to_numeric(L['SOCS (kg cm-2)'].astype(str).str.strip(),errors='coerce').values*10
la=pd.to_numeric(L.GPS_LAT,errors='coerce').values; lo=pd.to_numeric(L.GPS_LONG,errors='coerce').values
rr=((90-la)*6).astype(int).clip(0,H-1); cc=((lo+180)*6).astype(int).clip(0,W-1)
z=np.load(glob.glob(f'{O7}/maps10_0_30.npz')[0]); soc=np.full((H,W),np.nan); soc[mask]=z['soc']; pr=soc[rr,cc]; k=np.isfinite(pr)&np.isfinite(obs)
def met(o,p_): return dict(n=int(len(o)),bias=float((p_-o).mean()),median_bias=float(np.median(p_-o)),rmse=float(np.sqrt(((p_-o)**2).mean())),r2=float(r2_score(o,p_)),rel_bias=float((p_-o).mean()/o.mean()))
# 0-20/0-30 ratio from Jobbagy & Jackson (2000) beta model, beta 0.96-0.985 (assumption, doi:10.1890/1051-0761(2000)010[0423:TVDOSO]2.0.CO;2)
rat=lambda b:(1-b**20)/(1-b**30)
out['LUCAS']=dict(v7_as_reported_0_30_vs_0_20=met(obs[k],pr[k]),depth_harmonised_ratio=rat(0.978),harmonised=met(obs[k],pr[k]*rat(0.978)),
  harmonised_range=[met(obs[k],pr[k]*rat(0.96))['bias'],met(obs[k],pr[k]*rat(0.985))['bias']],note='LUCAS 2018 topsoil = 0-20 cm (Zenodo 10211884)')
print(out['LUCAS'],flush=True)
# ---- covariate test: add IMAGE 2015 cropland fraction
lu=nc.Dataset(f'{D}/isimip/landuse-5crops_image_ssp126_annual_2015_2100.nc')
fr=sum(np.ma.filled(lu.variables[v][0],0) for v in lu.variables if v not in('lat','lon','time') and lu.variables[v].ndim==3)
fr=fr if lu.variables['lat'][0]>lu.variables['lat'][-1] else fr[::-1]; fr=np.repeat(np.repeat(fr,3,0),3,1).astype('float32')
p=pd.read_csv(f'{D}/points_v7_qc.csv',low_memory=False)
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X0=S0x[:,r_,c_].T; X1=np.column_stack([X0,fr[r_,c_]]); ok=np.all(np.isfinite(X0),1)
cell=(np.floor(p.X.values*2).astype(int)*10000+np.floor(p.Y.values*2).astype(int)); w=pd.Series(cell).map(1/pd.Series(cell).value_counts()).values
soc=p.soc_0_30.values.astype(float); soc[(soc<0)|(soc>580)]=np.nan; m=ok&np.isfinite(soc)&(soc<=120)
kf=KFold(10,shuffle=True,random_state=42); res={}
for lab,X in [('base',X0),('plus_cropfrac',X1)]:
  y=np.log1p(soc[m]); Xm=X[m]; pr_=np.zeros(len(y))
  for a,b in kf.split(Xm): pr_[b]=xgb.XGBRegressor(**po).fit(Xm[a],y[a],sample_weight=w[m][a]).predict(Xm[b])
  res[lab]=dict(cv_r2_conc=float(r2_score(np.expm1(y),np.expm1(pr_))),cv_r2_log=float(r2_score(y,pr_)))
  M=xgb.XGBRegressor(**po).fit(Xm,y,sample_weight=w[m]); Fg_=S0x[:,mask].T if lab=='base' else np.column_stack([S0x[:,mask].T,fr[mask]])
  conc=np.expm1(M.predict(Fg_)).clip(0,120); res[lab]['global_mean_conc']=float((conc*area10).sum()/area10.sum())
  print(lab,res[lab],flush=True)
# LUCAS effect of crop covariate: ratio of conc maps applied to v7 stock map
out['cropfrac_test']=res
r=res['plus_cropfrac']['global_mean_conc']/res['base']['global_mean_conc']; out['cropfrac_test']['global_conc_ratio']=r
# ---- SIC: weighting sensitivity (Huang did not decluster)
sic=p.sic_0_30.values.astype(float); sic[(sic<0)|(sic>120)]=np.nan
out['note']='Adoption rule: adopt only if random-CV not degraded and LUCAS (independent) improves.'
json.dump(out,open(f'{O10}/bias_tests.json','w'),indent=1); print('DONE')
