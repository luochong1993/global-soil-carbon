# Fast global 30" mosaics — small tiles, land-only predict, climate from 10' bilinear indices + elev 30"
import numpy as np, json, os, joblib, rasterio, gc
from rasterio.transform import from_origin
from rasterio.windows import Window
O7='/workspace/soil_global/out/v7'; D='/workspace/soil_global/data'
os.makedirs(O7+'/maps30s',exist_ok=True)
src=open('/workspace/soil_global/scripts/12_v4_depth_model.py').read().split("p=pd.read_csv(f'{D}/points_v4_depths.csv')")[0]
exec(src)
models=joblib.load(f'{O7}/models_v7.joblib'); meta=json.load(open(f'{O7}/train_meta.json'))
M=models['_0_30']; Pscale=float(meta.get('Pscale',0.47)); ORG=120.0
H10,W10=S0x.shape[1],S0x.shape[2]
ELEV=f'{D}/wc30s/wc2.1_30s_elev.tif'
H30,W30=21600,43200; res=1/120.0
transform30=from_origin(-180,90,res,res)
nc=S0x.shape[0]

def write_profile(path):
  if os.path.exists(path): return
  prof=dict(driver='GTiff',height=H30,width=W30,count=1,dtype='float32',crs='EPSG:4326',
            transform=transform30,compress='deflate',tiled=True,blockxsize=512,blockysize=512,predictor=2,nodata=np.nan)
  with rasterio.open(path,'w',**prof) as dst: pass

paths=dict(ph=f'{O7}/maps30s/ph_0_30.tif',soc=f'{O7}/maps30s/socstock_0_30.tif',sic=f'{O7}/maps30s/sicstock_0_30.tif')
for p in paths.values(): write_profile(p)
done_f=f'{O7}/maps30s/strips_done.txt'; done=set(open(done_f).read().split()) if os.path.exists(done_f) else set()
STRIP=400; CHUNK=3600  # ~3.3° × 30°

ie=list(namesx).index('elev') if 'elev' in namesx else 21
islope=list(namesx).index('slope') if 'slope' in namesx else 22

for r0 in range(0,H30,STRIP):
  r1=min(r0+STRIP,H30); hs=r1-r0
  rr=((90-(np.arange(r0,r1)+0.5)*res)*6).astype(np.int32).clip(0,H10-1)
  for c0 in range(0,W30,CHUNK):
    c1=min(c0+CHUNK,W30); ws=c1-c0; key=f'{r0}_{c0}'
    if key in done: continue
    cc=(((-180+(np.arange(c0,c1)+0.5)*res)+180)*6).astype(np.int32).clip(0,W10-1)
    # land from 10' mask via meshgrid only for mask (uint8)
    RR,CC=np.meshgrid(rr,cc,indexing='ij')
    land=mask[RR,CC]
    del RR,CC
    # elev 30s
    try:
      with rasterio.open(ELEV) as ds:
        ev=ds.read(1,window=Window(c0,r0,ws,hs)).astype('float32'); ev[~np.isfinite(ev)|(ev<-1e30)]=np.nan
    except Exception:
      ev=np.full((hs,ws),np.nan,'float32')
    out_ph=np.full((hs,ws),np.nan,'float32'); out_soc=out_ph.copy(); out_sic=out_ph.copy()
    iy,ix=np.where(land)
    n=len(iy)
    if n>20:
      # covariates for land only: (n, nc)
      Ff=np.empty((n,nc),np.float32)
      for j in range(nc):
        Ff[:,j]=S0x[j,rr[iy],cc[ix]]
      # elev 30s override
      e30=ev[iy,ix]
      m=np.isfinite(e30); Ff[m,ie]=e30[m]
      # fill nan
      for j in range(nc):
        col=Ff[:,j]; bad=~np.isfinite(col)
        if bad.any():
          med=np.nanmedian(col); Ff[bad,j]=0 if not np.isfinite(med) else med
      ph=M['MpH'].predict(Ff).astype('float32')
      FS=np.column_stack([Ff,ph])
      sicc=(M['C'].predict_proba(FS)[:,1]*np.exp(M['R'].predict(FS))*M['sm']).astype('float32')
      Po=np.clip(M['Porg'].predict_proba(Ff)[:,1]*Pscale,0,1).astype('float32')
      socm=np.expm1(M['MO'].predict(Ff)).clip(0,ORG).astype('float32')
      bdm=np.clip(M['MB'].predict(np.column_stack([Ff,np.log1p(socm)])),0.5,2.0).astype('float32')
      f=(1-M['CF_med']/100)*30*0.1
      out_ph[iy,ix]=ph
      out_soc[iy,ix]=(Po*M['cd']+(1-Po)*socm*bdm)*f
      out_sic[iy,ix]=(1-Po)*sicc*bdm*f
      del Ff,FS,ph,sicc,Po,socm,bdm
    win=Window(c0,r0,ws,hs)
    with rasterio.open(paths['ph'],'r+') as dst: dst.write(out_ph,1,window=win)
    with rasterio.open(paths['soc'],'r+') as dst: dst.write(out_soc,1,window=win)
    with rasterio.open(paths['sic'],'r+') as dst: dst.write(out_sic,1,window=win)
    with open(done_f,'a') as fh: fh.write(key+'\n')
    done.add(key)
    if n>1000: print('OK',key,'land',n,'soc',float(np.nanmean(out_soc)),flush=True)
    del out_ph,out_soc,out_sic,land,ev,iy,ix; gc.collect()

print('Computing 30s stocks...',flush=True)
lat=90-(np.arange(H30)+0.5)*res
row_area=(111.32*res)*(111.32*res*np.cos(np.deg2rad(lat)))*100
soc_pg=sic_pg=0.0; nland=0
with rasterio.open(paths['soc']) as ds_soc, rasterio.open(paths['sic']) as ds_sic:
  for r0 in range(0,H30,STRIP):
    r1=min(r0+STRIP,H30)
    soc=ds_soc.read(1,window=Window(0,r0,W30,r1-r0))
    sic=ds_sic.read(1,window=Window(0,r0,W30,r1-r0))
    a=row_area[r0:r1][:,None]; m=np.isfinite(soc)
    soc_pg+=float(np.nansum(np.where(m,soc*a,0)))*1e-9
    sic_pg+=float(np.nansum(np.where(np.isfinite(sic),sic*a,0)))*1e-9
    nland+=int(m.sum())
stocks=dict(SOC_0_30_Pg=soc_pg,SIC_0_30_Pg=sic_pg,land_pixels=nland,grid='30arcsec',
            compare_10arcmin=json.load(open(f'{O7}/stocks10.json'))['_0_30'])
json.dump(stocks,open(f'{O7}/stocks30_0_30.json','w'),indent=1)
print('STOCKS30',stocks,flush=True); print('DONE 30S',flush=True)
