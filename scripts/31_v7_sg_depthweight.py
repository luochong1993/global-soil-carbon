# Depth-weight SoilGrids 1000m layers to 0-30, 30-100, 100-200 cm; write compressed GeoTIFF
import numpy as np, rasterio, os, glob
from rasterio.enums import Compression
D='/workspace/soil_global/data/sg1km'; O=D
# wait until all files present
need=[]
for v in ['cfvo','bdod','clay','sand','cec']:
  for d in ['0-5cm','5-15cm','15-30cm','30-60cm','60-100cm','100-200cm']:
    need.append(f'{D}/{v}_{d}_mean_1000.tif')
missing=[f for f in need if not os.path.exists(f) or os.path.getsize(f)<1e6]
if missing:
  print('WAITING',len(missing),missing[:3]); raise SystemExit(2)
# weights
W030=[( '0-5cm',5),('5-15cm',10),('15-30cm',15)]
W30100=[('30-60cm',30),('60-100cm',40)]
W100200=[('100-200cm',100)]
def wavg(v,parts,outname):
  arrs=[]; w=[]; ref=None
  for d,th in parts:
    with rasterio.open(f'{D}/{v}_{d}_mean_1000.tif') as r:
      a=r.read(1).astype('float32'); nd=r.nodata
      if nd is not None: a[a==nd]=np.nan
      a[a<-1000]=np.nan; arrs.append(a); w.append(th); ref=r if ref is None else ref
  W=sum(w); num=sum(a*th for a,th in zip(arrs,w)); den=sum(th*(~np.isnan(a)) for a,th in zip(arrs,w))
  out=np.where(den>0,num/np.maximum(den,1),np.nan)
  # scale: SoilGrids stores clay/sand/cfvo/cec as dg/kg or mmol → keep as-is; write int16 with nodata
  profile=ref.profile.copy(); profile.update(dtype='float32',compress='deflate',tiled=True,predictor=2,zlevel=6,nodata=np.nan)
  with rasterio.open(f'{O}/{v}_{outname}_mean_1000.tif','w',**profile) as dst: dst.write(out.astype('float32'),1)
  print(v,outname,np.nanmean(out),flush=True)
for v in ['cfvo','bdod','clay','sand','cec']:
  wavg(v,W030,'0-30cm'); wavg(v,W30100,'30-100cm'); wavg(v,W100200,'100-200cm')
print('DONE SG')
