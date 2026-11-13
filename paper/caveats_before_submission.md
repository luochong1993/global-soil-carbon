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
