import numpy as np, matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt, cartopy.crs as ccrs, cartopy.feature as cfeat, cartopy.io.shapereader as shp
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle
import rasterio.features as rf, rasterio.transform as rt
mpl.rcParams.update({'font.family':'DejaVu Sans','font.sans-serif':['Arial','Helvetica','Liberation Sans','DejaVu Sans'],'font.size':7,'axes.linewidth':0.5,
 'xtick.major.width':0.5,'ytick.major.width':0.5,'xtick.major.size':2,'ytick.major.size':2,'axes.spines.top':False,'axes.spines.right':False,
 'pdf.fonttype':42,'savefig.dpi':300,'legend.frameon':False})
GREY='#e3e3e3'
DIV=['#d7301f','#fc8d59','#fee08b','#c6dbef','#6baed6','#2171b5','#08306b']
DIV6=['#d7301f','#f88b3c','#fde08b','#c4c8f5','#7fa6ea','#3f6fbe']
BLUES=['#eff3ff','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#084594']
PURP=['#fcfbfd','#dadaeb','#bcbddc','#9e9ac8','#807dba','#6a51a3','#4a1486']
CONT=['AS','EU','NA','SA','AF','OC']; CCOL={'AS':'#f07f4f','EU':'#fbb065','NA':'#fff6c0','SA':'#8fc1dc','AF':'#2f4c9a','OC':'#e79ae8'}
mask=np.load('/workspace/soil_global/out/v4/mask.npy'); H,W=mask.shape
lat=90-(np.arange(H)+.5)/6; area=((111.32/6)**2*np.cos(np.deg2rad(lat))[:,None]*np.ones((1,W))*100)[mask]
def to2d(v):
  a=np.full((H,W),np.nan,'float32'); a[mask]=v; return a
_cc=None
def countries():
  global _cc
  if _cc is not None: return _cc
  import geopandas as gpd
  g=gpd.read_file(shp.natural_earth('50m','cultural','admin_0_countries'))
  cm={'Asia':'AS','Europe':'EU','North America':'NA','South America':'SA','Africa':'AF','Oceania':'OC'}
  tr=rt.from_origin(-180,90,1/6,1/6)
  ids=rf.rasterize([(geom,i+1) for i,geom in enumerate(g.geometry)],out_shape=(H,W),transform=tr,fill=0,dtype='int32')[mask]
  names=['']+list(g['NAME'].values); cont=['']+[cm.get(c,'') for c in g['CONTINENT'].values]
  _cc=(ids,np.array(names,object),np.array(cont,object)); return _cc
def by_country(v):
  ids,nm,ct=countries(); s=np.bincount(ids,weights=np.nan_to_num(v)*area,minlength=len(nm))*1e-9
  return s,nm,ct
def cont_share(v):
  ids,nm,ct=countries(); c=ct[ids]; tot=np.nansum(np.abs(v)*area); return {k:float(np.nansum((np.abs(v)*area)[c==k])/tot*100) for k in CONT}
def mapax(fig,rect):
  ax=fig.add_axes(rect,projection=ccrs.Robinson()); ax.set_extent([-180,180,-58,84],ccrs.PlateCarree())
  ax.add_feature(cfeat.LAND.with_scale('110m'),facecolor=GREY,edgecolor='none',zorder=0); ax.spines['geo'].set_visible(False)
  return ax
def classed(ax,v,bins,cols,inset='class',label='',fig=None,cbrect=None,fmt='{:g}',extend=True,cats=None):
  cmap=ListedColormap(cols); norm=BoundaryNorm(bins,len(cols),clip=True)
  a=to2d(v); ax.imshow(a,origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,interpolation='nearest',zorder=1,regrid_shape=1400)
  b=ax.inset_axes([0.04,0.10,0.16,0.36])
  if inset=='class':
    k=np.digitize(v,bins[1:-1]); ok=np.isfinite(v); p=[area[ok&(k==i)].sum()/area[ok].sum()*100 for i in range(len(cols))]
    b.bar(range(len(cols)),p,color=cols,width=0.8,edgecolor='none'); b.set_xticks([]); b.set_ylabel('Proportion (%)',fontsize=5)
  else:
    sh=cont_share(v); bot=0
    for c in CONT: b.bar(0,sh[c],bottom=bot,color=CCOL[c],width=0.6,edgecolor='white',lw=0.3); (b.text(0.42,bot+sh[c]/2,c,fontsize=4.5,va='center') if sh[c]>4 else None); bot+=sh[c]
    b.set_xlim(-0.5,1); b.set_xticks([]); b.set_ylabel('Share (%)',fontsize=5)
  b.tick_params(labelsize=5); b.patch.set_alpha(0)
  if fig is not None:
    pos=ax.get_position(); cr=cbrect or [pos.x0+pos.width*0.22,pos.y0-0.015,pos.width*0.55,0.012]
    c=fig.add_axes(cr); n=len(cols)
    for i,col in enumerate(cols): c.add_patch(Rectangle((i,0),1,1,color=col))
    c.add_patch(Rectangle((n+0.35,0),1,1,color=GREY)); c.text(n+1.5,0.5,'Not applied',va='center',fontsize=6)
    c.set_xlim(0,n+1.4); c.set_ylim(0,1); c.set_yticks([])
    if cats: c.set_xticks(np.arange(n)+0.5); c.set_xticklabels(cats,fontsize=5)
    else: c.set_xticks(range(1,n)); c.set_xticklabels([fmt.format(x) for x in bins[1:-1]],fontsize=5.5)
    for s in c.spines.values(): s.set_visible(False)
    c.tick_params(length=0,pad=1); c.set_title(label,fontsize=6.5,loc='left',x=-0.02,y=-0.2,ha='right',va='bottom') if False else c.text(-0.3,0.5,label,ha='right',va='center',fontsize=6.5)
BIV=np.array([['#e8e8e8','#ace4e4','#5ac8c8'],['#dfb0d6','#a5add3','#5698b9'],['#be64ac','#8c62aa','#3b4994']])
BIV2={(0,0):'#e8e8e8',(1,0):'#c85a5a',(0,1):'#64acbe',(1,1):'#574249'}
def bivar(ax,x,y,tx,ty,labs,cols=None,fig=None):
  cols=cols or {(1,1):'#3b4994',(1,0):'#be64ac',(0,1):'#5ac8c8',(0,0):'#d7a84a'}
  ok=np.isfinite(x)&np.isfinite(y); q=np.full(len(x),-1); 
  for (i,j),_ in cols.items(): q[ok&((x>tx)==bool(i))&((y>ty)==bool(j))]=i*2+j
  rgb=np.full((len(x),4),np.nan)
  for (i,j),c in cols.items(): rgb[q==i*2+j]=mpl.colors.to_rgba(c)
  img=np.zeros((H,W,4)); 
  for k in range(4): img[...,k][mask]=np.nan_to_num(rgb[:,k])
  ax.imshow(img,origin='upper',extent=[-180,180,-90,90],transform=ccrs.PlateCarree(),interpolation='nearest',zorder=1,regrid_shape=1400)
  L=ax.inset_axes([0.03,0.12,0.09,0.18]); 
  for (i,j),c in cols.items(): L.add_patch(Rectangle((i,j),1,1,color=c))
  L.set_xlim(0,2); L.set_ylim(0,2); L.set_xticks([0.5,1.5]); L.set_yticks([0.5,1.5]); L.set_xticklabels(['−','+'],fontsize=5); L.set_yticklabels(['−','+'],fontsize=5)
  L.set_xlabel(labs[0],fontsize=5,labelpad=0); L.set_ylabel(labs[1],fontsize=5,labelpad=0); L.tick_params(length=0,pad=1)
  B=ax.inset_axes([0.17,0.10,0.13,0.25]); p=[area[q==i*2+j].sum()/area[q>=0].sum()*100 for (i,j) in cols]
  B.bar(range(4),p,color=list(cols.values()),width=0.75)
  for k,v in enumerate(p): B.text(k,v+1,f'{v:.0f}',ha='center',fontsize=5,fontweight='bold')
  B.set_xticks([]); B.set_ylabel('Area (%)',fontsize=5); B.tick_params(labelsize=5); B.patch.set_alpha(0)
  return dict(zip([f'{i}{j}' for (i,j) in cols],p))
def letter(fig,ax,s,dx=-0.01,dy=0.0):
  p=ax.get_position(); fig.text(p.x0+dx,p.y1+dy,s,fontsize=9,fontweight='bold',va='bottom',ha='left')
def dens(ax,data,labels,colors,xlabel,log=False,inset=None):
  from scipy.stats import gaussian_kde
  for d,l,c in zip(data,labels,colors):
    d=d[np.isfinite(d)]; d=np.log10(d[d>0]) if log else d
    d=np.random.default_rng(0).choice(d,min(len(d),40000),replace=False); xs=np.linspace(np.percentile(d,0.5),np.percentile(d,99.5),300)
    ax.plot(xs,gaussian_kde(d)(xs),color=c,lw=1.1,label=l); ax.axvline(np.median(d),color=c,ls='--',lw=0.8)
  ax.set_xlabel(xlabel); ax.set_ylabel('Probability density'); ax.legend(fontsize=6,loc='upper left' if inset else 'upper right'); ax.set_ylim(bottom=0)
  if inset:
    b=ax.inset_axes([0.62,0.55,0.3,0.4]); cats,vals=inset; x=np.arange(len(cats)); wd=0.8/len(vals)
    for k,(v,c) in enumerate(zip(vals,colors)): b.bar(x+k*wd-0.4+wd/2,v,wd,color=c)
    b.set_xticks(x); b.set_xticklabels(cats,fontsize=5); b.tick_params(labelsize=5); b.set_title('Proportion (%)',fontsize=5.5)
def save(fig,path): fig.savefig(path+'.png',dpi=300,bbox_inches='tight'); fig.savefig(path+'.pdf',bbox_inches='tight'); plt.close(fig)
