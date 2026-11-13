# Köppen-Geiger classification (Beck et al. 2018/2023 rules, 30 classes) from monthly T/P at 10 arcmin
import numpy as np, rasterio, glob, os
D='/workspace/soil_global/data'
NAMES=['Af','Am','Aw','BWh','BWk','BSh','BSk','Csa','Csb','Csc','Cwa','Cwb','Cwc','Cfa','Cfb','Cfc','Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','Dfa','Dfb','Dfc','Dfd','ET','EF']
def classify(T,P,lat):
    MAT=T.mean(0); MAP=P.sum(0); Tc=T.min(0); Th=T.max(0); Pd=P.min(0)
    nh=(lat>=0)[None,:,None]
    m=np.arange(12)[:,None,None]; summ=np.where(nh,(m>=3)&(m<=8),(m<=2)|(m>=9))
    Ps=np.where(summ,P,0).sum(0); Pw=MAP-Ps
    Psdry=np.where(summ,P,1e9).min(0); Pwdry=np.where(~summ,P,1e9).min(0)
    Pswet=np.where(summ,P,-1).max(0); Pwwet=np.where(~summ,P,-1).max(0)
    Pth=np.where(Pw>=0.7*MAP,2*MAT,np.where(Ps>=0.7*MAP,2*MAT+28,2*MAT+14))
    T10=(T>=10).sum(0)
    k=np.zeros(MAT.shape,np.uint8)
    s=(Psdry<40)&(Psdry<Pwwet/3); w=(Pwdry<Pswet/10)&~s
    def third(base,isD):
        a=Th>=22; b=~a&(T10>=4); d=isD&(Tc<-38); c=~a&~b&~d
        return np.where(a,base,np.where(b,base+1,np.where(c,base+2,base+3)))
    A=(Tc>=18); B=MAP<10*Pth; E=Th<=10
    C=(Th>10)&(Tc>0)&(Tc<18); Dd=(Th>10)&(Tc<=0)
    k=np.where(A, np.where(Pd>=60,1,np.where(Pd>=100-MAP/25,2,3)),k)
    k=np.where(C, np.where(s,third(8,False),np.where(w,third(11,False),third(14,False))),k)
    k=np.where(Dd, np.where(s,third(17,True),np.where(w,third(21,True),third(25,True))),k)
    k=np.where(B, np.where(MAP<5*Pth, np.where(MAT>=18,4,5), np.where(MAT>=18,6,7)),k)
    k=np.where(E, np.where(Th>0,29,30),k)
    return k
def read(files):
    a=[];
    for f in files:
        with rasterio.open(f) as r: x=r.read().astype('float32'); prof=r.profile; nod=r.nodata
        x[x<-1e30]=np.nan
        if nod is not None: x[x==nod]=np.nan
        a.append(x)
    return np.concatenate(a,0),prof
def save(k,valid,prof,name):
    k=np.where(valid,k,0).astype('uint8'); p=prof.copy(); p.update(count=1,dtype='uint8',nodata=0,compress='lzw')
    with rasterio.open(f'{D}/grids/{name}.tif','w',**p) as o: o.write(k,1)
T,prof=read(sorted(glob.glob(f'{D}/wc2.1_10m_tavg/*.tif'),key=lambda f:int(f.split('_')[-1][:-4])))
P,_=read(sorted(glob.glob(f'{D}/wc2.1_10m_prec/*.tif'),key=lambda f:int(f.split('_')[-1][:-4])))
lat=np.linspace(90,-90,T.shape[1]+1)[:-1]-90/T.shape[1]
valid=~np.isnan(T[0]); save(classify(T,P,lat),valid,prof,'kg_present')
for f in sorted(glob.glob(f'{D}/wc2.1_10m_tmin_MPI*_ssp*.tif')):
    tag=f.split('MPI-ESM1-2-HR_')[1][:-4]
    tn,_=read([f]); tx,_=read([f.replace('tmin','tmax')]); pp,_=read([f.replace('tmin','prec')])
    save(classify((tn+tx)/2,pp,lat),valid&~np.isnan(tn[0]),prof,'kg_'+tag); print(tag)
