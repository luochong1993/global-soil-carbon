import json, re, sys
sys.path.insert(0,'/workspace/soil_global/paper/v15')
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from refs import REFS
import main_text as M, sm_text as S
import equations as EQ, omml
# v11: equations (native OMML) ---------------------------------------------------


R='/workspace/soil_global'
P8=json.load(open(R+'/out/v8/paper_numbers_v8.json'))
P10=json.load(open(R+'/out/v10/paper_numbers_v10.json'))
N6=json.load(open(R+'/out/v6/N_huang_formula.json'))
FM=R+'/figs/v15_main/'; FS=R+'/figs/v15_SI_raw/'; FS14=R+'/figs/v15_SI/'
DIR14=json.load(open(R+'/out/v15/direction_v14.json'))
S13=json.load(open(R+'/out/v13/summaries_v13.json')); PT13=json.load(open(R+'/out/v13/points_summary_v13.json'))

# ---------------- v14: SI figure/table renumbering by first citation (two passes)
import os, shutil
PASS=int(os.environ.get('V15PASS','2')); ORDF=R+'/paper/v15/_si_order.json'
FIGMAP={}; TABMAP={}
if PASS==2:
    _o=json.load(open(ORDF)); FIGMAP={int(k):v for k,v in _o['fig'].items()}; TABMAP={int(k):v for k,v in _o['tab'].items()}
CITES=[]
KWRE=re.compile(r'\b(?P<kw>[Ff]igs?\.|[Tt]ables?)(?P<body>\s+S\d+[A-Z]?(?:,\s*[A-L](?:\s*(?:and|to)\s*[A-L])?(?![a-z])|,?\s*(?:and|to)\s+S\d+[A-Z]?|,\s*S\d+[A-Z]?)*)')
def _fmtlist(news):
    news=sorted(set(news)); runs=[]; i=0
    while i<len(news):
        j=i
        while j+1<len(news) and news[j+1]==news[j]+1: j+=1
        runs.append(f'S{news[i]} to S{news[j]}' if j-i>=2 else ', '.join(f'S{n}' for n in news[i:j+1])); i=j+1
    parts=', '.join(runs).split(', ')
    if len(parts)==1: return parts[0]
    if len(parts)==2: return parts[0]+' and '+parts[1]
    return ', '.join(parts[:-1])+', and '+parts[-1]
def renum(t, record=True):
    def rep(m):
        kind='F' if m.group('kw').lower().startswith('fig') else 'T'; mp=FIGMAP if kind=='F' else TABMAP
        body=m.group('body')
        simple=re.fullmatch(r'\s+S\d+(?:(?:,\s*|,?\s*and\s+|\s+to\s+)S\d+)*',body) is not None
        olds=[]
        for mm in re.finditer(r'S(\d+) to S(\d+)|S(\d+)',body):
            if mm.group(1): olds+=list(range(int(mm.group(1)),int(mm.group(2))+1))
            else: olds.append(int(mm.group(3)))
        if record: CITES.extend((kind,o) for o in olds)
        if simple and len(olds)>1:
            return m.group('kw')+' '+_fmtlist([mp.get(o,o) for o in olds])
        def r2(mm):
            if mm.group(1):
                return _fmtlist([mp.get(o,o) for o in range(int(mm.group(1)),int(mm.group(2))+1)])
            return f'S{mp.get(int(mm.group(3)),int(mm.group(3)))}'
        return m.group('kw')+re.sub(r'S(\d+) to S(\d+)|S(\d+)',r2,body)
    return KWRE.sub(rep,t)
def renum_title(t):
    return re.sub(r'^Table S(\d+)',lambda m:f'Table S{TABMAP.get(int(m.group(1)),int(m.group(1)))}',t)

# ---------------- citation handling
ORDER=[]
def cite_num(k):
    if k not in REFS: raise KeyError(k)
    if k not in ORDER: ORDER.append(k)
    return ORDER.index(k)+1
def compress(nums):
    nums=sorted(set(nums)); out=[]; i=0
    while i<len(nums):
        j=i
        while j+1<len(nums) and nums[j+1]==nums[j]+1: j+=1
        out.append(f'{nums[i]}' if j==i else (f'{nums[i]}, {nums[j]}' if j==i+1 else f'{nums[i]}–{nums[j]}')); i=j+1
    return ', '.join(out)
def process_cites(t):
    t=renum(t)
    def rep(m):
        keys=[k.strip().lstrip('@') for k in m.group(1).split(';')]
        return '('+compress([cite_num(k) for k in keys])+')'
    t=re.sub(r'\[((?:@[\w]+;?\s*)+)\]', rep, t)
    return t
# nested pattern like [WoSIS; (12)] fine.

SUB=re.compile(r'(?<![\w/.])([A-Za-zτΔ]+)_(\{[^}]+\}|[A-Za-z0-9]+)')
def add_runs(par, text, size=None, base_bold=False, base_italic=False):
    # tokens: **bold**, *italic*, subscripts X_Y
    parts=re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
    for p_ in parts:
        if not p_: continue
        b=base_bold; i=base_italic
        if p_.startswith('**'): p_=p_[2:-2]; b=True
        elif p_.startswith('*') and p_.endswith('*') and len(p_)>2: p_=p_[1:-1]; i=True
        pos=0
        for m in SUB.finditer(p_):
            if m.start()>pos: _r(par,p_[pos:m.start()],b,i,size)
            _r(par,m.group(1),b,i,size)
            sub=m.group(2).strip('{}'); rr=_r(par,sub,b,i,size); rr.font.subscript=True
            pos=m.end()
        if pos<len(p_): _r(par,p_[pos:],b,i,size)
def _r(par,t,b,i,size):
    r=par.add_run(t); r.bold=b; r.italic=i
    if size: r.font.size=Pt(size)
    return r

def setup(doc):
    st=doc.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman')
    pf=st.paragraph_format; pf.space_after=Pt(4); pf.line_spacing=1.5
    for s in doc.sections:
        s.left_margin=s.right_margin=Inches(1); s.top_margin=s.bottom_margin=Inches(1)
def para(doc,text,size=None,bold=False,italic=False,align=None,cites=True,indent=False,space_after=None):
    p=doc.add_paragraph()
    if align=='c': p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if indent: p.paragraph_format.first_line_indent=Inches(0.3)
    if space_after is not None: p.paragraph_format.space_after=Pt(space_after)
    add_runs(p, process_cites(text) if cites else text, size, bold, italic); return p
def head(doc,text,size=12,align=None,space_before=10):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(space_before); p.paragraph_format.keep_with_next=True
    if align=='c': p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    add_runs(p,text,size,True); return p
def figure(doc,path,width=6.5):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(path,width=Inches(width))
def shade(cell,hexcol):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hexcol); tcPr.append(sh)
def table(doc,caption_title,caption_text,header,rows,widths=None,font=8.5,note=None):
    p=doc.add_paragraph(); p.paragraph_format.keep_with_next=True; p.paragraph_format.space_before=Pt(10)
    add_runs(p,renum_title(caption_title),10.5,True); add_runs(p,' '+process_cites(caption_text),10.5)
    t=doc.add_table(rows=1,cols=len(header)); t.style='Table Grid'
    for j,h in enumerate(header):
        c=t.rows[0].cells[j]; c.text=''; pp=c.paragraphs[0]; add_runs(pp,h,font,True); shade(c,'E7E6E6')
    for r in rows:
        cells=t.add_row().cells
        for j,v in enumerate(r):
            cells[j].text=''; pp=cells[j].paragraphs[0]; pp.paragraph_format.line_spacing=1.0; pp.paragraph_format.space_after=Pt(0)
            add_runs(pp,process_cites(str(v)),font)
    for row in t.rows:
        for c in row.cells:
            for pp in c.paragraphs: pp.paragraph_format.line_spacing=1.0; pp.paragraph_format.space_after=Pt(0)
    tot=TABLE_W[0]
    if not widths:
        L=[max(len(str(h)),*(len(str(r[j])) for r in rows)) for j,h in enumerate(header)]
        L=[min(max(l,6),60)**0.8 for l in L]; widths=[tot*l/sum(L) for l in L]
    else:
        sc=tot/sum(widths); widths=[w*sc for w in widths]
    t.autofit=False
    grid=t._tbl.tblGrid
    for j,gc in enumerate(grid.findall(qn('w:gridCol'))): gc.set(qn('w:w'),str(int(widths[j]*1440)))
    for row in t.rows:
        for j,w in enumerate(widths): row.cells[j].width=Inches(w)
    if note: para(doc,note,9,italic=False)
    return t
TABLE_W=[6.5]
from docx.enum.section import WD_SECTION
def orient(doc,land):
    sec=doc.add_section(WD_SECTION.NEW_PAGE)
    w,h=sec.page_width,sec.page_height
    if land and w<h: sec.orientation=WD_ORIENT.LANDSCAPE; sec.page_width,sec.page_height=h,w
    if not land and w>h: sec.orientation=WD_ORIENT.PORTRAIT; sec.page_width,sec.page_height=h,w
    TABLE_W[0]=9.0 if land else 6.5
def f0(x): return f'{round(x):d}'
def f1(x): return f'{x:.1f}'
def ci(a,fmt=f0): return f'{fmt(a[0])} ({fmt(a[1])} to {fmt(a[2])})'
def hstat(d, signed=False):
    """Huang-style mean (p05–p95; ±sd) from a paper_numbers dict entry."""
    m, lo, hi, sd = d['mean'], d['p05'], d['p95'], d['sd']
    if signed or m < 0 or lo < 0:
        def s(x):
            return f'{round(x):+d}'.replace('+', '−' if False else '+') if False else (f'−{abs(round(x))}' if x < 0 else f'{round(x)}')
        # Science-style minus
        def s(x):
            return f'−{abs(round(x))}' if x < 0 else str(round(x))
        return f"{s(m)} ({s(lo)} to {s(hi)}; ±{round(abs(sd))})"
    return f"{round(m)} ({round(lo)}–{round(hi)}; ±{round(sd)})"
def hci(d):
    """mean (p05 to p95) for signed future changes."""
    def s(x):
        return f'−{abs(round(x))}' if x < 0 else str(round(x))
    return f"{s(d['mean'])} ({s(d['p05'])} to {s(d['p95'])})"
def refs_section(doc,start_idx=0,title='References and Notes'):
    head(doc,title)
    for n,k in enumerate(ORDER[start_idx:],start=start_idx+1):
        p=doc.add_paragraph(); p.paragraph_format.line_spacing=1.15; p.paragraph_format.space_after=Pt(2)
        p.paragraph_format.left_indent=Inches(0.3); p.paragraph_format.first_line_indent=Inches(-0.3)
        add_runs(p,f'{n}. '+REFS[k],9.5)

def words(t):
    t=re.sub(r'\[((?:@[\w]+;?\s*)+)\]','',t); t=re.sub(r'\*','',t); return len(t.split())


# ---------------- v11 equation helpers
MATHTOK=re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]+\}|\^\{[^}]+\}|_[A-Za-z0-9](?![A-Za-z0-9]))')
def add_math_text(par,text,size=None):
    """Like add_runs but subscripts/superscripts after any character: X_{ab}, X^{ab}, X_i."""
    for tok in MATHTOK.split(text):
        if not tok: continue
        if tok.startswith('**'): _r(par,tok[2:-2],True,False,size)
        elif tok.startswith('*') and len(tok)>2: _r(par,tok[1:-1],False,True,size)
        elif tok.startswith('_{'): _r(par,tok[2:-1],False,False,size).font.subscript=True
        elif tok.startswith('^{'): _r(par,tok[2:-1],False,False,size).font.superscript=True
        elif tok.startswith('_') and len(tok)==2: _r(par,tok[1],False,False,size).font.subscript=True
        else: _r(par,tok,False,False,size)
def eq_items(doc,items,numfmt,num,fill,indent_first=False):
    """Render ('eq',key,latex)/('w',text) items; returns words added."""
    w=0
    for it in items:
        if it[0]=='eq':
            omml.add_equation(doc,it[2],numfmt(num[it[1]]))
        else:
            p=doc.add_paragraph(); add_math_text(p,process_cites(fill(it[1]))); w+=words(it[1])
    return w


# ---- equation numbering (main: Eq. 1..; SM: S1.. in order of appearance)
MAIN_NUM={}; 
for it in EQ.MAIN:
    if it[0]=='eq': MAIN_NUM[it[1]]=len(MAIN_NUM)+1
SM_NUM={}
for idx in range(len(S.MM)):
    for it in EQ.SM_INSERT.get(idx,[]):
        if it[0]=='eq': SM_NUM[it[1]]=len(SM_NUM)+1
def sm_fill(t):
    t=t.replace('{NSM}',str(len(SM_NUM)))
    return re.sub(r'S\{(\w+)\}',lambda m:'S'+str(SM_NUM[m.group(1)]),t)
def sm_text_v11(t):
    for a,b in EQ.SM_TEXT_FIXES:
        if a in t: t=t.replace(a,b)
    t=re.sub(r'(?<!eqs\. )\beq\. S([1-5])\b',lambda m:EQ.SM_TEXT_REFS[m.group(1)],t)
    return sm_fill(t)
omml.prefetch([it[2] for it in EQ.MAIN if it[0]=='eq']+[it[2] for v in EQ.SM_INSERT.values() for it in v if it[0]=='eq'])

# ======================= MAIN MANUSCRIPT
doc=Document(); setup(doc)
para(doc,'Research Article — SOIL CARBON',10,bold=True,cites=False)
p=para(doc,M.TITLE,18,bold=True,cites=False)
para(doc,'[Author names]¹*, [Author names]², …',11,cites=False)
para(doc,'¹[Affiliation]. ²[Affiliation]. *Corresponding author. Email: [address]',9,italic=True,cites=False)
para(doc,'**One-sentence summary:** '+M.ONE_SENTENCE,10.5,cites=False)

head(doc,'Structured Abstract',13)
for h,t in M.STRUCTURED:
    p=doc.add_paragraph(); add_runs(p,h+': ',10.5,True); add_runs(p,process_cites(t),10.5)
head(doc,'Abstract',13)
para(doc,M.ABSTRACT)

head(doc,'Main Text',13)
main_words=0
for kind,t in M.MAIN:
    if kind=='h': head(doc,t,12); main_words+=len(t.split())
    else: para(doc,t,indent=True); main_words+=words(t)

head(doc,'Materials and methods summary',12)
ms_words=0
for t in M.METHODS_SUMMARY: para(doc,t,indent=True); ms_words+=words(t)
ms_words+=eq_items(doc,EQ.MAIN,lambda n:str(n),MAIN_NUM,sm_fill)
n_main_refs=None
refs_section(doc)
n_main_refs=len(ORDER)
head(doc,'Acknowledgments')
para(doc,M.ACK,10)
head(doc,'Supplementary Materials')
para(doc,'Materials and Methods; Supplementary Text S1 to S6; Figs. S1 to S26; Tables S1 to S19; References ('+f'{n_main_refs+1}'+'–[n]).',10,cites=False)

doc.add_page_break()
exec(open('/workspace/soil_global/paper/v15/main_tables.py').read())
doc.add_page_break()
head(doc,'Figures and figure legends',13)
leg_words=0
for k in range(1,7):
    figure(doc,FM+M.FIGFILES[k])
    tt,tx=M.LEGENDS[k]; p=doc.add_paragraph(); p.paragraph_format.line_spacing=1.15
    add_runs(p,f'Fig. {k}. {tt} ',10,True); add_runs(p,process_cites(tx),10); leg_words+=words(tt+' '+tx)
    if k<6: doc.add_page_break()
# ensure ORDER updated by legends before writing refs? legends have no citations; fine.
doc.save(R+'/paper/manuscript_v15_Science.docx' if PASS==2 else '/tmp/_v15_pass1_main.docx')
abs_words=words(M.ABSTRACT); sabs=sum(words(t) for _,t in M.STRUCTURED)

# ======================= SUPPLEMENTARY MATERIALS
sm=Document(); setup(sm)
para(sm,'Supplementary Materials for',14,bold=True,align='c',cites=False)
para(sm,M.TITLE,16,bold=True,align='c',cites=False)
para(sm,'[Author names] et al.',11,align='c',cites=False)
para(sm,'Corresponding author: [name, email]',10,italic=True,align='c',cites=False)
para(sm,'**This file includes:**',11,cites=False)
for x in ['Materials and Methods','Supplementary Text S1 to S6','Figs. S1 to S26','Tables S1 to S19','References']:
    para(sm,'    '+x,11,cites=False,space_after=0)
sm.add_page_break()
head(sm,'Materials and Methods',14)
eqn={}
for idx,(kind,t) in enumerate(S.MM):
    if kind=='h': head(sm,t+'.',11.5)
    else: para(sm,sm_text_v11(t),indent=True)
    eq_items(sm,EQ.SM_INSERT.get(idx,[]),lambda n:'S'+str(n),SM_NUM,sm_fill)
head(sm,'Supplementary Text',14)
for kind,t in S.ST:
    if kind=='h': head(sm,t,11.5)
    else: para(sm,sm_text_v11(t),indent=True)

# ---- figures
sm.add_page_break(); head(sm,'Supplementary Figures',14)
_ALLF=S.FIGS+S.FIGS_V13+getattr(S,"FIGS_V15",[])
if PASS==2:
    os.makedirs(FS14,exist_ok=True)
    for _f in os.listdir(FS14): os.remove(FS14+_f)
_FIGINV={FIGMAP.get(o,o):o for o in range(1,len(_ALLF)+1)}
for i in range(1,len(_ALLF)+1):
    fn,tt,tx=_ALLF[_FIGINV[i]-1]
    if PASS==2:
        stem=re.sub(r'^FigS\d+_','',fn[:-4])
        for ext in ('.png','.pdf'): shutil.copy(FS+fn[:-4]+ext, FS14+f'FigS{i}_{stem}{ext}')
        fpath=FS14+f'FigS{i}_{stem}.png'
    else: fpath=FS+fn
    figure(sm,fpath, 6.5 if 'S10_' not in fn else 6.8)
    p=sm.add_paragraph(); p.paragraph_format.line_spacing=1.15
    add_runs(p,f'Fig. S{i}. {tt} ',10,True); add_runs(p,process_cites(tx),10)
    sm.add_paragraph()

# ---- tables
sm.add_page_break(); head(sm,'Supplementary Tables',14)
exec(open('/workspace/soil_global/paper/v15/si_head.py').read())
exec(open('/workspace/soil_global/paper/v15/si_tables_v14.py').read())  # chunk overrides (S8, S9) and new S19
_cur_land=False
for _new in range(1,len(TCHUNK)+1):
    _old=TAB_INV[_new]; _land,_code=TCHUNK[_old]
    if _land!=_cur_land: orient(sm,_land); _cur_land=_land
    exec(_code)
if _cur_land: orient(sm,False)
refs_section(sm,start_idx=n_main_refs,title='References')
para(sm,f'References 1–{n_main_refs} are listed in the main text.',9,italic=True,cites=False)
sm.save(R+'/paper/SM_v15_Science.docx' if PASS==2 else '/tmp/_v15_pass1_sm.docx')
if PASS==1:
    fo=[];to=[]
    for k,o in CITES:
        L_=fo if k=='F' else to
        if o not in L_: L_.append(o)
    NF=len(S.FIGS)+len(S.FIGS_V13)+len(getattr(S,"FIGS_V15",[])); NT=len(TCHUNK)
    fo+=[o for o in range(1,NF+1) if o not in fo]; to+=[o for o in range(1,NT+1) if o not in to]
    json.dump(dict(fig={o:i+1 for i,o in enumerate(fo)},tab={o:i+1 for i,o in enumerate(to)},fig_first_order=fo,tab_first_order=to),open(ORDF,'w'),indent=1)
    print('PASS1 order fig',fo,'tab',to)

print(json.dumps(dict(n_main_eq=len(MAIN_NUM),n_sm_eq=len(SM_NUM),main_text_words=main_words,abstract_words=abs_words,structured_abstract_words=sabs,methods_summary_words=ms_words,legend_words=leg_words,n_main_refs=n_main_refs,n_total_refs=len(ORDER)),indent=1))
