# Global soil organic and inorganic carbon under climate-zone shifts and nitrogen acidification

Science Research Article draft (v7). Random 10-fold CV primary. Target resolution ~1 km (30″).

## Abstract

Soils store organic carbon (SOC) and inorganic carbon (SIC) that respond differently to climate and nitrogen inputs, yet global assessments rarely treat them together. Extending the digital soil mapping framework of Huang et al. (2024) for SIC, we produce joint SOC–SIC estimates to 2 m depth from WoSIS observations after Huang-style quality control and mass-preserving depth splines. Models (XGBoost) were selected by random 10-fold cross-validation—the same class of metric Huang et al. reported—and trained with 0.5° cell declustering and an organic-horizon hurdle anchored to PEATMAP. Present-day stocks on the 10′ analysis grid are 2492 Pg SOC and 1603 Pg SIC (0–200 cm; total 4095 Pg). Thirty-arcsecond (~1 km) mosaics of 0–30 cm SOC, SIC and pH yield SOC 908 Pg and SIC 104 Pg, compared with 858 and 185 Pg at 10′. Random-CV SIC presence skill is high (AUC 0.95–0.97) while amount R² (0.31–0.49) and pH R² (0.65–0.67) remain below Huang’s benchmarks; we report this gap rather than emphasizing spatial CV. Equilibrium space-for-time projections under SSP5-8.5 imply large SOC losses nearly offset by SIC gains, whereas depth-specific first-order turnover constraints imply net total-carbon loss by 2100 because carbonate accumulation is slow. Applying Huang’s ΔpH = −0.06·Nin + 0.11 on ISIMIP IMAGE fertilizer yields 1.8–2.5 Pg topsoil SIC loss by 2050—below Huang’s 10–23 Pg—unless nitrogen inputs are scaled to high-N sensitivities that recover those magnitudes. Joint SOC–SIC vulnerability therefore depends on both time-scale assumptions and nitrogen scenario choice.

## Random 10-fold CV

- _0_30: pH R²=0.645; SIC AUC=0.948, R²=0.307; SOC mineral R²=0.643; BD R²=0.770
- _30_100: pH R²=0.667; SIC AUC=0.956, R²=0.456; SOC mineral R²=0.388; BD R²=0.813
- _100_200: pH R²=0.672; SIC AUC=0.965, R²=0.494; SOC mineral R²=0.434; BD R²=0.814

## Present stocks (10′)

- _0_30: {'SOC': 857.6398573646535, 'SIC': 185.09090256011712, 'SOC_org': 146.32804807469196, 'SOC_min': 711.3118091465683}
- _30_100: {'SOC': 826.1744939939013, 'SIC': 614.4433313095367, 'SOC_org': 99.50217658592872, 'SOC_min': 726.6723173633744}
- _100_200: {'SOC': 808.218788070561, 'SIC': 803.7562861309892, 'SOC_org': 110.97571648456129, 'SOC_min': 697.2430716006156}
- 0_200: {'SOC': 2492.0331394291156, 'SIC': 1603.290520000643, 'TC': 4095.3236594297587}

## 30″ stocks 0–30

{
 "SOC_0_30_Pg": 907.8916335728734,
 "SIC_0_30_Pg": 104.44047776325043,
 "land_pixels": 175334000,
 "grid": "30arcsec",
 "compare_10arcmin": {
  "SOC": 857.6398573646535,
  "SIC": 185.09090256011712,
  "SOC_org": 146.32804807469196,
  "SOC_min": 711.3118091465683
 }
}

## 30″ stocks 30–100

{
 "SOC_Pg": 1046.3733562554041,
 "SIC_Pg": 437.37430560493954,
 "land_pixels": 175334000,
 "depth": "_30_100",
 "grid": "30arcsec"
}

## 30″ stocks 100–200

{
 "SOC_Pg": 2125.9194571652465,
 "SIC_Pg": 528.3430383265792,
 "land_pixels": 175334000,
 "depth": "_100_200",
 "grid": "30arcsec"
}

## Figures

- figs/v8_SI/FigS10_MAOC_uncertainty_subsoil.png
- figs/v8_SI/FigS11_dominant_driver_pH_SIC.png
- figs/v8_SI/FigS12_30arcsec_zoom.png
- figs/v8_SI/FigS13_equilibrium_vs_time_limited.png
- figs/v8_SI/FigS1_random_CV.png
- figs/v8_SI/FigS2_fraction_data.png
- figs/v8_SI/FigS3_SHAP_top_features.png
- figs/v8_SI/FigS4_SHAP_dependence.png
- figs/v8_SI/FigS5_PDP_thresholds.png
- figs/v8_SI/FigS6_pH_SIC_curve.png
- figs/v8_SI/FigS7_tau_sensitivity.png
- figs/v8_SI/FigS8_path_analysis.png
- figs/v8_SI/FigS9_deep_layers.png
- figs/v8_main/Fig1_present_stocks.png
- figs/v8_main/Fig2_SIC_share_countries.png
- figs/v8_main/Fig3_climate_change.png
- figs/v8_main/Fig4_N_acidification.png
- figs/v8_main/Fig5_bivariate_SOC_SIC.png
- figs/v8_main/Fig6_MAOC_POC.png
- figs/v8_main/Fig7_drivers.png

## 中文相对 v6

v7：Huang 式 QC；随机 10 折主精度；疏化降 SOC；30″ 现状图；Huang ΔpH 氮路径；长英文 Word。
