"""Faithful 600-dpi redraw of the 22 v14 supporting figures, no new model run."""
import os,sys,json,glob,numpy as np
R='/workspace/soil_global';DEST=R+'/figs/v17_from_v14_SI_raw/'
exec(open(R+'/scripts/53_v10_figs.py').read().split('which=sys.argv[1]')[0],globals())
# Original v14 SI construction chain: 46 + 53b overrides, then 62 for regional SI.
src=build_env(open(R+'/scripts/46_v8_si.py').read()).split('for f in [globals()[n]')[0]
exec(src,globals());exec(open(R+'/scripts/53b_v10_overrides.py').read(),globals())
FS=DEST
# same capitalization used in 70_v14_figs.py
import matplotlib.axes,matplotlib.figure

def _up(fn):
 def wrap(self,*a,**k):
  a=list(a)
  if len(a)>=3 and isinstance(a[2],str) and len(a[2])==1 and a[2] in 'abcdefghijkl' and k.get('fontsize')==9 and k.get('fontweight')=='bold':a[2]=a[2].upper()
  return fn(self,*a,**k)
 return wrap
matplotlib.axes.Axes.text=_up(matplotlib.axes.Axes.text);matplotlib.figure.Figure.text=_up(matplotlib.figure.Figure.text)
def hi_save(fig,path):
 if os.path.basename(path) in ['FigS1_random_CV','FigS14_present_uncertainty']:
  ax=fig.axes[0]; ax.legend(ncol=3 if 'random' in path else 2,loc='lower center',bbox_to_anchor=(.5,1.015),frameon=False,fontsize=6)
 for ext in ['pdf','png']:fig.savefig(DEST+os.path.basename(path)+'.'+ext,dpi=600,bbox_inches='tight')
 plt.close(fig);print('SI',os.path.basename(path),flush=True)
save=hi_save
def S8():
 # Complete stored regression model, matrix display prevents crossed arrows and ambiguous labels.
 sem=json.load(open(R+'/out/v8/drivers_v8.json'))['sem']
 targets=['pH','SIC','SOC'];pred=['logAI','bio1','clay','carbonate_rock','pH']
 labels=['Humidity index: ln(1 + P/PET)','Mean annual temperature','Clay','Carbonate rock','pH']
 with plt.rc_context({'font.size':10,'axes.labelsize':10}):
  fig,ax=plt.subplots(figsize=(8,3.9));fig.subplots_adjust(left=.43,right=.96,top=.78,bottom=.20)
  ax.set_xlim(-.5,2.5);ax.set_ylim(4.5,-.5)
  for i,p in enumerate(pred):
   for j,target in enumerate(targets):
    v=sem[target].get(p);col='#f1f1f1' if v is None else ('#d7e8f3' if v>=0 else '#f7dedf')
    ax.add_patch(plt.Rectangle((j-.5,i-.5),1,1,fc=col,ec='white',lw=2))
    ax.text(j,i,'—' if v is None else f'{v:+.2f}',ha='center',va='center',fontsize=11,color='#555555' if v is None else ('#17578b' if v>=0 else '#ad2631'))
  ax.set_yticks(range(5),labels);ax.set_xticks(range(3),[f'{x} model\nR² = {sem[x]["R2"]:.2f}' for x in targets]);ax.xaxis.tick_top();ax.tick_params(length=0,pad=9)
  for sp in ax.spines.values():sp.set_visible(False)
  fig.suptitle('Complete standardized regression coefficients (n = 58,404)',fontsize=12,y=.98)
  fig.text(.05,.09,'Blank (—): predictor not included. Blue/red: positive/negative association, not causation.',fontsize=9)
  fig.text(.05,.035,'Humidity–pH–SIC indirect coefficient = −0.38; total humidity–SIC coefficient = −0.35.',fontsize=9)
  save(fig,FS+'FigS8_path_analysis')
selected=set(sys.argv[1:]) if sys.argv[1:] else {str(i) for i in range(1,23)}
for i in range(1,15):
 if str(i) in selected:globals()['S'+str(i)]()
src=open(R+'/scripts/62_v13_figs.py').read().split('for n in (sys.argv[1:]')[0]
exec(src,globals());FS=DEST;save=hi_save
for i in range(15,23):
 if str(i) in selected:globals()['S'+str(i)]()
