import numpy as np, json, os, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.colors as mc, matplotlib.patches as mpa
O='/workspace/soil_global/out/v4'; F='/workspace/soil_global/figs/v4'; os.makedirs(F,exist_ok=True)
plt.rcParams.update({'font.size':7,'font.family':['Noto Sans CJK JP','DejaVu Sans'],'axes.unicode_minus':False,'axes.linewidth':0.5})
mask=np.load(f'{O}/mask.npy'); H,W=mask.shape
lat=np.linspace(90,-90,H+1)[:-1]-90/H; area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
KG=dict(np.load('/workspace/soil_global/out/v2/kg_beck.npz')); kg0=KG['1991-2020'][mask]
grp=np.select([kg0==0,kg0<=3,kg0<=7,kg0<=16,kg0<=28],[0,1,2,3,4],5); GN={1:'A',2:'B',3:'C',4:'D',5:'E'}
DEP=[('_0_30',30),('_30_100',70),('_100_200',100)]
Z={d:dict(np.load(f'{O}/depth{d}.npz')) for d,_ in DEP}
st=lambda c,z,t: c*z['bd0']*(1-z['CF']/100)*t*0.1
Pg=lambda s,m=None: float(np.nansum(s*area if m is None else (s*area)[m])*1e-9)
R={'present':{},'scen':{}}
SOC={};SIC={}
for d,t in DEP:
    z=Z[d]; SOC[d]=st(z['soc0'],z,t); SIC[d]=st(z['sic0'],z,t)
    R['present'][d]={'SOC':Pg(SOC[d]),'SIC':Pg(SIC[d]),'by_zone':{GN[g]:{'SOC':Pg(SOC[d],grp==g),'SIC':Pg(SIC[d],grp==g)} for g in GN}}
R['present']['_0_200']={'SOC':sum(R['present'][d]['SOC'] for d,_ in DEP),'SIC':sum(R['present'][d]['SIC'] for d,_ in DEP)}
R['cv']={d:json.load(open(f'{O}/cv{d}.json')) for d,_ in DEP}
SCN=[(s,p) for s in ('126','245','370','585') for p in ('2041-2060','2081-2100')]
maps={}
for s,p in SCN:
    k=f'{s}_{p}'; r={}
    dO_all=0; dI_all=0; dOg=0; dIg=0
    for d,t in DEP:
        z=Z[d]
        gO=st(z[f'soc_{k}_gcm'].astype('float32'),z,t); gI=st(z[f'sic_{k}_gcm'].astype('float32'),z,t); gP=st(z[f'sicph_{k}_gcm'].astype('float32'),z,t)
        tO=[Pg(x) for x in gO]; tI=[Pg(x) for x in gI]; tP=[Pg(x) for x in gP]
        r[d]={'dSOC':[float(np.mean(tO)),min(tO),max(tO)],'dSIC_climate_total':[float(np.mean(tI)),min(tI),max(tI)],'dSIC_pH_pathway':[float(np.mean(tP)),min(tP),max(tP)],
              'by_zone':{GN[g]:{'dSOC':float(np.mean([Pg(x,grp==g) for x in gO])),'dSIC':float(np.mean([Pg(x,grp==g) for x in gI]))} for g in GN}}
        dOg=dOg+gO; dIg=dIg+gI
    tot=[Pg(a)+Pg(b) for a,b in zip(dOg,dIg)]
    r['_0_200']={'dSOC':float(np.mean([Pg(x) for x in dOg])),'dSIC':float(np.mean([Pg(x) for x in dIg])),'dTotal':[float(np.mean(tot)),min(tot),max(tot)]}
    mO=dOg.mean(0); mI=dIg.mean(0); agO=(np.sign(dOg)==np.sign(mO)).mean(0); agI=(np.sign(dIg)==np.sign(mI)).mean(0); rob=(agO>=5/6)&(agI>=5/6)
    r['_0_200']['coloss_Mkm2']=float(area[(mO<0)&(mI<0)].sum()/1e8); r['_0_200']['coloss_robust_Mkm2']=float(area[(mO<0)&(mI<0)&rob].sum()/1e8)
    r['_0_200']['tradeoff_Mkm2']=float(area[(mO*mI)<0].sum()/1e8); r['_0_200']['tradeoff_robust_Mkm2']=float(area[((mO*mI)<0)&rob].sum()/1e8)
    kf=KG[f"{ {'2041-2060':'2041-2070','2081-2100':'2071-2099'}[p]}-ssp{s}"][mask]; sh=(kf!=kg0)&(kf>0)
    r['_0_200']['shift_dSOC']=float(np.mean([Pg(x,sh) for x in dOg])); r['_0_200']['shift_dSIC']=float(np.mean([Pg(x,sh) for x in dIg]))
    R['scen'][k]=r; maps[k]=(mO,mI,rob); print(k,json.dumps(r['_0_200']),flush=True)
R['N_acid']=json.load(open(f'{O}/N_acidification.json'))
json.dump(R,open(f'{O}/results_v4.json','w'),indent=1)
# ---------- figures
sl=slice(0,150*6); ext=[-180,180,-60,90]
def full(v): a=np.full((H,W),np.nan,'float32'); a[mask]=v; return a[sl]
def mp(ax,a,cmap,norm,lab,cb=''):
    im=ax.imshow(a,extent=ext,cmap=cmap,norm=norm,interpolation='nearest'); ax.set_xticks([]);ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.text(0,1.02,lab,transform=ax.transAxes,fontweight='bold',fontsize=8)
    if cb is not None:
        c=plt.colorbar(im,ax=ax,orientation='horizontal',fraction=0.045,pad=0.02,aspect=35); c.set_label(cb,fontsize=6); c.ax.tick_params(labelsize=6); c.outline.set_linewidth(.4)
tO=sum(SOC.values()); tI=sum(SIC.values())
fig,ax=plt.subplots(2,2,figsize=(7.1,4.4),constrained_layout=True)
mp(ax[0,0],full(tO),'YlGn',mc.LogNorm(10,600),'a  SOC 0–200 cm','Mg C ha⁻¹')
mp(ax[0,1],full(tI),'OrRd',mc.LogNorm(1,800),'b  SIC 0–200 cm','Mg C ha⁻¹')
mp(ax[1,0],full(tI/(tI+tO)),'PuOr_r',mc.Normalize(0,1),'c  SIC/(SOC+SIC) 0–200 cm','')
a=ax[1,1]; zs=list(GN.values()); x=np.arange(5); bottom=np.zeros(5)
cols={'SOC':['#1b7837','#5aae61','#a6dba0'],'SIC':['#b35806','#f1a340','#fee0b6']}
for i,(d,_) in enumerate(DEP):
    v=np.array([R['present'][d]['by_zone'][g]['SOC'] for g in zs]); a.bar(x-.2,v,.38,bottom=bottom,color=cols['SOC'][i],label=f'SOC {d[1:].replace("_","–")} cm'); bottom+=v
bottom=np.zeros(5)
for i,(d,_) in enumerate(DEP):
    v=np.array([R['present'][d]['by_zone'][g]['SIC'] for g in zs]); a.bar(x+.2,v,.38,bottom=bottom,color=cols['SIC'][i],label=f'SIC {d[1:].replace("_","–")} cm'); bottom+=v
a.set_xticks(x,['A 热带','B 干旱','C 温带','D 冷温带','E 极地']); a.set_ylabel('Pg C'); a.legend(frameon=False,fontsize=5,ncol=2)
for sp in ['top','right']: a.spines[sp].set_visible(False)
a.text(0,1.02,'d  各气候大区分层碳储量',transform=a.transAxes,fontweight='bold',fontsize=8)
fig.savefig(f'{F}/Fig1_v4_total_carbon_0_200.png',dpi=300); plt.close()
# Fig2 change by depth/scenario
fig,ax=plt.subplots(1,3,figsize=(7.1,2.5),constrained_layout=True)
lab=[k.split('_')[0]+('\n中' if '2041' in k else '\n末') for k in R['scen']]
for a,(d,_),t in zip(ax,DEP,['a  0–30 cm','b  30–100 cm','c  100–200 cm']):
    x=np.arange(len(lab))
    for off,key,c,n in [(-.27,'dSOC','#1b7837','ΔSOC'),(0,'dSIC_climate_total','#b35806','ΔSIC 气候'),(.27,'dSIC_pH_pathway','#4393c3','ΔSIC pH 路径')]:
        v=np.array([R['scen'][k][d][key] for k in R['scen']]); a.bar(x+off,v[:,0],.26,color=c,label=n,yerr=[v[:,0]-v[:,1],v[:,2]-v[:,0]],error_kw=dict(lw=.4,capsize=1))
    a.axhline(0,c='k',lw=.4); a.set_xticks(x,lab,fontsize=5); a.text(0,1.02,t,transform=a.transAxes,fontweight='bold',fontsize=8)
    for sp in ['top','right']: a.spines[sp].set_visible(False)
ax[0].set_ylabel('Pg C（误差线为 6 个 GCM 范围）'); ax[0].legend(frameon=False,fontsize=5)
fig.savefig(f'{F}/Fig2_v4_change_by_depth.png',dpi=300); plt.close()
# Fig3 bivariate 0-200 + N loss map
bc=['#b2182b','#ef8a62','#67a9cf','#2166ac']
fig,ax=plt.subplots(1,2,figsize=(7.1,2.3),constrained_layout=True)
mO,mI,rob=maps['585_2081-2100']; cls=np.where((mO<0)&(mI<0),0,np.where((mO>=0)&(mI<0),1,np.where((mO<0)&(mI>=0),2,3))).astype('float32')
mp(ax[0],full(cls),mc.ListedColormap(bc),mc.Normalize(-.5,3.5),'a  ΔSOC×ΔSIC 0–200 cm（SSP5-8.5 末期）',None)
ax[0].imshow(full(np.where(rob,np.nan,1.0)),extent=ext,cmap=mc.ListedColormap(['white']),alpha=.55,interpolation='nearest')
Nl=np.load(f'{O}/Nloss_585_2021_2050_0_30.npy')
mp(ax[1],full(np.where(Nl>0,Nl,np.nan)),'magma_r',mc.LogNorm(0.01,5),'b  N 致酸 SIC 损失 0–30 cm（SSP5-8.5，2021–2050，中值假设）','Mg C ha⁻¹')
fig.legend(handles=[mpa.Patch(color=c,label=t) for c,t in zip(bc,['共损','SOC↑ SIC↓','SOC↓ SIC↑','共增'])],loc='lower left',ncol=4,frameon=False,fontsize=6,bbox_to_anchor=(0.02,-0.08))
fig.savefig(f'{F}/Fig3_v4_bivariate_Nacid.png',dpi=300,bbox_inches='tight'); plt.close()
print('FIGS OK')
