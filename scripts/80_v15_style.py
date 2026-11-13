# v15 style patches: opaque map insets in SE-Pacific dead zone; colorblind bivariate;
# breakpoint helpers; scatter with alpha + adjustText.
import numpy as np, matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import ListedColormap, BoundaryNorm

# Colorblind-safe 2x2 for ΔSOC × ΔSIC (trade-off vs co-loss distinct):
# (SOC+,SIC+) both gain = blue-purple; (SOC+,SIC-) = teal;
# (SOC-,SIC+) trade-off = orange; (SOC-,SIC-) co-loss = dark purple-brown.
BIV_CB = {
    (1, 1): '#3b4994',  # both gain — blue-purple
    (1, 0): '#5e4fa2',  # SOC+ SIC− — violet (was teal; keep distinct)
    (0, 1): '#fdae61',  # trade-off SOC− SIC+ — orange/yellow
    (0, 0): '#5e4c6d',  # co-loss — dark mauve (not red/pink)
}
# Even clearer Science-style pair: orange for SOC↓, blue for SIC↑
BIV_CB = {
    (0, 1): '#f4a261',  # trade-off: SOC− SIC+  orange
    (0, 0): '#6d597a',  # co-loss:   SOC− SIC−  purple-grey
    (1, 1): '#3d5a80',  # both gain: SOC+ SIC+  blue
    (1, 0): '#98c1d9',  # SOC+ SIC−              light blue
}

def style_inset(ax_inset, face='white', edge='0.35', lw=0.6, z=12):
    """Force opaque white inset background with thin border."""
    ax_inset.set_facecolor(face)
    ax_inset.patch.set_alpha(1.0)
    ax_inset.patch.set_visible(True)
    ax_inset.patch.set_edgecolor(edge)
    ax_inset.patch.set_linewidth(lw)
    ax_inset.set_zorder(z)
    # Draw an explicit opaque frame rectangle in the parent axes as a backdrop
    # (cartopy parents can leave the inset patch semi-see-through).
    try:
        parent = ax_inset.axes if False else ax_inset
        # ensure spines visible
        for sp in ax_inset.spines.values():
            sp.set_visible(True); sp.set_color(edge); sp.set_linewidth(lw); sp.set_zorder(z+1)
        # clip artists to axes box so bars don't spill
        ax_inset.set_clip_on(True)
        # raise the whole axes above the map
        ax_inset.set_axisbelow(False)
    except Exception:
        pass
    try:
        ax_inset.set_navigate(False)
    except Exception:
        pass
    return ax_inset

# Preferred inset rects in axes fraction — SE Pacific / outside southern ocean,
# clear of colorbar (colorbar sits ~y=-0.015 below map).
INSET_SE = [0.015, 0.28, 0.13, 0.28]       # class proportion bars
INSET_SE_STACK = [0.015, 0.28, 0.08, 0.28] # continental stacked share
INSET_BIV_LEG = [0.02, 0.08, 0.09, 0.18]
INSET_BIV_BAR = [0.14, 0.08, 0.16, 0.22]

def classed_v15(ax, v, bins, cols, inset='class', label='', fig=None, cbrect=None, fmt='{:g}', extend=True, cats=None):
    """Drop-in replacement for classed() with opaque SE-Pacific insets."""
    cmap = ListedColormap(cols); norm = BoundaryNorm(bins, len(cols), clip=True)
    a = to2d(v)
    ax.imshow(a, origin='upper', extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree(),
              cmap=cmap, norm=norm, interpolation='nearest', zorder=1, regrid_shape=1400)
    rect = INSET_SE_STACK if inset == 'continent' else INSET_SE
    # Opaque backdrop in parent axes (axes-fraction coords)
    from matplotlib.patches import FancyBboxPatch
    bg = FancyBboxPatch((rect[0]-0.012, rect[1]-0.018), rect[2]+0.024, rect[3]+0.036,
                        boxstyle='square,pad=0', facecolor='white', edgecolor='0.35',
                        linewidth=0.6, transform=ax.transAxes, zorder=11, clip_on=False)
    ax.add_patch(bg)
    b = ax.inset_axes(rect)
    style_inset(b)
    if inset == 'class':
        k = np.digitize(v, bins[1:-1]); ok = np.isfinite(v)
        p = [area[ok & (k == i)].sum() / area[ok].sum() * 100 for i in range(len(cols))]
        b.bar(range(len(cols)), p, color=cols, width=0.8, edgecolor='none')
        b.set_xticks([]); b.set_ylabel('Proportion (%)', fontsize=5)
    else:
        sh = cont_share(v); bot = 0
        for c in CONT:
            b.bar(0, sh[c], bottom=bot, color=CCOL[c], width=0.6, edgecolor='white', lw=0.3)
            if sh[c] > 4:
                b.text(0.42, bot + sh[c] / 2, c, fontsize=4.5, va='center')
            bot += sh[c]
        b.set_xlim(-0.5, 1); b.set_xticks([]); b.set_ylabel('Share (%)', fontsize=5)
    b.tick_params(labelsize=5); b.set_ylim(bottom=0)
    if fig is not None:
        pos = ax.get_position()
        cr = cbrect or [pos.x0 + pos.width * 0.28, pos.y0 - 0.018, pos.width * 0.55, 0.012]
        c = fig.add_axes(cr); n = len(cols)
        for i, col in enumerate(cols):
            c.add_patch(Rectangle((i, 0), 1, 1, color=col))
        c.add_patch(Rectangle((n + 0.35, 0), 1, 1, color=GREY))
        c.text(n + 1.5, 0.5, 'Not applied', va='center', fontsize=6)
        c.set_xlim(0, n + 1.4); c.set_ylim(0, 1); c.set_yticks([])
        if cats:
            c.set_xticks(np.arange(n) + 0.5); c.set_xticklabels(cats, fontsize=5)
        else:
            c.set_xticks(range(1, n)); c.set_xticklabels([fmt.format(x) for x in bins[1:-1]], fontsize=5.5)
        for s in c.spines.values():
            s.set_visible(False)
        c.tick_params(length=0, pad=1)
        c.text(-0.3, 0.5, label, ha='right', va='center', fontsize=6.5)

def bivar_v15(ax, x, y, tx, ty, labs, cols=None, fig=None, order=None, names=None, denom_label=None):
    cols = cols or BIV_CB
    ok = np.isfinite(x) & np.isfinite(y)
    q = np.full(len(x), -1)
    for (i, j), _ in cols.items():
        q[ok & ((x > tx) == bool(i)) & ((y > ty) == bool(j))] = i * 2 + j
    rgb = np.full((len(x), 4), np.nan)
    for (i, j), c in cols.items():
        rgb[q == i * 2 + j] = mpl.colors.to_rgba(c)
    img = np.zeros((H, W, 4))
    for k in range(4):
        img[..., k][mask] = np.nan_to_num(rgb[:, k])
    ax.imshow(img, origin='upper', extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree(),
              interpolation='nearest', zorder=1, regrid_shape=1400)
    from matplotlib.patches import FancyBboxPatch as _FBP
    for rect in (INSET_BIV_LEG, INSET_BIV_BAR):
        bg = _FBP((rect[0]-0.012, rect[1]-0.018), rect[2]+0.024, rect[3]+0.036,
                  boxstyle='square,pad=0', facecolor='white', edgecolor='0.35',
                  linewidth=0.6, transform=ax.transAxes, zorder=11, clip_on=False)
        ax.add_patch(bg)
    L = ax.inset_axes(INSET_BIV_LEG); style_inset(L)
    for (i, j), c in cols.items():
        L.add_patch(Rectangle((i, j), 1, 1, color=c))
    L.set_xlim(0, 2); L.set_ylim(0, 2)
    L.set_xticks([0.5, 1.5]); L.set_yticks([0.5, 1.5])
    L.set_xticklabels(['−', '+'], fontsize=5); L.set_yticklabels(['−', '+'], fontsize=5)
    L.set_xlabel(labs[0], fontsize=5, labelpad=0); L.set_ylabel(labs[1], fontsize=5, labelpad=0)
    L.tick_params(length=0, pad=1)
    order = order or [(0, 1), (0, 0), (1, 1), (1, 0)]
    tot = area[q >= 0].sum()
    p = [area[q == i * 2 + j].sum() / tot * 100 for (i, j) in order]
    B = ax.inset_axes(INSET_BIV_BAR); style_inset(B)
    B.bar(range(4), p, color=[cols[o] for o in order], width=0.75)
    for k, v in enumerate(p):
        B.text(k, v + 1, f'{v:.0f}', ha='center', fontsize=5, fontweight='bold')
    if names:
        B.set_xticks(range(4)); B.set_xticklabels(names, fontsize=4.0)
        B.tick_params(axis='x', length=0, pad=1)
    else:
        B.set_xticks([])
    ylab = denom_label or 'Area (%)'
    B.set_ylabel(ylab, fontsize=4.8); B.tick_params(labelsize=5)
    B.set_ylim(0, max(p) * 1.22)
    return dict(zip([f'{i}{j}' for (i, j) in order], p)), tot

def breakpoint_panel(ax, x, y, bp, col, xlabel, ylabel, fmt='{:.2g}'):
    """Plot PDP with dashed breakpoint UNDER the curve; label in white box above."""
    ax.axvline(bp, ls='--', c='0.55', lw=0.7, zorder=1)
    ax.plot(x, y, c=col, lw=1.3, zorder=3)
    ymin, ymax = ax.get_ylim()
    # place label just below top spine in a white box
    ax.text(bp, ymax - 0.02 * (ymax - ymin) if ymax > ymin else ymax,
            f' {fmt.format(bp)} ', fontsize=5.5, va='top', ha='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='0.6', lw=0.4),
            zorder=4, clip_on=False)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)

def scatter_alpha_label(ax, xs, ys, colors, labels=None, label_xy=None, s=9, alpha=0.55, edge=True):
    """Semi-transparent scatter; optional adjustText labels for a subset."""
    kw = dict(s=s, c=colors, alpha=alpha, lw=0.2 if edge else 0, zorder=2)
    if edge:
        kw['edgecolor'] = 'k'
    ax.scatter(xs, ys, **kw)
    if labels is not None and len(labels):
        texts = []
        for (x, y, lab) in zip(label_xy[0], label_xy[1], labels):
            texts.append(ax.text(x, y, lab, fontsize=4.8, zorder=5))
        try:
            from adjustText import adjust_text
            adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='0.5', lw=0.3),
                        force_text=(0.4, 0.6), force_points=(0.3, 0.4),
                        expand_text=(1.1, 1.2), expand_points=(1.2, 1.3))
        except Exception:
            pass
