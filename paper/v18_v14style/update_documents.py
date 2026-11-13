from pathlib import Path
import copy,re,json,hashlib,shutil
from docx import Document
from docx.shared import Inches,Pt
from docx.oxml.ns import qn
import pymupdf as fz
R=Path('/workspace/soil_global');P=R/'paper';F=R/'figs/v18_v14style_main';D=P/'v18_v14style'
files=['Fig1_inventory','Fig2_associations','Fig3_equilibrium_geography','Fig4_kinetic_stock_change','Fig5_nitrogen','Fig6_organic_fractions']
# Build the SI-only Georgiou comparison directly from original vector panel, not a screenshot.
src=fz.open(R/'figs/v14_main/Fig6_MAOC_POC.pdf');out=fz.open();pa=out.new_page(width=320,height=305)
pa.insert_text((15,20),'A',fontname='hebo',fontsize=11)
pa.show_pdf_page(fz.Rect(15,29,307,291),src,0,clip=fz.Rect(343,327,537,481),keep_proportion=True)
SI=R/'figs/v18_v14style_SI';SI.mkdir(exist_ok=True)
for f in (R/'figs/v17_from_v14_SI').iterdir():
 if f.is_file():shutil.copy2(f,SI/f.name)
sp=SI/'FigS22_Georgiou_validation.pdf';out.save(sp,garbage=4,deflate=True)
pm=pa.get_pixmap(matrix=fz.Matrix(600/72,600/72));pm.set_dpi(600,600);pm.save(SI/'FigS22_Georgiou_validation.png')
# Keep unneeded full archived figure outside active v18 SI to avoid duplicate S22 names.
for ext in ['png','pdf']:
 f=SI/('FigS22_v14_fractions.'+ext)
 if f.exists():f.unlink()

LEG={
1:('Present-day SOC and SIC stocks and depth partitioning.',
 '(A and B) Original v14 probability-density curves of SOC and SIC, respectively, for 0–30, 30–100 and 100–200 cm; dashed lines mark medians. The separate bar strip associated with A gives depth shares of the 0–200 cm total: SOC 34/33/34%, SIC 11/38/51%. (C and D) Topsoil SOC and SIC stocks (Mg C ha⁻¹); gutter bars give continent shares. (E and F) SOC and SIC stocks in 0–200 cm, with class-area proportions. Blue and purple palettes, Robinson maps and distributions are retained from v14; insets and color keys occupy dedicated space outside the map data. Grey, not mapped. Global stocks and uncertainty remain those in Table 1; independently rounded means need not add exactly. SIC/TC geography and national summaries remain in fig. S7.'),
2:('Descriptive associations and the proposed humidity–pH–SIC pathway.',
 '(A) Original v14 grouped TreeSHAP attribution (30,000 cells); numbers give percent contribution. (B) Selected pH-linked regression subgraph (n = 58,404), with the complete SOC-inclusive model in fig. S12 and coefficients in table S8. Blue/red denote positive/negative coefficients; the indirect coefficient product is −0.38. Arrows represent an assumed regression structure, not established causal links. (C and D) Dominant groups for SIC presence and mineral SOC, with land-area proportions in the gutters. (E and F) Original partial dependence of SIC presence on ln(1+P/PET) and predicted pH. (G and H) Partial dependence of fMAOC on clay and CEC. Dashed lines mark fitted breakpoints, labelled above the axes. The observed occurrence sigmoid (pH₅₀ = 7.10) remains in fig. S13 and is distinct from the model pH breakpoint (6.64). All panels describe associations, not causation.'),
3:('Equilibrium spatial change and SOC–SIC trade-offs.',
 '(A) Original v14 topsoil ΔSOC distributions under four SSPs; the separate strip gives area losing or gaining SOC. (B) ΔSOC and ΔSIC distributions in 0–200 cm under SSP5-8.5. (C and D) Equilibrium ΔSOC and ΔSIC maps (Mg C ha⁻¹), with class-area proportions in dedicated gutters. (E) Original v14 bivariate colors: pink SOC−/SIC+ (50% of mapped land), red co-loss (16%), dark blue joint gains (20%), teal SOC+/SIC− (13%). Matrix and area bars are below the map, separated by a gap. Denominator, 137.3 Mkm². Zero changes enter the non-positive class. (F) Continental changes from the same v14 ensemble totals. Future climate is 2081–2100 relative to 1970–2000; soil and terrain are fixed. Ensemble means use 10 fold-models × six GCMs. Sign classes are not cellwise significance tests; national scatter and scenario details remain in figs. S17 and S25.'),
4:('Assumed kinetics change the conditional stock balance.',
 '(A to C) SOC, SIC and TC changes in 0–200 cm across four SSPs: circles show equilibrium ensemble means; pale squares show by-2100 means; horizontal intervals are 90% CIs. (D and E) SSP5-8.5 stock-accounting waterfalls at equilibrium and by 2100, respectively; they are component budgets, not temporal trajectories. Signed labels retain independently rounded ensemble means: −378/+229/−150 Pg at equilibrium and −188/+7/−180 Pg by 2100. (F) The fraction of equilibrium SOC and SIC change realized by 2100 (50% and 3%). First-order response uses t = 85 years and assumed log-uniform τ ranges: SOC 20–100, 100–1000 and 500–3000 years by depth; SIC 1000–10,000 years. Timing is assumption-dependent, not validated by repeated observations. Stock change is not atmospheric CO₂ flux. Nitrogen and fraction projections are not included.'),
5:('Nitrogen-driven acidification as a separate experiment.',
 '(A) Original v14 cropland ΔpH distributions for 2020–2050, from ΔpH = −0.06 Nin + 0.11 with IMAGE inputs; dashed lines mark medians. Positive values reflect the fitted intercept. (B) Original v14 national loss-only ranking in 0–200 cm under SSP5-8.5 (Tg C), colored by continent. (C and D) Topsoil ΔSIC maps under SSP1-2.6 and SSP5-8.5 (Mg C ha⁻¹), with continent loss shares in gutters. Grey, not mapped. (E) Loss-only SIC decreases in 0–30 cm (dark) and 0–200 cm (pale), with 90% CIs across 10 fold-models. SSP2-4.5 fertilizer inputs are interpolated. The deeper estimate assumes topsoil ΔpH at every depth; it does not establish acidification propagation to 2 m. Net totals are in table S11. Climate and nitrogen differ in horizons, masks and assumptions and are not combined to infer a joint direction.'),
6:('Mineral-associated and particulate carbon: stocks and committed changes.',
 '(A) Original v14 MAOC/POC density curves by depth; dashed/dotted lines mark medians. (B) Topsoil MAOC and POC changes at equilibrium (dark) and by 2100 (pale), with existing 90% CIs including τ sampling for the latter. (C) MAOC fraction (%), with class-area proportions; (D) MAOC stock (Mg C ha⁻¹), with continent shares. (E) Original v14 stock bivariate map split at global medians: dark blue high/high, pink high-MAOC/low-POC, teal low-MAOC/high-POC, gold low/low; matrix and area shares are below the map. (F) Existing SSP5-8.5 committed decreases: MAOC 37 Pg by 2100 plus 41 Pg remaining; POC 39 Pg by 2100 with negligible remaining commitment. These are decreases, not exhaustion of the positive stocks. τ is assumed (MAOC 50–400; POC 5–30 years). Mineral soils only; this workflow is not directly additive with total SOC. Georgiou validation is retained only in fig. S22.')}

def reset(p,text,size=None):
 pr=copy.deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
 p.clear();r=p.add_run(text)
 if pr is not None:r._r.insert(0,pr)
 if size:r.font.size=Pt(size)

doc=Document(P/'manuscript_v17_from_v14_Science.docx')
changes={14:[('Fig. 1A','Fig. 1A, depth-share strip')],
15:[('Fig. 1, B–D','Fig. 1, C–F; fig. S7')],
17:[('Dominant-driver maps and the full partial-dependence set are retained in SI rather than repeating the attribution in several main panels (figs. S10 and S11).','Dominant-driver maps retain the spatial context (Fig. 2, C and D); selected partial dependences are shown in Fig. 2, E–H, with the full set in figs. S10 and S11.')],
19:[('Fig. 2, C and D; fig. S13','Fig. 2F; fig. S13'),('The weaker residual humidity dependence, SIC-amount curves and fraction-texture breakpoints remain in SI (figs. S10 and S14; table S8).','The weaker residual humidity dependence and fraction-texture breakpoints appear in Fig. 2, E, G and H; the complete curves remain in figs. S10 and S14 and table S8.')],
21:[('Fig. 3, A and B','Fig. 3, B–D')],
22:[('Fig. 3, C and D','Fig. 3E'),('Country scatter and continental bars are retained with the original spatial panels (fig. S17), avoiding a second main figure for the same divergence.','Continental totals summarize the same spatial divergence (Fig. 3F); country scatter remains in fig. S17, avoiding a second main figure for the same result.')],
29:[('Fig. 5B','Fig. 5E'),('national rankings are supporting information (fig. S20)','national rankings are shown in Fig. 5B and archived in fig. S20')],
32:[('Fig. 6, A and B','Fig. 6, A, C and D')],
33:[('Fig. 6, C and D','Fig. 6, B and F')]}
for i,pairs in changes.items():
 p=doc.paragraphs[i];text=p.text
 for a,b in pairs:
  assert a in text,(i,a);text=text.replace(a,b)
 reset(p,text)
# Embed high-resolution images and keep their aspect ratios.
for shape,name in zip(doc.inline_shapes,files):
 rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
 doc.part.related_parts[rid]._blob=(F/(name+'.png')).read_bytes()
 pdf=fz.open(F/(name+'.pdf'));rect=pdf[0].rect
 shape.width=Inches(6.5);shape.height=int(shape.width*rect.height/rect.width)
for p in doc.paragraphs:
 if p._p.xpath('.//w:drawing'):
  p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(3)
 if re.match(r'^Fig\. [1-6]\.',p.text):
  n=int(p.text[5]);title,body=LEG[n];p.clear();r=p.add_run(f'Fig. {n}. {title} ');r.bold=True;r.font.size=Pt(9)
  r=p.add_run(body);r.font.size=Pt(9);p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(0);p.paragraph_format.keep_together=True
outp=P/'manuscript_v18_v14style_Science.docx';doc.save(outp)
# SI: retain scientific corrections/numbering; replace only archived fraction composition with validation-only source panel.
sm=Document(P/'SM_v17_from_v14_Science.docx')
# S22 is the 22nd embedded SI figure in the unchanged S1–S29 order.
shape=sm.inline_shapes[21];rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
sm.part.related_parts[rid]._blob=(SI/'FigS22_Georgiou_validation.png').read_bytes();shape.width=Inches(4.7);shape.height=int(shape.width*305/320)
for p in sm.paragraphs:
 if p.text.startswith('Fig. S22.'):
  p.clear();rr=p.add_run('Fig. S22. Georgiou comparison retained as supplementary validation. ');rr.bold=True;rr.font.size=Pt(10)
  rr=p.add_run('Original v14 comparison of mineral-soil MAOC stocks in 0–30 and 30–100 cm for this study and the Georgiou gridded product. The dashed line marks the published non-permafrost estimate of 899 Pg C; masks and definitions differ, so this is methodological context, not an independent validation of all spatial predictions. The uncertainty bar is the original topsoil interval. The stock maps, density curves and stock-bivariate panel are restored to main Fig. 6 rather than repeated here. Only 34 fraction records below 30 cm constrain the subsoil estimates.');rr.bold=False;rr.font.size=Pt(10)
sm.core_properties.comments='v18: v14 visual style restored in six main figures. Scientific caveats and SI numbering retained from v17. No upload performed.'
sm.save(P/'SM_v18_v14style_Science.docx')
# Save editable caption source and a machine-readable image/caption audit.
(D/'legends_v18.json').write_text(json.dumps(LEG,ensure_ascii=False,indent=2))
audit={'main_figures':len(doc.inline_shapes),'SI_figures':len(sm.inline_shapes),'main_files':files,'source_numbers':'packaged original v14 ensemble_v10.json and fig_numbers_v14_45.json','unchanged_scientific_caveats':['association not causation','tau assumptions','stock change not atmospheric flux','N and climate not combined'],'main_docx':str(outp),'SM_docx':str(P/'SM_v18_v14style_Science.docx')}
(D/'document_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False,indent=2))
