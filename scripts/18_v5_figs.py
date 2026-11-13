import numpy as np, pandas as pd, json, glob, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O='/workspace/soil_global/out/v5'; F='/workspace/soil_global/figs/v5'; import os; os.makedirs(F,exist_ok=True)
plt.rcParams.update({'font.size':8,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
B=[json.load(open(f)) for f in sorted(glob.glob(f'{O}/boot*.json'))]; NB=len(B)
DEP=['_0_30','_30_100','_100_200']; TH={'_0_30':30,'_30_100':70,'_100_200':100}
# organic C-density correction: mean(SOC*BD) over organic points instead of mean(SOC)*mean(BD)
p=pd.read_csv('/workspace/soil_global/data/points_v5_spline.csv'); cd={}
for s in DEP:
    o=p['soc'+s]; b=p['bdfiod'+s]; m=(o>120)&(o<=580)&b.between(0.1,2.2); cd[s]=float((o[m]*b[m]).mean())
def present(r,s):
    v=r['present'][s]; ratio=cd[s]/(v['socorg']*v['bdorg']); return v['SOC_min']+v['SOC_org']*ratio, v['SIC'], v['SOC_org']*ratio
q=lambda a: [float(np.percentile(a,50)),float(np.percentile(a,5)),float(np.percentile(a,95))]
R={'n_boot':NB,'present':{},'eq':{},'transient':{},'organic_Cdensity_kgm3':cd}
PS=np.array([[present(r,s) for s in DEP] for r in B])  # NB x 3 x 3
for i,s in enumerate(DEP): R['present'][s]=dict(SOC=q(PS[:,i,0]),SIC=q(PS[:,i,1]),SOC_organic=q(PS[:,i,2]),central_b0=dict(SOC=PS[0,i,0],SIC=PS[0,i,1]))
R['present']['_0_200']=dict(SOC=q(PS[:,:,0].sum(1)),SIC=q(PS[:,:,1].sum(1)),TC=q(PS[:,:,:2].sum((1,2))))
R['present']['_0_100']=dict(SOC=q(PS[:,:2,0].sum(1)),SIC=q(PS[:,:2,1].sum(1)))
# transient bounding: f=1-exp(-t/tau), t=85 yr (2005->2090), tau log-uniform per depth (assumption)
TAU={'_0_30':(20,100),'_30_100':(100,1000),'_100_200':(500,3000)}; t=85; rng=np.random.default_rng(1)
SC=['126_2081-2100','245_2081-2100','370_2081-2100','585_2081-2100']
for sc in SC:
    eqS=np.array([[np.mean(r['fut'][sc][s]['dsoc']) for s in DEP] for r in B]); eqI=np.array([[np.mean(r['fut'][sc][s]['dsic']) for s in DEP] for r in B])
    gS=np.array([[r['fut'][sc][s]['dsoc'] for s in DEP] for r in B])   # NB x 3 x 6gcm
    R['eq'][sc]={s:dict(dSOC=q(eqS[:,i]),dSIC=q(eqI[:,i])) for i,s in enumerate(DEP)}
    R['eq'][sc]['_0_200']=dict(dSOC=q(eqS.sum(1)),dSIC=q(eqI.sum(1)),dTC=q(eqS.sum(1)+eqI.sum(1)),gcm_range_b0=[float(gS[0].sum(0).min()),float(gS[0].sum(0).max())])
    # MC: boot x gcm x tau draws
    sims=[];simsI=[]
    for k in range(4000):
        b=rng.integers(NB); g=rng.integers(6)
        f=[1-np.exp(-t/np.exp(rng.uniform(*np.log(TAU[s])))) for s in DEP]
        sims.append(sum(f[i]*B[b]['fut'][sc][s]['dsoc'][g] for i,s in enumerate(DEP)))
        fI=[1-np.exp(-t/np.exp(rng.uniform(np.log(1000),np.log(10000)))) for s in DEP]  # SIC tau 1e3-1e4 yr (assumption)
        simsI.append(sum(fI[i]*B[b]['fut'][sc][s]['dsic'][g] for i,s in enumerate(DEP)))
    R['transient'][sc]=dict(dSOC_0_200=q(sims),dSIC_0_200=q(simsI),dTC_0_200=q(np.array(sims)+np.array(simsI)),
        dSOC_0_30=q([(1-np.exp(-t/np.exp(rng.uniform(*np.log(TAU['_0_30'])))))*B[rng.integers(NB)]['fut'][sc]['_0_30']['dsoc'][rng.integers(6)] for _ in range(4000)]))
N=json.load(open(f'{O}/N_calib.json')); R['N']=N
json.dump(R,open(f'{O}/results_v5.json','w'),indent=1)
v4=json.load(open('/workspace/soil_global/out/v4/results_v4.json'))['present']
# Fig1 layer totals vs v4/Batjes/SoilGrids
fig,ax=plt.subplots(1,2,figsize=(7.2,2.8))
lab=['0–30','30–100','100–200']; x=np.arange(3); w=0.25
v4s=[v4[s]['SOC'] for s in DEP]; v5s=[R['present'][s]['SOC'][0] for s in DEP]; e=np.array([[R['present'][s]['SOC'][0]-R['present'][s]['SOC'][1],R['present'][s]['SOC'][2]-R['present'][s]['SOC'][0]] for s in DEP]).T
bat=[(684+724)/2,(1462+1548)/2-(684+724)/2,(2376+2456)/2-(1462+1548)/2]
ax[0].bar(x-w,v4s,w,color='#bbbbbb',label='v4'); ax[0].bar(x,v5s,w,yerr=e,color='#1b7837',label='v5 (90% CI)',capsize=2); ax[0].bar(x+w,bat,w,color='#762a83',label='Batjes 1996 (mid)')
ax[0].scatter([0-w],[658],marker='_',s=200,c='k',zorder=5,label='SoilGrids 0–30 (same mask)')
ax[0].set_xticks(x,lab); ax[0].set_ylabel('SOC stock (Pg C)'); ax[0].set_xlabel('Depth (cm)'); ax[0].legend(frameon=False,fontsize=6); ax[0].set_title('a  SOC by layer',loc='left',fontweight='bold')
qc=json.load(open(f'{O}/qc.json'))
ax[1].bar(x-0.2,[qc[s]['org_frac']*100 for s in DEP],0.4,color='#8c510a',label='organic horizons (% of points)')
ax[1].bar(x+0.2,[qc[s]['org_share_of_point_SOC']*100 for s in DEP],0.4,color='#dfc27d',label='their share of point SOC (%)')
ax[1].set_xticks(x,lab); ax[1].set_ylabel('%'); ax[1].legend(frameon=False,fontsize=6); ax[1].set_title('b  Organic horizons (SOC>120 g/kg) in WoSIS',loc='left',fontweight='bold')
plt.tight_layout(); plt.savefig(f'{F}/Fig1_v5_SOC_fix.png',dpi=300); plt.close()
# Fig2 BD by SOC class (points)
fig,ax=plt.subplots(figsize=(3.5,2.6)); bins=[0,5,10,20,50,120,250,600]
for s,c in zip(DEP,['#1b7837','#5aae61','#a6dba0']):
    o=p['soc'+s]; b=p['bdfiod'+s]; m=o.notna()&b.between(0.1,2.2); g=pd.cut(o[m],bins); md=b[m].groupby(g,observed=False).median()
    ax.plot(range(len(md)),md.values,'o-',c=c,label=s.replace('_','–').strip('–')+' cm')
ax.set_xticks(range(len(bins)-1),[f'{bins[i]}–{bins[i+1]}' for i in range(len(bins)-1)],rotation=30); ax.set_xlabel('SOC (g/kg)'); ax.set_ylabel('Measured BD median (g/cm³)'); ax.legend(frameon=False,fontsize=6)
plt.tight_layout(); plt.savefig(f'{F}/Fig2_v5_BD_by_SOC.png',dpi=300); plt.close()
# Fig3 equilibrium vs transient
fig,ax=plt.subplots(1,2,figsize=(7.2,2.8)); x=np.arange(4); nm=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']
for k,(key,tt) in enumerate([('dSOC','ΔSOC 0–200 cm'),('dTC','ΔTotal C (SOC+SIC) 0–200 cm')]):
    E=np.array([R['eq'][sc]['_0_200'][key] for sc in SC]); T=np.array([R['transient'][sc][key+'_0_200'] for sc in SC])
    ax[k].errorbar(x-0.1,E[:,0],yerr=[E[:,0]-E[:,1],E[:,2]-E[:,0]],fmt='o',c='#b2182b',capsize=2,label='equilibrium potential')
    ax[k].errorbar(x+0.1,T[:,0],yerr=[T[:,0]-T[:,1],T[:,2]-T[:,0]],fmt='s',c='#2166ac',capsize=2,label='transient-bounded by 2090')
    ax[k].axhline(0,c='k',lw=0.5); ax[k].set_xticks(x,nm); ax[k].set_ylabel('Pg C (2081–2100 vs 1991–2020)'); ax[k].set_title(('a  ','b  ')[k]+tt,loc='left',fontweight='bold')
ax[0].legend(frameon=False,fontsize=6); plt.tight_layout(); plt.savefig(f'{F}/Fig3_v5_eq_vs_transient.png',dpi=300); plt.close()
# Fig4 N
fig,ax=plt.subplots(figsize=(3.6,2.6)); sc=['ssp126_2021_2050','ssp370_2021_2050','ssp585_2021_2050']; x=np.arange(3)
tot=lambda d:d['loss_0_30']+d['loss_30_100']
c=[tot(N[s]['central']) for s in sc]; lo=[tot(N[s]['low']) for s in sc]; hi=[tot(N[s]['high']) for s in sc]
ax.bar(x-0.18,c,0.36,yerr=[np.subtract(c,lo),np.subtract(hi,c)],color='#2166ac',capsize=2,label='v5 calibrated (0.055–0.32 kg C/kg N)')
ax.bar([0+0.18,2+0.18],[10,23],0.36,color='#d6604d',label='Huang et al. 2024 (SSP1-2.6/5-8.5)')
ax.set_xticks(x,['SSP1-2.6','SSP3-7.0','SSP5-8.5']); ax.set_ylabel('N-driven SIC loss 2021–2050 (Pg C)'); ax.legend(frameon=False,fontsize=6)
plt.tight_layout(); plt.savefig(f'{F}/Fig4_v5_N_calibration.png',dpi=300); plt.close()
print(json.dumps({k:R[k] for k in ['present','transient']},indent=0)[:4000])
