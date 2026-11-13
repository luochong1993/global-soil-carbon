import numpy as np, pandas as pd, json, os, xgboost as xgb, joblib
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O='/workspace/soil_global/out/v7'; D='/workspace/soil_global/data'
hp=json.load(open(f'{O}/hp_cv.json')) if os.path.exists(f'{O}/hp_cv.json') else json.load(open(f'{O}/hp_cv_interim.json'))
DEF=dict(n_estimators=400,max_depth=7,learning_rate=0.08,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,n_jobs=4,tree_method='hist')
def merge_params(p):
  if not p: return dict(DEF)
  keys=['n_estimators','max_depth','learning_rate','subsample','colsample_bytree','min_child_weight']
  return {**DEF,**{k:p[k] for k in keys if k in p}}
p=pd.read_csv(f'{D}/points_v7_qc.csv',low_memory=False)
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
cell=(np.floor(p.X.values*2).astype(int)*10000+np.floor(p.Y.values*2).astype(int))
cnt=pd.Series(cell).value_counts(); w_cell=pd.Series(cell).map(1.0/cnt).values
ORG=120.0; models={}; meta={}; area10=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
Fg=S0x[:,mask].T; stocks10={}; P0=None; Pscale=None
for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'
  ph=p['phaq'+s].values.astype(float); sic=p['sic'+s].values.astype(float)
  soc=p['soc'+s].values.astype(float); bd=p['bdfiod'+s].values.astype(float); cf=p['cfvo'+s].values.astype(float)
  ph[(ph<3)|(ph>11)]=np.nan; sic[(sic<0)|(sic>120)]=np.nan; soc[(soc<0)|(soc>580)]=np.nan
  bd[(bd<0.05)|(bd>2.5)]=np.nan; cf[(cf<0)|(cf>90)]=np.nan
  org=np.isfinite(soc)&(soc>ORG); mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic); mO=ok&np.isfinite(soc); mM=mO&~org; mB=mM&np.isfinite(bd)
  rr=hp['results'][s]
  pp=merge_params(rr.get('pH',{}).get('params')); pc=merge_params(rr.get('SIC',{}).get('params_clf') or rr.get('SIC_clf',{}).get('params'))
  pa=merge_params(rr.get('SIC',{}).get('params_amt')); po=merge_params(rr.get('SOC_mineral',{}).get('params'))
  MpH=xgb.XGBRegressor(**pp).fit(X[mP],ph[mP],sample_weight=w_cell[mP])
  pho=MpH.predict(X); XS=np.column_stack([X,pho])
  C=xgb.XGBClassifier(**pc,eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int),sample_weight=w_cell[mS])
  j=np.where(mS&(sic>0.1))[0]
  R=xgb.XGBRegressor(**pa).fit(XS[j],np.log(sic[j]),sample_weight=w_cell[j])
  sm=float(np.average(np.exp(np.log(sic[j])-R.predict(XS[j])),weights=w_cell[j]))
  Porg=xgb.XGBClassifier(**DEF,eval_metric='logloss').fit(X[mO],org[mO].astype(int),sample_weight=w_cell[mO])
  MO=xgb.XGBRegressor(**po).fit(X[mM],np.log1p(soc[mM]),sample_weight=w_cell[mM])
  MB=xgb.XGBRegressor(**DEF).fit(np.column_stack([X,np.log1p(np.nan_to_num(soc))])[mB],bd[mB],sample_weight=w_cell[mB])
  oo=mO&org&np.isfinite(bd); cd=float((soc[oo]*bd[oo]).mean()) if oo.sum()>30 else 120.0
  models[s]=dict(MpH=MpH,C=C,R=R,sm=sm,Porg=Porg,MO=MO,MB=MB,cd=cd,CF_med=float(np.nanmedian(cf)))
  # predict 10'
  phg=MpH.predict(Fg); FS=np.column_stack([Fg,phg])
  sicg=C.predict_proba(FS)[:,1]*np.exp(R.predict(FS))*sm
  Po=Porg.predict_proba(Fg)[:,1]
  if Pscale is None:
    Pscale=4.23e6*100/float((Po*area10).sum()); Po=np.clip(Po*Pscale,0,1); P0=Po
  else:
    Po=np.minimum(np.clip(Po*Pscale,0,1),P0); P0=Po
  socm=np.expm1(MO.predict(Fg)).clip(0,ORG); bdm=np.clip(MB.predict(np.column_stack([Fg,np.log1p(socm)])),0.5,2.0)
  t=b-a; f=(1-models[s]['CF_med']/100)*t*0.1
  socS=(Po*cd+(1-Po)*socm*bdm)*f; sicS=(1-Po)*sicg*bdm*f
  stocks10[s]=dict(SOC=float((socS*area10).sum()*1e-9),SIC=float((sicS*area10).sum()*1e-9),SOC_org=float((Po*cd*f*area10).sum()*1e-9),SOC_min=float(((1-Po)*socm*bdm*f*area10).sum()*1e-9))
  np.savez_compressed(f'{O}/maps10_{s}.npz',soc=socS.astype('float32'),sic=sicS.astype('float32'),ph=phg.astype('float32'),P=Po.astype('float32'),socm=socm.astype('float32'),bdm=bdm.astype('float32'))
  meta[s]=dict(n_pH=int(mP.sum()),n_SIC=int(mS.sum()),n_SOC_min=int(mM.sum()),n_org=int(org.sum()),cd=cd,sm=sm)
  print('trained',s,stocks10[s],flush=True)
meta['Pscale']=Pscale; json.dump(stocks10,open(f'{O}/stocks10.json','w'),indent=1); json.dump(meta,open(f'{O}/train_meta.json','w'),indent=1)
joblib.dump(models,f'{O}/models_v7.joblib'); print('DONE TRAIN10',stocks10)
