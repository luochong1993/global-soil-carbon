# v5 N pathway calibrated to field/meta-analytic carbonate-C loss per kg N
# central 0.21 kg C/kg N (Zamanian et al. 2018 GCB doi:10.1111/gcb.14148; 50% NUE), high 0.32 (25% NUE),
# low 0.055 kg C/kg N (Conyers et al. 1996 doi:10.1016/0167-1987(95)01005-X: 46 kg CaCO3/ha/yr under 100 kg urea-N; upper 95 -> 0.114)
# NOy deposition weighted 0.5 relative to NHx/fertilizer (nitrate-acid deposition carries half the net acidity per N; assumption as v4)
import numpy as np, json, importlib.util, sys
src=open('/workspace/soil_global/scripts/13_v4_N_acidification.py').read().split('res={}; maps={}')[0]; exec(src)
z=np.load('/workspace/soil_global/out/v5/maps_b0.npz'); S1,S2=z['sic_0_30'],z['sic_30_100']
COEF={'low':0.055,'low2':0.114,'central':0.21,'high':0.32}; res={}
for s in ('126','370','585'):
    for (y0,y1) in [(2021,2050),(2021,2100)]:
        nhf,noy,fert=cumN(s,y0,y1); o={}
        for lab,k in COEF.items():
            Cpot=(nhf+0.5*noy)*k/1000.0   # Mg C/ha
            l1=np.minimum(Cpot,S1); l2=np.minimum(Cpot-l1,S2)
            o[lab]=dict(coef=k,loss_0_30=float((l1*area).sum()*1e-9),loss_30_100=float((l2*area).sum()*1e-9),
                        uncapped_potential=float((Cpot*area).sum()*1e-9),on_calcareous_frac_of_potential=float(((Cpot*area)[S1>1]).sum()/(Cpot*area).sum()))
            if lab=='central': np.save(f'/workspace/soil_global/out/v5/Nloss_{s}_{y0}_{y1}.npy',(l1+l2).astype('float32'))
        o['N_Tg_yr']=float(((nhf+noy)*area).sum()/1e9/(y1-y0+1)); res[f'ssp{s}_{y0}_{y1}']=o; print(s,y0,y1,{k:round(v['loss_0_30']+v['loss_30_100'],2) for k,v in o.items() if isinstance(v,dict)},flush=True)
json.dump(res,open('/workspace/soil_global/out/v5/N_calib.json','w'),indent=1)
