# v5: spline-harmonised points; organic(peat)-horizon hurdle for SOC; separate mineral/organic BD; CF QC; spatial-block bootstrap
import numpy as np, pandas as pd, json, os, sys
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)   # covariates, mask, KG, futF (reads cached v4 futstack), Fg, par, GCMS
O5='/workspace/soil_global/out/v5'; os.makedirs(O5,exist_ok=True)
NB=int(os.environ.get('NB','10'))
par=dict(n_estimators=250,max_depth=7,learning_rate=0.07,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
SCN=[(s,'2081-2100') for s in ('126','245','370','585')]
PEAT_KM2=float(os.environ.get('PEAT_KM2','4.23e6'))
DEP=[(0,30),(30,100),(100,200)]; ORG=120.0
area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]  # ha
zone=np.array(['','A','A','A','B','B','B','B','C','C','C','C','C','C','C','C','C','D','D','D','D','D','D','D','D','D','D','D','D','E','E'])[kg0[mask]]
p=pd.read_csv(f'{D}/points_v5_spline.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1); blk=(np.floor(p.X.values/5)*100+np.floor(p.Y.values/5)).astype(int)
pk=kg0[r_,c_]
qc={}
Y={}
top=p['soc_0_30'].values
for a,b in DEP:
    s=f'_{a}_{b}'
    ph=p['phaq'+s].values.copy(); tq=p['tceq'+s].values; sic=p['sic'+s].values.copy(); soc=p['soc'+s].values.copy(); bd=p['bdfiod'+s].values.copy(); cf=p['cfvo'+s].values.copy()
    ph[(ph<3)|(ph>11)]=np.nan; sic[(tq<0)|(tq>1000)]=np.nan; sic[(tq>10)&(ph<5.5)]=np.nan
    soc[(soc<0)|(soc>580)]=np.nan; bd[(bd<0.1)|(bd>2.2)]=np.nan; cf[(cf<0)|(cf>90)]=np.nan
    org=soc>ORG
    # subsoil outliers: mineral subsoil SOC > 3x topsoil and >20 g/kg (buried/inverted or unit errors) -> excluded from mineral model
    inv=(a>0)&np.isfinite(top)&(soc>3*np.maximum(top,1))&(soc>20)&~org
    qc[s]=dict(n_soc=int(np.isfinite(soc).sum()),n_org=int(org.sum()),org_frac=float(org[np.isfinite(soc)].mean()),
               org_share_of_point_SOC=float(np.nansum(soc[org])/np.nansum(soc)),n_inversion_excluded=int(inv.sum()),
               BD_org_med=float(np.nanmedian(bd[org])) if np.isfinite(bd[org]).any() else None,BD_min_med=float(np.nanmedian(bd[~org&np.isfinite(soc)])),
               CF_med=float(np.nanmedian(cf)),n_CF=int(np.isfinite(cf).sum()))
    Y[s]=dict(ph=ph,sic=sic,soc=soc,bd=bd,cf=cf,org=org,inv=inv)
json.dump(qc,open(f'{O5}/qc.json','w'),indent=1); print(json.dumps(qc),flush=True)
ub=np.unique(blk)
def fitdepth(s,w):
    y=Y[s]; m=lambda v: ok&np.isfinite(v)&(w>0)
    mP=m(y['ph']); MpH=xgb.XGBRegressor(**par).fit(X[mP],y['ph'][mP],sample_weight=w[mP])
    XS=np.column_stack([X,MpH.predict(X)])
    mS=m(y['sic']); C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[mS],(y['sic'][mS]>0.1).astype(int),sample_weight=w[mS])
    j=np.where(mS&(y['sic']>0.1))[0]; R=xgb.XGBRegressor(**par).fit(XS[j],np.log(y['sic'][j]),sample_weight=w[j])
    sm=float(np.average(np.exp(np.log(y['sic'][j])-R.predict(XS[j])),weights=w[j]))
    mO=m(y['soc']); P=xgb.XGBClassifier(**par,eval_metric='logloss').fit(X[mO],y['org'][mO].astype(int),sample_weight=w[mO])
    mM=mO&~y['org']&~y['inv']; MO=xgb.XGBRegressor(**par).fit(X[mM],np.log1p(y['soc'][mM]),sample_weight=w[mM])
    mB=mM&np.isfinite(y['bd']); MB=xgb.XGBRegressor(**par).fit(np.column_stack([X,np.log1p(y['soc'])])[mB],y['bd'][mB],sample_weight=w[mB])
    oo=mO&y['org']; socorg=float(np.average(y['soc'][oo],weights=w[oo]))
    ob=oo&np.isfinite(y['bd']); bdorg=float(np.average(y['bd'][ob],weights=w[ob])) if ob.sum()>20 else 0.3
    # CF: zone-median of observed (weighted by bootstrap via repeat)
    cfz=np.full(31,np.nan); mc=np.isfinite(y['cf'])&(w>0)
    for k in np.unique(pk[mc]):
        ii=mc&(pk==k); cfz[k]=np.median(np.repeat(y['cf'][ii],w[ii].astype(int)))
    CF=np.nan_to_num(cfz[kg0[mask]],nan=float(np.nanmedian(y['cf'])))
    return dict(MpH=MpH,C=C,R=R,sm=sm,P=P,MO=MO,MB=MB,socorg=socorg,bdorg=bdorg,CF=CF)
def pred(M,F,Pfix=None):
    ph=M['MpH'].predict(F); FS=np.column_stack([F,ph])
    sic=M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']
    P=M['P'].predict_proba(F)[:,1] if Pfix is None else Pfix
    socm=np.expm1(M['MO'].predict(F)).clip(0,ORG); bdm=np.clip(M['MB'].predict(np.column_stack([F,np.log1p(socm)])),0.6,2.0)
    return dict(ph=ph,sic=sic,P=P,socm=socm,bdm=bdm)
def stocks(M,q,t):
    f=(1-M['CF']/100)*t*0.1
    socS=(q['P']*M['socorg']*M['bdorg']+(1-q['P'])*q['socm']*q['bdm'])*f
    bdc=q['P']*M['bdorg']+(1-q['P'])*q['bdm']
    sicS=(1-q['P'])*q['sic']*q['bdm']*f   # no carbonate in organic horizons
    return socS,sicS,dict(org=q['P']*M['socorg']*M['bdorg']*f,min=(1-q['P'])*q['socm']*q['bdm']*f)
Pg=lambda v,sel=None: float((v*area).sum()*1e-9) if sel is None else float((v*area)[sel].sum()*1e-9)
for bi in range(NB):
    fn=f'{O5}/boot{bi:02d}.json'
    if os.path.exists(fn): print('skip',bi); continue
    rng=np.random.default_rng(100+bi)
    if bi==0: w=np.ones(len(p))
    else:
        dr=rng.choice(ub,len(ub),replace=True); cnt=pd.Series(dr).value_counts(); w=pd.Series(blk).map(cnt).fillna(0).values.astype(float)
    res=dict(present={},fut={}); Ms={}; Q0={}; P0top=None; mapsave={}
    for a,b in DEP:
        s=f'_{a}_{b}'; M=fitdepth(s,w); Ms[s]=M; q=pred(M,Fg)
        if P0top is None:
            k=PEAT_KM2*100/float((q['P']*area).sum()); res['Pscale']=k   # area (ha) anchor: PEATMAP 4.23 Mkm2 (Xu et al. 2018)
            q['P']=np.clip(q['P']*k,0,1); P0top=q['P']
        else:
            q['P']=np.minimum(np.clip(q['P']*k,0,1),P0top); P0top=q['P']   # organic subsoil only beneath organic layer above
        Q0[s]=q; so,si,parts=stocks(M,q,b-a)
        res['present'][s]=dict(SOC=Pg(so),SIC=Pg(si),SOC_org=Pg(parts['org']),SOC_min=Pg(parts['min']),socorg=M['socorg'],bdorg=M['bdorg'],
              by_zone={z:dict(SOC=Pg(so,zone==z),SIC=Pg(si,zone==z)) for z in 'ABCDE'},Porg_area_Mkm2=float((q['P']*area).sum()*1e-8))
        if bi==0: mapsave.update({f'soc{s}':so.astype('float32'),f'sic{s}':si.astype('float32'),f'P{s}':q['P'].astype('float32'),f'bdm{s}':q['bdm'].astype('float32'),f'socm{s}':q['socm'].astype('float32')})
    for sc,pr in SCN:
        acc={s:dict(dsoc=[],dsic=[],dsoc_z=[],dsic_z=[]) for s in Ms}
        accmap={s:[] for s in Ms}
        for g in GCMS:
            F=futF(g,sc,pr)
            for a,b in DEP:
                s=f'_{a}_{b}'; M=Ms[s]; q=pred(M,F,Pfix=Q0[s]['P'])   # organic fraction held at present (no peat space-for-time)
                so1,si1,_=stocks(M,q,b-a); so0,si0,_=stocks(M,Q0[s],b-a)
                acc[s]['dsoc'].append(Pg(so1-so0)); acc[s]['dsic'].append(Pg(si1-si0))
                acc[s]['dsoc_z'].append([Pg(so1-so0,zone==z) for z in 'ABCDE']); acc[s]['dsic_z'].append([Pg(si1-si0,zone==z) for z in 'ABCDE'])
                if bi==0: accmap[s].append((so1-so0).astype('float32'))
        res['fut'][f'{sc}_{pr}']=acc
        if bi==0:
            for s in Ms: mapsave[f'dsoc{s}_{sc}']=np.mean(accmap[s],0)
        print(bi,sc,{s:round(np.mean(acc[s]['dsoc']),1) for s in Ms},flush=True)
    if bi==0: np.savez_compressed(f'{O5}/maps_b0.npz',**mapsave,CF_0_30=Ms['_0_30']['CF'])
    json.dump(res,open(fn,'w')); print('boot',bi,{s:(round(v['SOC']),round(v['SIC'])) for s,v in res['present'].items()},flush=True)
print('DONE')
