import numpy as np, pandas as pd, json, os, xgboost as xgb, joblib, glob
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O7='/workspace/soil_global/out/v7'; O8='/workspace/soil_global/out/v8'; D='/workspace/soil_global/data'
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error
# ---------- 1. harmonize Georgiou et al. 2022 synthesis (doi:10.5281/zenodo.5987415)
d=pd.read_csv(f'{D}/frac/MOC_synthesis.csv'); flow={'raw':len(d)}
d=d[d.Lat.notna()&d.Lon.notna()]; flow['with_coords']=len(d)
d=d[d['Top.depth'].notna()&d['Bottom.depth'].notna()&(d['Bottom.depth']>d['Top.depth'])]; flow['with_depth']=len(d)
d['mid']=(d['Top.depth']+d['Bottom.depth'])/2
tot=d.SiltClayC+d.POM_C
d['fM']=np.where(d.POM_C.notna()&(tot>0),d.SiltClayC/tot,d.SiltClayC/d['Bulk.C'])
d['recov']=tot/d['Bulk.C']
d=d[np.isfinite(d.fM)&(d.fM>0)&(d.fM<=1.0)]; flow['fM_in_(0,1]']=len(d)
d=d[(d.fM<0.995)&~(d.POM_C==0)]; flow['drop_fM>=0.995_or_POC=0 (unmeasured POM)']=len(d)
d=d[d.recov.isna()|((d.recov>0.7)&(d.recov<1.3))]; flow['mass_balance_0.7-1.3']=len(d)
d=d[d.mid<=100]; flow['mid<=100cm']=len(d)
d['dens']=(d.frc_method!='Particle_Size').astype(int)
flow['by_method']=d.frc_method.value_counts().to_dict(); flow['by_source']=d.source.value_counts().to_dict()
flow['topsoil_mid<=30']=int((d.mid<=30).sum()); flow['subsoil']=int((d.mid>30).sum())
r_=((90-d.Lat)*6).astype(int).clip(0,H-1).values; c_=((d.Lon+180)*6).astype(int).clip(0,W-1).values
Xg=S0x[:,r_,c_].T; ok=np.all(np.isfinite(Xg),1); d=d[ok]; Xg=Xg[ok]; flow['with_covariates']=len(d)
X=np.column_stack([Xg,d.mid.values,d.dens.values]); fn=namesx+['depth_mid','density_method']
y=np.log(d.fM.values/(1-np.clip(d.fM.values,0,0.995)))  # logit
cell=(np.floor(d.Lon.values*2)*10000+np.floor(d.Lat.values*2)); w=pd.Series(cell).map(1/pd.Series(cell).value_counts()).values
inv=lambda z:1/(1+np.exp(-z))
grid=[dict(n_estimators=n,max_depth=m,learning_rate=lr,subsample=0.8,colsample_bytree=0.7,min_child_weight=mc,n_jobs=4,tree_method='hist')
 for n,m,lr,mc in [(300,4,0.05,3),(500,5,0.03,5),(300,6,0.05,5),(800,3,0.03,3),(400,4,0.05,10)]]
kf=KFold(10,shuffle=True,random_state=42); res=[]
for g in grid:
  pr=np.zeros(len(y))
  for tr,te in kf.split(X): pr[te]=xgb.XGBRegressor(**g).fit(X[tr],y[tr],sample_weight=w[tr]).predict(X[te])
  f=inv(pr); res.append((r2_score(d.fM,f),g,f))
res.sort(key=lambda r:-r[0]); best=res[0][1]; fcv=res[0][2]
cv=dict(n=len(y),R2_fMAOC=res[0][0],RMSE_fMAOC=float(np.sqrt(mean_squared_error(d.fM,fcv))),bias=float((fcv-d.fM).mean()),
  MAOC_conc_R2=float(r2_score((d['Bulk.C']*d.fM)[d['Bulk.C'].notna()],(d['Bulk.C']*fcv)[d['Bulk.C'].notna()])),grid=[(r[0],r[1]) for r in res],
  top_R2=float(r2_score(d.fM[d.mid<=30],fcv[d.mid<=30])))
# repeated CV for spread
rs=[]
for seed in range(5):
  pr=np.zeros(len(y))
  for tr,te in KFold(10,shuffle=True,random_state=seed).split(X): pr[te]=xgb.XGBRegressor(**best).fit(X[tr],y[tr],sample_weight=w[tr]).predict(X[te])
  rs.append(r2_score(d.fM,inv(pr)))
cv['R2_5x10_mean']=float(np.mean(rs)); cv['R2_5x10_sd']=float(np.std(rs))
print('CV',cv['R2_fMAOC'],cv['R2_5x10_mean'],flush=True)
pd.DataFrame(dict(obs=d.fM.values,cv=fcv,mid=d.mid.values,method=d.frc_method.values,lat=d.Lat.values,lon=d.Lon.values,clay=d.Clay.values,silt=d.Silt.values)).to_csv(f'{O8}/fM_cv_points.csv',index=False)
M=xgb.XGBRegressor(**best).fit(X,y,sample_weight=w)
boots=[]; rng=np.random.default_rng(1)
for b in range(50):
  i=rng.integers(0,len(y),len(y)); boots.append(xgb.XGBRegressor(**best).fit(X[i],y[i],sample_weight=w[i]))
joblib.dump(dict(M=M,boots=boots,fn=fn,best=best),f'{O8}/fM_models.joblib')
# ---------- 2. maps 10'
area10=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]  # ha
meta=json.load(open(f'{O7}/train_meta.json')); mods=joblib.load(f'{O7}/models_v7.joblib')
out={'flow':flow,'cv':cv}; maps={}
for s,mid in [('_0_30',15),('_30_100',65)]:
  z=np.load(glob.glob(f'{O7}/maps10_{s[1:]}.npz')[0] if glob.glob(f'{O7}/maps10_{s[1:]}.npz') else f'{O7}/maps10_{s}.npz')
  Fx=np.column_stack([Fg,np.full(len(Fg),mid),np.zeros(len(Fg))])
  fm=inv(M.predict(Fx)); fb=np.array([inv(m.predict(Fx)) for m in boots])
  t=int(s.split('_')[2])-int(s.split('_')[1]); fthk=(1-mods[s]['CF_med']/100)*t*0.1
  org=z['P']*meta[s]['cd']*fthk; mn=z['soc']-org
  MA=mn*fm; PO=mn*(1-fm)
  tb=np.array([(mn*fb_*area10).sum()*1e-9 for fb_ in fb])
  out[s]=dict(SOC_mineral=float((mn*area10).sum()*1e-9),SOC_organic=float((org*area10).sum()*1e-9),
    MAOC=float((MA*area10).sum()*1e-9),POC=float((PO*area10).sum()*1e-9),
    MAOC_CI90=[float(np.percentile(tb,5)),float(np.percentile(tb,95))],
    POC_CI90=[float((mn*area10).sum()*1e-9-np.percentile(tb,95)),float((mn*area10).sum()*1e-9-np.percentile(tb,5))],
    fMAOC_areamean=float((fm*area10).sum()/area10.sum()))
  maps[s]=dict(f=fm.astype('float32'),fsd=fb.std(0).astype('float32'),MA=MA.astype('float32'),PO=PO.astype('float32'))
  print(s,out[s],flush=True)
np.savez_compressed(f'{O8}/frac_maps10.npz',**{k+s:v for s,dd in maps.items() for k,v in dd.items()})
# Georgiou comparison (own sum of their grids, all cells) + their published value
import netCDF4 as nc
x=nc.Dataset(f'{D}/frac/global_MOC.nc'); la=x['lat'][:]; A=(111.32*0.5)**2*np.cos(np.deg2rad(la))[:,None]*1e6
gt=np.ma.filled(x['moc_t'][:].astype(float),np.nan); gs=np.ma.filled(x['moc_s'][:].astype(float),np.nan)
out['Georgiou']=dict(grid_sum_0_30=float(np.nansum(gt*A)/1e12),grid_sum_30_100=float(np.nansum(gs*A)/1e12),
  published_0_100_nonpermafrost=899,published_frac_top=0.66,published_frac_sub=0.70,doi='10.1038/s41467-022-31540-9')
# ---------- 3. future (mineral SOC model v7 + fMAOC model under future climate; 6-GCM mean, 2081-2100)
fut={}
z=np.load(glob.glob(f'{O7}/maps10_0_30.npz')[0]); s='_0_30'; md=mods[s]
t=30; fthk=(1-md['CF_med']/100)*t*0.1
def mineral(F):
  socm=np.expm1(md['MO'].predict(F)).clip(0,120); bdm=np.clip(md['MB'].predict(np.column_stack([F,np.log1p(socm)])),0.5,2.0)
  return (1-z['P'])*socm*bdm*fthk
Fx0=np.column_stack([Fg,np.full(len(Fg),15),np.zeros(len(Fg))])
mn0=mineral(Fg); f0=inv(M.predict(Fx0)); MA0=(mn0*f0*area10).sum()*1e-9; PO0=(mn0*(1-f0)*area10).sum()*1e-9
for ssp in ['126','245','370','585']:
  r=[]
  for g in GCMS:
    try: F=futF(g,ssp,'2081-2100')
    except Exception as e: print('skip',g,ssp,e); continue
    F=np.asarray(F,dtype='float32'); mn=mineral(F); fF=inv(M.predict(np.column_stack([F,np.full(len(F),15),np.zeros(len(F))])))
    r.append([(mn*fF*area10).sum()*1e-9-MA0,(mn*(1-fF)*area10).sum()*1e-9-PO0])
  r=np.array(r); fut[ssp]=dict(n_gcm=len(r),dMAOC_eq=float(r[:,0].mean()),dPOC_eq=float(r[:,1].mean()),
     dMAOC_eq_range=[float(r[:,0].min()),float(r[:,0].max())],dPOC_eq_range=[float(r[:,1].min()),float(r[:,1].max())])
  for tP,tM,lab in [(15,150,'central'),(5,50,'fast'),(30,400,'slow')]:
    fP=1-np.exp(-80/tP); fM_=1-np.exp(-80/tM)
    fut[ssp]['tl_'+lab]=dict(tau_POC=tP,tau_MAOC=tM,dPOC=fut[ssp]['dPOC_eq']*fP,dMAOC=fut[ssp]['dMAOC_eq']*fM_)
  print(ssp,fut[ssp],flush=True)
out['future_0_30']=dict(baseline_MAOC_mineralmodel=float(MA0),baseline_POC=float(PO0),scen=fut,
  note='2081-2100 vs 1970-2000 baseline; t=80 yr from 2020; tau ranges assumption based on Lavallee et al. 2020 GCB doi:10.1111/gcb.14859, Cotrufo et al. 2019 NatGeo doi:10.1038/s41561-019-0484-6')
json.dump(out,open(f'{O8}/fractions_v8.json','w'),indent=1,default=float); print('DONE A'); open(f'{O8}/A_done','w').write('1')
