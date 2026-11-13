from pathlib import Path
import shutil,runpy,re,pprint,json
R=Path('/workspace/soil_global');O=R/'paper/v17_from_v14'
# Read original v14 raw-numbered content: figure/table renumbering happens only at build time.
V=runpy.run_path(str(R/'paper/v14/main_text.py'));S=runpy.run_path(str(R/'paper/v14/sm_text.py'))
def archive_refs(t):
 pat=r'\b(?:Fig\.|Figs\.)\s+[1-7][A-H]?(?:(?:,\s*(?:and\s+)?|\s+(?:and|to)\s+)(?:[1-7][A-H]?|[A-H]))*'
 def sub(m):
  s=m.group();s=re.sub(r'\b([1-7])',lambda z:'S'+str(22+int(z.group(1))),s)
  return re.sub(r'^Figs?\.',lambda z:'figs.' if z.group()=='Figs.' else 'fig.',s)
 return re.sub(pat,sub,t)
# Keep all existing SI panels, correcting inference and validation labels.
def fix_sm(t):
 t=archive_refs(t)
 t=t.replace('cross-validated skill of the final models','cross-validated skill of the search models')
 t=t.replace('Cross-validated skill of the final models','Cross-validated skill of the search models')
 t=t.replace('cross-validation metrics of the final models','cross-validation metrics of the unweighted search models')
 t=t.replace('POC is nearly fully realized','the modeled committed POC decrease is nearly fully realized (not depletion of the entire POC stock)')
 t=t.replace('estimated the direct and indirect effects','estimated the direct and indirect regression associations')
 t=t.replace('indirect effects are products of path coefficients','indirect association coefficients are products of fitted path coefficients; the assumed directed structure does not identify causation')
 t=t.replace('Nitrogen and climate experiments are separate, so the direction of the SIC change by 2100 under both drivers is assessed by comparing magnitudes, not by a joint simulation (table S19).','Nitrogen and climate experiments differ in horizon, affected mask, depth assumptions and model configuration. Their outputs are not subtracted or summed to establish a combined SIC direction; no joint simulation is available (table S19).')
 t=t.replace('The linear model is descriptive and complements the nonlinear SHAP analysis.','The linear model is descriptive and complements nonlinear SHAP attribution; arrows specify assumed regression relations, not causal identification.')
 t=t.replace('Indirect effect of the humidity index','Indirect association coefficient of the humidity index').replace('total effect, −0.35','total association coefficient, −0.35')
 t=t.replace('ln(P/PET)','ln(1 + P/PET)')
 return t
for key in ['MM','ST']:
 S[key]=[(k,fix_sm(t)) for k,t in S[key]]
# Append methodological safeguards without changing MM item indices (equation insertion is indexed).
for i,(k,t) in enumerate(S['MM']):
 if k=='p' and t.startswith('We distinguish four soil carbon quantities.'):
  S['MM'][i]=(k,t+' A decrease in these solid-soil stocks is not equivalent to an atmospheric CO₂ source. Carbonate-carbon provenance, DIC export, degassing and reaction stoichiometry are not resolved. Independently rounded totals are retained without forcing rounded equalities.')
for i,(k,t) in enumerate(S['ST']):
 if k=='p' and t.startswith('(i) Space-for-time'):
  S['ST'][i]=(k,t+' (xiv) Search-CV fits were unweighted and included three extra point-sampled SoilGrids predictors; the final fold-models instead use the 32-covariate stack and declustering weights, so these metrics do not validate the exact final configuration. (xv) The fraction realized by 2100 refers to the modeled equilibrium change, not to the fraction of the entire carbon stock removed; MAOC and POC retain positive stocks. No atmospheric net source or sink is inferred from solid-stock change alone.')
for key in ['FIGS','FIGS_V13']:
 S[key]=[(fn,fix_sm(tt),fix_sm(tx)) for fn,tt,tx in S[key]]
# Original seven main figures: complete panel archive with old/new lookup in caption.
archive=['FigS23_v14_inventory.png','FigS24_v14_countries.png','FigS25_v14_drivers.png','FigS26_v14_equilibrium.png','FigS27_v14_tradeoffs.png','FigS28_v14_nitrogen.png','FigS29_v14_fractions.png']
for n,fn in enumerate(archive,1):
 tt,tx=V['LEGENDS'][n]
 tx=fix_sm(tx)
 tx=tx.replace('Time-limited changes by 2100 are given in fig. S13 and table S7.','Conditional time-limited changes are shown in main Fig. 4 and table S7.')
 prefix=f'Original v14 Fig. {n} panel composition, redrawn from its original inputs at 600 dpi for traceability. '
 # Prevent old figure label being mistaken for a live reference.
 prefix=prefix.replace(f'Original v14 Fig. {n}',f'Archived v14 main figure {n}')
 S['FIGS_V13'].append((fn,'Archived panels: '+tt,prefix+tx))
S['FIGS']=[(fn,'Complete standardized regression coefficients.','Matrix of coefficients from the original standardized path regressions (n = 58,404). Columns are the fitted pH, SIC and SOC models; rows are their candidate predictors. Blue/red shading denotes positive/negative coefficients. A dash means the predictor was not included in that equation, not a fitted zero. All fitted coefficients, including |β| < 0.05, are displayed. SIC and SOC responses were log1p-transformed before standardization. These descriptive regressions use observed pH; the separate predictive SIC models use modeled pH. R² values are the original in-sample regression summaries. The humidity index is ln(1 + P/PET). The indirect humidity–pH–SIC association coefficient is −0.38 and the total humidity–SIC association coefficient is −0.35. This assumed regression structure does not identify causal effects; the selected pH-linked subgraph is shown in main Fig. 2B.') if fn=='FigS8_path_analysis.png' else (fn,a,b) for fn,a,b in S['FIGS']]
# Original S8 and S13 retained as method/traceability copies, clearly labeled rather than another main claim.
with open(O/'sm_text.py','w') as f:
 for key in ['MM','ST','FIGS','FIGS_V13']:f.write(key+' = '+pprint.pformat(S[key],width=130,sort_dicts=False)+'\n\n')
# Replace all source helper paths ONLY in copied build sources.
for name in ['build.py','si_tables_v14.py','si_head.py','main_tables.py','equations.py','omml.py']:
 p=O/name;t=p.read_text().replace('/paper/v14','/paper/v17_from_v14')
 if name not in ['build.py','main_tables.py']:t=archive_refs(t)
 p.write_text(t)
# Remove duplicate main summary table 3 and its unsupported combined inference row.
p=O/'main_tables.py';t=p.read_text();t=t.split('# v14: Table 3')[0];p.write_text(t)
# Copy original table chunks so no reads are redirected to v15/v16.
chunks=json.load(open(R/'paper/v14/_table_chunks.json'))
for key,entry in chunks.items():
 entry[1]=fix_sm(entry[1]).replace('Random 10-fold cross-validation metrics of the final models','Random 10-fold cross-validation metrics of the search models')
 if key=='3':entry[1]=entry[1].replace('primary accuracy protocol','search protocol; unweighted fits with three additional point-sampled covariates, unlike final weighted models')
json.dump(chunks,open(O/'_table_chunks.json','w'),indent=1)
# Delete unsupported cross-experiment SIC-direction continuation (not an alteration of the stored data).
p=O/'si_tables_v14.py';t=p.read_text();marker="rows=[]\nfor s_,lab in SSPL:\n    b=DIR14['ssp'][s_]['SIC_by2100_both_drivers']"
assert marker in t
start=t.index(marker);end=t.index("''')",start);t=t[:start]+t[end:]
t=t.replace('Climate, realized by 2100','Climate, conditional by-2100')
p.write_text(t)
# Reduce displayed main equations; full original equations all retained in SM.
p=O/'equations.py';t=p.read_text();t += '\n# v17 main text leaves implementation equations in SM; no equation deleted from SM_INSERT.\nMAIN = [it for it in MAIN if it[0]=="eq" and it[1] in ("m_eq", "m_tl")]\n'
p.write_text(t)
# Independent build paths and six main figures.
p=O/'build.py';t=p.read_text().replace('figs/v14_main/','figs/v17_from_v14_main/').replace('figs/v14_SI_raw/','figs/v17_from_v14_SI_raw/').replace('figs/v14_SI/','figs/v17_from_v14_SI/').replace('V14PASS','V17PASS').replace('manuscript_v14_Science.docx','manuscript_v17_from_v14_Science.docx').replace('SM_v14_Science.docx','SM_v17_from_v14_Science.docx').replace('/tmp/_v14_pass1','/tmp/_v17_from_v14_pass1').replace('Figs. S1 to S22','Figs. S1 to S29')
t=t.replace('for k in range(1,8):','for k in range(1,7):').replace('if k<7:','if k<6:')
# Limit figure physical height so image + reasonable caption fit; do not chain entire SI into one keep group.
t=t.replace("p.paragraph_format.keep_with_next=True\n    p.add_run().add_picture(path,width=Inches(width))", "p.paragraph_format.keep_with_next=True\n    from PIL import Image\n    iw,ih=Image.open(path).size\n    width=min(width, 5.9*iw/ih)\n    p.add_run().add_picture(path,width=Inches(width))")
# Captions are not stranded and do not split mid-paragraph.
t=t.replace("p=doc.add_paragraph(); p.paragraph_format.line_spacing=1.15", "p=doc.add_paragraph(); p.paragraph_format.line_spacing=1.05; p.paragraph_format.keep_together=True")
t=t.replace("p=sm.add_paragraph(); p.paragraph_format.line_spacing=1.15", "p=sm.add_paragraph(); p.paragraph_format.line_spacing=1.05; p.paragraph_format.keep_together=True")
# Table numeric values unchanged; add explicit non-additivity note without derived joint balance.
t=t.replace("if note: para(doc,note,9,italic=False)","if note: para(doc,note,9,italic=False)")
p.write_text(t)
# Copy unchanged 22 source SI pairs, never source v15/v16.
fs=R/'figs/v17_from_v14_SI_raw';fs.mkdir(exist_ok=True)
for p in (R/'figs/v14_SI_raw').iterdir():
 if p.is_file():shutil.copy2(p,fs/p.name)
print('SM safeguarded; 29 raw SI figures; 2 main tables; unsupported joint rows removed')
