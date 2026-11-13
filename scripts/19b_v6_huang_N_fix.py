# Fix: Huang ΔpH uses cropland-intensity Nin (MgN per cropland ha), not grid-mean.
# Apply ΔSIC only on the cropland fraction of each cell.
import numpy as np, pandas as pd, json, os, xgboost as xgb, netCDF4 as nc
from scipy.optimize import curve_fit
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O='/workspace/soil_global/out/v6'; I='/workspace/soil_global/data/isimip'
area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
def up(a): return np.repeat(np.repeat(a,3,0),3,1)
def flip(d,a): return a if d.variables['lat'][0]>d.variables['lat'][-1] else a[::-1]
CROPS={'c3ann':['c3ann_irrigated','c3ann_rainfed'],'c3per':['c3per_irrigated_food','c3per_irrigated_bf','c3per_rainfed_food','c3per_rainfed_bf'],
       'c4ann':['c4ann_irrigated','c4ann_rainfed'],'c4per':['c4per_irrigated_food','c4per_irrigated_bf','c4per_rainfed_food','c4per_rainfed_bf'],'c3nfx':['c3nfx_irrigated','c3nfx_rainfed']}
def cum(s,y0,y1):
    t0,t1=(y0-2015),(y1-2015)
    nh=nc.Dataset(f'{I}/ndep-nhx_ssp{s}_monthly_2015_2100.nc'); no=nc.Dataset(f'{I}/ndep-noy_ssp{s}_monthly_2015_2100.nc')
    DEP=flip(nh,np.ma.filled(nh.variables['nhx'][t0*12:(t1+1)*12].sum(0),0))*10 + flip(no,np.ma.filled(no.variables['noy'][t0*12:(t1+1)*12].sum(0),0))*10
    fe=nc.Dataset(f'{I}/n-fertilizer-5crops_image_2015soc_ssp{s}_annual_2015_2100.nc')
    lu=nc.Dataset(f'{I}/landuse-5crops_image_ssp{s}_annual_2015_2100.nc')
    # cropland-intensity: sum_y sum_c (rate_c,y * fr_c,y) / sum_y sum_c fr_c,y  → then * nyears ≈ total Mg/ha cropland
    # equivalent: Nin = sum_y (sum_c rate_c*fr_c / max(sum_c fr_c, eps))
    nyr=t1-t0+1; Nin_crop=np.zeros((360,720)); fr_sum=np.zeros((360,720)); grid_fert=np.zeros((360,720))
    for y in range(t0,t1+1):
        num=np.zeros((360,720)); den=np.zeros((360,720))
        for c,vs in CROPS.items():
            rate=np.ma.filled(fe.variables[f'{c}_fertl'][y],0)
            fr=sum(np.ma.filled(lu.variables[v][y],0) for v in vs)
            num+=rate*fr; den+=fr; grid_fert+=rate*fr
        Nin_crop+=np.where(den>1e-6,num/den,0); fr_sum+=den
    fr_mean=fr_sum/nyr; Nin_crop=flip(fe,Nin_crop); fr_mean=flip(fe,fr_mean); grid_fert=flip(fe,grid_fert); DEP=flip(nh,DEP) if False else DEP
    # DEP already flipped above
    return up(Nin_crop)[mask]/1000, up(fr_mean)[mask], up(grid_fert)[mask], up(DEP)[mask]  # Mg/ha cropland, frac, kg/ha grid, kg/ha dep
# train models (same as 19)
p=pd.read_csv(f'{D}/points_v5_spline.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
par=dict(n_estimators=250,max_depth=7,learning_rate=0.07,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
z5=np.load('/workspace/soil_global/out/v5/maps_b0.npz'); DEP_L=[(0,30),(30,100),(100,200)]
models={}; ph0={}; sic0={}; bdm={}; Porg={}; CF={}
for a,b in DEP_L:
    s=f'_{a}_{b}'; ph=p['phaq'+s].values.copy(); tq=p['tceq'+s].values; sic=p['sic'+s].values.copy()
    ph[(ph<3)|(ph>11)]=np.nan; sic[(tq<0)|(tq>1000)]=np.nan; sic[(tq>10)&(ph<5.5)]=np.nan
    mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic)
    MpH=xgb.XGBRegressor(**par).fit(X[mP],ph[mP]); phoof=MpH.predict(X); XS=np.column_stack([X,phoof])
    C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int))
    j=np.where(mS&(sic>0.1))[0]; R=xgb.XGBRegressor(**par).fit(XS[j],np.log(sic[j]))
    sm=float(np.mean(np.exp(np.log(sic[j])-R.predict(XS[j]))))
    models[s]=dict(MpH=MpH,C=C,R=R,sm=sm)
    phg=MpH.predict(Fg); FS=np.column_stack([Fg,phg])
    sicg=C.predict_proba(FS)[:,1]*np.exp(R.predict(FS))*sm
    ph0[s]=phg; sic0[s]=sicg; Porg[s]=z5['P'+s]; bdm[s]=z5['bdm'+s]
    t=b-a; smap=z5['sic'+s]
    with np.errstate(divide='ignore',invalid='ignore'):
        den=(1-Porg[s])*sicg*bdm[s]*t*0.1; cf=np.clip(np.where(den>1e-6,smap/den,1.0),0.5,1.0)
    CF[s]=cf; print('trained',s,flush=True)

def sic_at(M,F,ph):
    FS=np.column_stack([F,ph]); return M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']
def stock(s,sic,t): return (1-Porg[s])*sic*bdm[s]*CF[s]*t*0.1

# sigmoid fit (fixed)
def sig(x,x0,k,a,b,c): return c+b/(a+np.exp(-k*(x-x0)))
sigparams={}
for a,b in DEP_L:
    s=f'_{a}_{b}'; M=models[s]; rng=np.random.default_rng(0); ii=rng.choice(len(Fg),min(5000,len(Fg)),False)
    F=Fg[ii]; base=sic_at(M,F,np.full(len(ii),float(ph0[s][ii].mean())))
    pgrid=np.linspace(4.5,9.5,21); y=np.array([float((sic_at(M,F,np.full(len(ii),pv))-base).mean()) for pv in pgrid])
    try:
        popt,_=curve_fit(sig,pgrid,y,p0=[7.9,6,3,25,-5],bounds=([5,0.1,0.1,0.1,-50],[10,20,50,200,50]),maxfev=8000)
        sigparams[s]={k:float(v) for k,v in zip(['x0','k','a','b','c'],popt)}
    except Exception as e: sigparams[s]={'error':str(e)}
json.dump(sigparams,open(f'{O}/SICpH_sigmoid_ours.json','w'),indent=1)

huang_sig={'_0_30':dict(x0=7.646,k=6.489,a=0.891,b=7.068,c=-4.967),'_30_100':dict(x0=7.928,k=6.111,a=3.792,b=33.179,c=-5.356),'_100_200':dict(x0=7.902,k=6.29,a=3.597,b=31.133,c=-5.432)}
def hdelta(s,ph,dph):
    p=huang_sig[s]; f=lambda x: p['c']+p['b']/(p['a']+np.exp(-p['k']*(x-p['x0'])))
    return f(ph+dph)-f(ph)

results={}; maps={}
for s in ('126','370','585'):
  for (y0,y1) in [(2020,2050),(2020,2100)]:
    Nin,frac,gfert,dep=cum(s,y0,y1)  # Nin Mg/ha cropland
    # deposition on cropland as Mg/ha (grid dep is already kg/ha; per cropland ≈ dep when frac high; add grid dep/1000 as Nin_dep for fert+dep)
    Nin_dep=dep/1000.0
    variants={}
    for lab,Nuse in [('fert_only',Nin),('fert_plus_dep',Nin+Nin_dep)]:
      dph_crop=np.where(frac>0.01,-0.06*Nuse+0.11,0.0)
      # finite difference on full cell, then scale by cropland fraction (acidification acts on cropland soils)
      dS={}; dS_hs={}; dS_neg={}
      for a,b in DEP_L:
        ss=f'_{a}_{b}'; t=b-a; M=models[ss]
        sicn=sic_at(M,Fg,ph0[ss]+dph_crop)
        d_full=stock(ss,sicn,t)-stock(ss,sic0[ss],t)
        dS[ss]=d_full*np.clip(frac,0,1)  # only cropland area experiences ΔpH
        dsc=hdelta(ss,ph0[ss],dph_crop); dsc=np.where(sic0[ss]>0.1,dsc,0)
        dS_hs[ss]=(stock(ss,sic0[ss]+dsc,t)-stock(ss,sic0[ss],t))*np.clip(frac,0,1)
        # losses only (clip gains from +0.11 intercept at low Nin)
        dS_neg[ss]=np.minimum(dS[ss],0)
      Pg=lambda v: float((v*area).sum()*1e-9)
      variants[lab]=dict(
        Nin_cropland_mean_Mgha=float(Nuse[frac>0.01].mean()),
        Nin_p90=float(np.percentile(Nuse[frac>0.01],90)),
        dph_cropland_mean=float(dph_crop[frac>0.01].mean()),
        dph_frac_negative=float((dph_crop[frac>0.01]<0).mean()),
        cropland_Mkm2=float((np.clip(frac,0,1)*area).sum()*1e-8),
        delta_our_FD={ss:Pg(dS[ss]) for ss in dS},
        delta_our_FD_0_30=Pg(dS['_0_30']), delta_our_FD_0_100=Pg(dS['_0_30']+dS['_30_100']),
        delta_our_FD_0_200=Pg(sum(dS[ss] for ss in dS)),
        loss_only_FD_0_30=Pg(dS_neg['_0_30']), loss_only_FD_0_100=Pg(dS_neg['_0_30']+dS_neg['_30_100']),
        loss_only_FD_0_200=Pg(sum(dS_neg[ss] for ss in dS_neg)),
        delta_HuangSig_0_30=Pg(dS_hs['_0_30']), delta_HuangSig_0_200=Pg(sum(dS_hs[ss] for ss in dS_hs)),
        loss_only_HuangSig_0_30=Pg(np.minimum(dS_hs['_0_30'],0)),
      )
      if lab=='fert_only' and y1==2050:
        maps[f'dSIC_{s}']=(sum(dS[ss] for ss in dS)).astype('float32')
        maps[f'dSIC_loss_{s}']=(sum(dS_neg[ss] for ss in dS_neg)).astype('float32')
        maps[f'dph_{s}']=dph_crop.astype('float32'); maps[f'frac_{s}']=frac.astype('float32')
    # Zamanian on grid fert+0.5 dep
    sto={}
    for name,coef in [('low',0.055),('central',0.21),('high',0.32)]:
      Cpot=(gfert+0.5*dep)*coef/1000.0; S1,S2=z5['sic_0_30'],z5['sic_30_100']
      l1=np.minimum(Cpot,S1); l2=np.minimum(np.maximum(Cpot-l1,0),S2)
      sto[name]=dict(coef=coef,loss_0_30=float((l1*area).sum()*1e-9),loss_0_100=float(((l1+l2)*area).sum()*1e-9))
    variants['zamanian_stoichiometry']=sto
    variants['N_input_Tg_yr']=dict(fertilizer=float((gfert*area).sum()/1e9/(y1-y0+1)),deposition=float((dep*area).sum()/1e9/(y1-y0+1)))
    results[f'ssp{s}_{y0}_{y1}']=variants
    fo=variants['fert_only']
    print(s,y0,y1,'Nin',round(fo['Nin_cropland_mean_Mgha'],2),'dph',round(fo['dph_cropland_mean'],3),
          'FD030',round(fo['delta_our_FD_0_30'],2),'loss030',round(fo['loss_only_FD_0_30'],2),
          'FD0200',round(fo['delta_our_FD_0_200'],2),'loss0200',round(fo['loss_only_FD_0_200'],2),flush=True)

json.dump(results,open(f'{O}/N_huang_formula.json','w'),indent=1)
np.savez_compressed(f'{O}/N_huang_maps.npz',**maps)
json.dump(dict(
  formula='ΔpH=-0.06×Nin+0.11 (Huang SM; China resurveys)',
  Nin='cumulative chemical N fertilizer per cropland hectare (ISIMIP IMAGE rate, not grid-mean)',
  SIC_response='finite difference of our XGB SIC hurdle w.r.t. pH covariate; change scaled by cropland fraction',
  huang_published_topsoil_2020_2050_Pg={'SSP1-2.6-High-Ambition-N':10,'SSP2-4.5-Medium-Ambition-N':14,'SSP5-8.5-Low-Ambition-N':23},
  note='ISIMIP IMAGE N trajectories ≠ GLOBIOM INMS ambition scenarios; no ssp245 N files; deposition from ISIMIP not CCMI',
  intercept_note='+0.11 intercept implies alkalinization at Nin<1.83 Mg/ha; report both net Δ and loss-only (gains clipped)',
),open(f'{O}/N_method.json','w'),indent=1)
print('DONE')
