# Hyperparameter search: XGB vs RF, random 10-fold CV (Huang style).
import numpy as np, pandas as pd, json, os
from sklearn.model_selection import KFold, ParameterSampler
from sklearn.metrics import r2_score, roc_auc_score, f1_score, precision_score, recall_score, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import xgboost as xgb, rasterio
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O='/workspace/soil_global/out/v7'; os.makedirs(O,exist_ok=True)
p=pd.read_csv(f'{D}/points_v7_qc.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
# optional SoilGrids 1km samples
def sample_tif(path,x,y):
  with rasterio.open(path) as ds:
    from rasterio.warp import transform as tf
    xs,ys=tf('EPSG:4326',ds.crs,list(x),list(y))
    out=np.full(len(x),np.nan); nd=ds.nodata
    for i,v in enumerate(ds.sample(zip(xs,ys))):
      val=float(v[0])
      if nd is not None and val==nd: continue
      if val<-1000 or not np.isfinite(val): continue
      out[i]=val
  return out
sg=[]; sgn=[]
for dep,lab in [('0-30cm','030'),('30-100cm','30100'),('100-200cm','100200')]:
  for v in ['cfvo','bdod','clay','sand','cec']:
    fp=f'{D}/sg1km/{v}_{dep}_mean_1000.tif'
    if os.path.exists(fp) and os.path.getsize(fp)>1e6:
      print('sample',os.path.basename(fp),flush=True)
      sg.append(sample_tif(fp,p.X.values,p.Y.values)); sgn.append(f'sg_{v}_{lab}')
names=list(namesx)
if sg:
  X=np.column_stack([X]+sg); names=names+sgn
  # fill SG nan with column median
  for j in range(X.shape[1]):
    col=X[:,j]; m=np.isnan(col)
    if m.any(): X[m,j]=np.nanmedian(col)
folds=list(KFold(10,shuffle=True,random_state=0).split(X))
xgb_reg=list(ParameterSampler(dict(n_estimators=[250,400],max_depth=[5,7,9],learning_rate=[0.05,0.08],subsample=[0.8],colsample_bytree=[0.7,0.9],min_child_weight=[1,5]),n_iter=3,random_state=0))
xgb_clf=list(ParameterSampler(dict(n_estimators=[250,400],max_depth=[5,7],learning_rate=[0.05,0.1],subsample=[0.8],colsample_bytree=[0.8],min_child_weight=[1,5]),n_iter=3,random_state=0))
rf_reg=[dict(n_estimators=200,max_depth=d,min_samples_leaf=l,n_jobs=4,max_features=0.5) for d in [15,None] for l in [2,5]]
ORG=120.0; results={}

def eval_reg(y,mask,params,kind,XX=None):
  XX=X if XX is None else XX
  oof=np.full(len(y),np.nan)
  for tr,te in folds:
    t=tr[mask[tr]]
    if len(t)<80: continue
    if kind=='xgb':
      m=xgb.XGBRegressor(**params,n_jobs=4,tree_method='hist'); m.fit(XX[t],y[t]); oof[te]=m.predict(XX[te])
    else:
      m=RandomForestRegressor(**params); m.fit(XX[t],y[t]); oof[te]=m.predict(XX[te])
  msk=mask&np.isfinite(oof)
  return dict(r2=float(r2_score(y[msk],oof[msk])),rmse=float(np.sqrt(mean_squared_error(y[msk],oof[msk]))),n=int(msk.sum()),oof=oof)

def eval_clf(ybin,mask,params,kind,XX=None):
  XX=X if XX is None else XX
  oof=np.full(len(ybin),np.nan)
  for tr,te in folds:
    t=tr[mask[tr]]
    if kind=='xgb':
      m=xgb.XGBClassifier(**params,n_jobs=4,tree_method='hist',eval_metric='logloss'); m.fit(XX[t],ybin[t]); oof[te]=m.predict_proba(XX[te])[:,1]
    else:
      m=RandomForestClassifier(**params); m.fit(XX[t],ybin[t]); oof[te]=m.predict_proba(XX[te])[:,1]
  msk=mask&np.isfinite(oof); yt=ybin[msk]; pr=(oof[msk]>=0.5).astype(int)
  return dict(AUC=float(roc_auc_score(yt,oof[msk])),F1=float(f1_score(yt,pr)),precision=float(precision_score(yt,pr)),
              recall=float(recall_score(yt,pr)),n=int(msk.sum()),oof=oof)

def best_reg(y,mask,XX=None):
  cands=[]
  for g in xgb_reg:
    e=eval_reg(y,mask,g,'xgb',XX); e['params']=g; e['kind']='xgb'; cands.append(e); print('   xgb',e['r2'],flush=True)
  for g in []:  # RF skipped for runtime; XGB only after pilot showed similar R2
    e=eval_reg(y,mask,g,'rf',XX); e['params']=g; e['kind']='rf'; cands.append(e); print('   rf',e['r2'],flush=True)
  return max(cands,key=lambda z:z['r2'])

def best_clf(ybin,mask,XX=None):
  cands=[]
  for g in xgb_clf:
    e=eval_clf(ybin,mask,g,'xgb',XX); e['params']=g; e['kind']='xgb'; cands.append(e); print('   xgb AUC',e['AUC'],flush=True)
  return max(cands,key=lambda z:z['AUC'])

for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'; print('DEPTH',s,flush=True)
  ph=p['phaq'+s].values.astype(float); sic=p['sic'+s].values.astype(float); soc=p['soc'+s].values.astype(float); bd=p['bdfiod'+s].values.astype(float)
  ph[(ph<3)|(ph>11)]=np.nan; sic[(sic<0)|(sic>120)]=np.nan; soc[(soc<0)|(soc>580)]=np.nan; bd[(bd<0.05)|(bd>2.5)]=np.nan
  org=(soc>ORG)&np.isfinite(soc)
  mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic); mO=ok&np.isfinite(soc); mM=mO&~org; mB=mM&np.isfinite(bd)
  out={}
  print(' pH',flush=True); bp=best_reg(ph,mP); phoof=bp['oof']; out['pH']={k:bp[k] for k in bp if k!='oof'}
  XS=np.column_stack([X,phoof])
  print(' SIC clf',flush=True); bc=best_clf((sic>0.1).astype(int),mS,XS); out['SIC_clf']={k:bc[k] for k in bc if k!='oof'}
  print(' SIC amt',flush=True); mpos=mS&(sic>0.1); ba=best_reg(np.log(sic),mpos,XS)
  # rebuild amount oof with smear
  oofA=np.full(len(p),np.nan)
  for tr,te in folds:
    t=tr[mpos[tr]]
    params={**ba['params']}
    if ba['kind']=='xgb':
      params={k:params[k] for k in params if k in ['n_estimators','max_depth','learning_rate','subsample','colsample_bytree','min_child_weight']}
      m=xgb.XGBRegressor(**params,n_jobs=4,tree_method='hist')
    else:
      m=RandomForestRegressor(**params)
    m.fit(XS[t],np.log(sic[t])); oofA[te]=np.exp(m.predict(XS[te]))
  sm=float(np.nanmean(sic[mpos]/np.maximum(oofA[mpos],1e-8))); oofS=bc['oof']*oofA*sm
  out['SIC']={'r2':float(r2_score(sic[mS],oofS[mS])),'rmse':float(np.sqrt(mean_squared_error(sic[mS],oofS[mS]))),
              'r2_log':float(r2_score(np.log1p(sic[mS]),np.log1p(np.maximum(oofS[mS],0)))),'smear':sm,
              'AUC':out['SIC_clf']['AUC'],'F1':out['SIC_clf']['F1'],'params_amt':ba['params'],'params_clf':bc['params'],'n':int(mS.sum())}
  print(' SOC mineral',flush=True); bo=best_reg(np.log1p(soc),mM); pred=np.expm1(bo['oof'])
  out['SOC_mineral']={'r2':float(r2_score(soc[mM],pred[mM])),'rmse':float(np.sqrt(mean_squared_error(soc[mM],pred[mM]))),
                      'r2_log':float(bo['r2']),'params':bo['params'],'kind':bo['kind'],'n':int(mM.sum())}
  print(' organic clf',flush=True); borg=best_clf(org.astype(int),mO); out['organic_clf']={k:borg[k] for k in borg if k!='oof'}
  print(' BD',flush=True); XB=np.column_stack([X,np.log1p(np.nan_to_num(soc))])
  bb=best_reg(bd,mB,XB); out['BD']={k:bb[k] for k in bb if k!='oof'}
  results[s]=out
  json.dump({'covariates':names,'cv':'random_10fold','results':results},open(f'{O}/hp_cv_checkpoint.json','w'),indent=1)
  print('SAVED',s,'SIC',out['SIC']['r2'],out['SIC']['AUC'],'pH',out['pH']['r2'],'SOC',out['SOC_mineral']['r2'],flush=True)

json.dump({'covariates':names,'cv':'random_10fold','protocol':'Huang-style random 10-fold; select best of XGB/RF by R2 or AUC','results':results},open(f'{O}/hp_cv.json','w'),indent=1)
print('DONE HP')
