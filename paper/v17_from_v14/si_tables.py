# v13 new SI tables S13-S18 (exec'd inside build.py namespace). Values from out/v13/summaries_v13.json (computed from out/v10).
def _sg(x,nd=0):
    v=round(x,nd); return ('−' if v<0 else '')+f'{abs(v):.{nd}f}'
def _ci(d,nd=0): return f"{_sg(d['mean'],nd)} ({_sg(d['p05'],nd)} to {_sg(d['p95'],nd)})"
def _ms(d,nd=0): return f"{_sg(d['mean'],nd)} ± {abs(d['sd']):.{nd}f}"
PRr=S13['present_regions']; FRr=S13['future_regions']; AR13=S13['area_Mkm2']
CN={'AS':'Asia','EU':'Europe','NA':'North America','SA':'South America','AF':'Africa','OC':'Oceania','Unassigned':'Unassigned coastal cells'}
orient(sm,True)
rows=[]; tot={k:0 for k in ['a','s30','s200','i30','i200','ma','po']}
for c in ['AS','EU','NA','SA','AF','OC','Unassigned']:
    d=PRr['continent'][c]; s200=d['soc_0_200']['mean']; i200=d['sic_0_200']['mean']
    rows.append([CN[c],f"{AR13['continent'][c]:.1f}",_ms(d['soc_0_30']),_ms(d['soc_0_200']),_ms(d['sic_0_30']),_ms(d['sic_0_200']),f0(s200+i200),f"{i200/(s200+i200)*100:.0f}",_ms(d['MA']),_ms(d['PO'])])
    for k,v in zip(['a','s30','s200','i30','i200','ma','po'],[AR13['continent'][c],d['soc_0_30']['mean'],s200,d['sic_0_30']['mean'],i200,d['MA']['mean'],d['PO']['mean']]): tot[k]+=v
rows.append(['**Sum (map integral)**',f"{tot['a']:.1f}",f0(tot['s30']),f0(tot['s200']),f0(tot['i30']),f0(tot['i200']),f0(tot['s200']+tot['i200']),f"{tot['i200']/(tot['s200']+tot['i200'])*100:.0f}",f0(tot['ma']),f0(tot['po'])])
table(sm,'Table S13.','Present-day soil carbon stocks by continent (Pg C; mean ± 1 SD across 10 fold-models; Monte Carlo perturbations not included, see Materials and Methods). Continents follow the country boundary raster used for all national statistics; unassigned cells are coastal or small-island cells whose centers fall outside every country polygon. Map integrals of fold-model means differ slightly from the Monte Carlo means in Table 1 and table S5. MAOC and POC: mineral soils, 0–30 cm. See fig. S17.',
      ['Continent','Area (Mkm²)','SOC 0–30','SOC 0–200','SIC 0–30','SIC 0–200','TC 0–200','SIC share (%)','MAOC 0–30','POC 0–30'],rows,font=7.5)
rows=[]
for c in ['AS','EU','NA','SA','AF','OC','Unassigned']:
    F=FRr['continent'][c]; r=[CN[c]]
    for s_ in ['126','245','370']: r+= [_sg(F[s_]['dsoc']['mean']), _sg(F[s_]['dsic']['mean'])]
    r+=[_ci(F['585']['dsoc']),_ci(F['585']['dsic'])]; rows.append(r)
table(sm,'Table S13 (continued).','Equilibrium change in SOC and SIC (0–200 cm, Pg C) by 2081–2100 by continent. Ensemble means of 10 fold-models × 6 GCMs; for SSP5-8.5 the 5th to 95th percentiles across the 60 members are given in parentheses. Continental sums equal the ensemble-mean map integrals (Fig. 5C).',
      ['Continent','ΔSOC SSP1-2.6','ΔSIC SSP1-2.6','ΔSOC SSP2-4.5','ΔSIC SSP2-4.5','ΔSOC SSP3-7.0','ΔSIC SSP3-7.0','ΔSOC SSP5-8.5','ΔSIC SSP5-8.5'],rows,font=7.5)
KN={'A':'Tropical','B':'Arid','C':'Temperate','D':'Cold','E':'Polar'}
rows=[]
for M_ in 'ABCDE':
    for key,grp,bold in [(M_,'koppen_main',True)]+[(k,'koppen_sub',False) for k in PRr['koppen_sub'] if k[0]==M_ and AR13['koppen_sub'][k]>=0.1]:
        d=PRr[grp][key]; a=AR13[grp][key]; s200=d['soc_0_200']['mean']; i200=d['sic_0_200']['mean']; F=FRr[grp][key]['585']
        nm_=f"{key} {KN[key]}" if bold else '   '+key
        r=[nm_,f"{a:.1f}",_ms(d['soc_0_30']),_ms(d['soc_0_200']),_ms(d['sic_0_200']),f"{i200/(s200+i200)*100:.0f}",f"{s200/a*10:.0f}",f"{i200/a*10:.0f}",_ci(F['dsoc']),_ci(F['dsic'])]
        if bold: r=[f'**{x}**' for x in r]
        rows.append(r)
table(sm,'Table S14.','Soil carbon by Köppen–Geiger zone (1991–2020; Beck et al. [@beck23]). Stocks in Pg C (mean ± 1 SD across 10 fold-models); densities in Mg C ha⁻¹ (0–200 cm); equilibrium change by 2081–2100 under SSP5-8.5 (0–200 cm; ensemble mean with 5th to 95th percentiles of 60 members). Main classes in bold; subclasses with area ≥0.1 Mkm² listed. Shares and changes refer to zones as defined for 1991–2020. See fig. S15.',
      ['Zone','Area (Mkm²)','SOC 0–30','SOC 0–200','SIC 0–200','SIC share (%)','SOC density','SIC density','Eq. ΔSOC SSP5-8.5','Eq. ΔSIC SSP5-8.5'],rows,font=7)
import pandas as _pd
cdf=_pd.DataFrame(S13['countries']); cdf=cdf[cdf.cont!='']; cdf['TC']=cdf.SOC_0_200+cdf.SIC_0_200; top=cdf.sort_values('TC',ascending=False).head(20)
rows=[]
for i,t in enumerate(top.itertuples(),1):
    rows.append([str(i),t.name,t.cont,f"{t.area_Mkm2:.2f}",f"{t.SOC_0_200:.1f}",f"{t.SIC_0_200:.1f}",f"{t.TC:.1f}",f"{t.SIC_0_200/t.TC*100:.0f}",f"{t.MAOC_0_30:.1f}",_sg(t.dSOC_585,1),_sg(t.dSIC_585,1),_sg(t.tl_dTC_585,1),f"{-t.Nloss_0_200_585*1000:.0f}"])
table(sm,'Table S15.','The 20 countries with the largest total soil carbon stocks (0–200 cm). Stocks and changes in Pg C from ensemble-mean 10′ maps; equilibrium (Eq.) and time-limited by 2100 (TL) changes for 2081–2100 under SSP5-8.5; nitrogen-driven SIC loss (0–200 cm, 2020–2050, SSP5-8.5 IMAGE fertilizer, loss-only) in Tg C. MAOC: mineral soils, 0–30 cm. Country boundaries: Natural Earth 1:50 m. See Fig. 2.',
      ['#','Country','Cont.','Area (Mkm²)','SOC','SIC','TC','SIC share (%)','MAOC 0–30','Eq. ΔSOC','Eq. ΔSIC','TL ΔTC by 2100','N-driven SIC loss (Tg)'],rows,font=7,widths=[0.3,1.5,0.45,0.6,0.6,0.6,0.6,0.55,0.6,0.65,0.6,0.65,0.7])
rows=[]; PG=S13['per_gcm']
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    for gc in ['ACCESS-CM2','EC-Earth3-Veg','MPI-ESM1-2-HR','UKESM1-0-LL','IPSL-CM6A-LR','MIROC6']:
        q=PG[f'{s_}_{gc}']; rows.append([lab,gc,_ms(q['dSOC_0_200']),_ms(q['dSIC_0_200']),_ms(q['dTC_0_200']),_ms(q['dSOC_0_30']),_ms(q['dMAOC']),_ms(q['dPOC']),_ms(q['dpH_mean'],2)])
    e=P10['future'][s_]['eq']
    rows.append([f'**{lab}**','**Ensemble (n = 60)**',f"**{_ci(e['dSOC_0_200'])}**",f"**{_ci(e['dSIC_0_200'])}**",f"**{_ci(e['dTC_0_200'])}**",f"**{_ci(e['dSOC_0_30'])}**",f"**{_ci(e['dMAOC'])}**",f"**{_ci(e['dPOC'])}**",f"**{_ci(e['dph'],2)}**"])
table(sm,'Table S16.','Equilibrium change by 2081–2100 for each CMIP6 model (Pg C; mean ± 1 SD across the 10 fold-models) and for the full ensemble (bold; mean with 5th to 95th percentiles of 60 members, as in table S7). ΔpH is the area-weighted mean change in topsoil pH. MAOC and POC: mineral soils, 0–30 cm. See fig. S18.',
      ['Scenario','GCM','ΔSOC 0–200','ΔSIC 0–200','ΔTC 0–200','ΔSOC 0–30','ΔMAOC 0–30','ΔPOC 0–30','ΔpH 0–30'],rows,font=7)
orient(sm,False)
rows=[]; TR=S13['transitions_main']
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    T=TR[s_]; items=sorted([(k,v) for k,v in T.items() if not k.startswith('_') and v['area_Mkm2']>=0.1],key=lambda kv:-kv[1]['area_Mkm2'])
    for k,v in items: rows.append([lab,k.replace('>','→'),f"{v['area_Mkm2']:.2f}",_ci(v['dSOC'],1),_ci(v['dSIC'],1)])
    tt=[v for k,v in T.items() if not k.startswith('_')]
    rows.append([f'**{lab}**','**All shifted land**',f"**{T['_any_main_change_Mkm2']:.1f}**",f"**{_sg(sum(v['map_dSOC'] for v in tt),1)}**",f"**{_sg(sum(v['map_dSIC'] for v in tt),1)}**"])
table(sm,'Table S17.','Köppen–Geiger main-class transitions (1991–2020 to 2071–2099; Beck et al. [@beck23]) with area ≥0.1 Mkm² and the associated equilibrium change in SOC and SIC (0–200 cm, Pg C, 2081–2100; ensemble mean with 5th to 95th percentiles of 60 members). A, tropical; B, arid; C, temperate; D, cold; E, polar. Totals on all shifted land equal the values in table S8. See fig. S21.',
      ['Scenario','Transition','Area (Mkm²)','Eq. ΔSOC','Eq. ΔSIC'],rows,font=7.5,widths=[0.9,1.3,0.8,1.6,1.6])
rows=[]; C_=PT13['counts']
for v,lab in [('SOC','SOC'),('SIC','SIC'),('pH','pH'),('BD','Bulk density')]:
    for l,ll in [('0_30','0–30'),('30_100','30–100'),('100_200','100–200')]:
        c=C_[f'{v}_{l}']; rows.append([lab,ll]+[f"{c[k]:,}" for k in ['AS','EU','NA','SA','AF','OC','Unassigned','total']])
table(sm,'Table S18.','Number of quality-controlled WoSIS profiles with harmonized values by variable, depth layer (cm), and continent (location of the profile; unassigned, profiles outside country polygons at 10′ resolution). Totals match table S1 and the main text; model training sets (table S3) are slightly smaller because they also require complete covariates. See fig. S22.',
      ['Variable','Layer','AS','EU','NA','SA','AF','OC','Unassigned','Total'],rows,font=7.5)
