# v6: random 5-fold CV metrics on v5 spline-harmonised points (primary accuracy for paper; matches Huang reporting style)
import numpy as np, pandas as pd, json, os, xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, roc_auc_score, mean_squared_error
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O='/workspace/soil_global/out/v6'
p=pd.read_csv(f'{D}/points_v5_spline.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
par=dict(n_estimators=250,max_depth=7,learning_rate=0.07,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
ORG=120.0; folds=list(KFold(5,shuffle=True,random_state=0).split(X))
def mets(y,pr,lg=False):
    d=dict(n=int(len(y)),r2=float(r2_score(y,pr)),rmse=float(np.sqrt(np.mean((y-pr)**2))))
    if lg: d['r2_log']=float(r2_score(np.log1p(y),np.log1p(np.clip(pr,0,None))))
    return d
out={}
for a,b in [(0,30),(30,100),(100,200)]:
    s=f'_{a}_{b}'; ph=p['phaq'+s].values.copy(); tq=p['tceq'+s].values; sic=p['sic'+s].values.copy()
    soc=p['soc'+s].values.copy(); bd=p['bdfiod'+s].values.copy()
    ph[(ph<3)|(ph>11)]=np.nan; sic[(tq<0)|(tq>1000)]=np.nan; sic[(tq>10)&(ph<5.5)]=np.nan
    soc[(soc<0)|(soc>580)]=np.nan; bd[(bd<0.1)|(bd>2.2)]=np.nan
    org=soc>ORG; top=p['soc_0_30'].values; inv=(a>0)&np.isfinite(top)&(soc>3*np.maximum(top,1))&(soc>20)&~org
    mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic); mO=ok&np.isfinite(soc); mM=mO&~org&~inv
    mB=mM&np.isfinite(bd)
    o={}
    # pH
    pr=np.full(len(p),np.nan)
    for tr,te in folds:
        t=tr[mP[tr]]; pr[te]=xgb.XGBRegressor(**par).fit(X[t],ph[t]).predict(X[te])
    o['pH']=mets(ph[mP],pr[mP])
    # SIC hurdle (pH OOF as covariate within fold)
    pS=np.full(len(p),np.nan); pb=np.full(len(p),np.nan); pho=np.full(len(p),np.nan)
    for tr,te in folds:
        t=tr[mP[tr]]; pho[te]=xgb.XGBRegressor(**par).fit(X[t],ph[t]).predict(X[te])
    XS=np.column_stack([X,pho])
    for tr,te in folds:
        t=tr[mS[tr]]; C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[t],(sic[t]>0.1).astype(int))
        j=t[sic[t]>0.1]; R=xgb.XGBRegressor(**par).fit(XS[j],np.log(sic[j])); sm=np.mean(np.exp(np.log(sic[j])-R.predict(XS[j])))
        pb[te]=C.predict_proba(XS[te])[:,1]; pS[te]=pb[te]*np.exp(R.predict(XS[te]))*sm
    o['SIC']=mets(sic[mS],pS[mS],True); o['SIC']['AUC']=float(roc_auc_score(sic[mS]>0.1,pb[mS])); o['SIC']['zero_frac']=float((sic[mS]<=0.1).mean())
    # mineral SOC + organic classifier
    pO=np.full(len(p),np.nan); pP=np.full(len(p),np.nan)
    for tr,te in folds:
        t=tr[mO[tr]]; pP[te]=xgb.XGBClassifier(**par,eval_metric='logloss').fit(X[t],org[t].astype(int)).predict_proba(X[te])[:,1]
        tm=tr[mM[tr]]; pO[te]=np.expm1(xgb.XGBRegressor(**par).fit(X[tm],np.log1p(soc[tm])).predict(X[te]))
    # combined prediction for evaluation on all SOC points
    socorg=float(np.nanmean(soc[mO&org])) if (mO&org).sum()>10 else 220
    pOc=pP*socorg+(1-pP)*np.clip(pO,0,ORG)
    o['SOC_mineral']=mets(soc[mM],pO[mM],True)
    o['SOC_combined']=mets(soc[mO],pOc[mO],True)
    o['organic_AUC']=float(roc_auc_score(org[mO],pP[mO])) if org[mO].sum()>10 else None
    # BD mineral
    pB=np.full(len(p),np.nan); XB=np.column_stack([X,np.log1p(np.nan_to_num(soc))])
    for tr,te in folds:
        t=tr[mB[tr]]; pB[te]=xgb.XGBRegressor(**par).fit(XB[t],bd[t]).predict(XB[te])
    o['BD']=mets(bd[mB],pB[mB])
    out[s]=o; print(s,json.dumps(o),flush=True)
json.dump(dict(cv='random_5fold',points='points_v5_spline',note='Primary accuracy metrics for paper; Huang 2024 also reports random 10-fold only',metrics=out),open(f'{O}/random_cv.json','w'),indent=1)
print('DONE CV')
