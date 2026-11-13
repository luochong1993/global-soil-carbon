import numpy as np, rasterio, json, os, time, glob
from rasterio.windows import Window
O7='/workspace/soil_global/out/v7'; O8='/workspace/soil_global/out/v8'
while not os.path.exists(f'{O8}/frac_maps10.npz'): time.sleep(20)
mask=np.load('/workspace/soil_global/out/v4/mask.npy'); H,W=mask.shape
z=np.load(f'{O8}/frac_maps10.npz'); s10=np.load(glob.glob(f'{O7}/maps10_0_30.npz')[0])['soc']
r=np.full((H,W),np.nan,'float32'); r[mask]=np.where(s10>0,z['MA_0_30']/np.maximum(s10,1e-6),np.nan)
src=rasterio.open(f'{O7}/maps30s/socstock_0_30.tif'); prof=src.profile; prof.update(compress='deflate',tiled=True,blockxsize=512,blockysize=512,dtype='float32',nodata=np.nan,BIGTIFF='YES')
os.makedirs(f'{O8}/maps30s',exist_ok=True)
dm=rasterio.open(f'{O8}/maps30s/maocstock_0_30.tif','w',**prof); dp=rasterio.open(f'{O8}/maps30s/pocstock_0_30.tif','w',**prof)
TM=TP=0.0
for y0 in range(0,21600,600):
  a=src.read(1,window=Window(0,y0,43200,600)).astype('float32'); rows=(np.arange(y0,y0+600)//20); rr=r[rows][:,np.arange(43200)//20]
  rr=np.where(np.isfinite(rr),rr,np.nanmedian(r)); ma=a*rr; po=a-ma
  la=90-(np.arange(y0,y0+600)+.5)/120; ar=((111.32/120)**2*np.cos(np.deg2rad(la))*100)[:,None]
  TM+=np.nansum(ma*ar)*1e-9; TP+=np.nansum(po*ar)*1e-9
  dm.write(ma,1,window=Window(0,y0,43200,600)); dp.write(po,1,window=Window(0,y0,43200,600))
dm.close(); dp.close()
json.dump(dict(MAOC_30s_0_30=TM,POC_incl_organic_30s_0_30=TP,note='30-arcsec SOC (v7) x 10-arcmin MAOC share of total SOC; POC here includes organic-horizon C'),open(f'{O8}/frac30s.json','w'),indent=1); print('DONE',TM,TP)
