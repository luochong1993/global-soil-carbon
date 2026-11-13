# Compile out/v6/paper_numbers.json for the Science paper draft
import json,numpy as np,os
O='out/v6'; R5=json.load(open('out/v5/results_v5.json')); CV=json.load(open(f'{O}/random_cv.json'))
N=json.load(open(f'{O}/N_huang_formula.json')); Z=json.load(open(f'{O}/zone_shift.json'))
Nm=json.load(open(f'{O}/N_method.json')); sig=json.load(open(f'{O}/SICpH_sigmoid_ours.json'))
r=lambda a: {'median':round(a[0],1),'p05':round(a[1],1),'p95':round(a[2],1)} if isinstance(a,list) and len(a)>=3 else a
P={'title':'Global soil organic and inorganic carbon under climate-zone shifts and nitrogen acidification',
   'version':'v6','units':'Pg C unless noted','present':{},'future_climate':{},'N_acidification':{},
   'random_CV':{},'zone_shift':{},'methods_notes':{},'huang_comparison':{}}
for s,v in R5['present'].items():
  P['present'][s]={k:r(x) for k,x in v.items() if isinstance(x,list)}
  if 'central_b0' in v: P['present'][s]['central_b0']={k:round(x,1) for k,x in v['central_b0'].items()}
P['present']['literature']=dict(Batjes1996_SOC={'0_30':'684-724','0_100':'1462-1548','0_200':'2376-2456','doi':'10.1111/j.1365-2389.1996.tb01386.x'},
  Batjes1996_SIC_0_100='695-748',Huang2024_SIC_0_200=2305,SoilGrids_SOC_0_30_same_mask=658,
  PEATMAP_area_Mkm2=4.23,PEATMAP_doi='10.1016/j.catena.2017.09.010')
for sc,v in R5['eq'].items():
  P['future_climate'][sc]=dict(equilibrium={k:r(x) for k,x in v.get('_0_200',v).items() if isinstance(x,list)},
    time_limited={k:r(x) for k,x in R5['transient'][sc].items()},
    by_depth_eq={d: {k:r(x) for k,x in v[d].items()} for d in ['_0_30','_30_100','_100_200'] if d in v})
P['future_climate']['tau_assumptions_yr']=dict(_0_30='20-100',_30_100='100-1000',_100_200='500-3000',SIC='1000-10000',
  refs=['10.1038/nature13731','10.1038/s41561-020-0596-z','10.1126/science.aad4273'],t_yr=85)
P['zone_shift']=Z
# N
for k,v in N.items():
  fo=v['fert_only']; fp=v.get('fert_plus_dep',{}); za=v['zamanian_stoichiometry']
  P['N_acidification'][k]=dict(
    Huang_formula_fert_only=dict(Nin_cropland_mean_Mgha=round(fo['Nin_cropland_mean_Mgha'],2),
      dph_cropland_mean=round(fo['dph_cropland_mean'],3),dph_frac_negative=round(fo['dph_frac_negative'],3),
      net_delta_0_30=round(fo['delta_our_FD_0_30'],2),net_delta_0_200=round(fo['delta_our_FD_0_200'],2),
      loss_only_0_30=round(fo['loss_only_FD_0_30'],2),loss_only_0_100=round(fo['loss_only_FD_0_100'],2),
      loss_only_0_200=round(fo['loss_only_FD_0_200'],2),
      HuangSig_loss_only_0_30=round(fo['loss_only_HuangSig_0_30'],2),
      HuangSig_net_0_30=round(fo['delta_HuangSig_0_30'],2)),
    Huang_formula_fert_plus_dep=dict(loss_only_0_30=round(fp.get('loss_only_FD_0_30',0),2),
      loss_only_0_200=round(fp.get('loss_only_FD_0_200',0),2),Nin_mean=round(fp.get('Nin_cropland_mean_Mgha',0),2)),
    zamanian_stoichiometry={n:{kk:round(vv,2) if isinstance(vv,float) else vv for kk,vv in d.items()} for n,d in za.items()},
    N_input_Tg_yr=v['N_input_Tg_yr'])
P['N_acidification']['method']=Nm
P['N_acidification']['Huang_published_0_30_2020_2050_Pg']=Nm['huang_published_topsoil_2020_2050_Pg']
# CV — random primary
for s,m in CV['metrics'].items():
  P['random_CV'][s]={k:({kk:round(vv,3) if isinstance(vv,float) else vv for kk,vv in v.items()} if isinstance(v,dict) else v) for k,v in m.items()}
P['random_CV']['protocol']=CV['cv']
P['random_CV']['huang_SIC_reported']=dict(AUC=0.99,R2_regression=0.79,CV='random_10fold',note='Table S3 GradientBoosting')
P['methods_notes']=dict(
  depth_harmonization='equal-area spline mpspline λ=0.1 (Bishop 1999; Malone 2009)',
  organic_hurdle='SOC>120 g/kg; P scaled to PEATMAP 4.23 Mkm2; mineral-only SOC/BD models',
  SIC_model='two-step hurdle (classifier + log regression with smearing); pH as covariate',
  stock='conc×BD×(1−CF/100)×thickness_cm×0.1',
  future_SOC='space-for-time equilibrium; time-limited with depth-specific τ (assumptions)',
  hybrid_mechanistic=dict(
    carbonate_equilibria='SM eqs S1–S2 (CaCO3–H2O–CO2); calcite equilibrium pH ≈8.19–8.23 at 350–400 ppm (Huang SM S7); used as interpretive context for SICpH sigmoid midpoint near pH 7.6–7.9',
    SICpH_sigmoid_ours=sig,
    SICpH_sigmoid_huang_tableS9={'_0_30':dict(x0=7.646,k=6.489,a=0.891,b=7.068,c=-4.967),'_30_100':dict(x0=7.928,k=6.111,a=3.792,b=33.179,c=-5.356)},
    SOC_multipool='ΔSOC_transient=(1−exp(−t/τ))×ΔSOC_eq; τ by depth as above — hybrid DSM + first-order kinetics, not a full land-surface model',
  ),
  primary_accuracy='random 5-fold CV (aligned with Huang reporting); spatial CV available in out/v4 but not emphasized',
)
P['huang_comparison']=dict(
  SIC_present_0_200_Pg=dict(ours=P['present']['_0_200']['SIC'],Huang=2305),
  N_loss_0_30_2020_2050=dict(ours_loss_only={k:P['N_acidification'][k]['Huang_formula_fert_only']['loss_only_0_30'] for k in P['N_acidification'] if k.startswith('ssp')},
    Huang_published=Nm['huang_published_topsoil_2020_2050_Pg'],
    caveat='IMAGE N ≠ GLOBIOM ambition-N; our SSP585≈SSP126 fertilizer totals'),
)
json.dump(P,open(f'{O}/paper_numbers.json','w'),indent=1)
print(json.dumps({k:P[k] if k in ('present','random_CV') else list(P[k]) if isinstance(P[k],dict) else P[k] for k in P},indent=1)[:2000])
print('saved',f'{O}/paper_numbers.json')
