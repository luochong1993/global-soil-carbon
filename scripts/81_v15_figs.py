#!/usr/bin/env python3
"""v15 figure regeneration.
Evaluation-driven: opaque insets, colorblind bivariate, scatter alpha/adjustText,
breakpoint zorder, elevate path+kinetics, demote Georgiou/country-rings, SI clarity.
Numbers from out/v10 + out/v8 + out/v13 only — no invented values.
"""
import sys, json, glob, os, numpy as np, pandas as pd
import matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import cartopy.crs as ccrs

R = '/workspace/soil_global'
O10 = R + '/out/v10'; O8 = R + '/out/v8'; O7 = R + '/out/v7'
FM = R + '/figs/v15_main/'; FS = R + '/figs/v15_SI_raw/'
os.makedirs(FM, exist_ok=True); os.makedirs(FS, exist_ok=True)

# ---- load style then v15 patches ----
exec(open(R + '/scripts/43_v8_style.py').read(), globals())
exec(open(R + '/scripts/80_v15_style.py').read(), globals())
classed = classed_v15  # override globally for this run

EM = np.load(O10 + '/ens_maps.npz')
EJ = json.load(open(O10 + '/ensemble_v10.json'))
DJ = json.load(open(O8 + '/drivers_v8.json'))
PD = json.load(open(O8 + '/pdp.json'))
OB = json.load(open(O8 + '/obs_curves.json'))
NM = json.load(open(O8 + '/shap_names.json')) if os.path.exists(O8 + '/shap_names.json') else {}
FJ8 = json.load(open(O8 + '/fractions_v8.json'))
P = EJ['present']
FJ = json.loads(json.dumps(FJ8))
FJ['_0_30'].update(MAOC=P['_0_30']['MAOC']['mean'], MAOC_CI90=[P['_0_30']['MAOC']['p05'], P['_0_30']['MAOC']['p95']])
FJ['_30_100'].update(MAOC=P['_30_100']['MAOC']['mean'])
sc = {}
for s in ['126', '245', '370', '585']:
    e = EJ['future'][s]['eq']; t = EJ['future'][s]['tl']
    sc[s] = dict(
        dMAOC_eq=e['dMAOC']['mean'], dPOC_eq=e['dPOC']['mean'],
        dMAOC_eq_range=[e['dMAOC']['p05'], e['dMAOC']['p95']],
        dPOC_eq_range=[e['dPOC']['p05'], e['dPOC']['p95']],
        tl_central=dict(dMAOC=t['dMAOC']['mean'], dPOC=t['dPOC']['mean'],
                        tau_POC='5–30', tau_MAOC='50–400'))
FJ['future_0_30']['scen'] = sc

z0 = dict(soc=EM['p_soc_0_30'], sic=EM['p_sic_0_30'])
z1 = dict(soc=EM['p_soc_30_100'], sic=EM['p_sic_30_100'])
z2 = dict(soc=EM['p_soc_100_200'], sic=EM['p_sic_100_200'])
SOC = z0['soc'] + z1['soc'] + z2['soc']
SIC = z0['sic'] + z1['sic'] + z2['sic']
TC = SOC + SIC
b5 = {f'dsoc_0_30_{s}': EM[f'dsoc_0_30_{s}'] for s in ['126', '245', '370', '585']}
sh = dict(dsoc=EM['dsoc_0_200_585'], dsic=EM['dsic_0_200_585'])
fr8 = np.load(O8 + '/frac_maps10.npz')
f0 = np.where(EM['p_MA'] + EM['p_PO'] > 0, EM['p_MA'] / np.maximum(EM['p_MA'] + EM['p_PO'], 1e-6), np.nan)
fr = dict(MA_0_30=EM['p_MA'], PO_0_30=EM['p_PO'], f_0_30=f0,
          MA_30_100=fr8['MA_30_100'], PO_30_100=fr8['PO_30_100'], fsd_0_30=fr8['fsd_0_30'])
NMAP = {}
for s in ['126', '245', '370', '585']:
    NMAP[f'dSIC_loss_{s}'] = EM[f'N_loss_0_30_{s}']
    NMAP[f'dSIC_loss0200_{s}'] = EM[f'N_loss_0_200_{s}']
    z = np.load(f'{O10}/Nin_{s}_2020_2050.npz')
    NMAP[f'dph_{s}'] = np.where(z['fr'] > 0.01, -0.06 * z['Nin'] + 0.11, 0)
N = NMAP
SSP = ['126', '245', '370', '585']
SSP4 = SSP
LBL = {s: f'SSP{s[0]}-{s[1]}.{s[2]}' for s in SSP}
SC = {'126': '#1d3c8f', '245': '#69b3e0', '370': '#f39c4a', '585': '#c0262c'}
SC4 = SC
GC = {'Climate': '#c0262c', 'Soil': '#8c510a', 'Topography': '#7fbc41',
      'Parent material': '#6a51a3', 'Sampling': '#bdbdbd'}
log = {}
letter_up = lambda fig, ax, s, dx=-0.01, dy=0.0: letter(fig, ax, s.upper(), dx, dy)

def F(fn):
    try:
        fn(); print('ok', fn.__name__, flush=True)
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAIL', fn.__name__, e, flush=True)

# ============== MAIN FIG 1: baseline stocks (polish insets only; keep 6 panels) ==============
def fig1():
    fig = plt.figure(figsize=(7.2, 6.3))
    a = fig.add_axes([0.07, 0.78, 0.38, 0.18])
    dens(a, [z0['soc'], z1['soc'], z2['soc']],
         ['0–30 cm', '30–100 cm', '100–200 cm'],
         ['#2171b5', '#6a51a3', '#e08214'],
         'log$_{10}$ SOC stock (Mg C ha$^{-1}$)', log=True,
         inset=(['SOC', 'SIC'],
                [[(z['soc'] * area).sum() / (SOC * area).sum() * 100,
                  (z['sic'] * area).sum() / (SIC * area).sum() * 100] for z in (z0, z1, z2)]))
    for iax in list(a.child_axes) if hasattr(a,'child_axes') else []:
        style_inset(iax)
    # dens uses inset_axes; find by title
    for iax in fig.axes:
        if iax is a: continue
        if (iax.get_title() or '').startswith('Proportion'):
            style_inset(iax)
    letter_up(fig, a, 'a', -0.05)
    b = fig.add_axes([0.57, 0.78, 0.38, 0.18])
    dens(b, [z0['sic'], z1['sic'], z2['sic']],
         ['0–30 cm', '30–100 cm', '100–200 cm'],
         ['#2171b5', '#6a51a3', '#e08214'],
         'log$_{10}$ SIC stock (Mg C ha$^{-1}$)', log=True)
    letter_up(fig, b, 'b', -0.05)
    for k, (v, bins, cols, lab, rect, ins) in enumerate([
        (z0['soc'], [0, 20, 40, 60, 80, 120, 200, 1e4], BLUES, 'SOC$_{0–30}$ (Mg C ha$^{-1}$)', [0.0, 0.42, 0.5, 0.3], 'continent'),
        (z0['sic'], [0, 1, 5, 10, 20, 40, 80, 1e4], PURP, 'SIC$_{0–30}$ (Mg C ha$^{-1}$)', [0.5, 0.42, 0.5, 0.3], 'continent'),
        (SOC, [0, 50, 100, 150, 200, 300, 500, 1e4], BLUES, 'SOC$_{0–200}$', [0.0, 0.06, 0.5, 0.3], 'class'),
        (SIC, [0, 5, 20, 50, 100, 200, 400, 1e4], PURP, 'SIC$_{0–200}$', [0.5, 0.06, 0.5, 0.3], 'class')]):
        ax = mapax(fig, rect); classed(ax, v, bins, cols, ins, lab, fig); letter_up(fig, ax, 'cdef'[k], 0.02, -0.02)
    save(fig, FM + 'Fig1_present_stocks')

# ============== MAIN FIG 2: SIC geography (slim: map + scatter + lollipop; rings → SI) ==============
def fig2():
    fig = plt.figure(figsize=(7.2, 5.4))
    share = np.where(TC > 0, SIC / TC * 100, np.nan)
    ax = mapax(fig, [0.0, 0.42, 0.62, 0.55])
    classed(ax, share, [0, 5, 10, 20, 30, 40, 60, 100],
            ['#08306b', '#3f6fbe', '#7fa6ea', '#c4c8f5', '#fde08b', '#f88b3c', '#d7301f'],
            'class', 'SIC/TC$_{0–200}$ (%)', fig)
    letter_up(fig, ax, 'a', 0.02)
    s1, nm, ct = by_country(SOC); s2, _, _ = by_country(SIC)
    df = pd.DataFrame(dict(n=nm, c=ct, soc=s1, sic=s2))[1:]
    df = df[df.c != '']; df['tc'] = df.soc + df.sic; df['sh'] = df.sic / df.tc * 100
    t = df.sort_values('tc', ascending=False).head(18)[::-1]
    b = fig.add_axes([0.70, 0.45, 0.27, 0.48])
    b.hlines(range(len(t)), 0, t.tc, color='0.4', lw=0.6)
    b.scatter(t.tc, range(len(t)), c=[CCOL[c] for c in t.c], s=22, edgecolor='k', lw=0.3, zorder=3)
    b.set_yticks(range(len(t))); b.set_yticklabels(t.n, fontsize=5.5)
    b.set_xlabel('Total C 0–200 cm (Pg)'); b.xaxis.set_label_position('top'); b.xaxis.tick_top()
    b.spines['bottom'].set_visible(False); b.spines['top'].set_visible(True)
    letter_up(fig, b, 'b', -0.12)
    # scatter with alpha
    c = fig.add_axes([0.08, 0.07, 0.55, 0.30])
    big = df[df.tc > 0.5]
    cols_pts = [CCOL[x] for x in big.c]
    c.scatter(np.log10(big.soc), big.sh, s=10, c=cols_pts, edgecolor='k', lw=0.15, alpha=0.55, zorder=2)
    m1 = np.median(np.log10(big.soc)); m2 = np.median(big.sh)
    c.axvline(m1, ls='--', c='0.5', lw=0.6, zorder=1); c.axhline(m2, ls='--', c='0.5', lw=0.6, zorder=1)
    for (qx, qy), (px, py) in {(1, 1): (0.97, 0.95), (0, 1): (0.03, 0.95), (0, 0): (0.03, 0.05), (1, 0): (0.97, 0.05)}.items():
        n = ((np.log10(big.soc) > m1) == qx) & ((big.sh > m2) == qy)
        c.text(px, py, f'{n.mean() * 100:.0f}%', transform=c.transAxes,
               ha='right' if qx else 'left', va='top' if qy else 'bottom', fontweight='bold', fontsize=7, zorder=5)
    # continent legend
    for k, cc in enumerate(CONT):
        c.scatter([], [], c=CCOL[cc], s=12, label=cc, edgecolor='k', lw=0.2)
    c.legend(fontsize=5.5, ncol=6, loc='upper center', bbox_to_anchor=(0.5, -0.18), handletextpad=0.2)
    c.set_xlabel('log$_{10}$ country SOC$_{0–200}$ (Pg)'); c.set_ylabel('SIC share of TC (%)')
    letter_up(fig, c, 'c', -0.06)
    # note: polar rings moved to SI (FigS_country_rings)
    save(fig, FM + 'Fig2_SIC_share_countries')

def figS_country_rings():
    """Demoted from main Fig2D (+ keep full 36-country polar)."""
    s1, nm, ct = by_country(SOC); s2, _, _ = by_country(SIC)
    df = pd.DataFrame(dict(n=nm, c=ct, soc=s1, sic=s2))[1:]
    df = df[df.c != '']; df['tc'] = df.soc + df.sic; df['sh'] = df.sic / df.tc * 100
    fig = plt.figure(figsize=(7.2, 4.2))
    d = fig.add_axes([0.08, 0.06, 0.55, 0.88], projection='polar')
    top = df.sort_values('sic', ascending=False).head(36); top = top.sort_values(['c', 'sh'])
    th = np.linspace(0, 2 * np.pi, len(top), endpoint=False)
    d.bar(th, top.sh, width=2 * np.pi / len(top) * 0.85, color=[CCOL[x] for x in top.c],
          edgecolor='white', lw=0.3, bottom=8)
    for t_, r_, n_ in zip(th, top.sh, top.n):
        d.text(t_, r_ + 12, n_[:12], fontsize=4.5,
               rotation=np.degrees(t_) if np.degrees(t_) <= 180 else np.degrees(t_) - 180,
               ha='center', va='center')
    d.set_yticklabels([]); d.set_xticks([]); d.spines['polar'].set_visible(False); d.grid(lw=0.3)
    for k, cc in enumerate(CONT):
        fig.text(0.70, 0.75 - k * 0.05, '■', color=CCOL[cc], fontsize=10)
        fig.text(0.73, 0.752 - k * 0.05, cc, fontsize=8)
    fig.text(0.02, 0.95, 'A', fontsize=9, fontweight='bold')
    save(fig, FS + 'FigS_country_SIC_rings')

# ============== MAIN FIG 3: drivers + path model (elevate S12; demote PDP G/H) ==============
def fig3_drivers():
    fig = plt.figure(figsize=(7.2, 6.4))
    S = DJ['shap']; comps = list(S); g = DJ['groups']
    a = fig.add_axes([0.08, 0.72, 0.38, 0.24]); left = np.zeros(len(comps))
    for gg in g:
        v = np.array([S[c]['group_pct'][gg] for c in comps])
        a.barh(range(len(comps)), v, left=left, color=GC[gg], label=gg, edgecolor='white', lw=0.3)
        for i, (l_, vv) in enumerate(zip(left, v)):
            if vv > 9:
                a.text(l_ + vv / 2, i, f'{vv:.0f}', ha='center', va='center', fontsize=5.5, color='white', fontweight='bold')
        left += v
    a.set_yticks(range(len(comps))); a.set_yticklabels(comps)
    a.set_xlabel('Share of mean |SHAP| (%)'); a.set_xlim(0, 100)
    a.legend(fontsize=5, ncol=5, loc='lower center', bbox_to_anchor=(0.5, 1.0), handlelength=1)
    letter_up(fig, a, 'a', -0.1)
    # path model (elevated from SI)
    s = DJ['sem']
    axp = fig.add_axes([0.55, 0.70, 0.42, 0.26]); axp.axis('off')
    Ppos = {'logAI': (0.08, 0.85), 'bio1': (0.08, 0.55), 'clay': (0.08, 0.28),
            'carbonate_rock': (0.08, 0.05), 'pH': (0.48, 0.48),
            'lSIC': (0.88, 0.72), 'lSOC': (0.88, 0.22)}
    lab = {'logAI': 'Aridity\n(log P/PET)', 'bio1': 'MAT', 'clay': 'Clay',
           'carbonate_rock': 'Carb. rock',
           'pH': f"pH\nR²={s['pH']['R2']:.2f}",
           'lSIC': f"SIC\nR²={s['SIC']['R2']:.2f}",
           'lSOC': f"SOC\nR²={s['SOC']['R2']:.2f}"}
    for k, (x, y) in Ppos.items():
        axp.text(x, y, lab[k], ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.25', fc='#f7f7f7', ec='0.35', lw=0.5), fontsize=5.5)
    for tgt, key in [('pH', 'pH'), ('lSIC', 'SIC'), ('lSOC', 'SOC')]:
        for src, bcoef in s[key].items():
            if src == 'R2' or abs(bcoef) < 0.05:
                continue
            (x0, y0), (x1, y1) = Ppos[src], Ppos[tgt]
            axp.annotate('', xy=(x1 - 0.07, y1), xytext=(x0 + 0.08, y0),
                         arrowprops=dict(arrowstyle='->',
                                         color='#c0262c' if bcoef < 0 else '#2171b5',
                                         lw=0.4 + abs(bcoef) * 4, mutation_scale=8))
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 0.04
            axp.text(mx, my, f'{bcoef:.2f}', fontsize=5,
                     color='#c0262c' if bcoef < 0 else '#2171b5',
                     ha='center',
                     bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.85))
    axp.text(0.5, 1.02, f"Path model (n={s['n']}); aridity→pH→SIC = {s['indirect_AI_pH_SIC']:.2f}",
             ha='center', fontsize=5.5, transform=axp.transAxes)
    letter_up(fig, axp, 'b', -0.02, 0.02)
    # dominant driver maps (SIC presence + mineral SOC only; fMAOC → SI with others)
    dd = np.load(O8 + '/dominant_driver.npz'); cols = [GC[x] for x in g[:4]]
    for k, (key, rect, let) in enumerate([
        ('SIC presence', [0.0, 0.36, 0.5, 0.28], 'c'),
        ('SOC (mineral)', [0.5, 0.36, 0.5, 0.28], 'd')]):
        ax = mapax(fig, rect)
        classed(ax, dd[key].astype(float) + 0.5, [0, 1, 2, 3, 4], cols, 'class', key, fig,
                cats=['Climate', 'Soil', 'Topo.', 'Parent'])
        letter_up(fig, ax, let, 0.02, -0.02)
    # breakpoints E/F only (SIC pathway); G/H fMAOC → SI
    for k, (key, xl, yl, col, let) in enumerate([
        ('SIC_presence_vs_logAI', 'ln(1+P/PET)', 'P(SIC>0.1)', '#6a51a3', 'e'),
        ('SIC_presence_vs_pH', 'predicted pH', 'P(SIC>0.1)', '#6a51a3', 'f')]):
        p = PD[key]
        ax = fig.add_axes([0.10 + k * 0.45, 0.06, 0.35, 0.24])
        ax.axvline(p['breakpoint'], ls='--', c='0.55', lw=0.7, zorder=1)
        ax.plot(p['x'], p['y'], c=col, lw=1.3, zorder=3)
        # label ABOVE the axes (not on the curve)
        import matplotlib.transforms as mtransforms
        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
        ax.text(p['breakpoint'], 1.02, f"{p['breakpoint']:.2g}", fontsize=5.5, va='bottom', ha='center',
                transform=trans, clip_on=False,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='0.6', lw=0.4), zorder=4)
        ax.set_xlabel(xl); ax.set_ylabel(yl)
        letter_up(fig, ax, let, -0.05)
    save(fig, FM + 'Fig7_drivers')  # keep filename; manuscript maps Fig3→this file

# ============== MAIN FIG 4: equilibrium + trade-off (merge old 4+5) ==============
def fig4_eq_tradeoff():
    fig = plt.figure(figsize=(7.2, 7.2))
    a = fig.add_axes([0.07, 0.78, 0.40, 0.18])
    dens(a, [b5[f'dsoc_0_30_{s}'] for s in SSP], [LBL[s] for s in SSP], [SC[s] for s in SSP],
         'ΔSOC$_{0–30}$ equilibrium (Mg C ha$^{-1}$)',
         inset=(['<0', '>0'],
                [[(area[b5[f'dsoc_0_30_{s}'] < 0]).sum() / area.sum() * 100,
                  (area[b5[f'dsoc_0_30_{s}'] > 0]).sum() / area.sum() * 100] for s in SSP]))
    a.set_xlim(-80, 40); letter_up(fig, a, 'a', -0.05)
    b = fig.add_axes([0.57, 0.78, 0.40, 0.18])
    dens(b, [sh['dsoc'], sh['dsic']], ['ΔSOC$_{0–200}$', 'ΔSIC$_{0–200}$'],
         ['#2171b5', '#c0262c'], 'Change SSP5-8.5 (Mg C ha$^{-1}$)')
    b.set_xlim(-150, 150); letter_up(fig, b, 'b', -0.05)
    bins = [-1e4, -50, -20, -5, 5, 20, 50, 1e4]
    for k, (v, lab, rect, let) in enumerate([
        (sh['dsoc'], 'ΔSOC$_{0–200}$ SSP5-8.5', [0.0, 0.48, 0.5, 0.26], 'c'),
        (sh['dsic'], 'ΔSIC$_{0–200}$ SSP5-8.5', [0.5, 0.48, 0.5, 0.26], 'd')]):
        ax = mapax(fig, rect); classed(ax, v, bins, DIV, 'class', lab, fig, fmt='{:g}')
        letter_up(fig, ax, let, 0.02, -0.02)
    # bivariate with colorblind palette
    ax = mapax(fig, [0.0, 0.14, 0.62, 0.30])
    order = [(0, 1), (0, 0), (1, 1), (1, 0)]
    names = ['SOC−\nSIC+', 'SOC−\nSIC−', 'SOC+\nSIC+', 'SOC+\nSIC−']
    land_mkm2 = area[np.isfinite(sh['dsoc']) & np.isfinite(sh['dsic'])].sum() / 1e8
    pdict, tot = bivar_v15(ax, sh['dsoc'], sh['dsic'], 0, 0, ['ΔSOC', 'ΔSIC'],
                           cols=BIV_CB, order=order, names=names,
                           denom_label=f'% of mapped land\n({land_mkm2:.1f} Mkm$^2$)')
    log['fig4_quadrants'] = pdict
    letter_up(fig, ax, 'e', 0.02)
    # continental bars
    d = fig.add_axes([0.68, 0.16, 0.28, 0.26])
    ids, nm_, ct_ = countries()
    M = np.array([[(v[ct_[ids] == cc] * area[ct_[ids] == cc]).sum() * 1e-9
                   for v in (sh['dsoc'], sh['dsic'])] for cc in CONT])
    x = np.arange(len(CONT))
    d.bar(x - 0.18, M[:, 0], 0.36, color='#2171b5', label='ΔSOC')
    d.bar(x + 0.18, M[:, 1], 0.36, color='#c0262c', label='ΔSIC')
    d.axhline(0, c='k', lw=0.4); d.set_xticks(x); d.set_xticklabels(CONT)
    d.set_ylabel('Change by continent (Pg C)'); d.legend(fontsize=6)
    letter_up(fig, d, 'f', -0.08)
    save(fig, FM + 'Fig3_climate_change')  # file used as manuscript Fig4 content base; also write tradeoff name
    # also save under bivariate name for any leftover refs during transition
    import shutil
    for ext in ('.png', '.pdf'):
        shutil.copy(FM + 'Fig3_climate_change' + ext, FM + 'Fig5_bivariate_SOC_SIC' + ext)

# ============== MAIN FIG 5: kinetic decoupling (NEW main; from S15) ==============
def fig5_kinetic():
    fig = plt.figure(figsize=(7.2, 4.6))
    ax = fig.add_axes([0.10, 0.18, 0.55, 0.72])
    x = np.arange(4)
    items = [
        ('eq', 'dSOC_0_200', 'Eq. ΔSOC', '#2171b5'),
        ('eq', 'dSIC_0_200', 'Eq. ΔSIC', '#6a51a3'),
        ('eq', 'dTC_0_200', 'Eq. ΔTC', '#7f7f7f'),
        ('tl', 'dSOC_0_200', 'By 2100 ΔSOC', '#9ecae1'),
        ('tl', 'dSIC_0_200', 'By 2100 ΔSIC', '#bcbddc'),
        ('tl', 'dTC_0_200', 'By 2100 ΔTC', '#d9d9d9'),
    ]
    for k, (kind, key, lab, col) in enumerate(items):
        d = [EJ['future'][s][kind][key] for s in SSP4]
        v = [q['mean'] for q in d]
        e = np.array([[q['mean'] - q['p05'], q['p95'] - q['mean']] for q in d]).T
        ax.bar(x - 0.375 + k * 0.15, v, 0.15, color=col, label=lab, yerr=e,
               error_kw=dict(lw=0.5, capsize=1))
    ax.axhline(0, c='k', lw=0.4)
    ax.set_xticks(x); ax.set_xticklabels([LBL[s] for s in SSP4])
    ax.set_ylabel('Change 0–200 cm (Pg C)')
    ax.legend(ncol=3, fontsize=5.5, loc='upper center', bbox_to_anchor=(0.5, 1.14))
    letter_up(fig, ax, 'a', -0.08)
    # callout panel: realized fractions SSP5-8.5
    bx = fig.add_axes([0.72, 0.18, 0.25, 0.72])
    s = '585'
    eq, tl = EJ['future'][s]['eq'], EJ['future'][s]['tl']
    soc_r = 100 * tl['dSOC_0_200']['mean'] / eq['dSOC_0_200']['mean']
    sic_r = 100 * tl['dSIC_0_200']['mean'] / eq['dSIC_0_200']['mean']
    labs = ['SOC\nrealized', 'SIC\nrealized']
    vals = [soc_r, sic_r]
    cols = ['#2171b5', '#6a51a3']
    bars = bx.bar([0, 1], vals, color=cols, width=0.65)
    for i, v in enumerate(vals):
        bx.text(i, v + 2, f'{v:.0f}%', ha='center', fontsize=8, fontweight='bold')
    bx.set_ylim(0, 110); bx.set_xticks([0, 1]); bx.set_xticklabels(labs, fontsize=6)
    bx.set_ylabel('Fraction of equilibrium change\nrealized by 2100 (%)', fontsize=6.5)
    bx.axhline(100, ls=':', c='0.5', lw=0.6)
    # annotation box
    tc_tl = tl['dTC_0_200']['mean']
    bx.text(0.5, -0.22, f"SSP5-8.5 net by 2100:\nΔTC = {tc_tl:.0f} Pg C",
            transform=bx.transAxes, ha='center', fontsize=7, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='#fff7e6', ec='#c0262c', lw=0.8))
    letter_up(fig, bx, 'b', -0.12)
    save(fig, FM + 'Fig_kinetic_decoupling')
    # also keep SI copy polished
    save(fig, FS + 'FigS13_equilibrium_vs_time_limited')  # will fail - fig closed. redo below

def fig5_kinetic_si_copy():
    """Rewrite SI version without the callout (legacy SI stays leaner) — actually keep enhanced as SI too until renumber."""
    # regenerate a lean SI twin is optional; main uses Fig_kinetic_decoupling.png
    pass

# re-open kinetic for SI duplicate with same content (useful as elevated main)
def _save_kinetic_again():
    fig = plt.figure(figsize=(7.2, 4.6))
    ax = fig.add_axes([0.10, 0.18, 0.55, 0.72])
    x = np.arange(4)
    items = [
        ('eq', 'dSOC_0_200', 'Eq. ΔSOC', '#2171b5'),
        ('eq', 'dSIC_0_200', 'Eq. ΔSIC', '#6a51a3'),
        ('eq', 'dTC_0_200', 'Eq. ΔTC', '#7f7f7f'),
        ('tl', 'dSOC_0_200', 'By 2100 ΔSOC', '#9ecae1'),
        ('tl', 'dSIC_0_200', 'By 2100 ΔSIC', '#bcbddc'),
        ('tl', 'dTC_0_200', 'By 2100 ΔTC', '#d9d9d9'),
    ]
    for k, (kind, key, lab, col) in enumerate(items):
        d = [EJ['future'][s][kind][key] for s in SSP4]
        v = [q['mean'] for q in d]
        e = np.array([[q['mean'] - q['p05'], q['p95'] - q['mean']] for q in d]).T
        ax.bar(x - 0.375 + k * 0.15, v, 0.15, color=col, label=lab, yerr=e, error_kw=dict(lw=0.5, capsize=1))
    ax.axhline(0, c='k', lw=0.4); ax.set_xticks(x); ax.set_xticklabels([LBL[s] for s in SSP4])
    ax.set_ylabel('Change 0–200 cm (Pg C)')
    ax.legend(ncol=3, fontsize=5.5, loc='upper center', bbox_to_anchor=(0.5, 1.14))
    letter_up(fig, ax, 'a', -0.08)
    bx = fig.add_axes([0.72, 0.18, 0.25, 0.72])
    s = '585'; eq, tl = EJ['future'][s]['eq'], EJ['future'][s]['tl']
    soc_r = 100 * tl['dSOC_0_200']['mean'] / eq['dSOC_0_200']['mean']
    sic_r = 100 * tl['dSIC_0_200']['mean'] / eq['dSIC_0_200']['mean']
    bx.bar([0, 1], [soc_r, sic_r], color=['#2171b5', '#6a51a3'], width=0.65)
    for i, v in enumerate([soc_r, sic_r]):
        bx.text(i, v + 2, f'{v:.0f}%', ha='center', fontsize=8, fontweight='bold')
    bx.set_ylim(0, 110); bx.set_xticks([0, 1]); bx.set_xticklabels(['SOC\nrealized', 'SIC\nrealized'], fontsize=6)
    bx.set_ylabel('Fraction of equilibrium change\nrealized by 2100 (%)', fontsize=6.5)
    bx.axhline(100, ls=':', c='0.5', lw=0.6)
    tc_tl = tl['dTC_0_200']['mean']
    bx.text(0.5, -0.22, f"SSP5-8.5 net by 2100:\nΔTC = {tc_tl:.0f} Pg C",
            transform=bx.transAxes, ha='center', fontsize=7, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='#fff7e6', ec='#c0262c', lw=0.8))
    letter_up(fig, bx, 'b', -0.12)
    save(fig, FS + 'FigS13_equilibrium_vs_time_limited')

# ============== MAIN FIG 6: N acidification (polish insets) ==============
def fig6_N():
    fig = plt.figure(figsize=(7.2, 5.6))
    a = fig.add_axes([0.07, 0.70, 0.4, 0.25])
    dens(a, [N[f'dph_{s}'][N[f'dph_{s}'] != 0] for s in SSP4], [LBL[s] for s in SSP4],
         [SC4[s] for s in SSP4], 'ΔpH on cropland, 2020–2050')
    a.legend(fontsize=6, loc='upper left'); letter_up(fig, a, 'a', -0.05)
    bins = [-1e4, -10, -5, -2, -1, -0.5, -0.01, 0.01]
    cols = ['#7f0000', '#d7301f', '#fc8d59', '#fdbb84', '#fdd49e', '#fff7ec', '#f7f7f7']
    ax = mapax(fig, [0.0, 0.32, 0.5, 0.32]); classed(ax, N['dSIC_loss_126'], bins, cols, 'continent', 'ΔSIC$_{0–30}$ SSP1-2.6', fig); letter_up(fig, ax, 'c', 0.02)
    ax = mapax(fig, [0.5, 0.32, 0.5, 0.32]); classed(ax, N['dSIC_loss_585'], bins, cols, 'continent', 'ΔSIC$_{0–30}$ SSP5-8.5', fig); letter_up(fig, ax, 'd', 0.02)
    s_, nm, ct = by_country(N['dSIC_loss0200_585'])
    df = pd.DataFrame(dict(n=nm, c=ct, l=-s_))[1:]; t = df.sort_values('l', ascending=False).head(12)[::-1]
    b = fig.add_axes([0.62, 0.70, 0.33, 0.26])
    b.hlines(range(len(t)), 0, t.l * 1000, color='0.4', lw=0.6)
    b.scatter(t.l * 1000, range(len(t)), c=[CCOL.get(c, '0.5') for c in t.c], s=20, edgecolor='k', lw=0.3, zorder=3)
    b.set_yticks(range(len(t))); b.set_yticklabels(t.n, fontsize=5.5)
    b.set_xlabel('SIC loss 0–200 cm, 2020–2050, SSP5-8.5 (Tg C)')
    letter_up(fig, b, 'b', -0.12)
    c = fig.add_axes([0.1, 0.05, 0.85, 0.18]); x = np.arange(4); NN = EJ['N']
    for k, (key, lab, al) in enumerate([('loss_0_30', '0–30 cm', 1.0), ('loss_0_200', '0–200 cm', 0.45)]):
        v = [-NN[s][key]['mean'] for s in SSP4]
        e = np.array([[-NN[s][key]['mean'] + NN[s][key]['p95'], -NN[s][key]['p05'] + NN[s][key]['mean']] for s in SSP4]).T
        c.bar(x + (k - 0.5) * 0.36, v, 0.36, color=[SC4[s] for s in SSP4], alpha=al, yerr=np.abs(e),
              error_kw=dict(lw=0.5, capsize=1.5), label=lab)
        for i, vv in enumerate(v):
            c.text(x[i] + (k - 0.5) * 0.36, vv, f'{vv:.1f}', ha='center', va='bottom', fontsize=5.5, fontweight='bold')
    c.set_xticks(x); c.set_xticklabels([LBL[s] + (' (interp.)' if s == '245' else '') for s in SSP4])
    c.set_ylabel('SIC loss 2020–2050 (Pg C)'); c.legend(fontsize=6)
    letter_up(fig, c, 'e', -0.1)
    save(fig, FM + 'Fig4_N_acidification')

# ============== MAIN FIG 7→6: MAOC/POC without Georgiou comparison ==============
def fig7_maoc():
    fig = plt.figure(figsize=(7.2, 6.4))
    ma, po, f = fr['MA_0_30'], fr['PO_0_30'], fr['f_0_30']
    a = fig.add_axes([0.07, 0.74, 0.40, 0.20])
    dens(a, [ma, po, fr['MA_30_100'], fr['PO_30_100']],
         ['MAOC 0–30', 'POC 0–30', 'MAOC 30–100', 'POC 30–100'],
         ['#2171b5', '#e08214', '#08306b', '#a63603'],
         'log$_{10}$ stock (Mg C ha$^{-1}$)', log=True)
    for l in a.lines[1::2][2:]:
        l.set_ls(':')
    letter_up(fig, a, 'a', -0.05)
    b = fig.add_axes([0.58, 0.74, 0.38, 0.20]); sc_ = FJ['future_0_30']['scen']; x = np.arange(4)
    # Use ensemble means for SSP5 emphasis — show all SSPs eq vs 2100
    for k, (key, lab, col, off) in enumerate([
        ('dMAOC_eq', 'ΔMAOC eq.', '#2171b5', -0.3),
        ('dPOC_eq', 'ΔPOC eq.', '#e08214', -0.1)]):
        v = [sc_[s][key] for s in SSP]
        e = np.array([[sc_[s][key] - sc_[s][key + '_range'][0], sc_[s][key + '_range'][1] - sc_[s][key]] for s in SSP]).T
        b.bar(x + off, v, 0.2, color=col, label=lab, yerr=e, error_kw=dict(lw=0.5, capsize=1.5))
    b.bar(x + 0.1, [sc_[s]['tl_central']['dMAOC'] for s in SSP], 0.2, color='#9ecae1', label='ΔMAOC by 2100')
    b.bar(x + 0.3, [sc_[s]['tl_central']['dPOC'] for s in SSP], 0.2, color='#fdbe85', label='ΔPOC by 2100')
    b.axhline(0, c='k', lw=0.4); b.set_xticks(x)
    b.set_xticklabels(['SSP1-2.6', 'SSP2-4.5', 'SSP3-7.0', 'SSP5-8.5'], fontsize=6)
    b.set_ylabel('Δ stock 0–30 cm (Pg C)'); b.legend(fontsize=5, ncol=2, loc='lower left')
    letter_up(fig, b, 'b', -0.06)
    ax = mapax(fig, [0.0, 0.38, 0.5, 0.30])
    classed(ax, f * 100, [0, 50, 60, 70, 80, 85, 90, 100],
            ['#fdd0a2', '#fdae6b', '#fd8d3c', '#c6dbef', '#6baed6', '#2171b5', '#08306b'],
            'class', 'f$_{MAOC}$ 0–30 (%)', fig); letter_up(fig, ax, 'c', 0.02, -0.02)
    ax = mapax(fig, [0.5, 0.38, 0.5, 0.30])
    classed(ax, ma, [0, 10, 20, 30, 40, 60, 90, 1e4], BLUES, 'continent', 'MAOC$_{0–30}$ (Mg C ha$^{-1}$)', fig)
    letter_up(fig, ax, 'd', 0.02, -0.02)
    # bivariate MAOC/POC full width (no Georgiou panel)
    ax = mapax(fig, [0.05, 0.02, 0.90, 0.32])
    # use distinct but not pink/red confusing for stock medians
    q = bivar_v15(ax, ma, po, np.nanmedian(ma), np.nanmedian(po), ['MAOC', 'POC'],
                  cols={(1, 1): '#3d5a80', (1, 0): '#98c1d9', (0, 1): '#f4a261', (0, 0): '#6d597a'})
    log['fig6_quadrants'] = q[0]
    letter_up(fig, ax, 'e', 0.02, -0.02)
    save(fig, FM + 'Fig6_MAOC_POC')
    # Georgiou comparison → SI
    fig2 = plt.figure(figsize=(3.5, 3.0)); c = fig2.add_axes([0.18, 0.15, 0.75, 0.75])
    G = FJ['Georgiou']; o = FJ
    vals = [[o['_0_30']['MAOC'], o['_30_100']['MAOC']], [G['grid_sum_0_30'], G['grid_sum_30_100']]]
    c.bar([0, 1], [vals[0][0], vals[1][0]], 0.5, color=['#2171b5', '#9ecae1'], label='0–30 cm')
    c.bar([0, 1], [vals[0][1], vals[1][1]], 0.5, bottom=[vals[0][0], vals[1][0]], color=['#08306b', '#4292c6'], label='30–100 cm')
    c.errorbar(0, vals[0][0], yerr=[[vals[0][0] - o['_0_30']['MAOC_CI90'][0]], [o['_0_30']['MAOC_CI90'][1] - vals[0][0]]], c='k', lw=0.6, capsize=2)
    c.axhline(899, ls='--', c='0.4', lw=0.6)
    c.text(1.3, 905, 'Georgiou 2022\n(non-permafrost, 899)', fontsize=5, ha='right', va='bottom')
    c.set_xticks([0, 1]); c.set_xticklabels(['This study', 'Georgiou grid'], fontsize=6)
    c.set_ylabel('Global MAOC (Pg C)'); c.legend(fontsize=5, loc='lower right')
    save(fig2, FS + 'FigS_Georgiou_MAOC_compare')

# ============== country ΔSOC vs ΔSIC scatter (demoted from main Fig5B, with alpha+adjustText) ==============
def figS_country_delta_scatter():
    fig = plt.figure(figsize=(4.5, 4.0)); c = fig.add_axes([0.15, 0.12, 0.80, 0.80])
    a_, b_ = sh['dsoc'], sh['dsic']
    s1, nm, ct = by_country(a_); s2, _, _ = by_country(b_)
    df = pd.DataFrame(dict(n=nm, c=ct, a=s1, b=s2))[1:]
    df = df[(df.c != '') & ((df.a.abs() + df.b.abs()) > 0.05)]
    cols = [BIV_CB[(int(x > 0), int(y > 0))] for x, y in zip(df.a, df.b)]
    c.scatter(df.a, df.b, s=11, c=cols, edgecolor='k', lw=0.15, alpha=0.55, zorder=2)
    c.axhline(0, ls='--', c='0.5', lw=0.6, zorder=1); c.axvline(0, ls='--', c='0.5', lw=0.6, zorder=1)
    c.set_xscale('symlog', linthresh=1); c.set_yscale('symlog', linthresh=1)
    c.set_xticks([-10, -1, 0, 1, 10]); c.set_yticks([-10, -1, 0, 1, 10])
    c.set_xticklabels(['−10', '−1', '0', '1', '10']); c.set_yticklabels(['−10', '−1', '0', '1', '10'])
    short = {'United States of America': 'United States'}
    top = df.reindex(df.a.abs().sort_values().index[-6:])
    texts = []
    for t in top.itertuples():
        texts.append(c.text(t.a, t.b, short.get(t.n, t.n), fontsize=5.5, zorder=5))
    try:
        from adjustText import adjust_text
        adjust_text(texts, ax=c, arrowprops=dict(arrowstyle='-', color='0.45', lw=0.35),
                    force_text=(0.5, 0.7), expand_points=(1.3, 1.4))
    except Exception as e:
        print('adjustText fail', e)
    for (qx, qy), (px, py) in {(1, 1): (0.97, 0.95), (0, 1): (0.03, 0.95), (0, 0): (0.03, 0.05), (1, 0): (0.97, 0.05)}.items():
        n = ((df.a > 0) == qx) & ((df.b > 0) == qy)
        c.text(px, py, f'{n.mean() * 100:.0f}%', transform=c.transAxes,
               ha='right' if qx else 'left', va='top' if qy else 'bottom', fontweight='bold')
    c.set_xlabel('Country ΔSOC (Pg C)'); c.set_ylabel('Country ΔSIC (Pg C)')
    save(fig, FS + 'FigS_country_delta_scatter')

# ============== SI fixes ==============
def S1_split():
    """Split mixed R²/AUC bars into two panels (+ keep fMAOC hexbin)."""
    hp = json.load(open(O7 + '/hp_cv.json'))['results']
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6))
    deps = ['_0_30', '_30_100', '_100_200']; cols = ['#2171b5', '#6a51a3', '#e08214']
    # Panel A: classification AUC
    keys_cls = [('SIC_clf', 'AUC', 'SIC AUC')]
    # also show F1 if present
    for k, d in enumerate(deps):
        r = hp[d].get('SIC_clf') or hp[d].get('SIC', {})
        auc = r.get('AUC', np.nan) if isinstance(r, dict) else np.nan
        f1 = r.get('F1', r.get('f1', np.nan)) if isinstance(r, dict) else np.nan
        ax[0].bar(0 + k * 0.27 - 0.27, auc, 0.27, color=cols[k], label=d[1:].replace('_', '–') + ' cm')
        if np.isfinite(f1):
            ax[0].bar(1 + k * 0.27 - 0.27, f1, 0.27, color=cols[k])
    ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(['SIC AUC', 'SIC F1'])
    ax[0].set_ylabel('Classification score'); ax[0].set_ylim(0, 1); ax[0].legend(fontsize=5.5)
    # Panel B: regression R²
    keys_reg = [('pH', 'r2', 'pH'), ('SIC_amt', 'r2', 'SIC R²'), ('SOC_mineral', 'r2', 'SOC R²'), ('BD', 'r2', 'BD R²')]
    for k, d in enumerate(deps):
        v = []
        for a, b, _ in keys_reg:
            r = hp[d].get(a) or hp[d].get(a.replace('_amt', ''), {})
            v.append(r.get(b, r.get('r2_amt', np.nan)) if isinstance(r, dict) else np.nan)
        ax[1].bar(np.arange(len(keys_reg)) + k * 0.27 - 0.27, v, 0.27, color=cols[k],
                  label=d[1:].replace('_', '–') + ' cm')
    ax[1].set_xticks(range(len(keys_reg))); ax[1].set_xticklabels([k[2] for k in keys_reg])
    ax[1].set_ylabel('Regression R²'); ax[1].set_ylim(0, 1); ax[1].legend(fontsize=5.5)
    # Panel C: fMAOC
    c = FJ['cv']; p = pd.read_csv(O8 + '/fM_cv_points.csv')
    ax[2].hexbin(p.obs, p.cv, gridsize=35, cmap='Blues', mincnt=1, lw=0)
    ax[2].plot([0, 1], [0, 1], 'k--', lw=0.6)
    ax[2].text(0.03, 0.95, f"f$_{{MAOC}}$ n={c['n']}\nR²={c['R2_fMAOC']:.2f} (5×10: {c['R2_5x10_mean']:.2f}±{c['R2_5x10_sd']:.2f})\nRMSE={c['RMSE_fMAOC']:.3f}",
               transform=ax[2].transAxes, va='top', fontsize=6)
    ax[2].set_xlabel('Observed f$_{MAOC}$'); ax[2].set_ylabel('CV predicted')
    for a_, l in zip(ax, 'ABC'):
        a_.text(-0.12, 1.03, l, transform=a_.transAxes, fontsize=9, fontweight='bold')
    fig.tight_layout(); save(fig, FS + 'FigS1_random_CV')

def S14_truncation_note():
    """Present uncertainty hexbin — annotate truncation at 200."""
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6)); L3 = ['_0_30', '_30_100', '_100_200']; x = np.arange(3)
    for k, (v, col) in enumerate([('SOC', '#2171b5'), ('SIC', '#6a51a3')]):
        d = [P[l][v] for l in L3]
        ax[0].bar(x + (k - 0.5) * 0.36, [q['mean'] for q in d], 0.36, color=col, label=v,
                  yerr=np.array([[q['mean'] - q['p05'], q['p95'] - q['mean']] for q in d]).T,
                  error_kw=dict(lw=0.6, capsize=2))
    ax[0].set_xticks(x); ax[0].set_xticklabels(['0–30', '30–100', '100–200'])
    ax[0].set_xlabel('Depth (cm)'); ax[0].set_ylabel('Stock (Pg C, mean, 90% CI)'); ax[0].legend(fontsize=6)
    ax[1].hexbin(EM['p_soc_0_30'], EM['p_soc_0_30_sd'], gridsize=60, bins='log', cmap='Blues', mincnt=1,
                 extent=(0, 200, 0, 40))
    ax[1].set_xlabel('SOC$_{0–30}$ mean (Mg C ha$^{-1}$)'); ax[1].set_ylabel('SD across fold models')
    ax[1].text(0.98, 0.98, 'Display truncated at\nmean = 200 Mg C ha$^{-1}$\n(high-SOC tail)',
               transform=ax[1].transAxes, ha='right', va='top', fontsize=5.5,
               bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='0.5', lw=0.5))
    for a_, l in zip(ax, 'AB'):
        a_.text(-0.12, 1.03, l, transform=a_.transAxes, fontsize=9, fontweight='bold')
    save(fig, FS + 'FigS14_present_uncertainty')

def S5_breakpoints():
    """PDP thresholds with zorder fix (includes fMAOC clay/CEC demoted from main)."""
    ks = list(PD); fig, axs = plt.subplots(3, 4, figsize=(7.2, 5))
    for a, k, l in zip(axs.ravel(), ks, 'ABCDEFGHIJKL'):
        p = PD[k]
        a.axvline(p['breakpoint'], ls='--', c='0.55', lw=0.7, zorder=1)
        a.plot(p['x'], p['y'], c='#c0262c', lw=1.1, zorder=3)
        a.set_title(k.replace('_', ' '), fontsize=6)
        a.text(0.97, 0.92, f"bp={p['breakpoint']:.3g}", transform=a.transAxes, ha='right', fontsize=5.5,
               bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='0.6', lw=0.4), zorder=4)
        a.text(-0.25, 1.05, l, transform=a.transAxes, fontsize=9, fontweight='bold')
    fig.tight_layout(); save(fig, FS + 'FigS5_PDP_thresholds')

def S8_path_keep():
    """Keep path in SI as well (also in main); slight label polish."""
    s = DJ['sem']; fig, ax = plt.subplots(figsize=(5, 3.2)); ax.axis('off')
    Ppos = {'logAI': (0.1, 0.85), 'bio1': (0.1, 0.6), 'clay': (0.1, 0.35), 'carbonate_rock': (0.1, 0.1),
            'pH': (0.5, 0.5), 'lSIC': (0.9, 0.75), 'lSOC': (0.9, 0.25)}
    lab = {'logAI': 'Aridity\n(log P/PET)', 'bio1': 'MAT', 'clay': 'Clay', 'carbonate_rock': 'Carbonate rock',
           'pH': f"pH\nR²={s['pH']['R2']:.2f}", 'lSIC': f"SIC\nR²={s['SIC']['R2']:.2f}",
           'lSOC': f"SOC\nR²={s['SOC']['R2']:.2f}"}
    for k, (x, y) in Ppos.items():
        ax.text(x, y, lab[k], ha='center', va='center',
                bbox=dict(boxstyle='round', fc='#f0f0f0', ec='0.3', lw=0.5), fontsize=6.5)
    for tgt, key in [('pH', 'pH'), ('lSIC', 'SIC'), ('lSOC', 'SOC')]:
        for src, bcoef in s[key].items():
            if src == 'R2' or abs(bcoef) < 0.05:
                continue
            (x0, y0), (x1, y1) = Ppos[src], Ppos[tgt]
            ax.annotate('', xy=(x1 - 0.06, y1), xytext=(x0 + 0.07, y0),
                        arrowprops=dict(arrowstyle='->', color='#c0262c' if bcoef < 0 else '#2171b5',
                                        lw=0.4 + abs(bcoef) * 4))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.03, f'{bcoef:.2f}', fontsize=5.5,
                    color='#c0262c' if bcoef < 0 else '#2171b5', ha='center',
                    bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.9))
    ax.text(0.5, 0.98, f"Standardized path coefficients (n={s['n']}); indirect aridity→pH→SIC = {s['indirect_AI_pH_SIC']:.2f}",
            ha='center', fontsize=6)
    save(fig, FS + 'FigS8_path_analysis')

# Run selected or all
which = sys.argv[1:] if len(sys.argv) > 1 else ['main']
jobs = {
    'fig1': fig1, 'fig2': fig2, 'fig3': fig3_drivers, 'fig4': fig4_eq_tradeoff,
    'fig5': fig5_kinetic, 'fig5si': _save_kinetic_again, 'fig6': fig6_N, 'fig7': fig7_maoc,
    'rings': figS_country_rings, 'cscatter': figS_country_delta_scatter,
    'S1': S1_split, 'S14': S14_truncation_note, 'S5': S5_breakpoints, 'S8': S8_path_keep,
}
if which == ['main']:
    order = ['fig1', 'fig2', 'fig3', 'fig4', 'fig5', 'fig5si', 'fig6', 'fig7', 'rings', 'cscatter', 'S1', 'S14', 'S5', 'S8']
elif which == ['si']:
    order = ['rings', 'cscatter', 'S1', 'S14', 'S5', 'S8', 'fig5si']
else:
    order = which
for n in order:
    F(jobs[n])
json.dump(log, open(R + '/out/v15/fig_numbers_v15.json', 'w'), indent=1, default=float)
print('DONE v15 figs', flush=True)
