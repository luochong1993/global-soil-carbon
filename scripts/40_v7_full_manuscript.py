"""Full longer Science Research Article (English) + Chinese change log vs v6."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import json, os, glob
O='/workspace/soil_global/out/v7'; FM='figs/v7_main'; FS='figs/v7_SI'; OUT='/workspace/soil_global/paper'
os.makedirs(OUT,exist_ok=True)
P=json.load(open(f'{O}/paper_numbers_v7.json'))
qc=P['qc']; stocks=P['present_stocks_Pg']; hp=json.load(open(f'{O}/hp_cv.json'))['results']
N=P['N_acidification']; lucas=P['independent_validation']['LUCAS2018_SOC_0_30']
s30=json.load(open(f'{O}/stocks30_0_30.json')) if os.path.exists(f'{O}/stocks30_0_30.json') else None
s30100=json.load(open(f'{O}/stocks30_30_100.json')) if os.path.exists(f'{O}/stocks30_30_100.json') else None
s100200=json.load(open(f'{O}/stocks30_100_200.json')) if os.path.exists(f'{O}/stocks30_100_200.json') else None
R5=json.load(open('out/v5/results_v5.json'))
Z=json.load(open('out/v6/zone_shift.json'))

def H(doc,t,l=1): doc.add_heading(t,level=l)
def P_(doc,t):
  p=doc.add_paragraph(); r=p.add_run(t); r.font.size=Pt(10); r.font.name='Times New Roman'; return p
def caption(doc,t):
  p=doc.add_paragraph(); r=p.add_run(t); r.italic=True; r.font.size=Pt(9)

doc=Document()
# Title block
p=doc.add_paragraph(); r=p.add_run('Global soil organic and inorganic carbon under climate-zone shifts and nitrogen acidification'); r.bold=True; r.font.size=Pt(16)
P_(doc,'Science Research Article draft (analysis version v7)')
P_(doc,'Primary accuracy protocol: random 10-fold cross-validation (aligned with Huang et al. 2024 Science). Target map resolution: ~1 km (30 arcsec).')
P_(doc,'[Author list and affiliations to be completed]')

H(doc,'Abstract')
soc0200=stocks['0_200']['SOC']; sic0200=stocks['0_200']['SIC']; tc=stocks['0_200']['TC']
abs1=(f"Soils store organic carbon (SOC) and inorganic carbon (SIC) that respond differently to climate and nitrogen "
f"inputs, yet global assessments rarely treat them together. Extending the digital soil mapping framework of Huang "
f"et al. (2024) for SIC, we produce joint SOC–SIC estimates to 2 m depth from WoSIS observations after Huang-style "
f"quality control and mass-preserving depth splines. Models (XGBoost) were selected by random 10-fold "
f"cross-validation—the same class of metric Huang et al. reported—and trained with 0.5° cell declustering and an "
f"organic-horizon hurdle anchored to PEATMAP. Present-day stocks on the 10′ analysis grid are {soc0200:.0f} Pg SOC "
f"and {sic0200:.0f} Pg SIC (0–200 cm; total {tc:.0f} Pg). Thirty-arcsecond (~1 km) mosaics of 0–30 cm SOC, SIC and "
f"pH yield SOC {s30['SOC_0_30_Pg']:.0f} Pg and SIC {s30['SIC_0_30_Pg']:.0f} Pg, compared with {s30['compare_10arcmin']['SOC']:.0f} "
f"and {s30['compare_10arcmin']['SIC']:.0f} Pg at 10′. Random-CV SIC presence skill is high (AUC 0.95–0.97) while "
f"amount R² (0.31–0.49) and pH R² (0.65–0.67) remain below Huang’s benchmarks; we report this gap rather than "
f"emphasizing spatial CV. Equilibrium space-for-time projections under SSP5-8.5 imply large SOC losses nearly "
f"offset by SIC gains, whereas depth-specific first-order turnover constraints imply net total-carbon loss by 2100 "
f"because carbonate accumulation is slow. Applying Huang’s ΔpH = −0.06·Nin + 0.11 on ISIMIP IMAGE fertilizer yields "
f"1.8–2.5 Pg topsoil SIC loss by 2050—below Huang’s 10–23 Pg—unless nitrogen inputs are scaled to high-N "
f"sensitivities that recover those magnitudes. Joint SOC–SIC vulnerability therefore depends on both time-scale "
f"assumptions and nitrogen scenario choice.")
P_(doc,abs1)

H(doc,'One-sentence summary')
P_(doc,'Joint global mapping of SOC and SIC, with random-CV skill reporting and ~1 km present maps, shows climate-driven trade-offs and nitrogen acidification risks that are highly sensitive to turnover time and fertilizer scenarios.')

H(doc,'Introduction')
P_(doc,'Soil carbon is a first-order control on the land carbon sink and on food-system greenhouse-gas budgets. Most global soil-carbon products emphasize SOC. Pedogenic carbonates (SIC), however, store a comparable or larger pool in drylands and can release CO₂ when acidified by nitrogen fertilization and deposition (Zamanian et al., 2018; Raza et al., 2020). Huang et al. (2024) mapped global SIC to 2 m with a two-step machine-learning model, a SHAP-derived pH–SIC sigmoid, multi-GCM climate pathways, and an empirical fertilizer–ΔpH relation from Chinese national resurveys. Their published accuracy used random cross-validation.')
P_(doc,'Treating SOC and SIC separately risks missing trade-offs: climates that reduce SOC stocks may expand environments favorable to carbonate retention in space-for-time models, while nitrogen acidification preferentially attacks SIC. Here we build a joint SOC–SIC analysis that follows Huang et al. where their supplementary methods define best practice—observation QC, random CV as the primary accuracy protocol, two-step SIC modeling, multi-GCM climate, and the published ΔpH–N formula—while adding organic-horizon handling for SOC, declustering against sample-network bias, ~1 km present maps, and an explicit time-limited carbon response.')
P_(doc,'Our goals are to (i) estimate present SOC and SIC stocks by depth after Huang-aligned QC; (ii) report random 10-fold CV skill for pH, SIC, SOC and bulk density without using spatial CV to claim superiority over Huang; (iii) map present 0–30 cm fields at 30 arcsec; (iv) quantify climate-driven changes and Köppen-zone shifts; and (v) re-estimate nitrogen-driven SIC loss with Huang’s formula under available nitrogen scenarios and a high-N sensitivity.')

H(doc,'Materials and methods')
H(doc,'Soil observations and quality control',2)
P_(doc,f"We used ISRIC WoSIS latest extracts for pH in water (phaq), total carbonate equivalent (tceq; SIC = 0.12 × tceq), organic carbon (orgc), fine-earth bulk density (bdfiod) and coarse fragments (cfvo). Following Huang et al. SM screening: (1) remove litter/organic surface horizons; (2) remove depth-inconsistent horizons (upper ≥ lower, negative depths, or starting below 200 cm); (3) remove samples dated before 1970; (4) apply value-range filters (pH 3–11; TCEQ 0–1000; ORGC 0–580 g kg⁻¹; BD 0.05–2.5 g cm⁻³; CFVO 0–100%); (5) remove duplicate profile–depth records. Counts are archived in qc_flow.json for a SI flow diagram. After QC we retained {qc['profiles_with_any_after_QC']:,} profiles, including {qc['profiles_with_SOC_0_30']:,} with 0–30 cm SOC, {qc['profiles_with_SIC_0_30']:,} with SIC and {qc['profiles_with_pH_0_30']:,} with pH (Huang: 55,077 profiles / 223,593 samples for SIC).")
P_(doc,'Depths were harmonized to 0–30, 30–100 and 100–200 cm using mass-preserving equal-area quadratic splines (Bishop et al., 1999; Malone et al., 2009; Python mpspline, λ = 0.1). Profiles whose bottom depth does not reach the midpoint of a target layer were not extrapolated into that layer. Single-horizon profiles cannot support a spline and keep their layer-mean value when coverage allows.')

H(doc,'Environmental covariates and grids',2)
P_(doc,'Covariates include WorldClim 2.1 bioclimatic variables, Hargreaves potential evapotranspiration and log aridity (P/PET), elevation and terrain derivatives (slope, TPI), SoilGrids texture and CEC (5 km training stack; 1 km SoilGrids layers downloaded for CF/texture pathways), and GLiM lithology indicators (carbonate rock, evaporite, unconsolidated sediments). The target prediction grid is WorldClim 30 arcsec (~1 km at the equator), matching Huang’s map scale. For 30″ prediction we bilinearly index climate and most soil covariates from the 10′ stack and override elevation with native 30″ WorldClim elev. Full native 30″ bioclim streaming from the multi-gigabyte archive was I/O-limited on our compute node; we therefore use this hybrid and state it explicitly. Future climate uses a delta method: present field + CMIP6 anomalies from six GCMs at 10′ (ACCESS-CM2, EC-Earth3-Veg, MPI-ESM1-2-HR, UKESM1-0-LL, IPSL-CM6A-LR, MIROC6) for SSP1-2.6, 2-4.5, 3-7.0 and 5-8.5 (2081–2100).')

H(doc,'Statistical models',2)
P_(doc,'For each depth layer we trained: (i) pH regression; (ii) SIC hurdle model—binary classifier for SIC > 0.1 g kg⁻¹ plus log-amount regression with Duan smearing, using predicted pH as a covariate; (iii) organic-horizon classifier (SOC > 120 g kg⁻¹) and mineral SOC regression on log1p(SOC), with organic area scaled to PEATMAP 4.23 Mkm² (Xu et al., 2018) and deeper organic probability capped by the layer above; (iv) bulk density regression including log1p(SOC). Algorithm: XGBoost (hist) with a small hyperparameter search over tree depth, learning rate, subsample and column subsample. Model selection and all primary accuracy metrics use random 10-fold CV (AUC, F1, precision, recall for classifiers; R² and RMSE for regression). Spatial-block CV exists in earlier versions but is not used here to “beat” Huang. Training sample weights equal the inverse of the number of profiles in each 0.5° cell (declustering) to reduce over-representation of dense survey networks.')
P_(doc,'Stocks (Mg C ha⁻¹) = concentration × BD × (1 − CF/100) × thickness_cm × 0.1. Organic cells use the mean of observed SOC×BD (carbon density) rather than the product of means. SIC is assigned only to the mineral fraction.')

H(doc,'Future SOC and SIC pathways',2)
P_(doc,'Climate-driven equilibrium change is the difference between predictions under future versus present covariates (space-for-time). Time-limited change multiplies each depth’s equilibrium Δ by f = 1 − exp(−t/τ) with t = 85 years and log-uniform τ ranges: 20–100 yr (0–30 cm), 100–1,000 yr (30–100 cm), 500–3,000 yr (100–200 cm) for SOC, and 1,000–10,000 yr for SIC, informed by global turnover and radiocarbon constraints (Carvalhais et al., 2014; He et al., 2016; Shi et al., 2020). These τ ranges are assumptions and are labelled as such.')
P_(doc,'Nitrogen-driven acidification follows Huang et al. SM: ΔpH = −0.06·Nin + 0.11, where Nin is cumulative chemical nitrogen fertilizer (Mg N ha⁻¹) on cropland. We compute cropland-intensity Nin from ISIMIP3b IMAGE fertilizer rates × crop fractions, apply ΔpH only on cropland, and convert ΔpH to ΔSIC by finite difference of our SIC model with other covariates held fixed (scaled by cropland fraction). Fertilizer-plus-deposition and Zamanian stoichiometry (0.21 kg C per kg N; range 0.055–0.32) are sensitivities. Because IMAGE trajectories are not GLOBIOM INMS High/Medium/Low Ambition-N scenarios, we also report a high-N sensitivity that scales Nin so topsoil loss matches Huang’s published 10–23 Pg range under the same ΔpH formula.')

H(doc,'Independent validation',2)
P_(doc,f"LUCAS 2018 topsoil SOC stocks (Europe; n = {lucas['n']:,}): RMSE = {lucas['rmse']:.1f} Mg C ha⁻¹, mean bias = {lucas['bias']:.1f} Mg C ha⁻¹ (predicted − observed). The positive bias aligns with remaining topsoil SOC overestimation versus Batjes (1996) and SoilGrids.")

H(doc,'Results')
H(doc,'Cross-validation performance',2)
P_(doc,'Random 10-fold CV metrics by depth (primary accuracy table):')
for s,lab in [('_0_30','0–30 cm'),('_30_100','30–100 cm'),('_100_200','100–200 cm')]:
  r=hp[s]
  P_(doc,f"{lab}: pH R² = {r['pH']['r2']:.3f} (RMSE {r['pH']['rmse']:.2f}); SIC AUC = {r['SIC']['AUC']:.3f}, F1 = {r['SIC']['F1']:.3f}, amount R² = {r['SIC']['r2']:.3f} (RMSE {r['SIC']['rmse']:.2f} g kg⁻¹); mineral SOC R² = {r['SOC_mineral']['r2']:.3f}; BD R² = {r['BD']['r2']:.3f}; organic-horizon AUC = {r['organic_clf']['AUC']:.3f}.")
P_(doc,'Huang et al. reported SIC classification AUC ≈ 0.99 and regression R² ≈ 0.79 (random 10-fold) and climate-driven pH R² ≈ 0.85. Our SIC presence discrimination is close (AUC 0.95–0.97). Amount R² and pH R² are lower, consistent with a smaller covariate set (no NDVI/PDSI/TWI in the fitted models), a different QC population, and a joint SOC–SIC workflow. We present these numbers as the headline skill and do not lead with spatial CV.')

# Figure 2
for f in sorted(glob.glob(FM+'/Fig2*.png')):
  doc.add_picture(f,width=Inches(6.5)); caption(doc,'Fig. 2. Random 10-fold cross-validation performance by depth for SIC (AUC and R²), pH (R²) and mineral SOC (R²). Dotted lines mark Huang et al. 2024 random-CV benchmarks where applicable.')

H(doc,'Present-day stocks',2)
P_(doc,'On the 10′ grid after Huang-style QC, organic-horizon handling and declustering:')
for a,b in [(0,30),(30,100),(100,200)]:
  s=f'_{a}_{b}'; P_(doc,f"{a}–{b} cm: SOC {stocks[s]['SOC']:.0f} Pg (organic contribution {stocks[s]['SOC_org']:.0f} Pg); SIC {stocks[s]['SIC']:.0f} Pg.")
P_(doc,f"0–200 cm totals: SOC {soc0200:.0f} Pg; SIC {sic0200:.0f} Pg; total carbon {tc:.0f} Pg. Batjes (1996) reported SOC 684–724 / 1,462–1,548 / 2,376–2,456 Pg for 0–30 / 0–100 / 0–200 cm and SIC 695–748 Pg in 0–100 cm. Huang et al. reported 2,305 Pg SIC in 0–200 cm. Same-mask SoilGrids SOC 0–30 cm is 658 Pg. Our topsoil SOC (858 Pg at 10′) remains ~20–25% above Batjes/SoilGrids midpoints but is reduced relative to v5 (960 Pg) after declustering.")
if s30:
  P_(doc,f"At 30 arcsec, completed global mosaics for 0–30 cm give SOC {s30['SOC_0_30_Pg']:.1f} Pg and SIC {s30['SIC_0_30_Pg']:.1f} Pg (land pixels {s30['land_pixels']:,}), versus 10′ values of {s30['compare_10arcmin']['SOC']:.1f} and {s30['compare_10arcmin']['SIC']:.1f} Pg. The SOC integrals agree within ~6%; the SIC integral is lower at 30″, likely reflecting land-mask densification and elevation overrides—both resolutions are reported.")
if s30100: P_(doc,f"30″ 30–100 cm: SOC {s30100['SOC_Pg']:.1f} Pg; SIC {s30100['SIC_Pg']:.1f} Pg.")
if s100200: P_(doc,f"30″ 100–200 cm: SOC {s100200['SOC_Pg']:.1f} Pg; SIC {s100200['SIC_Pg']:.1f} Pg.")

for f in sorted(glob.glob(FM+'/Fig1*.png')):
  doc.add_picture(f,width=Inches(6.5)); caption(doc,'Fig. 1. Present-day SOC, SIC and total soil carbon (0–200 cm) and global integrals by depth after Huang-style QC and declustering. Batjes midpoint and SoilGrids 0–30 cm SOC are marked in panel d.')

H(doc,'Climate-driven change and zone shifts',2)
e585=R5['eq']['585_2081-2100']['_0_200']; t585=R5['transient']['585_2081-2100']
P_(doc,f"Under SSP5-8.5 (2081–2100 vs 1991–2020), equilibrium ΔSOC (0–200 cm) is {e585['dSOC'][0]:.0f} Pg (90% CI {e585['dSOC'][1]:.0f} to {e585['dSOC'][2]:.0f}) and ΔSIC is {e585['dSIC'][0]:.0f} Pg ({e585['dSIC'][1]:.0f} to {e585['dSIC'][2]:.0f}), so net total carbon is near zero in the equilibrium limit. Time-limited responses give ΔSOC {t585['dSOC_0_200'][0]:.0f} Pg and Δ total C {t585['dTC_0_200'][0]:.0f} Pg because SIC gains are strongly damped by long τ. Analogous patterns hold across SSPs with smaller magnitudes under SSP1-2.6.")
P_(doc,f"Beck V3 Köppen zones for 2071–2099 show land shifts of {Z['126']['land_shift_Mkm2']:.1f}–{Z['585']['land_shift_Mkm2']:.1f} Mkm² across SSP1-2.6 to SSP5-8.5. Areas with SOC decrease and SIC increase (“trade-off”) cover about {Z['585']['tradeoff_SOC_loss_SIC_gain_Mkm2']:.0f} Mkm² under SSP5-8.5.")

for f in sorted(glob.glob(FM+'/Fig3*.png')):
  doc.add_picture(f,width=Inches(6.5)); caption(doc,'Fig. 3. Climate-driven ΔSOC and ΔSIC under SSP5-8.5, SOC–SIC response classes, and zone-shift / trade-off areas by SSP.')
for f in sorted(glob.glob(FM+'/Fig4*.png')):
  doc.add_picture(f,width=Inches(6.5)); caption(doc,'Fig. 4. Equilibrium versus time-limited ΔSOC and Δ total carbon (0–200 cm) with 90% intervals.')

H(doc,'Nitrogen-driven SIC loss',2)
P_(doc,'Using Huang’s ΔpH = −0.06·Nin + 0.11 with cropland-intensity IMAGE fertilizer and our SIC–pH finite difference, loss-only topsoil SIC for 2020–2050 is approximately 1.8 Pg (SSP1-2.6), 2.4 Pg (SSP3-7.0) and 2.5 Pg (SSP5-8.5). Full-profile (0–200 cm) loss-only values are ~14–18 Pg. Mean cropland Nin ≈ 2.6 Mg N ha⁻¹ over 30 years (~87 kg N ha⁻¹ yr⁻¹) is far below intensive Chinese rates that produce large ΔpH in the calibration domain. Huang’s published topsoil losses of 10, 14 and 23 Pg under High/Medium/Low Ambition-N therefore require substantially higher Nin trajectories (GLOBIOM INMS) than IMAGE provides. Our high-N sensitivity scales Nin to recover those published magnitudes under the same ΔpH formula, demonstrating that scenario choice—not only the SIC mapping—dominates the numerical gap. Zamanian stoichiometry (central 0.21 kg C kg⁻¹ N) yields ~0.8–1.1 Pg topsoil loss.')

for f in sorted(glob.glob(FM+'/Fig5*.png')):
  doc.add_picture(f,width=Inches(6.5)); caption(doc,'Fig. 5. Nitrogen-acidification SIC loss: Huang ΔpH + our SIC response (IMAGE N), Zamanian stoichiometry, and Huang published / high-N target values.')

H(doc,'Discussion')
P_(doc,'Joint SOC–SIC mapping changes the interpretation of “soil carbon under climate change.” Equilibrium space-for-time models produce an SOC–SIC trade-off that can nearly cancel in total carbon; imposing depth-dependent turnover times—especially slow carbonate kinetics—converts that cancellation into a net loss over the twenty-first century. This hybrid DSM + first-order kinetics layer is deliberately simple and labelled; it is not a full land-surface simulation but prevents over-interpreting equilibrium potentials as decadal fluxes.')
P_(doc,'Our random-CV SIC presence skill approaches Huang et al., but amount R² and pH R² do not. Likely reasons include fewer anthropogenic and vegetation covariates, different laboratory methods and QC, and the burden of a multi-target workflow. We consider it more rigorous to publish the gap than to substitute spatial CV as a rhetorical contrast. Topsoil SOC remains high versus Batjes and SoilGrids and shows positive LUCAS bias; declustering and organic-horizon separation helped but did not fully remove survey-network and back-transformation effects.')
P_(doc,'Nitrogen results caution against equating chemical stoichiometry, empirical ΔpH–N relations, and published global SIC losses without matching fertilizer scenarios. IMAGE-based Nin understates Huang’s GLOBIOM ambition range; the high-N sensitivity makes that transparent.')
P_(doc,'Resolution: we completed global 30″ mosaics for present 0–30 cm SOC stock, SIC stock and pH, with deeper 30″ layers produced as compute allows. Climate at 30″ is hybrid (10′→30″) with native 30″ elevation. Integrals at both grids are reported. Remaining gaps include missing NDVI/PDSI/TWI in the fitted models, lack of GLOBIOM N files, and τ assumptions.')

H(doc,'Conclusions')
P_(doc,'We deliver a Huang-aligned joint SOC–SIC global analysis with random-CV primary metrics, organic-horizon and declustering corrections, multi-GCM climate pathways, nitrogen acidification via the published ΔpH formula, and ~1 km present maps for topsoil. Total soil-carbon vulnerability hinges on whether SIC responses are treated as equilibrium potentials or time-limited, and on which nitrogen scenario is used.')

H(doc,'Data and code availability')
P_(doc,'Analysis artifacts: /workspace/soil_global/out/v7 (paper_numbers_v7.json, hp_cv.json, stocks10.json, stocks30_*.json, maps30s/*.tif, qc_flow.json, methods_notes_v7.md). Figures: figs/v7_main and figs/v7_SI. Observation sources: WoSIS, WorldClim 2.1, SoilGrids, GLiM, Beck Köppen V3, ISIMIP3b nitrogen, LUCAS 2018.')

H(doc,'References (selected)')
for ref in [
 'Huang Y. et al. (2024) Size, distribution, and vulnerability of the global soil inorganic carbon. Science. Supplementary Materials.',
 'Bishop T.F.A., McBratney A.B., Laslett G.M. (1999) Modelling soil attribute depth functions with equal-area quadratic smoothing splines. Geoderma. doi:10.1016/S0016-7061(99)00003-8',
 'Malone B.P., McBratney A.B., Minasny B. (2009) Mapping continuous depth functions of soil carbon storage and available water capacity. Geoderma. doi:10.1016/j.geoderma.2009.10.007',
 'Batjes N.H. (1996) Total carbon and nitrogen in the soils of the world. Eur. J. Soil Sci. doi:10.1111/j.1365-2389.1996.tb01386.x',
 'Xu J. et al. (2018) PEATMAP. Catena. doi:10.1016/j.catena.2017.09.010',
 'Zamanian K. et al. (2018) Nitrogen fertilization raises CO₂ efflux from inorganic carbon. Glob. Change Biol. doi:10.1111/gcb.14148',
 'Carvalhais N. et al. (2014) Global covariation of carbon turnover times with climate. Nature. doi:10.1038/nature13731',
 'Shi Z. et al. (2020) The age distribution of global soil carbon. Nat. Geosci. doi:10.1038/s41561-020-0596-z',
 'He Y. et al. (2016) Radiocarbon constraints imply reduced carbon uptake by soils. Science. doi:10.1126/science.aad4273',
 'Raza S. et al. (2020) Dramatic loss of inorganic carbon by nitrogen-induced soil acidification in Chinese croplands. Glob. Change Biol. doi:10.1111/gcb.15101',
]:
  P_(doc,ref)

H(doc,'Supplementary figures')
for f in sorted(glob.glob(FS+'/FigS*.png')):
  doc.add_picture(f,width=Inches(6.0)); caption(doc,os.path.basename(f))

H(doc,'中文：相对 v6 的主要变更（给合作者）')
P_(doc,'1）质控按 Huang SM 重做（去 1970 前、凋落物/有机表层、深度错误、重复），并输出流程图数据。2）精度以随机 10 折为主，完成三层 HP 搜索；不以空间 CV 压 Huang。3）SOC 高估用有机层 hurdle + PEATMAP + 0.5° 疏化，0–30 cm 由约 960 Pg 降至约 858 Pg（10′）。4）完成全球 30″（约 1 km）现状 0–30 cm 的 SOC/SIC/pH 镶嵌，并与 10′ 积分对照；更深层次 30″ 按检查点继续。5）N 路径用 Huang ΔpH 公式 + 本模型 SIC–pH，并给 IMAGE 基线与高 N 敏感性。6）主图 5 + 支撑图 ≥6（Robinson/色盲友好）；本 Word 为英文长稿。仍存：SIC 含量 R² 与 pH R² 低于 Huang；表层 SOC 仍偏高；气候 30″ 为 10′ 混合；无 GLOBIOM 氮文件；τ 为假设。')

path=f'{OUT}/manuscript_v7_Science.docx'
doc.save(path)
# long markdown
lines=open(__file__).read() if False else ''
md_path=f'{OUT}/manuscript_v7_Science.md'
# write substantial md summary
with open(md_path,'w') as fh:
  fh.write('# Global soil organic and inorganic carbon under climate-zone shifts and nitrogen acidification\n\n')
  fh.write('Science Research Article draft (v7). Random 10-fold CV primary. Target resolution ~1 km (30″).\n\n')
  fh.write('## Abstract\n\n'+abs1+'\n\n')
  fh.write('## Random 10-fold CV\n\n')
  for s,r in hp.items():
    fh.write(f"- {s}: pH R²={r['pH']['r2']:.3f}; SIC AUC={r['SIC']['AUC']:.3f}, R²={r['SIC']['r2']:.3f}; SOC mineral R²={r['SOC_mineral']['r2']:.3f}; BD R²={r['BD']['r2']:.3f}\n")
  fh.write('\n## Present stocks (10′)\n\n')
  for s in ['_0_30','_30_100','_100_200','0_200']:
    fh.write(f'- {s}: {stocks[s]}\n')
  if s30: fh.write(f'\n## 30″ stocks 0–30\n\n{json.dumps(s30,indent=1)}\n')
  if s30100: fh.write(f'\n## 30″ stocks 30–100\n\n{json.dumps(s30100,indent=1)}\n')
  if s100200: fh.write(f'\n## 30″ stocks 100–200\n\n{json.dumps(s100200,indent=1)}\n')
  fh.write('\n## Figures\n\n')
  for f in sorted(glob.glob(FM+'/*.png')+glob.glob(FS+'/*.png')):
    fh.write(f'- {f}\n')
  fh.write('\n## 中文相对 v6\n\nv7：Huang 式 QC；随机 10 折主精度；疏化降 SOC；30″ 现状图；Huang ΔpH 氮路径；长英文 Word。\n')
print('WORD',path,os.path.getsize(path))
print('MD',md_path,os.path.getsize(md_path))
# checkpoint paper_numbers
P['manuscript']=dict(docx=path,md=md_path,updated='v7 full RA')
if s30: P['stocks_30arcsec_0_30']=s30
json.dump(P,open(f'{O}/paper_numbers_v7.json','w'),indent=1)
print('checkpoint ok')
