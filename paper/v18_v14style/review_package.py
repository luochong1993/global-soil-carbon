from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import pymupdf as fz
import json,hashlib,zipfile,re
from docx import Document
R=Path('/workspace/soil_global');F=R/'figs/v18_v14style_main';D=R/'paper/v18_v14style';Q=D/'panel_QA';Q.mkdir(exist_ok=True)
files=['Fig1_inventory','Fig2_associations','Fig3_equilibrium_geography','Fig4_kinetic_stock_change','Fig5_nitrogen','Fig6_organic_fractions']
# Native-resolution panel review crops, directly from final PDFs.
rects={1:[(15,20,300,210),(315,20,602,165),(15,210,300,389),(315,210,602,389),(15,393,300,574),(315,393,602,574)],2:[(14,10,300,218),(315,12,602,220),(15,235,300,420),(315,235,602,420),(15,446,164,642),(164,446,314,642),(314,446,464,642),(464,446,602,642)],3:[(15,20,300,214),(315,20,602,165),(15,218,300,406),(315,218,602,406),(15,426,356,674),(362,430,602,648)],4:[(16,20,214,216),(214,20,410,216),(410,20,602,216),(15,240,301,447),(314,240,602,447),(15,472,602,601)],5:[(15,8,300,189),(308,8,602,189),(15,200,300,389),(315,200,602,389),(15,405,602,550)],6:[(15,20,300,200),(315,20,602,200),(15,213,300,399),(315,213,602,399),(15,416,382,637),(394,425,602,630)]}
for i,name in enumerate(files,1):
 d=fz.open(F/(name+'.pdf'))
 for k,box in enumerate(rects[i]):d[0].get_pixmap(matrix=fz.Matrix(3.2,3.2),clip=fz.Rect(box),alpha=False).save(Q/f'Fig{i}_{chr(65+k)}.png')
 # Panel sheets at readable scale, each row two panels.
 ps=[Image.open(Q/f'Fig{i}_{chr(65+k)}.png').convert('RGB') for k in range(len(rects[i]))]
 W=1800;rh=750;sheet=Image.new('RGB',(W,rh*((len(ps)+1)//2)), 'white');draw=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',21)
 for k,im in enumerate(ps):
  im.thumbnail((870,710),Image.Resampling.LANCZOS);x=(k%2)*900+(900-im.width)//2;y=(k//2)*rh+30
  sheet.paste(im,(x,y));draw.text(((k%2)*900+12,(k//2)*rh+4),f'Fig. {i}{chr(65+k)} | final source-PDF panel',fill='black',font=font)
 sheet.save(Q/f'Fig{i}_panel_sheet.png')
# User contact sheet (preview only; scientific figure PNGs are never downsampled).
W=2000;CW=1000;RH=1200;preview=Image.new('RGB',(W,3*RH+70),'#ededed');draw=ImageDraw.Draw(preview);ff=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
draw.text((25,17),'v18  |  v14 visual style restored  |  six main figures',font=ff,fill='black')
for k,name in enumerate(files):
 im=Image.open(F/(name+'.png')).convert('RGB');im.thumbnail((966,1135),Image.Resampling.LANCZOS)
 x=(k%2)*CW+(CW-im.width)//2;y=70+(k//2)*RH+42
 draw.text(((k%2)*CW+22,70+(k//2)*RH+5),f'Fig. {k+1}',font=ff,fill='black');preview.paste(im,(x,y))
preview.save(R/'figs/v18_v14style_contact_sheet.png')
# Final file/embedding/DPI audit.
doc=Document(R/'paper/manuscript_v18_v14style_Science.docx');checks=[]
for k,(shape,name) in enumerate(zip(doc.inline_shapes,files),1):
 rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
 b=doc.part.related_parts[rid].blob;raw=(F/(name+'.png')).read_bytes();im=Image.open(F/(name+'.png'))
 checks.append({'figure':k,'embedded_image_matches':hashlib.sha256(b).hexdigest()==hashlib.sha256(raw).hexdigest(),'px':im.size,'dpi':im.info.get('dpi'),'panels':len(rects[k]),'pdf_font_count':len(fz.open(F/(name+'.pdf'))[0].get_fonts(full=True))})
assert all(q['embedded_image_matches'] for q in checks)
assert len(list(F.glob('*.pdf')))==len(list(F.glob('*.png')))==6
with zipfile.ZipFile(R/'paper/v18_v14style_main_figures.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(F.iterdir()):z.write(f,arcname='v18_v14style_main/'+f.name)
report={'source_v14_read_before_design':True,'v17_read_for_comparison':True,'full_page_QA':True,'panel_QA_files':str(Q),'figures':checks,'main_figure_count':6,'main_panel_count':sum(q['panels'] for q in checks),'unfinished':[],'upload_performed':False}
(D/'final_QA.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
