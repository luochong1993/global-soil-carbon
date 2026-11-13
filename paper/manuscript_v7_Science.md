# Global soil organic and inorganic carbon under climate-zone shifts and nitrogen acidification

**Science Research Article draft (v7)**  
Primary accuracy: **random 10-fold CV** (Huang et al. 2024 practice). Target resolution: **~1 km (30″)**.  
Full formatted manuscript with embedded figures: `paper/manuscript_v7_Science.docx`.

## Abstract

Soils store SOC and SIC that respond differently to climate and nitrogen. Extending Huang et al. (2024), we jointly map SOC+SIC to 2 m after Huang-style QC and equal-area splines. Models (XGBoost) were selected by random 10-fold CV, with 0.5° declustering and a PEATMAP-anchored organic-horizon hurdle. Present stocks (10′): **2492 Pg SOC**, **1603 Pg SIC** (0–200 cm). Global **30″ mosaics** for 0–30 cm give SOC **908 Pg** and SIC **104 Pg** (vs 10′ 858 / 185). Random-CV SIC AUC **0.95–0.97**; amount R² **0.31–0.49**; pH R² **0.65–0.67** (below Huang’s 0.79 / 0.85—reported honestly). Equilibrium climate projections show SOC↓≈SIC↑ cancellation; time-limited τ responses imply net total-C loss. Huang ΔpH formula on IMAGE N yields **1.8–2.5 Pg** topsoil SIC loss by 2050 (below Huang 10–23 unless high-N scaled).

## Methods (essentials)

- **QC:** drop pre-1970, litter/O, bad depths, duplicates; spline to 0–30/30–100/100–200 cm (`qc_flow.json`).
- **CV:** random 10-fold primary; XGB hyperparameter search.
- **SOC bias:** organic hurdle + PEATMAP 4.23 Mkm² + 0.5° declustering.
- **30″ maps:** climate from 10′ bilinear index + native 30″ elev; tiled COGs in `out/v7/maps30s/`. Futures: delta method.
- **N path:** ΔpH=−0.06·Nin+0.11; SIC via finite difference; IMAGE + high-N sensitivity + Zamanian.

## Random 10-fold CV

| Depth | pH R² | SIC AUC | SIC R² | SOC mineral R² | BD R² |
|-------|-------|---------|--------|----------------|-------|
| 0–30 | 0.645 | 0.948 | 0.307 | 0.643 | 0.77 |
| 30–100 | 0.667 | 0.956 | 0.456 | 0.388 | 0.813 |
| 100–200 | 0.672 | 0.965 | 0.494 | 0.434 | 0.814 |

Huang benchmarks: SIC AUC≈0.99, SIC R²≈0.79, pH R²≈0.85 (random CV).

## Present stocks

### 10′ (headline 0–200 totals)

| Layer | SOC (Pg) | SIC (Pg) |
|-------|----------|----------|
| 0–30 | 858 | 185 |
| 30–100 | 826 | 614 |
| 100–200 | 808 | 804 |
| **0–200** | **2492** | **1603** |

### 30″ (~1 km)

| Layer | SOC (Pg) | SIC (Pg) | Notes |
|-------|----------|----------|-------|
| 0–30 | 908 | 104 | **Primary 1 km product** |
| 30–100 | 1046 | 437 | Mosaic complete; integral provisional |
| 100–200 | 2126 | 528 | Mosaic complete; SOC integral inflated vs 10′ (organic nesting not applied at 30″)—prefer 10′ for deep totals |

## Figures

### Main (`figs/v7_main/`)
- Fig1 present stocks (Robinson / cividis)
- Fig2 random CV
- Fig3 climate zones / trade-off
- Fig4 eq vs transient
- Fig5 N acidification

### SI (`figs/v7_SI/`)
- FigS1 QC flow · S2 LUCAS · S3 zone shift · S4 BD–SOC · S5 N sensitivity · S6 depth profiles · S7 organic P · S8 30″ vs 10′

## 中文：相对 v6

v7 已完成：Huang 式 QC；三层随机 10 折 CV；疏化后 10′ 储量；**全球 30″ SOC/SIC/pH 三层镶嵌**；0–30 cm 30″ 与 10′ 对照；Huang ΔpH 氮路径；主图5+支撑图8；英文长稿 Word。深層 30″ SOC 积分偏高（有机层概率未按 0–30 镶嵌嵌套），0–200 总量以 10′ 为准。SIC/pH R² 仍低于 Huang，已如实写。

## Paths

- Word: `paper/manuscript_v7_Science.docx`
- Numbers: `out/v7/paper_numbers_v7.json`
- Methods: `out/v7/methods_notes_v7.md`
- 30″ GeoTIFFs: `out/v7/maps30s/`
