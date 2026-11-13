import sys,json,glob,os,numpy as np,pandas as pd
exec(open('/workspace/soil_global/scripts/43_v8_style.py').read())
R='/workspace/soil_global'; O7=R+'/out/v7'; O8=R+'/out/v8'; FS=R+'/figs/v8_SI/'
L=lambda s: np.load(glob.glob(f'{O7}/maps10_{s}.npz')[0]); z1,z2=L('30_100'),L('100_200')
fr=np.load(O8+'/frac_maps10.npz'); FJ=json.load(open(O8+'/fractions_v8.json'))
J=lambda f: json.load(open(O8+f)) if os.path.exists(O8+f) else None
DJ=J('/drivers_v8.json'); PD=J('/pdp.json'); OB=J('/obs_curves.json'); NM=J('/shap_names.json')
GC={'Climate':'#c0262c','Soil':'#8c510a','Topography':'#7fbc41','Parent material':'#6a51a3','Sampling':'#bdbdbd'}
def F(fn):
  try: fn(); print('ok',fn.__name__,flush=True)
  except Exception as e: import traceback; traceback.print_exc(); print('FAIL',fn.__name__,flush=True)
def S1():  # random CV summary
  hp=json.load(open(O7+'/hp_cv.json'))['results']; fig,ax=plt.subplots(1,2,figsize=(7.2,2.6)); deps=['_0_30','_30_100','_100_200']; cols=['#2171b5','#6a51a3','#e08214']
  keys=[('pH','r2','pH'),('SIC_clf','AUC','SIC AUC'),('SIC_amt','r2','SIC R²'),('SOC_mineral','r2','SOC R²'),('BD','r2','BD R²')]
  for k,d in enumerate(deps):
    v=[]
    for a,b,_ in keys:
      r=hp[d].get(a) or hp[d].get(a.replace('_amt','').replace('_clf',''),{}); v.append(r.get(b,r.get('r2_amt',r.get('AUC',np.nan))) if isinstance(r,dict) else np.nan)
    ax[0].bar(np.arange(len(keys))+k*0.27-0.27,v,0.27,color=cols[k],label=d[1:].replace('_','–')+' cm')
  ax[0].set_xticks(range(len(keys))); ax[0].set_xticklabels([k[2] for k in keys]); ax[0].set_ylabel('Random 10-fold CV score'); ax[0].legend(fontsize=6); ax[0].set_ylim(0,1)
  c=FJ['cv']; p=pd.read_csv(O8+'/fM_cv_points.csv'); ax[1].hexbin(p.obs,p.cv,gridsize=35,cmap='Blues',mincnt=1,lw=0); ax[1].plot([0,1],[0,1],'k--',lw=0.6)
  ax[1].text(0.03,0.95,f"f$_{{MAOC}}$ n={c['n']}\nR²={c['R2_fMAOC']:.2f} (5×10: {c['R2_5x10_mean']:.2f}±{c['R2_5x10_sd']:.2f})\nRMSE={c['RMSE_fMAOC']:.3f}",transform=ax[1].transAxes,va='top',fontsize=6)
  ax[1].set_xlabel('Observed f$_{MAOC}$'); ax[1].set_ylabel('CV predicted')
  for a,l in zip(ax,'ab'): a.text(-0.12,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  save(fig,FS+'FigS1_random_CV')
def S2():  # fraction data
  p=pd.read_csv(O8+'/fM_cv_points.csv'); fig=plt.figure(figsize=(7.2,3.2)); ax=mapax(fig,[0,0.05,0.6,0.9])
  for m,c in [('Particle_Size','#2171b5'),('Density','#e08214'),('Density_Particle_Size','#6a51a3')]:
    q=p[p.method==m]; ax.scatter(q.lon,q.lat,s=3,c=c,transform=ccrs.PlateCarree(),label=f'{m} (n={len(q)})',zorder=3,lw=0)
  ax.legend(loc='lower left',fontsize=5.5,markerscale=2); fig.text(0.01,0.95,'a',fontsize=9,fontweight='bold')
  b=fig.add_axes([0.68,0.15,0.3,0.75]); b.boxplot([p.obs[p.method==m] for m in ['Particle_Size','Density']],tick_labels=['Size','Density'],widths=0.5,flierprops=dict(ms=1)); b.set_ylabel('Observed f$_{MAOC}$')
  fig.text(0.63,0.95,'b',fontsize=9,fontweight='bold'); save(fig,FS+'FigS2_fraction_data')
def S3():  # top features lollipop
  S=DJ['shap']; fig,axs=plt.subplots(1,5,figsize=(7.2,2.6))
  for a,(k,v),l in zip(axs,S.items(),'abcde'):
    t=v['top_features'][::-1]; nm=[x[0] for x in t]; val=[x[1] for x in t]
    a.hlines(range(len(t)),0,val,color='0.5',lw=0.6); a.scatter(val,range(len(t)),s=14,color='#2171b5',zorder=3); a.set_yticks(range(len(t))); a.set_yticklabels(nm,fontsize=5.5); a.set_title(k,fontsize=7); a.set_xlabel('|SHAP| (%)')
    a.text(-0.4,1.05,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  fig.tight_layout(); save(fig,FS+'FigS3_SHAP_top_features')
def S4():  # dependence
  fig,axs=plt.subplots(2,4,figsize=(7.2,3.8)); axs=axs.ravel()
  spec=[('SIC_presence','logAI',NM['fnS']),('SIC_presence','pH_pred',NM['fnS']),('SIC_amount','pH_pred',NM['fnS']),('pH','logAI',NM['fn_main']),('SOC_mineral','bio1',NM['fn_main']),('SOC_mineral','logAI',NM['fn_main']),('fMAOC','clay',NM['fnM']),('fMAOC','bio1',NM['fnM'])]
  for a,(k,f,fn),l in zip(axs,spec,'abcdefgh'):
    A=np.load(f'{O8}/shap_{k}_sample.npy'); n=len(fn); j=fn.index(f); x=A[:,j]; s=A[:,n+j]; i=np.random.default_rng(0).choice(len(x),8000,replace=False)
    a.scatter(x[i],s[i],s=1,c='#2171b5',alpha=0.3,lw=0); a.axhline(0,c='k',lw=0.4); a.set_xlabel(f); a.set_ylabel(f'SHAP ({k})',fontsize=6); a.text(-0.25,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  fig.tight_layout(); save(fig,FS+'FigS4_SHAP_dependence')
def S5():  # PDP thresholds
  ks=list(PD); fig,axs=plt.subplots(3,4,figsize=(7.2,5)); 
  for a,k,l in zip(axs.ravel(),ks,'abcdefghijkl'):
    p=PD[k]; a.plot(p['x'],p['y'],c='#c0262c',lw=1.1); a.axvline(p['breakpoint'],ls='--',c='0.4',lw=0.6); a.set_title(k.replace('_',' '),fontsize=6); a.text(0.97,0.05,f"bp={p['breakpoint']:.3g}",transform=a.transAxes,ha='right',fontsize=5.5)
    a.text(-0.25,1.05,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  fig.tight_layout(); save(fig,FS+'FigS5_PDP_thresholds')
def S6():  # pH–SIC curve
  fig,ax=plt.subplots(1,2,figsize=(7.2,2.6)); x=np.array(OB['pH_bins']); y=np.array([np.nan if v is None else v for v in OB['P_SIC']])
  ax[0].plot(x,y,'o',ms=3,c='#6a51a3',label='Observed (binned)'); xx=np.linspace(4,10,200); ax[0].plot(xx,1/(1+np.exp(-OB['logistic_k']*(xx-OB['logistic_pH50']))),c='k',lw=0.8,label=f"Logistic, pH$_{{50}}$={OB['logistic_pH50']:.2f}")
  p=PD['SIC_presence_vs_pH']; ax[0].plot(p['x'],p['y'],c='#c0262c',lw=1,label='Model PDP'); ax[0].set_xlabel('pH (H$_2$O)'); ax[0].set_ylabel('P(SIC>0.1 g kg$^{-1}$)'); ax[0].legend(fontsize=5.5)
  am=np.array([np.nan if v is None else v for v in OB['SIC_median']]); ax[1].semilogy(x,am,'o-',ms=3,c='#6a51a3'); ax[1].set_xlabel('pH (H$_2$O)'); ax[1].set_ylabel('Median SIC where present (g kg$^{-1}$)')
  for a,l in zip(ax,'ab'): a.text(-0.12,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  save(fig,FS+'FigS6_pH_SIC_curve')
def S7():  # tau sensitivity
  sc=FJ['future_0_30']['scen']; fig,ax=plt.subplots(1,2,figsize=(7.2,2.6)); SSP=['126','245','370','585']; x=np.arange(4)
  for a,key,col in [(ax[0],'dMAOC','#2171b5'),(ax[1],'dPOC','#e08214')]:
    a.bar(x-0.3,[sc[s][key+'_eq'] for s in SSP],0.2,color=col,label='Equilibrium')
    for k,(lab,al) in enumerate([('fast',0.8),('central',0.55),('slow',0.3)]): a.bar(x-0.1+k*0.2,[sc[s]['tl_'+lab][key] for s in SSP],0.2,color=col,alpha=al,label=f"by 2100, τ={sc['585']['tl_'+lab]['tau_POC' if key=='dPOC' else 'tau_MAOC']} yr")
    a.set_xticks(x); a.set_xticklabels([f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP],fontsize=6); a.set_ylabel(key[1:]+' change 0–30 cm (Pg C)'); a.legend(fontsize=5); a.axhline(0,c='k',lw=0.4)
  for a,l in zip(ax,'ab'): a.text(-0.12,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  save(fig,FS+'FigS7_tau_sensitivity')
def S8():  # path diagram
  s=DJ['sem']; fig,ax=plt.subplots(figsize=(5,3.2)); ax.axis('off')
  P={'logAI':(0.1,0.85),'bio1':(0.1,0.6),'clay':(0.1,0.35),'carbonate_rock':(0.1,0.1),'pH':(0.5,0.5),'lSIC':(0.9,0.75),'lSOC':(0.9,0.25)}
  lab={'logAI':'Aridity\n(log P/PET)','bio1':'MAT','clay':'Clay','carbonate_rock':'Carbonate rock','pH':'pH','lSIC':f"SIC\nR²={s['SIC']['R2']:.2f}",'lSOC':f"SOC\nR²={s['SOC']['R2']:.2f}"}
  for k,(x,y) in P.items(): ax.text(x,y,lab[k] if k!='pH' else f"pH\nR²={s['pH']['R2']:.2f}",ha='center',va='center',bbox=dict(boxstyle='round',fc='#f0f0f0',ec='0.3',lw=0.5),fontsize=6.5)
  for tgt,key in [('pH','pH'),('lSIC','SIC'),('lSOC','SOC')]:
    for src,b in s[key].items():
      if src=='R2' or abs(b)<0.05: continue
      (x0,y0),(x1,y1)=P[src],P[tgt]; ax.annotate('',xy=(x1-0.06,y1),xytext=(x0+0.07,y0),arrowprops=dict(arrowstyle='->',color='#c0262c' if b<0 else '#2171b5',lw=0.4+abs(b)*4))
      ax.text((x0+x1)/2,(y0+y1)/2,f'{b:.2f}',fontsize=5.5,color='#c0262c' if b<0 else '#2171b5')
  ax.text(0.5,0.98,f"Standardized path coefficients (n={s['n']}); indirect aridity→pH→SIC = {s['indirect_AI_pH_SIC']:.2f}",ha='center',fontsize=6)
  save(fig,FS+'FigS8_path_analysis')
def S9():  # deep layer maps
  fig=plt.figure(figsize=(7.2,4.4))
  for k,(v,bins,cols,lab,rect) in enumerate([(z1['soc'],[0,20,40,60,80,120,200,1e4],BLUES,'SOC$_{30–100}$',[0,0.52,0.5,0.45]),(z1['sic'],[0,1,5,20,50,100,200,1e4],PURP,'SIC$_{30–100}$',[0.5,0.52,0.5,0.45]),
     (z2['soc'],[0,20,40,60,80,120,200,1e4],BLUES,'SOC$_{100–200}$',[0,0.04,0.5,0.45]),(z2['sic'],[0,1,5,20,50,100,200,1e4],PURP,'SIC$_{100–200}$',[0.5,0.04,0.5,0.45])]):
    ax=mapax(fig,rect); classed(ax,v,bins,cols,'class',lab,fig); letter(fig,ax,'abcd'[k],0.02,-0.03)
  save(fig,FS+'FigS9_deep_layers')
def S10():  # fMAOC uncertainty + subsoil MAOC/POC
  fig=plt.figure(figsize=(7.2,2.6))
  ax=mapax(fig,[0,0.1,0.33,0.85]); classed(ax,fr['fsd_0_30']*100,[0,2,4,6,8,10,15,100],PURP,'class','SD f$_{MAOC}$ (%)',fig); letter(fig,ax,'a',0.02)
  ax=mapax(fig,[0.335,0.1,0.33,0.85]); classed(ax,fr['MA_30_100'],[0,10,20,30,40,60,90,1e4],BLUES,'continent','MAOC$_{30–100}$',fig); letter(fig,ax,'b',0.02)
  ax=mapax(fig,[0.67,0.1,0.33,0.85]); classed(ax,fr['PO_30_100'],[0,2,5,10,15,20,40,1e4],['#fff5eb','#fee6ce','#fdd0a2','#fdae6b','#fd8d3c','#e6550d','#a63603'],'continent','POC$_{30–100}$',fig); letter(fig,ax,'c',0.02)
  save(fig,FS+'FigS10_MAOC_uncertainty_subsoil')
def S11():  # dominant driver other components
  dd=np.load(O8+'/dominant_driver.npz'); g=DJ['groups']; cols=[GC[x] for x in g[:4]]; fig=plt.figure(figsize=(7.2,2.6))
  for k,key in enumerate(['pH','SIC amount']):
    ax=mapax(fig,[k*0.5,0.12,0.5,0.85]); classed(ax,dd[key].astype(float)+0.5,[0,1,2,3,4],cols,'class',key,fig,cats=['Climate','Soil','Topo.','Parent']); letter(fig,ax,'ab'[k],0.02)
  fig.text(0.3,0.02,'Classes 1–4 = '+', '.join(g[:4]),fontsize=6); save(fig,FS+'FigS11_dominant_driver_pH_SIC')
def S12():  # 30″ zoom
  import rasterio; from rasterio.windows import from_bounds
  fig,axs=plt.subplots(2,2,figsize=(7.2,4.6))
  for r,(fn,lab,cm) in enumerate([(O8+'/maps30s/maocstock_0_30.tif','MAOC 0–30 (Mg C ha$^{-1}$)','Blues'),(O7+'/maps30s/sicstock_0_30.tif','SIC 0–30 (Mg C ha$^{-1}$)','Purples')]):
    with rasterio.open(fn) as s:
      for c,(bb,nm) in enumerate([((100,30,120,42),'North China Plain / Loess Plateau'),((-5,40,15,52),'Western Europe')]):
        a=s.read(1,window=from_bounds(*bb,s.transform)); im=axs[r,c].imshow(a,extent=[bb[0],bb[2],bb[1],bb[3]],cmap=cm,vmin=0,vmax=np.nanpercentile(a,98)); axs[r,c].set_facecolor(GREY)
        axs[r,c].set_title(nm,fontsize=6.5); plt.colorbar(im,ax=axs[r,c],shrink=0.8,label=lab,orientation='horizontal',pad=0.12)
  for a,l in zip(axs.ravel(),'abcd'): a.text(-0.08,1.04,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  fig.tight_layout(); save(fig,FS+'FigS12_30arcsec_zoom')
def S13():
  R5=json.load(open(R+'/out/v5/results_v5.json')); SSP=['126','245','370','585']; fig,ax=plt.subplots(figsize=(7.2,2.8)); x=np.arange(4)
  items=[('eq','dSOC','Eq. ΔSOC','#2171b5'),('eq','dSIC','Eq. ΔSIC','#6a51a3'),('eq','dTC','Eq. ΔTC','#7f7f7f'),('transient','dSOC_0_200','TL ΔSOC','#9ecae1'),('transient','dSIC_0_200','TL ΔSIC','#bcbddc'),('transient','dTC_0_200','TL ΔTC','#d9d9d9')]
  for k,(a,key,lab,col) in enumerate(items):
    v=[];e=[]
    for s_ in SSP:
      r=R5[a][s_+'_2081-2100']; r=r['_0_200'] if a=='eq' else r; m,lo,hi=r[key]; v.append(m); e.append([m-lo,hi-m])
    ax.bar(x-0.375+k*0.15,v,0.15,color=col,label=lab,yerr=np.array(e).T,error_kw=dict(lw=0.5,capsize=1))
  ax.axhline(0,c='k',lw=0.4); ax.set_xticks(x); ax.set_xticklabels([f'SSP{s_[0]}-{s_[1]}.{s_[2]}' for s_ in SSP]); ax.set_ylabel('Change 0–200 cm, 2081–2100 (Pg C)'); ax.legend(ncol=6,fontsize=5.5,loc='upper center',bbox_to_anchor=(0.5,1.12))
  save(fig,FS+'FigS13_equilibrium_vs_time_limited')
for f in [globals()[n] for n in (sys.argv[1:] or ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11','S12','S13'])]: F(f)
