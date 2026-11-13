"""LaTeX -> native Word OMML (via pandoc's LaTeX-math reader), cached, and helpers to insert
numbered display equations into python-docx documents."""
import json, os, zipfile, hashlib, copy
import pypandoc
from lxml import etree
from docx.shared import Pt, Inches
from docx.enum.text import WD_TAB_ALIGNMENT
M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
CACHE = os.path.join(os.path.dirname(__file__), '_omml_cache.json')
_cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def _key(tex): return hashlib.md5(tex.encode()).hexdigest()

def prefetch(texs):
    """Convert all uncached LaTeX strings in one pandoc call."""
    texs = [t.replace('\\bar{', '\\overline{') for t in texs]
    todo = [t for t in dict.fromkeys(texs) if _key(t) not in _cache]
    if not todo: return
    md = '\n\n'.join('$$' + t + '$$' for t in todo) + '\n'
    out = '/tmp/_omml_batch.docx'
    pypandoc.convert_text(md, 'docx', format='markdown', outputfile=out)
    root = etree.fromstring(zipfile.ZipFile(out).read('word/document.xml'))
    maths = root.findall('.//{%s}oMathPara' % M_NS)
    if len(maths) != len(todo):
        raise RuntimeError(f'pandoc returned {len(maths)} equations for {len(todo)} inputs')
    for t, mp in zip(todo, maths):
        om = mp.find('{%s}oMath' % M_NS)
        _cache[_key(t)] = etree.tostring(om).decode()
    json.dump(_cache, open(CACHE, 'w'))

def _m(tag): return '{%s}%s' % (M_NS, tag)
def _is_upright_word(r):
    rpr = r.find(_m('rPr')); t = r.find(_m('t'))
    if rpr is None or t is None or t.text is None: return False
    sty = rpr.find(_m('sty'))
    return sty is not None and sty.get(_m('val')) == 'p' and t.text.isalpha()
def postprocess(om):
    """(i) merge runs of upright letters produced by pandoc for \\mathrm{...} (S,I,C -> SIC) and mark them
    as normal text (m:nor) so that every OMML renderer shows them upright; (ii) widen \\quad/\\qquad spaces."""
    for parent in list(om.iter()):
        kids = list(parent)
        i = 0
        while i < len(kids):
            r = kids[i]
            if r.tag == _m('r') and _is_upright_word(r):
                j = i + 1
                while j < len(kids) and kids[j].tag == _m('r') and _is_upright_word(kids[j]):
                    r.find(_m('t')).text += kids[j].find(_m('t')).text; parent.remove(kids[j]); j += 1
                rpr = r.find(_m('rPr'))
                if rpr.find(_m('nor')) is None: rpr.insert(0, etree.Element(_m('nor')))
                kids = list(parent)
            i += 1
    for t in om.iter(_m('t')):
        if t.text and t.text.strip(' ') == '' and len(t.text) >= 1 and t.text != '\u200b':
            n = len(t.text)
            t.text = '\u2003' * n if n >= 2 else '\u2002'
    return om
def omath(tex):
    tex = tex.replace('\\bar{', '\\overline{')
    prefetch([tex])
    return postprocess(etree.fromstring(_cache[_key(tex)]))

def add_equation(doc, tex, label, text_width_in=6.5, size=11):
    """Display equation: centered native OMML, right-aligned number '(label)'."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4); pf.space_after = Pt(4); pf.line_spacing = 1.15
    pf.keep_with_next = True
    ts = pf.tab_stops
    ts.add_tab_stop(Inches(text_width_in / 2), WD_TAB_ALIGNMENT.CENTER)
    ts.add_tab_stop(Inches(text_width_in), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run('\t')
    p._p.append(omath(tex))
    r = p.add_run('\t(' + label + ')'); r.font.size = Pt(size)
    return p
