# v14: definitive direction-of-change table, derived only from existing outputs (out/v10, out/v13). No refitting.
import json, numpy as np
R='/workspace/soil_global'
P=json.load(open(R+'/out/v10/paper_numbers_v10.json')); S13=json.load(open(R+'/out/v13/summaries_v13.json'))
mask=np.load(R+'/out/v4/mask.npy'); H,W=mask.shape
lat=90-(np.arange(H)+.5)/6; area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]; km=area/100/1e6
EM=np.load(R+'/out/v10/ens_maps.npz'); LAND=float(km.sum())
def st(d): return dict(mean=d['mean'],p05=d['p05'],p95=d['p95'])
out=dict(note='Signed changes in Pg C (negative = decrease of the soil stock). Climate: 2081-2100 vs WorldClim 1970-2000 baseline, 0-200 cm (MAOC/POC 0-30 cm mineral soils); ensemble 10 fold-models x 6 GCMs (TL adds tau sampling). N: 2020-2050, IMAGE fertilizer, fold-model ensemble (n=10). Areas: share of mapped land.',land_Mkm2=LAND,ssp={})
for s in ['126','245','370','585']:
  f=P['future'][s]; e=f['eq']; t=f['time_limited']; n=P['N']['scenarios'][s]; z=f['zone']
  a=EM[f'dsoc_0_200_{s}'].astype(float); b=EM[f'dsic_0_200_{s}'].astype(float)
  q=dict(tradeoff=(a<0)&(b>0),coloss=(a<0)&(b<0),bothgain=(a>0)&(b>0),socgain_sicloss=(a>0)&(b<0))
  zero=float(km[(a==0)|(b==0)].sum())
  d=dict(
    eq=dict(SOC=st(e['dSOC_0_200']),SIC=st(e['dSIC_0_200']),TC=st(e['dTC_0_200']),MAOC=st(e['dMAOC']),POC=st(e['dPOC']),SOC_0_30=st(e['dSOC_0_30']),SIC_0_30=st(e['dSIC_0_30']),dpH=st(e['dph'])),
    tl=dict(SOC=st(t['dSOC_0_200']),SIC=st(t['dSIC_0_200']),TC=st(t['dTC_0_200']),MAOC=st(t['dMAOC']),POC=st(t['dPOC']),SOC_0_30=st(t['dSOC_0_30'])),
    committed_after_2100={k:e[kk]['mean']-t[kk]['mean'] for k,kk in [('SOC','dSOC_0_200'),('SIC','dSIC_0_200'),('TC','dTC_0_200'),('MAOC','dMAOC'),('POC','dPOC')]},
    N=dict(loss_0_30=st(n['loss_0_30']),net_0_30=st(n['net_0_30']),loss_0_200=st(n['loss_0_200']),net_0_200=st(n['net_0_200'])),
    shift=dict(area_Mkm2=z['land_shift_Mkm2'],area_pct=100*z['land_shift_Mkm2']/LAND,SOC=z['dSOC_on_shift_Pg'],SIC=z['dSIC_on_shift_Pg'],TC=z['dSOC_on_shift_Pg']+z['dSIC_on_shift_Pg'],
               share_of_global_dSOC=z['dSOC_on_shift_Pg']/f['map_sums_equal_mean']['dSOC_0_200'],share_of_global_dSIC=z['dSIC_on_shift_Pg']/f['map_sums_equal_mean']['dSIC_0_200']),
    quadrant_Mkm2={k:float(km[v].sum()) for k,v in q.items()}, quadrant_pct={k:float(100*km[v].sum()/LAND) for k,v in q.items()}, zero_change_Mkm2=zero,
    land_pct=dict(SOC_decrease=float(100*km[a<0].sum()/LAND),SIC_increase=float(100*km[b>0].sum()/LAND),TC_decrease=float(100*km[(a+b)<0].sum()/LAND),SOC030_decrease=float(100*km[EM[f'dsoc_0_30_{s}']<0].sum()/LAND)),
  )
  tl=t['dSIC_0_200']
  d['SIC_by2100_both_drivers']=dict(TL_gain=st(tl),N_net=n['net_0_200']['mean'],N_loss=n['loss_0_200']['mean'],
     central_sum_net=tl['mean']+n['net_0_200']['mean'],central_sum_loss=tl['mean']+n['loss_0_200']['mean'],
     decrease_robust_net=bool(tl['p95']+n['net_0_200']['mean']<0),decrease_robust_loss=bool(tl['p95']+n['loss_0_200']['mean']<0),
     eq_sum_net=e['dSIC_0_200']['mean']+n['net_0_200']['mean'],eq_sum_loss=e['dSIC_0_200']['mean']+n['loss_0_200']['mean'],eq_increase_robust=bool(e['dSIC_0_200']['p05']+n['loss_0_200']['mean']>0))
  T=S13['transitions_main'][s]; d['transitions']={k:dict(area=v['area_Mkm2'],SOC=st(v['dSOC']),SIC=st(v['dSIC'])) for k,v in T.items() if not k.startswith('_') and v['area_Mkm2']>=0.3}
  d['per_gcm_all_SOCdec_SICinc_TCdec']=all(S13['per_gcm'][f'{s}_{g}']['dSOC_0_200']['mean']<0 and S13['per_gcm'][f'{s}_{g}']['dSIC_0_200']['mean']>0 and S13['per_gcm'][f'{s}_{g}']['dTC_0_200']['mean']<0 for g in ['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'])
  out['ssp'][s]=d
json.dump(out,open(R+'/out/v14/direction_v14.json','w'),indent=1)
for s,d in out['ssp'].items(): print(s,{k:round(v,1) for k,v in d['quadrant_pct'].items()},d['land_pct'],d['SIC_by2100_both_drivers'],d['per_gcm_all_SOCdec_SICinc_TCdec'],{k:round(v,1) for k,v in d['committed_after_2100'].items()})
