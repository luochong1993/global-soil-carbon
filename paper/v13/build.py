import json, re, sys
sys.path.insert(0,'/workspace/soil_global/paper/v13')
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
FM=R+'/figs/v13_main/'; FS=R+'/figs/v13_SI/'
S13=json.load(open(R+'/out/v13/summaries_v13.json')); PT13=json.load(open(R+'/out/v13/points_summary_v13.json'))

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
    add_runs(p,process_cites(caption_title),10.5,True); add_runs(p,' '+process_cites(caption_text),10.5)
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
para(doc,'Materials and Methods; Supplementary Text S1 to S6; Figs. S1 to S22; Tables S1 to S18; References ('+f'{n_main_refs+1}'+'–[n]).',10,cites=False)

doc.add_page_break()
exec(open('/workspace/soil_global/paper/v13/main_tables.py').read())
doc.add_page_break()
head(doc,'Figures and figure legends',13)
leg_words=0
for k in range(1,8):
    figure(doc,FM+M.FIGFILES[k])
    tt,tx=M.LEGENDS[k]; p=doc.add_paragraph(); p.paragraph_format.line_spacing=1.15
    add_runs(p,f'Fig. {k}. {tt} ',10,True); add_runs(p,process_cites(tx),10); leg_words+=words(tt+' '+tx)
    if k<7: doc.add_page_break()
# ensure ORDER updated by legends before writing refs? legends have no citations; fine.
doc.save(R+'/paper/manuscript_v13_Science.docx')
abs_words=words(M.ABSTRACT); sabs=sum(words(t) for _,t in M.STRUCTURED)

# ======================= SUPPLEMENTARY MATERIALS
sm=Document(); setup(sm)
para(sm,'Supplementary Materials for',14,bold=True,align='c',cites=False)
para(sm,M.TITLE,16,bold=True,align='c',cites=False)
para(sm,'[Author names] et al.',11,align='c',cites=False)
para(sm,'Corresponding author: [name, email]',10,italic=True,align='c',cites=False)
para(sm,'**This file includes:**',11,cites=False)
for x in ['Materials and Methods','Supplementary Text S1 to S6','Figs. S1 to S22','Tables S1 to S18','References']:
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
for i,(fn,tt,tx) in enumerate(S.FIGS+S.FIGS_V13, start=1):
    figure(sm,FS+fn, 6.5 if 'S10' not in fn else 6.8)
    p=sm.add_paragraph(); p.paragraph_format.line_spacing=1.15
    add_runs(p,f'Fig. S{i}. {tt} ',10,True); add_runs(p,process_cites(tx),10)
    sm.add_paragraph()

# ---- tables
sm.add_page_break(); head(sm,'Supplementary Tables',14)
q=P8['qc']
rows=[]
for code,name in [('phaq','pH (H₂O)'),('tceq','Carbonate (TCEQ)'),('orgc','Organic C'),('bdfiod','Bulk density'),('cfvo','Coarse fragments')]:
    rows.append([name,f"{q[code+'_layers_raw']:,}",f"{q[code+'_after_litter']:,}",f"{q[code+'_after_depth']:,}",f"{q[code+'_after_pre1970']:,} (−{q[code+'_pre1970_dropped']:,})",f"{q[code+'_after_valueQC']:,}",f"{q[code+'_dup_layers_dropped']:,}"])
table(sm,'Table S1.','Quality-control flow for WoSIS layers (number of layers retained after each step, following Huang et al. [@huang24]). Profiles: 226,821 before screening; 174,092 with at least one usable variable after screening, including 107,482 with 0–30 cm SOC, 99,199 with SIC, and 118,807 with pH. Huang et al. reported 223,593 SIC measurements from 55,077 profiles after their screening.',
      ['Variable','Raw','After litter/organic removal','After depth checks','After pre-1970 removal (dropped)','After value-range filter','Duplicates dropped'],rows)

cov=[['Climate','bio1–bio19','WorldClim 2.1 bioclimatic variables (temperature and precipitation means, extremes, seasonality)','10′; 30″ via interpolation','WorldClim 2.1 [@fick17]'],
     ['Climate','PET','Hargreaves potential evapotranspiration from monthly Tmin, Tmax, and extraterrestrial radiation','10′','[@hargreaves85]'],
     ['Climate','logAI','Humidity index ln(1 + P/PET)','10′','derived'],
     ['Topography','elev','Elevation','10′; native 30″ for 30″ maps','WorldClim 2.1'],
     ['Topography','slope, TPI','Slope (°) and topographic position index (elevation minus 5 × 5-cell mean)','10′','derived'],
     ['Soil','clay, sand, silt','Particle-size fractions (%); one map per property, used for all target layers (not depth-weighted); silt = 100 − clay − sand','aggregated to 10′','SoilGrids 2.0 [@poggio21]'],
     ['Soil','CEC','Cation exchange capacity (cmol kg⁻¹); used for all target layers','aggregated to 10′','SoilGrids 2.0'],
     ['Soil','pH_pred','Predicted pH (SIC models only)','10′','this study'],
     ['Parent material','GLiM, carbonate_rock, evaporite, unconsolidated','Lithology class code and binary indicators','0.5° → 10′ (nearest)','GLiM [@hartmann12]'],
     ['Sampling (f_MAOC only)','depth_mid, method','Sample depth midpoint; fractionation method (particle size, density)','—','[@georgiou22]'],
     ['Ancillary','Köppen–Geiger','Climate zones 1991–2020 and 2071–2099 (mask and zone-shift analysis)','1 km → 10′','[@beck23]'],
     ['Ancillary','PEATMAP','Peatland area constraint (4.23 Mkm²) for organic horizons','—','[@xu18]'],
     ['Ancillary','IMAGE N inputs','Fertilizer rates (five crops), crop fractions, N deposition (2015–2100)','0.5°','ISIMIP3b [@stehfest14;@lange19]']]
table(sm,'Table S2.','Environmental covariates and ancillary datasets. Models use 32 covariates (19 bioclimatic, PET, logAI, elev, slope, TPI, clay, sand, silt, CEC, and four GLiM terms), plus predicted pH for SIC (33). Huang et al. used about 60 covariates including vegetation, hydrology, salinity, and anthropogenic predictors (their table S2) [@huang24]; covariates in that set but absent here include NDVI/LAI, GPP/NPP, land cover, PDSI, TWI, water-table depth, electrical conductivity, and nitrogen deposition.',
      ['Category','Short name','Description','Resolution','Source'],cov,widths=[1.0,1.2,2.6,1.0,1.0])

cv=P10['CV_primary']; rows=[]
for d,lab in [('_0_30','0–30'),('_30_100','30–100'),('_100_200','100–200')]:
    c=cv[d]
    rows.append([lab,'pH','regression',f"{c['pH']['n']:,}",f"R² = {c['pH']['r2']:.3f}; RMSE = {c['pH']['rmse']:.2f}"])
    rows.append([lab,'SIC presence','classifier',f"{c['SIC_clf']['n']:,}",f"AUC = {c['SIC_clf']['AUC']:.3f}; F1 = {c['SIC_clf']['F1']:.3f}; precision = {c['SIC_clf']['precision']:.3f}; recall = {c['SIC_clf']['recall']:.3f}"])
    rows.append([lab,'SIC amount','hurdle regression',f"{c['SIC']['n']:,}",f"R² = {c['SIC']['r2']:.3f} (log scale {c['SIC']['r2_log']:.3f}); RMSE = {c['SIC']['rmse']:.2f} g kg⁻¹; smearing = {c['SIC']['smear']:.2f}"])
    rows.append([lab,'Mineral SOC','regression',f"{c['SOC_mineral']['n']:,}",f"R² = {c['SOC_mineral']['r2']:.3f} (log scale {c['SOC_mineral']['r2_log']:.3f}); RMSE = {c['SOC_mineral']['rmse']:.2f} g kg⁻¹"])
    rows.append([lab,'Organic horizon','classifier',f"{c['organic_clf']['n']:,}",f"AUC = {c['organic_clf']['AUC']:.3f}; F1 = {c['organic_clf']['F1']:.3f}; precision = {c['organic_clf']['precision']:.3f}; recall = {c['organic_clf']['recall']:.3f}"])
    rows.append([lab,'Bulk density','regression',f"{c['BD']['n']:,}",f"R² = {c['BD']['r2']:.3f}; RMSE = {c['BD']['rmse']:.3f} g cm⁻³"])
fc=P10['fractions_v8_cv']
rows.append(['0–100','f_MAOC','regression (logit)',f"{fc['n']:,}",f"R² = {fc['R2_fMAOC']:.3f} (5 × 10-fold {fc['R2_5x10_mean']:.2f} ± {fc['R2_5x10_sd']:.2f}); RMSE = {fc['RMSE_fMAOC']:.3f}; bias = +{fc['bias']:.3f}; MAOC concentration R² = {fc['MAOC_conc_R2']:.2f}"])
rows.append(['Huang et al.','SIC / pH','—','223,593 / 181,955','SIC classifier AUC = 0.99, F1 = 0.95; SIC regression R² = 0.79, RMSE = 6.17 g kg⁻¹; pH R² = 0.85'])
table(sm,'Table S3.','Random 10-fold cross-validation metrics of the final models (primary accuracy protocol, as in Huang et al. [@huang24]). R² and RMSE are on the original scale unless noted. SIC amount R² is the combined hurdle R² of out-of-fold expected SIC.',
      ['Depth (cm)','Target','Model','n','Metrics'],rows,widths=[0.8,1.0,1.0,0.8,3.2])

rows=[]
for d,lab in [('_0_30','0–30'),('_30_100','30–100'),('_100_200','100–200')]:
    c=cv[d]
    for key,name in [('pH','pH'),('SIC_clf','SIC presence'),('SIC','SIC amount'),('SOC_mineral','Mineral SOC'),('organic_clf','Organic horizon'),('BD','Bulk density')]:
        pp=c[key]['params'] if key!='SIC' else c[key]['params_amt']
        rows.append([lab,name,pp['n_estimators'],pp['max_depth'],pp['learning_rate'],pp['subsample'],pp['colsample_bytree'],pp['min_child_weight']])
for r2,pp in fc['grid']:
    rows.append(['f_MAOC',f'CV R² = {r2:.3f}',pp['n_estimators'],pp['max_depth'],pp['learning_rate'],pp['subsample'],pp['colsample_bytree'],pp['min_child_weight']])
table(sm,'Table S4.','Selected XGBoost hyperparameters by layer and target, and the five configurations compared for the f_MAOC model (ranked by random 10-fold R²; the first was retained).',
      ['Layer','Target','Trees','Max depth','Learning rate','Subsample','Col. subsample','Min child weight'],rows)

pr=P10['present']; s30=P8['stocks_30arcsec']; fr=P8['fractions']
rows=[]
for d,lab in [('_0_30','0–30'),('_30_100','30–100'),('_100_200','100–200')]:
    x=pr[d]
    soc=x['SOC']['mean']; sic=x['SIC']['mean']; tc=x['TC']['mean']
    smin=x['SOC_min_model_only']['mean']; sorg=x['SOC_org_model_only']['mean']
    rows.append([lab,f0(smin),f0(sorg),hstat(x['SOC']),hstat(x['SIC']),hstat(x['TC']),f"{sic/tc*100:.0f}"])
a=pr['_0_30'];b=pr['_30_100'];c_=pr['_100_200'];t=pr['_0_200']
rows.append(['0–100',f0(a['SOC_min_model_only']['mean']+b['SOC_min_model_only']['mean']),f0(a['SOC_org_model_only']['mean']+b['SOC_org_model_only']['mean']),
             f0(a['SOC']['mean']+b['SOC']['mean']),f0(a['SIC']['mean']+b['SIC']['mean']),
             f0(a['TC']['mean']+b['TC']['mean']),f"{(a['SIC']['mean']+b['SIC']['mean'])/(a['TC']['mean']+b['TC']['mean'])*100:.0f}"])
rows.append(['0–200',f0(a['SOC_min_model_only']['mean']+b['SOC_min_model_only']['mean']+c_['SOC_min_model_only']['mean']),
             f0(a['SOC_org_model_only']['mean']+b['SOC_org_model_only']['mean']+c_['SOC_org_model_only']['mean']),
             hstat(t['SOC']),hstat(t['SIC']),hstat(t['TC']),f"{t['SIC']['mean']/t['TC']['mean']*100:.0f}"])
ps=P8['present_stocks_Pg']
rows.append(['0–30 at 30″','—','—',f0(ps['0_30_30arcsec']['SOC']),f0(ps['0_30_30arcsec']['SIC']),f0(ps['0_30_30arcsec']['SOC']+ps['0_30_30arcsec']['SIC']),'—'])
rows.append(['30–100 at 30″ (provisional)','—','—',f0(s30['_30_100']['SOC_Pg']),f0(s30['_30_100']['SIC_Pg']),'—','—'])
rows.append(['100–200 at 30″ (provisional)','—','—',f0(s30['_100_200']['SOC_Pg']),f0(s30['_100_200']['SIC_Pg']),'—','—'])
table(sm,'Table S5.','Present-day soil carbon stocks (Pg C) on the 10′ analysis grid (mean with 90% CI and ±1 SD from fold-models × Monte Carlo), with 30″ integrals for comparison. Mineral/organic splits are fold-model means. Organic = organic horizons (peat), scaled to the PEATMAP area. Deep 30″ SOC integrals are inflated because organic-horizon probabilities were not nested at 30″ and are not used.',
      ['Layer (cm)','SOC mineral','SOC organic','SOC total','SIC','TC','SIC share (%)'],rows)
rows=[['0–30',hstat(pr['_0_30']['MAOC']),hstat(pr['_0_30']['POC']),f"{fr['_0_30']['fMAOC_areamean']:.2f}",f0(fr['Georgiou']['grid_sum_0_30'])],
      ['30–100',hstat(pr['_30_100']['MAOC']),hstat(pr['_30_100']['POC']),f"{fr['_30_100']['fMAOC_areamean']:.2f}",f0(fr['Georgiou']['grid_sum_30_100'])],
      ['0–100',hstat(pr['_0_100']['MAOC']),hstat(pr['_0_100']['POC']),'—',f"{f0(fr['Georgiou']['grid_sum_0_30']+fr['Georgiou']['grid_sum_30_100'])} (grid sum); 899 (published, non-permafrost)"],
      ['0–30 at 30″',f0(P8['frac30s']['MAOC_30s_0_30']),f"{f0(P8['frac30s']['POC_incl_organic_30s_0_30'])} (incl. organic horizons)",'—','—']]
table(sm,'Table S5 (continued).','MAOC and POC stocks in mineral soils (Pg C; 90% CI and ±1 SD) compared with Georgiou et al. [@georgiou22].',['Layer (cm)','MAOC','POC','Area-mean f_MAOC','Georgiou et al.'],rows)

rows=[['Schlesinger (1982)','SIC','Aridisols and arid Entisols','≥125 cm','780','Mean × area; 91 Arizona soils [@schlesinger82]'],
      ['Batjes (1996)','SIC','World','0–100 cm','695–748','FAO-UNESCO soil units; 4353 profiles [@batjes96]'],
      ['Lal et al. (1999)/Eswaran et al.','SIC','World','0–100 cm','940','Soil map × soil-climate map [@lal99]'],
      ['Plaza et al. (2018)','SIC','World','0–200 cm','1558','WISE30sec soil units [@plaza18]'],
      ['Huang et al. (2024)','SIC','World','0–200 cm','2305 ± 636 (±1 SD)','Digital soil mapping; 223,593 measurements [@huang24]'],
      ['This study','SIC','World','0–100 / 0–200 cm','780 / 1598 (1408–1801; ±119)','Digital soil mapping; WoSIS; 10′; MC CI'],
      ['Batjes (1996)','SOC','World','0–30 / 0–100 / 0–200 cm','684–724 / 1462–1548 / 2376–2456','FAO-UNESCO soil units [@batjes96]'],
      ['SoilGrids 2.0 (same land mask)','SOC','World','0–30 cm','658','Digital soil mapping, 250 m [@poggio21]'],
      ['This study','SOC','World','0–30 / 0–100 / 0–200 cm','848 (774–924; ±46) / 1666 / 2506 (2263–2761; ±151)','Includes organic horizons (361 Pg in 0–200 cm)'],
      ['Georgiou et al. (2022)','MAOC','Non-permafrost mineral soils / all cells','0–100 cm','899 / 1133','Published / gridded product summed here [@georgiou22]'],
      ['This study','MAOC','Mineral soils','0–100 cm','1048 (946–1152; ±62)','Fraction model × mineral SOC']]
table(sm,'Table S6.','Comparison with previous global estimates (Pg C), modeled on table S1 of Huang et al. [@huang24]. Independent validation of topsoil SOC against LUCAS 2018 (n = 15,378): as-reported (0–30 map vs 0–20 obs) mean bias = +28.6 Mg C ha⁻¹ (R² = −0.46); after depth harmonization, mean bias = +6.9 Mg C ha⁻¹ (R² ≈ 0.02). No global rescale applied.',
      ['Study','Pool','Domain','Depth','Estimate (Pg C)','Method / note'],rows,widths=[1.2,0.5,1.2,1.0,1.2,1.6])

orient(sm,True)
rows=[]
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    e=P10['future'][s_]['eq']; tl=P10['future'][s_]['time_limited']; ms=P10['future'][s_]['map_sums_equal_mean']
    rows.append([lab,hci(e['dSOC_0_200']),hci(e['dSIC_0_200']),hci(e['dTC_0_200']),
                 hci(tl['dSOC_0_200']),hci(tl['dSIC_0_200']),hci(tl['dTC_0_200']),hci(tl['dSOC_0_30']),
                 f"{f0(ms['dSOC_0_200'])} / +{f0(ms['dSIC_0_200'])} (map = headline mean)"])
table(sm,'Table S7.','Climate-driven change in soil carbon (Pg C, 0–200 cm unless noted) by 2081–2100. Ensemble: mean (5th to 95th percentile) across 10 final fold-models × six GCMs; time-limited (TL) values by 2100 include τ uncertainty. The last column repeats the ensemble-mean map integrals (equal to headline means; supplementary text S2).',
      ['Scenario','Eq. ΔSOC','Eq. ΔSIC','Eq. ΔTC','TL ΔSOC','TL ΔSIC','TL ΔTC','TL ΔSOC 0–30 cm','Map-sum ΔSOC / ΔSIC'],rows,font=8)

LAND=19.055656632226388/0.14915514369995175  # same Köppen land mask as v8
rows=[]
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    z=P10['future'][s_]['zone']; ms=P10['future'][s_]['map_sums_equal_mean']
    rows.append([lab,f"{z['land_shift_Mkm2']:.1f} ({z['land_shift_Mkm2']/LAND*100:.1f}%)",f"{z['tradeoff_SOC_loss_SIC_gain_Mkm2']:.1f}",
                 f"{z['dSOC_on_shift_Pg']:.1f}",f"+{z['dSIC_on_shift_Pg']:.1f}",f"{ms['dSOC_0_200']:.1f}",f"+{ms['dSIC_0_200']:.1f}"])
z5=P10['future']['585']['zone']
tq=100*z5['tradeoff_SOC_loss_SIC_gain_Mkm2']/LAND; bg=100*z5['both_gain_Mkm2']/LAND; bl=100*z5['both_loss_Mkm2']/LAND
sg=100*(LAND-z5['tradeoff_SOC_loss_SIC_gain_Mkm2']-z5['both_gain_Mkm2']-z5['both_loss_Mkm2'])/LAND
table(sm,'Table S8.','Köppen–Geiger zone shifts (2071–2099 versus 1991–2020; Beck et al. [@beck23]) and SOC–SIC trade-off areas, with ensemble-mean equilibrium carbon changes (0–200 cm, 2081–2100). Under SSP5-8.5, the land-area shares of the four ΔSOC/ΔSIC quadrants in Fig. 5A are: SOC loss with SIC gain, '+f"{tq:.0f}"+'%; both gain, '+f"{bg:.0f}"+'%; both loss, '+f"{bl:.0f}"+'%; SOC gain with SIC loss, '+f"{sg:.0f}"+'%.',
      ['Scenario','Shifted land, Mkm² (% of land)','Trade-off area (ΔSOC<0, ΔSIC>0), Mkm²','ΔSOC on shifted land (Pg)','ΔSIC on shifted land (Pg)','ΔSOC total (Pg)','ΔSIC total (Pg)'],rows)

rows=[]
# four SSPs from v10; N6 fert+dep / zamanian available for 126/370/585; 245 interpolated (no N6)
huang_pair={'126':(10,'High-Ambition-N'),'245':(14,'Medium-Ambition-N*'),'370':(14,'Medium-Ambition-N'),'585':(23,'Low-Ambition-N')}
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    n=P10['N']['scenarios'][s_]
    hv,hl=huang_pair[s_]
    nin=n['Nin_crop_mean']['mean']; dph=n['dph_crop_mean']['mean']
    loss30=abs(n['loss_0_30']['mean']); net30=n['net_0_30']['mean']; loss200=abs(n['loss_0_200']['mean'])
    if s_ in ('126','370','585'):
        fo=N6[f'ssp{s_}_2020_2050']['fert_only']; fd=N6[f'ssp{s_}_2020_2050']['fert_plus_dep']; zz=N6[f'ssp{s_}_2020_2050']['zamanian_stoichiometry']
        # fert+dep loss_only key may vary
        fd_loss = fd.get('loss_only_FD_0_30', fd.get('delta_our_FD_0_30'))
        if fd_loss is None: fd_loss = list(fd.get('delta_our_FD',{'_0_30':0}).values())[0] if False else fd.get('delta_our_FD',{}).get('_0_30', float('nan'))
        # Prefer explicit loss_only if present
        fd_loss = fd.get('loss_only_FD_0_30', abs(fd.get('delta_our_FD_0_30', fd.get('delta_our_FD',{}).get('_0_30',0))))
        zc=zz['central']['loss_0_30']; zl=zz['low']['loss_0_30']; zh=zz['high']['loss_0_30']
        p90=fo['Nin_p90']; fracneg=fo['dph_frac_negative']*100
        scale = hv/loss30
        rows.append([lab,f"{nin:.2f} ({p90:.1f})",f"{dph:.3f} ({fracneg:.0f}%)",f"{loss30:.2f}",f"{-abs(net30) if net30<0 else net30:.2f}",f"{abs(fd_loss):.2f}",f"{loss200:.1f}",f"{zc:.2f} ({zl:.2f}–{zh:.2f})",f"{hv} ({hl})",f"~{scale:.1f}×"])
    else:
        # SSP2-4.5: interpolated; no N6 fert+dep
        scale = hv/loss30
        rows.append([lab,f"{nin:.2f} (interp.)",f"{dph:.3f}",f"{loss30:.2f}",f"{net30:.2f}",'—',f"{loss200:.1f}",'—',f"{hv} ({hl})",f"~{scale:.1f}×"])
table(sm,'Table S9.','Nitrogen-driven SIC loss over 2020–2050 (Pg C) with ΔpH = −0.06 N_in + 0.11 and ISIMIP3b IMAGE fertilizer inputs (fold-model ensemble). N_in, mean cumulative cropland fertilizer input (Mg N ha⁻¹; 90th percentile in parentheses where available). Loss-only totals set cells with ΔSIC > 0 to zero; net totals include gains. SSP2-4.5 IMAGE fertilizer was interpolated as mean(SSP1-2.6, SSP3-7.0); GLOBIOM/INMS not obtained. Zamanian: stoichiometric 0.21 (0.055–0.32) kg C per kg N [@zamanian18] from the IMAGE fertilizer-only run. Scale factor: simple ratio of Huang et al. [@huang24] topsoil target to IMAGE loss-only (approximate). *Huang Medium-Ambition-N paired with interpolated SSP2-4.5.',
      ['IMAGE scenario','N_in','Mean cropland ΔpH (% cells negative)','Loss 0–30 (fert.)','Net 0–30 (fert.)','Loss 0–30 (fert. + dep.)','Loss 0–200 (fert.)','Zamanian 0–30','Huang et al. 0–30 (scenario)','Approx. scale'],rows,font=8)

orient(sm,False)
rows=[]
for s_,lab in [('126','SSP1-2.6'),('245','SSP2-4.5'),('370','SSP3-7.0'),('585','SSP5-8.5')]:
    e=P10['future'][s_]['eq']; tl=P10['future'][s_]['time_limited']
    rows.append([lab,hci(e['dMAOC']),hci(e['dPOC']),hci(tl['dMAOC']),hci(tl['dPOC']),
                 f"{tl['dMAOC']['mean']/e['dMAOC']['mean']*100:.0f}% / {tl['dPOC']['mean']/e['dPOC']['mean']*100:.0f}%"])
table(sm,'Table S10.','Change in topsoil (0–30 cm) MAOC and POC (Pg C) by 2081–2100 in mineral soils. Equilibrium and time-limited (TL) values: mean (5th to 95th) across 10 fold-models × 6 GCMs (TL includes τ log-uniform sampling). Baseline MAOC 518 (473–565; ±28) Pg, POC 183 (163–205; ±13) Pg.',
      ['Scenario','Eq. ΔMAOC','Eq. ΔPOC','TL ΔMAOC','TL ΔPOC','Realized share (MAOC / POC)'],rows)

sh=P8['drivers']['shap']; rows=[]
for k in ['pH','SIC presence','SIC amount','SOC (mineral)','fMAOC']:
    g=sh[k]['group_pct']; tf='; '.join(f"{n} ({v:.0f}%)" for n,v in sh[k]['top_features'][:5])
    rows.append([k.replace('fMAOC','f_MAOC'),f"{g['Climate']:.0f}",f"{g['Soil']:.0f}",f"{g['Topography']:.0f}",f"{g['Parent material']:.0f}",f"{g['Sampling']:.0f}",tf])
table(sm,'Table S11.','Driver attribution. Share of mean |SHAP| (%) by covariate group and top five covariates (topsoil models; 30,000 random land cells).',
      ['Component','Climate','Soil','Topography','Parent material','Sampling','Top covariates (% of mean |SHAP|)'],rows,widths=[1.0,0.55,0.5,0.6,0.6,0.6,2.8])
bp=P8['pdp_breakpoints']; import math
rows=[[k.replace('_vs_',' vs ').replace('_',' ').replace('fMAOC','f_MAOC'),(f"{v:.2f}"+(f" (P/PET ≈ {math.exp(v)-1:.2f})" if 'logAI' in k else '')) if not k.endswith('MAP') else f"{v:.0f} mm"] for k,v in bp.items()]
rows.append(['Observed logistic P(SIC>0.1) vs pH',f"pH₅₀ = {P8['pH_SIC_obs']['pH50']:.2f}; k = {P8['pH_SIC_obs']['k']:.2f}; n = {P8['pH_SIC_obs']['n']:,}"])
table(sm,'Table S11 (continued).','Breakpoints of two-segment piecewise-linear fits to partial dependence (logAI = ln(1 + P/PET); MAT in °C; clay and silt in %; CEC in cmol kg⁻¹) and the observed pH–SIC logistic fit.',['Relation','Breakpoint'],rows)
se=P8['drivers']['sem']; rows=[]
for tgt in ['pH','SIC','SOC']:
    for pr,v in se[tgt].items():
        if pr=='R2': continue
        rows.append([pr.replace('logAI','ln(P/PET)').replace('bio1','MAT').replace('carbonate_rock','carbonate rock'),tgt,f"{v:.3f}"])
    rows.append(['R²',tgt,f"{se[tgt]['R2']:.3f}"])
rows.append(['Indirect ln(P/PET) → pH → SIC','SIC',f"{se['indirect_AI_pH_SIC']:.3f}"]); rows.append(['Total ln(P/PET) → SIC','SIC',f"{se['total_AI_SIC']:.3f}"])
table(sm,'Table S11 (continued).',f"Standardized path coefficients (n = {se['n']:,} topsoil observations).",['Predictor','Response','β'],rows)

fl=P8['fractions']['flow']
rows=[['Raw records (Georgiou et al. synthesis)',fl['raw']],['With coordinates',fl['with_coords']],['With depth',fl['with_depth']],['f_MAOC in (0, 1]',fl['fM_in_(0,1]']],['POC measured (drop f_MAOC ≥ 0.995 or POC = 0)',fl['drop_fM>=0.995_or_POC=0 (unmeasured POM)']],['Mass-balance recovery 0.7–1.3',fl['mass_balance_0.7-1.3']],['Depth midpoint ≤ 100 cm',fl['mid<=100cm']],['With complete covariates (final)',fl['with_covariates']],
      ['  by source: synthesis / LUCAS / ISRAD',f"{fl['by_source']['Synthesis']} / {fl['by_source']['LUCAS']} / {fl['by_source']['ISRAD']}"],['  by method: particle size / density / combined (before covariate matching)',f"{fl['by_method']['Particle_Size']} / {fl['by_method']['Density']} / {fl['by_method']['Density_Particle_Size']}"],['  topsoil (midpoint ≤ 30 cm) / subsoil',f"{fl['topsoil_mid<=30']} / {fl['subsoil']}"]]
table(sm,'Table S12.','Selection of MAOC/POC fraction records [@georgiou22;@georgiou_data].',['Step','Records'],rows)

exec(open('/workspace/soil_global/paper/v13/si_tables.py').read())
refs_section(sm,start_idx=n_main_refs,title='References')
para(sm,f'References 1–{n_main_refs} are listed in the main text.',9,italic=True,cites=False)
sm.save(R+'/paper/SM_v13_Science.docx')

print(json.dumps(dict(n_main_eq=len(MAIN_NUM),n_sm_eq=len(SM_NUM),main_text_words=main_words,abstract_words=abs_words,structured_abstract_words=sabs,methods_summary_words=ms_words,legend_words=leg_words,n_main_refs=n_main_refs,n_total_refs=len(ORDER)),indent=1))
