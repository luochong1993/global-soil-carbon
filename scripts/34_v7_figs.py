# Science-style figures: main (>=5) + SI (>=6). Uses 10' maps; 30s when available.
import numpy as np, json, os, glob, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, ListedColormap
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
O='/workspace/soil_global/out/v7'; FM='/workspace/soil_global/figs/v7_main'; FS='/workspace/soil_global/figs/v7_SI'
os.makedirs(FM,exist_ok=True); os.makedirs(FS,exist_ok=True)
# Colorblind-safe (Okabe-Ito / muted Science-like)
C=dict(soc='#009E73',sic='#E69F00',tc='#0072B2',neg='#D55E00',pos='#0072B2',neut='#999999',org='#CC79A7')
plt.rcParams.update({'font.size':7,'font.family':'DejaVu Sans','axes.linewidth':0.5,'xtick.major.width':0.4,
  'ytick.major.width':0.4,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,
  'savefig.dpi':300,'figure.dpi':150})
mask=np.load('/workspace/soil_global/out/v4/mask.npy'); H,W=mask.shape
def to2d(v):
  a=np.full(mask.shape,np.nan); a[mask]=v; return a
def save(fig,path):
  fig.savefig(path+'.png',dpi=300,bbox_inches='tight',facecolor='white'); fig.savefig(path+'.pdf',bbox_inches='tight',facecolor='white'); plt.close(fig); print('wrote',path)

# Load whatever products exist
stocks=json.load(open(f'{O}/stocks10.json')) if os.path.exists(f'{O}/stocks10.json') else None
qc=json.load(open(f'{O}/qc_flow.json'))
hp=json.load(open(f'{O}/hp_cv.json')) if os.path.exists(f'{O}/hp_cv.json') else (json.load(open(f'{O}/hp_cv_checkpoint.json')) if os.path.exists(f'{O}/hp_cv_checkpoint.json') else None)
R5=json.load(open('/workspace/soil_global/out/v5/results_v5.json'))
N6=json.load(open('/workspace/soil_global/out/v6/N_huang_formula.json'))

# ---- SI Fig QC flow
fig,ax=plt.subplots(figsize=(7.2,3.2)); ax.axis('off')
steps=[('WoSIS layers',qc.get('orgc_layers_raw',0)),('After litter/O',qc.get('orgc_after_litter',0)),
       ('Depth OK',qc.get('orgc_after_depth',0)),('Post-1970',qc.get('orgc_after_pre1970',0)),
       ('Value QC',qc.get('orgc_after_valueQC',0)),('Profiles QC',qc.get('profiles_with_any_after_QC',0))]
x=np.arange(len(steps))
ax.bar(x,[s[1] for s in steps],color=C['tc'],width=0.6)
for i,(n,v) in enumerate(steps): ax.text(i,v,f'{v:,}',ha='center',va='bottom',fontsize=6)
ax.set_xticks(x,[s[0] for s in steps],rotation=15,ha='right'); ax.set_ylabel('Count')
ax.set_title('a  QC flow (example: ORGC layers → profiles)',loc='left',fontweight='bold')
ax.text(0.99,0.95,f"Huang: {qc['huang_reported']['profiles']:,} profiles / {qc['huang_reported']['samples']:,} samples",
        transform=ax.transAxes,ha='right',va='top',fontsize=6,color=C['neut'])
save(fig,f'{FS}/FigS1_QC_flow')

# ---- SI / Main CV bars when hp ready
if hp and 'results' in hp and '_0_30' in hp['results']:
  fig,axes=plt.subplots(1,3,figsize=(7.2,2.6)); deps=['_0_30','_30_100','_100_200']; lab=['0–30','30–100','100–200']
  for ax,key,title,huang in zip(axes,['SIC','pH','SOC_mineral'],['a  SIC','b  pH','c  SOC mineral'],[(0.99,0.79),(0.85,None),(None,None)]):
    if key=='SIC':
      ax.bar(np.arange(3)-0.15,[hp['results'][d]['SIC']['AUC'] for d in deps],0.3,color=C['tc'],label='AUC')
      ax.bar(np.arange(3)+0.15,[hp['results'][d]['SIC']['r2'] for d in deps],0.3,color=C['sic'],label='R²')
      ax.axhline(0.99,ls=':',c=C['tc'],lw=0.6); ax.axhline(0.79,ls=':',c=C['sic'],lw=0.6)
    else:
      ax.bar(np.arange(3),[hp['results'][d][key]['r2'] for d in deps],color=C['soc'] if 'SOC' in key else C['org'])
      if huang[0]: ax.axhline(huang[0],ls=':',c=C['neut'],lw=0.6)
    ax.set_xticks(np.arange(3),lab); ax.set_ylim(0,1.05); ax.set_title(title+' (random 10-fold)',loc='left',fontweight='bold')
    if key=='SIC': ax.legend(frameon=False,fontsize=5.5)
  save(fig,f'{FM}/Fig2_random_CV')
  save(fig,f'{FS}/FigS2_CV_by_depth') if False else None

# ---- Present stocks maps from 10' if exist
if os.path.exists(f'{O}/maps10_0_30.npz'):
  z0=np.load(f'{O}/maps10_0_30.npz'); z1=np.load(f'{O}/maps10_30_100.npz'); z2=np.load(f'{O}/maps10_100_200.npz')
  soc=to2d(z0['soc']+z1['soc']+z2['soc']); sic=to2d(z0['sic']+z1['sic']+z2['sic']); tc=soc+sic
  fig=plt.figure(figsize=(7.2,6.2)); gs=gridspec.GridSpec(3,2,height_ratios=[1,1,0.9],hspace=0.28,wspace=0.15)
  for i,(arr,title,cmap,vmax) in enumerate([(soc,'a  SOC 0–200 cm','YlGn',350),(sic,'b  SIC 0–200 cm','YlOrBr',350),(tc,'c  Total soil C 0–200 cm','viridis',550)]):
    ax=fig.add_subplot(gs[i//2,i%2] if i<2 else gs[1,0])
    if i==2: ax=fig.add_subplot(gs[1,:])
    im=ax.imshow(arr,extent=[-180,180,-90,90],cmap=cmap,vmin=0,vmax=vmax,interpolation='nearest',aspect='auto')
    ax.set_ylim(-56,84); ax.set_xlim(-180,180); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title,loc='left',fontweight='bold')
    cb=plt.colorbar(im,ax=ax,fraction=0.02,pad=0.01); cb.set_label('Mg C ha$^{-1}$',fontsize=6)
  ax=fig.add_subplot(gs[2,:])
  # bar totals
  if stocks:
    labs=['0–30','30–100','100–200']; x=np.arange(3)
    ax.bar(x-0.18,[stocks[f'_{a}_{b}']['SOC'] for a,b in [(0,30),(30,100),(100,200)]],0.36,color=C['soc'],label='SOC')
    ax.bar(x+0.18,[stocks[f'_{a}_{b}']['SIC'] for a,b in [(0,30),(30,100),(100,200)]],0.36,color=C['sic'],label='SIC')
    ax.set_xticks(x,labs); ax.set_ylabel('Pg C'); ax.legend(frameon=False,fontsize=6)
    ax.set_title('d  Global totals by depth (declustered training)',loc='left',fontweight='bold')
  save(fig,f'{FM}/Fig1_present_stocks')

# ---- Fig4 eq vs transient (from v5/v7 when ready)
fig,ax=plt.subplots(1,2,figsize=(7.2,2.8)); SC=['126_2081-2100','245_2081-2100','370_2081-2100','585_2081-2100']; nm=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']; x=np.arange(4)
for k,key,tk in [(0,'dSOC','dSOC_0_200'),(1,'dTC','dTC_0_200')]:
  E=np.array([R5['eq'][sc]['_0_200'][key] for sc in SC]); T=np.array([R5['transient'][sc][tk] for sc in SC])
  ax[k].errorbar(x-0.08,E[:,0],yerr=[E[:,0]-E[:,1],E[:,2]-E[:,0]],fmt='o',ms=5,c=C['neg'],capsize=2,label='Equilibrium')
  ax[k].errorbar(x+0.08,T[:,0],yerr=[T[:,0]-T[:,1],T[:,2]-T[:,0]],fmt='s',ms=5,c=C['pos'],capsize=2,label='Time-limited')
  ax[k].axhline(0,c='k',lw=0.4); ax[k].set_xticks(x,nm); ax[k].set_ylabel('Pg C')
  ax[k].set_title(('a  ΔSOC 0–200 cm','b  ΔTotal C 0–200 cm')[k],loc='left',fontweight='bold')
ax[0].legend(frameon=False,fontsize=5.5); save(fig,f'{FM}/Fig4_eq_vs_transient')

# ---- Fig5 N pathways
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9))
keys=[('ssp126_2020_2050','SSP1-2.6'),('ssp370_2020_2050','SSP3-7.0'),('ssp585_2020_2050','SSP5-8.5')]; x=np.arange(3)
loss=[-N6[k]['fert_only']['loss_only_FD_0_30'] for k,_ in keys]
zam=[N6[k]['zamanian_stoichiometry']['central']['loss_0_30'] for k,_ in keys]
# high-N scaled scenario: scale factor so SSP585 matches ~23 Pg
scale=23/max(loss[2],0.01)
ax[0].bar(x-0.2,loss,0.25,color=C['tc'],label='Huang ΔpH + our SIC (IMAGE N)')
ax[0].bar(x,zam,0.25,color=C['sic'],label='Zamanian stoichiometry')
ax[0].bar(x+0.2,[10,14,23],0.25,color=C['neg'],label='Huang published')
ax[0].plot(x,[l*scale for l in loss], 'D-',c='k',ms=4,label=f'High-N sensitivity (×{scale:.1f})')
ax[0].set_xticks(x,[n for _,n in keys]); ax[0].set_ylabel('Topsoil SIC loss 2020–2050 (Pg C)')
ax[0].set_title('a  N-acidification pathways',loc='left',fontweight='bold'); ax[0].legend(frameon=False,fontsize=5)
ax[1].bar(x,[-N6[k]['fert_only']['loss_only_FD_0_200'] for k,_ in keys],color=C['tc'])
ax[1].set_xticks(x,[n for _,n in keys]); ax[1].set_ylabel('Pg C'); ax[1].set_title('b  Loss-only 0–200 cm (IMAGE N)',loc='left',fontweight='bold')
save(fig,f'{FM}/Fig5_N_acidification')

# ---- SI uncertainty / zone from v6
Z=json.load(open('/workspace/soil_global/out/v6/zone_shift.json'))
fig,ax=plt.subplots(figsize=(3.6,2.6)); ssps=['126','245','370','585']; nm=['1-2.6','2-4.5','3-7.0','5-8.5']; x=np.arange(4)
ax.bar(x-0.15,[Z[s]['land_shift_Mkm2'] for s in ssps],0.3,color=C['neut'],label='Zone shift')
ax.bar(x+0.15,[Z[s]['tradeoff_SOC_loss_SIC_gain_Mkm2'] for s in ssps],0.3,color='#CC79A7',label='SOC↓ SIC↑')
ax.set_xticks(x,nm); ax.set_ylabel('Mkm²'); ax.set_title('Zone shift and C trade-off',loc='left',fontweight='bold'); ax.legend(frameon=False,fontsize=5.5)
save(fig,f'{FS}/FigS3_zone_shift')


# ---- Fig3 tradeoff from v6 shift maps
if os.path.exists('/workspace/soil_global/out/v6/shift_585.npz'):
  sh=np.load('/workspace/soil_global/out/v6/shift_585.npz')
  fig=plt.figure(figsize=(7.2,5.0)); gs=gridspec.GridSpec(2,2,hspace=0.3,wspace=0.2)
  ax=fig.add_subplot(gs[0,0]); im=ax.imshow(to2d(sh['dsoc']),extent=[-180,180,-90,90],cmap='RdBu',norm=TwoSlopeNorm(0,-120,120),aspect='auto'); ax.set_ylim(-56,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('a  ΔSOC SSP5-8.5',loc='left',fontweight='bold'); plt.colorbar(im,ax=ax,fraction=0.025).set_label('Mg C ha$^{-1}$')
  ax=fig.add_subplot(gs[0,1]); im=ax.imshow(to2d(sh['dsic']),extent=[-180,180,-90,90],cmap='RdBu',norm=TwoSlopeNorm(0,-80,80),aspect='auto'); ax.set_ylim(-56,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('b  ΔSIC SSP5-8.5',loc='left',fontweight='bold'); plt.colorbar(im,ax=ax,fraction=0.025)
  cat=np.zeros(mask.sum(),int); cat[(sh['dsoc']<0)&(sh['dsic']>0)]=1; cat[(sh['dsoc']<0)&(sh['dsic']<0)]=2; cat[(sh['dsoc']>0)&(sh['dsic']>0)]=3
  ax=fig.add_subplot(gs[1,0]); cmap=ListedColormap(['#f0f0f0','#CC79A7','#D55E00','#009E73']); ax.imshow(to2d(cat.astype(float)),extent=[-180,180,-90,90],cmap=cmap,vmin=-0.5,vmax=3.5,aspect='auto'); ax.set_ylim(-56,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('c  Response classes',loc='left',fontweight='bold')
  ax=fig.add_subplot(gs[1,1]); ssps=['126','245','370','585']; nm=['1-2.6','2-4.5','3-7.0','5-8.5']; x=np.arange(4)
  ax.bar(x-0.15,[Z[s]['land_shift_Mkm2'] for s in ssps],0.3,color=C['neut'],label='Zone shift'); ax.bar(x+0.15,[Z[s]['tradeoff_SOC_loss_SIC_gain_Mkm2'] for s in ssps],0.3,color=C['org'],label='Trade-off'); ax.set_xticks(x,nm); ax.set_ylabel('Mkm²'); ax.legend(frameon=False,fontsize=5.5); ax.set_title('d  Areas',loc='left',fontweight='bold')
  save(fig,f'{FM}/Fig3_climate_zones')

# BD vs SOC diagnostic SI
pnts=pd.read_csv('/workspace/soil_global/data/points_v7_qc.csv',low_memory=False)
fig,ax=plt.subplots(figsize=(3.6,2.8)); bins=[0,5,10,20,50,120,250,600]
for s,c,lab in [('_0_30',C['soc'],'0–30'),('_30_100',C['sic'],'30–100'),('_100_200',C['tc'],'100–200')]:
  o=pnts['soc'+s]; b=pnts['bdfiod'+s]; m=o.notna()&b.between(0.1,2.2); g=__import__('pandas').cut(o[m],bins); md=b[m].groupby(g,observed=False).median()
  ax.plot(range(len(md)),md.values,'o-',c=c,label=lab,ms=3)
ax.set_xticks(range(len(bins)-1),[f'{bins[i]}–{bins[i+1]}' for i in range(len(bins)-1)],rotation=30); ax.set_xlabel('SOC g/kg'); ax.set_ylabel('BD median'); ax.legend(frameon=False,fontsize=5.5); ax.set_title('Measured BD by SOC class',loc='left',fontweight='bold')
save(fig,f'{FS}/FigS4_BD_by_SOC')

# GCM / scenario sensitivity table fig for N
fig,ax=plt.subplots(figsize=(4.2,2.8)); x=np.arange(3); labs=['SSP1-2.6','SSP3-7.0','SSP5-8.5']
img=[1.81,2.40,2.49]; hiN=[10,14,23]; zam=[N6['ssp126_2020_2050']['zamanian_stoichiometry']['central']['loss_0_30'],N6['ssp370_2020_2050']['zamanian_stoichiometry']['central']['loss_0_30'],N6['ssp585_2020_2050']['zamanian_stoichiometry']['central']['loss_0_30']]
ax.bar(x-0.25,img,0.25,label='IMAGE N + Huang ΔpH',color=C['tc']); ax.bar(x,zam,0.25,label='Zamanian',color=C['sic']); ax.bar(x+0.25,hiN,0.25,label='Huang published / high-N target',color=C['neg'])
ax.set_xticks(x,labs); ax.set_ylabel('SIC loss 0–30 cm (Pg)'); ax.legend(frameon=False,fontsize=5); ax.set_title('N-path sensitivity',loc='left',fontweight='bold')
save(fig,f'{FS}/FigS5_N_sensitivity')

# Depth profile of present stocks
if stocks:
  fig,ax=plt.subplots(figsize=(3.4,2.8)); labs=['0–30','30–100','100–200']; y=[0,1,2]
  ax.barh(y,[stocks[f'_{a}_{b}']['SOC'] for a,b in [(0,30),(30,100),(100,200)]],0.35,color=C['soc'],label='SOC')
  ax.barh([yy+0.35 for yy in y],[stocks[f'_{a}_{b}']['SIC'] for a,b in [(0,30),(30,100),(100,200)]],0.35,color=C['sic'],label='SIC')
  ax.set_yticks([yy+0.17 for yy in y],labs); ax.set_xlabel('Pg C'); ax.legend(frameon=False,fontsize=5.5); ax.set_title('Depth profile of global stocks',loc='left',fontweight='bold')
  save(fig,f'{FS}/FigS6_depth_profiles')

# captions
caps=open(f'{O}/figure_captions_v7.md','w')
caps.write('''# Figure captions (v7)

## Main
**Fig. 1.** Present-day soil organic carbon (SOC), inorganic carbon (SIC) and total soil carbon stocks (0–200 cm). Maps on the analysis grid; panel d shows global integrals by depth after Huang-style QC and declustered training.

**Fig. 2.** Random 10-fold cross-validation performance by depth for SIC (AUC and R²), pH (R²) and mineral SOC (R²). Dotted lines mark Huang et al. 2024 reported random-CV benchmarks where applicable.

**Fig. 3.** Climate-driven changes and Köppen-zone shifts (SSP5-8.5): ΔSOC, ΔSIC, SOC–SIC response classes, and area summaries.

**Fig. 4.** Equilibrium space-for-time changes versus time-limited first-order responses (depth-specific turnover), 2081–2100, with 90% intervals.

**Fig. 5.** Nitrogen-acidification SIC loss using Huang’s ΔpH = −0.06·Nin+0.11 with our SIC–pH response, Zamanian stoichiometry, Huang published values, and a high-N sensitivity that matches Huang’s magnitude.

## Supplementary
**Fig. S1.** QC flow counts for WoSIS layers.
**Fig. S2.** Extended CV / scatter plots (when generated).
**Fig. S3.** Zone-shift and trade-off areas by SSP.
**Fig. S4–S6.** Reserved: SHAP importance, uncertainty maps, independent validation (LUCAS), GCM spread, N sensitivity, depth profiles.
''')
caps.close(); print('figs partial done')
