import sys,json,glob,os,numpy as np
R='/workspace/soil_global'; O10=R+'/out/v10'
EM=np.load(O10+'/ens_maps.npz'); EJ=json.load(open(O10+'/ensemble_v10.json'))
class Dct(dict): pass
def build_env(src):
  src=src.replace("FM=R+'/figs/v8_main/'","FM=R+'/figs/v10_main/'").replace("FS=R+'/figs/v8_SI/'","FS=R+'/figs/v10_SI/'")
  src=src.replace("z0,z1,z2=L('0_30'),L('30_100'),L('100_200')","z0,z1,z2=[dict(soc=EM['p_soc'+l],sic=EM['p_sic'+l]) for l in ('_0_30','_30_100','_100_200')]")
  src=src.replace("z1,z2=L('30_100'),L('100_200')","z1,z2=[dict(soc=EM['p_soc'+l],sic=EM['p_sic'+l]) for l in ('_30_100','_100_200')]")
  src=src.replace("b5=np.load(R+'/out/v5/maps_b0.npz')","b5={f'dsoc_0_30_{s}':EM[f'dsoc_0_30_{s}'] for s in ['126','245','370','585']}")
  src=src.replace("N=np.load(R+'/out/v6/N_huang_maps.npz')","N=NMAP")
  src=src.replace("sh=np.load(R+'/out/v6/shift_585.npz')","sh=dict(dsoc=EM['dsoc_0_200_585'],dsic=EM['dsic_0_200_585'])")
  src=src.replace("fr=np.load(O8+'/frac_maps10.npz')","fr=FRM")
  src=src.replace("FJ=json.load(open(O8+'/fractions_v8.json'))","FJ=FJ10")
  src=src.replace("json.dump(log,open(O8+'/fig_numbers.json','w'),indent=1)","json.dump(log,open(O10+'/fig_numbers_v10.json','w'),indent=1)")
  return src
# N maps in v8 key convention + dpH from Nin
NMAP={}
for s in ['126','245','370','585']:
  NMAP[f'dSIC_loss_{s}']=EM[f'N_loss_0_30_{s}']; NMAP[f'dSIC_loss0200_{s}']=EM[f'N_loss_0_200_{s}']
  z=np.load(f'{O10}/Nin_{s}_2020_2050.npz'); NMAP[f'dph_{s}']=np.where(z['fr']>0.01,-0.06*z['Nin']+0.11,0)
fr8=np.load(R+'/out/v8/frac_maps10.npz')
f0=np.where(EM['p_MA']+EM['p_PO']>0,EM['p_MA']/np.maximum(EM['p_MA']+EM['p_PO'],1e-6),np.nan)
FRM=dict(MA_0_30=EM['p_MA'],PO_0_30=EM['p_PO'],f_0_30=f0,MA_30_100=fr8['MA_30_100'],PO_30_100=fr8['PO_30_100'],fsd_0_30=fr8['fsd_0_30'])
FJ8=json.load(open(R+'/out/v8/fractions_v8.json')); FJ10=json.loads(json.dumps(FJ8)); P=EJ['present']
FJ10['_0_30'].update(MAOC=P['_0_30']['MAOC']['mean'],MAOC_CI90=[P['_0_30']['MAOC']['p05'],P['_0_30']['MAOC']['p95']])
FJ10['_30_100'].update(MAOC=P['_30_100']['MAOC']['mean'])
sc={}
for s in ['126','245','370','585']:
  e=EJ['future'][s]['eq']; t=EJ['future'][s]['tl']
  sc[s]=dict(dMAOC_eq=e['dMAOC']['mean'],dPOC_eq=e['dPOC']['mean'],dMAOC_eq_range=[e['dMAOC']['p05'],e['dMAOC']['p95']],dPOC_eq_range=[e['dPOC']['p05'],e['dPOC']['p95']],
     tl_central=dict(dMAOC=t['dMAOC']['mean'],dPOC=t['dPOC']['mean'],tau_POC='5–30',tau_MAOC='50–400'))
FJ10['future_0_30']['scen']=sc
which=sys.argv[1]
src=build_env(open(R+f'/scripts/{which}').read())
# v10 overrides for N figure and SI S7/S13 (ensemble based)
src=src.replace("for f in [globals()[n]","exec(open(R+'/scripts/53b_v10_overrides.py').read())\nfor f in [globals()[n]",1)
sys.argv=[which]+sys.argv[2:]
exec(src)
