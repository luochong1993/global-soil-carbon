import sys,json,glob,numpy as np,pandas as pd
exec(open('/workspace/soil_global/scripts/43_v8_style.py').read())
R='/workspace/soil_global'; O7=R+'/out/v7'; O8=R+'/out/v8'; FM=R+'/figs/v9_main/'; FS=R+'/figs/v8_SI/'
L=lambda s: np.load(glob.glob(f'{O7}/maps10_{s}.npz')[0])
z0,z1,z2=L('0_30'),L('30_100'),L('100_200'); b5=np.load(R+'/out/v5/maps_b0.npz'); N=np.load(R+'/out/v6/N_huang_maps.npz')
fr=np.load(O8+'/frac_maps10.npz'); FJ=json.load(open(O8+'/fractions_v8.json')); import os
DJ=json.load(open(O8+'/drivers_v8.json')) if os.path.exists(O8+'/drivers_v8.json') else None; PD=json.load(open(O8+'/pdp.json')) if os.path.exists(O8+'/pdp.json') else None; OB=json.load(open(O8+'/obs_curves.json')) if os.path.exists(O8+'/obs_curves.json') else None
SOC=z0['soc']+z1['soc']+z2['soc']; SIC=z0['sic']+z1['sic']+z2['sic']; TC=SOC+SIC
SSP=['126','245','370','585']; SC={'126':'#1d3c8f','245':'#69b3e0','370':'#f39c4a','585':'#c0262c'}
log={}
def F(fn):
  try: fn(); print('ok',fn.__name__,flush=True)
  except Exception as e: import traceback; traceback.print_exc(); print('FAIL',fn.__name__,e,flush=True)
# ---------------- Fig1 present stocks
def fig1():
  fig=plt.figure(figsize=(7.2,6.3))
  a=fig.add_axes([0.07,0.78,0.38,0.18]); dens(a,[z0['soc'],z1['soc'],z2['soc']],['0–30 cm','30–100 cm','100–200 cm'],['#2171b5','#6a51a3','#e08214'],'log$_{10}$ SOC stock (Mg C ha$^{-1}$)',log=True,
     inset=(['SOC','SIC'],[[(z['soc']*area).sum()*1e-9/ (SOC*area).sum()*1e-9*100 for z in [z0]][0]]*0+[[ (z['soc']*area).sum()/(SOC*area).sum()*100,(z['sic']*area).sum()/(SIC*area).sum()*100] for z in (z0,z1,z2)]))
  letter(fig,a,'a',-0.05)
  b=fig.add_axes([0.57,0.78,0.38,0.18]); dens(b,[z0['sic'],z1['sic'],z2['sic']],['0–30 cm','30–100 cm','100–200 cm'],['#2171b5','#6a51a3','#e08214'],'log$_{10}$ SIC stock (Mg C ha$^{-1}$)',log=True); letter(fig,b,'b',-0.05)
  for k,(v,bins,cols,lab,rect,ins) in enumerate([(z0['soc'],[0,20,40,60,80,120,200,1e4],BLUES,'SOC$_{0–30}$ (Mg C ha$^{-1}$)',[0.0,0.42,0.5,0.3],'continent'),
      (z0['sic'],[0,1,5,10,20,40,80,1e4],PURP,'SIC$_{0–30}$ (Mg C ha$^{-1}$)',[0.5,0.42,0.5,0.3],'continent'),
      (SOC,[0,50,100,150,200,300,500,1e4],BLUES,'SOC$_{0–200}$',[0.0,0.06,0.5,0.3],'class'),
      (SIC,[0,5,20,50,100,200,400,1e4],PURP,'SIC$_{0–200}$',[0.5,0.06,0.5,0.3],'class')]):
    ax=mapax(fig,rect); classed(ax,v,bins,cols,ins,lab,fig); letter(fig,ax,'cdef'[k],0.02,-0.02)
  save(fig,FM+'Fig1_present_stocks')
def fig2():
  fig=plt.figure(figsize=(7.2,6.2))
  share=np.where(TC>0,SIC/TC*100,np.nan)
  ax=mapax(fig,[0.0,0.52,0.6,0.45]); classed(ax,share,[0,5,10,20,30,40,60,100],DIV6[::-1]+['#7a0177'] if False else ['#08306b','#3f6fbe','#7fa6ea','#c4c8f5','#fde08b','#f88b3c','#d7301f'],'class','SIC/TC$_{0–200}$ (%)',fig); letter(fig,ax,'a',0.02)
  s1,nm,ct=by_country(SOC); s2,_,_=by_country(SIC); df=pd.DataFrame(dict(n=nm,c=ct,soc=s1,sic=s2))[1:]; df=df[df.c!='']; df['tc']=df.soc+df.sic; df['sh']=df.sic/df.tc*100
  t=df.sort_values('tc',ascending=False).head(18)[::-1]; b=fig.add_axes([0.72,0.53,0.25,0.42])
  b.hlines(range(len(t)),0,t.tc,color='0.4',lw=0.6); b.scatter(t.tc,range(len(t)),c=[CCOL[c] for c in t.c],s=22,edgecolor='k',lw=0.3,zorder=3)
  b.set_yticks(range(len(t))); b.set_yticklabels(t.n,fontsize=5.5); b.set_xlabel('Total C 0–200 cm (Pg)'); b.xaxis.set_label_position('top'); b.xaxis.tick_top(); b.spines['bottom'].set_visible(False); b.spines['top'].set_visible(True); letter(fig,b,'b',-0.12)
  c=fig.add_axes([0.07,0.07,0.38,0.36]); big=df[df.tc>0.5]
  c.scatter(np.log10(big.soc),big.sh,s=8,c=[CCOL[x] for x in big.c],edgecolor='k',lw=0.2); m1=np.median(np.log10(big.soc)); m2=np.median(big.sh)
  c.axvline(m1,ls='--',c='0.5',lw=0.6); c.axhline(m2,ls='--',c='0.5',lw=0.6)
  for (qx,qy),(px,py) in {(1,1):(0.97,0.95),(0,1):(0.03,0.95),(0,0):(0.03,0.05),(1,0):(0.97,0.05)}.items():
    n=((np.log10(big.soc)>m1)==qx)&((big.sh>m2)==qy); c.text(px,py,f'{n.mean()*100:.0f}%',transform=c.transAxes,ha='right' if qx else 'left',va='top' if qy else 'bottom',fontweight='bold',fontsize=7)
  c.set_xlabel('log$_{10}$ country SOC$_{0–200}$ (Pg)'); c.set_ylabel('SIC share of TC (%)'); letter(fig,c,'c',-0.06)
  d=fig.add_axes([0.55,0.03,0.42,0.42],projection='polar'); top=df.sort_values('sic',ascending=False).head(36); top=top.sort_values(['c','sh'])
  th=np.linspace(0,2*np.pi,len(top),endpoint=False); d.bar(th,top.sh,width=2*np.pi/len(top)*0.85,color=[CCOL[x] for x in top.c],edgecolor='white',lw=0.3,bottom=8)
  for t_,r_,n_ in zip(th,top.sh,top.n): d.text(t_,r_+12,n_[:12],fontsize=4.2,rotation=np.degrees(t_) if np.degrees(t_)<=180 else np.degrees(t_)-180,ha='center',va='center')
  d.set_yticklabels([]); d.set_xticks([]); d.spines['polar'].set_visible(False); d.grid(lw=0.3)
  for k,cc in enumerate(CONT): fig.text(0.52,0.42-k*0.022,'■',color=CCOL[cc],fontsize=8); fig.text(0.545,0.422-k*0.022,cc,fontsize=6)
  letter(fig,d,'d',-0.02); save(fig,FM+'Fig2_SIC_share_countries')
def fig3():
  fig=plt.figure(figsize=(7.2,6.6))
  a=fig.add_axes([0.07,0.74,0.4,0.22]); dens(a,[b5[f'dsoc_0_30_{s}'] for s in SSP],[f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP],[SC[s] for s in SSP],'ΔSOC$_{0–30}$ equilibrium (Mg C ha$^{-1}$)',
     inset=(['<0','>0'],[[ (area[b5[f'dsoc_0_30_{s}']<0]).sum()/area.sum()*100,(area[b5[f'dsoc_0_30_{s}']>0]).sum()/area.sum()*100] for s in SSP])); a.set_xlim(-80,40); letter(fig,a,'a',-0.05)
  sh=np.load(R+'/out/v6/shift_585.npz')
  b=fig.add_axes([0.57,0.74,0.4,0.22]); dens(b,[sh['dsoc'],sh['dsic']],['ΔSOC$_{0–200}$','ΔSIC$_{0–200}$'],['#2171b5','#c0262c'],'Change SSP5-8.5 (Mg C ha$^{-1}$)'); b.set_xlim(-150,150); letter(fig,b,'b',-0.05)
  bins=[-1e4,-50,-20,-5,5,20,50,1e4]
  for k,(v,lab,rect) in enumerate([(b5['dsoc_0_30_126'],'ΔSOC$_{0–30}$ SSP1-2.6',[0.0,0.38,0.5,0.3]),(b5['dsoc_0_30_585'],'ΔSOC$_{0–30}$ SSP5-8.5',[0.5,0.38,0.5,0.3]),
      (sh['dsoc'],'ΔSOC$_{0–200}$ SSP5-8.5',[0.0,0.04,0.5,0.3]),(sh['dsic'],'ΔSIC$_{0–200}$ SSP5-8.5',[0.5,0.04,0.5,0.3])]):
    ax=mapax(fig,rect); classed(ax,v,bins,DIV,'class',lab,fig,fmt='{:g}'); letter(fig,ax,'cdef'[k],0.02,-0.02)
  save(fig,FM+'Fig3_climate_change')
def fig4():
  fig=plt.figure(figsize=(7.2,5.6))
  a=fig.add_axes([0.07,0.70,0.4,0.25]); dens(a,[N[f'dph_{s}'][N[f'dph_{s}']!=0] for s in ['126','370','585']],['SSP1-2.6','SSP3-7.0','SSP5-8.5'],[SC['126'],SC['370'],SC['585']],'ΔpH (cropland, N input)'); letter(fig,a,'a',-0.05)
  ax=mapax(fig,[0.0,0.32,0.5,0.32]); classed(ax,N['dSIC_loss_126'],[-1e4,-10,-5,-2,-1,-0.5,-0.01,0.01],DIV[:6]+['#f7f7f7'],'continent','ΔSIC$_{N}$ SSP1-2.6',fig); letter(fig,ax,'c',0.02)
  ax=mapax(fig,[0.5,0.32,0.5,0.32]); classed(ax,N['dSIC_loss_585'],[-1e4,-10,-5,-2,-1,-0.5,-0.01,0.01],DIV[:6]+['#f7f7f7'],'continent','ΔSIC$_{N}$ SSP5-8.5',fig); letter(fig,ax,'d',0.02)
  s,nm,ct=by_country(N['dSIC_loss_585']); df=pd.DataFrame(dict(n=nm,c=ct,l=-s))[1:]; t=df.sort_values('l',ascending=False).head(12)[::-1]
  b=fig.add_axes([0.62,0.70,0.33,0.26]); b.hlines(range(len(t)),0,t.l*1000,color='0.4',lw=0.6); b.scatter(t.l*1000,range(len(t)),c=[CCOL.get(c,'0.5') for c in t.c],s=20,edgecolor='k',lw=0.3,zorder=3)
  b.set_yticks(range(len(t))); b.set_yticklabels(t.n,fontsize=5.5); b.set_xlabel('SIC loss 0–200 cm, 2020–2050, SSP5-8.5 (Tg C)'); letter(fig,b,'b',-0.12)
  c=fig.add_axes([0.1,0.05,0.85,0.18]); tot=json.load(open(R+'/out/v6/N_huang_formula.json')) if False else None
  vals=[-(N[f'dSIC_loss_{s}']*area).sum()*1e-9 for s in ['126','370','585']]
  PN=json.load(open(O8+'/paper_numbers_v8.json'))['N_acidification']['IMAGE_Huang_formula']; top=[PN[f'ssp{s}_2020_2050']['loss_only_0_30'] for s in ['126','370','585']]
  xx=np.arange(3); c.bar(xx-0.17,top,0.32,color=[SC['126'],SC['370'],SC['585']],alpha=0.45,edgecolor='k',lw=0.4,label='0–30 cm'); c.bar(xx+0.17,vals,0.32,color=[SC['126'],SC['370'],SC['585']],edgecolor='k',lw=0.4,label='0–200 cm')
  c.set_xticks(xx); c.set_xticklabels(['SSP1-2.6','SSP3-7.0','SSP5-8.5']); c.set_ylabel('SIC loss 2020–2050 (Pg C)')
  for i,v in enumerate(vals): c.text(i+0.17,v,f'{v:.1f}',ha='center',va='bottom',fontweight='bold')
  for i,v in enumerate(top): c.text(i-0.17,v,f'{v:.1f}',ha='center',va='bottom',fontweight='bold')
  from matplotlib.patches import Patch; c.legend(handles=[Patch(facecolor='0.75',edgecolor='k',lw=0.4,label='0–30 cm'),Patch(facecolor='0.35',edgecolor='k',lw=0.4,label='0–200 cm')],fontsize=6,frameon=False,loc='upper left')
  letter(fig,c,'e',-0.06); save(fig,FM+'Fig4_N_acidification')
def fig5():
  sh=np.load(R+'/out/v6/shift_585.npz'); fig=plt.figure(figsize=(7.2,5.0))
  ax=mapax(fig,[0.0,0.38,1.0,0.6]); p=bivar(ax,sh['dsoc'],sh['dsic'],0,0,['ΔSOC','ΔSIC'],cols={(1,1):'#3b4994',(1,0):'#5ac8c8',(0,1):'#be64ac',(0,0):'#d7301f'}); log['fig5_quadrants']=p; letter(fig,ax,'a',0.03)
  s1,nm,ct=by_country(sh['dsoc']); s2,_,_=by_country(sh['dsic']); df=pd.DataFrame(dict(n=nm,c=ct,a=s1,b=s2))[1:]; df=df[(df.c!='')&((df.a.abs()+df.b.abs())>0.05)]
  c=fig.add_axes([0.08,0.06,0.38,0.3]); c.scatter(df.a,df.b,s=9,c=['#3b4994' if (x>0 and y>0) else '#5ac8c8' if x>0 else '#be64ac' if y>0 else '#d7301f' for x,y in zip(df.a,df.b)],edgecolor='k',lw=0.2)
  c.axhline(0,ls='--',c='0.5',lw=0.6); c.axvline(0,ls='--',c='0.5',lw=0.6); c.set_xscale('symlog',linthresh=1); c.set_yscale('symlog',linthresh=1); [g([-10,-1,0,1,10]) for g in (c.set_xticks,c.set_yticks)]; c.set_xticklabels(['−10','−1','0','1','10']); c.set_yticklabels(['−10','−1','0','1','10'])
  for t in df.reindex(df.a.abs().sort_values().index[-6:]).itertuples(): c.text(t.a,t.b,t.n[:10],fontsize=4.5)
  for (qx,qy),(px,py) in {(1,1):(0.97,0.95),(0,1):(0.03,0.95),(0,0):(0.03,0.05),(1,0):(0.97,0.05)}.items():
    n=((df.a>0)==qx)&((df.b>0)==qy); c.text(px,py,f'{n.mean()*100:.0f}%',transform=c.transAxes,ha='right' if qx else 'left',va='top' if qy else 'bottom',fontweight='bold')
  c.set_xlabel('Country ΔSOC (Pg C)'); c.set_ylabel('Country ΔSIC (Pg C)'); letter(fig,c,'b',-0.06)
  d=fig.add_axes([0.58,0.06,0.38,0.3]); net=(sh['dsoc']+sh['dsic']); bot=np.zeros(2)
  for k,cc in enumerate(CONT):
    ids,nm_,ct_=countries(); m=ct_[ids]==cc; v=[(sh['dsoc'][m]*area[m]).sum()*1e-9,(sh['dsic'][m]*area[m]).sum()*1e-9]
    d.bar([0,1],v,0.55,color=CCOL[cc],edgecolor='white',lw=0.3,label=cc,bottom=[0,0] if k==0 else None)
  d.cla()
  M=np.array([[(sh[k][countries()[2][countries()[0]]==cc]*area[countries()[2][countries()[0]]==cc]).sum()*1e-9 for k in ('dsoc','dsic')] for cc in CONT])
  x=np.arange(len(CONT)); d.bar(x-0.18,M[:,0],0.36,color='#2171b5',label='ΔSOC'); d.bar(x+0.18,M[:,1],0.36,color='#c0262c',label='ΔSIC'); d.axhline(0,c='k',lw=0.4)
  d.set_xticks(x); d.set_xticklabels(CONT); d.set_ylabel('Change by continent (Pg C)'); d.legend(fontsize=6); letter(fig,d,'c',-0.06)
  save(fig,FM+'Fig5_bivariate_SOC_SIC')
def fig6():
  fig=plt.figure(figsize=(7.2,7.0)); ma,po,f=fr['MA_0_30'],fr['PO_0_30'],fr['f_0_30']
  a=fig.add_axes([0.07,0.77,0.4,0.19]); dens(a,[ma,po,fr['MA_30_100'],fr['PO_30_100']],['MAOC 0–30','POC 0–30','MAOC 30–100','POC 30–100'],['#2171b5','#e08214','#08306b','#a63603'],'log$_{10}$ stock (Mg C ha$^{-1}$)',log=True)
  for l in a.lines[1::2][2:]: l.set_ls(':')
  letter(fig,a,'a',-0.05)
  b=fig.add_axes([0.58,0.77,0.38,0.19]); sc=FJ['future_0_30']['scen']; x=np.arange(4)
  for k,(key,lab,col,off) in enumerate([('dMAOC_eq','ΔMAOC eq.','#2171b5',-0.3),('dPOC_eq','ΔPOC eq.','#e08214',-0.1)]):
    v=[sc[s][key] for s in SSP]; e=np.array([[sc[s][key]-sc[s][key+'_range'][0],sc[s][key+'_range'][1]-sc[s][key]] for s in SSP]).T
    b.bar(x+off,v,0.2,color=col,label=lab,yerr=e,error_kw=dict(lw=0.5,capsize=1.5))
  b.bar(x+0.1,[sc[s]['tl_central']['dMAOC'] for s in SSP],0.2,color='#9ecae1',label='ΔMAOC by 2100'); b.bar(x+0.3,[sc[s]['tl_central']['dPOC'] for s in SSP],0.2,color='#fdbe85',label='ΔPOC by 2100')
  b.axhline(0,c='k',lw=0.4); b.set_xticks(x); b.set_xticklabels(['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5'],fontsize=6); b.set_ylabel('Δ stock 0–30 cm (Pg C)'); b.legend(fontsize=5,ncol=2,loc='lower left'); letter(fig,b,'b',-0.06)
  ax=mapax(fig,[0.0,0.42,0.5,0.3]); classed(ax,f*100,[0,50,60,70,80,85,90,100],['#fdd0a2','#fdae6b','#fd8d3c','#c6dbef','#6baed6','#2171b5','#08306b'],'class','f$_{MAOC}$ 0–30 (%)',fig); letter(fig,ax,'c',0.02,-0.02)
  ax=mapax(fig,[0.5,0.42,0.5,0.3]); classed(ax,ma,[0,10,20,30,40,60,90,1e4],BLUES,'continent','MAOC$_{0–30}$ (Mg C ha$^{-1}$)',fig); letter(fig,ax,'d',0.02,-0.02)
  ax=mapax(fig,[0.0,0.03,0.62,0.36]); q=bivar(ax,ma,po,np.nanmedian(ma),np.nanmedian(po),['MAOC','POC']); log['fig6_quadrants']=q; letter(fig,ax,'e',0.02,-0.02)
  c=fig.add_axes([0.70,0.07,0.27,0.28]); G=FJ['Georgiou']; o=FJ
  vals=[[o['_0_30']['MAOC'],o['_30_100']['MAOC']],[G['grid_sum_0_30'],G['grid_sum_30_100']]]
  c.bar([0,1],[vals[0][0],vals[1][0]],0.5,color=['#2171b5','#9ecae1'],label='0–30 cm'); c.bar([0,1],[vals[0][1],vals[1][1]],0.5,bottom=[vals[0][0],vals[1][0]],color=['#08306b','#4292c6'],label='30–100 cm')
  c.errorbar(0,vals[0][0],yerr=[[vals[0][0]-o['_0_30']['MAOC_CI90'][0]],[o['_0_30']['MAOC_CI90'][1]-vals[0][0]]],c='k',lw=0.6,capsize=2)
  c.axhline(899,ls='--',c='0.4',lw=0.6); c.text(1.3,905,'Georgiou 2022\n(non-permafrost, 899)',fontsize=5,ha='right',va='bottom')
  c.set_xticks([0,1]); c.set_xticklabels(['This study','Georgiou grid'],fontsize=6); c.set_ylabel('Global MAOC (Pg C)'); c.legend(fontsize=5,loc='lower right'); letter(fig,c,'f',-0.06)
  save(fig,FM+'Fig6_MAOC_POC')
GC={'Climate':'#c0262c','Soil':'#8c510a','Topography':'#7fbc41','Parent material':'#6a51a3','Sampling':'#bdbdbd'}
def fig7():
  fig=plt.figure(figsize=(7.2,6.6)); S=DJ['shap']; comps=list(S); g=DJ['groups']
  a=fig.add_axes([0.08,0.70,0.36,0.26]); left=np.zeros(len(comps))
  for gg in g:
    v=np.array([S[c]['group_pct'][gg] for c in comps]); a.barh(range(len(comps)),v,left=left,color=GC[gg],label=gg,edgecolor='white',lw=0.3)
    for i,(l_,vv) in enumerate(zip(left,v)):
      if vv>9: a.text(l_+vv/2,i,f'{vv:.0f}',ha='center',va='center',fontsize=5.5,color='white',fontweight='bold')
    left+=v
  a.set_yticks(range(len(comps))); a.set_yticklabels(comps); a.set_xlabel('Share of mean |SHAP| (%)'); a.set_xlim(0,100); a.legend(fontsize=5,ncol=5,loc='lower center',bbox_to_anchor=(0.5,1.0),handlelength=1); letter(fig,a,'a',-0.1)
  dd=np.load(O8+'/dominant_driver.npz'); cols=[GC[x] for x in g[:4]]
  for k,(key,rect) in enumerate([('SIC presence',[0.5,0.68,0.5,0.3]),('fMAOC',[0.0,0.36,0.5,0.3]),('SOC (mineral)',[0.5,0.36,0.5,0.3])]):
    ax=mapax(fig,rect); classed(ax,dd[key].astype(float)+0.5,[0,1,2,3,4],cols,'class',key,fig,cats=['Climate','Soil','Topo.','Parent']); letter(fig,ax,'bcd'[k],0.02,-0.02)
  for k,(key,xl,yl,col) in enumerate([('SIC_presence_vs_logAI','ln(1+P/PET)','P(SIC>0.1)','#6a51a3'),('SIC_presence_vs_pH','predicted pH','P(SIC>0.1)','#6a51a3'),('fMAOC_vs_clay','clay (%)','f$_{MAOC}$','#2171b5'),('fMAOC_vs_CEC','CEC (cmol kg$^{-1}$)','f$_{MAOC}$','#2171b5')]):
    p=PD[key]; ax=fig.add_axes([0.07+k*0.24,0.06,0.18,0.18]); ax.plot(p['x'],p['y'],c=col,lw=1.2); ax.axvline(p['breakpoint'],ls='--',c='0.4',lw=0.6)
    ax.text(p['breakpoint'],ax.get_ylim()[1],f" {p['breakpoint']:.2g}",fontsize=5.5,va='top'); ax.set_xlabel(xl); ax.set_ylabel(yl); letter(fig,ax,'efgh'[k],-0.05)
  save(fig,FM+'Fig7_drivers')
for f in [globals()[n] for n in (sys.argv[1:] or ['fig1','fig2','fig3','fig4','fig5','fig6','fig7'])]: F(f)
json.dump(log,open(O8+'/fig_numbers.json','w'),indent=1)
