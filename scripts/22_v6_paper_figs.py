# Science-style multi-panel figures for main text
import numpy as np, json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import matplotlib.gridspec as gridspec
O='out/v6'; F='figs/v6_paper'; import os; os.makedirs(F,exist_ok=True)
plt.rcParams.update({'font.size':7,'font.family':'Arial','axes.linewidth':0.6,'xtick.major.width':0.5,'ytick.major.width':0.5,
  'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
# fallback font
import matplotlib; matplotlib.rcParams['font.family']='DejaVu Sans'
P=json.load(open(f'{O}/paper_numbers.json')); R5=json.load(open('out/v5/results_v5.json'))
mask=np.load('out/v4/mask.npy'); H,W=mask.shape
lat=np.linspace(90,-90,H+1)[:-1]-90/H
def to2d(v):
  a=np.full(mask.shape,np.nan); a[mask]=v; return a
z5=np.load('out/v5/maps_b0.npz')
soc=to2d(z5['soc_0_30']+z5['soc_30_100']+z5['soc_100_200'])
sic=to2d(z5['sic_0_30']+z5['sic_30_100']+z5['sic_100_200'])
tc=soc+sic

# ---- Fig1 present stocks
fig=plt.figure(figsize=(7.2,5.2)); gs=gridspec.GridSpec(2,2,height_ratios=[1.2,1],hspace=0.35,wspace=0.25)
for i,(arr,title,cmap,vmax) in enumerate([(soc,'a  SOC 0–200 cm','YlGn',400),(sic,'b  SIC 0–200 cm','YlOrBr',400),(tc,'c  Total C 0–200 cm','viridis',600)]):
  ax=fig.add_subplot(gs[0,i] if i<2 else gs[1,0])
  if i==2: ax=fig.add_subplot(gs[1,0])
  im=ax.imshow(arr,extent=[-180,180,-90,90],cmap=cmap,vmin=0,vmax=vmax,interpolation='nearest')
  ax.set_ylim(-60,84); ax.set_title(title,loc='left',fontweight='bold',fontsize=8); ax.set_xticks([]); ax.set_yticks([])
  cb=plt.colorbar(im,ax=ax,fraction=0.025,pad=0.02); cb.set_label('Mg C ha$^{-1}$',fontsize=6); cb.ax.tick_params(labelsize=5)
ax=fig.add_subplot(gs[1,1])
labs=['0–30','30–100','100–200','0–200']; x=np.arange(4)
socv=[P['present'][s]['SOC']['median'] for s in ['_0_30','_30_100','_100_200','_0_200']]
sicv=[P['present'][s]['SIC']['median'] for s in ['_0_30','_30_100','_100_200','_0_200']]
soce=np.array([[P['present'][s]['SOC']['median']-P['present'][s]['SOC']['p05'],P['present'][s]['SOC']['p95']-P['present'][s]['SOC']['median']] for s in ['_0_30','_30_100','_100_200','_0_200']]).T
sice=np.array([[P['present'][s]['SIC']['median']-P['present'][s]['SIC']['p05'],P['present'][s]['SIC']['p95']-P['present'][s]['SIC']['median']] for s in ['_0_30','_30_100','_100_200','_0_200']]).T
ax.bar(x-0.18,socv,0.36,yerr=soce,color='#1b7837',capsize=2,label='SOC'); ax.bar(x+0.18,sicv,0.36,yerr=sice,color='#b35806',capsize=2,label='SIC')
ax.axhline(2305,ls='--',c='#b35806',lw=0.7,label='Huang SIC 0–200')
ax.set_xticks(x,labs); ax.set_ylabel('Pg C'); ax.set_title('d  Global totals (90% CI)',loc='left',fontweight='bold',fontsize=8)
ax.legend(frameon=False,fontsize=5.5); ax.set_ylim(0,2800)
plt.savefig(f'{F}/Fig1_present_stocks.png',dpi=300,bbox_inches='tight'); plt.close(); print('Fig1')

# ---- Fig2 random CV
fig,axes=plt.subplots(2,2,figsize=(7.2,5.0)); flat=axes.ravel()
CV=P['random_CV']; deps=['_0_30','_30_100','_100_200']; dlab=['0–30 cm','30–100 cm','100–200 cm']
# a SIC AUC & R2
ax=flat[0]; x=np.arange(3)
ax.bar(x-0.15,[CV[d]['SIC']['AUC'] for d in deps],0.3,color='#2166ac',label='AUC (presence)')
ax.bar(x+0.15,[CV[d]['SIC']['r2'] for d in deps],0.3,color='#92c5de',label='R² (amount)')
ax.axhline(0.99,ls=':',c='#2166ac',lw=0.7); ax.axhline(0.79,ls=':',c='#92c5de',lw=0.7)
ax.text(2.1,0.99,'Huang AUC',fontsize=5,va='bottom',c='#2166ac'); ax.text(2.1,0.79,'Huang R²',fontsize=5,va='bottom',c='#4a90a4')
ax.set_xticks(x,dlab); ax.set_ylim(0,1.05); ax.set_ylabel('Metric'); ax.set_title('a  SIC random 5-fold CV',loc='left',fontweight='bold'); ax.legend(frameon=False,fontsize=5.5)
# b SOC R2
ax=flat[1]
ax.bar(x-0.15,[CV[d]['SOC_mineral']['r2'] for d in deps],0.3,color='#1b7837',label='Mineral SOC R²')
ax.bar(x+0.15,[CV[d]['SOC_combined']['r2'] for d in deps],0.3,color='#a6dba0',label='Combined R²')
ax.set_xticks(x,dlab); ax.set_ylim(0,1); ax.set_title('b  SOC random 5-fold CV',loc='left',fontweight='bold'); ax.legend(frameon=False,fontsize=5.5)
# c pH & BD
ax=flat[2]
ax.bar(x-0.15,[CV[d]['pH']['r2'] for d in deps],0.3,color='#762a83',label='pH R²')
ax.bar(x+0.15,[CV[d]['BD']['r2'] for d in deps],0.3,color='#c2a5cf',label='BD R²')
ax.axhline(0.85,ls=':',c='#762a83',lw=0.7); ax.text(2.05,0.85,'Huang pH 0.85',fontsize=5,va='bottom')
ax.set_xticks(x,dlab); ax.set_ylim(0,1); ax.set_title('c  pH and bulk density',loc='left',fontweight='bold'); ax.legend(frameon=False,fontsize=5.5)
# d RMSE table-like
ax=flat[3]; ax.axis('off')
rows=[['Depth','SIC RMSE','SOC min RMSE','pH RMSE','BD RMSE','n SIC']]
for d,l in zip(deps,dlab):
  rows.append([l,f"{CV[d]['SIC']['rmse']:.1f}",f"{CV[d]['SOC_mineral']['rmse']:.1f}",f"{CV[d]['pH']['rmse']:.2f}",f"{CV[d]['BD']['rmse']:.2f}",str(CV[d]['SIC']['n'])])
tab=ax.table(cellText=rows[1:],colLabels=rows[0],loc='center',cellLoc='center'); tab.auto_set_font_size(False); tab.set_fontsize(6); tab.scale(1,1.4)
ax.set_title('d  RMSE (g/kg or g/cm³) and sample size',loc='left',fontweight='bold',y=0.95)
plt.tight_layout(); plt.savefig(f'{F}/Fig2_random_CV.png',dpi=300,bbox_inches='tight'); plt.close(); print('Fig2')

# ---- Fig3 zone shift / trade-off
fig=plt.figure(figsize=(7.2,5.5)); gs=gridspec.GridSpec(2,2,hspace=0.3,wspace=0.2)
sh=np.load(f'{O}/shift_585.npz')
ax=fig.add_subplot(gs[0,0]); im=ax.imshow(to2d(sh['dsoc']),extent=[-180,180,-90,90],cmap='RdBu',norm=TwoSlopeNorm(0,-150,150),interpolation='nearest')
ax.set_ylim(-60,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('a  ΔSOC 0–200 cm (SSP5-8.5 eq.)',loc='left',fontweight='bold')
plt.colorbar(im,ax=ax,fraction=0.025,pad=0.02).set_label('Mg C ha$^{-1}$',fontsize=6)
ax=fig.add_subplot(gs[0,1]); im=ax.imshow(to2d(sh['dsic']),extent=[-180,180,-90,90],cmap='RdBu',norm=TwoSlopeNorm(0,-80,80),interpolation='nearest')
ax.set_ylim(-60,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('b  ΔSIC 0–200 cm (SSP5-8.5 eq.)',loc='left',fontweight='bold')
plt.colorbar(im,ax=ax,fraction=0.025,pad=0.02).set_label('Mg C ha$^{-1}$',fontsize=6)
# trade-off map: 1=trade SOC↓SIC↑, 2=both loss, 3=both gain
cat=np.zeros(mask.sum(),dtype=int); cat[(sh['dsoc']<0)&(sh['dsic']>0)]=1; cat[(sh['dsoc']<0)&(sh['dsic']<0)]=2; cat[(sh['dsoc']>0)&(sh['dsic']>0)]=3
from matplotlib.colors import ListedColormap
ax=fig.add_subplot(gs[1,0]); cmap=ListedColormap(['#f0f0f0','#8073ac','#d73027','#1a9850'])
im=ax.imshow(to2d(cat.astype(float)),extent=[-180,180,-90,90],cmap=cmap,vmin=-0.5,vmax=3.5,interpolation='nearest')
ax.set_ylim(-60,84); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('c  SOC–SIC response classes',loc='left',fontweight='bold')
ax.legend(handles=[plt.Rectangle((0,0),1,1,fc=cmap(i+1)) for i in range(3)],labels=['SOC↓ SIC↑ trade-off','Both lose','Both gain'],frameon=False,fontsize=5.5,loc='lower left')
ax=fig.add_subplot(gs[1,1])
ssps=['126','245','370','585']; nm=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']; x=np.arange(4)
ax.bar(x-0.2,[P['zone_shift'][s]['land_shift_Mkm2'] for s in ssps],0.4,color='#4d4d4d',label='Zone-shift area')
ax.bar(x+0.2,[P['zone_shift'][s]['tradeoff_SOC_loss_SIC_gain_Mkm2'] for s in ssps],0.4,color='#8073ac',label='Trade-off area')
ax.set_xticks(x,nm); ax.set_ylabel('Mkm²'); ax.set_title('d  Zone shift and trade-off extent',loc='left',fontweight='bold'); ax.legend(frameon=False,fontsize=5.5)
plt.savefig(f'{F}/Fig3_zone_tradeoff.png',dpi=300,bbox_inches='tight'); plt.close(); print('Fig3')

# ---- Fig4 eq vs time-limited
fig,ax=plt.subplots(1,2,figsize=(7.2,2.8)); SC=['126_2081-2100','245_2081-2100','370_2081-2100','585_2081-2100']; nm=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']; x=np.arange(4)
for k,(key,tt) in enumerate([('dSOC','ΔSOC 0–200 cm'),('dTC','ΔTotal C 0–200 cm')]):
  E=np.array([[R5['eq'][sc]['_0_200'][key][0],R5['eq'][sc]['_0_200'][key][1],R5['eq'][sc]['_0_200'][key][2]] for sc in SC])
  Tkey='dSOC_0_200' if key=='dSOC' else 'dTC_0_200'
  T=np.array([[R5['transient'][sc][Tkey][0],R5['transient'][sc][Tkey][1],R5['transient'][sc][Tkey][2]] for sc in SC])
  ax[k].errorbar(x-0.08,E[:,0],yerr=[E[:,0]-E[:,1],E[:,2]-E[:,0]],fmt='o',ms=5,c='#b2182b',capsize=2,label='Equilibrium potential')
  ax[k].errorbar(x+0.08,T[:,0],yerr=[T[:,0]-T[:,1],T[:,2]-T[:,0]],fmt='s',ms=5,c='#2166ac',capsize=2,label='Time-limited (τ by depth)')
  ax[k].axhline(0,c='k',lw=0.4); ax[k].set_xticks(x,nm); ax[k].set_ylabel('Pg C'); ax[k].set_title(('a  ','b  ')[k]+tt,loc='left',fontweight='bold')
ax[0].legend(frameon=False,fontsize=5.5)
plt.tight_layout(); plt.savefig(f'{F}/Fig4_eq_vs_transient.png',dpi=300,bbox_inches='tight'); plt.close(); print('Fig4')

# ---- Fig5 N acidification
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9))
# map SSP keys
keys=[('ssp126_2020_2050','SSP1-2.6'),('ssp370_2020_2050','SSP3-7.0'),('ssp585_2020_2050','SSP5-8.5')]
x=np.arange(3)
loss=[P['N_acidification'][k]['Huang_formula_fert_only']['loss_only_0_30'] for k,_ in keys]
net=[P['N_acidification'][k]['Huang_formula_fert_only']['net_delta_0_30'] for k,_ in keys]
hsig=[P['N_acidification'][k]['Huang_formula_fert_only']['HuangSig_loss_only_0_30'] for k,_ in keys]
zam=[P['N_acidification'][k]['zamanian_stoichiometry']['central']['loss_0_30'] for k,_ in keys]
zamL=[P['N_acidification'][k]['zamanian_stoichiometry']['low']['loss_0_30'] for k,_ in keys]
zamH=[P['N_acidification'][k]['zamanian_stoichiometry']['high']['loss_0_30'] for k,_ in keys]
huang_pub=[10,np.nan,23]  # no ssp370 in Huang; ssp245=14
ax[0].bar(x-0.3,[-v for v in loss],0.2,color='#2166ac',label='Ours FD loss-only')
ax[0].bar(x-0.1,[-v for v in hsig],0.2,color='#92c5de',label='Huang sigmoid loss-only')
ax[0].bar(x+0.1,zam,0.2,yerr=[np.subtract(zam,zamL),np.subtract(zamH,zam)],color='#f4a582',capsize=2,label='Zamanian stoichiometry')
ax[0].bar(x+0.3,[10,14,23],0.2,color='#b2182b',label='Huang published')
# place 14 at middle even though our middle is 370
ax[0].set_xticks(x,[n for _,n in keys]); ax[0].set_ylabel('SIC change 0–30 cm (Pg C)')
ax[0].axhline(0,c='k',lw=0.4); ax[0].set_title('a  2020–2050 topsoil N pathway',loc='left',fontweight='bold')
ax[0].legend(frameon=False,fontsize=5,loc='upper right')
# note: loss_only are negative numbers in FD; I negated for display as positive loss bars... wait
# loss_only_FD is Pg of dS_neg which is negative → bar of -v makes positive height = magnitude of loss. Good.
# Huang published is positive loss magnitude. Zamanian is positive loss. Good.

# panel b: 0-200 and map
ax[1].bar(x-0.2,[-P['N_acidification'][k]['Huang_formula_fert_only']['loss_only_0_200'] for k,_ in keys],0.4,color='#2166ac',label='FD loss-only 0–200 cm')
ax[1].bar(x+0.2,[-P['N_acidification'][k]['Huang_formula_fert_only']['net_delta_0_200'] for k,_ in keys],0.4,color='#67a9cf',label='FD net Δ 0–200 cm')
ax[1].set_xticks(x,[n for _,n in keys]); ax[1].set_ylabel('Pg C'); ax[1].axhline(0,c='k',lw=0.4)
ax[1].set_title('b  Full-profile response (Huang ΔpH + our SIC)',loc='left',fontweight='bold'); ax[1].legend(frameon=False,fontsize=5.5)
plt.tight_layout(); plt.savefig(f'{F}/Fig5_N_acidification.png',dpi=300,bbox_inches='tight'); plt.close(); print('Fig5')
print('ALL FIGS DONE')
