# Coupled trajectories of global soil organic and inorganic carbon under climate-zone shifts and nitrogen-driven acidification

**[Author names]**  
Affiliations TBD.

---

## One-sentence summary

Climate shifts make SIC gains cancel SOC losses at equilibrium, yet slower SIC response yields a century-scale net C source.

*(124 characters)*

---

## Abstract

Global assessments of soil carbon often treat organic (SOC) and inorganic (SIC) pools separately, obscuring how climate change and nitrogen inputs reshape total soil carbon. We map SOC and SIC jointly to 200 cm with digital soil mapping hybridized with carbonate equilibria and depth-dependent first-order response times, using WoSIS profiles, Beck Köppen zones, a six-GCM WorldClim CMIP6 ensemble, and ISIMIP nitrogen. Present stocks (0–200 cm) are 2,474 (2,424–2,508) Pg SOC and 1,554 (1,423–1,714) Pg SIC, totaling 3,991 (3,874–4,202) Pg C; arid soils hold roughly half of their carbon as SIC. Under SSP5-8.5 (2081–2100), equilibrium ΔSOC (−246 Pg) and ΔSIC (+290 Pg) nearly cancel, but with depth-specific response times the time-limited Δ total C is −182 (−266 to −119) Pg—a century-scale net source. Köppen zone shifts coincide with a large SOC↓SIC↑ trade-off (~57 Mkm²). Applying Huang and colleagues' ΔpH–N relation with IMAGE fertilizer rates yields 0–30 cm SIC losses of only 1.8–2.5 Pg (2020–2050), versus their published 10–23 Pg under GLOBIOM ambition-N scenarios; Zamanian stoichiometry gives ~0.8–0.9 Pg. Joint SOC–SIC accounting, equilibrium versus transient framing, and explicit N-scenario sensitivity redefine the near-term soil carbon response to climate and fertilization.

*(188 words)*

---

## Main text

Soil is the largest terrestrial carbon reservoir, yet global assessments still partition organic (SOC) and inorganic (SIC) carbon into largely separate ledgers (1–3). SOC dominates humid and high-latitude soils and responds to warming, moisture change, and land use on timescales of decades to centuries (6–8, 20, 22, 23). SIC concentrates in arid and semi-arid regions where solid carbonates persist under alkaline conditions governed by the CaCO₃–H₂O–CO₂ system (4, 5, 24). Dissolved inorganic carbon is a minor mass fraction but couples atmospheric and soil CO₂ to the dissolution or precipitation of solid carbonate. Treating the two solid pools independently therefore risks mis-signing the net response of total soil carbon (TC = SOC + SIC) when climate warming, hydrological change, and nitrogen (N) inputs act jointly across depths—and when the pools' characteristic response times differ by orders of magnitude.

Huang et al. (4) recently mapped global SIC and showed that nitrogen-driven acidification could dissolve tens of petagrams of topsoil carbonate this century, bringing inorganic carbon into the same policy conversation long occupied by SOC. Their analysis did not, however, couple SIC trajectories to concurrent SOC responses under identical climate forcing, nor did it distinguish equilibrium potential from time-limited change given the multi-centennial to millennial response times of deep carbonates and deep organic matter (6–8). Digital soil mapping products such as SoilGrids provide high-resolution SOC surfaces (2), and classical inventories constrain global totals (1), but a process-aware, depth-resolved joint projection of SOC and SIC under Shared Socioeconomic Pathways (SSPs) has been missing. Here we develop joint 0–200 cm maps of SOC and SIC, hybridize statistical predictions with carbonate equilibria and first-order kinetics, and ask three questions: (i) what are present coupled stocks and their depth structure; (ii) do climate-driven SIC gains offset SOC losses at equilibrium, and does that cancellation survive when response times are imposed; and (iii) how sensitive is the N-acidification pathway to the choice of fertilizer scenario relative to published Huang estimates.

Present stocks and complementary geography. Using a two-step hurdle model for SIC (presence classifier plus log-concentration regression with smearing retransformation), separate mineral- and organic-horizon models for SOC, equal-area spline depth harmonization (9, 10), and peat area constrained to PEATMAP (11), we estimate 0–200 cm stocks of 2,474 (90% bootstrap confidence interval 2,424–2,508) Pg SOC and 1,554 (1,423–1,714) Pg SIC, for a total of 3,991 (3,874–4,202) Pg C (Fig. 1). By depth, SOC declines from 960 (950–975) Pg in 0–30 cm to 788 (775–808) Pg in 30–100 cm and 719 (679–748) Pg in 100–200 cm. SIC increases over the same intervals: 177 (167–196), 594 (513–684), and 775 (707–848) Pg. Consequently, SIC exceeds SOC in the 100–200 cm layer. In arid climates, where solid carbonates dominate the fine-earth inorganic fraction, SIC approaches roughly half of local TC—an arid-zone inorganic share that global SOC-only ledgers omit (4, 12, 24). Our SOC totals sit close to Batjes' classical 0–200 cm range (1); 0–30 cm SOC exceeds a SoilGrids extract on the same mask, partly reflecting peat handling and profile selection. Our SIC is lower than Huang et al.'s 2,305 Pg to 200 cm (4). We attribute that gap primarily to differences in profile coverage and supplementation, explicit hurdle treatment of the large zero fraction (~81% of 0–30 cm SIC observations), and the covariate stack (lithology, climate, pH), rather than to a single algorithmic switch.

Spatial patterns are nearly complementary (Fig. 1, A to C). High SOC densities concentrate in boreal, tundra, and peatland domains and in parts of the humid tropics; high SIC densities occupy the arid belt from North Africa through the Middle East and Central Asia into western North America and interior Australia. Total carbon therefore remains substantial in both humid organic-rich and arid carbonate-rich regions—an integrated geography that is invisible when either pool is mapped alone. Aggregating 0–100 cm yields 1,758 (1,725–1,765) Pg SOC and 780 (681–866) Pg SIC, confirming that a large fraction of SIC, and a non-negligible fraction of SOC, lies below 1 m and must be retained in any TC budget intended for century-scale climate assessment.

Model evaluation. We report random five-fold cross-validation as the primary accuracy metric, matching the reporting convention used for SIC by Huang et al. (4) (Fig. 2). For 0–30 cm, SIC presence classification achieves an area under the receiver operating characteristic curve (AUC) of 0.944 and concentration regression R² of 0.433 (log-space R² = 0.489); mineral-horizon SOC R² = 0.610 (log-space 0.633); pH R² = 0.627; bulk density R² = 0.714. Organic-horizon presence classification reaches AUC ≈ 0.95. Deeper layers retain strong SIC classification (AUC 0.953 at 30–100 cm and 0.961 at 100–200 cm) with regression R² of 0.48 and 0.52, respectively; mineral SOC R² declines with depth (0.33 and 0.35), as expected when vertical information thins. These scores are lower than Huang et al.'s GradientBoosting SIC metrics (AUC 0.99, regression R² 0.79; their Table S3) (4). The gap is expected given our explicit zero hurdle, high zero fraction, and independent covariate stack; we do not claim superior predictive skill, and we do not elevate spatial block cross-validation as a lead claim against published random-CV benchmarks. Independent LUCAS SOC checks and depth-stratified residual diagnostics are summarized for the Supplementary Materials. Random CV remains the transparent comparator for readers placing this study next to Huang et al.

Climate futures: equilibrium cancellation versus transient source. Holding non-climate predictors fixed and substituting climate covariates from a six-member WorldClim CMIP6 ensemble (17, 18) yields space-for-time equilibrium maps for 2081–2100. Under SSP5-8.5, median equilibrium ΔSOC is −246 (−318 to −157) Pg and ΔSIC is +290 (+95 to +355) Pg; net equilibrium ΔTC is a near-zero +24 (−106 to +109) Pg (Fig. 4). Parallel near-cancellation appears under SSP1-2.6 (−119 SOC / +122 SIC; ΔTC ≈ −1 Pg), SSP2-4.5 (−185 / +189; ΔTC ≈ +5 Pg), and SSP3-7.0 (−226 / +252; ΔTC ≈ +9 Pg). Depth decomposition under SSP5-8.5 shows that equilibrium SOC loss is topsoil-dominated (−228 Pg in 0–30 cm; −59 Pg in 30–100 cm; a small gain of +40 Pg in 100–200 cm), whereas SIC gains concentrate below 30 cm (+39, +81, and +175 Pg in 0–30, 30–100, and 100–200 cm). The geography of change is coherent with aridification and warming: mid-latitude and dryland belts tend to lose SOC while gaining SIC, whereas high-latitude organic-rich domains lose SOC with little SIC compensation (Fig. 3, A and B).

Equilibrium maps, however, assume that soils fully re-equilibrate with the new climate within the projection horizon—an assumption that contradicts radiocarbon and inventory evidence for slow deep-soil turnover (6–8, 20). We therefore impose first-order kinetics with depth-dependent response times τ: 20–100 years (0–30 cm), 100–1,000 years (30–100 cm), and 500–3,000 years (100–200 cm) for SOC, and 1,000–10,000 years for SIC (6–8). Over a horizon t ≈ 85 years to the midpoint of 2081–2100, realized change is ΔC_transient = (1 − e^(−t/τ)) × ΔC_eq. With these assumptions, time-limited ΔSOC under SSP5-8.5 is −190 (−277 to −126) Pg, of which −177 Pg occurs in 0–30 cm alone, whereas time-limited ΔSIC shrinks to only +8 (−1 to +18) Pg. Net time-limited ΔTC is therefore −182 (−266 to −119) Pg (Fig. 4B)—a robust century-scale carbon source even though equilibrium TC is nearly neutral. The same qualitative gap between equilibrium cancellation and transient loss holds across SSPs: time-limited ΔTC of −67 (−149 to −34), −110 (−201 to −66), and −154 (−239 to −97) Pg under SSP1-2.6, 2-4.5, and 3-7.0. GCM spread in equilibrium SOC change under SSP5-8.5 remains substantial (central-run range about −238 to −175 Pg), but it does not restore a time-limited net sink once SIC's slow response is acknowledged.

The central implication is mechanistic rather than numerical. Surface SOC responds on decadal scales to temperature and moisture shifts; carbonate accumulation and deep SOC respond on centennial to millennial scales. Climate-driven SIC gains that appear large in equilibrium space-for-time maps therefore cannot offset SOC losses within the twenty-first century. Reporting only equilibrium TC—or only SOC—would miss this sign-relevant transient. Hybridizing digital soil mapping with elementary first-order kinetics is deliberately simpler than a full land-surface model; it is sufficient to show that the equilibrium cancellation is an asymptotic statement, not a forecast for 2100.

Köppen zone shifts and the SOC–SIC trade-off. Overlaying Beck et al. (13) Köppen-Geiger projections for 2071–2099 with our carbon change fields reveals a geographically coherent trade-off that extends well beyond pixels that change named climate class (Fig. 3). Under SSP5-8.5, about 19 Mkm² of ice-free land changes primary Köppen class (~15%); under SSP1-2.6, 2-4.5, and 3-7.0 the shifting area is ~7, 12, and 16 Mkm². Yet the area experiencing concurrent SOC loss and SIC gain is far larger—~57 Mkm² under SSP5-8.5—and remains ~53–58 Mkm² across all four SSPs (Fig. 3D). Co-loss and co-gain occupy smaller domains (~22 and ~32 Mkm² under SSP5-8.5). On shifting pixels alone, ΔSOC is −30 Pg and ΔSIC is +45 Pg under SSP5-8.5; globally, equilibrium carbon changes are −206 Pg SOC and +206 Pg SIC in the zone-shift diagnostic fields, underscoring near-cancellation at the planetary integral even as local signs diverge. The trade-off pattern dominates mid-latitude aridifying and warming belts across North America, Eurasia, and parts of the Southern Hemisphere, whereas high-latitude and some tropical domains lose both pools. Climate-zone mismatch therefore does not merely relocate carbon among biomes—it rewires the sign of the two pools in opposite directions over a continental-scale footprint. Assessments that track only SOC register a widespread loss; assessments that track only SIC register a widespread gain; only the joint map reveals the compensating geometry and its failure to cancel in time.

Nitrogen-driven acidification: scenario sensitivity. Solid carbonate persistence is tightly coupled to pH through the equilibria H₂O + CO₂(g) ↔ H₂CO₃ ↔ HCO₃⁻ + H⁺ and CaCO₃(s) + H⁺ ↔ HCO₃⁻ + Ca²⁺ (Huang supplementary equations S1–S2) (4). Empirically, the contribution of pH to predicted SIC follows a sigmoid with midpoints near 7.6–8.0 in both Huang et al.'s fits and ours, close to calcite equilibrium pH ≈ 8.2 under open-system conditions at present atmospheric CO₂ (Huang SM equation S7) (4). Acid inputs that depress pH through this sensitive window dissolve solid carbonate and can release CO₂ (5). We apply Huang et al.'s China-resurvey relation ΔpH = −0.06 × Nin + 0.11, where Nin is cumulative chemical N fertilizer in Mg N ha⁻¹ (4), and propagate ΔpH through a finite-difference of our trained SIC–pH response, scaled by cropland fraction. Parallel calculations substitute Huang's published SICpH sigmoid parameters and, separately, Zamanian stoichiometric coefficients that convert acidifying N directly to carbonate mass loss (5).

Using ISIMIP IMAGE N trajectories (19), cropland-mean Nin for 2020–2050 is only ~2.6–2.7 Mg N ha⁻¹ across SSP1-2.6, 3-7.0, and 5-8.5 (mean cropland ΔpH ≈ −0.045 to −0.052). Loss-only 0–30 cm SIC declines are 1.8, 2.4, and 2.5 Pg under these three SSPs—an order of magnitude below Huang et al.'s published topsoil losses of 10, 14, and 23 Pg under GLOBIOM High-, Medium-, and Low-Ambition-N scenarios for the same horizon (4) (Fig. 5A). Including deposition alongside fertilizer raises our 0–30 cm loss-only values only modestly (to ~2.1–2.9 Pg). Full-profile (0–200 cm) loss-only declines reach 14–18 Pg, with net changes—allowing alkalinization where Nin is low enough for the +0.11 intercept to dominate—of 7–12 Pg (Fig. 5B). A stoichiometric alternative following Zamanian et al. (5) yields central 0–30 cm losses of only ~0.8–0.9 Pg over 2020–2050 (coefficient 0.21; low/high bounds ~0.2–1.4 Pg). Extending IMAGE N to 2100 raises our Huang-formula 0–30 cm loss-only estimates to ~7.6–10.3 Pg—still below Huang's 2050 ambition-N headlines—and 0–200 cm loss-only totals to ~65–85 Pg.

The discrepancy is not primarily a disagreement about carbonate chemistry. IMAGE fertilizer totals for 2020–2050 imply modest cumulative Nin per cropland hectare, whereas GLOBIOM Low-Ambition-N embeds substantially higher mineral N inputs by design (4, 14). Deposition products also differ (ISIMIP versus CCMI). When we substitute Huang's published SICpH sigmoid parameters in place of our finite-difference response under the same IMAGE Nin, 0–30 cm losses remain in the ~1.0–1.5 Pg range—confirming that the N scenario, not the local slope of SIC versus pH, drives the gap between our results and the published 10–23 Pg range. The +0.11 intercept in the ΔpH relation further implies alkalinization wherever Nin < 1.83 Mg ha⁻¹; we therefore report both loss-only and net ΔSIC. We treat N-acidification as highly scenario-dependent and refrain from transferring Huang's multi-ten-petagram headline to IMAGE-based pathways. The scientifically durable statement is that N-driven SIC loss scales with cumulative acidifying inputs; the headline number does not travel across fertilizer futures without re-specification.

Implications. Three results follow for carbon accounting and mitigation. First, joint SOC–SIC maps show that arid and semi-arid soils store a large inorganic share of TC; omitting SIC understates dryland carbon and misplaces where total stocks are vulnerable. Second, climate-driven equilibrium cancellation between SOC loss and SIC gain emerges consistently across SSPs in our projections, but it is an asymptotic statement: with plausible response times, the twenty-first century remains a net soil carbon source of order 10² Pg under high emissions, concentrated in topsoil SOC. Third, N-acidification can dissolve meaningful SIC, yet published multi-ten-petagram topsoil losses are not transferable across fertilizer scenarios; IMAGE-based pathways imply low-single-digit petagram 0–30 cm losses to mid-century. For national inventories and land-based mitigation (3, 25), the practical message is to report SOC and SIC together, to separate equilibrium potential from time-limited commitment, and to condition acidification losses on explicit N pathways.

Limitations. Several limitations warrant explicit statement. Space-for-time equilibrium maps omit land-use change, irrigation chemistry, dust Ca²⁺ inputs, erosional carbonate redistribution, and rising atmospheric CO₂ effects on soil pCO₂ beyond what climate covariates mediate. Response times τ are literature-informed ranges rather than locally calibrated parameters; widening the τ envelope widens the transient uncertainty band but does not restore equilibrium cancellation within ~85 years under our central assumptions. Our SIC stock is lower than that of Huang et al. (4); until harmonized profile sets, shared zero-handling, and common masks are compared side by side, absolute SIC baselines remain unsettled even when directional climate and N sensitivities agree. The ΔpH–N relation is calibrated on Chinese resurveys and applied globally; regional buffering capacity, carbonate mineralogy (calcite versus dolomite), and non-carbonate acidity sinks are unresolved at the pixel scale. Bootstrap intervals capture profile resampling and some GCM spread but not full structural uncertainty in machine-learning architecture or in land-surface feedbacks. Organic carbon in peat is area-constrained to PEATMAP; alternative peat maps would shift high-latitude SOC. These caveats argue for presenting equilibrium and transient results side by side, for reporting N-driven SIC loss as a scenario-conditioned range, and for reading this study as a complement to Huang et al. on carbonate vulnerability rather than as a refutation of their chemistry.

Materials and methods summary. Observations and depth harmonization. Soil profiles were drawn from the ISRIC WoSIS snapshot (15), with additional QA/QC for units, depth logic, and property ranges. Horizon data were harmonized to 0–30, 30–100, and 100–200 cm by equal-area quadratic splines (mpspline, λ = 0.1) (9, 10) and by thickness-weighted aggregation where splines were unstable. Organic horizons were flagged at SOC > 120 g kg⁻¹; mapped organic presence probability was area-scaled so that organic extent matches PEATMAP (4.23 Mkm²) (11). Mineral-horizon SOC and bulk density models excluded organic samples. LUCAS topsoil observations (21) provided an independent SOC check. Coarse fragment corrections entered the stock equation explicitly.

Covariates and mapping. Predictive covariates included WorldClim climatologies (17), Beck Köppen-Geiger V3 zones (13), GLiM lithology (16), elevation and terrain derivatives, and related soil-forming factors assembled for digital soil mapping. SIC was modeled with a two-step hurdle: an XGBoost classifier for presence followed by log-concentration regression with smearing retransformation; soil pH entered as a covariate, enabling later finite-difference acidification experiments. SOC used separate mineral and organic models. pH and bulk density were mapped as supporting properties. Stocks were computed as concentration × bulk density × (1 − coarse fraction/100) × thickness (cm) × 0.1, with 90% bootstrap confidence intervals from profile resampling. Hybrid mechanistic context used Huang supplementary carbonate equilibria (S1–S2) and calcite equilibrium pH (S7) to interpret SICpH sigmoid midpoints near 7.6–8.0 (4).

Future climate, zone shifts, and nitrogen. Climate covariates for 2041–2060 and 2081–2100 were ensemble-averaged from six CMIP6 GCMs delivered through WorldClim (17, 18). Equilibrium ΔC applied future climate covariates in the trained models while holding other predictors at present values. Transient ΔC applied ΔC_eq × (1 − e^(−t/τ)) with depth-specific τ as above (t = 85 years to mid 2081–2100). Zone-shift analysis combined Beck present and 2071–2099 maps with carbon change fields to measure shifting area, SOC↓SIC↑ trade-off area, and carbon deltas on shifting versus all pixels. N acidification used ΔpH = −0.06 × Nin + 0.11 (4) with ISIMIP IMAGE cumulative chemical fertilizer per cropland hectare (and optionally deposition) (19), finite-difference SIC response to pH, and cropland-fraction scaling; Huang Table S9 sigmoid parameters and Zamanian stoichiometric coefficients (5) provided sensitivity bounds. Full protocols, covariate lists, GCM identifiers, cross-validation tables, and additional maps are outlined below for the Supplementary Materials.


*Main text word count: 2806*


---

## Acknowledgments

[Author names and contributions TBD.] We thank the ISRIC WoSIS and LUCAS data teams, the Beck Köppen-Geiger project, WorldClim and CMIP6 modeling groups, GLiM, PEATMAP, and ISIMIP for openly provided data products. [Funding agencies and grant numbers TBD.] All authors declare no competing interests. Data, trained models, and analysis code will be deposited in an open repository upon acceptance, with snapshot DOIs for input datasets.


---

## References and Notes

1. N. H. Batjes, Total carbon and nitrogen in the soils of the world. Eur. J. Soil Sci. 47, 151–163 (1996). doi:10.1111/j.1365-2389.1996.tb01386.x

2. T. Hengl et al., SoilGrids250m: Global gridded soil information based on machine learning. PLOS ONE 12, e0169748 (2017). doi:10.1371/journal.pone.0169748

3. P. Smith et al., How to measure, report and verify soil carbon change to realize the potential of soil carbon sequestration for atmospheric greenhouse gas removal. Glob. Change Biol. 26, 219–241 (2020). doi:10.1111/gcb.14815

4. Y. Huang et al., Size, distribution, and vulnerability of the global soil inorganic carbon. Science 384, 233–239 (2024). doi:10.1126/science.adi7918

5. K. Zamanian, K. Zarebanadkouki, Y. Kuzyakov, Nitrogen fertilization raises CO₂ efflux from inorganic carbon: A global assessment. Glob. Change Biol. 24, 2810–2817 (2018). doi:10.1111/gcb.14148

6. M. W. I. Schmidt et al., Persistence of soil organic matter as an ecosystem property. Nature 478, 49–56 (2011). doi:10.1038/nature10386

7. Z. Shi et al., The age distribution of global soil carbon inferred from radiocarbon measurements. Nat. Geosci. 13, 555–559 (2020). doi:10.1038/s41561-020-0596-z

8. Y. He et al., Radiocarbon constraints imply reduced carbon uptake by soils during the 21st century. Science 353, 1419–1424 (2016). doi:10.1126/science.aad4273

9. T. F. A. Bishop, A. B. McBratney, G. M. Laslett, Modelling soil attribute depth functions with equal-area quadratic smoothing splines. Geoderma 91, 27–45 (1999). doi:10.1016/S0016-7061(99)00003-8

10. B. P. Malone, A. B. McBratney, B. Minasny, G. M. Laslett, Mapping continuous depth functions of soil carbon storage and available water capacity. Geoderma 154, 138–152 (2009). doi:10.1016/j.geoderma.2009.10.007

11. J. Xu, P. J. Morris, J. Liu, J. Holden, PEATMAP: Refining estimates of global peatland distribution based on a meta-analysis. Catena 160, 134–140 (2018). doi:10.1016/j.catena.2017.09.010

12. R. Lal, Soil carbon sequestration impacts on global climate change and food security. Science 304, 1623–1627 (2004). doi:10.1126/science.1097396

13. H. E. Beck et al., High-resolution (1 km) Köppen-Geiger maps for the last 12,000 years and 2100 projections. Sci. Data 10, 724 (2023). doi:10.1038/s41597-023-02586-1

14. W. Winiwarter, L. Höglund-Isaksson, et al., Nitrogen management scenarios in the INMS/GLOBIOM framework as applied by Huang et al., Science 384, 233 (2024); see also International Nitrogen Management System documentation (https://www.inms.international/).

15. N. H. Batjes, E. Ribeiro, A. van Oostrum, Standardised soil profile data to support global mapping and modelling (WoSIS snapshot 2019). Earth Syst. Sci. Data 12, 299–320 (2020). doi:10.5194/essd-12-299-2020

16. J. Hartmann, N. Moosdorf, The new global lithological map database GLiM: A representation of rock properties at the Earth surface. Geochem. Geophys. Geosyst. 13, Q12004 (2012). doi:10.1029/2012GC004370

17. S. E. Fick, R. J. Hijmans, WorldClim 2: new 1-km spatial climate surfaces for global land areas. Int. J. Climatol. 37, 4302–4315 (2017). doi:10.1002/joc.5086

18. V. Eyring et al., Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization. Geosci. Model Dev. 9, 1937–1958 (2016). doi:10.5194/gmd-9-1937-2016

19. K. Frieler et al., Assessing the impacts of 1.5 °C global warming – simulation protocol of the Inter-Sectoral Impact Model Intercomparison Project (ISIMIP2b). Geosci. Model Dev. 10, 4321–4345 (2017). doi:10.5194/gmd-10-4321-2017

20. C. Poeplau et al., Temporal dynamics of soil organic carbon after land-use change in the temperate zone – carbon response functions as a model approach. Glob. Change Biol. 17, 2415–2427 (2011). doi:10.1111/j.1365-2486.2011.02408.x

21. G. Tóth, A. Jones, L. Montanarella, Eds., LUCAS Topsoil Survey: Methodology, Data and Results (Publications Office of the European Union, EUR 26102 EN, 2013). doi:10.2788/97942

22. T. W. Crowther et al., Quantifying global soil carbon losses in response to warming. Nature 540, 104–108 (2016). doi:10.1038/nature20150

23. E. A. Davidson, I. A. Janssens, Temperature sensitivity of soil carbon decomposition and feedbacks to climate change. Nature 440, 165–173 (2006). doi:10.1038/nature04514

24. K. Zamanian, Y. Kuzyakov, Contribution of soil inorganic carbon to atmospheric CO₂: More important than previously thought. Glob. Change Biol. 25, e1–e3 (2019). doi:10.1111/gcb.14463

25. P. Friedlingstein et al., Global Carbon Budget 2023. Earth Syst. Sci. Data 15, 5301–5369 (2023). doi:10.5194/essd-15-5301-2023


---

## Figure legends

**Fig. 1. Present global soil carbon stocks (0–200 cm).** (A) SOC density. (B) SIC density. (C) Total carbon (SOC + SIC). (D) Global totals by depth with 90% bootstrap confidence intervals; dashed line marks Huang et al. (4) SIC 0–200 cm (2,305 Pg). Units: Mg C ha⁻¹ (A–C) and Pg C (D).

**Fig. 2. Random five-fold cross-validation skill.** Primary metrics for 0–30, 30–100, and 100–200 cm: SIC presence AUC and concentration R², mineral SOC R², and pH R². Random CV is the lead accuracy claim; spatial block CV appears only in the Supplementary Materials.

**Fig. 3. Climate-zone shift and SOC–SIC trade-off under SSP5-8.5 equilibrium projections (0–200 cm).** (A) ΔSOC. (B) ΔSIC. (C) Response classes: SOC↓SIC↑ trade-off, both lose, both gain. (D) Area of Köppen zone shift and of SOC↓SIC↑ trade-off across SSPs (~57 Mkm² trade-off under mid-to-high forcing).

**Fig. 4. Equilibrium potential versus time-limited change (0–200 cm).** (A) ΔSOC and (B) Δ total C under SSP1-2.6, 2-4.5, 3-7.0, and 5-8.5 (2081–2100). Red: equilibrium space-for-time potential; blue: first-order transient with depth-dependent τ. Under SSP5-8.5, equilibrium ΔSOC (−246 Pg) and ΔSIC (+290 Pg) nearly cancel, yet time-limited ΔTC ≈ −182 Pg.

**Fig. 5. Nitrogen-acidification pathway comparison (2020–2050).** (A) 0–30 cm SIC loss: Huang et al. published GLOBIOM ambition-N values (10–23 Pg) versus our Huang-formula finite-difference and SICpH-sigmoid responses under IMAGE Nin (~1.8–2.5 Pg) and Zamanian stoichiometry (~0.8–0.9 Pg). (B) Full-profile (0–200 cm) loss-only and net ΔSIC using Huang ΔpH = −0.06×Nin+0.11 with IMAGE fertilizer.


### Figure files

- Figure 1: `figs/v6_paper/Fig1_present_stocks.png` (absolute: `/workspace/soil_global/figs/v6_paper/Fig1_present_stocks.png`)

- Figure 2: `figs/v6_paper/Fig2_random_CV.png` (absolute: `/workspace/soil_global/figs/v6_paper/Fig2_random_CV.png`)

- Figure 3: `figs/v6_paper/Fig3_zone_tradeoff.png` (absolute: `/workspace/soil_global/figs/v6_paper/Fig3_zone_tradeoff.png`)

- Figure 4: `figs/v6_paper/Fig4_eq_vs_transient.png` (absolute: `/workspace/soil_global/figs/v6_paper/Fig4_eq_vs_transient.png`)

- Figure 5: `figs/v6_paper/Fig5_N_acidification.png` (absolute: `/workspace/soil_global/figs/v6_paper/Fig5_N_acidification.png`)


---

## Supplementary Materials outline

Supplementary Materials (outline)

Materials and Methods (extended)
- Profile QA/QC, spline parameters (λ = 0.1), organic-horizon threshold (SOC > 120 g kg⁻¹), PEATMAP area scaling (4.23 Mkm²)
- Full covariate table (climate, lithology, topography, land cover, soil properties) with sources and resolutions
- Hurdle SIC model specification, smearing factor, XGBoost hyperparameters; SOC mineral vs organic models
- Bulk density and coarse-fragment treatment; stock equation; bootstrap design (90% CIs)
- Named list of six CMIP6 GCMs in the WorldClim ensemble; SSP definitions; time slices 2041–2060 and 2081–2100
- τ assumptions by depth with literature bounds; sensitivity to low/central/high τ envelopes
- Zone-shift algorithm (Beck V3 present vs 2071–2099) and trade-off classification rules
- N pathway: IMAGE rates, cropland mask, ΔpH formula, finite-difference SICpH, sigmoid parameters (ours vs Huang Table S9), Zamanian coefficients; IMAGE vs GLOBIOM Nin comparison table
- Carbonate equilibria context (Huang SM eqs S1–S2, S7)

Supplementary Text
- Comparison of SIC baselines with Huang et al. and earlier inventories (Batjes and others)
- Why random CV is primary; spatial CV results without claim inflation
- IMAGE vs GLOBIOM/INMS N scenarios: fertilizer totals and implications for the 1.8–2.5 vs 10–23 Pg contrast
- Equilibrium vs transient framing and limitations of space-for-time substitution
- Arid/semi-arid share of TC stored as SIC (exact percentages by Köppen class)

Figs. S1 to S_n (planned)
- Sample locations and depth coverage; organic vs mineral flags
- Covariate importance; SICpH sigmoid fits by depth
- Additional SSP maps (ΔSOC, ΔSIC, ΔTC) for 2041–2060 and 2081–2100
- Zone-shift maps for SSP1-2.6 / 2-4.5 / 3-7.0
- N ΔpH maps; cropland-scaled SIC response surfaces
- LUCAS SOC validation scatter; residual maps
- τ sensitivity fan charts for transient ΔTC

Tables S1 to S_n (planned)
- Stock totals by depth and climate zone (arid SIC share)
- Random CV full metrics; spatial CV appendix
- GCM-level equilibrium ΔC ranges
- N pathway numerical summary (all SSPs × horizons; loss-only vs net)
- Parameter tables for SICpH sigmoids (ours and Huang Table S9)
