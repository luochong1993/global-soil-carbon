import numpy as np, pandas as pd, rasterio, json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.colors as mc
D='/workspace/soil_global/data'; O='/workspace/soil_global/out'; F='/workspace/soil_global/figs'
plt.rcParams.update({'font.size':8,'font.family':['Noto Sans CJK SC','Noto Serif CJK SC','DejaVu Sans'],'axes.unicode_minus':False})
mask=np.load(f'{O}/mask.npy'); H,W=mask.shape; lat=np.linspace(90,-90,H+1)[:-1]-90/H
area_ha=(111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100
kg0=rasterio.open(f'{D}/grids/kg_present.tif').read(1)
grp=lambda k: np.select([k==0,k<=3,k<=7,k<=16,k<=28],[0,1,2,3,4],5)
G=['A 热带','B 干旱','C 温带','D 冷温带','E 极地']
P0=dict(np.load(f'{O}/pred_present.npz'))
# coarse fragments: per-zone median of observed (model CV R2<0)
pts=pd.read_csv(f'{D}/points_topsoil.csv'); r_=((90-pts.Y)*6).astype(int).clip(0,H-1); c_=((pts.X+180)*6).astype(int).clip(0,W-1)
pts['kg']=kg0[r_,c_]; cfz=pts.groupby('kg').cfvo.median().reindex(range(31)).fillna(pts.cfvo.median()).values
CF=cfz[kg0]
def stock(conc,bd): return conc*bd*(1-CF/100)*3.0  # Mg C/ha, 0-30 cm
SOC0=stock(P0['soc'],P0['bd']); SIC0=stock(P0['sic'],P0['bd'])
tot=lambda s,m=mask: float(np.nansum((s*area_ha)[m])*1e-9)
R={'present':{'SOC_Pg':tot(SOC0),'SIC_Pg':tot(SIC0)}}
# zone envelopes (5-95%) of present predictions, SIC share by zone
zone=[]
for z in range(1,30):
    m=mask&(kg0==z)
    if m.sum()<50: continue
    s,i=tot(SOC0,m),tot(SIC0,m)
    zone.append(dict(zone=z,area_Mkm2=float(area_ha[m].sum()/1e8),SOC_Pg=s,SIC_Pg=i,SIC_share=i/(s+i),
      pH_p5=float(np.nanpercentile(P0['phaq'][m],5)),pH_p95=float(np.nanpercentile(P0['phaq'][m],95)),
      SIC_p5=float(np.nanpercentile(P0['sic'][m],5)),SIC_p95=float(np.nanpercentile(P0['sic'][m],95)),
      SOC_p5=float(np.nanpercentile(P0['soc'][m],5)),SOC_p95=float(np.nanpercentile(P0['soc'][m],95))))
ZN=['','Af','Am','Aw','BWh','BWk','BSh','BSk','Csa','Csb','Csc','Cwa','Cwb','Cwc','Cfa','Cfb','Cfc','Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','Dfa','Dfb','Dfc','Dfd','ET','EF']
zt=pd.DataFrame(zone); zt['name']=zt.zone.map(lambda z:ZN[z]); zt.to_csv(f'{O}/zone_envelopes.csv',index=False)
env={r.zone:r for r in zt.itertuples()}
scen=[f'ssp{s}_{p}' for s in (126,245,370,585) for p in ('2041-2060','2081-2100')]
rows=[]; keep={}
for sc in scen:
    kf=rasterio.open(f'{D}/grids/kg_{sc}.tif').read(1); Pf=np.load(f'{O}/pred_{sc}.npz')
    SOCf=stock(Pf['soc'],P0['bd']); SICf=stock(Pf['sic'],P0['bd'])
    sh=mask&(kf!=kg0)&(kf>0)
    # mismatch: present value outside the new zone's present-day 5-95% envelope
    def mis(var,a):
        lo=np.full(31,-np.inf); hi=np.full(31,np.inf)
        for z,e in env.items(): lo[z]=getattr(e,var+'_p5'); hi[z]=getattr(e,var+'_p95')
        return sh&((a<lo[kf])|(a>hi[kf]))
    mS,mP,mO=mis('SIC',P0['sic']),mis('pH',P0['phaq']),mis('SOC',P0['soc'])
    dSOC=SOCf-SOC0; dSIC=SICf-SIC0
    gtrans=pd.crosstab(grp(kg0[mask]),grp(kf[mask]),values=area_ha[mask]/1e8,aggfunc='sum').fillna(0)
    gtrans.to_csv(f'{O}/transition_{sc}.csv')
    colos=mask&(dSOC<0)&(dSIC<0); toff=mask&((dSOC>0)&(dSIC<0)|(dSOC<0)&(dSIC>0))
    rows.append(dict(scenario=sc,shift_area_Mkm2=float(area_ha[sh].sum()/1e8),shift_frac=float(area_ha[sh].sum()/area_ha[mask].sum()),
      mismatch_SIC_Mkm2=float(area_ha[mS].sum()/1e8),mismatch_pH_Mkm2=float(area_ha[mP].sum()/1e8),mismatch_SOC_Mkm2=float(area_ha[mO].sum()/1e8),
      SIC_stock_in_SICmismatch_Pg=tot(SIC0,mS),SOC_stock_in_SOCmismatch_Pg=tot(SOC0,mO),
      SOC_future_Pg=tot(SOCf),SIC_future_Pg=tot(SICf),dSOC_Pg=tot(dSOC),dSIC_Pg=tot(dSIC),
      SIC_loss_in_shift_Pg=tot(np.minimum(dSIC,0),sh),SOC_loss_in_shift_Pg=tot(np.minimum(dSOC,0),sh),
      coloss_Mkm2=float(area_ha[colos].sum()/1e8),tradeoff_Mkm2=float(area_ha[toff].sum()/1e8),
      dpH_mean=float(np.nanmean((Pf['phaq']-P0['phaq'])[mask]))))
    keep[sc]=(kf,dSOC,dSIC,Pf['phaq']-P0['phaq'],mS)
st=pd.DataFrame(rows); st.to_csv(f'{O}/scenario_summary.csv',index=False)
R['scenarios']=rows; json.dump(R,open(f'{O}/results.json','w'),indent=1)
print(json.dumps(R['present'])); print(st.round(3).T.to_string())
print(zt[['name','area_Mkm2','SOC_Pg','SIC_Pg','SIC_share']].round(2).to_string())
# ---------- figures
ext=[-180,180,-90,90]; sl=slice(0,int(150*6))  # 90N-60S
def mp(ax,a,cmap,norm=None,title='',cb=''):
    a=np.where(mask,a,np.nan)[sl]; im=ax.imshow(a,extent=[-180,180,-60,90],cmap=cmap,norm=norm,interpolation='nearest')
    ax.set_facecolor('#f0f0f0'); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title,loc='left',fontweight='bold')
    plt.colorbar(im,ax=ax,orientation='horizontal',fraction=0.05,pad=0.03,label=cb); return im
# Fig1 present maps
fig,ax=plt.subplots(2,2,figsize=(7.2,4.6),constrained_layout=True)
mp(ax[0,0],SOC0,'YlGn',mc.LogNorm(5,300),'a  SOC 储量 0–30 cm','Mg C ha$^{-1}$')
mp(ax[0,1],SIC0,'OrRd',mc.LogNorm(1,200),'b  SIC 储量 0–30 cm','Mg C ha$^{-1}$')
mp(ax[1,0],P0['phaq'],'RdYlBu_r',mc.Normalize(4,9),'c  pH(H$_2$O)','')
mp(ax[1,1],SIC0/(SIC0+SOC0),'PuOr_r',mc.Normalize(0,1),'d  SIC 占总碳比例','')
fig.savefig(f'{F}/fig1_present_maps.png',dpi=300); plt.close()
# Fig2 Köppen present/future + shift
cmap30=plt.get_cmap('tab20b',30)
fig,ax=plt.subplots(1,3,figsize=(7.2,2.3),constrained_layout=True)
kf=keep['ssp585_2081-2100'][0]
for a_,k,t in [(ax[0],kg0,'a  KG 1970–2000 (WorldClim)'),(ax[1],kf,'b  KG 2081–2100 SSP5-8.5')]:
    a_.imshow(np.where(mask,k,np.nan)[sl],extent=[-180,180,-60,90],cmap=cmap30,vmin=0.5,vmax=30.5,interpolation='nearest'); a_.set_xticks([]);a_.set_yticks([]);a_.set_title(t,loc='left',fontweight='bold')
mp(ax[2],np.where(kf!=kg0,1.,0.),mc.ListedColormap(['#dddddd','#c0392b']),mc.Normalize(0,1),'c  气候带发生迁移','')
fig.savefig(f'{F}/fig2_koppen_shift.png',dpi=300); plt.close()
# Fig3 bivariate dSOC x dSIC (SSP2-4.5 & 5-8.5 2081-2100)
bc=mc.ListedColormap(['#b2182b','#ef8a62','#67a9cf','#2166ac'])
fig,ax=plt.subplots(1,2,figsize=(7.2,2.6),constrained_layout=True)
for a_,sc in zip(ax,['ssp245_2081-2100','ssp585_2081-2100']):
    _,dO,dI,_,_=keep[sc]; cls=np.where((dO<0)&(dI<0),0,np.where((dO>=0)&(dI<0),1,np.where((dO<0)&(dI>=0),2,3))).astype(float)
    a_.imshow(np.where(mask,cls,np.nan)[sl],extent=[-180,180,-60,90],cmap=bc,vmin=-.5,vmax=3.5,interpolation='nearest');a_.set_xticks([]);a_.set_yticks([]);a_.set_title(sc.replace('_',' '),loc='left',fontweight='bold')
import matplotlib.patches as mpa
fig.legend(handles=[mpa.Patch(color=c,label=l) for c,l in zip(bc.colors,['SOC↓ SIC↓ 共损','SOC↑ SIC↓ 权衡','SOC↓ SIC↑ 权衡','SOC↑ SIC↑ 共增'])],loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,-.08))
fig.savefig(f'{F}/fig3_bivariate_dSOC_dSIC.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig4 SHAP
names=json.load(open(f'{O}/names.json'))
fig,ax=plt.subplots(1,3,figsize=(7.2,2.8),constrained_layout=True)
for a_,t in zip(ax,['soc','sic','phaq']):
    sv=np.abs(np.load(f'{O}/shap_{t}.npy')).mean(0); o=np.argsort(sv)[-10:]
    a_.barh([names[i] for i in o],sv[o],color='#3b6ea8'); a_.set_title({'soc':'a  SOC','sic':'b  SIC','phaq':'c  pH'}[t],loc='left',fontweight='bold'); a_.set_xlabel('mean |SHAP|')
fig.savefig(f'{F}/fig4_shap.png',dpi=300); plt.close()
# Fig5 scenario bars + SIC share by zone group
fig,ax=plt.subplots(1,3,figsize=(7.2,2.6),constrained_layout=True)
x=np.arange(len(st)); ax[0].bar(x-.2,st.dSOC_Pg,.4,label='ΔSOC',color='#1b7837');ax[0].bar(x+.2,st.dSIC_Pg,.4,label='ΔSIC',color='#b35806')
ax[0].set_xticks(x,[s[3:6]+('-M' if '2041' in s else '-L') for s in st.scenario],fontsize=6,rotation=45);ax[0].axhline(0,c='k',lw=.5);ax[0].set_ylabel('Pg C');ax[0].legend(frameon=False);ax[0].set_title('a  平衡态碳储量变化',loc='left',fontweight='bold')
ax[1].bar(x,st.mismatch_SIC_Mkm2,color='#b35806',label='SIC');ax[1].bar(x,st.mismatch_pH_Mkm2,bottom=st.mismatch_SIC_Mkm2,color='#4393c3',label='pH')
ax[1].set_xticks(x,[s[3:6]+('-M' if '2041' in s else '-L') for s in st.scenario],fontsize=6,rotation=45);ax[1].set_ylabel('10$^6$ km$^2$');ax[1].legend(frameon=False);ax[1].set_title('b  错配面积',loc='left',fontweight='bold')
zg=zt.assign(g=zt.zone.map(lambda z:G[int(grp(np.array(z)))-1])).groupby('g')[['SOC_Pg','SIC_Pg']].sum()
ax[2].bar(zg.index,zg.SOC_Pg,color='#1b7837',label='SOC');ax[2].bar(zg.index,zg.SIC_Pg,bottom=zg.SOC_Pg,color='#b35806',label='SIC')
for i,(s,c) in enumerate(zip(zg.SOC_Pg,zg.SIC_Pg)): ax[2].text(i,s+c,f'{c/(s+c):.0%}',ha='center',va='bottom',fontsize=6)
ax[2].set_ylabel('Pg C');ax[2].tick_params(axis='x',labelsize=6,rotation=30);ax[2].legend(frameon=False);ax[2].set_title('c  各气候大区 SIC 占比',loc='left',fontweight='bold')
fig.savefig(f'{F}/fig5_scenarios_zones.png',dpi=300); plt.close()
# Fig S1 year distribution
yd=pd.read_csv(f'{O}/year_distribution.csv',index_col=0); yd.plot.bar(figsize=(5,2.6)); plt.ylabel('剖面数'); plt.tight_layout(); plt.savefig(f'{F}/figS1_year_distribution.png',dpi=300); plt.close()
