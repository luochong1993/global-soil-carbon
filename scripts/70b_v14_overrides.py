# v14 overrides (exec'd after 53b inside the 53_v10_figs environment). Inputs unchanged (out/v10/ens_maps.npz).
_dens0=dens
def dens(ax,data,labels,colors,xlabel,log=False,inset=None):
  _dens0(ax,data,labels,colors,xlabel,log,inset)
  if xlabel.startswith('ΔpH'): ax.legend(fontsize=6,loc='upper left')
def fig5():
  a_=EM['dsoc_0_200_585'].astype(float); b_=EM['dsic_0_200_585'].astype(float)
  fig=plt.figure(figsize=(7.2,5.0))
  ax=mapax(fig,[0.0,0.38,1.0,0.6])
  cols={(1,1):'#3b4994',(1,0):'#5ac8c8',(0,1):'#be64ac',(0,0):'#d7301f'}
  ok=np.isfinite(a_)&np.isfinite(b_); q=np.full(len(a_),-1)
  for (i,j) in cols: q[ok&((a_>0)==bool(i))&((b_>0)==bool(j))]=i*2+j
  rgb=np.zeros((len(a_),4))
  for (i,j),c in cols.items(): rgb[q==i*2+j]=mpl.colors.to_rgba(c)
  img=np.zeros((H,W,4))
  for k in range(4): img[...,k][mask]=rgb[:,k]
  ax.imshow(img,origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),interpolation='nearest',zorder=1,regrid_shape=1400)
  L=ax.inset_axes([0.03,0.12,0.09,0.18])
  for (i,j),c in cols.items(): L.add_patch(Rectangle((i,j),1,1,color=c))
  L.set_xlim(0,2); L.set_ylim(0,2); L.set_xticks([0.5,1.5]); L.set_yticks([0.5,1.5]); L.set_xticklabels(['−','+'],fontsize=5); L.set_yticklabels(['−','+'],fontsize=5)
  L.set_xlabel('ΔSOC',fontsize=5,labelpad=0); L.set_ylabel('ΔSIC',fontsize=5,labelpad=0); L.tick_params(length=0,pad=1)
  tot=area[ok].sum(); order=[(0,1),(0,0),(1,1),(1,0)]; names=['SOC−\nSIC+','SOC−\nSIC−','SOC+\nSIC+','SOC+\nSIC−']
  p=[area[q==i*2+j].sum()/tot*100 for (i,j) in order]
  B=ax.inset_axes([0.18,0.13,0.13,0.25]); B.set_zorder(10); B.bar(range(4),p,color=[cols[o] for o in order],width=0.75)
  for k,v in enumerate(p): B.text(k,v+1,f'{v:.0f}',ha='center',fontsize=5,fontweight='bold')
  B.set_xticks(range(4)); B.set_xticklabels(names,fontsize=4.2); B.tick_params(axis='x',length=0,pad=1)
  B.set_ylabel(f'% of mapped land\n({tot/1e8:.1f} Mkm$^2$)',fontsize=4.8); B.tick_params(axis='y',labelsize=5); B.patch.set_alpha(0); B.set_ylim(0,max(p)*1.18)
  log['fig5_quadrants_pct_of_mapped_land']=dict(zip(['tradeoff','both_loss','both_gain','SOCgain_SICloss'],p)); log['fig5_land_Mkm2']=tot/1e8
  letter(fig,ax,'a',0.03)
  s1,nm,ct=by_country(a_); s2,_,_=by_country(b_); df=pd.DataFrame(dict(n=nm,c=ct,a=s1,b=s2))[1:]; df=df[(df.c!='')&((df.a.abs()+df.b.abs())>0.05)]
  c=fig.add_axes([0.08,0.06,0.38,0.3]); c.scatter(df.a,df.b,s=9,c=['#3b4994' if (x>0 and y>0) else '#5ac8c8' if x>0 else '#be64ac' if y>0 else '#d7301f' for x,y in zip(df.a,df.b)],edgecolor='k',lw=0.2)
  c.axhline(0,ls='--',c='0.5',lw=0.6); c.axvline(0,ls='--',c='0.5',lw=0.6); c.set_xscale('symlog',linthresh=1); c.set_yscale('symlog',linthresh=1); [g([-10,-1,0,1,10]) for g in (c.set_xticks,c.set_yticks)]; c.set_xticklabels(['−10','−1','0','1','10']); c.set_yticklabels(['−10','−1','0','1','10'])
  short={'United States of America':'United States'}
  top=df.reindex(df.a.abs().sort_values().index[-6:]).sort_values('b',ascending=False)
  k=0
  for t in top.itertuples():
    if t.b>1: xy=(0.20,0.97-0.075*k); k+=1
    else: xy=(0.20,0.18)
    c.annotate(short.get(t.n,t.n),(t.a,t.b),xytext=xy,textcoords='axes fraction',fontsize=4.8,va='center',arrowprops=dict(arrowstyle='-',lw=0.3,color='0.5',shrinkA=0,shrinkB=1.5))
  for (qx,qy),(px,py) in {(1,1):(0.97,0.95),(0,1):(0.03,0.95),(0,0):(0.03,0.05),(1,0):(0.97,0.05)}.items():
    n=((df.a>0)==qx)&((df.b>0)==qy); c.text(px,py,f'{n.mean()*100:.0f}%',transform=c.transAxes,ha='right' if qx else 'left',va='top' if qy else 'bottom',fontweight='bold')
  c.set_xlabel('Country ΔSOC (Pg C)'); c.set_ylabel('Country ΔSIC (Pg C)'); letter(fig,c,'b',-0.06)
  d=fig.add_axes([0.58,0.06,0.38,0.3]); ids,nm_,ct_=countries()
  M=np.array([[(v[ct_[ids]==cc]*area[ct_[ids]==cc]).sum()*1e-9 for v in (a_,b_)] for cc in CONT])
  x=np.arange(len(CONT)); d.bar(x-0.18,M[:,0],0.36,color='#2171b5',label='ΔSOC'); d.bar(x+0.18,M[:,1],0.36,color='#c0262c',label='ΔSIC'); d.axhline(0,c='k',lw=0.4)
  d.set_xticks(x); d.set_xticklabels(CONT); d.set_ylabel('Change by continent (Pg C)'); d.legend(fontsize=6); letter(fig,d,'c',-0.06)
  log['fig5_continent']={cc:list(map(float,M[i])) for i,cc in enumerate(CONT)}
  save(fig,FM+'Fig5_bivariate_SOC_SIC')
_s53b=open(R+'/scripts/53b_v10_overrides.py').read(); _i=_s53b.index('def fig4'); _j=_s53b.index('def S7')
exec(_s53b[_i:_j].replace("letter(fig,c,'e',-0.06)","letter(fig,c,'e',-0.1)"))
