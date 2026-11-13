SSP4=['126','245','370','585']; LBL={s:f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP4}
SC4={'126':'#1d3c8f','245':'#69b3e0','370':'#f39c4a','585':'#c0262c'}
def fig4():
  fig=plt.figure(figsize=(7.2,5.6))
  a=fig.add_axes([0.07,0.70,0.4,0.25]); dens(a,[N[f'dph_{s}'][N[f'dph_{s}']!=0] for s in SSP4],[LBL[s] for s in SSP4],[SC4[s] for s in SSP4],'ΔpH on cropland, 2020–2050'); letter(fig,a,'a',-0.05)
  bins=[-1e4,-10,-5,-2,-1,-0.5,-0.01,0.01]; cols=['#7f0000','#d7301f','#fc8d59','#fdbb84','#fdd49e','#fff7ec','#f7f7f7']
  ax=mapax(fig,[0.0,0.32,0.5,0.32]); classed(ax,N['dSIC_loss_126'],bins,cols,'continent','ΔSIC$_{0–30}$ SSP1-2.6',fig); letter(fig,ax,'c',0.02)
  ax=mapax(fig,[0.5,0.32,0.5,0.32]); classed(ax,N['dSIC_loss_585'],bins,cols,'continent','ΔSIC$_{0–30}$ SSP5-8.5',fig); letter(fig,ax,'d',0.02)
  s_,nm,ct=by_country(N['dSIC_loss0200_585']); df=pd.DataFrame(dict(n=nm,c=ct,l=-s_))[1:]; t=df.sort_values('l',ascending=False).head(12)[::-1]
  b=fig.add_axes([0.62,0.70,0.33,0.26]); b.hlines(range(len(t)),0,t.l*1000,color='0.4',lw=0.6); b.scatter(t.l*1000,range(len(t)),c=[CCOL.get(c,'0.5') for c in t.c],s=20,edgecolor='k',lw=0.3,zorder=3)
  b.set_yticks(range(len(t))); b.set_yticklabels(t.n,fontsize=5.5); b.set_xlabel('SIC loss 0–200 cm, 2020–2050, SSP5-8.5 (Tg C)'); letter(fig,b,'b',-0.12)
  c=fig.add_axes([0.1,0.05,0.85,0.18]); x=np.arange(4); NN=EJ['N']
  for k,(key,lab,al) in enumerate([('loss_0_30','0–30 cm',1.0),('loss_0_200','0–200 cm',0.45)]):
    v=[-NN[s][key]['mean'] for s in SSP4]; e=np.array([[NN[s][key]['mean']-NN[s][key]['p05'] if False else -NN[s][key]['mean']+NN[s][key]['p95'], -NN[s][key]['p05']+NN[s][key]['mean']] for s in SSP4]).T
    c.bar(x+(k-0.5)*0.36,v,0.36,color=[SC4[s] for s in SSP4],alpha=al,yerr=np.abs(e),error_kw=dict(lw=0.5,capsize=1.5),label=lab)
    for i,vv in enumerate(v): c.text(x[i]+(k-0.5)*0.36,vv,f'{vv:.1f}',ha='center',va='bottom',fontsize=5.5,fontweight='bold')
  c.set_xticks(x); c.set_xticklabels([LBL[s]+(' (interp.)' if s=='245' else '') for s in SSP4]); c.set_ylabel('SIC loss 2020–2050 (Pg C)'); c.legend(fontsize=6)
  letter(fig,c,'e',-0.06); save(fig,FM+'Fig4_N_acidification')
def S7():
  fig,ax=plt.subplots(1,2,figsize=(7.2,2.6)); x=np.arange(4)
  for a,key,col in [(ax[0],'dMAOC','#2171b5'),(ax[1],'dPOC','#e08214')]:
    for k,(kind,al,lab) in enumerate([('eq',1.0,'Equilibrium'),('tl',0.45,'By 2100 (τ log-uniform)')]):
      d=[EJ['future'][s][kind][key] for s in SSP4]; v=[q['mean'] for q in d]; e=np.array([[q['mean']-q['p05'],q['p95']-q['mean']] for q in d]).T
      a.bar(x+(k-0.5)*0.36,v,0.36,color=col,alpha=al,yerr=e,error_kw=dict(lw=0.5,capsize=1.5),label=lab)
    a.set_xticks(x); a.set_xticklabels([LBL[s] for s in SSP4],fontsize=6); a.set_ylabel(key[1:]+' change 0–30 cm (Pg C)'); a.legend(fontsize=5.5); a.axhline(0,c='k',lw=0.4)
  for a,l in zip(ax,'ab'): a.text(-0.12,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  save(fig,FS+'FigS7_tau_sensitivity')
def S13():
  fig,ax=plt.subplots(figsize=(7.2,2.8)); x=np.arange(4)
  items=[('eq','dSOC_0_200','Eq. ΔSOC','#2171b5'),('eq','dSIC_0_200','Eq. ΔSIC','#6a51a3'),('eq','dTC_0_200','Eq. ΔTC','#7f7f7f'),('tl','dSOC_0_200','TL ΔSOC','#9ecae1'),('tl','dSIC_0_200','TL ΔSIC','#bcbddc'),('tl','dTC_0_200','TL ΔTC','#d9d9d9')]
  for k,(kind,key,lab,col) in enumerate(items):
    d=[EJ['future'][s][kind][key] for s in SSP4]; v=[q['mean'] for q in d]; e=np.array([[q['mean']-q['p05'],q['p95']-q['mean']] for q in d]).T
    ax.bar(x-0.375+k*0.15,v,0.15,color=col,label=lab,yerr=e,error_kw=dict(lw=0.5,capsize=1))
  ax.axhline(0,c='k',lw=0.4); ax.set_xticks(x); ax.set_xticklabels([LBL[s] for s in SSP4]); ax.set_ylabel('Change 0–200 cm, 2081–2100 (Pg C)'); ax.legend(ncol=6,fontsize=5.5,loc='upper center',bbox_to_anchor=(0.5,1.12))
  save(fig,FS+'FigS13_equilibrium_vs_time_limited')
def S14():  # present uncertainty
  P=EJ['present']; fig,ax=plt.subplots(1,2,figsize=(7.2,2.6)); L3=['_0_30','_30_100','_100_200']; x=np.arange(3)
  for k,(v,col) in enumerate([('SOC','#2171b5'),('SIC','#6a51a3')]):
    d=[P[l][v] for l in L3]; ax[0].bar(x+(k-0.5)*0.36,[q['mean'] for q in d],0.36,color=col,label=v,yerr=np.array([[q['mean']-q['p05'],q['p95']-q['mean']] for q in d]).T,error_kw=dict(lw=0.6,capsize=2))
  ax[0].set_xticks(x); ax[0].set_xticklabels(['0–30','30–100','100–200']); ax[0].set_xlabel('Depth (cm)'); ax[0].set_ylabel('Stock (Pg C, mean, 90% CI)'); ax[0].legend(fontsize=6)
  ax[1].hexbin(EM['p_soc_0_30'],EM['p_soc_0_30_sd'],gridsize=60,bins='log',cmap='Blues',mincnt=1,extent=(0,200,0,40)); ax[1].set_xlabel('SOC$_{0–30}$ mean (Mg C ha$^{-1}$)'); ax[1].set_ylabel('SD across fold models')
  for a,l in zip(ax,'ab'): a.text(-0.12,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')
  save(fig,FS+'FigS14_present_uncertainty')
