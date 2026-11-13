# Full Science Research Article Word + Markdown (English) + Chinese summary
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import json, os, glob
O='/workspace/soil_global/out/v7'; FM='/workspace/soil_global/figs/v7_main'; FS='/workspace/soil_global/figs/v7_SI'
P=json.load(open(f'{O}/paper_numbers_v7.json'))
qc=P['qc']; stocks=P['present_stocks_Pg']; cv=P.get('random_CV_summary',{})
hp=json.load(open(f'{O}/hp_cv.json'))['results']
N=P['N_acidification']; R5fut=P['future_climate_0_200']
s30=json.load(open(f'{O}/stocks30_0_30.json')) if os.path.exists(f'{O}/stocks30_0_30.json') else None

def add_heading_en(doc,text,level=1):
  doc.add_heading(text,level=level)

def para(doc,text,bold=False):
  p=doc.add_paragraph(); run=p.add_run(text); run.font.size=Pt(10); run.bold=bold; return p

doc=Document()
# Title
t=doc.add_paragraph(); r=t.add_run('Global soil organic and inorganic carbon stocks and their vulnerability to climate-zone shifts and nitrogen-driven acidification'); r.bold=True; r.font.size=Pt(14)
para(doc,'A Science-format Research Article draft assembled from the v7 digital soil mapping analysis. Primary accuracy metrics are random cross-validation, following Huang et al. (2024).')
para(doc,'Authors: [to be completed]  |  Correspondence: [to be completed]')

add_heading_en(doc,'Abstract',1)
soc0200=stocks['0_200']['SOC']; sic0200=stocks['0_200']['SIC']
para(doc,
f"Soils store both organic carbon (SOC) and inorganic carbon (SIC), yet most global assessments treat them separately. Building on the digital soil mapping framework of Huang et al. (2024) for SIC, we jointly map SOC and SIC to 2 m depth using WoSIS observations after Huang-style quality control, mass-preserving depth splines, and machine-learning models selected by random 10-fold cross-validation. Present-day stocks are {soc0200:.0f} Pg SOC and {sic0200:.0f} Pg SIC (0–200 cm) after organic-horizon handling and spatial declustering. Under SSP5-8.5 by 2081–2100, equilibrium space-for-time projections suggest large SOC losses that are largely offset by SIC gains, whereas a depth-specific first-order turnover constraint implies a net total-carbon loss because carbonate accumulation is slow. Nitrogen-driven acidification estimated with Huang’s empirical ΔpH–fertilizer relation yields 1.8–2.5 Pg topsoil SIC loss by 2050 under ISIMIP IMAGE nitrogen inputs—below Huang’s 10–23 Pg—unless nitrogen inputs are scaled to high-ambition/low-ambition GLOBIOM-like magnitudes. We report random-CV skill honestly (SIC AUC ≈ 0.95–0.97; SIC amount R² ≈ 0.31–0.49; pH R² ≈ 0.65–0.67), below some Huang benchmarks, and document resolution (target 30″ / ~1 km maps; integrals compared at 10′ and 30″).")

add_heading_en(doc,'One-sentence summary',1)
para(doc,'Joint global SOC–SIC mapping shows climate-driven trade-offs and nitrogen acidification risks, with random-CV accuracy and 1 km mapping targets aligned to Huang et al. 2024 practice.')

add_heading_en(doc,'Introduction',1)
para(doc,'Soil carbon is central to the global carbon cycle and to climate mitigation. Organic carbon responds relatively quickly to climate and land use, whereas pedogenic carbonates (SIC) respond on longer timescales but can dissolve rapidly under acidifying nitrogen inputs (Zamanian et al. 2018; Huang et al. 2024). Huang et al. (2024) produced a global SIC assessment with two-step machine learning, a SHAP-derived pH–SIC sigmoid, multi-GCM climate pathways, and an empirical nitrogen–ΔpH relationship from Chinese resurveys. Their reported model skill used random cross-validation.')
para(doc,'Here we extend that paradigm to total soil carbon (SOC + SIC). We (i) apply Huang-aligned observation QC and equal-area depth splines; (ii) train depth-specific models with hyperparameter search under random 10-fold CV as the primary accuracy protocol; (iii) correct organic-horizon inflation of deep SOC; (iv) project climate-driven changes with multi-GCM ensembles and a labelled transient constraint; and (v) re-estimate nitrogen-driven SIC loss with Huang’s ΔpH formula and our SIC–pH response, including a high-N sensitivity. Target map resolution is ~1 km (30 arcsec), with stocks reported for both 10′ and 30″ grids when available.')

add_heading_en(doc,'Materials and methods',1)
add_heading_en(doc,'Observations and quality control',2)
para(doc,f"We used WoSIS latest layers for pH (H₂O), total carbonate equivalent (TCEQ; SIC = 0.12 × TCEQ), organic carbon, bulk density (fine earth), and coarse fragments. Following Huang et al. SM: remove litter/organic surface horizons; remove depth-inconsistent records; remove samples dated before 1970; apply value-range filters; remove duplicate profile–depth records. After QC we retained {qc['profiles_with_any_after_QC']:,} profiles ({qc['profiles_with_SOC_0_30']:,} with 0–30 cm SOC; {qc['profiles_with_SIC_0_30']:,} with SIC; {qc['profiles_with_pH_0_30']:,} with pH). Huang reported 55,077 profiles / 223,593 samples for SIC. Depths were harmonized to 0–30, 30–100 and 100–200 cm with mass-preserving equal-area splines (Bishop et al. 1999; Malone et al. 2009; λ = 0.1).")

add_heading_en(doc,'Covariates and prediction grid',2)
para(doc,'Training covariates include WorldClim 2.1 bioclimatic variables, Hargreaves aridity (log P/PET), elevation and terrain derivatives, SoilGrids texture/CEC (and 1 km layers where available), and GLiM lithology classes (carbonate rock, evaporite, unconsolidated). The target prediction grid is WorldClim 30 arcsec (~1 km). Climate fields for 30″ prediction were bilinearly indexed from the 10′ stack (delta-method futures use 10′ CMIP6 anomalies added to the present field); elevation uses native 30″ WorldClim. Full native 30″ bioclim reading via archive I/O was I/O-bound on our system; we document this hybrid explicitly rather than silently upsampling.')

add_heading_en(doc,'Models and cross-validation',2)
para(doc,'For each depth we fit: (1) pH regression; (2) SIC hurdle (presence classifier + log-amount regression with Duan smearing), using out-of-fold pH as a covariate; (3) organic-horizon classifier (SOC > 120 g kg⁻¹) plus mineral SOC log1p regression, with peat area anchored to PEATMAP 4.23 Mkm² (Xu et al. 2018); (4) bulk density regression with log1p(SOC). Algorithms: XGBoost with hyperparameter search. Model selection and reported skill use random 10-fold CV (AUC/F1 for classifiers; R²/RMSE for regression), matching Huang’s reporting style. Spatial block CV is not used to claim superiority over Huang. Sample weights = inverse count in 0.5° cells (declustering) to reduce dense-network bias.')

add_heading_en(doc,'Stocks and uncertainty',2)
para(doc,'Stock (Mg C ha⁻¹) = concentration × BD × (1 − CF/100) × thickness_cm × 0.1. Organic cells use observed SOC×BD mean density. Uncertainty: bootstrap / repeated CV where computed; 5–95% intervals as 90% CI for scenario aggregates carried from v5 ensemble analysis.')

add_heading_en(doc,'Future climate and nitrogen pathways',2)
para(doc,'Climate: six CMIP6 GCMs × SSP1-2.6/2-4.5/3-7.0/5-8.5 for 2081–2100. Equilibrium change = space-for-time under future covariates. Transient SOC/SIC: Δ_trans = [1 − exp(−t/τ)] Δ_eq with depth-specific τ ranges informed by turnover/¹⁴C literature (Carvalhais 2014; Shi 2020; He 2016)—labelled assumptions. Nitrogen: ΔpH = −0.06·Nin + 0.11 (Huang SM; Nin = cumulative cropland fertilizer Mg N ha⁻¹); ΔSIC from finite difference of our SIC model w.r.t. pH, scaled by cropland fraction. ISIMIP IMAGE nitrogen is not GLOBIOM INMS; we add a high-N sensitivity scaled to Huang’s published 10–23 Pg topsoil losses. Zamanian (2018) stoichiometry (0.21 kg C kg⁻¹ N) is a flux-style sensitivity.')

add_heading_en(doc,'Independent validation',2)
lucas=P['independent_validation']['LUCAS2018_SOC_0_30']
para(doc,f"LUCAS 2018 SOC stocks (Europe): n={lucas['n']}, RMSE={lucas['rmse']:.1f} Mg C ha⁻¹, mean bias={lucas['bias']:.1f} Mg C ha⁻¹. Positive bias is consistent with remaining topsoil SOC overestimation versus Batjes/SoilGrids.")

add_heading_en(doc,'Results',1)
add_heading_en(doc,'Model performance (random 10-fold CV)',2)
para(doc,'Table-like summary (0–30 / 30–100 / 100–200 cm):')
for s in ['_0_30','_30_100','_100_200']:
  r=hp[s]; para(doc,f"{s}: pH R²={r['pH']['r2']:.3f}; SIC AUC={r['SIC']['AUC']:.3f}, SIC R²={r['SIC']['r2']:.3f}; mineral SOC R²={r['SOC_mineral']['r2']:.3f}; BD R²={r['BD']['r2']:.3f}.")
para(doc,'Huang et al. reported SIC AUC ≈ 0.99 and regression R² ≈ 0.79 (random 10-fold) and climate-driven pH R² ≈ 0.85. Our SIC presence skill is close (AUC 0.95–0.97); amount R² and pH R² remain lower, likely reflecting fewer covariates (no NDVI/PDSI/TWI in the final fit), different QC populations, and a joint SOC–SIC workflow. We do not emphasize spatial CV to “beat” Huang.')

# embed main figures
add_heading_en(doc,'Present-day stocks',2)
for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'; para(doc,f"{a}–{b} cm: SOC {stocks[s]['SOC']:.0f} Pg; SIC {stocks[s]['SIC']:.0f} Pg.")
para(doc,f"0–200 cm: SOC {soc0200:.0f} Pg; SIC {sic0200:.0f} Pg; total {stocks['0_200']['TC']:.0f} Pg. Literature: Batjes (1996) SOC 2,376–2,456 Pg (0–200 cm); Huang SIC 2,305 Pg (0–200 cm). Topsoil SOC (858 Pg at 10′) remains above Batjes 684–724 and SoilGrids 658 on the same mask, but is reduced relative to v5 (960 Pg) after declustering.")
if s30:
  para(doc,f"At 30 arcsec, 0–30 cm stocks are SOC {s30['SOC_0_30_Pg']:.1f} Pg and SIC {s30['SIC_0_30_Pg']:.1f} Pg (land pixels={s30['land_pixels']:,}), compared with 10′ SOC {s30['compare_10arcmin']['SOC']:.1f} and SIC {s30['compare_10arcmin']['SIC']:.1f} Pg.")

for fig in sorted(glob.glob(FM+'/Fig*.png')):
  doc.add_paragraph(os.path.basename(fig))
  try: doc.add_picture(fig, width=Inches(6.3))
  except Exception as e: para(doc,str(e))

add_heading_en(doc,'Climate-driven change and zone shifts',2)
para(doc,'Under SSP5-8.5 (2081–2100), equilibrium ΔSOC (0–200 cm) is about −246 Pg (90% CI −318 to −157) with ΔSIC about +290 Pg (95 to 355), so net total carbon is near zero in the equilibrium limit. Time-limited responses yield ΔSOC ≈ −190 Pg and Δ total C ≈ −182 Pg because SIC gains are strongly damped by long τ. Köppen-zone shifts reach ~19 Mkm²; SOC↓SIC↑ trade-off areas are ~57 Mkm².')

add_heading_en(doc,'Nitrogen-driven SIC loss',2)
para(doc,'Using Huang’s ΔpH = −0.06·Nin + 0.11 on cropland-intensity IMAGE fertilizer, loss-only topsoil SIC for 2020–2050 is ~1.8 (SSP1-2.6), 2.4 (SSP3-7.0) and 2.5 Pg (SSP5-8.5)—an order of magnitude below Huang’s 10–23 Pg. Mean cropland Nin ≈ 2.6 Mg N ha⁻¹ (~87 kg N ha⁻¹ yr⁻¹) is far below intensive Chinese rates that motivate large ΔpH. Scaling Nin to match Huang’s published magnitudes (high-N sensitivity) recovers 10–23 Pg by construction, showing that nitrogen scenario choice—not only the SIC–pH mapping—drives the gap. Zamanian stoichiometry gives ~0.8–1.1 Pg.')

for fig in sorted(glob.glob(FS+'/FigS*.png')):
  doc.add_paragraph(os.path.basename(fig))
  try: doc.add_picture(fig, width=Inches(5.8))
  except Exception as e: para(doc,str(e))

add_heading_en(doc,'Discussion',1)
para(doc,'Joint SOC–SIC mapping reveals a climate trade-off: warming/drying can reduce SOC while expanding environments favorable to carbonates in space-for-time models. Mechanistic time constraints reverse the net total-carbon conclusion for this century. Nitrogen acidification is real but quantitatively tied to fertilizer scenarios; without GLOBIOM INMS pathways, IMAGE-based estimates are lower than Huang’s published range.')
para(doc,'Limitations: (1) random-CV SIC amount and pH skill below Huang; (2) topsoil SOC still high vs Batjes/SoilGrids and LUCAS bias positive; (3) 30″ mosaics use hybrid climate (10′→30″) with native 30″ elevation; (4) τ assumptions; (5) no GLOBIOM N files. Future work should add vegetation indices, water balance/PDSI, TWI, and process-model benchmarks (TRENDY/CMIP6 soil C).')

add_heading_en(doc,'Conclusions',1)
para(doc,'We provide a Huang-aligned, jointly SOC–SIC global analysis with random-CV primary metrics, organic-horizon corrections, multi-GCM climate pathways, and nitrogen acidification using the published ΔpH formula. Total soil carbon vulnerability depends critically on whether SIC responses are treated as equilibrium potentials or time-limited, and on nitrogen input scenarios.')

add_heading_en(doc,'References (selected DOIs)',1)
for ref in [
 'Huang et al. 2024 Science — Size, distribution, and vulnerability of the global soil inorganic carbon',
 'Bishop et al. 1999 Geoderma doi:10.1016/S0016-7061(99)00003-8',
 'Malone et al. 2009 Geoderma doi:10.1016/j.geoderma.2009.10.007',
 'Batjes 1996 EJSS doi:10.1111/j.1365-2389.1996.tb01386.x',
 'Xu et al. 2018 Catena PEATMAP doi:10.1016/j.catena.2017.09.010',
 'Zamanian et al. 2018 GCB doi:10.1111/gcb.14148',
 'Carvalhais et al. 2014 Nature doi:10.1038/nature13731',
 'Shi et al. 2020 Nat. Geosci. doi:10.1038/s41561-020-0596-z',
 'He et al. 2016 Science doi:10.1126/science.aad4273',
]:
  para(doc,ref)

add_heading_en(doc,'中文摘要：相对 v6 的变更',1)
para(doc,'v7 按 Huang 支撑材料重做了质控（去 1970 前、凋落物、深度错误、重复），以随机 10 折为主报告精度，并用 0.5° 疏化减轻 SOC 高估（0–30 cm 由约 960 Pg 降至约 858 Pg）。制图目标为 30″（约 1 km）：样点训练，分块预测；气候由 10′ 双线性到 30″，高程用原生 30″。N 路径采用 Huang 的 ΔpH 公式，并给出高 N 敏感性以对照其 10–23 Pg。主图 5 张、支撑图 ≥6 张；本稿为英文 Science 长文草稿，精度差距与分辨率混合策略均如实写出，不用空间 CV 压过 Huang。')

out_docx='/workspace/soil_global/paper/manuscript_v7_Science.docx'
doc.save(out_docx); print('saved',out_docx)

# Markdown twin
md=[]
md.append('# Global soil organic and inorganic carbon stocks and their vulnerability to climate-zone shifts and nitrogen-driven acidification\n')
md.append('Science-format Research Article draft (v7).\n')
md.append('## Abstract\n')
md.append(f"Soils store SOC and SIC. Following Huang et al. 2024 practice (random CV primary), we map both to 2 m. Present stocks: {soc0200:.0f} Pg SOC and {sic0200:.0f} Pg SIC (0–200 cm). Climate equilibrium suggests SOC loss offset by SIC gain; time-limited responses imply net total-C loss. N acidification with Huang ΔpH formula gives 1.8–2.5 Pg topsoil SIC loss by 2050 under IMAGE N (below Huang 10–23 unless high-N scaled).\n")
md.append('## Random 10-fold CV\n')
for s,r in hp.items():
  md.append(f"- {s}: pH R²={r['pH']['r2']:.3f}; SIC AUC={r['SIC']['AUC']:.3f}, R²={r['SIC']['r2']:.3f}; SOC mineral R²={r['SOC_mineral']['r2']:.3f}; BD R²={r['BD']['r2']:.3f}\n")
md.append('## Present stocks (10′ integrals after declustering)\n')
for s in ['_0_30','_30_100','_100_200','0_200']:
  if s in stocks: md.append(f"- {s}: {stocks[s]}\n")
if s30: md.append(f"\n## 30″ stocks 0–30\n\n{s30}\n")
md.append('\n## Chinese summary vs v6\n\nv7 重做 Huang 式 QC、随机 10 折主精度、疏化降 SOC 高估、30″ 制图目标、Huang ΔpH 氮路径 + 高 N 敏感性；主图/支撑图与 Word 长稿见 paper/。\n')
md.append('\n## Figures\n')
for f in sorted(glob.glob(FM+'/*.png')+glob.glob(FS+'/*.png')):
  md.append(f'- {f}\n')
open('/workspace/soil_global/paper/manuscript_v7_Science.md','w').write(''.join(md))
print('saved md')
