import json,os,glob,numpy as np
O10='/workspace/soil_global/out/v10'; O7='/workspace/soil_global/out/v7'; O8='/workspace/soil_global/out/v8'
E=json.load(open(f'{O10}/ensemble_v10.json')); B=json.load(open(f'{O10}/bias_tests.json'))
P7=json.load(open(f'{O7}/paper_numbers_v7.json')) if os.path.exists(f'{O7}/paper_numbers_v7.json') else {}
P8=json.load(open(f'{O8}/paper_numbers_v8.json')) if os.path.exists(f'{O8}/paper_numbers_v8.json') else {}
def sd_pack(d):
  # Huang-style ±1 SD alongside 90% CI
  return dict(mean=d['mean'],median=d['median'],p05=d['p05'],p95=d['p95'],sd=d['sd'],
              CI90=[d['p05'],d['p95']], plus_minus_1sd=[d['mean']-d['sd'],d['mean']+d['sd']],n=d['n'])
def layer_pack(s):
  out={}
  for k,v in E['present'][s].items():
    if k.endswith('_model_only'): out[k]=v; continue
    out[k]=sd_pack(v)
  return out
PN=dict(
  version='v10', date='2026-10-31',
  design=E['design'],
  accounting_note='All future maps and headlines come from the same 10 fold-models × 6 GCMs ensemble. Maps are ensemble MEANS so that map-area integrals equal the headline mean. Medians and 90% CI (5–95%) are also reported. Time-limited responses sample τ log-uniform within literature ranges.',
  present=dict(
    _0_30=layer_pack('_0_30'), _30_100=layer_pack('_30_100'), _100_200=layer_pack('_100_200'),
    _0_100=dict(MAOC=sd_pack(E['present']['0_100']['MAOC']),POC=sd_pack(E['present']['0_100']['POC'])),
    _0_200=dict(SOC=sd_pack(E['present']['0_200']['SOC']),SIC=sd_pack(E['present']['0_200']['SIC']),TC=sd_pack(E['present']['0_200']['TC'])),
    uncertainty_method=E['present']['note'],
    literature=dict(Batjes1996_SOC_0_30='684-724',Batjes1996_SOC_0_200='2376-2456',Huang_SIC_0_200_mean_sd='2305 ± 636',Georgiou_MAOC_0_100_nonpermafrost=899),
  ),
  future={s:dict(
    eq={k:sd_pack(v) for k,v in E['future'][s]['eq'].items()},
    time_limited={k:sd_pack(v) for k,v in E['future'][s]['tl'].items()},
    map_sums_equal_mean=E['future'][s]['map_sums'],
    zone=E['future'][s].get('zone'),
  ) for s in ['126','245','370','585']},
  N=dict(
    scenarios={s:{k:sd_pack(v) if isinstance(v,dict) and 'mean' in v else v for k,v in E['N'][s].items()} for s in ['126','245','370','585']},
    method=E['N']['note'],
    GLOBIOM_INMS='Not obtained. INMS portal (data.inms.international) hosts GLOBIOM N-cycle grids for Kanter et al. 2020 scenarios but requires registered INMS-user download; no open Zenodo mirror of the gridded fertilizer fields was found. Fallback: ISIMIP3b IMAGE fertilizer + cropland fraction; SSP2-4.5 Nin = mean(SSP1-2.6, SSP3-7.0).',
    Huang_targets_topsoil_Pg='10 / 14 / 23 under High/Medium/Low Ambition-N (GLOBIOM); IMAGE recovers only 1.6–2.2 Pg at 0–30 cm',
  ),
  bias_tests=dict(
    LUCAS=B['LUCAS'],
    cropfrac_test=B['cropfrac_test'],
    decisions=[
      'DO NOT adopt IMAGE cropland-fraction as a new SOC covariate: random-CV R² unchanged (+0.001) and global mean concentration barely changes (+0.7%); no independent LUCAS improvement expected from this alone.',
      'DO adopt depth-harmonised LUCAS reporting: LUCAS 2018 stocks are 0–20 cm (Zenodo 10211884). Comparing them to the 0–30 cm map inflated bias to +28.6 Mg/ha (R²=−0.46). Scaling the prediction by Jobbagy–Jackson beta≈0.978 (0–20/0–30 ≈ 0.74) reduces bias to +6.9 Mg/ha (R²≈0.02). This is a validation fix, not a map recalibration; residual positive bias remains.',
      'No multiplicative LUCAS bias-calibration of global maps: would change stocks without a global independent check outside Europe, and depth-harmonisation already explains most of the reported bias.',
      'NDVI/land-cover: no quick open 10′ stack already in the project; cropland fraction (IMAGE 2015) was the obtainable proxy and was rejected under the CV rule.',
    ],
  ),
  vs_v7_v8_v9=dict(
    present_0_200_point_v7=dict(SOC=2492,SIC=1603,TC=4095),
    present_0_200_v10=dict(SOC_mean=E['present']['0_200']['SOC']['mean'],SIC_mean=E['present']['0_200']['SIC']['mean'],
      SOC_CI90=[E['present']['0_200']['SOC']['p05'],E['present']['0_200']['SOC']['p95']],
      SIC_CI90=[E['present']['0_200']['SIC']['p05'],E['present']['0_200']['SIC']['p95']],
      SOC_pm1sd=E['present']['0_200']['SOC']['sd'],SIC_pm1sd=E['present']['0_200']['SIC']['sd']),
    future_SSP585_eq_v5_headline=dict(dSOC=-246,dSIC=290,dTC=25,note='bootstrap×GCM of pre-final (v5) models'),
    future_SSP585_eq_v10=dict(dSOC=E['future']['585']['eq']['dSOC_0_200']['mean'],dSIC=E['future']['585']['eq']['dSIC_0_200']['mean'],dTC=E['future']['585']['eq']['dTC_0_200']['mean'],
      dSOC_CI90=[E['future']['585']['eq']['dSOC_0_200']['p05'],E['future']['585']['eq']['dSOC_0_200']['p95']],
      dSIC_CI90=[E['future']['585']['eq']['dSIC_0_200']['p05'],E['future']['585']['eq']['dSIC_0_200']['p95']]),
    future_SSP585_tl_v5=dict(dTC=-182),
    future_SSP585_tl_v10=dict(dTC=E['future']['585']['tl']['dTC_0_200']['mean'],dTC_CI90=[E['future']['585']['tl']['dTC_0_200']['p05'],E['future']['585']['tl']['dTC_0_200']['p95']]),
    fig3_5_accounting='FIXED: Fig.3/5 maps are ensemble means of the same fold×GCM set that produces headlines; map integrals equal headline means (checked).',
    N_v7_IMAGE_topsoil_loss='1.8 / 2.4 / 2.5 Pg (126/370/585)',
    N_v10_IMAGE_topsoil_loss=dict(**{s: -E['N'][s]['loss_0_30']['mean'] for s in ['126','245','370','585']}),
  ),
  CV_primary=P7.get('random_CV_10fold') or json.load(open(f'{O7}/hp_cv.json'))['results'],
  fractions_v8_cv=P8.get('fractions',{}).get('cv') if P8 else json.load(open(f'{O8}/fractions_v8.json'))['cv'],
  figures=dict(main=sorted(glob.glob('/workspace/soil_global/figs/v10_main/*.png')),si=sorted(glob.glob('/workspace/soil_global/figs/v10_SI/*.png'))),
  files=dict(ensemble=f'{O10}/ensemble_v10.json',ens_maps=f'{O10}/ens_maps.npz',members=f'{O10}/members/',bias=f'{O10}/bias_tests.json'),
)
# round nested floats lightly for readability in a compact summary
json.dump(PN,open(f'{O10}/paper_numbers_v10.json','w'),indent=1)
# short human summary
S=dict(
  present_0_200_SOC=f"{PN['present']['_0_200']['SOC']['mean']:.0f} ({PN['present']['_0_200']['SOC']['p05']:.0f}–{PN['present']['_0_200']['SOC']['p95']:.0f}; ±{PN['present']['_0_200']['SOC']['sd']:.0f})",
  present_0_200_SIC=f"{PN['present']['_0_200']['SIC']['mean']:.0f} ({PN['present']['_0_200']['SIC']['p05']:.0f}–{PN['present']['_0_200']['SIC']['p95']:.0f}; ±{PN['present']['_0_200']['SIC']['sd']:.0f})",
  present_0_30_SOC=f"{PN['present']['_0_30']['SOC']['mean']:.0f} ({PN['present']['_0_30']['SOC']['p05']:.0f}–{PN['present']['_0_30']['SOC']['p95']:.0f})",
  present_0_30_MAOC=f"{PN['present']['_0_30']['MAOC']['mean']:.0f} ({PN['present']['_0_30']['MAOC']['p05']:.0f}–{PN['present']['_0_30']['MAOC']['p95']:.0f})",
  present_0_30_POC=f"{PN['present']['_0_30']['POC']['mean']:.0f} ({PN['present']['_0_30']['POC']['p05']:.0f}–{PN['present']['_0_30']['POC']['p95']:.0f})",
  SSP585_eq_dSOC=f"{PN['future']['585']['eq']['dSOC_0_200']['mean']:.0f} ({PN['future']['585']['eq']['dSOC_0_200']['p05']:.0f}–{PN['future']['585']['eq']['dSOC_0_200']['p95']:.0f})",
  SSP585_eq_dSIC=f"{PN['future']['585']['eq']['dSIC_0_200']['mean']:.0f} ({PN['future']['585']['eq']['dSIC_0_200']['p05']:.0f}–{PN['future']['585']['eq']['dSIC_0_200']['p95']:.0f})",
  SSP585_eq_dTC=f"{PN['future']['585']['eq']['dTC_0_200']['mean']:.0f} ({PN['future']['585']['eq']['dTC_0_200']['p05']:.0f}–{PN['future']['585']['eq']['dTC_0_200']['p95']:.0f})",
  SSP585_tl_dTC=f"{PN['future']['585']['time_limited']['dTC_0_200']['mean']:.0f} ({PN['future']['585']['time_limited']['dTC_0_200']['p05']:.0f}–{PN['future']['585']['time_limited']['dTC_0_200']['p95']:.0f})",
  SSP585_eq_dMAOC=f"{PN['future']['585']['eq']['dMAOC']['mean']:.0f}",
  SSP585_eq_dPOC=f"{PN['future']['585']['eq']['dPOC']['mean']:.0f}",
  SSP585_tl_dMAOC=f"{PN['future']['585']['time_limited']['dMAOC']['mean']:.0f}",
  SSP585_tl_dPOC=f"{PN['future']['585']['time_limited']['dPOC']['mean']:.0f}",
  N_topsoil_loss={s:round(-PN['N']['scenarios'][s]['loss_0_30']['mean'],2) for s in ['126','245','370','585']},
  N_0_200_loss={s:round(-PN['N']['scenarios'][s]['loss_0_200']['mean'],1) for s in ['126','245','370','585']},
  LUCAS_bias_before_after=[B['LUCAS']['v7_as_reported_0_30_vs_0_20']['bias'],B['LUCAS']['harmonised']['bias']],
  map_equals_headline_check={s:E['future'][s]['map_sums'] for s in ['126','585']},
)
json.dump(S,open(f'{O10}/KEY_NUMBERS_v10.json','w'),indent=1)
print(json.dumps(S,indent=2))
print('WROTE',f'{O10}/paper_numbers_v10.json',os.path.getsize(f'{O10}/paper_numbers_v10.json'))
