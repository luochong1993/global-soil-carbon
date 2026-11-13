from pathlib import Path
import fitz, json, re, math
from PIL import Image,ImageOps,ImageDraw
ROOT=Path('/workspace/soil_global/paper/v17_from_v14/render_check')
report={}
for label,fn in [('main','manuscript_v17_from_v14_Science.pdf'),('SM','SM_v17_from_v14_Science.pdf')]:
 d=fitz.open(ROOT/fn); thumbnails=[];issues=[];caps=[];figpages=[]
 for i,p in enumerate(d):
  text=p.get_text()
  if len(text.strip())<10:issues.append({'page':i+1,'issue':'blank_or_near_blank'})
  boxes=[b[:4] for b in p.get_text('blocks') if len(b)>4 and str(b[4]).strip()]
  for b in boxes:
   if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:issues.append({'page':i+1,'outside_text_bbox':b})
  for m in re.finditer(r'Fig\.\s+(S?\d+)\.',text):caps.append({'figure':m.group(1),'page':i+1})
  im=Image.frombytes('RGB',[p.get_pixmap(matrix=fitz.Matrix(.62,.62)).width,p.get_pixmap(matrix=fitz.Matrix(.62,.62)).height],p.get_pixmap(matrix=fitz.Matrix(.62,.62)).samples)
  im=ImageOps.contain(im,(390,515));tile=Image.new('RGB',(410,550),'#dddddd');tile.paste(im,((410-im.width)//2,25));ImageDraw.Draw(tile).text((12,7),f'{label} page {i+1}',fill='black');thumbnails.append(tile)
  if label=='main' and re.search(r'Fig\.\s+[1-6]\.',text):
   p.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(ROOT/f'main_page_{i+1:02d}.png');figpages.append(i+1)
 for start in range(0,len(thumbnails),12):
  sheet=Image.new('RGB',(1640,550*math.ceil(min(12,len(thumbnails)-start)/4)),'white')
  for k,im in enumerate(thumbnails[start:start+12]):sheet.paste(im,((k%4)*410,(k//4)*550))
  sheet.save(ROOT/f'{label}_contact_{start//12+1:02d}.jpg',quality=92)
 (ROOT/f'{label}_render_text.txt').write_text('\n\n'.join(p.get_text() for p in d))
 report[label]={'pages':len(d),'layout_issues':issues,'figure_captions':caps,'full_review_pages':figpages}
json.dump(report,open(ROOT/'render_qa.json','w'),indent=2)
print(json.dumps(report,indent=2))
