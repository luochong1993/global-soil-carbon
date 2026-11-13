import numpy as np, pandas as pd, json, geopandas as gpd, cartopy.io.shapereader as shp, rasterio.features as rf, rasterio.transform as rt
R='/workspace/soil_global'
mask=np.load(R+'/out/v4/mask.npy'); H,W=mask.shape
g=gpd.read_file(shp.natural_earth('50m','cultural','admin_0_countries'))
cm={'Asia':'AS','Europe':'EU','North America':'NA','South America':'SA','Africa':'AF','Oceania':'OC'}
ids=rf.rasterize([(geom,i+1) for i,geom in enumerate(g.geometry)],out_shape=(H,W),transform=rt.from_origin(-180,90,1/6,1/6),fill=0,dtype='int32')
cont=np.array(['']+[cm.get(c,'') for c in g['CONTINENT'].values],object)
p=pd.read_csv(R+'/data/points_v7_qc.csv',usecols=lambda c: c in ['profile_id','X','Y','year']+[f'{v}_{l}' for v in ['phaq','bdfiod','soc','sic','cfvo'] for l in ['0_30','30_100','100_200']])
r=np.clip(((90-p.Y)*6).astype(int),0,H-1); c=np.clip(((p.X+180)*6).astype(int),0,W-1)
p['cont']=cont[ids[r,c]]; p.loc[p.cont=='','cont']='Unassigned'; p['inmask']=mask[r,c]; p['row']=r; p['col']=c
out={'n_profiles':int(len(p)),'n_in_mask':int(p.inmask.sum())}
T={}
for v,lab in [('soc','SOC'),('sic','SIC'),('phaq','pH'),('bdfiod','BD')]:
  for l in ['0_30','30_100','100_200']:
    k=f'{v}_{l}'; ok=p[k].notna()
    T[f'{lab}_{l}']={**{cc:int((ok&(p.cont==cc)).sum()) for cc in ['AS','EU','NA','SA','AF','OC','Unassigned']},'total':int(ok.sum())}
out['counts']=T
# per 1 deg cell counts for maps, lat histogram
dens={}
for k in ['soc_0_30','sic_0_30','soc_100_200','sic_100_200']:
  ok=p[k].notna(); a=np.zeros((180,360)); np.add.at(a,(np.clip((90-p.Y[ok]).astype(int),0,179),np.clip((p.X[ok]+180).astype(int),0,359)),1); dens[k]=a
  out[f'latcount_{k}']=np.bincount(np.clip(np.floor(p.Y[ok]).astype(int)+90,0,179),minlength=180).tolist()
  out[f'n_cells1deg_{k}']=int((a>0).sum())
yrs=p.year.dropna(); out['year']={'n_dated':int(len(yrs)),'n_undated':int(p.year.isna().sum()),'median':float(yrs.median()) if len(yrs) else None}
np.savez_compressed(R+'/out/v13/points_density_1deg.npz',**dens)
json.dump(out,open(R+'/out/v13/points_summary_v13.json','w'),indent=1); print(json.dumps(out['counts'],indent=0)[:2000]); print(out['year'])
