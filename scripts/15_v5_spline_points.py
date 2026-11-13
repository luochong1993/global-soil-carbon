# v5: Bishop et al. (1999) / Malone et al. (2009) mass-preserving equal-area spline (python mpspline 0.2.0, lambda=0.1)
import pandas as pd, numpy as np, os, sys, warnings, logging
from multiprocessing import Pool
from mpspline.algorithm import spline_one
logging.disable(logging.WARNING); warnings.filterwarnings('ignore')
D='/workspace/soil_global/data'; INT=[(0,30),(30,100),(100,200)]
def one(args):
    pid,g,code,vhigh=args
    g=g.sort_values('UD')
    bot=g.LD.max(); out=[np.nan]*3
    if len(g)==1:
        r=None
    try:
        r=spline_one(g[['UD','LD','v']],'v',lam=0.1,target_depths=INT,vlow=0,vhigh=vhigh)['est_dcm']
    except Exception: r=[np.nan]*3
    for i,(a,b) in enumerate(INT):
        if bot>=a+0.5*(b-a) and g.UD.min()<=a+0.5*(b-a): out[i]=r[i]
    return pid,out
def run(code,vhigh):
    fn=f'{D}/spline_{code}.csv'
    if os.path.exists(fn): return pd.read_csv(fn,index_col=0)
    d=pd.read_csv(f'{D}/wosis_latest_{code}.csv',usecols=['profile_id','upper_depth','lower_depth','value_avg'],low_memory=False)
    d=d[(d.lower_depth>d.upper_depth)&d.value_avg.notna()&(d.upper_depth<200)].rename(columns={'upper_depth':'UD','lower_depth':'LD','value_avg':'v'})
    d=d.drop_duplicates(['profile_id','UD','LD'])
    # drop overlapping horizons (keep first) - spline needs non-overlapping sequence
    d=d.sort_values(['profile_id','UD']); prevLD=d.groupby('profile_id').LD.shift(); d=d[~(d.UD<prevLD)]
    tasks=[(pid,g,code,vhigh) for pid,g in d.groupby('profile_id')]
    with Pool(4) as p: res=p.map(one,tasks,chunksize=500)
    o=pd.DataFrame({pid:v for pid,v in res}).T; o.columns=[f'{code}_{a}_{b}' for a,b in INT]; o.to_csv(fn); print(code,o.notna().sum().to_dict(),flush=True); return o
if __name__=='__main__':
    res=None
    for c,vh in [('phaq',14),('tceq',1000),('orgc',600),('bdfiod',2.6),('cfvo',100)]:
        o=run(c,vh); res=o if res is None else res.join(o,how='outer')
    xy=pd.read_csv(f'{D}/points_v4_depths.csv',usecols=['profile_id','X','Y']).set_index('profile_id')
    res=res.join(xy,how='inner')
    for a,b in INT:
        s=f'_{a}_{b}'; res['sic'+s]=res['tceq'+s]*0.12
        imp=res['tceq'+s].isna()&(res['phaq'+s]<6.5); res.loc[imp,'sic'+s]=0.0
        res['soc'+s]=res['orgc'+s]
    res.index.name='profile_id'; res.to_csv(f'{D}/points_v5_spline.csv'); print('DONE',len(res))
