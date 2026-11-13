# v4: harmonize WoSIS layers to 0-30, 30-100, 100-200 cm by overlap (thickness) weighting.
# Overlap weighting conserves the layer-mass-weighted mean over each target interval (mass-preserving for
# interval means); it is NOT the Bishop et al. 1999 equal-area spline (labelled as such in the report).
import pandas as pd, numpy as np
D='/workspace/soil_global/data'
INT=[(0,30),(30,100),(100,200)]
def agg(code):
    d=pd.read_csv(f'{D}/wosis_latest_{code}.csv',usecols=['X','Y','profile_id','upper_depth','lower_depth','value_avg'],low_memory=False)
    d=d[(d.lower_depth>d.upper_depth)&d.value_avg.notna()&(d.upper_depth<200)]
    out=[]
    for a,b in INT:
        w=(np.minimum(d.lower_depth,b)-np.maximum(d.upper_depth,a)).clip(lower=0)
        e=d.assign(w=w,vw=w*d.value_avg)[w>0]
        g=e.groupby('profile_id').agg(X=('X','first'),Y=('Y','first'),vw=('vw','sum'),w=('w','sum'))
        g=g[g.w>=0.5*(b-a)]   # require >=50% coverage of the interval
        g[f'{code}_{a}_{b}']=g.vw/g.w; out.append(g[['X','Y',f'{code}_{a}_{b}']])
    r=out[0]
    for o in out[1:]: r=r.combine_first(o)
    return r
res=None
for c in ['phaq','tceq','orgc','bdfiod','cfvo']:
    g=agg(c); print(c,{k:int(g[k].notna().sum()) for k in g.columns if '_' in k},flush=True)
    res=g if res is None else res.combine_first(g)
for a,b in INT:
    s=f'_{a}_{b}'; res['sic'+s]=res['tceq'+s]*0.12
    imp=res['tceq'+s].isna()&(res['phaq'+s]<6.5); res.loc[imp,'sic'+s]=0.0; res['sicimp'+s]=imp
    res['soc'+s]=res['orgc'+s]
res.to_csv(f'{D}/points_v4_depths.csv'); print(len(res))
print(res[[c for c in res.columns if c.startswith(('sic_','soc_','phaq_','bdfiod_'))]].notna().sum())
