import numpy as np, pandas as pd, json, os, xgboost as xgb, joblib, time
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O7='/workspace/soil_global/out/v7'; O8='/workspace/soil_global/out/v8'; D='/workspace/soil_global/data'
while not os.path.exists(f'{O8}/A_done'): time.sleep(30)
mods=joblib.load(f'{O7}/models_v7.joblib')['_0_30']; FM=joblib.load(f'{O8}/fM_models.joblib')
G={}
for n in namesx:
  G[n]='Climate' if (n.startswith('bio') or n in('logAI','PET')) else 'Topography' if n in('elev','slope','TPI') else 'Parent material' if n in('GLiM','carbonate_rock','evaporite','unconsolidated') else 'Soil'
groups=['Climate','Soil','Topography','Parent material','Sampling']
def contrib(model,X,fn,approx=False):
  c=model.get_booster().predict(xgb.DMatrix(X),pred_contribs=True,approx_contribs=approx)[:,:-1]
  out=np.zeros((len(X),len(groups)))
  for j,n in enumerate(fn):
    g=G.get(n,'Soil' if n in('pH_pred',) else 'Sampling'); out[:,groups.index(g)]+=c[:,j]
  return c,out
phg=mods['MpH'].predict(Fg); FS=np.column_stack([Fg,phg]); fnS=namesx+['pH_pred']
FX=np.column_stack([Fg,np.full(len(Fg),15),np.zeros(len(Fg))])
comp={'pH':(mods['MpH'],Fg,namesx),'SIC presence':(mods['C'],FS,fnS),'SIC amount':(mods['R'],FS,fnS),
      'SOC (mineral)':(mods['MO'],Fg,namesx),'fMAOC':(FM['M'],FX,FM['fn'])}
res={}; dom={}; rng=np.random.default_rng(0); samp=rng.choice(len(Fg),30000,replace=False)
for k,(m,X,fn) in comp.items():
  c,g=contrib(m,X[samp],fn); a=np.abs(g); imp=a.mean(0); fimp=np.abs(c).mean(0)
  _,gf=contrib(m,X,fn,approx=True)
  res[k]=dict(group_pct={gg:float(v/imp.sum()*100) for gg,v in zip(groups,imp)},
    top_features=sorted([(fn[j],float(fimp[j]/fimp.sum()*100)) for j in range(len(fn))],key=lambda t:-t[1])[:8])
  dom[k]=np.argmax(np.abs(gf)[:,:4],1).astype('int8')
  np.save(f'{O8}/shap_{k.replace(" ","_").replace("(","").replace(")","")}_sample.npy',np.column_stack([X[samp][:,:len(fn)],c]).astype('float32'))
  print(k,res[k],flush=True)
np.savez_compressed(f'{O8}/dominant_driver.npz',**{k:v for k,v in dom.items()})
json.dump(dict(fn_main=namesx,fnS=fnS,fnM=FM['fn']),open(f'{O8}/shap_names.json','w'))
# PDP + breakpoints
def pdp(m,X,j,q=np.linspace(0.02,0.98,40),transform=None,joint=None):
  Xs=X[rng.choice(len(X),3000,replace=False)].copy(); vals=np.quantile(X[:,j],q); ys=[]
  for v in vals:
    Z=Xs.copy(); Z[:,j]=v
    if joint is not None: Z[:,joint[0]]=v*joint[1]
    p=m.predict_proba(Z)[:,1] if hasattr(m,'predict_proba') else m.predict(Z)
    ys.append(float(np.mean(transform(p) if transform else p)))
  return vals,np.array(ys)
def brk(x,y):
  best=(1e18,None)
  for i in range(4,len(x)-4):
    e=0
    for sl in (slice(0,i+1),slice(i,None)):
      A=np.column_stack([x[sl],np.ones(len(x[sl]))]); r=np.linalg.lstsq(A,y[sl],rcond=None)[1]; e+=r[0] if len(r) else 0
    if e<best[0]: best=(e,float(x[i]))
  return best[1]
inv=lambda z:1/(1+np.exp(-z)); P={}
ix=lambda n,fn: fn.index(n)
for lab,(m,X,fn,feat,tr) in {'SIC_presence_vs_logAI':(mods['C'],FS,fnS,'logAI',None),'SIC_presence_vs_MAP':(mods['C'],FS,fnS,'bio12',None),
   'SIC_presence_vs_pH':(mods['C'],FS,fnS,'pH_pred',None),'SIC_amount_vs_pH':(mods['R'],FS,fnS,'pH_pred',np.exp),
   'fMAOC_vs_clay':(FM['M'],FX,FM['fn'],'clay',inv),'fMAOC_vs_silt':(FM['M'],FX,FM['fn'],'silt',inv),'fMAOC_vs_CEC':(FM['M'],FX,FM['fn'],'CEC',inv),
   'fMAOC_vs_MAT':(FM['M'],FX,FM['fn'],'bio1',inv),'fMAOC_vs_logAI':(FM['M'],FX,FM['fn'],'logAI',inv),
   'SOC_vs_MAT':(mods['MO'],Fg,namesx,'bio1',np.expm1),'SOC_vs_logAI':(mods['MO'],Fg,namesx,'logAI',np.expm1),
   'pH_vs_logAI':(mods['MpH'],Fg,namesx,'logAI',None)}.items():
  x,y=pdp(m,X,ix(feat,fn),transform=tr); P[lab]=dict(x=x.tolist(),y=y.tolist(),breakpoint=brk(x,y)); print(lab,P[lab]['breakpoint'],flush=True)
json.dump(P,open(f'{O8}/pdp.json','w'))
# observed pH–SIC (cf. Huang et al. 2024 Fig.3) + clay+silt vs fMAOC observed
p=pd.read_csv(f'{D}/points_v7_qc.csv',low_memory=False,usecols=['X','Y','phaq_0_30','sic_0_30','soc_0_30'])
ph=p.phaq_0_30.values; sic=p.sic_0_30.values; ok=np.isfinite(ph)&np.isfinite(sic)&(ph>3)&(ph<11)&(sic>=0)&(sic<120)
bins=np.arange(4,10.01,0.25); bc=(bins[:-1]+bins[1:])/2; pr=[];am=[]
for a,b in zip(bins[:-1],bins[1:]):
  s=ok&(ph>=a)&(ph<b); pr.append(float((sic[s]>0.1).mean()) if s.sum()>30 else None); am.append(float(np.median(sic[s][sic[s]>0.1])) if (s&(sic>0.1)).sum()>30 else None)
from scipy.optimize import curve_fit
f=lambda x,k,x0:1/(1+np.exp(-k*(x-x0)))
popt,_=curve_fit(f,ph[ok],(sic[ok]>0.1).astype(float),p0=[3,7.5])
fr=pd.read_csv(f'{O8}/fM_cv_points.csv'); cs=fr.clay+fr.silt; sb=np.arange(0,101,10); fcs=[]
for a,b in zip(sb[:-1],sb[1:]):
  s=(cs>=a)&(cs<b); fcs.append(float(fr.obs[s].median()) if s.sum()>10 else None)
obs=dict(pH_bins=bc.tolist(),P_SIC=pr,SIC_median=am,logistic_k=float(popt[0]),logistic_pH50=float(popt[1]),n=int(ok.sum()),
  claysilt_bins=((sb[:-1]+sb[1:])/2).tolist(),fM_median=fcs,claysilt_breakpoint=brk(cs.values[np.argsort(cs.values)][np.isfinite(cs.values[np.argsort(cs.values)])][::5],fr.obs.values[np.argsort(cs.values)][np.isfinite(cs.values[np.argsort(cs.values)])][::5]) if cs.notna().sum()>50 else None)
json.dump(obs,open(f'{O8}/obs_curves.json','w')); print(obs['logistic_pH50'])
# path analysis (standardized OLS, 0-30 cm points)
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; df=pd.DataFrame(X,columns=namesx); df['pH']=ph; df['lSIC']=np.log1p(sic); df['lSOC']=np.log1p(p.soc_0_30.values)
df=df[['logAI','bio1','clay','carbonate_rock','pH','lSIC','lSOC']].replace([np.inf,-np.inf],np.nan).dropna(); df=df[(df.pH>3)&(df.pH<11)]
z=(df-df.mean())/df.std()
def ols(y,xs):
  A=np.column_stack([z[xs].values,np.ones(len(z))]); b=np.linalg.lstsq(A,z[y].values,rcond=None)[0]; r2=1-np.var(z[y].values-A@b)/np.var(z[y].values)
  return dict(zip(xs,map(float,b[:-1])),R2=float(r2))
sem=dict(n=len(z),pH=ols('pH',['logAI','bio1','clay','carbonate_rock']),SIC=ols('lSIC',['pH','logAI','bio1','clay','carbonate_rock']),
  SOC=ols('lSOC',['pH','logAI','bio1','clay']))
sem['indirect_AI_pH_SIC']=sem['pH']['logAI']*sem['SIC']['pH']; sem['total_AI_SIC']=sem['indirect_AI_pH_SIC']+sem['SIC']['logAI']
json.dump(dict(shap=res,sem=sem,groups=groups,note='Vegetation and N-deposition covariates are not in the v7 covariate stack; SHAP groups are Climate/Soil/Topography/Parent material(+Sampling for fMAOC depth/method).'),open(f'{O8}/drivers_v8.json','w'),indent=1)
print('DONE B',sem)
