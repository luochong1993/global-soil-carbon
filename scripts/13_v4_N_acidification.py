# Huang-style N-driven acidification pathway, implemented as a proton budget on carbonate-bearing soils.
# N inputs: ISIMIP3b n-deposition (NHx+NOy, g N m-2 mon-1) + n-fertilizer-5crops (IMAGE, kg N ha-1 crop yr-1) x landuse-5crops fractions.
# Net H+ per mol N (assumptions, Bolan et al. 1991 stoichiometry): NHx & fertilizer N: 1.0 (range 0.5-1.5); NOy: 0.5 (0.25-0.75).
# Carbonate consumed: CaCO3 + 2H+ -> Ca2+ + CO2 + H2O (0.5 mol C per H+, central/low) to CaCO3 + H+ -> Ca2+ + HCO3- (1.0, high).
# Protons consumed first in 0-30 cm, overflow to 30-100 cm; loss capped by SIC stock. Uniform pH buffer by carbonates assumed.
import numpy as np, netCDF4 as nc, json, os
I='/workspace/soil_global/data/isimip'; O='/workspace/soil_global/out/v4'
mask=np.load(f'{O}/mask.npy'); H,W=mask.shape
lat=np.linspace(90,-90,H+1)[:-1]-90/H; area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
def up(a):  # 0.5deg (lat descending? check) -> 10'
    return np.repeat(np.repeat(a,3,0),3,1)
def flip(d,a): return a if d.variables['lat'][0]>d.variables['lat'][-1] else a[::-1]
CROPS={'c3ann':['c3ann_irrigated','c3ann_rainfed'],'c3per':['c3per_irrigated_food','c3per_irrigated_bf','c3per_rainfed_food','c3per_rainfed_bf'],
       'c4ann':['c4ann_irrigated','c4ann_rainfed'],'c4per':['c4per_irrigated_food','c4per_irrigated_bf','c4per_rainfed_food','c4per_rainfed_bf'],'c3nfx':['c3nfx_irrigated','c3nfx_rainfed']}
def cumN(s,y0,y1):
    """cumulative kg N ha-1 over years y0..y1 inclusive: (NHx+fert, NOy)"""
    t0,t1=(y0-2015),(y1-2015)
    nh=nc.Dataset(f'{I}/ndep-nhx_ssp{s}_monthly_2015_2100.nc'); no=nc.Dataset(f'{I}/ndep-noy_ssp{s}_monthly_2015_2100.nc')
    # monthly index: file time counts months since 1661; first record = Jan 2015
    NH=flip(nh,np.ma.filled(nh.variables['nhx'][t0*12:(t1+1)*12].sum(0),0))*10
    NO=flip(no,np.ma.filled(no.variables['noy'][t0*12:(t1+1)*12].sum(0),0))*10
    fe=nc.Dataset(f'{I}/n-fertilizer-5crops_image_2015soc_ssp{s}_annual_2015_2100.nc'); lu=nc.Dataset(f'{I}/landuse-5crops_image_ssp{s}_annual_2015_2100.nc')
    FT=np.zeros((360,720))
    for c,vs in CROPS.items():
        rate=np.ma.filled(fe.variables[f'{c}_fertl'][t0:t1+1],0); fr=sum(np.ma.filled(lu.variables[v][t0:t1+1],0) for v in vs)
        FT+=np.nan_to_num((rate*fr).sum(0))
    FT=flip(fe,FT)
    return up(NH+FT)[mask], up(NO)[mask], up(FT)[mask]
res={}; maps={}
for d in ['_0_30','_30_100']:
    z=np.load(f'{O}/depth{d}.npz'); t={'_0_30':30,'_30_100':70}[d]
    maps[d]=z['sic0']*z['bd0']*(1-z['CF']/100)*t*0.1   # Mg C ha-1
S1,S2=maps['_0_30'],maps['_30_100']
for s in ('126','370','585'):
    for (y0,y1) in [(2021,2050),(2021,2100)]:
        nhf,noy,fert=cumN(s,y0,y1)
        out={}
        for lab,(aN,aO,beta) in {'low':(0.5,0.25,0.5),'central':(1.0,0.5,0.5),'high':(1.5,0.75,1.0)}.items():
            Hmol=(nhf*aN+noy*aO)/14.0*1000   # mol H+ ha-1
            Cpot=Hmol*beta*12/1e6            # Mg C ha-1 potential carbonate-C dissolution
            l1=np.minimum(Cpot,S1); l2=np.minimum(Cpot-l1,S2)
            out[lab]=dict(SIC_loss_0_30_Pg=float((l1*area).sum()*1e-9),SIC_loss_30_100_Pg=float((l2*area).sum()*1e-9),
                          acid_on_noncalcareous_frac=float(((Cpot>0)&(S1<=0.01)).mean()))
            if lab=='central': np.save(f'{O}/Nloss_{s}_{y0}_{y1}_0_30.npy',l1.astype('float32'))
        out['N_input_Tg_per_yr']=dict(total=float(((nhf+noy)*area).sum()/1e9/(y1-y0+1)),fertilizer=float((fert*area).sum()/1e9/(y1-y0+1)))
        res[f'ssp{s}_{y0}_{y1}']=out; print(s,y0,y1,json.dumps(out),flush=True)
json.dump(res,open(f'{O}/N_acidification.json','w'),indent=1)
