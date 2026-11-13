#!/usr/bin/env python3
"""Restore v14 drawing objects, not v17 minimalist layouts. No fitting/new input data.
Source PDFs supply their exact vector curves, SHAP/PDP and embedded map pixels;
map land vectors + original pixels are rebuilt separately from the insets.
600-dpi PNGs are rendered from final vector PDF pages, never from screenshot crops.
"""
from pathlib import Path
import io,json,sys
import numpy as np
import pymupdf as fz
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
R=Path('/workspace/soil_global'); O=R/'figs/v18_v14style_main'; A=R/'paper/v18_v14style/assets'
O.mkdir(exist_ok=True); A.mkdir(parents=True,exist_ok=True)
SRC=R/'figs/v14_main'; NUM=R/'paper/packages/Global_Soil_Carbon_v14_package/numbers'
J=json.load(open(NUM/'out_v10/ensemble_v10.json'))
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':.55,'axes.spines.top':False,'axes.spines.right':False,'xtick.major.size':2.3,'ytick.major.size':2.3,'pdf.fonttype':42,'savefig.dpi':600,'legend.frameon':False})
SS=['126','245','370','585']; LL=['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']
SOC='#2171b5'; SIC='#6a51a3'; TC='#666666'; SC=['#1d3c8f','#69b3e0','#f39c4a','#c0262c']
BLUES=['#eff3ff','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#084594']
PURP=['#fcfbfd','#dadaeb','#bcbddc','#9e9ac8','#807dba','#6a51a3','#4a1486']
DIV=['#d7301f','#fc8d59','#fee08b','#c6dbef','#6baed6','#2171b5','#08306b']
BIV={(1,1):'#3b4994',(1,0):'#5ac8c8',(0,1):'#be64ac',(0,0):'#d7301f'}
MA_BIV={(1,1):'#3b4994',(1,0):'#be64ac',(0,1):'#5ac8c8',(0,0):'#d7a84a'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CACHE={}; OPEN=[]; AUDIT={}
def source(name):
 if name not in CACHE:CACHE[name]=fz.open(SRC/(name+'.pdf'))
 return CACHE[name]
def new(h=640):
 d=fz.open(); p=d.new_page(width=612,height=h);return d,p
def txt(p,x,y,s,size=8,bold=False,color=(0,0,0)):
 p.insert_text((x,y),s,fontsize=size,fontname='DVB' if bold else 'DV',fontfile=BOLD if bold else FONT,color=color)
def letter(p,x,y,s):txt(p,x,y,s,11,True)
def clip(p,rect,name,box):
 d=source(name) if isinstance(name,str) else name
 p.show_pdf_page(fz.Rect(rect),d,0,clip=fz.Rect(box),keep_proportion=True)
def snip(fig):
 b=io.BytesIO();fig.savefig(b,format='pdf',bbox_inches='tight',pad_inches=.045);plt.close(fig)
 d=fz.open(stream=b.getvalue(),filetype='pdf');OPEN.append(d);return d
def put(p,rect,d):p.show_pdf_page(fz.Rect(rect),d,0,keep_proportion=True)
def save(d,name,n):
 path=O/(name+'.pdf');d.save(path,garbage=4,deflate=True)
 p=d[0]; pix=p.get_pixmap(matrix=fz.Matrix(600/72,600/72),alpha=False);pix.set_dpi(600,600);pix.save(O/(name+'.png'))
 # full-page review and exact panel crops produced by review script later
 AUDIT[name]={'panels':n,'page_pt':list(p.rect),'png_px':[pix.width,pix.height],'dpi':600,'source':'v14 vector drawing objects / original embedded map rasters'}
 print('SAVED',name,flush=True)

def cleanmap(name,idx):
 key=(name,idx)
 if key in CACHE:return CACHE[key]
 sd=source(name);sp=sd[0];im=sp.get_images()[idx];xref,smask=im[:2];r=sp.get_image_rects(xref)[0]
 d=fz.open();p=d.new_page(width=r.width,height=r.height)
 # Rebuild original grey land vector paths (beneath the RGBA scientific map).
 for v in sp.get_drawings():
  if v['type']!='f' or not v['fill'] or max(abs(c-.89) for c in v['fill'])>.015:continue
  if not (r & v['rect']).is_empty and r.contains(v['rect']):
   sh=p.new_shape();off=fz.Point(r.x0,r.y0)
   for it in v['items']:
    if it[0]=='l':sh.draw_line(it[1]-off,it[2]-off)
    elif it[0]=='c':sh.draw_bezier(*[pt-off for pt in it[1:]])
    elif it[0]=='re':sh.draw_rect(it[1]-r.top_left)
    elif it[0]=='qu':sh.draw_quad(it[1])
   sh.finish(fill=v['fill'],color=None,closePath=v['closePath'],even_odd=v['even_odd']);sh.commit()
 pm=fz.Pixmap(sd,xref)
 if smask:pm=fz.Pixmap(pm,fz.Pixmap(sd,smask))
 p.insert_image(p.rect,stream=pm.tobytes('png'))
 CACHE[key]=d;OPEN.append(d);return d

def inset_rebuild(name,box):
 sp=source(name)[0];r=fz.Rect(box)
 bars=[v for v in sp.get_drawings() if v['fill'] and v['type'] in ('f','fs') and r.contains(v['rect']) and v['rect'].width>1 and v['rect'].height>.01 and max(v['fill'])>.12 and max(abs(c-1) for c in v['fill'])>.0001 and max(abs(c-.89) for c in v['fill'])>.015]
 bars.sort(key=lambda v:(v['rect'].x0,v['rect'].y1))
 if not bars:raise ValueError(('No vector bars',name,box))
 fig=plt.figure(figsize=(.78,1.0));ax=fig.add_axes([.37,.13,.53,.79])
 stack=max(v['rect'].x0 for v in bars)-min(v['rect'].x0 for v in bars)<1
 hh=np.array([v['rect'].height for v in bars]);vals=hh/hh.sum()*100
 if stack:
  bars.sort(key=lambda v:-v['rect'].y1);hh=np.array([v['rect'].height for v in bars]);vals=hh/hh.sum()*100
  cc={'AS':'#f07f4f','EU':'#fbb065','NA':'#fff6c0','SA':'#8fc1dc','AF':'#2f4c9a','OC':'#e79ae8'}
  bot=0
  for v,h in zip(bars,vals):
   ax.bar(0,h,bottom=bot,width=.58,color=v['fill'],edgecolor='white',lw=.25)
   if h>4:
    from matplotlib.colors import to_rgb
    lab=min(cc,key=lambda z:np.linalg.norm(np.array(to_rgb(cc[z]))-np.array(v['fill'])))
    ax.text(.38,bot+h/2,lab,va='center',fontsize=5.3)
   bot+=h
  ax.set(xlim=(-.55,1.1),ylim=(0,102),yticks=[0,50,100],xticks=[]);ax.set_ylabel('Share (%)',fontsize=5.8,labelpad=1)
 else:
  ax.bar(range(len(vals)),vals,color=[v['fill'] for v in bars],width=.8)
  ax.set(ylim=(0,max(vals)*1.18),xticks=[]);ax.set_ylabel('Proportion (%)',fontsize=5.6,labelpad=1)
 ax.tick_params(labelsize=5.5,length=1.5,pad=1)
 return snip(fig)

def proportions(name,ids,base,unit,cats,cols):
 ds=source(name)[0].get_drawings();fig,ax=plt.subplots(figsize=(1.60,.78));fig.subplots_adjust(left=.20,right=.97,bottom=.23,top=.80)
 n=len(cols);w=.80/n
 for k,c in enumerate(cols):
  vals=[ds[ids[k*2+j]]['rect'].height/unit for j in range(2)]
  ax.bar(np.arange(2)+(k-(n-1)/2)*w,vals,w,color=c)
 ax.set(xticks=[0,1],xticklabels=cats,ylim=(0,85 if len(cols)==4 else 58));ax.set_title('Proportion (%)',fontsize=6,pad=3);ax.tick_params(labelsize=5.5,length=1.5,pad=1)
 return snip(fig)

def classkey(cols,ticks,label,cats=False):
 fig=plt.figure(figsize=(3.1,.44));ax=fig.add_axes([.025,.55,.95,.28]);n=len(cols)
 for i,c in enumerate(cols):ax.add_patch(Rectangle((i,0),1,1,facecolor=c,edgecolor='none'))
 ax.set(xlim=(0,n),ylim=(0,1),yticks=[])
 ax.set_xticks(np.arange(n)+.5 if cats else np.arange(1,n));ax.set_xticklabels(ticks,fontsize=6)
 ax.tick_params(length=0,pad=1)
 for s in ax.spines.values():s.set_visible(False)
 ax.set_xlabel(label,fontsize=7,labelpad=3)
 return snip(fig)
def mappanel(p,rect,let,name,idx,cols,ticks,label,inset=None,cats=False):
 x,y,w,h=rect;letter(p,x+2,y+11,let)
 # Dedicated inset gutter: no scientific map is ever underneath a chart.
 gutter=51 if inset else 4
 mr=fz.Rect(x+gutter,y+15,x+w,y+h-40)
 md=cleanmap(name,idx);p.show_pdf_page(mr,md,0,keep_proportion=True)
 if inset:
  sr,box=inset
  put(p,(x-2,y+h-111,x+48,y+h-42),inset_rebuild(sr,box))
 key=classkey(cols,ticks,label,cats);put(p,(x+gutter-4,y+h-38,x+w,y+h),key)
 return mr

# Reuse exact existing vector density polylines + medians; calibrations are PDF axes,
# not fits or synthesized observations. Underlying curves formerly hidden by insets survive.
def density(name,ids,medids,cal,xlabel,labels,legend='upper left',size=(3.65,1.85),xlim=None):
 xzero,xscale,yzero,yscale,xlo,xhi,ytop=cal
 ds=source(name)[0].get_drawings();fig,ax=plt.subplots(figsize=size);fig.subplots_adjust(left=.16,right=.97,bottom=.25,top=.94)
 for k,i in enumerate(ids):
  v=ds[i];pts=[]
  for it in v['items']:
   if it[0]=='l':
    if not pts:pts.append(tuple(it[1]))
    pts.append(tuple(it[2]))
  pts=np.asarray(pts);xx=(pts[:,0]-xzero)/xscale;yy=(yzero-pts[:,1])/yscale
  ax.plot(xx,yy,c=v['color'],lw=1.15,label=labels[k],clip_on=True)
  if medids:
   mm=ds[medids[k]]['items'][0][1].x
   ax.axvline((mm-xzero)/xscale,c=v['color'],ls=':' if k>1 and name=='Fig6_MAOC_POC' else '--',lw=.7)
 ax.set(xlim=xlim or (xlo,xhi),ylim=(0,ytop),xlabel=xlabel,ylabel='Probability density')
 if legend=='above':ax.legend(ncol=2,loc='lower left',bbox_to_anchor=(0,1.01),fontsize=6.5,columnspacing=.7)
 else:ax.legend(loc=legend,fontsize=6.7,handlelength=1.6)
 return snip(fig)
C1A=(-22.487273,98.8851,97.847992,50.63644,.81,2.80,1.65)
C1B=(411.719879,34.59722,97.847992,155.8078,-2.74,2.95,.535)
C3A=(193.795425,1.728,120.743988,1509.2926,-80,40,.070)
C3B=(418.435425,.6912,120.743988,6920.068,-150,150,.0155)
C6A=(33.156553,96.95092,111.959991,58.62386,.215,2.355,1.65)

def fig1():
 d,p=new(604)
 letter(p,19,19,'A');letter(p,318,19,'B')
 da=density('Fig1_present_stocks',[14,16,18],[15,17,19],C1A,'log$_{10}$ SOC stock (Mg C ha$^{-1}$)',['0–30 cm','30–100 cm','100–200 cm'],size=(3.5,1.9))
 db=density('Fig1_present_stocks',[48,50,52],[49,51,53],C1B,'log$_{10}$ SIC stock (Mg C ha$^{-1}$)',['0–30 cm','30–100 cm','100–200 cm'],size=(3.5,1.9))
 put(p,(21,23,288,160),da);put(p,(320,23,598,160),db)
 # Depth shares in a separate strip, outside all probability curves.
 put(p,(190,155,294,207),proportions('Fig1_present_stocks',[23,24,25,26,27,28],52.941589,.606237,['SOC','SIC'],[SOC,SIC,'#e08214']))
 txt(p,32,181,'Depth share of 0–200 cm stock',7.5)
 txt(p,32,194,'SOC: 34 / 33 / 34%;  SIC: 11 / 38 / 51%',7)
 spec=[('C',0,BLUES,['20','40','60','80','120','200'],'SOC$_{0–30}$ (Mg C ha$^{-1}$)',('Fig1_present_stocks',(7,193,78,244))),('D',1,PURP,['1','5','10','20','40','80'],'SIC$_{0–30}$ (Mg C ha$^{-1}$)',('Fig1_present_stocks',(263,192,337,244))),('E',2,BLUES,['50','100','150','200','300','500'],'SOC$_{0–200}$ (Mg C ha$^{-1}$)',('Fig1_present_stocks',(7,359,78,407))),('F',3,PURP,['5','20','50','100','200','400'],'SIC$_{0–200}$ (Mg C ha$^{-1}$)',('Fig1_present_stocks',(266,359,338,407)))]
 for k,(let,idx,cols,ticks,lab,ins) in enumerate(spec):mappanel(p,(16+300*(k%2),212+181*(k//2),280,175),let,'Fig1_present_stocks',idx,cols,ticks,lab,ins)
 txt(p,22,596,'Grey: not mapped.  Insets: continent stock shares (C/D), class area shares (E/F).',6.8,color=(.35,.35,.35))
 save(d,'Fig1_inventory',6)

def pathway():
 fig,ax=plt.subplots(figsize=(3.9,2.2));ax.set(xlim=(0,1),ylim=(-.1,1.08));ax.axis('off')
 pos={'Humidity\nln(1+P/PET)':(.13,.91),'MAT':(.13,.65),'Clay':(.13,.38),'Carb. rock':(.13,.10),'pH\nR²=0.34':(.56,.52),'SIC\nR²=0.44':(.91,.52)}
 vals=[-.56,-.19,.20,.05];tg='pH\nR²=0.34'
 for k,(src,v) in enumerate(zip(list(pos)[:4],vals)):
  x,y=pos[src];u,z=pos[tg];c='#c0262c' if v<0 else SOC
  ax.annotate('',xy=(u-.07,z),xytext=(x+.10,y),arrowprops=dict(arrowstyle='->',color=c,lw=.55+abs(v)*3.0),zorder=1)
  yy=(y+z)/2+([.06,.035,-.025,-.055][k])
  ax.text(.36,yy,f'{v:.2f}',color=c,fontsize=8,ha='center',bbox=dict(fc='white',ec='none',pad=.5),zorder=3)
 ax.annotate('',xy=(.84,.52),xytext=(.65,.52),arrowprops=dict(arrowstyle='->',color=SOC,lw=2.5),zorder=1)
 ax.text(.745,.60,'0.67',ha='center',color=SOC,fontsize=8)
 for s,(x,y) in pos.items():ax.text(x,y,s,ha='center',va='center',fontsize=8,zorder=10,bbox=dict(boxstyle='round,pad=.28',fc='#f8f8f8',ec='.5',lw=.5))
 ax.text(.51,-.07,'n = 58,404; indirect association = −0.38',fontsize=7,ha='center')
 return snip(fig)
def pdp_row():
 ds=source('Fig7_drivers')[0].get_drawings();fig,axs=plt.subplots(1,4,figsize=(8.15,2.08));fig.subplots_adjust(left=.06,right=.995,bottom=.24,top=.88,wspace=.60)
 pars=[(455,60.236465,68.464294,435.726684,2726.614,.30,56.656624,149.968628,360.843994,446.379974,.56,'ln(1+P/PET)','P(SIC>0.1)'),(468,89.115428,21.64205,443.204224,82.0299,0,181.072632,274.384614,360.843994,446.379974,6.64,'predicted pH','P(SIC>0.1)'),(482,286.85986,2.599904,431.772583,1481.749,.69,305.488616,398.800628,360.843994,446.379974,22,'clay (%)','f$_{MAOC}$'),(494,417.52179,2.0609375,445.45166,1951.321,.69,429.904633,523.216614,360.843994,446.379974,25,'CEC (cmol kg$^{-1}$)','f$_{MAOC}$')]
 for ax,par in zip(axs,pars):
  idx,xz,xs,yz,ys,yb,xl,xr,yt,ybot,bp,xlab,ylab=par;v=ds[idx];pts=[]
  for it in v['items']:
   if it[0]=='l':
    if not pts:pts.append(tuple(it[1]))
    pts.append(tuple(it[2]))
  q=np.array(pts);ax.plot((q[:,0]-xz)/xs,yb+(yz-q[:,1])/ys,c=v['color'],lw=1.15,zorder=3)
  ax.axvline(bp,c='.55',ls='--',lw=.6,zorder=1)
  ax.set(xlim=((xl-xz)/xs,(xr-xz)/xs),ylim=(yb+(yz-ybot)/ys,yb+(yz-yt)/ys),xlabel=xlab,ylabel=ylab)
  ax.text(bp,1.025,f'{bp:g}',transform=ax.get_xaxis_transform(),ha='center',fontsize=6.5,bbox=dict(fc='white',ec='none',pad=.25))
 return snip(fig)

def fig2():
 d,p=new(670)
 # Retain original v14 SHAP drawing, percentages and legend.
 clip(p,(18,15,296,212),'Fig7_drivers',(5,5,262,169))
 letter(p,320,24,'B');put(p,(322,32,598,204),pathway())
 txt(p,326,215,'Selected regression structure, not causal links; full model in SI.',6.7,color=(.35,.35,.35))
 gc=['#c0262c','#8c510a','#7fbc41','#6a51a3']
 mappanel(p,(16,239,280,178),'C','Fig7_drivers',0,gc,['Climate','Soil','Topo.','Parent'],'Dominant group: SIC presence',('Fig7_drivers',(266,82,332,130)),True)
 mappanel(p,(316,239,280,178),'D','Fig7_drivers',2,gc,['Climate','Soil','Topo.','Parent'],'Dominant group: SOC (mineral)',('Fig7_drivers',(266,234,332,282)),True)
 # Exact original vector PDP polylines, relabelled cleanly without adjacent-panel fragments.
 put(p,(18,467,598,639),pdp_row())
 for k,s in enumerate('EFGH'):letter(p,19+150*k,455,s)
 txt(p,22,658,'Dashed lines: fitted PDP breakpoints. SHAP, maps and paths describe associations, not causation.',6.8,color=(.35,.35,.35))
 save(d,'Fig2_associations',8)

def bivarlegend(cols,labs):
 fig=plt.figure(figsize=(2.5,.85));ax=fig.add_axes([.16,.28,.20,.57])
 for (i,j),c in cols.items():ax.add_patch(Rectangle((i,j),1,1,color=c,ec='white',lw=.4))
 ax.set(xlim=(0,2),ylim=(0,2),xticks=[.5,1.5],yticks=[.5,1.5]);ax.set_xticklabels(['−','+'],fontsize=6);ax.set_yticklabels(['−','+'],fontsize=6);ax.tick_params(length=0,pad=1)
 ax.set_xlabel(labs[0],fontsize=6,labelpad=0);ax.set_ylabel(labs[1],fontsize=6,labelpad=0)
 return fig,ax

def bivpanel(p,rect,let,name,idx,cols,labs,values,order,denom='Area (%)'):
 x,y,w,h=rect;letter(p,x+2,y+11,let)
 # Both small charts BELOW map, with a dedicated horizontal strip and 25pt gap.
 put(p,(x+3,y+15,x+w,y+h-80),cleanmap(name,idx))
 fig,ax=bivarlegend(cols,labs)
 bx=fig.add_axes([.60,.28,.36,.57]);bx.bar(range(4),values,color=[cols[k] for k in order],width=.75)
 bx.set(xticks=[],ylim=(0,max(values)*1.28));bx.set_ylabel(denom,fontsize=5.5,labelpad=1);bx.tick_params(labelsize=5.5,length=2,pad=1)
 for i,v in enumerate(values):bx.text(i,v+1,f'{v:.0f}',ha='center',fontsize=6,fontweight='bold')
 put(p,(x+7,y+h-79,x+w-3,y+h-5),snip(fig))

def continental():
 j=json.load(open(NUM/'out_v14/fig_numbers_v14_45.json'))['fig5_continent']
 cc=['AS','EU','NA','SA','AF','OC'];v=np.array([j[c] for c in cc]);x=np.arange(6)
 fig,ax=plt.subplots(figsize=(3.3,2.45));fig.subplots_adjust(left=.22,right=.97,bottom=.20,top=.96)
 ax.bar(x-.18,v[:,0],.36,color=SOC,label='ΔSOC');ax.bar(x+.18,v[:,1],.36,color='#c0262c',label='ΔSIC');ax.axhline(0,c='.5',lw=.5)
 ax.set(xticks=x,xticklabels=cc,ylabel='Change by continent (Pg C)',ylim=(-195,165));ax.legend(loc='upper right',fontsize=6.5)
 return snip(fig)

def fig3():
 d,p=new(692);letter(p,19,19,'A');letter(p,318,19,'B')
 put(p,(20,23,294,163),density('Fig3_climate_change',[16,18,20,22],[17,19,21,23],C3A,'ΔSOC$_{0–30}$ equilibrium (Mg C ha$^{-1}$)',LL,size=(3.65,1.95)))
 put(p,(320,23,598,163),density('Fig3_climate_change',[62,64],[63,65],C3B,'Change SSP5-8.5 (Mg C ha$^{-1}$)',['ΔSOC$_{0–200}$','ΔSIC$_{0–200}$'],size=(3.65,1.95)))
 txt(p,30,184,'Area with topsoil SOC loss / gain',7.5)
 put(p,(190,161,294,213),proportions('Fig3_climate_change',list(range(27,35)),63.244781,.5312546,['<0','>0'],SC))
 bins=['−50','−20','−5','5','20','50']
 mappanel(p,(16,220,280,183),'C','Fig3_climate_change',2,DIV,bins,'ΔSOC$_{0–200}$ SSP5-8.5',('Fig3_climate_change',(5,383,77,433)))
 mappanel(p,(316,220,280,183),'D','Fig3_climate_change',3,DIV,bins,'ΔSIC$_{0–200}$ SSP5-8.5',('Fig3_climate_change',(265,383,337,433)))
 bivpanel(p,(16,429,337,241),'E','Fig5_bivariate_SOC_SIC',0,BIV,['ΔSOC','ΔSIC'],list(json.load(open(NUM/'out_v14/fig_numbers_v14_45.json'))['fig5_quadrants_pct_of_mapped_land'].values()),[(0,1),(0,0),(1,1),(1,0)],'% mapped land')
 # Original continental vector bar panel, no redundant country scatter.
 put(p,(365,456,598,644),continental());letter(p,365,440,'F')
 txt(p,25,683,'Bivariate denominator: 137.3 Mkm². Signs of ensemble means are not cellwise significance tests.',6.7,color=(.35,.35,.35))
 save(d,'Fig3_equilibrium_geography',6)

def fig4():
 # Rich kinetics: interval distributions, budget, realized shares, and depth synthesis.
 d,p=new(630)
 fig=plt.figure(figsize=(8.2,2.4));axs=[fig.add_axes([.075+k*.32,.23,.245,.68]) for k in range(3)]
 for ax,pool,c in zip(axs,['SOC','SIC','TC'],[SOC,SIC,TC]):
  key='d'+pool+'_0_200'
  for k,kind in enumerate(['eq','tl']):
   dat=[J['future'][s][kind][key] for s in SS];means=np.array([z['mean'] for z in dat]);err=np.array([[z['mean']-z['p05'],z['p95']-z['mean']] for z in dat]).T
   ax.errorbar(means,np.arange(4)+(k-.5)*.16,xerr=err,fmt='o' if k==0 else 's',ms=4,c=c,alpha=1 if k==0 else .46,elinewidth=.9,capsize=2,label='Equilibrium' if k==0 else 'By 2100')
  ax.axvline(0,c='.6',lw=.6);ax.set_yticks(range(4));ax.set_yticklabels(LL);ax.invert_yaxis();ax.set_xlabel('Δ'+pool+' (0–200 cm; Pg C)');ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=2,fontsize=6.5,columnspacing=.6)
 put(p,(18,25,598,215),snip(fig))
 for k,l in enumerate('ABC'):letter(p,19+199*k,19,l)
 # D / E are accounting waterfalls, not synthetic temporal trajectories.
 for k,kind in enumerate(['eq','tl']):
  vals=[J['future']['585'][kind]['d'+pool+'_0_200']['mean'] for pool in ['SOC','SIC','TC']]
  fig,ax=plt.subplots(figsize=(3.7,2.25));fig.subplots_adjust(left=.18,bottom=.23,top=.82,right=.96)
  ax.bar(0,vals[0],color=SOC,width=.58);ax.bar(1,vals[1],bottom=vals[0],color=SIC,width=.58);ax.bar(2,vals[2],color=TC,width=.58)
  ax.plot([.29,.71],[vals[0]]*2,c='.5',lw=.65);ax.plot([1.29,1.71],[vals[0]+vals[1]]*2,c='.5',lw=.65)
  ax.axhline(0,c='.6',lw=.5)
  for i,v in enumerate(vals):
   yp=(vals[0]+vals[1]/2 if i==1 else v/2)
   ax.text(i,yp+30 if abs(v)<25 else yp,f'{v:+.0f}',ha='center',va='center',color=c if False else ('#6a51a3' if abs(v)<25 else 'white'),fontsize=9,fontweight='bold')
  ax.set(xticks=range(3),xticklabels=['ΔSOC','ΔSIC','ΔTC'],ylim=(-430,35),ylabel='Stock change (Pg C)')
  ax.set_title('SSP5-8.5: '+('equilibrium' if kind=='eq' else 'by 2100'),fontsize=8.5,loc='left',pad=10)
  put(p,(19+300*k,254,298+300*k,443),snip(fig));letter(p,19+300*k,244,'DE'[k])
 # F: paired realized and committed fractions, with subdued horizontal bars.
 fig,ax=plt.subplots(figsize=(7.7,1.35));fig.subplots_adjust(left=.11,right=.97,bottom=.38,top=.92)
 ratios=[100*J['future']['585']['tl']['d'+q+'_0_200']['mean']/J['future']['585']['eq']['d'+q+'_0_200']['mean'] for q in ['SOC','SIC']]
 for i,(v,c) in enumerate(zip(ratios,[SOC,SIC])):
  ax.barh(i,100,color='#eeeeee',height=.42);ax.barh(i,v,color=c,height=.42);ax.text(v+1.8,i,f'{v:.0f}%',va='center',fontsize=8,fontweight='bold')
 ax.set(yticks=[0,1],yticklabels=['SOC','SIC'],xlim=(0,109),xticks=[0,25,50,75,100],xlabel='Fraction of SSP5-8.5 equilibrium change realized by 2100 (%)');ax.invert_yaxis()
 put(p,(25,481,592,596),snip(fig));letter(p,19,477,'F')
 txt(p,24,617,'Assumed first-order response (t = 85 years); not observed trajectories or atmospheric CO₂ fluxes.',6.9,color=(.35,.35,.35))
 save(d,'Fig4_kinetic_stock_change',6)

def fig5():
 d,p=new(576)
 # Original rich v14 density + national lollipop rankings.
 clip(p,(15,12,297,185),'Fig4_N_acidification',(29,7,266,143))
 clip(p,(311,12,600,185),'Fig4_N_acidification',(267,3,540,143))
 nc=['#7f0000','#d7301f','#fc8d59','#fdbb84','#fdd49e','#fff7ec','#f7f7f7'];nt=['−10','−5','−2','−1','−0.5','−0.01']
 mappanel(p,(16,204,280,181),'C','Fig4_N_acidification',0,nc,nt,'ΔSIC$_{0–30}$ SSP1-2.6',('Fig4_N_acidification',(4,209,78,260)))
 mappanel(p,(316,204,280,181),'D','Fig4_N_acidification',1,nc,nt,'ΔSIC$_{0–30}$ SSP5-8.5',('Fig4_N_acidification',(263,209,337,260)))
 clip(p,(17,408,598,546),'Fig4_N_acidification',(19,297,535,397))
 txt(p,23,566,'Separate 2020–2050 N experiment; deeper losses assume topsoil ΔpH at every depth. Not combined with climate.',6.6,color=(.35,.35,.35))
 save(d,'Fig5_nitrogen',5)

def fraction_bars():
 fig,ax=plt.subplots(figsize=(3.8,2.05));fig.subplots_adjust(left=.20,right=.97,bottom=.23,top=.94);x=np.arange(4)
 items=[('eq','dMAOC',SOC,'ΔMAOC eq.'),('eq','dPOC','#e08214','ΔPOC eq.'),('tl','dMAOC','#9ecae1','ΔMAOC by 2100'),('tl','dPOC','#fdbe85','ΔPOC by 2100')]
 for k,(kind,key,c,lab) in enumerate(items):
  z=[J['future'][s][kind][key] for s in SS];v=[q['mean'] for q in z];err=np.array([[q['mean']-q['p05'],q['p95']-q['mean']] for q in z]).T
  ax.bar(x+(k-1.5)*.19,v,.19,color=c,label=lab,yerr=err,error_kw=dict(lw=.5,capsize=1))
 ax.axhline(0,c='.4',lw=.5);ax.set(xticks=x,xticklabels=LL,ylabel='Δ stock 0–30 cm (Pg C)',ylim=(-137,5));ax.tick_params(axis='x',labelsize=6.5)
 ax.legend(loc='lower left',ncol=2,fontsize=5.5,handlelength=1.2,columnspacing=.8)
 return snip(fig)
def fig6():
 d,p=new(654);letter(p,19,19,'A');letter(p,318,19,'B')
 put(p,(21,23,296,195),density('Fig6_MAOC_POC',[15,17,19,21],[16,18,20,22],C6A,'log$_{10}$ stock (Mg C ha$^{-1}$)',['MAOC 0–30','POC 0–30','MAOC 30–100','POC 30–100'],legend='above',size=(3.7,2.05)))
 put(p,(320,25,598,195),fraction_bars())
 mappanel(p,(16,217,280,178),'C','Fig6_MAOC_POC',0,['#fdd0a2','#fdae6b','#fd8d3c','#c6dbef','#6baed6','#2171b5','#08306b'],['50','60','70','80','85','90'],'f$_{MAOC}$ 0–30 (%)',('Fig6_MAOC_POC',(4,214,76,263)))
 mappanel(p,(316,217,280,178),'D','Fig6_MAOC_POC',1,BLUES,['10','20','30','40','60','90'],'MAOC$_{0–30}$ (Mg C ha$^{-1}$)',('Fig6_MAOC_POC',(261,211,335,263)))
 bivpanel(p,(16,420,362,216),'E','Fig6_MAOC_POC',2,MA_BIV,['MAOC','POC'],[30,15,11,44],[(1,1),(1,0),(0,1),(0,0)])
 # Distinguish committed decrease from depletion of entire stock: summary of known ensemble means.
 fig,ax=plt.subplots(figsize=(2.7,2.2));fig.subplots_adjust(left=.25,bottom=.23,right=.95,top=.88)
 vals=[]
 for key in ['dMAOC','dPOC']:
  e=J['future']['585']['eq'][key]['mean'];t=J['future']['585']['tl'][key]['mean'];vals.append((-t,-(e-t)))
 for i,(real,late) in enumerate(vals):
  ax.bar(i,real,.52,color=SOC if i==0 else '#e08214',label='By 2100' if i==0 else None)
  ax.bar(i,late,.52,bottom=real,color='#c6dbef' if i==0 else '#fdd0a2',label='Remaining commitment' if i==0 else None)
  ax.text(i,real/2,f'{real:.0f}',ha='center',va='center',color='white',fontsize=8,fontweight='bold')
  if late>2:ax.text(i,real+late/2,f'{late:.0f}',ha='center',va='center',fontsize=8)
 ax.set(xticks=[0,1],xticklabels=['MAOC','POC'],ylim=(0,90),ylabel='Committed decrease (Pg C)')
 from matplotlib.patches import Patch
 ax.legend(handles=[Patch(facecolor='#666666',label='Dark: by 2100'),Patch(facecolor='#dddddd',label='Pale: remaining commitment')],loc='upper center',bbox_to_anchor=(.5,1.30),fontsize=6)
 put(p,(398,440,595,626),snip(fig));letter(p,397,431,'F')
 txt(p,23,646,'Mineral soils only; τ assumed. Committed loss is not depletion of the pool. Georgiou comparison remains in SI.',6.6,color=(.35,.35,.35))
 save(d,'Fig6_organic_fractions',6)

if __name__=='__main__':
 for i in sys.argv[1:] or ['1','2','3','4','5','6']:globals()['fig'+i]()
 (R/'paper/v18_v14style/figure_render_audit.json').write_text(json.dumps(AUDIT,indent=2))
