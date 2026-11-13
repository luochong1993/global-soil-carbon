# v16 修改说明（manuscript_v16_Science.docx / SM_v16_Science.docx）

**仅布局 / 清晰度**；数字与叙事相对 v15 **未改**。主图目录：`figs/v16_main/`（PDF+PNG，≥600 dpi）。

## 逐面板修复（对应用户中文反馈）

### Fig.1（`Fig1_present_stocks`）
| 面板 | 问题 | 处理 |
|---|---|---|
| **A** | 右上 Proportion inset 压密度曲线 | inset 移到 **右下**（白底框），图例留在左上 |
| **B** | 图例压盖 SIC 密度峰 | 图例改到 **轴外左上**（`bbox_to_anchor`），避开右侧主峰 |
| **D** | 洲际 Share inset 太靠左，压南美西岸 | 全局地图 inset 改到 **左上北极/北太平洋**（灰/海区） |
| **F** | 同 D（类别比例 inset 压图） | 同上 |

### Fig.2（`Fig7_drivers`）
| 面板 | 问题 | 处理 |
|---|---|---|
| **B** | 路径图中间（pH）被箭头压住 | **先画箭头再画节点**；pH 最后画、最高 zorder |
| **C/D** | 中间小图（Proportion）太靠左压陆 | 同 Fig.1：inset → 左上北极/洋区 |

### Fig.3（`Fig3_climate_change`）
| 面板 | 问题 | 处理 |
|---|---|---|
| **A** | 右上 Proportion inset 压曲线 | inset → **右下** |
| **C/D** | 小图太靠左 | inset → 左上北极/洋区 |
| **E** | 双变量 2×2 图例与柱状 inset 互相压盖 | 两者并排放在 **左上**，中间留空隙（减小白底 pad） |

### Fig.4（`Fig_kinetic_decoupling`）
| 面板 | 问题 | 处理 |
|---|---|---|
| **B 右下** | 橙色粗边 callout（ΔTC=−180）突兀 | **去掉色块框**，改为轴外一行浅灰说明文字 |

### Fig.5（`Fig4_N_acidification`）
- 无用户点名的遮挡项；本轮仅 **随主图统一 600 dpi 重导出**（地图 inset 位置与 v16 样式一致）。

### Fig.6（`Fig6_MAOC_POC`）
| 面板 | 问题 | 处理 |
|---|---|---|
| **A** | 图例压盖密度曲线 | 图例移到 **轴上方**（ncol=2），避开曲线 |
| **C/D** | 小图太靠左 | inset → 左上北极/洋区 |
| **E** | 两个小图互相压盖 | 与 Fig.3E 相同：左上并排 + 间隙 |

## 清晰度（全部主图 + 触及的 SI）
- `savefig`：**PDF（矢量字体 pdf.fonttype=42）+ PNG @ 600 dpi**，略增大 `figsize`
- 地图 `imshow`：`regrid_shape=2200`，`interpolation='nearest'`（无软下采样）
- 主图像素约 **~4700×3800**（相对 v15 ~2300×1800 约 2×）
- 触及 SI：`FigS14_path_analysis`（路径 zorder）、`FigS26_equilibrium_vs_time_limited`（去掉突兀 callout）已从 `figs/v16_SI_raw/` 覆盖进 `figs/v16_SI/`

## 未改内容
- 所有储量 / Δ / 象限面积 / 断点数值与正文叙事
- 主图 6 张叙事结构与图注文字（仅嵌入新 PNG 路径）

## 重建
```bash
python3 scripts/81_v16_figs.py fig1 fig3 fig4 fig5 fig5si fig6 fig7 S8
cd paper/v16 && V16PASS=1 python3 build.py && V16PASS=2 python3 build.py
```

## 产出
- `figs/v16_main/`
- `paper/manuscript_v16_Science.docx`
- `paper/SM_v16_Science.docx`
- `paper/v16_changes_zh.md`（本文件）
