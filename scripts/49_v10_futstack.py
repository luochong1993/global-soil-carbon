import numpy as np, pandas as pd, json, os
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
for s in ('126','245','370','585'):
  for g in GCMS:
    F=futF(g,s,'2081-2100'); print(g,s,F.shape,flush=True)
print('DONE')
