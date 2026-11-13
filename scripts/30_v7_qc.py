# Huang-style QC on WoSIS layers → points_v7_qc.csv + qc_flow.json
# Drop: pre-1970, litter/organic_surface, depth inconsistencies (upper>=lower, negative, upper>200),
# duplicates (same profile+depths), extreme outliers; keep post-1970 or undated with flag.
import pandas as pd, numpy as np, json, os, re
D='/workspace/soil_global/data'; O='/workspace/soil_global/out/v7'; os.makedirs(O,exist_ok=True)
flow={}
prof=pd.read_csv(f'{D}/wosis_latest_profiles.csv',usecols=['profile_id','year','longitude','latitude','country_name','usda_order_name','wrb_reference_soil_group'],low_memory=False)
prof=prof.rename(columns={'longitude':'X','latitude':'Y'}); flow['profiles_raw']=int(len(prof))
# year from profiles; also parse layer date
def load(code):
    cols=['profile_id','layer_id','upper_depth','lower_depth','value_avg','organic_surface','layer_name','date']
    d=pd.read_csv(f'{D}/wosis_latest_{code}.csv',usecols=lambda c:c in cols+['X','Y'],low_memory=False)
    flow[f'{code}_layers_raw']=int(len(d)); return d
props={}
for code in ['phaq','tceq','orgc','bdfiod','cfvo']:
    d=load(code)
    # litter / organic surface
    lit=d['organic_surface'].fillna(0).astype(str).isin(['1','True','true'])
    if 'layer_name' in d.columns:
        lit=lit|d['layer_name'].fillna('').str.contains(r'^(O|Oi|Oe|Oa|L|F|H)\b|litter|forest floor',case=False,regex=True)
    d=d.loc[~lit].copy(); flow[f'{code}_after_litter']=int(len(d))
    # depth consistency
    d=d[(d.lower_depth>d.upper_depth)&(d.upper_depth>=0)&(d.lower_depth>0)&(d.upper_depth<200)]
    flow[f'{code}_after_depth']=int(len(d))
    # date / year
    y=pd.to_numeric(d['date'].astype(str).str.extract(r'(\d{4})',expand=False),errors='coerce') if 'date' in d.columns else pd.Series(np.nan,index=d.index)
    # join profile year
    d=d.merge(prof[['profile_id','year','X','Y','country_name']],on='profile_id',how='left',suffixes=('','_p'))
    if 'X' not in d.columns or d['X'].isna().all(): d['X']=d.get('X_p'); d['Y']=d.get('Y_p')
    yy=pd.to_numeric(d['year'],errors='coerce'); yy=yy.fillna(y)
    d['year_use']=yy
    pre=(yy<1970)&yy.notna(); d=d.loc[~pre].copy(); flow[f'{code}_after_pre1970']=int(len(d)); flow[f'{code}_pre1970_dropped']=int(pre.sum())
    # value QC
    d=d[d.value_avg.notna()]
    if code=='phaq': d=d[(d.value_avg>=3)&(d.value_avg<=11)]
    if code=='tceq': d=d[(d.value_avg>=0)&(d.value_avg<=1000)]
    if code=='orgc': d=d[(d.value_avg>=0)&(d.value_avg<=580)]
    if code=='bdfiod': d=d[(d.value_avg>=0.05)&(d.value_avg<=2.5)]
    if code=='cfvo': d=d[(d.value_avg>=0)&(d.value_avg<=100)]
    flow[f'{code}_after_valueQC']=int(len(d))
    # duplicates: same profile+UD+LD keep first
    n0=len(d); d=d.drop_duplicates(['profile_id','upper_depth','lower_depth']); flow[f'{code}_dup_layers_dropped']=n0-len(d)
    props[code]=d
# spline harmonize QC'd layers
from mpspline.algorithm import spline_one
import logging; logging.disable(logging.WARNING)
INT=[(0,30),(30,100),(100,200)]
def spline_prop(code,vhigh):
    d=props[code][['profile_id','upper_depth','lower_depth','value_avg']].rename(columns={'upper_depth':'UD','lower_depth':'LD','value_avg':'v'})
    d=d.sort_values(['profile_id','UD']); prev=d.groupby('profile_id').LD.shift(); d=d[~(d.UD<prev)]
    rows=[]
    for pid,g in d.groupby('profile_id'):
        g=g.sort_values('UD'); bot=g.LD.max(); out=[np.nan]*3
        try:
            if len(g)==1:
                v=float(g.v.iloc[0]); 
                for i,(a,b) in enumerate(INT):
                    if bot>=a+0.5*(b-a) and g.UD.min()<=a+0.5*(b-a): out[i]=v
            else:
                r=spline_one(g[['UD','LD','v']],'v',lam=0.1,target_depths=INT,vlow=0,vhigh=vhigh)['est_dcm']
                for i,(a,b) in enumerate(INT):
                    if bot>=a+0.5*(b-a) and g.UD.min()<=a+0.5*(b-a): out[i]=r[i]
        except Exception: pass
        rows.append((pid,*out))
    o=pd.DataFrame(rows,columns=['profile_id']+[f'{code}_{a}_{b}' for a,b in INT]).set_index('profile_id')
    return o
print('splining...',flush=True)
res=None
for c,vh in [('phaq',14),('tceq',1000),('orgc',600),('bdfiod',2.6),('cfvo',100)]:
    o=spline_prop(c,vh); print(c,o.notna().sum().to_dict(),flush=True)
    res=o if res is None else res.join(o,how='outer')
xy=prof.set_index('profile_id')[['X','Y','year','country_name','usda_order_name','wrb_reference_soil_group']]
res=res.join(xy,how='inner')
for a,b in INT:
    s=f'_{a}_{b}'; res['sic'+s]=res['tceq'+s]*0.12
    imp=res['tceq'+s].isna()&(res['phaq'+s]<6.5); res.loc[imp,'sic'+s]=0.0
    res['soc'+s]=res['orgc'+s]
# counts
flow['profiles_with_any_after_QC']=int(len(res))
flow['profiles_with_SOC_0_30']=int(res['soc_0_30'].notna().sum())
flow['profiles_with_SIC_0_30']=int(res['sic_0_30'].notna().sum())
flow['profiles_with_pH_0_30']=int(res['phaq_0_30'].notna().sum())
flow['huang_reported']={'profiles':55077,'samples':223593,'note':'after their QC'}
res.to_csv(f'{D}/points_v7_qc.csv'); json.dump(flow,open(f'{O}/qc_flow.json','w'),indent=1)
print('DONE QC',len(res),json.dumps(flow),flush=True)
