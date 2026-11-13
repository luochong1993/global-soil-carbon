"""Redraw seven ORIGINAL v14 panel compositions at 600 dpi for SI archive.
Preserves panels for new/old comparison, not the baseline manuscript narrative.
"""
import os,sys,json,glob,numpy as np
R='/workspace/soil_global';DEST=R+'/figs/v17_from_v14_SI_raw/';os.makedirs(DEST,exist_ok=True)
exec(open(R+'/scripts/53_v10_figs.py').read().split('which=sys.argv[1]')[0],globals())
src=build_env(open(R+'/scripts/45_v8_figs.py').read()).split('for f in [globals()[n]')[0]
exec(src,globals())
exec(open(R+'/scripts/53b_v10_overrides.py').read(),globals())
exec(open(R+'/scripts/70b_v14_overrides.py').read(),globals())
FS=DEST;FM=DEST
import matplotlib as mpl
mpl.rcParams.update({'pdf.fonttype':42,'savefig.dpi':600})
def save(fig,path):
 old=os.path.basename(path)
 names={'Fig1_present_stocks':'FigS23_v14_inventory','Fig2_SIC_share_countries':'FigS24_v14_countries',
 'Fig7_drivers':'FigS25_v14_drivers','Fig3_climate_change':'FigS26_v14_equilibrium',
 'Fig5_bivariate_SOC_SIC':'FigS27_v14_tradeoffs','Fig4_N_acidification':'FigS28_v14_nitrogen','Fig6_MAOC_POC':'FigS29_v14_fractions'}
 for ext in ['pdf','png']:fig.savefig(FS+names[old]+'.'+ext,dpi=600,bbox_inches='tight')
 plt.close(fig);print('archived',names[old],flush=True)
for fn in [fig1,fig2,fig7,fig3,fig5,fig4,fig6]:fn()
