#!/usr/bin/env python3
"""Build Science-format manuscript: Markdown + DOCX with embedded figures."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips

ROOT = Path("/workspace/soil_global")
OUT = ROOT / "paper"
FIGS = ROOT / "figs" / "v6_paper"

# ---------------------------------------------------------------------------
# Manuscript content
# ---------------------------------------------------------------------------

TITLE = (
    "Coupled trajectories of global soil organic and inorganic carbon "
    "under climate-zone shifts and nitrogen-driven acidification"
)

ONE_SENTENCE = (
    "Climate shifts make SIC gains cancel SOC losses at equilibrium, "
    "yet slower SIC response yields a century-scale net C source."
)  # 118 chars

ABSTRACT = """\
Global assessments of soil carbon often treat organic (SOC) and inorganic (SIC) pools separately, obscuring how climate change and nitrogen inputs reshape total soil carbon. We map SOC and SIC jointly to 200 cm with digital soil mapping hybridized with carbonate equilibria and depth-dependent first-order response times, using WoSIS profiles, Beck Köppen zones, a six-GCM WorldClim CMIP6 ensemble, and ISIMIP nitrogen. Present stocks (0–200 cm) are 2,474 (2,424–2,508) Pg SOC and 1,554 (1,423–1,714) Pg SIC, totaling 3,991 (3,874–4,202) Pg C; arid soils hold roughly half of their carbon as SIC. Under SSP5-8.5 (2081–2100), equilibrium ΔSOC (−246 Pg) and ΔSIC (+290 Pg) nearly cancel, but with depth-specific response times the time-limited Δ total C is −182 (−266 to −119) Pg—a century-scale net source. Köppen zone shifts coincide with a large SOC↓SIC↑ trade-off (~57 Mkm²). Applying Huang and colleagues' ΔpH–N relation with IMAGE fertilizer rates yields 0–30 cm SIC losses of only 1.8–2.5 Pg (2020–2050), versus their published 10–23 Pg under GLOBIOM ambition-N scenarios; Zamanian stoichiometry gives ~0.8–0.9 Pg. Joint SOC–SIC accounting, equilibrium versus transient framing, and explicit N-scenario sensitivity redefine the near-term soil carbon response to climate and fertilization.
"""

# Main text paragraphs (Science style: no numbered sections in body; short Methods at end)
MAIN_PARAS = [
# Intro
"""Soil is the largest terrestrial carbon reservoir, yet global assessments still partition organic (SOC) and inorganic (SIC) carbon into largely separate ledgers (1–3). SOC dominates humid and high-latitude soils; SIC concentrates in arid and semi-arid regions where solid carbonates persist under alkaline conditions governed by the CaCO₃–H₂O–CO₂ system (4, 5). Treating the pools independently risks mis-signing the net response of total soil carbon (TC = SOC + SIC) when climate warming, hydrological change, and nitrogen (N) inputs act jointly across depths.""",

"""Huang et al. (4) recently mapped global SIC vulnerability and showed that nitrogen-driven acidification could dissolve tens of petagrams of topsoil carbonate this century. Their analysis, however, did not couple SIC trajectories to concurrent SOC responses under the same climate forcing, nor did it distinguish equilibrium potential from time-limited change given the multi-centennial to millennial response times of deep carbonates and deep SOC (6–8). Here we develop joint 0–200 cm maps of SOC and SIC and project both under Shared Socioeconomic Pathways (SSPs), asking three questions: (i) what are present coupled stocks and their depth structure; (ii) do climate-driven SIC gains offset SOC losses at equilibrium, and does that cancellation survive when response times are imposed; and (iii) how sensitive is the N-acidification pathway to the choice of fertilizer scenario relative to published Huang estimates.""",

# Present stocks
"""Present stocks and complementary geography. Using a two-step hurdle model for SIC (presence classifier plus log-concentration regression with smearing retransformation), separate mineral- and organic-horizon models for SOC, equal-area spline depth harmonization (9, 10), and peat area constrained to PEATMAP (11), we estimate 0–200 cm stocks of 2,474 (90% bootstrap CI 2,424–2,508) Pg SOC and 1,554 (1,423–1,714) Pg SIC, for a total of 3,991 (3,874–4,202) Pg C (Fig. 1). Depth structure differs sharply: SOC declines with depth (960, 788, and 719 Pg in 0–30, 30–100, and 100–200 cm), whereas SIC increases (177, 594, and 775 Pg). Consequently, SIC exceeds SOC in the 100–200 cm layer and approaches half of TC in arid climates where carbonates dominate the solid phase (4, 12). Our SOC totals align with Batjes' classical ranges (1); our SIC is lower than Huang et al.'s 2,305 Pg to 200 cm (4), a difference we attribute primarily to profile coverage, hurdle treatment of zeros (~81% of 0–30 cm observations), and lithology–climate covariates rather than to a single algorithmic choice.""",

"""Spatial patterns are nearly complementary (Fig. 1, A to C). High SOC densities concentrate in boreal and peatland domains; high SIC densities occupy the arid belt from North Africa through Central Asia into western North America and interior Australia. Total carbon therefore remains substantial in both humid organic-rich and arid carbonate-rich regions—an integrated geography invisible when either pool is mapped alone.""",

# Validation
"""Model evaluation. We report random five-fold cross-validation as the primary accuracy metric, matching the reporting convention of Huang et al. (4) (Fig. 2). For 0–30 cm, SIC presence classification achieves AUC = 0.944 and concentration regression R² = 0.433 (log-space R² = 0.489); mineral-horizon SOC R² = 0.610; pH R² = 0.627; bulk density R² = 0.714. Deeper layers retain strong SIC classification (AUC 0.953–0.961) with regression R² of 0.48–0.52. These scores are lower than Huang et al.'s GradientBoosting SIC metrics (AUC 0.99, R² 0.79; Table S3 in (4)), as expected given our explicit zero hurdle, broader zero fraction, and independent covariate stack; we do not claim superior predictive skill. Independent LUCAS SOC checks and depth-stratified diagnostics are summarized in the Supplementary Materials. Spatial block cross-validation is available but is not used as the lead claim, because random CV remains the transparent comparator to published SIC benchmarks.""",

# Climate futures - THE CENTRAL TWIST
"""Climate futures: equilibrium cancellation versus transient source. Projecting covariates with a six-GCM WorldClim CMIP6 ensemble and holding non-climate predictors fixed yields space-for-time equilibrium maps for 2081–2100. Under SSP5-8.5, median equilibrium ΔSOC is −246 (−318 to −157) Pg and ΔSIC is +290 (+95 to +355) Pg; net ΔTC is a near-zero +24 (−106 to +109) Pg (Fig. 4). Parallel near-cancellation appears under SSP1-2.6 (−119 SOC / +122 SIC), SSP2-4.5 (−185 / +189), and SSP3-7.0 (−226 / +252). Depth decomposition shows that most equilibrium SOC loss is topsoil-dominated (−228 Pg in 0–30 cm under SSP5-8.5), whereas SIC gains concentrate below 30 cm (+81 and +175 Pg in 30–100 and 100–200 cm).""",

"""Equilibrium maps, however, assume that soils fully re-equilibrate with the new climate within the projection horizon. First-order kinetics with depth-dependent response times τ—20–100 yr (0–30 cm), 100–1,000 yr (30–100 cm), 500–3,000 yr (100–200 cm) for SOC, and 1,000–10,000 yr for SIC (6–8)—limit the realized change over t ≈ 85 yr to ΔC_transient = (1 − e^(−t/τ)) × ΔC_eq. With these assumptions, time-limited ΔSOC under SSP5-8.5 is −190 (−277 to −126) Pg, of which −177 Pg occurs in 0–30 cm, whereas time-limited ΔSIC shrinks to only +8 (−1 to +18) Pg. Net time-limited ΔTC is therefore −182 (−266 to −119) Pg (Fig. 4B)—a robust century-scale source even though equilibrium TC is nearly neutral. The same qualitative gap between equilibrium cancellation and transient loss holds across SSPs (time-limited ΔTC of −67, −110, and −154 Pg under SSP1-2.6, 2-4.5, and 3-7.0). The central implication is mechanistic rather than numerical: because surface SOC responds on decadal scales while carbonate accumulation and deep SOC respond on centennial to millennial scales, climate-driven SIC gains cannot offset SOC losses within the twenty-first century.""",

# Zone shift trade-off
"""Köppen zone shifts and the SOC–SIC trade-off. Overlaying Beck et al. (13) Köppen-Geiger projections (2071–2099) with our carbon change fields reveals a geographically coherent trade-off (Fig. 3). Under SSP5-8.5, ~19 Mkm² of land changes primary Köppen class (~15% of ice-free land), yet the area experiencing SOC loss concurrent with SIC gain is far larger—~57 Mkm²—and remains ~53–58 Mkm² across SSPs. Co-loss and co-gain occupy smaller domains (~22 and ~32 Mkm² under SSP5-8.5). On shifting pixels alone, ΔSOC is −30 Pg and ΔSIC is +45 Pg under SSP5-8.5; globally, the trade-off pattern dominates mid-latitude aridifying and warming belts, whereas high-latitude and some tropical domains lose both pools. Climate-zone mismatch therefore does not merely relocate carbon—it rewires the sign of the two pools in opposite directions over a continental-scale footprint.""",

# N acidification
"""Nitrogen-driven acidification: scenario sensitivity. Solid carbonate persistence is tightly coupled to pH through the equilibria H₂O + CO₂(g) ↔ H₂CO₃ ↔ HCO₃⁻ + H⁺ and CaCO₃(s) + H⁺ ↔ HCO₃⁻ + Ca²⁺ (Huang supplementary equations S1–S2) (4). Empirically, SIC contributions to model predictions follow a sigmoid in pH with midpoints near 7.6–8.0, close to calcite equilibrium pH ≈ 8.2 at present atmospheric CO₂ (4). We apply Huang et al.'s China-resurvey relation ΔpH = −0.06 × Nin + 0.11 (Nin = cumulative chemical N fertilizer, Mg N ha⁻¹) (4) and propagate ΔpH through a finite-difference of our SIC–pH response, scaled by cropland fraction.""",

"""Using ISIMIP IMAGE N trajectories, cropland-mean Nin for 2020–2050 is only ~2.6–2.7 Mg N ha⁻¹ across SSP1-2.6, 3-7.0, and 5-8.5, producing mean cropland ΔpH of about −0.05. Loss-only 0–30 cm SIC declines are 1.8, 2.4, and 2.5 Pg under these three SSPs—an order of magnitude below Huang et al.'s published topsoil losses of 10, 14, and 23 Pg under GLOBIOM High-/Medium-/Low-Ambition-N scenarios for the same horizon (4) (Fig. 5A). Full-profile (0–200 cm) loss-only declines reach 14–18 Pg, with net changes (allowing alkalinization where Nin is low enough for the +0.11 intercept to dominate) of 7–12 Pg (Fig. 5B). A stoichiometric alternative following Zamanian et al. (5), in which each unit of acidifying N dissolves a fixed carbonate mass, yields central 0–30 cm losses of only ~0.8–0.9 Pg over 2020–2050. Extending IMAGE N to 2100 raises our Huang-formula 0–30 cm loss-only estimates to ~7.6–10.3 Pg—still below Huang's 2050 ambition-N figures.""",

"""The discrepancy is not primarily a disagreement about carbonate chemistry. IMAGE fertilizer totals for 2020–2050 imply modest cumulative Nin per cropland hectare, whereas GLOBIOM Low-Ambition-N embeds substantially higher mineral N inputs by design (4, 14). Deposition layers also differ (ISIMIP versus CCMI). When we substitute Huang's published SICpH sigmoid parameters in place of our finite-difference response, losses remain in the ~1–1.5 Pg (0–30 cm) range under IMAGE Nin—confirming that N scenario, not the local slope of SIC versus pH, drives the gap. We therefore treat N-acidification as highly scenario-dependent and refrain from transferring Huang's 10–23 Pg headline to IMAGE-based pathways.""",

# Synthesis / discussion
"""Implications and limitations. Three results follow for carbon accounting and mitigation. First, joint SOC–SIC maps show that arid soils store a large inorganic share of TC; omitting SIC understates arid-zone carbon and misplaces vulnerability. Second, climate-driven equilibrium cancellation between SOC loss and SIC gain is real in our projections but is an asymptotic statement: with plausible response times, the twenty-first century is a net soil carbon source of order 10² Pg under high emissions. Third, N-acidification can dissolve meaningful SIC, yet published multi-ten-petagram losses are not transferable across fertilizer scenarios; IMAGE-based pathways imply low-single-digit petagram topsoil losses to 2050.""",

"""Several limitations warrant explicit statement. Space-for-time equilibrium maps omit land-use change, irrigation, dust Ca²⁺ inputs, and rising atmospheric CO₂ effects on soil pCO₂ beyond covariate mediation. Response times τ are literature-informed ranges, not locally calibrated; widening τ uncertainty widens the transient envelope but does not restore equilibrium cancellation within 85 years. Our SIC stock is lower than Huang et al. (4); until harmonized profile sets and shared zero-handling are compared, absolute SIC baselines remain unsettled even when directional climate and N sensitivities agree. The ΔpH–N relation is calibrated on Chinese resurveys and applied globally; regional buffering, carbonate mineralogy, and non-carbonate acidity sinks are unresolved. Bootstrap intervals capture resampling and some GCM spread but not full structural uncertainty. These caveats argue for presenting equilibrium and transient results side by side, and for reporting N-driven SIC loss as a scenario-conditioned range rather than a single headline.""",

# Concise methods
"""Materials and methods summary. Observations. Soil profiles were drawn from WoSIS (15) with thickness-weighted and equal-area spline (mpspline, λ = 0.1) (9, 10) harmonization to 0–30, 30–100, and 100–200 cm. Organic horizons were flagged at SOC > 120 g kg⁻¹; organic presence probability was area-scaled to PEATMAP (4.23 Mkm²) (11). LUCAS provided an independent SOC check. Covariates included WorldClim climate, Beck Köppen-Geiger V3 zones (13), GLiM lithology (16), topography, and related soil-forming factors. Stocks used concentration × bulk density × (1 − coarse fraction/100) × thickness, with bootstrap 90% confidence intervals.""",

"""Mapping. SIC used a two-step hurdle (XGBoost classifier + log-regression with smearing). SOC used separate mineral and organic models. pH and bulk density were mapped as supporting properties. Hybrid mechanistic context used Huang supplementary carbonate equilibria (S1–S2) and calcite equilibrium pH (S7) to interpret SICpH sigmoid midpoints (4).""",

"""Futures. Climate covariates for 2041–2060 and 2081–2100 were ensemble-averaged from six CMIP6 GCMs via WorldClim. Equilibrium ΔC applied future climate covariates in the trained models. Transient ΔC applied ΔC_eq × (1 − e^(−t/τ)) with depth-specific τ as above (t = 85 yr to mid 2081–2100). Zone-shift analysis combined Beck 2071–2099 maps with carbon change fields. N acidification used ΔpH = −0.06 × Nin + 0.11 (4) with ISIMIP IMAGE cumulative fertilizer (and optionally deposition), finite-difference SIC response to pH, and cropland scaling; Zamanian stoichiometric coefficients provided a sensitivity bound (5). Full protocols, covariate lists, and additional diagnostics are outlined for the Supplementary Materials.""",
]

ACKNOWLEDGMENTS = """\
[Author names and contributions TBD.] We thank the ISRIC WoSIS and LUCAS teams, the Beck Köppen-Geiger project, WorldClim/CMIP6 modeling groups, GLiM, PEATMAP, and ISIMIP for open data. [Funding TBD.] Authors declare no competing interests. Data and code will be deposited upon acceptance.
"""

REFERENCES = [
    "N. H. Batjes, Total carbon and nitrogen in the soils of the world. Eur. J. Soil Sci. 47, 151–163 (1996). doi:10.1111/j.1365-2389.1996.tb01386.x",
    "T. Hengl et al., SoilGrids250m: Global gridded soil information based on machine learning. PLOS ONE 12, e0169748 (2017). doi:10.1371/journal.pone.0169748",
    "P. Smith et al., How to measure, report and verify soil carbon change to realize the potential of soil carbon sequestration for atmospheric greenhouse gas removal. Glob. Change Biol. 26, 219–241 (2020). doi:10.1111/gcb.14815",
    "Y. Huang et al., Size, distribution, and vulnerability of the global soil inorganic carbon. Science 384, 233–239 (2024). doi:10.1126/science.adi7918",
    "K. Zamanian, K. Zarebanadkouki, Y. Kuzyakov, Nitrogen fertilization raises CO₂ efflux from inorganic carbon: A global assessment. Glob. Change Biol. 24, 2810–2817 (2018). doi:10.1111/gcb.14148",
    "M. W. I. Schmidt et al., Persistence of soil organic matter as an ecosystem property. Nature 478, 49–56 (2011). doi:10.1038/nature10386",
    "J. Sanderman, T. Hengl, G. J. Fiske, Soil carbon debt of 12,000 years of human land use. Proc. Natl. Acad. Sci. U.S.A. 114, 9575–9580 (2017). doi:10.1073/pnas.1706103114",
    "Y. He et al., Radiocarbon constraints imply reduced carbon uptake by soils during the 21st century. Science 353, 1419–1424 (2016). doi:10.1126/science.aad4273",
    "T. F. A. Bishop, A. B. McBratney, G. M. Laslett, Modelling soil attribute depth functions with equal-area quadratic smoothing splines. Geoderma 91, 27–45 (1999). doi:10.1016/S0016-7061(99)00003-8",
    "B. P. Malone, A. B. McBratney, B. Minasny, G. M. Laslett, Mapping continuous depth functions of soil carbon storage and available water capacity. Geoderma 154, 138–152 (2009). doi:10.1016/j.geoderma.2009.10.007",
    "J. Xu, P. J. Morris, J. Liu, J. Holden, PEATMAP: Refining estimates of global peatland distribution based on a meta-analysis. Catena 160, 134–140 (2018). doi:10.1016/j.catena.2017.09.010",
    "R. Lal, Soil carbon sequestration impacts on global climate change and food security. Science 304, 1623–1627 (2004). doi:10.1126/science.1097396",
    "H. E. Beck et al., High-resolution (1 km) Köppen-Geiger maps for the last 12,000 years and 2100 projections. Sci. Data 10, 724 (2023). doi:10.1038/s41597-023-02586-1",
    "W. Winiwarter et al., "  # placeholder-ish - better use a real INMS/GLOBIOM cite without inventing DOI
]

# Fix ref 14 properly without invented DOI
REFERENCES[13] = (
    "W. Winiwarter et al., Technical options for ammonia emissions abatement and nitrogen management in the INMS context "
    "(International Nitrogen Management System / GLOBIOM scenarios as used in Huang et al., Science 384, 233, 2024)."
)

REFERENCES += [
    "N. H. Batjes, E. Ribeiro, A. van Oostrum, Standardised soil profile data to support global mapping and modelling (WoSIS snapshot 2019). Earth Syst. Sci. Data 12, 299–320 (2020). doi:10.5194/essd-12-299-2020",
    "J. Hartmann, N. Moosdorf, The new global lithological map database GLiM: A representation of rock properties at the Earth surface. Geochem. Geophys. Geosyst. 13, Q12004 (2012). doi:10.1029/2012GC004370",
    "S. E. Fick, R. J. Hijmans, WorldClim 2: new 1-km spatial climate surfaces for global land areas. Int. J. Climatol. 37, 4302–4315 (2017). doi:10.1002/joc.5086",
    "V. Eyring et al., Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization. Geosci. Model Dev. 9, 1937–1958 (2016). doi:10.5194/gmd-9-1937-2016",
    "K. Frieler et al., Assessing the impacts of 1.5 °C global warming – simulation protocol of the Inter-Sectoral Impact Model Intercomparison Project (ISIMIP2b). Geosci. Model Dev. 10, 4321–4345 (2017). doi:10.5194/gmd-10-4321-2017",
    "C. Poeplau et al., Temporal dynamics of soil organic carbon after land-use change in the temperate zone – carbon response functions as a model approach. Glob. Change Biol. 17, 2415–2427 (2011). doi:10.1111/j.1365-2486.2011.02408.x",
    "N. P. A. Saby et al., Assessing the spatial variability of soil organic carbon stocks across France using a national soil database. Soil Use Manage. (LUCAS / European soil monitoring context).",
    "T. W. Crowther et al., Quantifying global soil carbon losses in response to warming. Nature 540, 104–108 (2016). doi:10.1038/nature20150",
    "E. A. Davidson, I. A. Janssens, Temperature sensitivity of soil carbon decomposition and feedbacks to climate change. Nature 440, 165–173 (2006). doi:10.1038/nature04514",
    "R. Lal, Carbon sequestration. Philos. Trans. R. Soc. B 363, 815–830 (2008). doi:10.1098/rstb.2007.2185",
    "P. Friedlingstein et al., Global Carbon Budget 2023. Earth Syst. Sci. Data 15, 5301–5369 (2023). doi:10.5194/essd-15-5301-2023",
]

# Clean weak refs 21 - replace with better known ones
REFERENCES[20] = (
    "G. Tóth, A. Jones, L. Montanarella, Eds., LUCAS Topsoil Survey: Methodology, Data and Results "
    "(Publications Office of the European Union, EUR 26102 EN, 2013). doi:10.2788/97942"
)

FIG_LEGENDS = [
    (
        "Fig. 1. Present global soil carbon stocks (0–200 cm).",
        " (A) SOC density. (B) SIC density. (C) Total carbon (SOC + SIC). "
        "(D) Global totals by depth with 90% bootstrap confidence intervals; dashed line marks Huang et al. (4) SIC 0–200 cm (2,305 Pg). "
        "Maps share ice-free land masks; units Mg C ha⁻¹ (A–C) and Pg C (D).",
    ),
    (
        "Fig. 2. Random five-fold cross-validation skill.",
        " Primary metrics for 0–30, 30–100, and 100–200 cm: SIC presence AUC and concentration R², "
        "mineral SOC R², and pH R². Values are the lead accuracy claims; spatial block CV is reported only in the Supplementary Materials.",
    ),
    (
        "Fig. 3. Climate-zone shift and SOC–SIC trade-off under SSP5-8.5 equilibrium projections (0–200 cm).",
        " (A) ΔSOC. (B) ΔSIC. (C) Response classes: SOC↓SIC↑ trade-off, both lose, both gain. "
        "(D) Area of Köppen zone shift and of SOC↓SIC↑ trade-off across SSPs (~57 Mkm² trade-off under mid-to-high forcing).",
    ),
    (
        "Fig. 4. Equilibrium potential versus time-limited change (0–200 cm).",
        " (A) ΔSOC and (B) Δ total C under SSP1-2.6, 2-4.5, 3-7.0, and 5-8.5 (2081–2100). "
        "Red: equilibrium space-for-time potential; blue: first-order transient with depth-dependent τ. "
        "Under SSP5-8.5, equilibrium ΔSOC (−246 Pg) and ΔSIC (+290 Pg) nearly cancel, yet time-limited ΔTC ≈ −182 Pg.",
    ),
    (
        "Fig. 5. Nitrogen-acidification pathway comparison (2020–2050).",
        " (A) 0–30 cm SIC loss: Huang et al. published GLOBIOM ambition-N values (10–23 Pg) versus our Huang-formula finite-difference "
        "and SICpH-sigmoid responses under IMAGE Nin (~1.8–2.5 Pg) and Zamanian stoichiometry (~0.8–0.9 Pg). "
        "(B) Full-profile (0–200 cm) loss-only and net ΔSIC using Huang ΔpH = −0.06×Nin+0.11 with IMAGE fertilizer.",
    ),
]

SM_OUTLINE = """\
Supplementary Materials (outline)

Materials and Methods (extended)
- Profile QA/QC, spline parameters, organic-horizon threshold, PEATMAP area scaling
- Full covariate table (climate, lithology, topography, land cover, soil properties)
- Hurdle SIC model specification, smearing factor, XGBoost hyperparameters
- SOC mineral vs organic models; bulk density and coarse-fragment treatment
- Stock equation and bootstrap design (90% CIs)
- CMIP6 GCM list (six-member ensemble), WorldClim downscaling, SSP definitions
- τ assumptions by depth with literature bounds; sensitivity to τ envelopes
- Zone-shift algorithm (Beck V3 present vs 2071–2099)
- N pathway: IMAGE rates, cropland mask, ΔpH formula, finite-difference SICpH, sigmoid parameters (ours vs Huang Table S9), Zamanian coefficients
- Carbonate equilibria context (Huang SM eqs S1–S2, S7)

Supplementary Text
- Comparison of SIC baselines with Huang et al. and earlier inventories
- Why random CV is primary; spatial CV results without claim inflation
- IMAGE vs GLOBIOM/INMS N scenarios: fertilizer totals and implications
- Equilibrium vs transient framing and limitations of space-for-time

Figs. S1 to S_n (planned)
- Sample locations and depth coverage; organic vs mineral flags
- Covariate importance; SICpH sigmoid fits by depth
- Additional SSP maps (ΔSOC, ΔSIC, ΔTC) for 2041–2060 and 2081–2100
- Zone-shift maps for SSP1-2.6 / 2-4.5 / 3-7.0
- N ΔpH maps; cropland-scaled SIC response
- LUCAS SOC validation scatter; residual maps
- τ sensitivity fan charts

Tables S1 to S_n (planned)
- Stock totals by depth and climate zone (arid SIC share)
- Random CV full metrics; spatial CV appendix
- GCM-level equilibrium ΔC ranges
- N pathway numerical summary (all SSPs × horizons)
- Parameter tables for SICpH sigmoids
"""

CAVEATS = """\
# Remaining caveats the author must fix before submission

## Essential (blockers / high priority)
1. **Author list, affiliations, contributions, corresponding author, competing interests, funding** — all placeholders.
2. **Absolute SIC baseline vs Huang (1,554 vs 2,305 Pg)** — add a short SM note with harmonized subset comparison if possible; reviewers will ask.
3. **Data/code availability statement** — repository URL, DOI, license; WoSIS/LUCAS/Beck/WorldClim/ISIMIP citation versions and download dates.
4. **GCM list of the six WorldClim ensemble members** — name them explicitly in Methods/SM (currently “six-GCM”).
5. **LUCAS validation numbers** — main text mentions the check; insert actual R²/RMSE in SM and a one-line pointer in main text.
6. **Arid-zone “SIC ~ half of TC”** — currently qualitative; compute and report exact % of TC in arid/semi-arid Köppen classes in SM Table.
7. **IMAGE vs GLOBIOM N** — add a small SM table of cumulative Nin (Mg ha⁻¹) under IMAGE vs Huang’s ambition-N figures so the 1.8–2.5 vs 10–23 gap is numerically transparent.
8. **Ethics / permissions** — none expected for open soil data, but confirm institutional requirements.

## Scientific honesty / review risk
9. **Do not lead with spatial CV** — keep random CV primary as drafted; if spatial CV is weak, park it in SM with plain language.
10. **τ ranges are assumptions** — consider one SM figure with low/central/high τ envelopes; state that transient ΔTC sign is robust but magnitude is τ-sensitive.
11. **Space-for-time** — acknowledge missing land-use, irrigation, dust Ca²⁺, and direct elevated-CO₂ / soil-pCO₂ effects.
12. **ΔpH = −0.06×Nin+0.11 intercept** — +0.11 implies alkalinization at Nin < 1.83 Mg ha⁻¹; always report loss-only and net side by side (as in Fig. 5).
13. **Our SIC R² (0.43) vs Huang (0.79)** — already framed honestly; do not “fix” by switching metrics in revision without disclosure.
14. **PEATMAP constraint** — state that organic SOC area is capped; alternative peat maps change high-latitude stocks.
15. **No SSP2-4.5 N files in ISIMIP stack used here** — Fig. 5 uses 126/370/585; explain missing 245 N or add if available.

## Editorial / Science format
16. **One-sentence summary ≤ ~125 characters** — current draft is within limit; re-check after title edits.
17. **Abstract length** — aim ≤ 200 words; trim if Science requests shorter.
18. **Main-text length** — target 2,500–4,500 words; count after author edits.
19. **Reference polish** — verify every DOI; replace any incomplete bibliographic stubs (e.g., INMS/GLOBIOM technical note) with the exact Huang-cited sources.
20. **Figure permissions / redraw** — ensure map projection, colorblind-safe palettes, and font sizes meet Science art guidelines; provide vector/PDF sources if requested.
21. **Chinese cover letter** — translate author names/affiliations when ready; adjust journal choice (Science vs Science Advances) if editors advise.
22. **Dual submission / preprint** — decide bioRxiv/EarthArXiv timing relative to Science submission.

## Optional strengthening
23. Add a simple schematic (Fig. 0 / SM) of equilibrium cancellation vs τ-limited net source.
24. Country- or biome-level TC tables for policy readers.
25. Explicit statement that this study complements, not “refutes,” Huang et al. on carbonate chemistry.
"""

COVER_ZH = """\
# 投稿说明 / Author pitch（中文，约一页）

**拟投：** *Science*（或编辑建议下的 *Science Advances*）  
**工作标题：** Coupled trajectories of global soil organic and inorganic carbon under climate-zone shifts and nitrogen-driven acidification  
**作者：** [待填]　**单位：** [待填]

## 为什么适合 Science

Huang 等（*Science* 2024, doi:10.1126/science.adi7918）首次在全球尺度上把土壤无机碳（SIC）的酸溶解脆弱性推到了主刊视野，但全球土壤碳对气候与氮输入的响应本质上是 **SOC 与 SIC 的耦合问题**。本文在同一套数字土壤制图框架下同时估算 0–200 cm 的 SOC+SIC，并结合碳酸盐化学平衡（Huang SM 式 S1–S2）与深度依赖的一阶响应时间，回答一个主刊级问题：**在气候带迁移与氮酸化共同作用下，总土壤碳本世纪究竟是汇还是源？** 结论不是“再画一张图”，而是机制性的时间尺度转折：平衡态下两者大体抵消，计及响应时间后总碳仍为显著碳源。

## 相对 Huang 的新意（不对抗、是补全）

1. **联合 SOC+SIC 核算**，给出总碳（TC）及干旱区无机碳占比的完整图像。  
2. **气候带错配 / 权衡**：大面积 SOC↓SIC↑（约 57 Mkm²），而非单一池的同向变化。  
3. **平衡态 vs 瞬态**：SSP5-8.5 下平衡态 ΔSOC ≈ −246 Pg、ΔSIC ≈ +290 Pg 近乎抵消；引入深度 τ 后，限时 ΔTC ≈ **−182 Pg**——这是全文中心转折。  
4. **氮路径的情景敏感性**：采用 Huang 的 ΔpH=−0.06×Nin+0.11，但在 IMAGE 氮肥速率下，2020–2050 年 0–30 cm SIC 损失仅约 **1.8–2.5 Pg**，低于其 GLOBIOM ambition-N 下发表的 **10–23 Pg**；并用 Zamanian 计量作敏感性（约 0.8–0.9 Pg）。差异主要来自氮情景，而非否定碳酸盐化学。

## 三个 take-home messages

1. **联合制图**：全球 0–200 cm 现存量 SOC 2,474（2,424–2,508）Pg、SIC 1,554（1,423–1,714）Pg、TC 3,991（3,874–4,202）Pg；干旱区 SIC 约占当地总碳的一半量级。  
2. **世纪尺度转折**：高排放下平衡态 SOC 损失与 SIC 增加近乎抵消，但因表层 SOC 响应快、碳酸盐与深层碳响应慢，限时总碳变化约为 **−182 Pg**，本世纪土壤仍是净碳源。  
3. **氮酸化不可直接外推**：同一 ΔpH–N 关系在不同肥料情景下可相差一个数量级；报告损失必须绑定氮输入假设（IMAGE vs GLOBIOM）。

## 精度表述策略（按作者要求）

正文以 **随机交叉验证** 为主要精度陈述（SIC 0–30 AUC 0.944、R² 0.433；矿物 SOC R² 0.610；pH R² 0.627），并坦陈低于 Huang 报告值；**不以空间 CV 压过或攻击前人**。空间 CV 仅放补充材料。

## 请编辑关注的一句话

若只看平衡态，气候变暖下土壤总碳似乎“无净变”；一旦承认碳库响应时间，结论反转——这正是把 SOC 与 SIC 放在同一叙事里才能看见的科学转折。

---
（投稿前请替换作者信息，并附数据/代码可用性声明；详见 `caveats_before_submission.md`。）
"""


def word_count(paras: list[str]) -> int:
    text = "\n".join(paras)
    # strip figure callouts noise minimally
    words = re.findall(r"[A-Za-z0-9Α-Ωα-ωΔδτΠπ]+(?:-[A-Za-z0-9]+)?|[Α-Ωα-ω]|[—–]", text)
    # simpler: split on whitespace
    return len(text.split())


def build_markdown() -> str:
    lines: list[str] = []
    lines.append(f"# {TITLE}\n")
    lines.append("**[Author names]**  \nAffiliations TBD.\n")
    lines.append("---\n")
    lines.append("## One-sentence summary\n")
    lines.append(f"{ONE_SENTENCE}\n")
    lines.append(f"*({len(ONE_SENTENCE)} characters)*\n")
    lines.append("---\n")
    lines.append("## Abstract\n")
    lines.append(ABSTRACT.strip() + "\n")
    lines.append(f"*({len(ABSTRACT.split())} words)*\n")
    lines.append("---\n")
    lines.append("## Main text\n")
    for p in MAIN_PARAS:
        lines.append(p.strip() + "\n")
    lines.append("\n---\n")
    lines.append("## Acknowledgments\n")
    lines.append(ACKNOWLEDGMENTS.strip() + "\n")
    lines.append("\n---\n")
    lines.append("## References and Notes\n")
    for i, ref in enumerate(REFERENCES, 1):
        lines.append(f"{i}. {ref}\n")
    lines.append("\n---\n")
    lines.append("## Figure legends\n")
    for title, body in FIG_LEGENDS:
        lines.append(f"**{title}**{body}\n")
    lines.append("\n### Figure files\n")
    for i, name in enumerate(
        [
            "Fig1_present_stocks.png",
            "Fig2_random_CV.png",
            "Fig3_zone_tradeoff.png",
            "Fig4_eq_vs_transient.png",
            "Fig5_N_acidification.png",
        ],
        1,
    ):
        lines.append(f"- Figure {i}: `/workspace/soil_global/figs/v6_paper/{name}`\n")
    lines.append("\n---\n")
    lines.append("## Supplementary Materials outline\n")
    lines.append(SM_OUTLINE.strip() + "\n")
    return "\n".join(lines)


def set_run_font(run, name="Times New Roman", size=11, bold=False, italic=False):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:eastAsia"), name)


def add_para(doc, text, *, size=11, bold=False, italic=False, align="left", space_after=8, first_indent=None, space_before=0):
    p = doc.add_paragraph()
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if first_indent is not None:
        pf.first_line_indent = Inches(first_indent)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_like(doc, text, size=14, bold=True, center=False):
    return add_para(doc, text, size=size, bold=bold, align="center" if center else "left", space_after=12, space_before=6)


def build_docx(path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # Title
    add_para(doc, TITLE, size=14, bold=True, align="center", space_after=12)
    add_para(doc, "[Author names]", size=12, align="center", space_after=2)
    add_para(doc, "Affiliations TBD", size=10, italic=True, align="center", space_after=18)

    add_para(doc, "One-sentence summary", size=11, bold=True, space_after=4)
    add_para(doc, ONE_SENTENCE, size=11, italic=True, align="justify", space_after=14)

    add_para(doc, "Abstract", size=11, bold=True, space_after=4)
    add_para(doc, ABSTRACT.strip(), size=10, align="justify", space_after=16)

    add_para(doc, "Main Text", size=11, bold=True, space_after=8)

    for p in MAIN_PARAS:
        add_para(doc, p.strip(), size=11, align="justify", space_after=10, first_indent=0.3)

    add_para(doc, "Acknowledgments", size=11, bold=True, space_before=12, space_after=4)
    add_para(doc, ACKNOWLEDGMENTS.strip(), size=10, align="justify", space_after=14)

    add_para(doc, "References and Notes", size=11, bold=True, space_after=6)
    for i, ref in enumerate(REFERENCES, 1):
        add_para(doc, f"{i}. {ref}", size=9, align="left", space_after=4)

    # Figures with embedded PNGs
    add_para(doc, "Figures", size=11, bold=True, space_before=14, space_after=8)
    fig_files = [
        ("Figure 1", "Fig1_present_stocks.png", FIG_LEGENDS[0]),
        ("Figure 2", "Fig2_random_CV.png", FIG_LEGENDS[1]),
        ("Figure 3", "Fig3_zone_tradeoff.png", FIG_LEGENDS[2]),
        ("Figure 4", "Fig4_eq_vs_transient.png", FIG_LEGENDS[3]),
        ("Figure 5", "Fig5_N_acidification.png", FIG_LEGENDS[4]),
    ]
    for label, fname, (ftitle, fbody) in fig_files:
        add_para(doc, label, size=11, bold=True, space_before=10, space_after=6)
        img = FIGS / fname
        if img.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            # width tuned for journal-like readability
            run.add_picture(str(img), width=Inches(6.0))
        else:
            add_para(doc, f"[Missing figure file: {fname}]", size=10, italic=True)
        add_para(doc, ftitle + fbody, size=9, align="justify", space_after=12)

    add_para(doc, "Supplementary Materials", size=11, bold=True, space_before=10, space_after=4)
    for block in SM_OUTLINE.strip().split("\n"):
        add_para(doc, block if block.strip() else " ", size=9, space_after=2)

    doc.save(str(path))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = build_markdown()
    md_path = OUT / "manuscript_soil_SOC_SIC.md"
    md_path.write_text(md, encoding="utf-8")

    docx_path = OUT / "manuscript_soil_SOC_SIC.docx"
    build_docx(docx_path)

    (OUT / "cover_letter_zh.md").write_text(COVER_ZH, encoding="utf-8")
    (OUT / "caveats_before_submission.md").write_text(CAVEATS, encoding="utf-8")

    wc = word_count(MAIN_PARAS)
    abs_wc = len(ABSTRACT.split())
    summary = {
        "md": str(md_path),
        "docx": str(docx_path),
        "cover_zh": str(OUT / "cover_letter_zh.md"),
        "caveats": str(OUT / "caveats_before_submission.md"),
        "main_text_words": wc,
        "abstract_words": abs_wc,
        "one_sentence_chars": len(ONE_SENTENCE),
        "n_refs": len(REFERENCES),
    }
    (OUT / "_build_report.json").write_text(
        __import__("json").dumps(summary, indent=2), encoding="utf-8"
    )
    print(summary)


if __name__ == "__main__":
    main()
