# v13: new summaries from EXISTING v10 outputs only (no refitting). Output: out/v13/summaries_v13.json + out/v13/cellmaps_v13.npz
import numpy as np, json, glob, sys
sys.path.insert(0,'/workspace/soil_global/scripts')
R='/workspace/soil_global'; O10=R+'/out/v10'; O13=R+'/out/v13'
exec(open(R+'/scripts/43_v8_style.py').read())   # mask, area, countries(), CONT
ids,nm,ct=countries(); cont=ct[ids]
EM=np.load(O10+'/ens_maps.npz'); fr8=np.load(R+'/out/v8/frac_maps10.npz')
kg=np.load(R+'/out/v2/kg_beck.npz'); K0=kg['1991-2020'][mask].astype(int)
MAIN=np.array(['']+['A']*3+['B']*4+['C']*9+['D']*12+['E']*2)
KGN=['','Af','Am','Aw','BWh','BWk','BSh','BSk','Csa','Csb','Csc','Cwa','Cwb','Cwc','Cfa','Cfb','Cfc','Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','Dfa','Dfb','Dfc','Dfd','ET','EF']
km0=MAIN[np.clip(K0,0,30)]
SSP=['126','245','370','585']; GCMS=['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']
KF={s:MAIN[np.clip(kg[f'2071-2099-ssp{s}'][mask].astype(int),0,30)] for s in SSP}
Pg=lambda v,m=None: float(np.nansum((v if m is None else np.where(m,v,0))*area)*1e-9)
st=lambda a: dict(mean=float(np.mean(a)),p05=float(np.percentile(a,5)),p95=float(np.percentile(a,95)),sd=float(np.std(a,ddof=1)),n=len(a))
out={'note':'All values computed from out/v10 (ensemble maps and 10 fold-model members x 6 GCMs). Regional totals are area integrals of 10-arcmin maps (Pg C). Uncertainty for regional present stocks = spread across 10 fold-models only (no Monte Carlo BD/CF/thickness perturbation, which is only available globally).'}
# ----- groups
groups={'continent':{c:(cont==c) for c in CONT}, 'koppen_main':{c:(km0==c) for c in 'ABCDE'}, 'koppen_sub':{KGN[k]:(K0==k) for k in range(1,31) if (K0==k).sum()>0}}
groups['continent']['Unassigned']=(cont=='')
out['area_Mkm2']={g:{k:float(area[m].sum()/1e8) for k,m in G.items()} for g,G in groups.items()}; out['area_Mkm2']['total']=float(area.sum()/1e8)
# ----- present, per member
M=sorted(glob.glob(O10+'/members/m*.npz')); nM=len(M)
pres={g:{k:{} for k in G} for g,G in groups.items()}
LAY=['_0_30','_30_100','_100_200']
acc={k:np.zeros(len(area)) for k in ['soc','soc2','sic','sic2','ma','ma2']}
fut={}  # [s][gcm] list of global dicts per member
reg_fut={g:{k:{s:{'dsoc':[],'dsic':[]} for s in SSP} for k in G} for g,G in groups.items()}
agree={'dsoc_neg':np.zeros(len(area)),'dsic_pos':np.zeros(len(area)),'dsoc':np.zeros(len(area)),'dsoc2':np.zeros(len(area)),'dsic':np.zeros(len(area)),'dsic2':np.zeros(len(area))}
trans_mem={s:{} for s in SSP}
lat_full=np.repeat(lat[:,None],W,1)[mask]; band=np.floor(lat_full).astype(int)
for i,f in enumerate(M):
  z=np.load(f); print('member',i,flush=True)
  P={}
  for v in ['soc','sic']:
    for l in LAY: P[v+l]=z[f'p_{v}{l}'].astype('float32')
  P['MA']=z['p_MA'].astype('float32'); P['PO']=z['p_PO'].astype('float32')
  soc=P['soc_0_30']+P['soc_30_100']+P['soc_100_200']; sic=P['sic_0_30']+P['sic_30_100']+P['sic_100_200']
  acc['soc']+=soc; acc['soc2']+=soc**2; acc['sic']+=sic; acc['sic2']+=sic**2; acc['ma']+=P['MA']; acc['ma2']+=P['MA']**2
  for g,G in groups.items():
    for k,m in G.items():
      d=pres[g][k]
      for key,v in list(P.items())+[('soc_0_200',soc),('sic_0_200',sic)]: d.setdefault(key,[]).append(Pg(v,m))
  for s in SSP:
    for gc in GCMS:
      p=f'f_{s}_{gc}_'
      ds=sum(z[p+'dsoc'+l].astype('float32') for l in LAY); di=sum(z[p+'dsic'+l].astype('float32') for l in LAY)
      for g,G in groups.items():
        for k,m in G.items(): reg_fut[g][k][s]['dsoc'].append(Pg(ds,m)); reg_fut[g][k][s]['dsic'].append(Pg(di,m))
      # transitions (main class), per member x gcm
      tk=np.char.add(np.char.add(km0.astype('U1'),'>'),KF[s].astype('U1'))
      for t in np.unique(tk):
        if t[0]==t[-1] or '' in (t[0],): continue
        m=tk==t; d=trans_mem[s].setdefault(t,{'dsoc':[],'dsic':[]}); d['dsoc'].append(Pg(ds,m)); d['dsic'].append(Pg(di,m))
      if s=='585':
        agree['dsoc_neg']+=(ds<0); agree['dsic_pos']+=(di>0); agree['dsoc']+=ds; agree['dsoc2']+=ds**2; agree['dsic']+=di; agree['dsic2']+=di**2
  del z
n=nM; nf=nM*len(GCMS)
cell={}
for v in ['soc','sic','ma']:
  mu=acc[v]/n; sd=np.sqrt(np.maximum(acc[v+'2']/n-mu**2,0)*n/(n-1)); cell[f'cv_{v}']=np.where(mu>0.5,sd/np.maximum(mu,1e-6)*100,np.nan); cell[f'sd_{v}']=sd
for v in ['dsoc','dsic']:
  mu=agree[v]/nf; cell[f'sd_{v}_585']=np.sqrt(np.maximum(agree[v+'2']/nf-mu**2,0)*nf/(nf-1)); cell[f'mean_{v}_585']=mu
cell['frac_dsoc_neg_585']=agree['dsoc_neg']/nf; cell['frac_dsic_pos_585']=agree['dsic_pos']/nf
np.savez_compressed(O13+'/cellmaps_v13.npz',**{k:np.asarray(v,'float32') for k,v in cell.items()})
out['present_regions']={g:{k:{key:st(v) for key,v in d.items()} for k,d in G.items()} for g,G in pres.items()}
out['future_regions']={g:{k:{s:{q:st(v) for q,v in d.items()} for s,d in S.items()} for k,S in G.items()} for g,G in reg_fut.items()}
# transitions: area and Pg (ensemble mean map) + member spread
tr={}
for s in SSP:
  tk=np.char.add(np.char.add(km0.astype('U1'),'>'),KF[s].astype('U1')); tr[s]={}
  for t in np.unique(tk):
    if t[0]==t[-1]: continue
    m=tk==t; tr[s][t]=dict(area_Mkm2=float(area[m].sum()/1e8),dSOC=st(trans_mem[s][t]['dsoc']),dSIC=st(trans_mem[s][t]['dsic']),
       map_dSOC=Pg(EM[f'dsoc_0_200_{s}'],m),map_dSIC=Pg(EM[f'dsic_0_200_{s}'],m))
  tr[s]['_any_main_change_Mkm2']=float(area[km0!=KF[s]].sum()/1e8)
  M5=np.zeros((5,5))
  for a_,A in enumerate('ABCDE'):
    for b_,B in enumerate('ABCDE'): M5[a_,b_]=area[(km0==A)&(KF[s]==B)].sum()/1e8
  tr[s]['_matrix_Mkm2']=M5.tolist()
out['transitions_main']=tr
out['v6_shift_Mkm2']={s:float(area[np.load(R+f'/out/v6/shift_{s}.npz')['shift'].astype(bool)].sum()/1e8) for s in SSP}
# latitude profiles (ensemble mean maps), Pg per 1 deg band
bands=np.arange(-56,84); lp={'lat':bands.tolist()}
src={'SOC_0_30':EM['p_soc_0_30'],'SOC_30_100':EM['p_soc_30_100'],'SOC_100_200':EM['p_soc_100_200'],'SIC_0_30':EM['p_sic_0_30'],'SIC_30_100':EM['p_sic_30_100'],'SIC_100_200':EM['p_sic_100_200'],
     'MAOC_0_30':EM['p_MA'],'POC_0_30':EM['p_PO'],'MAOC_30_100':fr8['MA_30_100'],'POC_30_100':fr8['PO_30_100']}
for s in SSP: src[f'dSOC_0_200_{s}']=EM[f'dsoc_0_200_{s}']; src[f'dSIC_0_200_{s}']=EM[f'dsic_0_200_{s}']
for k,v in src.items(): lp[k]=np.bincount(band-(-56),weights=np.nan_to_num(v)*area*1e-9,minlength=len(bands)+30)[:len(bands)].tolist()
lp['area_Mkm2']=np.bincount(band+56,weights=area/1e8,minlength=len(bands)+30)[:len(bands)].tolist()
out['lat_profiles']=lp
# countries (ensemble mean maps) present + future + N
def bc(v): return np.bincount(ids,weights=np.nan_to_num(v)*area,minlength=len(nm))*1e-9
C={'SOC_0_30':bc(EM['p_soc_0_30']),'SOC_0_200':bc(EM['p_soc_0_30']+EM['p_soc_30_100']+EM['p_soc_100_200']),'SIC_0_30':bc(EM['p_sic_0_30']),
   'SIC_0_200':bc(EM['p_sic_0_30']+EM['p_sic_30_100']+EM['p_sic_100_200']),'MAOC_0_30':bc(EM['p_MA']),'POC_0_30':bc(EM['p_PO']),
   'dSOC_585':bc(EM['dsoc_0_200_585']),'dSIC_585':bc(EM['dsic_0_200_585']),'dSOC_126':bc(EM['dsoc_0_200_126']),'dSIC_126':bc(EM['dsic_0_200_126']),
   'tl_dTC_585':bc(EM['tl_dtc_0_200_585']),'Nloss_0_200_585':bc(EM['N_loss_0_200_585']),'area_Mkm2':np.bincount(ids,weights=area/1e8,minlength=len(nm))}
out['countries']=[dict(name=str(nm[i]),cont=str(ct[i]),**{k:float(v[i]) for k,v in C.items()}) for i in range(1,len(nm)) if C['area_Mkm2'][i]>0]
# global per-GCM (member json)
J=[json.load(open(f.replace('.npz','.json'))) for f in M]; pg={}
for s in SSP:
  for gc in GCMS:
    L=[j['fut'][f'{s}_{gc}'] for j in J]
    pg[f'{s}_{gc}']=dict(dSOC_0_200=st([q['dsoc_0_30']+q['dsoc_30_100']+q['dsoc_100_200'] for q in L]),dSIC_0_200=st([q['dsic_0_30']+q['dsic_30_100']+q['dsic_100_200'] for q in L]),
       dTC_0_200=st([q['dsoc_0_30']+q['dsoc_30_100']+q['dsoc_100_200']+q['dsic_0_30']+q['dsic_30_100']+q['dsic_100_200'] for q in L]),
       dSOC_0_30=st([q['dsoc_0_30'] for q in L]),dSIC_0_30=st([q['dsic_0_30'] for q in L]),dMAOC=st([q['dMA'] for q in L]),dPOC=st([q['dPO'] for q in L]),dpH_mean=st([q['dph_mean'] for q in L]),
       members=dict(dSOC_0_200=[q['dsoc_0_30']+q['dsoc_30_100']+q['dsoc_100_200'] for q in L],dSIC_0_200=[q['dsic_0_30']+q['dsic_30_100']+q['dsic_100_200'] for q in L]))
out['per_gcm']=pg
json.dump(out,open(O13+'/summaries_v13.json','w'),indent=1); print('DONE')
