import numpy as np, pandas as pd, json, glob, os, rasterio, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.colors as mc, matplotlib.patches as mpa
from rasterio.warp import reproject, Resampling
D='/workspace/soil_global/data'; O='/workspace/soil_global/out/v2'; F='/workspace/soil_global/figs/v2'+os.environ.get('TAG',''); os.makedirs(F,exist_ok=True)
plt.rcParams.update({'font.size':7,'font.family':['Noto Sans CJK JP','DejaVu Sans'],'axes.unicode_minus':False,'axes.linewidth':0.5,'xtick.major.width':0.5,'ytick.major.width':0.5})
mask=np.load(f'{O}/mask.npy'); aoa=np.load(f'{O}/aoa.npy'); H,W=mask.shape; lat=np.linspace(90,-90,H+1)[:-1]-90/H
area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
KG=dict(np.load(f'{O}/kg_beck.npz')); kg0=KG['1991-2020'][mask]; aoam=aoa[mask]
_p=pd.read_csv(f'{D}/points_topsoil.csv'); _r=((90-_p.Y)*6).astype(int).clip(0,H-1); _c=((_p.X+180)*6).astype(int).clip(0,W-1)
_s=pd.Series(_p.cfvo.values,index=KG['1991-2020'][_r,_c]).groupby(level=0).median()
cfz=np.full(31,np.nanmedian(_p.cfvo)); cfz[_s.index.values]=_s.values; CF=cfz[kg0]
grp=lambda k: np.select([k==0,k<=3,k<=7,k<=16,k<=28],[0,1,2,3,4],5)
GN=['A','B','C','D','E']
boots=[f for f in sorted(glob.glob(f'{O}/boot*_present.npz')) if os.path.exists(f.replace('present','future'))]; NB=len(boots)
P=[dict(np.load(f)) for f in boots]
SD=float(os.environ.get('SOC_DIV',1.0)); TAG=os.environ.get('TAG','')
for b in P: b['soc']=np.clip((b['soc']+1)/SD-1,0,None)
stk=lambda c,bd: c*bd*(1-CF/100)*3.0
Pg=lambda s,m=None: float(np.nansum(s*area if m is None else (s*area)[m])*1e-9)
q=lambda a: (float(np.mean(a)),float(np.percentile(a,5)),float(np.percentile(a,95)))
R={'n_boot':NB}
SOC0=[stk(b['soc'],b['bd']) for b in P]; SIC0=[stk(b['sic'],b['bd']) for b in P]
R['present']={'SOC_Pg':q([Pg(s) for s in SOC0]),'SIC_Pg':q([Pg(s) for s in SIC0]),
  'SOC_Pg_inAOA':q([Pg(s,aoam) for s in SOC0]),'SIC_Pg_inAOA':q([Pg(s,aoam) for s in SIC0]),'AOA_area_frac':float((area*aoam).sum()/area.sum())}
# SoilGrids OCS 0-30 comparison on the same mask
ref=rasterio.open(f'{D}/grids/kg_present.tif')
with rasterio.open(f'{D}/sg_ocs030.tif') as r:
    a=r.read(1).astype('float32'); a[(a==r.nodata)|(a<0)]=np.nan; sg=np.full((H,W),np.nan,'float32')
    reproject(a,sg,src_transform=r.transform,src_crs=r.crs,dst_transform=ref.transform,dst_crs=ref.crs,resampling=Resampling.average,src_nodata=np.nan,dst_nodata=np.nan)
sgm=sg[mask]; R['present']['SoilGrids_OCS030_Pg_same_mask']=Pg(np.nan_to_num(sgm))
# zone stats + envelopes per boot
zrows=[]
for z in range(1,30):
    m=kg0==z
    if m.sum()<30: continue
    so=[Pg(s,m) for s in SOC0]; si=[Pg(s,m) for s in SIC0]; sh=[b/max(a+b,1e-9) for a,b in zip(so,si)]
    zrows.append(dict(zone=z,area_Mkm2=float(area[m].sum()/1e8),SOC=q(so),SIC=q(si),SIC_share=q(sh)))
ZN=['','Af','Am','Aw','BWh','BWk','BSh','BSk','Csa','Csb','Csc','Cwa','Cwb','Cwc','Cfa','Cfb','Cfc','Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','Dfa','Dfb','Dfc','Dfd','ET','EF']
R['zones']=[dict(r,name=ZN[r['zone']]) for r in zrows]
gro={}
for gi,gname in enumerate(GN,1):
    m=grp(kg0)==gi; so=[Pg(s,m) for s in SOC0]; si=[Pg(s,m) for s in SIC0]
    gro[gname]=dict(SOC=q(so),SIC=q(si),share=q([b/max(a+b,1e-9) for a,b in zip(so,si)]))
R['groups']=gro
def env(vals,lo=5,hi=95):
    L=np.full(31,-np.inf); U=np.full(31,np.inf)
    for z in range(1,30):
        m=kg0==z
        if m.sum()>=30: L[z],U[z]=np.nanpercentile(vals[m],[lo,hi])
    return L,U
# futures
BP={'2041-2060':'2041-2070','2081-2100':'2071-2099'}
FB=[np.load(f.replace('present','future')) for f in boots]
keys=list(FB[0].files); GCMS=sorted(set(k.split('|')[0] for k in keys))
R['gcms']=GCMS
rows=[]; maps={}
for s in ('126','245','370','585'):
  for pr in ('2041-2060','2081-2100'):
    kf=KG[f'{BP[pr]}-ssp{s}'][mask]; shf=(kf!=kg0)&(kf>0)
    mis={'SIC':[],'pH':[],'SOC':[]}; atrisk=[]; dSOC=[]; dSIC=[]; lossSIC=[]; lossSOC=[]; dpH=[]
    ens_dO=[]; ens_dI=[]
    for b in range(NB):
        pb=P[b]
        for var,vals in [('SIC',pb['sic']),('pH',pb['ph']),('SOC',pb['soc'])]:
            L,U=env(vals); mm=shf&((vals<L[kf])|(vals>U[kf])); mis[var].append(float(area[mm].sum()/1e8))
            if var=='SIC': atrisk.append(Pg(SIC0[b],mm))
        gO=[];gI=[]
        for g in GCMS:
            k=f'{g}|{s}|{pr}'
            if k not in FB[b].files: continue
            fu=FB[b][k].astype('float32'); fO=stk(np.clip((fu[2]+1)/SD-1,0,None),pb['bd']); fI=stk(fu[1],pb['bd'])
            dO=fO-SOC0[b]; dI=fI-SIC0[b]
            dSOC.append(Pg(dO)); dSIC.append(Pg(dI)); lossSIC.append(Pg(np.minimum(dI,0),shf)); lossSOC.append(Pg(np.minimum(dO,0),shf))
            dpH.append(float(np.average(fu[0]-pb['ph'],weights=area)))
            gO.append(dO); gI.append(dI)
        ens_dO.append(np.array(gO)); ens_dI.append(np.array(gI))
    eO=np.mean(ens_dO,0); eI=np.mean(ens_dI,0)  # (G,N) boot-mean per GCM
    mO=eO.mean(0); mI=eI.mean(0)
    agO=(np.sign(eO)==np.sign(mO)).mean(0); agI=(np.sign(eI)==np.sign(mI)).mean(0)
    robust=(agO>=5/6)&(agI>=5/6)
    colos=(mO<0)&(mI<0); toff=((mO>0)&(mI<0))|((mO<0)&(mI>0))
    rows.append(dict(scenario=f'SSP{s[0]}-{s[1]}.{s[2]} {pr}',beck_period=BP[pr],n_members=len(dSOC),
      shift_Mkm2=float(area[shf].sum()/1e8),shift_frac=float(area[shf].sum()/area.sum()),
      mis_SIC=q(mis['SIC']),mis_pH=q(mis['pH']),mis_SOC=q(mis['SOC']),SIC_in_mis=q(atrisk),
      dSOC=q(dSOC),dSIC=q(dSIC),SIC_loss_shift=q(lossSIC),SOC_loss_shift=q(lossSOC),dpH=q(dpH),
      coloss_Mkm2=float(area[colos].sum()/1e8),coloss_robust_Mkm2=float(area[colos&robust].sum()/1e8),
      tradeoff_Mkm2=float(area[toff].sum()/1e8),tradeoff_robust_Mkm2=float(area[toff&robust].sum()/1e8),
      agree_SOC_frac=float((area*(agO>=5/6)).sum()/area.sum()),agree_SIC_frac=float((area*(agI>=5/6)).sum()/area.sum())))
    maps[(s,pr)]=(kf,shf,mO,mI,robust)
    print(rows[-1]['scenario'],flush=True)
R['scenarios']=rows
tm=pd.crosstab(pd.Series(grp(kg0),name='present'),pd.Series(grp(KG['2071-2099-ssp585'][mask]),name='ssp585_2071_2099'),values=area/1e8,aggfunc='sum').fillna(0)
tm.to_csv(f'{O}/transition_beck_ssp585_2071-2099.csv'); R['transition_ssp585_2071_2099']=tm.round(2).to_dict()
# LUCAS 2018 independent (0-20 cm SOC stock, Zenodo 10211884, not in WoSIS)
lu=pd.read_csv(f'{D}/lucas2018_socs.csv'); lu.columns=[c.strip() for c in lu.columns]
lu=lu[pd.to_numeric(lu['SOCS (kg cm-2)'],errors='coerce').notna()]
obs=pd.to_numeric(lu['SOCS (kg cm-2)'])*10  # kg m-2 -> Mg ha-1 (header unit read as kg m-2)
full=lambda v: (lambda a:(a.__setitem__(mask,v),a)[1])(np.full((H,W),np.nan,'float32'))
socS=full(np.mean(SOC0,0)); rr=((90-lu.GPS_LAT)*6).astype(int).clip(0,H-1); cc=((lu.GPS_LONG+180)*6).astype(int).clip(0,W-1)
pr_=socS[rr,cc]*20/30; sgp=sg[rr,cc]*20/30; ok=np.isfinite(pr_)&np.isfinite(obs.values)&np.isfinite(sgp)
from sklearn.metrics import r2_score
def mm_(o,pp): return dict(n=int(len(o)),r2=float(r2_score(o,pp)),rmse=float(np.sqrt(np.mean((pp-o)**2))),bias=float(np.mean(pp-o)),r_pearson=float(np.corrcoef(o,pp)[0,1]),median_obs=float(np.median(o)),median_pred=float(np.median(pp)))
R['LUCAS2018']={'this_model':mm_(obs.values[ok],pr_[ok]),'SoilGrids':mm_(obs.values[ok],sgp[ok])}
json.dump(R,open(f'{O}/results_v2'+TAG+'.json','w'),indent=1,ensure_ascii=False)
print(json.dumps({k:R[k] for k in ['present','LUCAS2018','groups']},indent=1,ensure_ascii=False))
# ================= FIGURES
sl=slice(0,150*6); ext=[-180,180,-60,90]
def full2(v,fill=np.nan): a=np.full((H,W),fill,'float32'); a[mask]=v; return a[sl]
def ax_map(ax,a,cmap,norm,lab,cbl='',hatch_out=True):
    ax.imshow(np.where(np.isnan(a),np.nan,1)[...]*0+0.0,extent=ext,cmap=mc.ListedColormap(['#e6e6e6']),interpolation='nearest')
    im=ax.imshow(a,extent=ext,cmap=cmap,norm=norm,interpolation='nearest')
    if hatch_out:
        out=np.where(~aoa[sl]&mask[sl],1.0,np.nan); ax.imshow(out,extent=ext,cmap=mc.ListedColormap(['#9e9e9e']),alpha=0.65,interpolation='nearest')
    ax.set_xlim(-180,180); ax.set_ylim(-60,85); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.text(0.0,1.02,lab,transform=ax.transAxes,fontweight='bold',fontsize=8,va='bottom')
    if cbl is not None:
        cb=plt.colorbar(im,ax=ax,orientation='horizontal',fraction=0.045,pad=0.02,aspect=35); cb.set_label(cbl,fontsize=6); cb.ax.tick_params(labelsize=6,width=.4); cb.outline.set_linewidth(.4)
mS=np.mean(SOC0,0); mI=np.mean(SIC0,0); mph=np.mean([b['ph'] for b in P],0)
fig,ax=plt.subplots(2,2,figsize=(7.1,4.3),constrained_layout=True)
ax_map(ax[0,0],full2(mS),'YlGn',mc.LogNorm(5,250),'a  SOC 储量（0–30 cm）','Mg C ha⁻¹')
ax_map(ax[0,1],full2(mI),'OrRd',mc.LogNorm(0.5,150),'b  SIC 储量（0–30 cm）','Mg C ha⁻¹')
ax_map(ax[1,0],full2(mph),'RdYlBu_r',mc.Normalize(4,9),'c  pH(H₂O)','')
ax_map(ax[1,1],full2(mI/(mI+mS)),'PuOr_r',mc.Normalize(0,1),'d  SIC/(SOC+SIC)','')
fig.savefig(f'{F}/Fig1_present_carbon_pH.png',dpi=300); plt.close()
# Fig2 Beck zones + mismatch
leg=['#0000FF','#0078FF','#46AAFA','#FF0000','#FF9696','#F5A500','#FFDC64','#FFFF00','#C8C800','#969600','#96FF96','#64C864','#329632','#C8FF50','#64FF50','#32C800','#FF00FF','#C800C8','#963296','#966496','#AAAFFF','#5A78DC','#4B50B4','#320087','#00FFFF','#37C8FF','#007D7D','#00465F','#B2B2B2','#666666']
kc=mc.ListedColormap(leg)
fig,ax=plt.subplots(2,2,figsize=(7.1,4.1),constrained_layout=True)
for a_,k,l in [(ax[0,0],'1991-2020','a  Köppen–Geiger 1991–2020（Beck V3）'),(ax[0,1],'2071-2099-ssp585','b  2071–2099 SSP5-8.5')]:
    ax_map(a_,full2(KG[k][mask].astype('float32')),kc,mc.Normalize(0.5,30.5),l,None,False)
kf,shf,_,_,_=maps[('585','2081-2100')]
for a_,var,vals,l in [(ax[1,0],'SIC',np.mean([b['sic'] for b in P],0),'c  SIC 错配（SSP5-8.5 末期）'),(ax[1,1],'pH',mph,'d  pH 错配（SSP5-8.5 末期）')]:
    L,U=env(vals); cls=np.where(~shf,0,np.where(vals<L[kf],1,np.where(vals>U[kf],2,3))).astype('float32')
    ax_map(a_,full2(cls),mc.ListedColormap(['#f2f2f2','#2166ac','#b2182b','#fdd49e']),mc.Normalize(-.5,3.5),l,None,False)
fig.legend(handles=[mpa.Patch(color=c,label=t) for c,t in zip(['#fdd49e','#2166ac','#b2182b'],['迁移但在新带区间内','低于新带 5%','高于新带 95%'])],loc='lower center',ncol=3,frameon=False,fontsize=6,bbox_to_anchor=(0.5,-0.04))
fig.savefig(f'{F}/Fig2_zone_shift_mismatch.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig3 bivariate with robustness
bc=['#b2182b','#ef8a62','#67a9cf','#2166ac']
fig,ax=plt.subplots(1,2,figsize=(7.1,2.2),constrained_layout=True)
for a_,(s,pr),l in [(ax[0],('245','2081-2100'),'a  SSP2-4.5 2081–2100'),(ax[1],('585','2081-2100'),'b  SSP5-8.5 2081–2100')]:
    _,_,dO,dI,rob=maps[(s,pr)]
    cls=np.where((dO<0)&(dI<0),0,np.where((dO>=0)&(dI<0),1,np.where((dO<0)&(dI>=0),2,3))).astype('float32')
    ax_map(a_,full2(cls),mc.ListedColormap(bc),mc.Normalize(-.5,3.5),l,None,False)
    a_.imshow(full2(np.where(rob,np.nan,1.0)),extent=ext,cmap=mc.ListedColormap(['white']),alpha=0.55,interpolation='nearest')
fig.legend(handles=[mpa.Patch(color=c,label=t) for c,t in zip(bc,['SOC↓ SIC↓ 共损','SOC↑ SIC↓','SOC↓ SIC↑','SOC↑ SIC↑'])],loc='lower center',ncol=4,frameon=False,fontsize=6,bbox_to_anchor=(0.5,-0.1))
fig.savefig(f'{F}/Fig3_bivariate_dSOC_dSIC_robust.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig4 SHAP
imp=json.load(open(f'{O}/shap_importance.json'))
fig,ax=plt.subplots(1,4,figsize=(7.1,2.4),constrained_layout=True)
for a_,(k,l) in zip(ax,[('SOC','a  SOC'),('SIC_presence','b  SIC 有无'),('SIC_amount','c  SIC 含量'),('pH','d  pH')]):
    s=pd.Series(imp[k]).sort_values()[-8:]; a_.barh(s.index,s.values,color='#3b6ea8',height=.7)
    a_.set_title(l,loc='left',fontweight='bold',fontsize=8); a_.tick_params(labelsize=6); a_.set_xlabel('mean |SHAP|',fontsize=6)
    for sp in ['top','right']: a_.spines[sp].set_visible(False)
fig.savefig(f'{F}/Fig4_shap.png',dpi=300); plt.close()
# Fig5 scenarios with 90% CI, group shares
st=pd.DataFrame(rows); lab=[r.split(' ')[0].replace('SSP','')+('\n中期' if '2041' in r else '\n末期') for r in st.scenario]
fig,ax=plt.subplots(1,3,figsize=(7.1,2.5),constrained_layout=True)
x=np.arange(len(st))
for off,col,c,n in [(-.2,'dSOC','#1b7837','ΔSOC'),(.2,'dSIC','#b35806','ΔSIC')]:
    m_=np.array([v[0] for v in st[col]]); lo=np.array([v[1] for v in st[col]]); hi=np.array([v[2] for v in st[col]])
    ax[0].bar(x+off,m_,.4,color=c,label=n,yerr=[m_-lo,hi-m_],error_kw=dict(lw=.5,capsize=1))
ax[0].axhline(0,c='k',lw=.4); ax[0].set_xticks(x,lab,fontsize=5); ax[0].set_ylabel('Pg C'); ax[0].legend(frameon=False,fontsize=6); ax[0].set_title('a  平衡态储量变化（90% CI）',loc='left',fontweight='bold',fontsize=8)
for off,col,c,n in [(-.2,'mis_SIC','#b35806','SIC'),(.2,'mis_pH','#4393c3','pH')]:
    m_=np.array([v[0] for v in st[col]]); lo=np.array([v[1] for v in st[col]]); hi=np.array([v[2] for v in st[col]])
    ax[1].bar(x+off,m_,.4,color=c,label=n,yerr=[m_-lo,hi-m_],error_kw=dict(lw=.5,capsize=1))
ax[1].set_xticks(x,lab,fontsize=5); ax[1].set_ylabel('10⁶ km²'); ax[1].legend(frameon=False,fontsize=6); ax[1].set_title('b  错配面积',loc='left',fontweight='bold',fontsize=8)
gs=pd.DataFrame({g:{'SOC':v['SOC'][0],'SIC':v['SIC'][0],'sh':v['share'][0]} for g,v in gro.items()}).T
ax[2].bar(gs.index,gs.SOC,color='#1b7837',label='SOC'); ax[2].bar(gs.index,gs.SIC,bottom=gs.SOC,color='#b35806',label='SIC')
for i,(a1,b1,sh) in enumerate(zip(gs.SOC,gs.SIC,gs.sh)): ax[2].text(i,a1+b1+5,f'{sh:.0%}',ha='center',fontsize=6)
ax[2].set_ylabel('Pg C'); ax[2].legend(frameon=False,fontsize=6); ax[2].set_title('c  气候大区 SIC 占比',loc='left',fontweight='bold',fontsize=8)
for a_ in ax:
    for sp in ['top','right']: a_.spines[sp].set_visible(False)
fig.savefig(f'{F}/Fig5_scenarios_CI_zones.png',dpi=300); plt.close()
# Fig6 LUCAS validation
fig,ax=plt.subplots(1,2,figsize=(5,2.4),constrained_layout=True)
for a_,pp,l in [(ax[0],pr_[ok],'a  本模型'),(ax[1],sgp[ok],'b  SoilGrids 2.0')]:
    a_.hexbin(obs.values[ok],pp,gridsize=40,bins='log',cmap='Blues',extent=(0,200,0,200),linewidths=0)
    a_.plot([0,200],[0,200],'k--',lw=.5); a_.set_xlim(0,200); a_.set_ylim(0,200)
    a_.set_xlabel('LUCAS 2018 观测 SOC 储量 0–20 cm (Mg ha⁻¹)',fontsize=6); a_.set_ylabel('预测',fontsize=6)
    a_.set_title(l,loc='left',fontweight='bold',fontsize=8); mtr=mm_(obs.values[ok],pp)
    a_.text(.04,.9,f"R²={mtr['r2']:.2f}  bias={mtr['bias']:.1f}",transform=a_.transAxes,fontsize=6)
fig.savefig(f'{F}/Fig6_LUCAS_validation.png',dpi=300); plt.close()
print('FIGS OK')
