# v15 修改说明（manuscript_v15_Science.docx / SM_v15_Science.docx）

所有数字仍来自 out/v10、out/v8、out/v13、out/v14/direction_v14.json（已复制到 out/v15），**没有新编数字**。

## 我对审稿式图评的评估原则
- **有利于清晰度 / Science 适配的改**：做。
- **仅换顺序、不增强论证的改**：不做或只做轻量。
- Science Research Article 目标主图 **6 张**；当前 v14 为 7 张，且核心“2100 动力学脱耦”埋在 SI。

---

## A. 已采纳的高价值改动

### A1 地图 inset 压盖（全面）
- 统一把 classed / bivariate inset 挪到地图左下偏 SE Pacific 死角，并加 **不透明白底 + 细边框**（`scripts/80_v15_style.py`）。
- 色条位置略右移，减少与 inset 争位。
- 影响主图地图面板（Fig.1 C–F、Fig.3 C–E、Fig.5 C–D、Fig.6 C–E）及同类 SI 地图。

### A2 散点过密与标签（Fig.2C → SI；旧 Fig.5B → SI）
- 国家散点改 **alpha≈0.55**；ΔSOC–ΔSIC 国家散点用 **adjustText** 避让（`FigS26`）。
- 主文不再放国家级散点主图，避免与全球格局争视觉权重。

### A3 双变量色盘（色盲友好）
- 旧粉红(trade-off)/红(co-loss) 易混。
- 新盘：**橙 = SOC↓SIC↑（权衡）**，**mauve = 同减**，**蓝 = 同增**，**浅蓝 = SOC↑SIC↓**。
- 主图 Fig.3E 与 SI 国家散点一致。

### A4 断点竖线与标签（主图 Fig.2E/F；SI PDP）
- 竖虚线 **zorder 低于曲线**；数值标签移到 **轴上方白底框**，避免贴在上升沿上。

### A5 SI 具体缺陷
| 项目 | 处理 |
|---|---|
| 原 S2 式 R²/AUC 混排 | `FigS1_random_CV` 拆成 **分类 AUC/F1** 与 **回归 R²** 两栏 + fMAOC hexbin |
| S3B/uncertainty 截断 | `FigS14` B 面板注明 **mean=200 处显示截断** |
| 纬度剖面 MAOC/POC 缠绕 | `FigS16` 加粗线宽 + `fill_betweenx` |
| GCM 近绿难辨 | `FigS18`：**形状+高对比色**（圆/方/三角/菱/倒三角/十字） |
| Sankey 字太细 | `FigS21` 节点标签加粗加大，流线略加粗 |

### A6 叙事主图重组 → **6 主图**（评估后采纳）

| 新主图 | 内容 | 相对 v14 |
|---|---|---|
| **Fig.1** | 现状储量与深度不对称（密度+地图） | 保留；视觉抛光 |
| **Fig.2** | 驱动力 + **路径模型** + SIC 断点 | 原 Fig.3；**提升原 S12/S8 路径图**；fMAOC PDP G/H 下沉 SI |
| **Fig.3** | 平衡态响应 + 权衡双变量 + 洲际柱 | **合并**原 Fig.4+5（去掉冗余 SSP1 顶土图与国家散点） |
| **Fig.4** | **动力学脱耦**：平衡态 vs 2100 实现（SOC≈50%，SIC≈3%，净 −180） | **新主图**（自原 S13/S15 提升并加 callout） |
| **Fig.5** | 氮酸化 SIC 损失 | 原 Fig.6；inset 抛光 |
| **Fig.6** | MAOC vs POC（无 Georgiou 对比柱） | 原 Fig.7；**7F → SI Fig.S24** |

**有意不做的叙事建议：**
- **不把 Fig.1 与国家排行硬并成一张超载大图**：六面板储量图已满，再塞 SIC/TC 地图+国家环会损清晰度；改为把原 Fig.2（SIC 地理/国家）整体下沉 SI（S23/S25）。
- **不把氮酸化并入动力学图**：机制与时间尺度不同，合并只会挤。
- **保留路径图在 SI 一份副本**（S8），便于 Methods 单独引用。

---

## B. 文稿与编号
- 正文/图注/交叉引用已改为 6 主图叙事；路径模型改为 Fig.2B；动力学改为 Fig.4；Georgiou/国家地理改引 SI。
- SI 按首次引用两遍构建重编号 → `figs/v15_SI/`（现 **S1–S26**）。
- 摘要数字未改（仍为 v14 方向总表）。
- 正文词数仍约 **5187**（v14 已超 Science ~4500；本轮未做删减，需作者另轮压缩）。

## C. 重建命令
```bash
python3 scripts/81_v15_figs.py main          # 或分 fig1..fig7 / SI 子命令
python3 scripts/82_v15_si_extra.py           # S16/S18/S21
cd paper/v15 && V15PASS=1 python3 build.py && V15PASS=2 python3 build.py
```

## D. 产出路径
- `paper/manuscript_v15_Science.docx`
- `paper/SM_v15_Science.docx`
- `figs/v15_main/`（6 主图文件 + 中间产物）
- `figs/v15_SI/`（按引用序重编号）、`figs/v15_SI_raw/`
- `paper/v15/` 构建源；`paper/v15_changes_zh.md`（本文件）

## E. 仍建议作者目视的残留点
1. 部分 Robinson 投影下 inset 仍贴近南美西岸——已白底框，但若排版缩到单栏可再外移到图框外。
2. 路径图（Fig.2B）系数标签在箭头交叉处仍略挤（已加白底）；若审稿再挑可改为表列系数。
3. 断点竖线在极陡上升沿处视觉上仍可能“穿过”曲线（zorder 已低于曲线）；可接受。
4. 篇幅超限未在本轮处理。

## F. 末轮微调（相对上文）
- Fig.3E 双变量图例与柱状 inset 下移并拉开间距，减少互相压盖。
- SI `FigS1`/`S14`/`S16`/`S18`/`S21` 在被 v14 拷贝覆盖后已重新 overlay。
