# Science-quality figures with Robinson projection via pyproj, Okabe-Ito / cividis, panel letters
import numpy as np, json, os, glob
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, ListedColormap
import matplotlib.gridspec as gridspec
from pyproj import Transformer
O='out/v7'; FM='figs/v7_main'; FS='figs/v7_SI'
os.makedirs(FM,exist_ok=True); os.makedirs(FS,exist_ok=True)
plt.rcParams.update({'font.size':7,'font.family':'DejaVu Sans','axes.linewidth':0.5,'pdf.fonttype':42,'ps.fonttype':42,
  'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':300})
C=dict(soc='#009E73',sic='#E69F00',tc='#0072B2',neg='#D55E00',pos='#56B4E9',org='#CC79A7',neut='#999999')
mask=np.load('out/v4/mask.npy'); H,W=mask.shape
# Robinson helpers: plot geographic with aspect for Robinson look (true Robinson pcolormesh)
tr=Transformer.from_crs('EPSG:4326','+proj=robin +lon_0=0 +datum=WGS84 +units=m +no_defs',always_xy=True)
lon=np.linspace(-180,180,W); lat=np.linspace(90,-90,H)
LON,LAT=np.meshgrid(lon,lat)
X,Y=tr.transform(LON,LAT)
def to2d(v):
  a=np.full(mask.shape,np.nan); a[mask]=v; return a
def save(fig,path):
  fig.savefig(path+'.png',dpi=300,bbox_inches='tight',facecolor='white')
  fig.savefig(path+'.pdf',bbox_inches='tight',facecolor='white'); plt.close(fig); print('wrote',path)
def world(ax,arr,cmap,vmin,vmax,title):
  Z=np.ma.array(arr,mask=~np.isfinite(arr))
  pcm=ax.pcolormesh(X,Y,Z,cmap=cmap,vmin=vmin,vmax=vmax,shading='auto',rasterized=True)
  ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title,loc='left',fontweight='bold',fontsize=8)
  # simple coastline-ish: mask edge
  return pcm

stocks=json.load(open(f'{O}/stocks10.json'))
z0=np.load(f'{O}/maps10_0_30.npz'); z1=np.load(f'{O}/maps10_30_100.npz'); z2=np.load(f'{O}/maps10_100_200.npz')
soc=to2d(z0['soc']+z1['soc']+z2['soc']); sic=to2d(z0['sic']+z1['sic']+z2['sic']); tc=soc+sic
# prefer 30s if complete
s30=f'{O}/stocks30_0_30.json'
use30=os.path.exists(s30) and os.path.exists(f'{O}/maps30s/socstock_0_30.tif')
note30=''
if use30:
  import rasterio
  with rasterio.open(f'{O}/maps30s/socstock_0_30.tif') as ds:
    # downsample for plotting
    soc30=ds.read(1,out_shape=(H,W),resampling=rasterio.enums.Resampling.average)
  with rasterio.open(f'{O}/maps30s/sicstock_0_30.tif') as ds:
    sic30=ds.read(1,out_shape=(H,W),resampling=rasterio.enums.Resampling.average)
  note30=' (0–30 cm maps inset from 30″)'

# Fig1
fig=plt.figure(figsize=(7.2,7.0)); gs=gridspec.GridSpec(3,2,height_ratios=[1.1,1.1,0.9],hspace=0.25,wspace=0.08)
ax=fig.add_subplot(gs[0,0]); pcm=world(ax,soc,'cividis',0,350,'a  SOC 0–200 cm'); plt.colorbar(pcm,ax=ax,fraction=0.03,pad=0.02).set_label('Mg C ha$^{-1}$')
ax=fig.add_subplot(gs[0,1]); pcm=world(ax,sic,'cividis',0,350,'b  SIC 0–200 cm'); plt.colorbar(pcm,ax=ax,fraction=0.03,pad=0.02).set_label('Mg C ha$^{-1}$')
ax=fig.add_subplot(gs[1,:]); pcm=world(ax,tc,'viridis',0,550,'c  Total soil carbon 0–200 cm'); plt.colorbar(pcm,ax=ax,fraction=0.02,pad=0.01).set_label('Mg C ha$^{-1}$')
ax=fig.add_subplot(gs[2,:]); x=np.arange(3); labs=['0–30','30–100','100–200']
ax.bar(x-0.18,[stocks[f'_{a}_{b}']['SOC'] for a,b in [(0,30),(30,100),(100,200)]],0.36,color=C['soc'],label='SOC')
ax.bar(x+0.18,[stocks[f'_{a}_{b}']['SIC'] for a,b in [(0,30),(30,100),(100,200)]],0.36,color=C['sic'],label='SIC')
ax.scatter([-0.18],[704],marker='_',s=220,c='k',zorder=5); ax.scatter([-0.18],[658],marker='x',s=35,c='k',zorder=5)
ax.text(0.02,0.92,'— Batjes mid   × SoilGrids',transform=ax.transAxes,fontsize=5.5)
ax.set_xticks(x,labs); ax.set_ylabel('Pg C'); ax.legend(frameon=False,fontsize=6,loc='upper right')
ax.set_title('d  Global integrals (Huang-style QC + declustering)',loc='left',fontweight='bold')
if os.path.exists(s30):
  st=json.load(open(s30)); ax.text(0.98,0.08,f"30″ 0–30: SOC {st['SOC_0_30_Pg']:.0f} / SIC {st['SIC_0_30_Pg']:.0f} Pg",transform=ax.transAxes,ha='right',fontsize=5.5,color=C['neut'])
save(fig,f'{FM}/Fig1_present_stocks')

# Fig2 CV
hp=json.load(open(f'{O}/hp_cv.json'))['results']
fig,axes=plt.subplots(1,3,figsize=(7.2,2.5)); deps=['_0_30','_30_100','_100_200']; lab=['0–30','30–100','100–200']; x=np.arange(3)
axes[0].bar(x-0.15,[hp[d]['SIC']['AUC'] for d in deps],0.3,color=C['tc'],label='AUC'); axes[0].bar(x+0.15,[hp[d]['SIC']['r2'] for d in deps],0.3,color=C['sic'],label='R²')
axes[0].axhline(0.99,ls=':',c=C['tc'],lw=0.6); axes[0].axhline(0.79,ls=':',c=C['sic'],lw=0.6); axes[0].legend(frameon=False,fontsize=5)
axes[0].set_title('a  SIC (random 10-fold)',loc='left',fontweight='bold')
axes[1].bar(x,[hp[d]['pH']['r2'] for d in deps],color=C['org']); axes[1].axhline(0.85,ls=':',c='k',lw=0.6)
axes[1].set_title('b  pH R²',loc='left',fontweight='bold')
axes[2].bar(x,[hp[d]['SOC_mineral']['r2'] for d in deps],color=C['soc']); axes[2].set_title('c  Mineral SOC R²',loc='left',fontweight='bold')
for ax in axes: ax.set_xticks(x,lab); ax.set_ylim(0,1.05)
save(fig,f'{FM}/Fig2_random_CV')

# Fig3
Z=json.load(open('out/v6/zone_shift.json')); sh=np.load('out/v6/shift_585.npz')
fig=plt.figure(figsize=(7.2,5.2)); gs=gridspec.GridSpec(2,2,hspace=0.28,wspace=0.12)
ax=fig.add_subplot(gs[0,0]); pcm=world(ax,to2d(sh['dsoc']),'RdBu_r',-120,120,'a  ΔSOC SSP5-8.5 (eq.)'); plt.colorbar(pcm,ax=ax,fraction=0.03).set_label('Mg C ha$^{-1}$')
ax=fig.add_subplot(gs[0,1]); pcm=world(ax,to2d(sh['dsic']),'RdBu_r',-80,80,'b  ΔSIC SSP5-8.5 (eq.)'); plt.colorbar(pcm,ax=ax,fraction=0.03)
cat=np.zeros(mask.sum(),int); cat[(sh['dsoc']<0)&(sh['dsic']>0)]=1; cat[(sh['dsoc']<0)&(sh['dsic']<0)]=2; cat[(sh['dsoc']>0)&(sh['dsic']>0)]=3
ax=fig.add_subplot(gs[1,0]); cmap=ListedColormap(['#f0f0f0',C['org'],C['neg'],C['soc']])
world(ax,to2d(cat.astype(float)),cmap,-0.5,3.5,'c  SOC–SIC classes'); 
ax=fig.add_subplot(gs[1,1]); ssps=['126','245','370','585']; nm=['1-2.6','2-4.5','3-7.0','5-8.5']; x=np.arange(4)
ax.bar(x-0.15,[Z[s]['land_shift_Mkm2'] for s in ssps],0.3,color=C['neut'],label='Zone shift')
ax.bar(x+0.15,[Z[s]['tradeoff_SOC_loss_SIC_gain_Mkm2'] for s in ssps],0.3,color=C['org'],label='Trade-off')
ax.set_xticks(x,nm); ax.set_ylabel('Mkm²'); ax.legend(frameon=False,fontsize=5.5); ax.set_title('d  Areas by SSP',loc='left',fontweight='bold')
save(fig,f'{FM}/Fig3_climate_zones')

# Fig4
R5=json.load(open('out/v5/results_v5.json'))
fig,ax=plt.subplots(1,2,figsize=(7.2,2.7)); SC=['126_2081-2100','245_2081-2100','370_2081-2100','585_2081-2100']; nm=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']; x=np.arange(4)
for k,key,tk in [(0,'dSOC','dSOC_0_200'),(1,'dTC','dTC_0_200')]:
  E=np.array([R5['eq'][sc]['_0_200'][key] for sc in SC]); T=np.array([R5['transient'][sc][tk] for sc in SC])
  ax[k].errorbar(x-0.08,E[:,0],yerr=[E[:,0]-E[:,1],E[:,2]-E[:,0]],fmt='o',ms=5,c=C['neg'],capsize=2,label='Equilibrium')
  ax[k].errorbar(x+0.08,T[:,0],yerr=[T[:,0]-T[:,1],T[:,2]-T[:,0]],fmt='s',ms=5,c=C['pos'],capsize=2,label='Time-limited')
  ax[k].axhline(0,c='k',lw=0.4); ax[k].set_xticks(x,nm); ax[k].set_ylabel('Pg C')
  ax[k].set_title(('a  ΔSOC 0–200 cm','b  ΔTotal C 0–200 cm')[k],loc='left',fontweight='bold')
ax[0].legend(frameon=False,fontsize=5.5); save(fig,f'{FM}/Fig4_eq_vs_transient')

# Fig5 N
N6=json.load(open('out/v6/N_huang_formula.json'))
fig,ax=plt.subplots(1,2,figsize=(7.2,2.8)); keys=[('ssp126_2020_2050','SSP1-2.6'),('ssp370_2020_2050','SSP3-7.0'),('ssp585_2020_2050','SSP5-8.5')]; x=np.arange(3)
loss=[-N6[k]['fert_only']['loss_only_FD_0_30'] for k,_ in keys]
zam=[N6[k]['zamanian_stoichiometry']['central']['loss_0_30'] for k,_ in keys]
ax[0].bar(x-0.25,loss,0.25,color=C['tc'],label='Huang ΔpH + our SIC (IMAGE)')
ax[0].bar(x,zam,0.25,color=C['sic'],label='Zamanian')
ax[0].bar(x+0.25,[10,14,23],0.25,color=C['neg'],label='Huang published / high-N target')
ax[0].set_xticks(x,[n for _,n in keys]); ax[0].set_ylabel('SIC loss 0–30 cm (Pg C)'); ax[0].legend(frameon=False,fontsize=5)
ax[0].set_title('a  N acidification 2020–2050',loc='left',fontweight='bold')
ax[1].bar(x,[-N6[k]['fert_only']['loss_only_FD_0_200'] for k,_ in keys],color=C['tc'])
ax[1].set_xticks(x,[n for _,n in keys]); ax[1].set_ylabel('Pg C'); ax[1].set_title('b  Loss-only 0–200 cm',loc='left',fontweight='bold')
save(fig,f'{FM}/Fig5_N_acidification')

# SI figs keep/regenerate key ones quickly
qc=json.load(open(f'{O}/qc_flow.json'))
fig,ax=plt.subplots(figsize=(7.0,2.8)); steps=[('Raw ORGC',qc['orgc_layers_raw']),('−Litter',qc['orgc_after_litter']),('Depth OK',qc['orgc_after_depth']),('≥1970',qc['orgc_after_pre1970']),('Value QC',qc['orgc_after_valueQC']),('Profiles',qc['profiles_with_any_after_QC'])]
ax.bar(range(len(steps)),[s[1] for s in steps],color=C['tc']); ax.set_xticks(range(len(steps)),[s[0] for s in steps],rotation=15,ha='right')
for i,(_,v) in enumerate(steps): ax.text(i,v,f'{v:,}',ha='center',va='bottom',fontsize=5.5)
ax.set_ylabel('Count'); ax.set_title('a  QC flow (ORGC example)',loc='left',fontweight='bold'); save(fig,f'{FS}/FigS1_QC_flow')

# copy remaining SI if missing from prior
print('main',len(glob.glob(FM+'/*.png')),'SI',len(glob.glob(FS+'/*.png')))
