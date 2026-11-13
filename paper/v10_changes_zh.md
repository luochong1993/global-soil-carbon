# v10 修改说明（相对 v9）

## 一、数字更新（全部来自 `out/v10/paper_numbers_v10.json` / `KEY_NUMBERS_v10.json`，未编造）

### 现状储量（均值；90% CI；±1 SD，Huang 风格）
| 库 | v9 | v10 |
|---|---|---|
| SOC 0–30 | 858（无 CI） | **848 (774–924; ±46)** |
| SIC 0–30 | 185 | **178 (163–194; ±9)** |
| MAOC 0–30 | 525 (508–538) | **518 (473–565; ±28)** |
| POC 0–30 | 187 (173–203) | **183 (163–205; ±13)** |
| SOC 0–200 | 2492 | **2506 (2263–2761; ±151)** |
| SIC 0–200 | 1603 | **1598 (1408–1801; ±119)** |
| TC 0–200 | 4095 | **4105 (3675–4549; ±265)** |
| MAOC 0–100 | 1063 | **1048 (946–1152; ±62)** |
| 有机层 SOC | 357 | **361**（三层 146/102/113） |

SIC 仍低于 Huang 的 2305 ± 636（约低 30%）；新 CI 上界 1801 与 Huang ±1 SD 的下半段重叠。

### 气候未来（最终模型；10 fold × 6 GCM；地图=集合均值=头条均值）
| SSP5-8.5 | v9（v5 头条） | v10 |
|---|---|---|
| Eq ΔSOC 0–200 | −246 (−318 to −157) | **−378 (−526 to −254)** |
| Eq ΔSIC | +290 (95–355) | **+229 (130–382)** |
| Eq ΔTC | ~+25（与零无异） | **−150 (−245 to −41)** |
| TL ΔTC | −182 (119–266) | **−180 (−282 to −100)** |
| 权衡区面积 | 57 Mkm²（v6 地图） | **69 Mkm²** |
| MAOC/POC eq（0–30） | −111 / −38 | **−78 / −39** |
| MAOC/POC by-2100 | 视 τ 中心约 −46 / −38 | **−37 / −39** |

其它 SSP 的 Eq ΔSOC：−129 / −217 / −311（1-2.6 / 2-4.5 / 3-7.0）。

### 氮酸化（2020–2050，IMAGE；GLOBIOM 仍未取得）
表层 loss-only：**1.6 / 1.8 / 2.1 / 2.2 Pg**（SSP1-2.6 / 2-4.5 / 3-7.0 / 5-8.5）。  
0–200 cm：13.4 / 15.1 / 17.2 / 17.4。  
**SSP2-4.5 = mean(SSP1-2.6, SSP3-7.0) 插值**，文中已写明。相对 Huang 10/14/23 Pg 的简单比值约 6–11×。

### LUCAS 偏差
深度对齐前 +28.6 Mg/ha（R²=−0.46）；**对齐后 +6.9 Mg/ha（R²≈0.02）**。只报告，**不做全球 rescale**。耕地比例协变量经 CV 检验未采用。

## 二、叙事与口径改写
1. **删除「地图与头条口径不一致」**：v9 专门有一段说明 Fig.3/5 用中心模型（−206/+206）而头条用 v5 bootstrap（−246/+290）。v10 改为统一表述：*同一* 10 fold×6 GCM 集合；地图为集合均值，积分等于头条均值（已核对 SSP5-8.5：−378/+229）。SM Text S2 标题改为 “Unified map–headline accounting”。
2. **平衡态不再写成「净变与零无异」**：Eq ΔTC 在 SSP5-8.5 为 −150，头条与结论改为「SIC 增益只部分抵消 SOC 损失」。
3. **局限段软化/更新**：未来已在最终模型上；现状已有 CI；GLOBIOM 仍缺（IMAGE + SSP2-4.5 插值）；SIC 低于 Huang 但 CI 重叠；SOC 偏差经深度对齐后下降。
4. **主图/SM 图**：嵌入 `figs/v10_main/`（7）与 `figs/v10_SI/`（14，含新 Fig. S14 现状不确定度）。

## 三、参考文献核对（WebSearch）
已核实并补 DOI：Huang 2024 (*Science* 384:233–239, doi:10.1126/science.adi7918)；Kim 2020 (doi:10.1111/gcb.15207)；Song 2022 (doi:10.1093/nsr/nwab120)；Plaza 2018 (doi:10.1038/s41598-018-32229-0)；Batjes 1996、Georgiou 2022、Beck 2023、Zamanian 2018、Lavallee 2020、SoilGrids/Poggio 2021、PEATMAP/Xu 2018、Bishop 1999、Malone 2009 等与 v9 一致且 DOI 正确。  
**仍无 DOI / 需作者再核**：Lal 1999（编著）、Schlesinger 1982、IPCC 2006/2019 指南、Canadell AR6 章、Stehfest IMAGE 报告、Lundberg NIPS 2017。  
**需注意**：文中「Plaza 1558 Pg（全球 0–200 SIC）」沿用 Huang 表与 v9；Plaza 原文摘要侧重旱地（旱地 SIC 0–2 m 约 1237 Pg），全球 1558 的归属请作者对照 Huang Table S1 再确认。

## 四、交付文件
- `/workspace/soil_global/paper/manuscript_v10_Science.docx`
- `/workspace/soil_global/paper/SM_v10_Science.docx`
- `/workspace/soil_global/paper/v10_changes_zh.md`（本文件）
- 构建脚本：`paper/v10/{build,main_text,sm_text,refs}.py`

## 五、字数与诚实缺口
| 项 | 词数 |
|---|---|
| 正文 Main Text | **4143**（目标 4000–5000） |
| 结构化摘要 | 580 |
| 短摘要 | 144 |
| Methods summary | 261 |
| 图注合计 | 1290 |
| 正文引用 | 51；全文引用 52 |

**投稿前仍需作者处理：**
1. 作者/单位/基金/贡献/数据仓库 DOI 仍为占位符。
2. GLOBIOM/INMS 网格仍未取得；N 结果仅 IMAGE + SSP2-4.5 插值。
3. Plaza 1558 Pg 全球归属建议再核；无 DOI 条目（Lal 1999、Schlesinger 1982、IPCC 等）请补全。
4. 30″ 深层 SOC 积分仍属临时产品；亚表层 MAOC 仅 34 条记录。
5. τ 与 Monte Carlo 扰动范围为假设，文中已标明。
6. Fig. 4 国家排名等空间细节仍基于 IMAGE 驱动场；若重跑 N 地图需与 v10 表层 1.6–2.2 头条一致（当前 Fig.4 已换 v10 图）。
