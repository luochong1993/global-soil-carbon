# v13 new SI tables S13-S18 (exec'd inside build.py namespace). Values from out/v13/summaries_v13.json (computed from out/v10).
def _sg(x,nd=0):
    v=round(x,nd); return ('−' if v<0 else '')+f'{abs(v):.{nd}f}'
def _ci(d,nd=0): return f"{_sg(d['mean'],nd)} ({_sg(d['p05'],nd)} to {_sg(d['p95'],nd)})"
def _ms(d,nd=0): return f"{_sg(d['mean'],nd)} ± {abs(d['sd']):.{nd}f}"
PRr=S13['present_regions']; FRr=S13['future_regions']; AR13=S13['area_Mkm2']
CN={'AS':'Asia','EU':'Europe','NA':'North America','SA':'South America','AF':'Africa','OC':'Oceania','Unassigned':'Unassigned coastal cells'}
