# v6: Huang-formula N→ΔpH→ΔSIC using our SIC model's local pH response (finite difference)
# ΔpH = -0.06*Nin + 0.11, Nin = cumulative chemical N fertilizer 2020–2050 in MgN ha-1
# (Huang et al. 2024 Science SM; derived from China resurveys, ref 63 Fig.7)
# Deposition (ISIMIP NHx+NOy) added as Nin_dep for a fert+dep variant.
# Stock conversion uses v5 maps (BD, CF via stocks already in maps_b0 as Mg/ha).
# Sensitivity: Zamanian stoichiometry 0.21 (0.055–0.32) kg C/kg N.
import numpy as np, pandas as pd, json, os, xgboost as xgb
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
O='/workspace/soil_global/out/v6'; os.makedirs(O,exist_ok=True)
I='/workspace/soil_global/data/isimip'
area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
import netCDF4 as nc
def up(a): return np.repeat(np.repeat(a,3,0),3,1)
def flip(d,a): return a if d.variables['lat'][0]>d.variables['lat'][-1] else a[::-1]
CROPS={'c3ann':['c3ann_irrigated','c3ann_rainfed'],'c3per':['c3per_irrigated_food','c3per_irrigated_bf','c3per_rainfed_food','c3per_rainfed_bf'],
       'c4ann':['c4ann_irrigated','c4ann_rainfed'],'c4per':['c4per_irrigated_food','c4per_irrigated_bf','c4per_rainfed_food','c4per_rainfed_bf'],'c3nfx':['c3nfx_irrigated','c3nfx_rainfed']}
def cum_fert_dep(s,y0,y1):
    t0,t1=(y0-2015),(y1-2015)
    nh=nc.Dataset(f'{I}/ndep-nhx_ssp{s}_monthly_2015_2100.nc'); no=nc.Dataset(f'{I}/ndep-noy_ssp{s}_monthly_2015_2100.nc')
    NH=flip(nh,np.ma.filled(nh.variables['nhx'][t0*12:(t1+1)*12].sum(0),0))*10  # kg N/ha
    NO=flip(no,np.ma.filled(no.variables['noy'][t0*12:(t1+1)*12].sum(0),0))*10
    fe=nc.Dataset(f'{I}/n-fertilizer-5crops_image_2015soc_ssp{s}_annual_2015_2100.nc')
    lu=nc.Dataset(f'{I}/landuse-5crops_image_ssp{s}_annual_2015_2100.nc')
    FT=np.zeros((360,720)); crop=np.zeros((360,720))
    for c,vs in CROPS.items():
        rate=np.ma.filled(fe.variables[f'{c}_fertl'][t0:t1+1],0); fr=sum(np.ma.filled(lu.variables[v][t0:t1+1],0) for v in vs)
        FT+=np.nan_to_num((rate*fr).sum(0)); crop+=np.nan_to_num(fr.mean(0))
    FT=flip(fe,FT); crop=flip(fe,crop)
    return up(FT)[mask], up(NH+NO)[mask], up(crop)[mask]  # kg/ha, kg/ha, fraction
# ---- train SIC models per depth on v5 spline points (full sample = paper central)
p=pd.read_csv(f'{D}/points_v5_spline.csv')
r_=((90-p.Y)*6).astype(int).clip(0,H-1).values; c_=((p.X+180)*6).astype(int).clip(0,W-1).values
X=S0x[:,r_,c_].T; ok=np.all(np.isfinite(X),1)
par=dict(n_estimators=250,max_depth=7,learning_rate=0.07,subsample=0.8,colsample_bytree=0.8,n_jobs=4,tree_method='hist',min_child_weight=5)
ORG=120.0; DEP=[(0,30),(30,100),(100,200)]
z5=np.load('/workspace/soil_global/out/v5/maps_b0.npz')
models={}
for a,b in DEP:
    s=f'_{a}_{b}'; ph=p['phaq'+s].values.copy(); tq=p['tceq'+s].values; sic=p['sic'+s].values.copy()
    ph[(ph<3)|(ph>11)]=np.nan; sic[(tq<0)|(tq>1000)]=np.nan; sic[(tq>10)&(ph<5.5)]=np.nan
    mP=ok&np.isfinite(ph); mS=ok&np.isfinite(sic)
    MpH=xgb.XGBRegressor(**par).fit(X[mP],ph[mP])
    phoof=MpH.predict(X); XS=np.column_stack([X,phoof])
    C=xgb.XGBClassifier(**par,eval_metric='logloss').fit(XS[mS],(sic[mS]>0.1).astype(int))
    j=np.where(mS&(sic>0.1))[0]; R=xgb.XGBRegressor(**par).fit(XS[j],np.log(sic[j]))
    sm=float(np.mean(np.exp(np.log(sic[j])-R.predict(XS[j]))))
    # BD mineral for stock (reuse map-implied: stock/(conc*(1-CF)*t*0.1) ≈ bdm for mineral)
    models[s]=dict(MpH=MpH,C=C,R=R,sm=sm)
    print('trained',s,flush=True)
# present grid predictions at baseline pH and for pH shifts
ph0={}; sic0={}; bdm={}; Porg={}; CF={}
for a,b in DEP:
    s=f'_{a}_{b}'; M=models[s]
    ph=M['MpH'].predict(Fg); FS=np.column_stack([Fg,ph])
    sic=M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']
    ph0[s]=ph; sic0[s]=sic
    # recover BD and CF from v5 stock maps: stock = sic_conc * bd * (1-CF/100) * t * 0.1
    # for mineral-dominated cells use maps; organic fraction from v5
    Porg[s]=z5['P'+s]; bdm[s]=z5['bdm'+s]
    # CF from v5: sic stock mineral = (1-P)*sic*bdm*(1-CF/100)*t*0.1
    t=b-a; smap=z5['sic'+s]
    with np.errstate(divide='ignore',invalid='ignore'):
        # implied (1-CF/100) from mineral part; clamp
        den=(1-Porg[s])*sic*bdm[s]*t*0.1; cf_factor=np.where(den>1e-6,smap/den,1.0)
        cf_factor=np.clip(cf_factor,0.5,1.0)
    CF[s]=cf_factor
    print(s,'mean sic',float(sic.mean()),'stock Pg',float((smap*area).sum()*1e-9),flush=True)

def sic_at_ph(M,F,ph):
    FS=np.column_stack([F,ph])
    return M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']

def stock_from_conc(s,sic,t):
    return (1-Porg[s])*sic*bdm[s]*CF[s]*t*0.1

# Finite-difference SICpH response: build local dSIC/dpH by ±0.1 pH and also fit depth-wise sigmoid on SHAP-style marginal
# For Huang pathway we apply actual ΔpH per cell
def apply_dph(dph):
    out={}
    for a,b in DEP:
        s=f'_{a}_{b}'; t=b-a; M=models[s]
        phn=ph0[s]+dph
        sicn=sic_at_ph(M,Fg,phn)
        dS=stock_from_conc(s,sicn,t)-stock_from_conc(s,sic0[s],t)
        # only allow losses from acidification (ΔpH<0) to reduce SIC; gains from +intercept clipped separately
        out[s]=dS
    return out

# Also fit a simple 5-param-style sigmoid on finite-diff SICpH for documentation
def fit_local_sigmoid():
    from scipy.optimize import curve_fit
    def sig(x,x0,k,a,b,c): return c+b/(a+np.exp(-k*(x-x0)))
    res={}
    for a,b in DEP:
        s=f'_{a}_{b}'; M=models[s]
        # sample land cells
        rng=np.random.default_rng(0); ii=rng.choice(len(Fg),min(8000,len(Fg)),replace=False)
        F=Fg[ii]; phb=ph0[s][ii]
        # SICpH ≈ SIC(ph) - SIC(ph_mean) holding other fixed — approximate with predictions at ph grid
        pgrid=np.linspace(4.5,9.5,21); curves=[]
        base=sic_at_ph(M,F,np.full(len(F),phb.mean()))
        for pv in pgrid:
            curves.append(sic_at_ph(M,F,np.full(len(F),pv))-base)
        y=np.mean(curves,0)
        try:
            popt,_=curve_fit(sig,pgrid,y,p0=[7.9,6,3,25,-5],bounds=([5,0.1,0.1,0.1,-50],[10,20,50,200,50]),maxfev=5000)
            res[s]=dict(x0=float(popt[0]),k=float(popt[1]),a=float(popt[2]),b=float(popt[3]),c=float(popt[4]),
                        form='c+b/(a+exp(-k*(pH-x0)))',note='fit to our model finite-diff SICpH, not Huang SHAP')
        except Exception as e:
            res[s]=dict(error=str(e))
    return res

sigparams=fit_local_sigmoid(); json.dump(sigparams,open(f'{O}/SICpH_sigmoid_ours.json','w'),indent=1); print('sigmoid',sigparams,flush=True)

# Huang Table S9 overall params for comparison (SICpH = c + b/(a+exp(...)) assumed same form)
huang_sig={'overall':dict(x0=7.893,k=6.086,a=3.373,b=28.694,c=-5.156),
           '_0_30':dict(x0=7.646,k=6.489,a=0.891,b=7.068,c=-4.967),
           '_30_100':dict(x0=7.928,k=6.111,a=3.792,b=33.179,c=-5.356),
           '_100_200':dict(x0=7.902,k=6.29,a=3.597,b=31.133,c=-5.432)}

def huang_sig_delta(s,ph,dph):
    p=huang_sig.get(s,huang_sig['overall'])
    f=lambda x: p['c']+p['b']/(p['a']+np.exp(-p['k']*(x-p['x0'])))
    return f(ph+dph)-f(ph)  # g/kg SICpH change

results={}; maps={}
for s in ('126','370','585'):
    for (y0,y1) in [(2020,2050),(2020,2100)]:
        fert,dep,crop=cum_fert_dep(s,y0,y1)
        Nin_f=fert/1000.0; Nin_d=dep/1000.0  # Mg N/ha
        # Huang formula on fertilizer; fert+dep variant
        variants={}
        for lab,Nin in [('fert_only',Nin_f),('fert_plus_dep',Nin_f+Nin_d)]:
            dph=-0.06*Nin+0.11
            # apply only where Nin>0 (cropland / deposition); elsewhere 0
            dph=np.where(Nin>0,dph,0.0)
            dS=apply_dph(dph)
            # Huang sigmoid applied to concentration then stock (sensitivity)
            dS_hs={}
            for a,b in DEP:
                ss=f'_{a}_{b}'; t=b-a
                dsc=huang_sig_delta(ss,ph0[ss],dph)
                # only where present SIC>0.1
                dsc=np.where(sic0[ss]>0.1,dsc,0.0)
                dS_hs[ss]=stock_from_conc(ss,sic0[ss]+dsc,t)-stock_from_conc(ss,sic0[ss],t)
            def Pg(v): return float((v*area).sum()*1e-9)
            variants[lab]=dict(
                Nin_mean_Mgha=float(Nin[Nin>0].mean()) if (Nin>0).any() else 0,
                Nin_on_crop_mean=float(Nin[crop>0.01].mean()) if (crop>0.01).any() else 0,
                dph_mean_on_N=float(dph[Nin>0].mean()) if (Nin>0).any() else 0,
                dph_mean_on_crop=float(dph[crop>0.01].mean()) if (crop>0.01).any() else 0,
                loss_our_FD={ss:Pg(dS[ss]) for ss in dS},
                loss_our_FD_0_30=Pg(dS['_0_30']),
                loss_our_FD_0_100=Pg(dS['_0_30']+dS['_30_100']),
                loss_our_FD_0_200=Pg(dS['_0_30']+dS['_30_100']+dS['_100_200']),
                loss_HuangSig={ss:Pg(dS_hs[ss]) for ss in dS_hs},
                loss_HuangSig_0_30=Pg(dS_hs['_0_30']),
                loss_HuangSig_0_200=Pg(dS_hs['_0_30']+dS_hs['_30_100']+dS_hs['_100_200']),
            )
            if lab=='fert_only' and y0==2020 and y1==2050:
                maps[f'dSIC_FD_{s}']=(dS['_0_30']+dS['_30_100']+dS['_100_200']).astype('float32')
                maps[f'dph_{s}']=dph.astype('float32')
        # Zamanian stoichiometry sensitivity (kg C / kg N on fert+0.5*dep)
        Nkg=fert+0.5*dep
        sto={}
        for name,coef in [('low',0.055),('central',0.21),('high',0.32)]:
            Cpot=Nkg*coef/1000.0  # Mg C/ha
            S1=z5['sic_0_30']; S2=z5['sic_30_100']
            l1=np.minimum(Cpot,S1); l2=np.minimum(np.maximum(Cpot-l1,0),S2)
            sto[name]=dict(coef=coef,loss_0_30=float((l1*area).sum()*1e-9),loss_0_100=float(((l1+l2)*area).sum()*1e-9))
        variants['zamanian_stoichiometry']=sto
        variants['N_input_Tg_yr']=dict(fertilizer=float((fert*area).sum()/1e9/(y1-y0+1)),
                                       deposition=float((dep*area).sum()/1e9/(y1-y0+1)))
        results[f'ssp{s}_{y0}_{y1}']=variants
        print(s,y0,y1,'FD0-30',variants['fert_only']['loss_our_FD_0_30'],
              'FD0-200',variants['fert_only']['loss_our_FD_0_200'],
              'Hsig0-30',variants['fert_only']['loss_HuangSig_0_30'],flush=True)

json.dump(results,open(f'{O}/N_huang_formula.json','w'),indent=1)
np.savez_compressed(f'{O}/N_huang_maps.npz',**maps)
json.dump(dict(method='finite_difference on XGB SIC hurdle with pH covariate; Huang ΔpH=-0.06*Nin+0.11; Nin from ISIMIP IMAGE fertilizer (not GLOBIOM); deposition ISIMIP not CCMI',
               huang_published_0_30_Pg={'SSP1-2.6':10,'SSP2-4.5':14,'SSP5-8.5':23},
               note_scenarios='ISIMIP has ssp126/370/585; no ssp245 N files. Map 370≈medium as sensitivity.'),open(f'{O}/N_method.json','w'),indent=1)
print('DONE N')
