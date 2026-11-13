import numpy as np, pandas as pd, json, os
from scipy.spatial import cKDTree
O='/workspace/soil_global/out/v7'
lucas=pd.read_csv('/workspace/soil_global/data/lucas2018_socs.csv')
lucas.columns=[c.strip() for c in lucas.columns]
# SOCS kg m-2 → Mg/ha = *10
lucas['soc_Mgha']=pd.to_numeric(lucas['SOCS (kg cm-2)'].astype(str).str.replace(' ',''),errors='coerce')*10  # file header says kg cm-2 but Zenodo is kg m-2; v2 used *10
# Actually prior note: kg m-2 ×10 = Mg/ha. Header typo in csv.
lat=pd.to_numeric(lucas['GPS_LAT'],errors='coerce'); lon=pd.to_numeric(lucas['GPS_LONG'],errors='coerce')
m=np.isfinite(lat)&np.isfinite(lon)&np.isfinite(lucas['soc_Mgha'])
lucas=lucas.loc[m]
if not os.path.exists(f'{O}/maps10__0_30.npz'):
  print('no map'); raise SystemExit(2)
z=np.load(f'{O}/maps10__0_30.npz'); mask=np.load('/workspace/soil_global/out/v4/mask.npy'); H,W=mask.shape
soc=np.full(mask.shape,np.nan); soc[mask]=z['soc']
rr=((90-lat.values)*6).astype(int).clip(0,H-1); cc=((lon.values+180)*6).astype(int).clip(0,W-1)
pred=soc[rr,cc]; ok=np.isfinite(pred)&np.isfinite(lucas['soc_Mgha'].values)
obs=lucas['soc_Mgha'].values[ok]; pr=pred[ok]
from sklearn.metrics import r2_score, mean_squared_error
res=dict(n=int(ok.sum()),r2=float(r2_score(obs,pr)),rmse=float(np.sqrt(mean_squared_error(obs,pr))),
         bias=float((pr-obs).mean()),median_bias=float(np.median(pr-obs)))
json.dump(res,open(f'{O}/lucas_val.json','w'),indent=1); print(res)
