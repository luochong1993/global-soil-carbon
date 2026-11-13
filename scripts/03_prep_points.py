# Topsoil 0-30 cm depth-weighted means per WoSIS profile; sampling year distribution
import pandas as pd, numpy as np
D='/workspace/soil_global/data'
def agg(code):
    d=pd.read_csv(f'{D}/wosis_latest_{code}.csv',usecols=['X','Y','profile_id','upper_depth','lower_depth','value_avg','date'],low_memory=False)
    d=d[(d.upper_depth<30)&(d.lower_depth>d.upper_depth)&d.value_avg.notna()]
    d['w']=np.minimum(d.lower_depth,30)-d.upper_depth
    d=d[d.w>0]; d['vw']=d.value_avg*d.w
    g=d.groupby('profile_id').agg(X=('X','first'),Y=('Y','first'),vw=('vw','sum'),w=('w','sum'),date=('date','first'))
    g[code]=g.vw/g.w; g['cov_'+code]=g.w; return g[['X','Y','date',code,'cov_'+code]]
out=None
for c in ['phaq','tceq','orgc','bdfiod','cfvo']:
    g=agg(c); print(c,len(g))
    out=g if out is None else out.join(g[[c,'cov_'+c]].join(g[['X','Y','date']].add_suffix('_'+c)),how='outer')
    if 'X_'+c in out:
        for k in ['X','Y','date']: out[k]=out[k].fillna(out[k+'_'+c]); out=out.drop(columns=k+'_'+c)
pr=pd.read_csv(f'{D}/wosis_latest_profiles.csv',usecols=['profile_id','year','dataset_code','country_name'])
out=out.join(pr.set_index('profile_id'),how='left')
yr=pd.to_numeric(out.date.astype(str).str[:4],errors='coerce'); out['yr']=out.year.fillna(yr)
# implied SIC: TCEQ(g/kg)*0.12; if TCEQ missing and pH<6.5 -> 0 (non-calcareous assumption)
out['sic']=out.tceq*0.12; out['sic_imputed0']=out.tceq.isna()&(out.phaq<6.5)
out.loc[out.sic_imputed0,'sic']=0.0
out['soc']=out.orgc
out.to_csv(f'{D}/points_topsoil.csv')
print(len(out)); print(out[['phaq','tceq','sic','soc','bdfiod','cfvo']].notna().sum())
print('sic imputed 0:',out.sic_imputed0.sum())
b=pd.cut(out.yr,[1900,1950,1960,1970,1980,1990,2000,2010,2020,2030],right=False)
yt=pd.DataFrame({v:out[out[v].notna()].groupby(b[out[v].notna()],observed=False).size() for v in ['phaq','tceq','soc','bdfiod']})
yt.loc['unknown']=[out[v].notna().sum()-yt[v].sum() for v in yt]
print(yt); yt.to_csv('/workspace/soil_global/out/year_distribution.csv')
