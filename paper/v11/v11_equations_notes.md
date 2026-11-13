# v11: equations added (native OMML)
Build: `python3 paper/v11/build.py` -> paper/manuscript_v11_Science.docx, paper/SM_v11_Science.docx
Equations: paper/v11/equations.py (LaTeX source, written from scripts/ code). Conversion: paper/v11/omml.py
(LaTeX -> OMML via pandoc [pip --user pypandoc_binary], cached in _omml_cache.json; post-processing merges
upright multi-letter names into one m:r run with m:nor so they render upright in Word and LibreOffice).
Render check: paper/v11/render_check/*.pdf (LibreOffice + libreoffice-math 25.2.3 installed on the box).
Text changes vs v10 (all else identical; tables, figures, citation numbers unchanged):
- old SM equation references renumbered (eq. S1->S11 hurdle, S2->S21/S22 stocks, S3->S29 TL, S4->S35 dpH, S5->S36 dSIC_N)
- MM "Driver attribution": logistic fit described as fitted to individual presence indicators (code: curve_fit on
  individual 0/1 data, scripts/42_v8_drivers.py), not to binned data
- MM "Driver attribution": group importance = mean |sum of SHAP within group| (code), not sum of mean |SHAP|
See final report for implementation caveats (CF median, SoilGrids covariates, CV covariates/weights, MEC/CCC, k_N).
