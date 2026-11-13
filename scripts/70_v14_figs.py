# v14 figure regeneration: same inputs (out/v10, out/v13), no refitting.
# Changes vs v13: (1) panel letters upper-case (Science style; legends already use A, B, ...);
# (2) Fig. 5 (file Fig5_bivariate_SOC_SIC) inset labelled with quadrant names and the 137.3 Mkm2 denominator, country labels de-overlapped;
# (3) Fig. 6 (file Fig4_N_acidification) panel-A legend moved off the curves.
# usage: python3 70_v14_figs.py main|si|v13si [fig names...]
import sys, matplotlib, matplotlib.axes, matplotlib.figure
def _up(f):
  def g(self,*a,**k):
    a=list(a)
    if len(a)>=3 and isinstance(a[2],str) and len(a[2])==1 and a[2] in 'abcdefghijkl' and k.get('fontsize')==9 and k.get('fontweight')=='bold': a[2]=a[2].upper()
    return f(self,*a,**k)
  return g
matplotlib.axes.Axes.text=_up(matplotlib.axes.Axes.text); matplotlib.figure.Figure.text=_up(matplotlib.figure.Figure.text)
R='/workspace/soil_global'
mode=sys.argv[1]; rest=sys.argv[2:]
if mode in ('main','si'):
  s=open(R+'/scripts/53_v10_figs.py').read()
  s=s.replace("\"FM=R+'/figs/v10_main/'\"","\"FM=R+'/figs/v14_main/'\"").replace("\"FS=R+'/figs/v10_SI/'\"","\"FS=R+'/figs/v14_SI_raw/'\"")
  s=s.replace("json.dump(log,open(O10+'/fig_numbers_v10.json','w'),indent=1)","json.dump(log,open(R+'/out/v14/fig_numbers_v14_'+which.split('_')[0]+'.json','w'),indent=1,default=float)")
  s=s.replace("exec(open(R+'/scripts/53b_v10_overrides.py').read())","exec(open(R+'/scripts/53b_v10_overrides.py').read())\\nexec(open(R+'/scripts/70b_v14_overrides.py').read())")
  sys.argv=['53',('45_v8_figs.py' if mode=='main' else '46_v8_si.py')]+rest
  exec(s)
else:
  s=open(R+'/scripts/62_v13_figs.py').read()
  s=s.replace("FS=R+'/figs/v13_SI/'","FS=R+'/figs/v14_SI_raw/'").replace("R+'/out/v13/fig_numbers_v13.json'","R+'/out/v14/fig_numbers_v14_v13si.json'")
  sys.argv=['62']+rest
  exec(s)
