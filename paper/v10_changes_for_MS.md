# v10 numbers for manuscript update (do not rewrite here; update from these)

## Accounting fix (Fig. 3 / Fig. 5)
Maps and headlines now use the **same** ensemble: **10 random-10-fold fold-models of the final v7/v8 workflow × 6 GCMs**. Maps = ensemble **mean**. Checked: SSP5-8.5 map integrals = −378 / +229 Pg = headline means (was −206 / +206 from v5/v6 maps vs −246 / +290 from v5 bootstrap headlines).

## Present stocks with 90% CI and Huang-style ±1 SD
Uncertainty = fold-model spread × Monte Carlo on BD (±5%), CF (log-U 0.5–2× median), effective thickness (N(1,0.05/0.10)), organic C-density (±20%). Assumptions labelled in `out/v10/paper_numbers_v10.json`.

| Pool | Mean (Pg) | 90% CI | ±1 SD |
|---|---|---|---|
| SOC 0–30 | 848 | 774–924 | ±46 |
| SIC 0–30 | 178 | 163–194 | ±9 |
| MAOC 0–30 | 518 | 473–565 | ±28 |
| POC 0–30 | 183 | 163–205 | ±13 |
| SOC 0–200 | 2506 | 2263–2761 | ±151 |
| SIC 0–200 | 1598 | 1408–1801 | ±119 |
| TC 0–200 | 4105 | 3675–4549 | ±265 |
| MAOC 0–100 | 1048 | 946–1152 | ±62 |
| POC 0–100 | 370 | 324–416 | ±28 |

SIC 0–200 remains ~30% below Huang’s 2305 ± 636; the new CI upper bound (1801) still sits below Huang’s mean but overlaps the lower half of Huang’s ±1 SD.

## Future climate (final models; 2081–2100 vs present)
| SSP | Eq ΔSOC 0–200 | Eq ΔSIC | Eq ΔTC | TL ΔTC (τ sampled) |
|---|---|---|---|---|
| 1-2.6 | −129 (−240 to −54) | +84 | ~−45 | −54 (−…) |
| 2-4.5 | −217 (−357 to −136) | +138 | | −96 |
| 3-7.0 | −311 (−468 to −200) | +197 | | −144 |
| 5-8.5 | **−378 (−526 to −254)** | **+229 (130–382)** | **−150 (−245 to −41)** | **−180 (−282 to −100)** |

v9 text used v5 headline −246 / +290 / TL −182. **Update to v10.** TL ΔTC is almost unchanged (−180 vs −182); equilibrium SOC loss is larger and SIC gain smaller than v5, so eq ΔTC is more negative (−150 vs ~+25).

MAOC/POC 0–30 (SSP5-8.5): eq ΔMAOC −78, ΔPOC −39; by-2100 (τ log-U) ΔMAOC −37, ΔPOC −39.

Zone-shift trade-off (SOC↓ SIC↑) under SSP5-8.5: **69 Mkm²** (was 57 on v6 maps).

## N acidification (2020–2050)
GLOBIOM/INMS **not obtained** (INMS registration wall; no Zenodo grid). IMAGE ISIMIP3b fertilizer; **SSP2-4.5 = mean(SSP1-2.6, SSP3-7.0)** — document as interpolation.

Topsoil loss-only (Pg): 1.6 / 1.8 / 2.1 / 2.2 for SSP1-2.6 / 2-4.5 / 3-7.0 / 5-8.5. Full 0–200: 13.4 / 15.1 / 17.2 / 17.4. Still far below Huang’s 10–23 Pg GLOBIOM targets.

## Bias tests (adoption rule)
- Cropland fraction covariate: CV R² +0.001 only → **not adopted**.
- LUCAS: prior +28.6 Mg/ha was largely 0–30 map vs 0–20 observations. Depth-harmonised bias **+6.9** → **report this**; do not rescale global maps.
- NDVI not available quickly; IMAGE cropland was the proxy test.

## Figures
`figs/v10_main/` Fig1–7 and `figs/v10_SI/` FigS1–S14 (Nature Food style retained). Machine-readable: `out/v10/paper_numbers_v10.json`, `out/v10/KEY_NUMBERS_v10.json`, `out/v10/ensemble_v10.json`, `out/v10/ens_maps.npz`.
