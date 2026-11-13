import numpy as np, json, glob, os
O10='/workspace/soil_global/out/v10'; mask=np.load('/workspace/soil_global/out/v4/mask.npy'); H,W=mask.shape
lat=90-(np.arange(H)+.5)/6; area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
T=lambda v: float((np.asarray(v,'float64')*area).sum()*1e-9)
M=sorted(glob.glob(O10+'/members/m*.json')); J=[json.load(open(f)) for f in M]; Z=[np.load(f.replace('.json','.npz')) for f in M]; nM=len(J)
GCMS=['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']; SSP=['126','245','370','585']; LAY=['_0_30','_30_100','_100_200']
def st(a): a=np.asarray(a,float); return dict(mean=float(a.mean()),median=float(np.median(a)),p05=float(np.percentile(a,5)),p95=float(np.percentile(a,95)),sd=float(a.std(ddof=1)) if len(a)>1 else 0.0,n=int(len(a)))
rng=np.random.default_rng(10); out=dict(n_members=nM,design='10 random-10-fold fold models (each trained on 90% of profiles) x 6 GCMs; maps = ensemble MEAN so that map sums equal headline central values; median and 5-95% also reported')
# ---------- present with BD / CF / thickness / organic C-density perturbation (assumptions, labelled)
ND=300; pres={}
for s in LAY:
  for v in ['SOC','SOC_min','SOC_org','SIC']+(['MAOC','POC'] if s in('_0_30','_30_100') else []):
    pres.setdefault(s,{})[v+'_model_only']=st([j['present'][s][v] for j in J])
draws={k:[] for k in ['SOC','SIC','TC','MAOC','POC']}; lay_d={s:{'SOC':[],'SIC':[],'MAOC':[],'POC':[]} for s in LAY}
for j in J:
  for _ in range(ND):
    bd=rng.normal(1,0.05)  # systematic BD error (relative)
    tot={'SOC':0,'SIC':0,'MAOC':0,'POC':0}
    for s in LAY:
      cf=j['CF'][s]; cfn=np.clip(cf*np.exp(rng.uniform(np.log(0.5),np.log(2.0))),0,60); fcf=(1-cfn/100)/(1-cf/100)   # CF scalar vs SoilGrids-like spread
      th={'_0_30':1.0,'_30_100':rng.normal(1,0.05),'_100_200':rng.normal(1,0.10)}[s]   # effective-thickness (bedrock/shallow soil) uncertainty, symmetric (assumption)
      od=rng.normal(1,0.2)
      P=j['present'][s]; f=bd*fcf*th
      soc=P['SOC_min']*f+P['SOC_org']*od*th; sic=P['SIC']*f
      lay_d[s]['SOC'].append(soc); lay_d[s]['SIC'].append(sic); tot['SOC']+=soc; tot['SIC']+=sic
      if 'MAOC' in P: lay_d[s]['MAOC'].append(P['MAOC']*f); lay_d[s]['POC'].append(P['POC']*f); tot['MAOC']+=P['MAOC']*f; tot['POC']+=P['POC']*f
    for k in ['SOC','SIC','MAOC','POC']: draws[k].append(tot[k])
    draws['TC'].append(tot['SOC']+tot['SIC'])
for s in LAY:
  for k,v in lay_d[s].items():
    if v: pres[s][k]=st(v)
  pres[s]['TC']=st(np.array(lay_d[s]['SOC'])+np.array(lay_d[s]['SIC']))
pres['0_200']={k:st(v) for k,v in draws.items() if k not in('MAOC','POC')}; pres['0_100']={k:st(draws[k]) for k in ('MAOC','POC')}
pres['note']='model spread (10 fold models) x Monte Carlo: BD systematic N(1,0.05); CF x log-U(0.5,2) of layer median (cap 60%); effective thickness factor 30-100 N(1,0.05), 100-200 N(1,0.10); organic C density N(1,0.2). Perturbation ranges are assumptions.'
out['present']=pres; print('present 0-200',pres['0_200'],flush=True)
# ---------- future climate (eq) and time-limited
t=85.0; out['future']={}
taus={'soc_0_30':(20,100),'soc_30_100':(100,1000),'soc_100_200':(500,3000),'sic':(1000,10000),'MA':(50,400),'PO':(5,30)}
lu=lambda lo,hi,n: np.exp(rng.uniform(np.log(lo),np.log(hi),n))
fE=lambda k,n=4000: float((1-np.exp(-t/lu(*taus[k],n))).mean())
maps={}
for s in SSP:
  E={k:[] for k in ['dSOC_0_30','dSIC_0_30','dSOC_0_200','dSIC_0_200','dTC_0_200','dMAOC','dPOC','dph']}; TL={k:[] for k in ['dSOC_0_200','dSIC_0_200','dTC_0_200','dSOC_0_30','dMAOC','dPOC']}
  for j in J:
    for g in GCMS:
      f=j['fut'][f'{s}_{g}']; dso=[f['dsoc'+l] for l in LAY]; dsi=[f['dsic'+l] for l in LAY]
      E['dSOC_0_30'].append(dso[0]); E['dSIC_0_30'].append(dsi[0]); E['dSOC_0_200'].append(sum(dso)); E['dSIC_0_200'].append(sum(dsi)); E['dTC_0_200'].append(sum(dso)+sum(dsi))
      E['dMAOC'].append(f['dMA']); E['dPOC'].append(f['dPO']); E['dph'].append(f['dph_mean'])
      for _ in range(20):
        fs=[1-np.exp(-t/lu(*taus[k],1)[0]) for k in ('soc_0_30','soc_30_100','soc_100_200')]; fi=1-np.exp(-t/lu(*taus['sic'],1)[0])
        a=sum(d*x for d,x in zip(dso,fs)); b=sum(dsi)*fi
        TL['dSOC_0_200'].append(a); TL['dSIC_0_200'].append(b); TL['dTC_0_200'].append(a+b); TL['dSOC_0_30'].append(dso[0]*fs[0])
        TL['dMAOC'].append(f['dMA']*(1-np.exp(-t/lu(*taus['MA'],1)[0]))); TL['dPOC'].append(f['dPO']*(1-np.exp(-t/lu(*taus['PO'],1)[0])))
  out['future'][s]=dict(eq={k:st(v) for k,v in E.items()},tl={k:st(v) for k,v in TL.items()})
  # mean maps (same ensemble)
  acc={}
  for z in Z:
    for g in GCMS:
      k=f'f_{s}_{g}_'
      for v in ['dsoc_0_30','dsoc_30_100','dsoc_100_200','dsic_0_30','dsic_30_100','dsic_100_200','dph_0_30','dMA','dPO']:
        acc[v]=acc.get(v,0)+z[k+v].astype('float32')
  n=len(Z)*len(GCMS); acc={k:v/n for k,v in acc.items()}
  maps[f'dsoc_0_30_{s}']=acc['dsoc_0_30']; maps[f'dsoc_0_200_{s}']=acc['dsoc_0_30']+acc['dsoc_30_100']+acc['dsoc_100_200']; maps[f'dsic_0_200_{s}']=acc['dsic_0_30']+acc['dsic_30_100']+acc['dsic_100_200']
  maps[f'dph_{s}']=acc['dph_0_30']; maps[f'dMA_{s}']=acc['dMA']; maps[f'dPO_{s}']=acc['dPO']
  maps[f'tl_dsoc_0_200_{s}']=acc['dsoc_0_30']*fE('soc_0_30')+acc['dsoc_30_100']*fE('soc_30_100')+acc['dsoc_100_200']*fE('soc_100_200')
  maps[f'tl_dtc_0_200_{s}']=maps[f'tl_dsoc_0_200_{s}']+maps[f'dsic_0_200_{s}']*fE('sic')
  out['future'][s]['map_sums']=dict(dSOC_0_30=T(maps[f'dsoc_0_30_{s}']),dSOC_0_200=T(maps[f'dsoc_0_200_{s}']),dSIC_0_200=T(maps[f'dsic_0_200_{s}']),dMAOC=T(maps[f'dMA_{s}']),dPOC=T(maps[f'dPO_{s}']),tl_dTC_0_200=T(maps[f'tl_dtc_0_200_{s}']))
  # zone shift trade-off with Beck V3 shift mask (model independent, v6)
  sh_f=f'/workspace/soil_global/out/v6/shift_{s}.npz'
  if os.path.exists(sh_f):
    sh=np.load(sh_f)['shift'].astype(bool); a_=maps[f'dsoc_0_200_{s}']; b_=maps[f'dsic_0_200_{s}']; km=area/100/1e6
    out['future'][s]['zone']=dict(land_shift_Mkm2=float(km[sh].sum()),tradeoff_SOC_loss_SIC_gain_Mkm2=float(km[(a_<0)&(b_>0)].sum()),both_loss_Mkm2=float(km[(a_<0)&(b_<0)].sum()),both_gain_Mkm2=float(km[(a_>0)&(b_>0)].sum()),
      dSOC_on_shift_Pg=T(np.where(sh,a_,0)),dSIC_on_shift_Pg=T(np.where(sh,b_,0)))
  print(s,'eq dSOC0-200',out['future'][s]['eq']['dSOC_0_200'],'map',out['future'][s]['map_sums'],flush=True)
# ---------- N
out['N']={}
for s in SSP:
  out['N'][s]={k:st([j['N'][s][k] for j in J]) for k in J[0]['N'][s]}
  for k in ('loss_0_30','loss_0_200','net_0_30'):
    maps[f'N_{k}_{s}']=np.mean([z[f'N_{s}_{k}'].astype('float32') for z in Z],0)
  out['N'][s]['loss_0_200']=st([sum(j['N'][s]['loss'+l] for l in LAY) for j in J]); out['N'][s]['net_0_200']=st([sum(j['N'][s]['net'+l] for l in LAY) for j in J])
  out['N'][s]['map_sum_loss_0_30']=T(maps[f'N_loss_0_30_{s}'])
out['N']['note']='Huang dpH=-0.06*Nin+0.11 on cropland; Nin = cumulative 2020-2050 IMAGE (ISIMIP3b) fertilizer per cropland ha; SSP2-4.5 = mean of SSP1-2.6 and SSP3-7.0 IMAGE inputs (interpolation; GLOBIOM/INMS data require registered INMS access and were not obtained).'
# present mean maps
for v in ['p_soc_0_30','p_soc_30_100','p_soc_100_200','p_sic_0_30','p_sic_30_100','p_sic_100_200','p_MA','p_PO','p_ph_0_30']:
  a=np.array([z[v].astype('float32') for z in Z]); maps[v]=a.mean(0); maps[v+'_sd']=a.std(0)
np.savez_compressed(O10+'/ens_maps.npz',**{k:np.asarray(v,'float32') for k,v in maps.items()})
json.dump(out,open(O10+'/ensemble_v10.json','w'),indent=1); print('DONE AGG')
