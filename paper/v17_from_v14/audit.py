from pathlib import Path
from docx import Document
from PIL import Image
import json,re,hashlib,zipfile,runpy,collections
R=Path('/workspace/soil_global');O=R/'paper/v17_from_v14';qa={}
def paras(doc):return [p.text for p in doc.paragraphs]
def alltext(doc):return '\n'.join(n.text for n in doc.element.iter() if n.tag.endswith('}t') and n.text)
M=Document(R/'paper/manuscript_v17_from_v14_Science.docx');S=Document(R/'paper/SM_v17_from_v14_Science.docx')
mt=alltext(M);st=alltext(S)
qa['embedded_main_figures']=len(M.inline_shapes);qa['embedded_SI_figures']=len(S.inline_shapes)
qa['main_table_count']=len(M.tables);qa['SI_table_count_including_continuations']=len(S.tables)
qa['main_caption_numbers']=[int(re.match(r'Fig\. (\d+)\.',p).group(1)) for p in paras(M) if re.match(r'Fig\. (\d+)\.',p)]
qa['SI_caption_numbers']=[int(re.match(r'Fig\. S(\d+)\.',p).group(1)) for p in paras(S) if re.match(r'Fig\. S(\d+)\.',p)]
qa['table_caption_numbers_main']=[int(re.match(r'Table (\d+)\.',p).group(1)) for p in paras(M) if re.match(r'Table (\d+)\.',p)]
qa['table_caption_numbers_SI']=sorted(set(int(re.match(r'Table S(\d+)',p).group(1)) for p in paras(S) if re.match(r'Table S(\d+)',p)))
qa['unresolved_tokens']=[s for s in ['[n]','S{','[@'] if s in mt+'\n'+st]
qa['invalid_main_figure_refs']=sorted(set(int(x) for x in re.findall(r'\b(?:[Ff]ig\.|[Ff]igs\.)\s+(\d+)',mt+'\n'+st) if int(x)>6))
qa['invalid_main_table_refs']=sorted(set(int(x) for x in re.findall(r'\b[Tt]ables?\s+(\d+)',mt+'\n'+st) if int(x)>2))
qa['invalid_SI_refs']=sorted(set(int(x) for x in re.findall(r'\bS(\d+)\b',mt+'\n'+st) if int(x)>57))
# Dedicated figure/table reference groups including lists and ranges.
qa['missing_referenced_SI_figures']=[];qa['missing_referenced_SI_tables']=[]
for kind,lim in [('fig',29),('table',19)]:
 pat=(r'\b[Ff]igs?\.\s+S\d+[A-H]?(?:(?:,?\s*(?:and|to|–)\s+|,\s*)S?\d+[A-H]?)*' if kind=='fig' else r'\b[Tt]ables?\s+S\d+(?:(?:,?\s*(?:and|to|–)\s+|,\s*)S?\d+)*')
 for m in re.finditer(pat,mt+'\n'+st):
  for n in re.findall(r'\bS?(\d+)',m.group()):
   if int(n)>lim:qa['missing_referenced_SI_'+('figures' if kind=='fig' else 'tables')].append(m.group())
# Confirm actual embedded media bytes correspond to latest main PNGs.
mainfiles=runpy.run_path(str(O/'main_text.py'))['FIGFILES']
with zipfile.ZipFile(R/'paper/manuscript_v17_from_v14_Science.docx') as z:
 hashes={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
 qa['latest_main_images_embedded']=all(hashlib.sha256((R/'figs/v17_from_v14_main'/fn).read_bytes()).hexdigest() in hashes for fn in mainfiles.values())
qa['pngs']=[]
for dn in ['v17_from_v14_main','v17_from_v14_SI']:
 for p in sorted((R/'figs'/dn).glob('*.png')):
  im=Image.open(p);dpi=im.info.get('dpi');qa['pngs'].append({'file':str(p.relative_to(R)),'pixels':im.size,'dpi':dpi})
qa['all_output_pngs_600dpi']=all(x['dpi'] and min(x['dpi'])>=599 for x in qa['pngs'])
old=json.load(open(O/'v14_source_hashes.json'));qa['changed_v14_files']=[f for f,h in old.items() if hashlib.sha256((R/f).read_bytes()).hexdigest()!=h]
qa['preserved_v14_file_count']=len(old)
qa['retained_main_numeric_sentinels']={n:n in mt for n in ['4105','2506','1598','378','229','150','188','180','518','183','78','37','39','6.9','34']}
qa['forbidden_claims_present']=[x for x in ['soils become a net carbon source','soils are a net carbon source','central_sum','robust to τ for net','Sum of central values (net / loss-only N)'] if x in mt+'\n'+st]
# Same word-count implementation as build.py, main body includes headings, not abstracts/captions/methods.
V=runpy.run_path(str(O/'main_text.py'));V14=runpy.run_path(str(R/'paper/v14/main_text.py'))
def words(t):return len(re.sub(r'\*','',re.sub(r'\[((?:@[\w]+;?\s*)+)\]','',t)).split())
qa['word_counts']={'main_body_with_headings':sum(words(t) for _,t in V['MAIN']), 'v14_main_body_with_headings':sum(words(t) for _,t in V14['MAIN']), 'abstract':words(V['ABSTRACT']),'alternative_structured_abstract_not_in_Word':sum(words(t) for _,t in V['STRUCTURED']),'methods_summary_prose':sum(words(t) for t in V['METHODS_SUMMARY']),'legends':sum(words(a+' '+b) for a,b in V['LEGENDS'].values())}
qa['checks']={
 'six_main_figures':qa['main_caption_numbers']==list(range(1,7)) and qa['embedded_main_figures']==6,
 '29_SI_figures':qa['SI_caption_numbers']==list(range(1,30)) and qa['embedded_SI_figures']==29,
 'two_main_tables':qa['table_caption_numbers_main']==[1,2],
 '19_SI_tables':qa['table_caption_numbers_SI']==list(range(1,20)),
 'v14_unchanged':not qa['changed_v14_files'],
 'no_unresolved_ref_tokens':not qa['unresolved_tokens'],
 'references_in_bounds':not(qa['invalid_main_figure_refs'] or qa['invalid_main_table_refs'] or qa['missing_referenced_SI_figures'] or qa['missing_referenced_SI_tables']),
 'latest_main_images':qa['latest_main_images_embedded'],
 '600dpi_all_PNG':qa['all_output_pngs_600dpi'],
 'no_forbidden_joint_claims':not qa['forbidden_claims_present']}
# Verify final displayed first-citation sequence across main then SM, excluding caption labels.
xmlparas=[]
for doc in [M,S]:
 for pe in doc.element.body.iter():
  if pe.tag.endswith('}p'):
   text=''.join(x.text or '' for x in pe.iter() if x.tag.endswith('}t'))
   xmlparas.append(re.sub(r'^(?:Fig\. S?\d+\.|Table S?\d+\.)\s*','',text))
qa['first_citation_order']={}
for kind,pat in [('SI_fig',r'\b[Ff]igs?\.\s+S\d+[A-H]?(?:(?:,?\s*(?:and|to|–)\s+|,\s*)S?\d+[A-H]?)*'),('SI_table',r'\b[Tt]ables?\s+S\d+(?:(?:,?\s*(?:and|to|–)\s+|,\s*)S?\d+)*'),('main_fig',r'\b[Ff]igs?\.\s+(?!S)\d+[A-H]?(?:(?:,?\s*(?:and|to|–)\s+|,\s*)\d+[A-H]?)*'),('main_table',r'\b[Tt]ables?\s+(?!S)\d+')]:
 seen=[]
 for text in xmlparas:
  for match in re.finditer(pat,text):
   nums=[int(x) for x in re.findall(r'\bS?(\d+)',match.group())]
   if re.search(r'\bto\b|–',match.group()) and len(nums)==2:nums=list(range(nums[0],nums[1]+1))
   for n in nums:
    if n not in seen:seen.append(n)
 qa['first_citation_order'][kind]=seen
qa['checks']['first_citations_sequential']=all(v==list(range(1,n+1)) for k,n in [('SI_fig',29),('SI_table',19),('main_fig',6),('main_table',2)] for v in [qa['first_citation_order'][k]])
json.dump(qa,open(O/'qa_report.json','w'),indent=2,ensure_ascii=False)
for n,t in [('main',mt),('SM',st)]: (O/(n+'_final_text.txt')).write_text(t)
print(json.dumps({'checks':qa['checks'],'word_counts':qa['word_counts'],'bad_fig_refs':qa['invalid_main_figure_refs'],'bad_table_refs':qa['invalid_main_table_refs'],'bad_si_figs':qa['missing_referenced_SI_figures'],'bad_si_tabs':qa['missing_referenced_SI_tables']},indent=2,ensure_ascii=False))
