# v13 main-text Tables 1 and 2 (exec'd inside build.py namespace). All values from out/v10/paper_numbers_v10.json.
def _sg(x,nd=0):
    v=round(x,nd); return ('−' if v<0 else '')+f'{abs(v):.{nd}f}'
def _ci(d,nd=0): return f"{_sg(d['mean'],nd)} ({_sg(d['p05'],nd)} to {_sg(d['p95'],nd)})"
head(doc,'Tables',13)
pr=P10['present']; L3=['_0_30','_30_100','_100_200']
def _h(d): return hstat(d)
rows=[]
socm=[pr[l]['SOC']['mean'] for l in L3]; sicm=[pr[l]['SIC']['mean'] for l in L3]; orgm=[pr[l]['SOC_org_model_only']['mean'] for l in L3]
rows.append(['SOC (total)']+[_h(pr[l]['SOC']) for l in L3]+[f0(socm[0]+socm[1])+'*',_h(pr['_0_200']['SOC'])])
rows.append(['   of which organic horizons†']+[f0(x) for x in orgm]+[f0(orgm[0]+orgm[1]),f0(sum(orgm))])
rows.append(['SIC']+[_h(pr[l]['SIC']) for l in L3]+[f0(sicm[0]+sicm[1])+'*',_h(pr['_0_200']['SIC'])])
rows.append(['TC = SOC + SIC']+[_h(pr[l]['TC']) for l in L3]+[f0(socm[0]+socm[1]+sicm[0]+sicm[1])+'*',_h(pr['_0_200']['TC'])])
rows.append(['SIC share of TC (%)']+[f"{sicm[i]/(socm[i]+sicm[i])*100:.0f}" for i in range(3)]+[f"{(sicm[0]+sicm[1])/(socm[0]+socm[1]+sicm[0]+sicm[1])*100:.0f}",f"{pr['_0_200']['SIC']['mean']/pr['_0_200']['TC']['mean']*100:.0f}"])
rows.append(['MAOC (mineral soils)',_h(pr['_0_30']['MAOC']),_h(pr['_30_100']['MAOC']),'—',_h(pr['_0_100']['MAOC']),'—'])
rows.append(['POC (mineral soils)',_h(pr['_0_30']['POC']),_h(pr['_30_100']['POC']),'—',_h(pr['_0_100']['POC']),'—'])
table(doc,'Table 1.','Global soil carbon stocks by pool and depth (Pg C; 10′ analysis grid). Values are means with 90% CI (5th–95th percentiles) and ±1 SD from 10 fold-models × Monte Carlo perturbations of bulk density, coarse fragments, effective thickness, and organic C density (n = 3000). *0–100 cm SOC, SIC, and TC are sums of layer means (no joint CI computed). †Fold-model means of the organic-horizon (peat) component, scaled to the PEATMAP area. MAOC and POC exclude organic horizons; subsoil fractions rest on 34 fraction records. Layer-level details in table S5; regional breakdowns in tables S13 to S15.',
      ['Pool','0–30 cm','30–100 cm','100–200 cm','0–100 cm','0–200 cm'],rows,widths=[1.3,1.05,1.05,1.05,1.0,1.1],font=7.5)
rows=[]
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    e=P10['future'][s_]['eq']; tl=P10['future'][s_]['time_limited']; n=P10['N']['scenarios'][s_]
    rows.append([lab,_ci(e['dSOC_0_200']),_ci(e['dSIC_0_200']),_ci(e['dTC_0_200']),_ci(tl['dTC_0_200']),
                 f"{_sg(e['dMAOC']['mean'])} / {_sg(tl['dMAOC']['mean'])}",f"{_sg(e['dPOC']['mean'])} / {_sg(tl['dPOC']['mean'])}",
                 f"{_sg(n['loss_0_30']['mean'],1)} / {_sg(n['loss_0_200']['mean'],1)}"+('‡' if s_=='245' else '')])
table(doc,'Table 2.','Projected change in soil carbon by scenario (Pg C; signed, negative = decrease of the soil stock). Climate-driven changes are for 2081–2100 relative to the WorldClim 1970–2000 baseline: equilibrium (Eq.) and time-limited by 2100 (TL; first-order response with τ sampled log-uniformly), means with 90% CI across 10 fold-models × 6 GCMs (TL additionally samples τ). MAOC and POC: topsoil (0–30 cm) mineral soils, equilibrium / by 2100. Nitrogen-driven ΔSIC: loss-only totals over 2020–2050 from ISIMIP3b IMAGE fertilizer inputs with ΔpH = −0.06 N_in + 0.11, 0–30 / 0–200 cm. ‡SSP2-4.5 fertilizer interpolated as the mean of SSP1-2.6 and SSP3-7.0. Nitrogen and climate experiments are separate and not additive. Details in tables S7, S9, S10, S16, and S19.',
      ['Scenario','Eq. ΔSOC 0–200 cm','Eq. ΔSIC 0–200 cm','Eq. ΔTC 0–200 cm','TL ΔTC 0–200 cm by 2100','ΔMAOC Eq. / TL','ΔPOC Eq. / TL','N-driven ΔSIC (loss-only) 0–30 / 0–200 cm'],rows,widths=[0.8,1.05,0.95,0.95,1.0,0.75,0.75,0.85],font=7.5)

# v14: Table 3 -- net budget and direction of change by pool and process (SSP5-8.5). Values from out/v10 and out/v14/direction_v14.json (derived).
def _sp3(x,nd=0):
    v=round(x,nd); return ('−' if v<0 else ('+' if v>0 else ''))+f'{abs(v):.{nd}f}'
def _d3(d,nd=0):
    a='↓' if d['p95']<0 else ('↑' if d['p05']>0 else '↑↓'); return f"{a} {_sp3(d['mean'],nd)} ({_sp3(d['p05'],nd)} to {_sp3(d['p95'],nd)})"
def _m3(x,nd=0): return ('↓ ' if x<0 else '↑ ')+_sp3(x,nd)
e=P10['future']['585']['eq']; tl=P10['future']['585']['time_limited']; n=P10['N']['scenarios']['585']; D5=DIR14['ssp']['585']; c=D5['committed_after_2100']; sh=D5['shift']; lp=D5['land_pct']; b=D5['SIC_by2100_both_drivers']
rows=[['Climate change, equilibrium',_d3(e['dSOC_0_200']),_d3(e['dSIC_0_200']),_d3(e['dTC_0_200']),_d3(e['dMAOC']),_d3(e['dPOC'])],
      ['Climate change, realized by 2100',_d3(tl['dSOC_0_200']),_d3(tl['dSIC_0_200']),_d3(tl['dTC_0_200']),_d3(tl['dMAOC']),_d3(tl['dPOC'])],
      ['Committed after 2100 (equilibrium minus by 2100)',_m3(c['SOC']),_m3(c['SIC']),_m3(c['TC']),_m3(c['MAOC']),_m3(c['POC'],1)],
      ['Nitrogen acidification, 2020–2050 (separate experiment)','not modeled',f"↓ {_sp3(n['loss_0_200']['mean'],1)} loss-only; {_sp3(n['net_0_200']['mean'],1)} net (0–30 cm: {_sp3(n['loss_0_30']['mean'],1)}; {_sp3(n['net_0_30']['mean'],1)})",'not added','not modeled','not modeled'],
      [f"Köppen–Geiger-shifted land ({sh['area_Mkm2']:.1f} Mkm²), equilibrium",_m3(sh['SOC']),_m3(sh['SIC']),_m3(sh['TC']),'—','—'],
      ['Share of mapped land with this direction, equilibrium',f"ΔSOC < 0 on {lp['SOC_decrease']:.0f}%",f"ΔSIC > 0 on {lp['SIC_increase']:.0f}%",f"ΔTC < 0 on {lp['TC_decrease']:.0f}%",'—','—'],
      ['SIC by 2100, climate and nitrogen compared (not a joint simulation)','—',f"↑↓ {_sp3(b['central_sum_net'])} to {_sp3(b['central_sum_loss'])} (central values; not resolved)",'↓ (SOC term dominates)','—','—']]
table(doc,'Table 3.','Net soil carbon budget and direction of change by pool and process under SSP5-8.5 (Pg C; signed, negative = decrease of the soil stock). ↓, decrease; ↑, increase; ↑↓, direction not resolved (90% CI includes zero). Climate: 2081–2100 relative to the WorldClim 1970–2000 baseline; means with 5th to 95th percentiles of 10 fold-models × 6 GCMs (by 2100 additionally samples τ). SOC, SIC, and TC in 0–200 cm; MAOC and POC in 0–30 cm of mineral soils (separate fraction model; not additive with ΔSOC). The realized TC decrease by 2100 exceeds the equilibrium decrease because the SIC increase is realized slowly; after 2100, TC would partly recover. Nitrogen-driven changes come from a separate experiment and are not added to the climate totals; comparing them with the realized SIC increase leaves the direction of SIC change by 2100 unresolved under SSP5-8.5 (central sum −4 Pg with net or −10 Pg with loss-only nitrogen totals; table S19). All scenarios in table S19.',
      ['Process','ΔSOC','ΔSIC','ΔTC = ΔSOC + ΔSIC','ΔMAOC (0–30 cm)','ΔPOC (0–30 cm)'],rows,widths=[1.5,1.05,1.45,1.05,1.0,0.95],font=7.5)
