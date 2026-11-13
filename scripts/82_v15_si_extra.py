"""v15 SI extras: S16 thicken MAOC/POC, S18 shape+color GCMs, S21 thicker Sankey labels."""
import sys, json, os, numpy as np, matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
R='/workspace/soil_global'
# Bootstrap like 62_v13_figs
exec(open(R+'/scripts/43_v8_style.py').read(), globals())
exec(open(R+'/scripts/80_v15_style.py').read(), globals())
FS=R+'/figs/v15_SI_raw/'; O10=R+'/out/v10'; O13=R+'/out/v13'
S=json.load(open(O13+'/summaries_v13.json')); PT=json.load(open(O13+'/points_summary_v13.json'))
EM=np.load(O10+'/ens_maps.npz'); EJ=json.load(open(O10+'/ensemble_v10.json'))
SSP=['126','245','370','585']; LBL={s:f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP}
SC={'126':'#1d3c8f','245':'#69b3e0','370':'#f39c4a','585':'#c0262c'}
# High-contrast GCM colors + shapes
GC6=dict(zip(
  ['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],
  ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628']))
GMARK=dict(zip(GC6.keys(), ['o','s','^','D','v','P']))
log={}; DC=['#2171b5','#6a51a3','#e08214']; DL=['0–30','30–100','100–200']
KC={'A':'#1b9e77','B':'#d95f02','C':'#7570b3','D':'#e7298a','E':'#66a61e'}
MAIN=np.array(list(' ABCDE'))  # placeholder if needed

def lt(a,l,dx=-0.12):
  a.text(dx,1.03,l,transform=a.transAxes,fontsize=9,fontweight='bold')

# ---- S16 latitude with thicker MAOC/POC + fill_between ----
def S16():
  L=S['lat_profiles']; lat_=np.array(L['lat'])
  def sm(v,w=3):
    v=np.asarray(v,float); k=np.ones(w)/w; return np.convolve(np.nan_to_num(v),k,mode='same')
  fig,ax=plt.subplots(2,3,figsize=(7.2,5.2)); plt.subplots_adjust(hspace=0.35,wspace=0.3)
  for l,lay in enumerate(['0_30','30_100','100_200']):
    ax[0,0].fill_betweenx(lat_,0,sm(L['SOC_'+lay]),color=DC[l],alpha=0.18,lw=0)
    ax[0,0].plot(sm(L['SOC_'+lay]),lat_,c=DC[l],lw=1.1,label=DL[l])
    ax[0,1].fill_betweenx(lat_,0,sm(L['SIC_'+lay]),color=DC[l],alpha=0.18,lw=0)
    ax[0,1].plot(sm(L['SIC_'+lay]),lat_,c=DC[l],lw=1.1,label=DL[l])
  ax[0,0].set_xlabel('SOC (Pg C per 1°)'); ax[0,1].set_xlabel('SIC (Pg C per 1°)')
  ax[0,0].legend(fontsize=5); ax[0,1].legend(fontsize=5)
  # Panel C: MAOC vs POC — thicken + fill
  specs=[('MAOC_0_30','#2171b5','-',0.25),('POC_0_30','#e08214','-',0.25),
         ('MAOC_30_100','#08306b',':',0.18),('POC_30_100','#a63603',':',0.18)]
  for key,col,ls,al in specs:
    y=sm(L[key])
    ax[0,2].fill_betweenx(lat_,0,y,color=col,alpha=al,lw=0)
    ax[0,2].plot(y,lat_,c=col,lw=1.6,ls=ls,label=key.replace('_',' '))
  ax[0,2].set_xlabel('MAOC, POC (Pg C per 1°)'); ax[0,2].legend(fontsize=4.8,loc='lower right')
  soc=sm(L['SOC_0_30'])+sm(L['SOC_30_100'])+sm(L['SOC_100_200'])
  sic=sm(L['SIC_0_30'])+sm(L['SIC_30_100'])+sm(L['SIC_100_200'])
  sh=np.where(soc+sic>0.05,sic/(soc+sic)*100,np.nan)
  ax[1,0].plot(sm(sh),lat_,c='#7a0177',lw=1.2); ax[1,0].fill_betweenx(lat_,0,sm(sh),color='#7a0177',alpha=0.15,lw=0)
  ax[1,0].set_xlabel('SIC/TC (%)')
  # keep other panels from original if present in L
  for a in ax.flat:
    a.set_ylim(-56,84); a.set_ylabel('Latitude (°)') if a in (ax[0,0],ax[1,0]) else None
  # panels D-F: future deltas if available
  if 'dSOC_0_200_585' in L or 'dSOC_585' in L:
    pass
  # Replicate remaining from 62 more carefully
  exec(open(R+'/scripts/62_v13_figs.py').read().split('def S16')[1].split('def S17')[0].split('save(fig')[0], globals())
  # Actually simpler: call original then overlay — skip. Write minimal 6-panel from data keys
  for a,l in zip(ax.flat[:4],'ABCD'):
    lt(a,l,-0.14)
  # blank E F if not filled — fill with eq delta lat profiles if keys exist
  keys_fut=[k for k in L if k.startswith('dSOC') or k.startswith('dSIC') or k.startswith('dMAOC')]
  # From 62: panels D-F use future
  # Just save 2x2 if future missing
  if 'dSOC_0_200_126' in L:
    for j,s in enumerate(['126','585']):
      ax[1,1].plot(sm(L[f'dSOC_0_200_{s}']),lat_,c=SC[s],lw=1.1,label=LBL[s])
      ax[1,2].plot(sm(L[f'dSIC_0_200_{s}']),lat_,c=SC[s],lw=1.1,label=LBL[s])
    ax[1,1].axvline(0,c='0.5',lw=0.4); ax[1,2].axvline(0,c='0.5',lw=0.4)
    ax[1,1].legend(fontsize=5); ax[1,2].legend(fontsize=5)
    ax[1,1].set_xlabel('Eq. ΔSOC 0–200'); ax[1,2].set_xlabel('Eq. ΔSIC 0–200')
    lt(ax[1,1],'E',-0.14); lt(ax[1,2],'F',-0.14)
  else:
    ax[1,1].axis('off'); ax[1,2].axis('off')
  save(fig,FS+'FigS16_latitude_profiles')
  print('ok S16', flush=True)

# Better approach: patch 62 in-place via exec with overrides
def S16_from62():
  src=open(R+'/scripts/62_v13_figs.py').read()
  # thicken MAOC/POC lines and add fill
  src=src.replace("FS=R+'/figs/v13_SI/'","FS=R+'/figs/v15_SI_raw/'")
  src=src.replace(
    "for k,(key,col,ls) in enumerate([('MAOC_0_30','#2171b5','-'),('POC_0_30','#e08214','-'),('MAOC_30_100','#08306b',':'),('POC_30_100','#a63603',':')]):\n    ax[2].plot(sm(L[key]),lat_,c=col,lw=0.9,ls=ls,label=key.replace('_',' '))",
    "for k,(key,col,ls,al) in enumerate([('MAOC_0_30','#2171b5','-',0.22),('POC_0_30','#e08214','-',0.22),('MAOC_30_100','#08306b',':',0.15),('POC_30_100','#a63603',':',0.15)]):\n    y=sm(L[key]); ax[2].fill_betweenx(lat_,0,y,color=col,alpha=al,lw=0); ax[2].plot(y,lat_,c=col,lw=1.7,ls=ls,label=key.replace('_',' '))"
  )
  # GCM colors+shapes
  src=src.replace(
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#a6761d']))",
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628'])); GMARK=dict(zip(GC6,['o','s','^','D','v','P']))"
  )
  src=src.replace(
    "a.scatter(xx,q['mean'],s=16,color=col,edgecolor='k',lw=0.3,zorder=3,label=gc if i==0 else None)",
    "a.scatter(xx,q['mean'],s=28,color=col,marker=GMARK[gc],edgecolor='k',lw=0.35,zorder=3,label=gc if i==0 else None)"
  )
  # Sankey thicker labels
  src=src.replace(
    "b.text(-0.03,y0[i]+tot0[i]/2,f'{k} {tot0[i]:.0f}',ha='right',va='center',fontsize=5.5); b.text(1.03,y1[i]+tot1[i]/2,f'{k} {tot1[i]:.0f}',ha='left',va='center',fontsize=5.5)",
    "b.text(-0.03,y0[i]+tot0[i]/2,f'{k} {tot0[i]:.0f}',ha='right',va='center',fontsize=7,fontweight='bold'); b.text(1.03,y1[i]+tot1[i]/2,f'{k} {tot1[i]:.0f}',ha='left',va='center',fontsize=7,fontweight='bold')"
  )
  src=src.replace("alpha=0.25 if i==j else 0.75,lw=0)","alpha=0.3 if i==j else 0.85,lw=0.2)")
  # Only run S16,S18,S21
  src=src.split('for n in (sys.argv[1:]')[0]
  src += "\nfor n in ['S16','S18','S21']:\n  try: globals()[n](); print('ok',n,flush=True)\n  except Exception as e:\n    import traceback; traceback.print_exc(); print('FAIL',n,e,flush=True)\n"
  # Need globals from 62 preamble — run full file preamble
  preamble=open(R+'/scripts/62_v13_figs.py').read().split('def S15')[0]
  preamble=preamble.replace("FS=R+'/figs/v13_SI/'","FS=R+'/figs/v15_SI_raw/'")
  preamble=preamble.replace(
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#a6761d']))",
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628'])); GMARK=dict(zip(list(GC6),['o','s','^','D','v','P']))"
  )
  # Extract function bodies with patches
  full=open(R+'/scripts/62_v13_figs.py').read()
  full=full.replace("FS=R+'/figs/v13_SI/'","FS=R+'/figs/v15_SI_raw/'")
  full=full.replace(
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#a6761d']))",
    "GC6=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628'])); GMARK=dict(zip(['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6'],['o','s','^','D','v','P']))"
  )
  full=full.replace(
    "for k,(key,col,ls) in enumerate([('MAOC_0_30','#2171b5','-'),('POC_0_30','#e08214','-'),('MAOC_30_100','#08306b',':'),('POC_30_100','#a63603',':')]):\n    ax[2].plot(sm(L[key]),lat_,c=col,lw=0.9,ls=ls,label=key.replace('_',' '))",
    "for k,(key,col,ls,al) in enumerate([('MAOC_0_30','#2171b5','-',0.22),('POC_0_30','#e08214','-',0.22),('MAOC_30_100','#08306b',':',0.15),('POC_30_100','#a63603',':',0.15)]):\n    y=sm(L[key]); ax[2].fill_betweenx(lat_,0,y,color=col,alpha=al,lw=0); ax[2].plot(y,lat_,c=col,lw=1.7,ls=ls,label=key.replace('_',' '))"
  )
  full=full.replace(
    "a.scatter(xx,q['mean'],s=16,color=col,edgecolor='k',lw=0.3,zorder=3,label=gc if i==0 else None)",
    "a.scatter(xx,q['mean'],s=28,color=col,marker=GMARK[gc],edgecolor='k',lw=0.35,zorder=3,label=gc if i==0 else None)"
  )
  full=full.replace(
    "b.text(-0.03,y0[i]+tot0[i]/2,f'{k} {tot0[i]:.0f}',ha='right',va='center',fontsize=5.5); b.text(1.03,y1[i]+tot1[i]/2,f'{k} {tot1[i]:.0f}',ha='left',va='center',fontsize=5.5)",
    "b.text(-0.03,y0[i]+tot0[i]/2,f'{k} {tot0[i]:.0f}',ha='right',va='center',fontsize=7.5,fontweight='bold'); b.text(1.03,y1[i]+tot1[i]/2,f'{k} {tot1[i]:.0f}',ha='left',va='center',fontsize=7.5,fontweight='bold')"
  )
  full=full.replace("alpha=0.25 if i==j else 0.75,lw=0)","alpha=0.35 if i==j else 0.9,lw=0.25)")
  # Restrict to S16 S18 S21
  full=full.replace(
    "for n in (sys.argv[1:] or ['S15','S16','S17','S18','S19','S20','S21','S22']):",
    "for n in (sys.argv[1:] or ['S16','S18','S21']):"
  )
  full=full.replace("R+'/out/v13/fig_numbers_v13.json'","R+'/out/v15/fig_numbers_v15_si_extra.json'")
  # also apply classed_v15 for any maps in S21
  g={'classed': classed_v15}
  exec(full, {**globals(), **g})

if __name__=='__main__' or True:
  S16_from62()
