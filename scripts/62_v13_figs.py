# v13 new SI figures (S15-S22) from out/v10 + out/v13 summaries. Style = 43_v8_style.py (v10 figures).
import sys,json,numpy as np,pandas as pd
exec(open('/workspace/soil_global/scripts/43_v8_style.py').read())
R='/workspace/soil_global'; FS=R+'/figs/v13_SI/'
EM=np.load(R+'/out/v10/ens_maps.npz'); S=json.load(open(R+'/out/v13/summaries_v13.json')); CM=np.load(R+'/out/v13/cellmaps_v13.npz')
PT=json.load(open(R+'/out/v13/points_summary_v13.json')); PD=np.load(R+'/out/v13/points_density_1deg.npz')
SSP=['126','245','370','585']; LBL={s:f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP}; SC={'126':'#1d3c8f','245':'#69b3e0','370':'#f39c4a','585':'#c0262c'}
DC=['#2171b5','#6a51a3','#e08214']; DL=['0–30 cm','30–100 cm','100–200 cm']; LAY=['_0_30','_30_100','_100_200']
SOCB=['#9ecae1','#4292c6','#08519c']; SICB=['#bcbddc','#807dba','#4a1486']
KC={'A':'#2166ac','B':'#e08214','C':'#4dac26','D':'#8073ac','E':'#9ecae1'}; KN={'A':'Tropical','B':'Arid','C':'Temperate','D':'Cold','E':'Polar'}
GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#a6761d']))
log={}
def lt(ax,s,x=-0.12,y=1.03): ax.text(x,y,s,transform=ax.transAxes,fontsize=9,fontweight='bold',va='bottom')
kg=np.load(R+'/out/v2/kg_beck.npz'); K0=kg['1991-2020'][mask].astype(int)
MAIN=np.array(['']+['A']*3+['B']*4+['C']*9+['D']*12+['E']*2); km0=MAIN[np.clip(K0,0,30)]
SOC=EM['p_soc_0_30']+EM['p_soc_30_100']+EM['p_soc_100_200']; SIC=EM['p_sic_0_30']+EM['p_sic_30_100']+EM['p_sic_100_200']
PR=S['present_regions']; AR=S['area_Mkm2']

def S15():  # Koppen zones
  fig=plt.figure(figsize=(7.2,6.0))
  ax=mapax(fig,[0.0,0.53,0.52,0.42]); v=np.array([('ABCDE'.index(k)+0.5) if k else np.nan for k in km0])
  classed(ax,v,[0,1,2,3,4,5],[KC[k] for k in 'ABCDE'],'class','Köppen–Geiger\n1991–2020',fig,cats=list('ABCDE')); letter(fig,ax,'a',0.02)
  b=fig.add_axes([0.61,0.58,0.36,0.36]); x=np.arange(5); w=0.38
  for j,(pool,cols,off) in enumerate([('soc',SOCB,-w/2),('sic',SICB,w/2)]):
    bot=np.zeros(5)
    for l,lay in enumerate(LAY):
      vals=np.array([PR['koppen_main'][k][pool+lay]['mean'] for k in 'ABCDE']); b.bar(x+off,vals,w,bottom=bot,color=cols[l],edgecolor='white',lw=0.3,label=f'{pool.upper()} {DL[l]}'); bot+=vals
    sd=[PR['koppen_main'][k][pool+'_0_200']['sd'] for k in 'ABCDE']; b.errorbar(x+off,bot,yerr=sd,fmt='none',ecolor='k',elinewidth=0.5,capsize=1.5)
    log[f'S15_{pool}_0_200']=dict(zip('ABCDE',bot.round(0).tolist()))
  b.set_xticks(x); b.set_xticklabels([f'{k}\n{KN[k]}' for k in 'ABCDE']); b.set_ylabel('Stock 0–200 cm (Pg C)'); b.legend(fontsize=5,ncol=2,loc='upper left',handlelength=1)
  b.set_ylim(0,max(b.get_ylim()[1],1)*1.25); lt(b,'b',-0.16)
  c=fig.add_axes([0.08,0.08,0.36,0.36])
  for j,(pool,col,mk) in enumerate([('soc','#2171b5','o'),('sic','#6a51a3','s')]):
    d=[PR['koppen_main'][k][pool+'_0_200']['mean']/AR['koppen_main'][k]*10 for k in 'ABCDE']   # Pg/Mkm2 *10 = Mg/ha
    c.hlines(np.arange(5)+(j-0.5)*0.25,0,d,color=col,lw=0.8); c.scatter(d,np.arange(5)+(j-0.5)*0.25,color=col,marker=mk,s=22,edgecolor='k',lw=0.3,zorder=3,label=pool.upper())
    for i,dd in enumerate(d): c.text(dd+12,i+(j-0.5)*0.25,f'{dd:.0f}',va='center',fontsize=5.5)
  c.set_yticks(range(5)); c.set_yticklabels([f'{k} {KN[k]}' for k in 'ABCDE']); c.invert_yaxis(); c.set_xlim(0,430); c.set_xlabel('Mean stock density 0–200 cm (Mg C ha$^{-1}$)'); c.legend(fontsize=6,loc='upper right'); lt(c,'c',-0.2)
  d=fig.add_axes([0.60,0.08,0.37,0.40]); sub=PR['koppen_sub']
  rows=[(k,sub[k]['sic_0_200']['mean']/(sub[k]['sic_0_200']['mean']+sub[k]['soc_0_200']['mean'])*100,AR['koppen_sub'][k]) for k in sub if AR['koppen_sub'][k]>0.5]
  rows=sorted(rows,key=lambda r:r[1])
  d.hlines(range(len(rows)),0,[r[1] for r in rows],color='0.5',lw=0.6)
  d.scatter([r[1] for r in rows],range(len(rows)),s=[8+r[2]*2.2 for r in rows],c=[KC[r[0][0]] for r in rows],edgecolor='k',lw=0.3,zorder=3)
  d.set_yticks(range(len(rows))); d.set_yticklabels([r[0] for r in rows],fontsize=5.5); d.set_xlabel('SIC share of TC, 0–200 cm (%)'); d.set_xlim(0,100)
  for a_ in [5,10,20]: d.scatter([],[],s=8+a_*2.2,c='w',edgecolor='k',lw=0.3,label=f'{a_} Mkm²')
  d.legend(fontsize=5,loc='lower right',title='Area',title_fontsize=5,labelspacing=0.8); lt(d,'d',-0.14)
  log['S15_sub_share']={r[0]:round(r[1],1) for r in rows}
  save(fig,FS+'FigS15_koppen_stocks')

def S16():  # latitude profiles
  L=S['lat_profiles']; lat_=np.array(L['lat'])+0.5
  sm=lambda v: np.convolve(np.array(v),np.ones(3)/3,'same')
  fig,ax=plt.subplots(1,6,figsize=(7.2,3.3),sharey=True); plt.subplots_adjust(wspace=0.12,left=0.07,right=0.99,bottom=0.17,top=0.86)
  for l,lay in enumerate(['0_30','30_100','100_200']):
    ax[0].fill_betweenx(lat_,0,sm(L['SOC_'+lay]),color=DC[l],alpha=0.18,lw=0); ax[0].plot(sm(L['SOC_'+lay]),lat_,c=DC[l],lw=0.9,label=DL[l])
    ax[1].fill_betweenx(lat_,0,sm(L['SIC_'+lay]),color=DC[l],alpha=0.18,lw=0); ax[1].plot(sm(L['SIC_'+lay]),lat_,c=DC[l],lw=0.9,label=DL[l])
  ax[0].set_xlabel('SOC (Pg C per 1° lat.)'); ax[1].set_xlabel('SIC (Pg C per 1° lat.)'); ax[0].legend(fontsize=5,loc='lower right')
  for k,(key,col,ls) in enumerate([('MAOC_0_30','#2171b5','-'),('POC_0_30','#e08214','-'),('MAOC_30_100','#08306b',':'),('POC_30_100','#a63603',':')]):
    ax[2].plot(sm(L[key]),lat_,c=col,ls=ls,lw=0.9,label=key.replace('_0_30',' 0–30').replace('_30_100',' 30–100'))
  ax[2].set_xlabel('MAOC, POC (Pg C per 1°)'); ax[2].legend(fontsize=4.8,loc='lower right')
  soc=sum(np.array(L['SOC_'+l]) for l in ['0_30','30_100','100_200']); sic=sum(np.array(L['SIC_'+l]) for l in ['0_30','30_100','100_200'])
  sh=np.where(soc+sic>0.05,sic/(soc+sic)*100,np.nan); ax[3].plot(sm(sh),lat_,c='#7a0177',lw=1); ax[3].fill_betweenx(lat_,0,sm(sh),color='#7a0177',alpha=0.15,lw=0)
  ax[3].axvline(S['present_regions']['continent']['AS']['soc_0_200']['mean']*0+1598/4105*100 if False else 1598/(2506+1598)*100,ls='--',c='0.5',lw=0.6); ax[3].set_xlabel('SIC share of TC (%)'); ax[3].set_xlim(0,100)
  for s in SSP:
    ax[4].plot(sm(L[f'dSOC_0_200_{s}']),lat_,c=SC[s],lw=0.9,label=LBL[s]); ax[5].plot(sm(L[f'dSIC_0_200_{s}']),lat_,c=SC[s],lw=0.9,label=LBL[s])
  for a_ in ax[4:]: a_.axvline(0,c='k',lw=0.4)
  ax[4].set_xlabel('Eq. ΔSOC$_{0–200}$ (Pg per 1°)'); ax[5].set_xlabel('Eq. ΔSIC$_{0–200}$ (Pg per 1°)'); ax[5].legend(fontsize=4.8,loc='lower right')
  ax[0].set_ylabel('Latitude (°)'); ax[0].set_ylim(-56,84); ax[0].set_yticks([-40,-20,0,20,40,60,80])
  for a_,l in zip(ax,'abcdef'): lt(a_,l,-0.1,1.02); a_.tick_params(labelsize=5.5); a_.xaxis.label.set_size(6)
  i=int(np.nanargmax(soc)); log['S16_soc_peak_lat']=float(lat_[i]); log['S16_sic_peak_lat']=float(lat_[int(np.nanargmax(sic))])
  save(fig,FS+'FigS16_latitude_profiles')

def S17():  # depth by continent, ring charts
  fig=plt.figure(figsize=(7.2,4.6)); regs=['Global']+CONT; G=S['present_regions']['continent']
  def val(r,pool,lay):
    if r=='Global': return sum(G[c][pool+lay]['mean'] for c in G)
    return G[r][pool+lay]['mean']
  for i,r in enumerate(regs):
    a=fig.add_axes([0.005+i*0.141,0.58,0.135,0.33])
    so=[val(r,'soc',l) for l in LAY]; si=[val(r,'sic',l) for l in LAY]
    a.pie(so,radius=1,colors=SOCB,startangle=90,counterclock=False,wedgeprops=dict(width=0.3,edgecolor='white',lw=0.5))
    a.pie(si,radius=0.68,colors=SICB,startangle=90,counterclock=False,wedgeprops=dict(width=0.3,edgecolor='white',lw=0.5))
    a.text(0,0,r,ha='center',va='center',fontsize=5.5 if r=='Global' else 6,fontweight='bold'); a.text(0,-1.12,f'TC {sum(so)+sum(si):.0f} Pg',ha='center',va='top',fontsize=5.5); a.set_aspect('equal')
    a.set_title(f'below 30 cm:\nSOC {sum(so[1:])/sum(so)*100:.0f}%  SIC {sum(si[1:])/sum(si)*100:.0f}%',fontsize=5,pad=1)
    log[f'S17_{r}_deep_share']=(round(sum(so[1:])/sum(so)*100,1),round(sum(si[1:])/sum(si)*100,1))
  fig.text(0.01,0.95,'a',fontsize=9,fontweight='bold')
  from matplotlib.patches import Patch
  fig.legend(handles=[Patch(color=c,label=f'SOC {d} (outer)') for c,d in zip(SOCB,DL)]+[Patch(color=c,label=f'SIC {d} (inner)') for c,d in zip(SICB,DL)],ncol=6,fontsize=5.5,loc='upper center',bbox_to_anchor=(0.5,0.555),handlelength=1)
  b=fig.add_axes([0.1,0.08,0.86,0.36]); y=np.arange(len(CONT))
  for j,(pool,cols,off) in enumerate([('soc',SOCB,-0.2),('sic',SICB,0.2)]):
    left=np.zeros(len(CONT))
    for l,lay in enumerate(LAY):
      v=np.array([G[c][pool+lay]['mean'] for c in CONT]); b.barh(y+off,v,0.38,left=left,color=cols[l],edgecolor='white',lw=0.3); left+=v
    sd=[G[c][pool+'_0_200']['sd'] for c in CONT]; b.errorbar(left,y+off,xerr=sd,fmt='none',ecolor='k',elinewidth=0.5,capsize=1.2)
    for k,c in enumerate(CONT): b.text(left[k]+sd[k]+8,y[k]+off,f'{left[k]:.0f}',va='center',fontsize=5)
  for k,c in enumerate(CONT):
    sh=G[c]['sic_0_200']['mean']/(G[c]['sic_0_200']['mean']+G[c]['soc_0_200']['mean'])*100; b.text(1.0,y[k],f'SIC {sh:.0f}%',transform=b.get_yaxis_transform(),ha='right',va='center',fontsize=5.5,color='#4a1486')
  b.set_xlim(0,820); b.set_yticks(y); b.set_yticklabels(['Asia','Europe','North America','South America','Africa','Oceania']); b.invert_yaxis(); b.set_xlabel('Stock 0–200 cm (Pg C; upper bar SOC, lower bar SIC)'); lt(b,'b',-0.1)
  save(fig,FS+'FigS17_depth_by_continent')

def S18():  # per-GCM spread
  P=S['per_gcm']; fig,ax=plt.subplots(2,2,figsize=(7.2,5.0)); plt.subplots_adjust(hspace=0.35,wspace=0.25,top=0.9)
  E=json.load(open(R+'/out/v10/paper_numbers_v10.json'))['future']
  items=[('dSOC_0_200','Eq. ΔSOC 0–200 cm (Pg C)','dSOC_0_200'),('dSIC_0_200','Eq. ΔSIC 0–200 cm (Pg C)','dSIC_0_200'),('dTC_0_200','Eq. ΔTC 0–200 cm (Pg C)','dTC_0_200'),('dpH_mean','Area-weighted mean Δ topsoil pH',None)]
  rng=np.random.default_rng(1)
  for a,(key,yl,ek) in zip(ax.flat,items):
    for i,s in enumerate(SSP):
      for g,(gc,col) in enumerate(GC6.items()):
        q=P[f'{s}_{gc}'][key]; xx=i+(g-2.5)*0.12
        if key in P[f'{s}_{gc}']['members']: a.scatter(xx+rng.uniform(-0.03,0.03,10),P[f'{s}_{gc}']['members'][key],s=2,color=col,alpha=0.5,lw=0)
        a.vlines(xx,q['p05'],q['p95'],color=col,lw=0.6) if key not in P[f'{s}_{gc}']['members'] else None
        a.scatter(xx,q['mean'],s=16,color=col,edgecolor='k',lw=0.3,zorder=3,label=gc if i==0 else None)
      if ek: m=E[s]['eq'][ek]; a.hlines(m['mean'],i-0.4,i+0.4,color='k',lw=0.9); a.add_patch(Rectangle((i-0.4,m['p05']),0.8,m['p95']-m['p05'],color=SC[s],alpha=0.12,lw=0))
    a.axhline(0,c='0.5',lw=0.4,ls='--'); a.set_xticks(range(4)); a.set_xticklabels([LBL[s] for s in SSP]); a.set_ylabel(yl)
  ax[0,0].legend(fontsize=5.5,ncol=6,loc='lower center',bbox_to_anchor=(1.1,1.08),handletextpad=0.2,columnspacing=0.8)
  for a,l in zip(ax.flat,'abcd'): lt(a,l,-0.14)
  log['S18']={k:{kk:round(v[kk]['mean'],1) for kk in ['dSOC_0_200','dSIC_0_200','dTC_0_200']} for k,v in P.items() if k.startswith('585')}
  save(fig,FS+'FigS18_per_GCM_spread')

def S19():  # SSP comparison of dTC + member agreement
  fig=plt.figure(figsize=(7.2,6.6)); bins=[-1e4,-50,-20,-5,5,20,50,1e4]
  for k,s in enumerate(SSP):
    v=EM[f'dsoc_0_200_{s}']+EM[f'dsic_0_200_{s}']; ax=mapax(fig,[0.0+0.5*(k%2),0.70-0.33*(k//2),0.5,0.27]); classed(ax,v,bins,DIV,'class',f'Eq. ΔTC$_{{0–200}}$ {LBL[s]}',fig); letter(fig,ax,'abcd'[k],0.02,-0.01)
    log[f'S19_dTC_{s}_Pg']=float((v*area).sum()*1e-9); log[f'S19_dTC_{s}_neg_area_pct']=float(area[v<0].sum()/area.sum()*100)
  ab=[-10,0,10,25,40,60,75,90,100.01]; cats=['|Δ|<1','<10','10–25','25–40','40–60','60–75','75–90','≥90']
  vs=np.where(np.abs(CM['mean_dsoc_585'])<1,-5,CM['frac_dsoc_neg_585']*100); vi=np.where(np.abs(CM['mean_dsic_585'])<1,-5,CM['frac_dsic_pos_585']*100)
  log['S19_negligible_area_pct']=dict(soc=float(area[np.abs(CM['mean_dsoc_585'])<1].sum()/area.sum()*100),sic=float(area[np.abs(CM['mean_dsic_585'])<1].sum()/area.sum()*100))
  ax=mapax(fig,[0.0,0.04,0.5,0.27]); P_=ax.get_position(); classed(ax,vs,ab,['#f4f4f4']+DIV[::-1],'class','Members with\nΔSOC < 0 (%)',fig,cbrect=[P_.x0+P_.width*0.24,P_.y0-0.015,P_.width*0.62,0.012],cats=cats); letter(fig,ax,'e',0.02,-0.01)
  ax=mapax(fig,[0.5,0.04,0.5,0.27]); P_=ax.get_position(); classed(ax,vi,ab,['#f4f4f4']+DIV,'class','Members with\nΔSIC > 0 (%)',fig,cbrect=[P_.x0+P_.width*0.24,P_.y0-0.015,P_.width*0.62,0.012],cats=cats); letter(fig,ax,'f',0.02,-0.01)
  f1=CM['frac_dsoc_neg_585']; f2=CM['frac_dsic_pos_585']
  log['S19_agree']=dict(soc_loss_ge90=float(area[f1>=0.9].sum()/area.sum()*100),soc_gain_ge90=float(area[f1<=0.1].sum()/area.sum()*100),sic_gain_ge90=float(area[f2>=0.9].sum()/area.sum()*100),sic_loss_ge90=float(area[f2<=0.1].sum()/area.sum()*100))
  save(fig,FS+'FigS19_SSP_dTC_agreement')

def S20():  # present-day uncertainty maps
  fig=plt.figure(figsize=(7.2,5.4)); bins=[0,2,5,10,15,20,30,1e4]; cols=['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#e31a1c','#800026']
  for k,(key,lab) in enumerate([('cv_soc','CV SOC$_{0–200}$ (%)'),('cv_sic','CV SIC$_{0–200}$ (%)'),('cv_ma','CV MAOC$_{0–30}$ (%)')]):
    ax=mapax(fig,[0.0+0.5*(k%2),0.55-0.47*(k//2),0.5,0.40]); classed(ax,CM[key],bins,cols,'class',lab,fig); letter(fig,ax,'abc'[k],0.02,-0.01)
    v=CM[key]; ok=np.isfinite(v); log[f'S20_{key}_cell_median']=float(np.median(v[ok])) ; log[f'S20_{key}_area_gt20pct']=float(area[ok&(v>20)].sum()/area[ok].sum()*100)
  d=fig.add_axes([0.58,0.12,0.36,0.28]); dens(d,[CM['cv_soc'],CM['cv_sic'],CM['cv_ma']],['SOC 0–200','SIC 0–200','MAOC 0–30'],['#2171b5','#6a51a3','#08306b'],'log$_{10}$ CV across fold-models (%)',log=True); letter(fig,d,'d',-0.05)
  save(fig,FS+'FigS20_uncertainty_maps')

def S21():  # Koppen transitions SSP5-8.5
  T=S['transitions_main']['585']; tl=[(k,v) for k,v in T.items() if not k.startswith('_')]; tl=sorted(tl,key=lambda kv:-kv[1]['area_Mkm2'])
  top=[k for k,v in tl if v['area_Mkm2']>=0.3]; log['S21_trans_area']={k:round(v['area_Mkm2'],2) for k,v in tl}
  fig=plt.figure(figsize=(7.2,6.4))
  kf=MAIN[np.clip(kg['2071-2099-ssp585'][mask].astype(int),0,30)]; tk=np.char.add(np.char.add(km0.astype('U1'),'>'),kf.astype('U1'))
  pal=['#d7301f','#fc8d59','#fee08b','#91bfdb','#4575b4','#1a9850','#984ea3','#a6611a']
  code=np.full(len(tk),np.nan); cats=[]
  for i,t in enumerate(top[:7]): code[tk==t]=i+0.5; cats.append(t.replace('>','→'))
  code[np.isnan(code)&(km0!=kf)&(km0!='')]=len(cats)+0.5; cats.append('Other')
  ax=mapax(fig,[0.0,0.50,0.62,0.46]); ns=np.where(np.isnan(code)&(km0!=''),1.0,np.nan)
  ax.imshow(to2d(ns),origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),cmap=ListedColormap(['#fdfdfd']),interpolation='nearest',zorder=0.5,regrid_shape=1400)
  P_=ax.get_position(); classed(ax,code,list(range(len(cats)+1)),pal[:len(cats)],'class','Main-class\ntransition',fig,cats=cats,cbrect=[P_.x0+P_.width*0.2,P_.y0-0.015,P_.width*0.66,0.012]); letter(fig,ax,'a',0.02)
  # alluvial
  b=fig.add_axes([0.68,0.52,0.30,0.42]); Mx=np.array(T['_matrix_Mkm2']); tot0=Mx.sum(1); tot1=Mx.sum(0); gap=1.5
  y0=np.concatenate([[0],np.cumsum(tot0+gap)])[:5]; y1=np.concatenate([[0],np.cumsum(tot1+gap)])[:5]
  for i,k in enumerate('ABCDE'):
    b.add_patch(Rectangle((0,y0[i]),0.08,tot0[i],color=KC[k])); b.add_patch(Rectangle((0.92,y1[i]),0.08,tot1[i],color=KC[k]))
    b.text(-0.03,y0[i]+tot0[i]/2,f'{k} {tot0[i]:.0f}',ha='right',va='center',fontsize=5.5); b.text(1.03,y1[i]+tot1[i]/2,f'{k} {tot1[i]:.0f}',ha='left',va='center',fontsize=5.5)
  o0=y0.copy(); o1=y1.copy(); t=np.linspace(0,1,50); sg=3*t**2-2*t**3
  for i in range(5):
    for j in range(5):
      f=Mx[i,j]
      if f<=0: o0[i]+=0; continue
      lo=o0[i]+(o1[j]-o0[i])*sg; xs=0.08+0.84*t
      b.fill_between(xs,lo,lo+f,color=KC['ABCDE'[i]],alpha=0.25 if i==j else 0.75,lw=0); o0[i]+=f; o1[j]+=f
  b.set_xlim(-0.25,1.25); b.set_ylim(y0[-1]+tot0[-1]+1,-1); b.axis('off'); b.text(0.04,-3,'1991–2020',ha='center',fontsize=6); b.text(0.96,-3,'2071–2099',ha='center',fontsize=6)
  b.text(-0.3,-6,'b',fontsize=9,fontweight='bold',va='bottom')
  c=fig.add_axes([0.08,0.07,0.55,0.33]); x=np.arange(len(top))
  for j,(key,col,off) in enumerate([('dSOC','#2171b5',-0.18),('dSIC','#6a51a3',0.18)]):
    v=[T[t][key]['mean'] for t in top]; e=np.array([[T[t][key]['mean']-T[t][key]['p05'],T[t][key]['p95']-T[t][key]['mean']] for t in top]).T
    c.bar(x+off,v,0.36,color=col,yerr=e,error_kw=dict(lw=0.5,capsize=1.2),label=key[1:].replace('d','')+' change' if False else ('ΔSOC' if key=='dSOC' else 'ΔSIC'))
  c.axhline(0,c='k',lw=0.4); c.set_xticks(x); c.set_xticklabels([t.replace('>','→') for t in top]); c.set_ylabel('Eq. change 0–200 cm on\ntransition area (Pg C)'); c.legend(fontsize=6)
  c2=c.twinx(); c2.plot(x,[T[t]['area_Mkm2'] for t in top],'D',ms=3,color='0.3'); c2.set_ylabel('Area (Mkm², ◆)',fontsize=6); c2.spines['right'].set_visible(True); c2.tick_params(labelsize=5.5); c2.set_ylim(0,None)
  lt(c,'c',-0.12)
  d=fig.add_axes([0.74,0.07,0.24,0.33]); 
  for k_,s in enumerate(SSP):
    TT=S['transitions_main'][s]; a_=TT['_any_main_change_Mkm2']; so=sum(v['map_dSOC'] for kk,v in TT.items() if not kk.startswith('_')); si=sum(v['map_dSIC'] for kk,v in TT.items() if not kk.startswith('_'))
    d.bar(k_-0.18,so,0.36,color='#2171b5'); d.bar(k_+0.18,si,0.36,color='#6a51a3'); d.text(k_,max(si,0)+3,f'{a_:.0f}',ha='center',fontsize=5,color='0.3')
    log[f'S21_{s}']=dict(area=a_,dsoc=so,dsic=si)
  d.axhline(0,c='k',lw=0.4); d.set_xticks(range(4)); d.set_xticklabels([LBL[s].replace('SSP','') for s in SSP],fontsize=5.5,rotation=30); d.set_ylabel('Eq. change on shifted land (Pg C)')
  d.text(0.02,0.98,'numbers: shifted\narea (Mkm²)',transform=d.transAxes,fontsize=5,va='top'); lt(d,'d',-0.3)
  save(fig,FS+'FigS21_koppen_transitions')

def S22():  # training data coverage
  fig=plt.figure(figsize=(7.2,5.6))
  bins=[0.5,1.5,3.5,10.5,30.5,100.5,1e6]; cols=['#fff7bc','#fee391','#fec44f','#fe9929','#d95f0e','#993404']
  def dmap(ax,a,lab):
    b=np.digitize(a,bins)-1; img=np.zeros((180,360,4))
    for i,c in enumerate(cols): img[b==i]=mpl.colors.to_rgba(c)
    img[a<0.5]=(0,0,0,0)
    ax.imshow(img,origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),interpolation='nearest',zorder=1,regrid_shape=1000)
    pos=ax.get_position(); c=fig.add_axes([pos.x0+pos.width*0.22,pos.y0-0.015,pos.width*0.55,0.012]); n=len(cols)
    for i,col in enumerate(cols): c.add_patch(Rectangle((i,0),1,1,color=col))
    c.add_patch(Rectangle((n+0.35,0),1,1,color=GREY)); c.text(n+1.5,0.5,'No profiles',va='center',fontsize=6); c.set_xlim(0,n+1.4); c.set_ylim(0,1); c.set_yticks([])
    c.set_xticks(np.arange(n)+0.5); c.set_xticklabels(['1','2–3','4–10','11–30','31–100','>100'],fontsize=5); [s.set_visible(False) for s in c.spines.values()]; c.tick_params(length=0,pad=1)
    c.text(-0.3,0.5,lab,ha='right',va='center',fontsize=6.5)
  for k,(key,lab) in enumerate([('soc_0_30','SOC 0–30 cm\nprofiles per 1°'),('sic_100_200','SIC 100–200 cm\nprofiles per 1°')]):
    ax=mapax(fig,[0.0+0.5*k,0.56,0.5,0.4]); dmap(ax,PD[key],lab); letter(fig,ax,'ab'[k],0.02)
  c=fig.add_axes([0.08,0.08,0.52,0.36]); C=PT['counts']; regs=CONT; x=np.arange(len(regs)); w=0.13
  for j,(var,cs) in enumerate([('SOC',SOCB),('SIC',SICB)]):
    for l,lay in enumerate(['0_30','30_100','100_200']):
      c.bar(x+(j*3+l-2.5)*w,[C[f'{var}_{lay}'][r]/1000 for r in regs],w,color=cs[l],label=f'{var} {DL[l]}')
  c.set_xticks(x); c.set_xticklabels(['Asia','Europe','N. America','S. America','Africa','Oceania']); c.set_ylabel('Profiles (thousands)'); c.legend(fontsize=5,ncol=2,handlelength=1); lt(c,'c',-0.1)
  d=fig.add_axes([0.72,0.08,0.25,0.36]); L=S['lat_profiles']; la=np.array(L['lat']); A=np.array(L['area_Mkm2'])
  # aggregate to 5-degree bands
  e=np.arange(-60,90,5); ar=np.histogram(la,e,weights=A)[0]; ar=ar/ar.sum()*100
  for key,col,lab in [('soc_0_30','#2171b5','SOC 0–30'),('sic_100_200','#6a51a3','SIC 100–200')]:
    lc=np.array(PT[f'latcount_{key}']); lv=np.arange(-90,90); h=np.histogram(lv,e,weights=lc[:len(lv)])[0]; h=h/h.sum()*100
    d.plot(h,e[:-1]+2.5,c=col,lw=1,label=lab)
  d.fill_betweenx(e[:-1]+2.5,0,ar,color=GREY,lw=0,label='Land area'); d.set_ylim(-56,84); d.set_xlabel('Share per 5° band (%)'); d.set_ylabel('Latitude (°)'); d.legend(fontsize=5,loc='lower right'); lt(d,'d',-0.25)
  log['S22_cells']={k:PT[f'n_cells1deg_{k}'] for k in ['soc_0_30','sic_0_30','soc_100_200','sic_100_200']}
  save(fig,FS+'FigS22_training_coverage')

for n in (sys.argv[1:] or ['S15','S16','S17','S18','S19','S20','S21','S22']):
  try: globals()[n](); print('ok',n,flush=True)
  except Exception as e: import traceback; traceback.print_exc(); print('FAIL',n,flush=True)
old=json.load(open(R+'/out/v13/fig_numbers_v13.json')) if __import__('os').path.exists(R+'/out/v13/fig_numbers_v13.json') else {}
old.update(log); json.dump(old,open(R+'/out/v13/fig_numbers_v13.json','w'),indent=1,default=float)
