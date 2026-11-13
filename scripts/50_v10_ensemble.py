# v10: 10 fold-models (random 10-fold, Huang-style) of the FINAL v7 model set, present + all futures + N, one accounting
import numpy as np, pandas as pd, json, os, sys, xgboost as xgb, joblib, netCDF4 as nc
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O7='/workspace/soil_global/out/v7'; O8='/workspace/soil_global/out/v8'; O10='/workspace/soil_global/out/v10'; D='/workspace/soil_global/data'; I=D+'/isimip'
os.makedirs(O10+'/members',exist_ok=True)
MEM=[int(x) for x in sys.argv[1].split(',')]; NJ=int(sys.argv[2]) if len(sys.argv)>2 else 4
hp=json.load(open(f'{O7}/hp_cv.json'))
DEF=dict(n_estimators=400,max_depth=7,learning_rate=0.08,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,n_jobs=NJ,tree_method='hist')
def mp(p):
  if not p: return dict(DEF)
  return {**DEF,**{k:p[k] for k in ['n_estimators','max_depth','learning_rate','subsample','colsample_bytree','min_child_weight'] if k in p}}
p=pd.read_csv(f'{D}/points_v7_qc.csv',low_memory=False)
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
cell=(np.floor(p.X.values*2).astype(int)*10000+np.floor(p.Y.values*2).astype(int)); cnt=pd.Series(cell).value_counts(); wc=pd.Series(cell).map(1.0/cnt).values
from sklearn.model_selection import KFold
folds=list(KFold(10,shuffle=True,random_state=2026).split(X))
ORG=120.0; area10=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
LAY=[(0,30),(30,100),(100,200)]
FM=joblib.load(f'{O8}/fM_models.joblib'); inv=lambda z:1/(1+np.exp(-z))
# ---------- N inputs (IMAGE; SSP2-4.5 = mean of SSP1-2.6 and SSP3-7.0, documented interpolation)
def up(a): return np.repeat(np.repeat(a,3,0),3,1)
def flip(d,a): return a if d.variables['lat'][0]>d.variables['lat'][-1] else a[::-1]
CROPS={'c3ann':['c3ann_irrigated','c3ann_rainfed'],'c3per':['c3per_irrigated_food','c3per_irrigated_bf','c3per_rainfed_food','c3per_rainfed_bf'],
 'c4ann':['c4ann_irrigated','c4ann_rainfed'],'c4per':['c4per_irrigated_food','c4per_irrigated_bf','c4per_rainfed_food','c4per_rainfed_bf'],'c3nfx':['c3nfx_irrigated','c3nfx_rainfed']}
def cumN(s,y0=2020,y1=2050):
  fn=f'{O10}/Nin_{s}_{y0}_{y1}.npz'
  if os.path.exists(fn): z=np.load(fn); return z['Nin'],z['fr']
  if s=='245':
    a,b=cumN('126',y0,y1),cumN('370',y0,y1); Nin,fr=(a[0]+b[0])/2,(a[1]+b[1])/2
  else:
    t0,t1=y0-2015,y1-2015; fe=nc.Dataset(f'{I}/n-fertilizer-5crops_image_2015soc_ssp{s}_annual_2015_2100.nc'); lu=nc.Dataset(f'{I}/landuse-5crops_image_ssp{s}_annual_2015_2100.nc')
    Nc=np.zeros((360,720)); fs=np.zeros((360,720))
    for y in range(t0,t1+1):
      num=np.zeros((360,720)); den=np.zeros((360,720))
      for c,vs in CROPS.items():
        rate=np.ma.filled(fe.variables[f'{c}_fertl'][y],0); fr=sum(np.ma.filled(lu.variables[v][y],0) for v in vs); num+=rate*fr; den+=fr
      Nc+=np.where(den>1e-6,num/den,0); fs+=den
    Nin=up(flip(fe,Nc))[mask]/1000; fr=up(flip(fe,fs/(t1-t0+1)))[mask]
  np.savez_compressed(fn,Nin=Nin.astype('float32'),fr=fr.astype('float32')); return Nin,fr
NS={s:cumN(s) for s in ('126','245','370','585')}
FUT=[(s,g) for s in ('126','245','370','585') for g in GCMS]
for m in MEM:
  outf=f'{O10}/members/m{m}.npz'
  if os.path.exists(outf): print('skip',m); continue
  tr=np.zeros(len(X),bool); tr[folds[m][0]]=True
  mods={}; P0=None; Pscale=None
  for a,b in LAY:
    s=f'_{a}_{b}'
    ph=p['phaq'+s].values.astype(float); sic=p['sic'+s].values.astype(float); soc=p['soc'+s].values.astype(float); bd=p['bdfiod'+s].values.astype(float); cf=p['cfvo'+s].values.astype(float)
    ph[(ph<3)|(ph>11)]=np.nan; sic[(sic<0)|(sic>120)]=np.nan; soc[(soc<0)|(soc>580)]=np.nan; bd[(bd<0.05)|(bd>2.5)]=np.nan; cf[(cf<0)|(cf>90)]=np.nan
    org=np.isfinite(soc)&(soc>ORG); base=ok&tr
    mP=base&np.isfinite(ph); mS=base&np.isfinite(sic); mO=base&np.isfinite(soc); mM=mO&~org; mB=mM&np.isfinite(bd)
    rr=hp['results'][s]
    pp=mp(rr.get('pH',{}).get('params')); pc=mp(rr.get('SIC',{}).get('params_clf') or rr.get('SIC_clf',{}).get('params')); pa=mp(rr.get('SIC',{}).get('params_amt')); po=mp(rr.get('SOC_mineral',{}).get('params'))
    MpH=xgb.XGBRegressor(**pp).fit(X[mP],ph[mP],sample_weight=wc[mP]); XS=np.column_stack([X,MpH.predict(X)])
    C=xgb.XGBClassifier(**pc,eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int),sample_weight=wc[mS])
    j=np.where(mS&(sic>0.1))[0]; R=xgb.XGBRegressor(**pa).fit(XS[j],np.log(sic[j]),sample_weight=wc[j])
    sm=float(np.average(np.exp(np.log(sic[j])-R.predict(XS[j])),weights=wc[j]))
    Porg=xgb.XGBClassifier(**DEF,eval_metric='logloss').fit(X[mO],org[mO].astype(int),sample_weight=wc[mO])
    MO=xgb.XGBRegressor(**po).fit(X[mM],np.log1p(soc[mM]),sample_weight=wc[mM])
    MB=xgb.XGBRegressor(**DEF).fit(np.column_stack([X,np.log1p(np.nan_to_num(soc))])[mB],bd[mB],sample_weight=wc[mB])
    oo=mO&org&np.isfinite(bd); cd=float((soc[oo]*bd[oo]).mean()) if oo.sum()>30 else 120.0
    # held-out fold skill (this member's test fold)
    te=ok&~tr
    mods[s]=dict(MpH=MpH,C=C,R=R,sm=sm,Porg=Porg,MO=MO,MB=MB,cd=cd,CF=float(np.nanmedian(cf[base])))
    print('m',m,'trained',s,flush=True)
  def predict(F,dph=None,only_sic=False):
    out={}; Pprev=None
    for a,b in LAY:
      s=f'_{a}_{b}'; md=mods[s]; t=b-a; fth=(1-md['CF']/100)*t*0.1
      ph=md['MpH'].predict(F); 
      if dph is not None: ph=ph+dph
      FS=np.column_stack([F,ph]); sic=md['C'].predict_proba(FS)[:,1]*np.exp(md['R'].predict(FS))*md['sm']
      if only_sic and 'Po'+s in base_P: Po=base_P['Po'+s]; bdm=base_P['bd'+s]
      else:
        Po=md['Porg'].predict_proba(F)[:,1]; Po=np.clip(Po*Psc,0,1); Po=Po if Pprev is None else np.minimum(Po,Pprev); Pprev=Po
        socm=np.expm1(md['MO'].predict(F)).clip(0,ORG); bdm=np.clip(md['MB'].predict(np.column_stack([F,np.log1p(socm)])),0.5,2.0)
        out['socmin'+s]=(1-Po)*socm*bdm*fth; out['socorg'+s]=Po*md['cd']*fth
      out['sic'+s]=(1-Po)*sic*bdm*fth; out['ph'+s]=ph; out['Po'+s]=Po; out['bd'+s]=bdm
    return out
  Po0=mods['_0_30']['Porg'].predict_proba(Fg)[:,1]; Psc=4.23e6*100/float((Po0*area10).sum())
  base_P={}
  pres=predict(Fg); base_P={k:v for k,v in pres.items() if k.startswith('Po') or k.startswith('bd')}
  fb=FM['boots'][m]; fM0=inv(fb.predict(np.column_stack([Fg,np.full(len(Fg),15),np.zeros(len(Fg))]))); fM1=inv(fb.predict(np.column_stack([Fg,np.full(len(Fg),65),np.zeros(len(Fg))])))
  res=dict(Pscale=Psc,CF={s:mods[s]['CF'] for s in mods})
  T=lambda v: float((v*area10).sum()*1e-9)
  res['present']={s:dict(SOC=T(pres['socmin'+s]+pres['socorg'+s]),SOC_min=T(pres['socmin'+s]),SOC_org=T(pres['socorg'+s]),SIC=T(pres['sic'+s])) for s in mods}
  res['present']['_0_30'].update(MAOC=T(pres['socmin_0_30']*fM0),POC=T(pres['socmin_0_30']*(1-fM0))); res['present']['_30_100'].update(MAOC=T(pres['socmin_30_100']*fM1),POC=T(pres['socmin_30_100']*(1-fM1)))
  save={}
  for s in mods: save['p_soc'+s]=(pres['socmin'+s]+pres['socorg'+s]).astype('float16'); save['p_sic'+s]=pres['sic'+s].astype('float16')
  save['p_ph_0_30']=pres['ph_0_30'].astype('float16'); save['p_MA']=(pres['socmin_0_30']*fM0).astype('float16'); save['p_PO']=(pres['socmin_0_30']*(1-fM0)).astype('float16')
  # ---- future climate
  res['fut']={}
  for (ss,g) in FUT:
    F=np.asarray(futF(g,ss,'2081-2100'),dtype='float32'); fu=predict(F)
    fMf=inv(fb.predict(np.column_stack([F,np.full(len(F),15),np.zeros(len(F))])))
    k=f'{ss}_{g}'; d={}
    for s in mods:
      d['dsoc'+s]=(fu['socmin'+s]+fu['socorg'+s])-(pres['socmin'+s]+pres['socorg'+s]); d['dsic'+s]=fu['sic'+s]-pres['sic'+s]
    d['dph_0_30']=fu['ph_0_30']-pres['ph_0_30']
    d['dMA']=fu['socmin_0_30']*fMf-pres['socmin_0_30']*fM0; d['dPO']=fu['socmin_0_30']*(1-fMf)-pres['socmin_0_30']*(1-fM0)
    res['fut'][k]={kk:T(v) for kk,v in d.items() if kk!='dph_0_30'}; res['fut'][k]['dph_mean']=float((d['dph_0_30']*area10).sum()/area10.sum())
    for kk,v in d.items(): save[f'f_{k}_{kk}']=v.astype('float16')
    print('m',m,k,res['fut'][k]['dsoc_0_30'],res['fut'][k]['dsic_0_30'],flush=True)
  # ---- N pathway (Huang ΔpH=-0.06 Nin+0.11 on cropland, finite difference of this member's SIC model, scaled by cropland fraction)
  res['N']={}
  for ss,(Nin,fr) in NS.items():
    dph=(-0.06*Nin+0.11); dph=np.where(fr>0.001,dph,0.0)
    fu=predict(Fg,dph=dph,only_sic=True); d={}
    for s in mods:
      dd=(fu['sic'+s]-pres['sic'+s])*np.clip(fr,0,1); d['net'+s]=dd; d['loss'+s]=np.minimum(dd,0)
    res['N'][ss]={kk:T(v) for kk,v in d.items()}; res['N'][ss]['dph_crop_mean']=float(dph[fr>0.01].mean()); res['N'][ss]['Nin_crop_mean']=float(Nin[fr>0.01].mean())
    for kk in ('loss_0_30','net_0_30'): save[f'N_{ss}_{kk}']=d[kk].astype('float16')
    save[f'N_{ss}_loss_0_200']=(d['loss_0_30']+d['loss_30_100']+d['loss_100_200']).astype('float16')
    print('m',m,'N',ss,res['N'][ss]['loss_0_30'],flush=True)
  np.savez_compressed(outf,**save); json.dump(res,open(f'{O10}/members/m{m}.json','w'),indent=1)
  print('MEMBER DONE',m,res['present'],flush=True)
