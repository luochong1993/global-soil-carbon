# v14: SI table chunks (old numbering) -> TCHUNK; overrides for S8 (single 137.3 Mkm2 denominator, co-loss column) and S9 (signed),
# and new S19 (direction of change). exec'd inside build.py namespace. All values from out/v10, out/v13, out/v14/direction_v14.json (derived).
import json as _json
TCHUNK={int(k):(v[0],v[1]) for k,v in _json.load(open('/workspace/soil_global/paper/v17_from_v14/_table_chunks.json')).items()}
SSPL=[('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]
def _sp(x,nd=0):
    v=round(x,nd); return ('−' if v<0 else ('+' if v>0 else ''))+f'{abs(v):.{nd}f}'
def _dci(d,nd=0):
    m,lo,hi=d['mean'],d['p05'],d['p95']; a='↓' if hi<0 else ('↑' if lo>0 else '↑↓')
    return f"{a} {_sp(m,nd)} ({_sp(lo,nd)} to {_sp(hi,nd)})"
def _dm(x,nd=0):
    a='↓' if x<0 else '↑'; return f"{a} {_sp(x,nd)}"
TCHUNK[8]=(True,r'''
LAND=DIR14['land_Mkm2']; rows=[]
for s_,lab in SSPL:
    z=P10['future'][s_]['zone']; ms=P10['future'][s_]['map_sums_equal_mean']; dq=DIR14['ssp'][s_]
    rows.append([lab,f"{z['land_shift_Mkm2']:.1f} ({z['land_shift_Mkm2']/LAND*100:.1f}%)",
                 f"{dq['quadrant_Mkm2']['tradeoff']:.1f} ({dq['quadrant_pct']['tradeoff']:.0f}%)",f"{dq['quadrant_Mkm2']['coloss']:.1f} ({dq['quadrant_pct']['coloss']:.0f}%)",
                 _sp(z['dSOC_on_shift_Pg'],1),_sp(z['dSIC_on_shift_Pg'],1),_sp(z['dSOC_on_shift_Pg']+z['dSIC_on_shift_Pg'],1),_sp(ms['dSOC_0_200'],1),_sp(ms['dSIC_0_200'],1)])
q5=DIR14['ssp']['585']['quadrant_pct']
table(sm,'Table S8.','Köppen–Geiger zone shifts (2071–2099 versus 1991–2020; Beck et al. [@beck23]), trade-off and co-loss areas, and ensemble-mean equilibrium carbon changes (0–200 cm, 2081–2100; signed, negative = decrease). All area percentages use the 137.3 Mkm² of mapped land (10′ analysis mask) as denominator. Trade-off, ΔSOC < 0 and ΔSIC > 0; co-loss, ΔSOC < 0 and ΔSIC < 0 (ensemble-mean maps). Under SSP5-8.5, the land-area shares of the four ΔSOC/ΔSIC quadrants in fig. S27A are: SOC decrease with SIC increase (trade-off), '+f"{q5['tradeoff']:.0f}"+'%; both increase, '+f"{q5['bothgain']:.0f}"+'%; both decrease (co-loss), '+f"{q5['coloss']:.0f}"+'%; SOC increase with SIC decrease, '+f"{q5['socgain_sicloss']:.0f}"+'%. Quadrant shares for all scenarios are given in table S19.',
      ['Scenario','Shifted land, Mkm² (% of mapped land)','Trade-off area, Mkm² (%)','Co-loss area, Mkm² (%)','ΔSOC on shifted land','ΔSIC on shifted land','ΔTC on shifted land','ΔSOC total','ΔSIC total'],rows)
''')
TCHUNK[9]=(True,r'''
rows=[]
huang_pair={'126':(10,'High-Ambition-N'),'245':(14,'Medium-Ambition-N*'),'370':(14,'Medium-Ambition-N'),'585':(23,'Low-Ambition-N')}
for s_,lab in SSPL:
    n=P10['N']['scenarios'][s_]; hv,hl=huang_pair[s_]
    nin=n['Nin_crop_mean']['mean']; dph=n['dph_crop_mean']['mean']
    l30=n['loss_0_30']['mean']; n30=n['net_0_30']['mean']; l200=n['loss_0_200']['mean']; n200=n['net_0_200']['mean']
    scale=hv/abs(l30)
    if s_ in ('126','370','585'):
        fo=N6[f'ssp{s_}_2020_2050']['fert_only']; fd=N6[f'ssp{s_}_2020_2050']['fert_plus_dep']; zz=N6[f'ssp{s_}_2020_2050']['zamanian_stoichiometry']
        fdl=-abs(fd.get('loss_only_FD_0_30', fd.get('delta_our_FD_0_30',0)))
        zc=zz['central']['loss_0_30']; zl=zz['low']['loss_0_30']; zh=zz['high']['loss_0_30']
        rows.append([lab,f"{nin:.2f} ({fo['Nin_p90']:.1f})",f"{_sp(dph,3)} ({fo['dph_frac_negative']*100:.0f}%)",_sp(l30,2),_sp(n30,2),_sp(fdl,2),_sp(l200,1),_sp(n200,1),f"−{zc:.2f} (−{zl:.2f} to −{zh:.2f})",f"{hv} ({hl})",f"~{scale:.1f}×"])
    else:
        rows.append([lab,f"{nin:.2f} (interp.)",_sp(dph,3),_sp(l30,2),_sp(n30,2),'—',_sp(l200,1),_sp(n200,1),'—',f"{hv} ({hl})",f"~{scale:.1f}×"])
table(sm,'Table S9.','Nitrogen-driven change in SIC over 2020–2050 (ΔSIC_N, Pg C; signed, negative = decrease) with ΔpH = −0.06 N_in + 0.11 and ISIMIP3b IMAGE fertilizer inputs (fold-model ensemble means). N_in, mean cumulative cropland fertilizer input (Mg N ha⁻¹; 90th percentile in parentheses where available). Loss-only totals set cells with ΔSIC > 0 to zero; net totals include the increases in cells where the positive intercept raises pH. The topsoil ΔpH is applied to all layers in 0–200 cm totals. SSP2-4.5 IMAGE fertilizer was interpolated as mean(SSP1-2.6, SSP3-7.0); GLOBIOM/INMS not obtained. Zamanian: stoichiometric 0.21 (0.055–0.32) kg C per kg N [@zamanian18] from the IMAGE fertilizer-only run. Huang et al. [@huang24] values are published topsoil loss magnitudes (positive). Scale factor: simple ratio of the Huang et al. topsoil loss to the IMAGE loss-only magnitude (approximate). *Huang Medium-Ambition-N paired with interpolated SSP2-4.5.',
      ['IMAGE scenario','N_in','Mean cropland ΔpH (% cells negative)','ΔSIC_N loss-only 0–30 (fert.)','ΔSIC_N net 0–30 (fert.)','ΔSIC_N loss-only 0–30 (fert. + dep.)','ΔSIC_N loss-only 0–200 (fert.)','ΔSIC_N net 0–200 (fert.)','ΔSIC_N Zamanian 0–30','Huang et al. loss 0–30 (scenario)','Approx. scale'],rows,font=7.5)
''')
TCHUNK[19]=(True,r'''
rows=[]
for s_,lab in SSPL:
    e=P10['future'][s_]['eq']; tl=P10['future'][s_]['time_limited']; dq=DIR14['ssp'][s_]
    rows.append(['Climate, equilibrium (2081–2100)',lab,_dci(e['dSOC_0_200']),_dci(e['dSIC_0_200']),_dci(e['dTC_0_200']),_dci(e['dMAOC']),_dci(e['dPOC'])])
for s_,lab in SSPL:
    tl=P10['future'][s_]['time_limited']
    rows.append(['Climate, conditional by-2100',lab,_dci(tl['dSOC_0_200']),_dci(tl['dSIC_0_200']),_dci(tl['dTC_0_200']),_dci(tl['dMAOC']),_dci(tl['dPOC'])])
for s_,lab in SSPL:
    c=DIR14['ssp'][s_]['committed_after_2100']
    rows.append(['Committed after 2100 (equilibrium minus by 2100; means)',lab,_dm(c['SOC']),_dm(c['SIC']),_dm(c['TC']),_dm(c['MAOC']),_dm(c['POC'],1)])
for s_,lab in SSPL:
    n=P10['N']['scenarios'][s_]
    rows.append(['Nitrogen acidification, 2020–2050 (separate experiment)',lab+('‡' if s_=='245' else ''),'not modeled',f"{_dci(n['loss_0_200'],1)} loss-only; {_sp(n['net_0_200']['mean'],1)} net (0–30 cm: {_sp(n['loss_0_30']['mean'],1)}; {_sp(n['net_0_30']['mean'],1)})",'not added','not modeled','not modeled'])
for s_,lab in SSPL:
    sh=DIR14['ssp'][s_]['shift']
    rows.append(['Köppen–Geiger-shifted land (equilibrium; map integral)',f"{lab} ({sh['area_Mkm2']:.1f} Mkm²)",_dm(sh['SOC'],1),_dm(sh['SIC'],1),_dm(sh['TC'],1),'—','—'])
table(sm,'Table S19.','Direction and magnitude of change in each soil carbon pool by process and scenario (Pg C; signed, negative = decrease). ↓, decrease; ↑, increase; ↑↓, direction not resolved (90% CI includes zero). Climate: 2081–2100 relative to the WorldClim 1970–2000 baseline, ensemble mean with 5th to 95th percentiles of 10 fold-models × 6 GCMs (by-2100 values additionally sample τ); SOC, SIC, and TC in 0–200 cm; MAOC and POC in 0–30 cm of mineral soils (separate fraction model; not additive with ΔSOC). Committed change: difference of ensemble means (no CI). Nitrogen: IMAGE fertilizer, 10 fold-models, 0–200 cm with 0–30 cm in parentheses; ‡SSP2-4.5 interpolated. Köppen–Geiger-shifted land: ensemble-mean map integrals (transition-level CIs in table S17). Nitrogen and climate experiments are separate and are not added.',
      ['Process','Scenario','ΔSOC','ΔSIC','ΔTC = ΔSOC + ΔSIC','ΔMAOC (0–30 cm)','ΔPOC (0–30 cm)'],rows,font=7,widths=[1.6,1.0,1.35,1.9,1.35,1.2,1.1])
rows=[]
for s_,lab in SSPL:
    dq=DIR14['ssp'][s_]; q=dq['quadrant_pct']; lp=dq['land_pct']
    rows.append([lab,f"{q['tradeoff']:.0f}",f"{q['coloss']:.0f}",f"{q['bothgain']:.0f}",f"{q['socgain_sicloss']:.0f}",f"{lp['SOC_decrease']:.0f}",f"{lp['SIC_increase']:.0f}",f"{lp['TC_decrease']:.0f}",'yes' if dq['per_gcm_all_SOCdec_SICinc_TCdec'] else 'no'])
table(sm,'Table S19 (continued).','Share of the 137.3 Mkm² of mapped land (%) in each direction class of the equilibrium ensemble-mean change (0–200 cm, 2081–2100), and agreement of the six GCMs (each averaged over the 10 fold-models) on the direction of the global change.',
      ['Scenario','SOC ↓, SIC ↑ (trade-off)','SOC ↓, SIC ↓ (co-loss)','SOC ↑, SIC ↑','SOC ↑, SIC ↓','Land with ΔSOC < 0','Land with ΔSIC > 0','Land with ΔTC < 0','All six GCMs: global SOC ↓, SIC ↑, TC ↓'],rows,font=7.5,widths=[0.9,1.0,1.0,0.8,0.8,0.9,0.9,0.9,1.4])
''')
TAB_INV={TABMAP.get(o,o):o for o in TCHUNK}
