import json,os,glob,re
src=open('/workspace/soil_global/scripts/40_v7_full_manuscript.py').read()
src=src.replace("FM='figs/v7_main'; FS='figs/v7_SI'","FM='figs/v8_main'; FS='figs/v8_SI'")
# remove v7 figure insert blocks
src=re.sub(r"\n(# Figure 2\n)?for f in sorted\(glob\.glob\(FM\+'/Fig\d\*\.png'\)\):\n  doc\.add_picture\(f,width=Inches\(6\.5\)\); caption\(doc,'[^\n]*'\)\n","\n",src)
src=src.replace("analysis version v7","analysis version v8")
src=src.replace("H(doc,'Discussion')","exec(open('/workspace/soil_global/scripts/47b_v8_sections.py').read())\nH(doc,'Discussion')")
src=src.replace("""H(doc,'Supplementary figures')
for f in sorted(glob.glob(FS+'/FigS*.png')):
  doc.add_picture(f,width=Inches(6.0)); caption(doc,os.path.basename(f))""","""H(doc,'Supplementary figures')
for f in sorted(glob.glob(FS+'/FigS*.png'),key=lambda x:int(re.findall(r'FigS(\\d+)',x)[0])):
  doc.add_picture(f,width=Inches(6.0)); caption(doc,SCAP.get(os.path.basename(f).split('_')[0],os.path.basename(f)))""")
src=src.replace("H(doc,'中文：相对 v6 的主要变更（给合作者）')","H(doc,'中文：v8 相对 v7 的主要变更')\nP_(doc,CN8)\nH(doc,'中文：v7 相对 v6 的主要变更（存档）')")
src=src.replace("manuscript_v7_Science","manuscript_v8_Science").replace("paper_numbers_v7.json',\'w\'","paper_numbers_v7.json','w'")
src=src.replace("P_(doc,abs1)","P_(doc,abs1)\n_F=json.load(open('/workspace/soil_global/out/v8/fractions_v8.json'))\nP_(doc,f\"v8 addition: Using {_F['cv']['n']} harmonized fraction measurements (random 10-fold CV R² = {_F['cv']['R2_fMAOC']:.2f}), mineral-associated organic carbon totals {_F['_0_30']['MAOC']+_F['_30_100']['MAOC']:.0f} Pg and particulate organic carbon {_F['_0_30']['POC']+_F['_30_100']['POC']:.0f} Pg in 0–100 cm mineral soils. Under SSP5-8.5, POC realizes most 21st-century topsoil losses whereas MAOC carries the larger committed equilibrium loss. SHAP attribution shows climate (aridity) dominating pH and mineral SOC, and soil properties (pH, texture) dominating SIC occurrence.\")",1)
src=src.split("# checkpoint paper_numbers")[0]
open('/workspace/soil_global/scripts/47_gen.py','w').write("import re\n"+src)
