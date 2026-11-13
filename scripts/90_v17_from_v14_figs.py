#!/usr/bin/env python3
"""Independent v17 panel design, ONLY v14-generation inputs; no v15/v16 imports.
Redraws existing v14 results; does not refit, simulate new mechanisms, or alter values.
"""
import os,json,sys,numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Rectangle
R='/workspace/soil_global'
exec(open(R+'/scripts/43_v8_style.py').read(),globals())
OUT=R+'/figs/v17_from_v14_main'; os.makedirs(OUT,exist_ok=True)
mpl.rcParams.update({'font.size':10,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,
 'legend.fontsize':9,'pdf.fonttype':42,'savefig.dpi':600,'axes.titlesize':10})
E=np.load(R+'/out/v10/ens_maps.npz'); J=json.load(open(R+'/out/v10/ensemble_v10.json'))
D=json.load(open(R+'/out/v8/drivers_v8.json')); PD=json.load(open(R+'/out/v8/pdp.json')); OB=json.load(open(R+'/out/v8/obs_curves.json'))
SS=['126','245','370','585']; LL=[f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SS]
SOC=sum(E['p_soc_'+d] for d in ['0_30','30_100','100_200']); SIC=sum(E['p_sic_'+d] for d in ['0_30','30_100','100_200'])
COL={'SOC':'#2171b5','SIC':'#7651a3','TC':'#555555','MAOC':'#2171b5','POC':'#d88424'}
PAL={(0,1):'#de9a55',(0,0):'#8b637f',(1,1):'#355b88',(1,0):'#85bdc9'}
NUM={}
def save17(fig,name):
 for ext in ['pdf','png']:fig.savefig(f'{OUT}/{name}.{ext}',dpi=600,bbox_inches='tight',pad_inches=.12)
 plt.close(fig); print('saved',name,flush=True)
def tag(ax,letter,title):
 ax.set_title(letter+'   '+title,loc='left',fontweight='bold',pad=12)
def mp(fig,rect,letter,title,v,bins,cols,cats=None):
 ax=mapax(fig,rect); ax.set_title(letter+'   '+title,loc='left',fontweight='bold',pad=9)
 norm=BoundaryNorm(bins,len(cols),clip=True)
 ax.imshow(to2d(v),extent=[-180,180,-90,90],origin='upper',transform=ccrs.PlateCarree(),
  cmap=ListedColormap(cols),norm=norm,interpolation='nearest',regrid_shape=2200,zorder=1)
 p=ax.get_position(); ca=fig.add_axes([p.x0+.07*p.width,p.y0-.029,.86*p.width,.013])
 for i,c in enumerate(cols):ca.add_patch(Rectangle((i,0),1,1,color=c))
 ca.set_xlim(0,len(cols));ca.set_ylim(0,1);ca.set_yticks([])
 if cats:ca.set_xticks(np.arange(len(cols))+.5);ca.set_xticklabels(cats,fontsize=9)
 else:ca.set_xticks(np.arange(1,len(cols)));ca.set_xticklabels([f'{x:g}' for x in bins[1:-1]],fontsize=9)
 ca.tick_params(length=0,pad=2)
 for sp in ca.spines.values():sp.set_visible(False)
 return ax
def future_bars(ax,key,pool,letter,depth='0–200 cm'):
 x=np.arange(4)
 for k,kind in enumerate(['eq','tl']):
  ds=[J['future'][s][kind][key] for s in SS]; m=np.array([d['mean'] for d in ds]); err=np.array([[d['mean']-d['p05'],d['p95']-d['mean']] for d in ds]).T
  ax.bar(x+(k-.5)*.34,m,.32,color=COL[pool],alpha=1 if k==0 else .4,
   yerr=err,error_kw=dict(lw=.8,capsize=2),label='Equilibrium' if k==0 else 'By 2100 (assumed τ)')
 ax.axhline(0,c='.4',lw=.6);ax.set_xticks(x);ax.set_xticklabels(LL,rotation=20,ha='right',fontsize=9)
 ax.set_ylabel(f'Δ{pool} ({depth}; Pg C)');tag(ax,letter,pool+' stock change')
def fig1():
 fig=plt.figure(figsize=(8.5,6.63))
 ax=fig.add_axes([.08,.59,.36,.29]);tag(ax,'A','Depth partition of the stock')
 ds=['_0_30','_30_100','_100_200'];xx=np.arange(3)
 for k,pool in enumerate(['SOC','SIC']):
  dat=[J['present'][d][pool] for d in ds];m=[d['mean'] for d in dat];er=np.array([[d['mean']-d['p05'],d['p95']-d['mean']] for d in dat]).T
  ax.bar(xx+(k-.5)*.34,m,.32,color=COL[pool],yerr=er,error_kw=dict(lw=.7,capsize=2),label=pool)
 ax.set_xticks(xx);ax.set_xticklabels(['0–30','30–100','100–200']);ax.set_xlabel('Depth (cm)');ax.set_ylabel('Global stock (Pg C)');ax.set_ylim(0,1200);ax.legend(loc='upper left',ncol=2)
 fig.text(.08,.945,'TC 0–200 cm: 4105 Pg C (90% CI 3675–4549)',fontsize=11,fontweight='bold')
 share=np.where(SOC+SIC>0,100*SIC/(SOC+SIC),np.nan)
 mp(fig,[.52,.57,.45,.32],'B','SIC share of TC, 0–200 cm (%)',share,[0,5,10,20,30,40,60,100],['#173d73','#4b76b5','#92b6dc','#cbd9e9','#f9dd99','#f6a259','#c54333'])
 mp(fig,[.035,.10,.45,.32],'C','SOC, 0–200 cm (Mg C ha$^{-1}$)',SOC,[0,50,100,150,200,300,500,1e4],BLUES)
 mp(fig,[.52,.10,.45,.32],'D','SIC, 0–200 cm (Mg C ha$^{-1}$)',SIC,[0,5,20,50,100,200,400,1e4],PURP)
 fig.text(.52,.015,'Grey = not mapped.',fontsize=8.5,color='.4')
 save17(fig,'Fig1_inventory')
def fig2():
 fig=plt.figure(figsize=(8.5,6.375));ax=fig.add_axes([.13,.60,.32,.28]);tag(ax,'A','Model attribution (not causation)')
 groups=D['groups'];comps=list(D['shap']);gc=['#bc333a','#935511','#88b849','#8564a2','#bdbdbd'];left=np.zeros(len(comps))
 for g,c in zip(groups,gc):
  vals=np.array([D['shap'][p]['group_pct'][g] for p in comps]);ax.barh(range(len(comps)),vals,left=left,color=c,label=g);left+=vals
 ax.set_yticks(range(len(comps)));ax.set_yticklabels(comps);ax.set_xlim(0,100);ax.set_xlabel('Share of mean |SHAP| (%)')
 ax.legend(ncol=3,loc='lower left',bbox_to_anchor=(-.15,1.16),fontsize=9,frameon=False)
 bx=fig.add_axes([.56,.58,.42,.30]);bx.axis('off');tag(bx,'B','Selected association subgraph')
 s=D['sem'];pos={'logAI':(.10,.83),'bio1':(.10,.57),'clay':(.10,.31),'carbonate_rock':(.10,.06),'pH':(.51,.48),'lSIC':(.90,.48)}
 lab={'logAI':'Humidity\nln(1+P/PET)','bio1':'MAT','clay':'Clay','carbonate_rock':'Carb. rock','pH':f"pH\nR²={s['pH']['R2']:.2f}",'lSIC':f"SIC\nR²={s['SIC']['R2']:.2f}",'lSOC':f"SOC\nR²={s['SOC']['R2']:.2f}"}
 # Main shows the selected pH-linked subgraph; full SOC-inclusive structure is retained in SI.
 offsets={('logAI','pH'):(-.03,.06),('bio1','pH'):(-.03,.05),('clay','pH'):(-.03,-.02),('carbonate_rock','pH'):(-.03,-.04),('logAI','lSOC'):(.11,.12),('bio1','lSOC'):(.13,.00),('clay','lSOC'):(.10,-.10),('pH','lSIC'):(.01,.055),('pH','lSOC'):(.01,-.04)}
 for target,key in [('pH','pH'),('lSIC','SIC')]:
  for src,val in s[key].items():
   if src=='R2' or abs(val)<.05:continue
   x,y=pos[src];u,v=pos[target];c='#bd3b42' if val<0 else '#2171b5'
   bx.annotate('',(u-.065,v),(x+.07,y),arrowprops=dict(arrowstyle='->',lw=.5+abs(val)*3,color=c),zorder=1)
   dx,dy=offsets.get((src,target),(0,.05));bx.text((x+u)/2+dx,(y+v)/2+dy,f'{val:.2f}',fontsize=9,color=c,ha='center',zorder=3,bbox=dict(fc='white',ec='none',pad=.6))
 for key,(x,y) in pos.items():bx.text(x,y,lab[key],ha='center',va='center',fontsize=9,zorder=12,bbox=dict(boxstyle='round,pad=.3',fc='#f8f8f8',ec='.5',lw=.5))
 bx.text(.5,-.17,'n = 58,404; indirect coefficient = −0.38\nSelected pH–SIC paths; full model in SI. Not causal links.',ha='center',fontsize=9,transform=bx.transAxes)
 # Observed logistic relation (same fitted coefficients as v14)
 cx=fig.add_axes([.10,.12,.35,.27]);tag(cx,'C','Observed carbonate occurrence')
 # Stored observation summaries are shown, not refitted.
 cx.scatter(OB['pH_bins'],OB['P_SIC'],s=12,color=COL['SIC'],alpha=.65,zorder=3)
 z=np.linspace(3,10,300);cx.plot(z,1/(1+np.exp(-OB['logistic_k']*(z-OB['logistic_pH50']))),color='black',lw=1.4)
 cx.axvline(7.10,color='.55',ls='--',lw=.7);cx.text(7.22,.14,'pH₅₀ = 7.10\nn = 91,273',fontsize=9)
 cx.set_xlabel('Observed topsoil pH');cx.set_ylabel('P(SIC > 0.1 g kg$^{-1}$)');cx.set_ylim(0,1.03)
 dx=fig.add_axes([.60,.12,.35,.27]);tag(dx,'D','Model partial dependence')
 p=PD['SIC_presence_vs_pH'];dx.axvline(p['breakpoint'],ls='--',c='.6',lw=.7,zorder=1);dx.plot(p['x'],p['y'],c=COL['SIC'],lw=1.5,zorder=3)
 dx.text(.03,.91,f"Breakpoint = {p['breakpoint']:.2f}",transform=dx.transAxes,fontsize=9);dx.set_xlabel('Predicted pH');dx.set_ylabel('P(SIC > 0.1 g kg$^{-1}$)')
 save17(fig,'Fig2_associations')
def fig3():
 fig=plt.figure(figsize=(8.5,6.29));a=E['dsoc_0_200_585'];b=E['dsic_0_200_585'];bins=[-1e4,-50,-20,-5,5,20,50,1e4]
 mp(fig,[.03,.58,.45,.32],'A','Equilibrium ΔSOC (Mg C ha$^{-1}$)',a,bins,DIV)
 mp(fig,[.52,.58,.45,.32],'B','Equilibrium ΔSIC (Mg C ha$^{-1}$)',b,bins,DIV)
 ax=mapax(fig,[.03,.10,.53,.36]);tag(ax,'C','Joint signs, SSP5-8.5 (0–200 cm)')
 q=((a>0).astype(int)*2+(b>0).astype(int));ok=np.isfinite(a)&np.isfinite(b);rgba=np.zeros((H,W,4))
 for k,c in PAL.items():
  tmp=np.zeros((H,W,4));m=ok&(q==k[0]*2+k[1]);rr=np.zeros((len(a),4));rr[m]=mpl.colors.to_rgba(c);tmp[mask]=rr;rgba+=tmp
 ax.imshow(rgba,origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),interpolation='nearest',regrid_shape=2200,zorder=1)
 dx=fig.add_axes([.70,.12,.26,.30]);tag(dx,'D','Share of mapped land')
 order=[(0,1),(0,0),(1,1),(1,0)];val=[area[ok&(q==i*2+j)].sum()/area[ok].sum()*100 for i,j in order]
 dx.barh(np.arange(4),val,color=[PAL[k] for k in order]);dx.set_yticks(range(4));dx.set_yticklabels(['SOC− / SIC+\nTrade-off','SOC− / SIC−\nCo-loss','SOC+ / SIC+','SOC+ / SIC−'],fontsize=9);dx.invert_yaxis();dx.set_xlim(0,60);dx.set_xlabel('Mapped land (%)')
 for i,v in enumerate(val):dx.text(v+1,i,f'{v:.0f}%',va='center',fontsize=9)
 fig.text(.62,.015,'Denominator: 137.3 Mkm²; ensemble-mean signs.',fontsize=9)
 NUM['quadrants_pct']=val
 save17(fig,'Fig3_equilibrium_geography')
def fig4():
 fig,axs=plt.subplots(1,3,figsize=(8.5,3.57));fig.subplots_adjust(left=.08,right=.98,bottom=.23,top=.79,wspace=.55)
 for ax,p,let in zip(axs,['SOC','SIC','TC'],'ABC'):future_bars(ax,'d'+p+'_0_200',p,let)
 fig.suptitle('Equilibrium target versus by-2100 stock change',fontsize=12,fontweight='bold',y=1.07)
 fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.53,.98),ncol=2,frameon=False,fontsize=9)
 fig.text(.08,.025,'By-2100 values are conditional on first-order kinetics and assumed τ, not observed trajectories.',fontsize=8.5,color='.3')
 save17(fig,'Fig4_kinetic_stock_change')
def fig5():
 fig=plt.figure(figsize=(8.5,6.375));ax=fig.add_axes([.08,.60,.36,.27]);tag(ax,'A','Cropland pH change, 2020–2050')
 from scipy.stats import gaussian_kde
 for s,c,l in zip(SS,['#224c8e','#69a7ce','#ef9a48','#bb323a'],LL):
  z=np.load(f'{R}/out/v10/Nin_{s}_2020_2050.npz');v=np.where(z['fr']>.01,-.06*z['Nin']+.11,0);v=v[(v!=0)&np.isfinite(v)];v=np.random.default_rng(0).choice(v,min(40000,len(v)),replace=False);xs=np.linspace(np.percentile(v,.5),np.percentile(v,99.5),300);ax.plot(xs,gaussian_kde(v)(xs),c=c,label=l)
 ax.set_xlabel('ΔpH');ax.set_ylabel('Probability density');ax.legend(fontsize=9,loc='upper left')
 bx=fig.add_axes([.61,.60,.35,.27]);tag(bx,'B','Separate nitrogen experiment');x=np.arange(4)
 for k,key in enumerate(['loss_0_30','loss_0_200']):
  ds=[J['N'][s][key] for s in SS];m=[-d['mean'] for d in ds];err=np.array([[-d['mean']+d['p95'],-d['p05']+d['mean']] for d in ds]).T
  bx.bar(x+(k-.5)*.34,m,.32,yerr=err,color='#97472c' if k==0 else '#e0b393',error_kw=dict(lw=.8,capsize=2),label='0–30 cm' if k==0 else '0–200 cm*')
 bx.set_xticks(x);bx.set_xticklabels([l.replace('SSP','')+('†' if s=='245' else '') for s,l in zip(SS,LL)],fontsize=9);bx.set_ylabel('SIC loss-only (Pg C)');bx.legend(fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2,frameon=False)
 bins=[-1e4,-10,-5,-2,-1,-.5,-.01,.01];cols=['#7f0000','#c93226','#ef8058','#f5b394','#f8d7b0','#fff3de','#f6f6f6']
 mp(fig,[.03,.13,.45,.32],'C','ΔSIC$_N$, SSP1-2.6 (Mg C ha$^{-1}$)',E['N_loss_0_30_126'],bins,cols)
 mp(fig,[.52,.13,.45,.32],'D','ΔSIC$_N$, SSP5-8.5 (Mg C ha$^{-1}$)',E['N_loss_0_30_585'],bins,cols)
 fig.text(.07,.025,'*Topsoil ΔpH applied at all depths.  †Interpolated fertilizer inputs.  Not combined with climate projections.',fontsize=8.5,color='.3')
 save17(fig,'Fig5_nitrogen')
def fig6():
 fig=plt.figure(figsize=(8.5,6.205));ma=E['p_MA'];po=E['p_PO'];f=np.where(ma+po>0,ma/(ma+po)*100,np.nan)
 mp(fig,[.03,.59,.45,.32],'A','MAOC fraction, 0–30 cm (%)',f,[0,50,60,70,80,85,90,100],['#fdd0a2','#fdae6b','#fd8d3c','#c6dbef','#6baed6','#2171b5','#08306b'])
 mp(fig,[.52,.59,.45,.32],'B','MAOC stock, 0–30 cm (Mg C ha$^{-1}$)',ma,[0,10,20,30,40,60,90,1e4],BLUES)
 ax=fig.add_axes([.10,.14,.35,.28]);bx=fig.add_axes([.61,.14,.35,.28]);future_bars(ax,'dMAOC','MAOC','C','0–30 cm');future_bars(bx,'dPOC','POC','D','0–30 cm')
 fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.52,1.015),ncol=2,frameon=False,fontsize=9)
 fig.text(.08,.015,'Mineral soils only. Baseline: MAOC 518 Pg C; POC 183 Pg C. Realized loss ≠ depletion of the entire pool.',fontsize=8.5,color='.3')
 save17(fig,'Fig6_organic_fractions')
if __name__=='__main__':
 for n in (sys.argv[1:] or ['1','2','3','4','5','6']):globals()['fig'+n]()
 os.makedirs(R+'/out/v17_from_v14',exist_ok=True);json.dump(NUM,open(R+'/out/v17_from_v14/figure_check.json','w'),indent=2)
