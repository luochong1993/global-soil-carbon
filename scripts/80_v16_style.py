# v16 layout + sharpness patches on top of v15 style.
# Goals: clear map/density insets from land & curves; separate bivariate insets;
# crisp PDF+PNG at high dpi.
import numpy as np, matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import ListedColormap, BoundaryNorm

# --- sharpness defaults ---
mpl.rcParams.update({
    'savefig.dpi': 600,
    'figure.dpi': 150,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
    'text.antialiased': True,
    'lines.antialiased': True,
    'patch.antialiased': True,
})

# Map insets: upper-left over Arctic / N Pacific (grey / ocean on all stock maps),
# clear of South America west coast that the old SE-Pacific box covered.
INSET_SE = [0.02, 0.66, 0.145, 0.28]
INSET_SE_STACK = [0.02, 0.66, 0.095, 0.28]
# Bivariate: both in upper-left Arctic/N-Pacific (grey/ocean), side-by-side with gap.
INSET_BIV_LEG = [0.015, 0.68, 0.10, 0.24]
INSET_BIV_BAR = [0.145, 0.66, 0.175, 0.28]

REGRID = 2200  # sharper cartopy imshow resampling

def style_inset(ax_inset, face='white', edge='0.35', lw=0.6, z=12):
    ax_inset.set_facecolor(face)
    ax_inset.patch.set_alpha(1.0)
    ax_inset.patch.set_visible(True)
    ax_inset.patch.set_edgecolor(edge)
    ax_inset.patch.set_linewidth(lw)
    ax_inset.set_zorder(z)
    try:
        for sp in ax_inset.spines.values():
            sp.set_visible(True); sp.set_color(edge); sp.set_linewidth(lw); sp.set_zorder(z + 1)
        ax_inset.set_clip_on(True)
        ax_inset.set_axisbelow(False)
    except Exception:
        pass
    try:
        ax_inset.set_navigate(False)
    except Exception:
        pass
    return ax_inset

def _backdrop(ax, rect, pad=(0.010, 0.014), z=11):
    bg = FancyBboxPatch((rect[0] - pad[0], rect[1] - pad[1]),
                        rect[2] + 2 * pad[0], rect[3] + 2 * pad[1],
                        boxstyle='square,pad=0', facecolor='white', edgecolor='0.35',
                        linewidth=0.55, transform=ax.transAxes, zorder=z, clip_on=False)
    ax.add_patch(bg)
    return bg

def classed_v16(ax, v, bins, cols, inset='class', label='', fig=None, cbrect=None,
                fmt='{:g}', extend=True, cats=None, inset_rect=None):
    """classed with Arctic/N-Pacific insets (clear of SA coastline)."""
    cmap = ListedColormap(cols); norm = BoundaryNorm(bins, len(cols), clip=True)
    a = to2d(v)
    ax.imshow(a, origin='upper', extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree(),
              cmap=cmap, norm=norm, interpolation='nearest', zorder=1, regrid_shape=REGRID)
    rect = inset_rect or (INSET_SE_STACK if inset == 'continent' else INSET_SE)
    _backdrop(ax, rect)
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
        # colorbar slightly more to the right so it does not fight left insets
        cr = cbrect or [pos.x0 + pos.width * 0.30, pos.y0 - 0.018, pos.width * 0.55, 0.012]
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

def bivar_v16(ax, x, y, tx, ty, labs, cols=None, fig=None, order=None, names=None, denom_label=None):
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
              interpolation='nearest', zorder=1, regrid_shape=REGRID)
    for rect in (INSET_BIV_LEG, INSET_BIV_BAR):
        _backdrop(ax, rect, pad=(0.008, 0.012))
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

def dens_v16(ax, data, labels, colors, xlabel, log=False, inset=None,
             legend_loc='best', inset_rect=None):
    """Density with inset clear of curves (lower-right) and movable legend."""
    from scipy.stats import gaussian_kde
    for d, l, c in zip(data, labels, colors):
        d = d[np.isfinite(d)]; d = np.log10(d[d > 0]) if log else d
        d = np.random.default_rng(0).choice(d, min(len(d), 40000), replace=False)
        xs = np.linspace(np.percentile(d, 0.5), np.percentile(d, 99.5), 300)
        ax.plot(xs, gaussian_kde(d)(xs), color=c, lw=1.25, label=l)
        ax.axvline(np.median(d), color=c, ls='--', lw=0.8)
    ax.set_xlabel(xlabel); ax.set_ylabel('Probability density'); ax.set_ylim(bottom=0)
    leg_kw = dict(fontsize=6, frameon=True, fancybox=False, edgecolor='0.7', framealpha=0.95,
                  borderpad=0.3, handlelength=1.4, labelspacing=0.25)
    if inset:
        # lower-right: away from modal peaks that sit mid/upper
        rect = inset_rect or [0.60, 0.08, 0.37, 0.48]
        _backdrop(ax, rect, pad=(0.008, 0.010), z=5)
        b = ax.inset_axes(rect); style_inset(b, z=6)
        cats, vals = inset; x = np.arange(len(cats)); wd = 0.8 / len(vals)
        for k, (v, c) in enumerate(zip(vals, colors)):
            b.bar(x + k * wd - 0.4 + wd / 2, v, wd, color=c)
        b.set_xticks(x); b.set_xticklabels(cats, fontsize=5)
        b.tick_params(labelsize=5); b.set_title('Proportion (%)', fontsize=5.5)
        ax.legend(loc=legend_loc if legend_loc != 'best' else 'upper left', **leg_kw)
    else:
        # outside top-left corner of axes so it does not sit on density peaks
        if legend_loc in ('upper left', 'best'):
            ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0),
                      bbox_transform=ax.transAxes, **leg_kw)
        elif legend_loc == 'outside_right':
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0),
                      bbox_transform=ax.transAxes, **leg_kw)
        else:
            ax.legend(loc=legend_loc, **leg_kw)

def save_v16(fig, path, dpi=600):
    """PDF (vector) + high-dpi PNG; no soft downsampling."""
    fig.savefig(path + '.pdf', bbox_inches='tight', dpi=dpi)
    fig.savefig(path + '.png', bbox_inches='tight', dpi=dpi)
    plt.close(fig)

def draw_path_model(axp, s, Ppos=None, lab=None, fontsize=5.5):
    """Draw path diagram with arrows UNDER nodes so the middle (pH) sits on top."""
    axp.axis('off')
    Ppos = Ppos or {'logAI': (0.08, 0.85), 'bio1': (0.08, 0.55), 'clay': (0.08, 0.28),
                    'carbonate_rock': (0.08, 0.05), 'pH': (0.48, 0.48),
                    'lSIC': (0.88, 0.72), 'lSOC': (0.88, 0.22)}
    lab = lab or {'logAI': 'Aridity\n(log P/PET)', 'bio1': 'MAT', 'clay': 'Clay',
                  'carbonate_rock': 'Carb. rock',
                  'pH': f"pH\nR²={s['pH']['R2']:.2f}",
                  'lSIC': f"SIC\nR²={s['SIC']['R2']:.2f}",
                  'lSOC': f"SOC\nR²={s['SOC']['R2']:.2f}"}
    # 1) arrows + coefficient labels first (low zorder)
    for tgt, key in [('pH', 'pH'), ('lSIC', 'SIC'), ('lSOC', 'SOC')]:
        for src, bcoef in s[key].items():
            if src == 'R2' or abs(bcoef) < 0.05:
                continue
            (x0, y0), (x1, y1) = Ppos[src], Ppos[tgt]
            axp.annotate('', xy=(x1 - 0.07, y1), xytext=(x0 + 0.08, y0),
                         arrowprops=dict(arrowstyle='->',
                                         color='#c0262c' if bcoef < 0 else '#2171b5',
                                         lw=0.4 + abs(bcoef) * 4, mutation_scale=8),
                         zorder=1)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 0.04
            axp.text(mx, my, f'{bcoef:.2f}', fontsize=5,
                     color='#c0262c' if bcoef < 0 else '#2171b5',
                     ha='center', zorder=2,
                     bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.9))
    # 2) nodes on top — pH last so middle element is uppermost
    order = ['logAI', 'bio1', 'clay', 'carbonate_rock', 'lSIC', 'lSOC', 'pH']
    for k in order:
        x, y = Ppos[k]
        z = 10 if k == 'pH' else 6
        axp.text(x, y, lab[k], ha='center', va='center', zorder=z, fontsize=fontsize,
                 bbox=dict(boxstyle='round,pad=0.25', fc='#f7f7f7', ec='0.35', lw=0.5,
                           mutation_aspect=0.8))
    axp.text(0.5, 1.02, f"Path model (n={s['n']}); aridity→pH→SIC = {s['indirect_AI_pH_SIC']:.2f}",
             ha='center', fontsize=5.5, transform=axp.transAxes, zorder=5)
