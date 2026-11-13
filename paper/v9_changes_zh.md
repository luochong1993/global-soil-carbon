# v9 修改说明：从 Huang et al. 2024 *Science* 学到的写法，以及本稿的改动

## 一、从 Huang 等 (2024) 学到的写作要点
1. **标题与摘要**：标题只有一个主张；摘要约 120 词，先写缺口（“仍基本未被量化”），再给 2–3 个带不确定度的头条数字（2305 ± 636 Pg、最多 23 Pg、至少 1.13 ± 0.33 Pg/yr），最后用一句话说明意义。v9 摘要按这个格式改写为 120 词。
2. **引言写法**：先打破常识（SIC 一般被认为是千年尺度、相对惰性的碳库），然后给几条新证据，再说明它为什么要紧（碳收支没有算进去），最后说“这一缺口很紧迫”。v9 引言用同样的逻辑：SOC 与 SIC 对同一气候梯度的响应方向相反，所以单独评估任何一个都会出错。
3. **小标题就是结论**：Huang 的小标题如 “Covariates explain the global SIC distribution”、“Vulnerability of SIC to pH changes”。v9 的每个小标题本身就是一个结论（如 “Slow carbonate kinetics turn an equilibrium balance into a net loss”），每段第一句是论断，后面跟数字和图号。
4. **精度写在括号里**：例如 “[classification: AUC = 0.99, F = 0.95; regression: R² = 0.79 …, 10-fold cross-validation]”。v9 在正文括号中直接给出随机十折的 AUC、F1、R² 和 RMSE，并如实写出与 Huang 的差距及原因。
5. **不确定度写法**：Huang 用 ±1 SD，SM 中写明 STD 由 10 折模型得到、CV 图在 fig. S6。v9 一律用 90% CI（5–95 百分位），并在方法中写清楚它由 bootstrap × GCM（以及 τ）组合得到。
6. **pH–SIC 曲线**：Huang 拟合五参数 sigmoid（x0 = 7.89，7–8.5 之间变化最陡），并按土纲、深度、植被分组讨论（Table S9）。v9 在 SM Text S3 中说明：我们拟合的是“碳酸盐出现概率”的 logistic 曲线（pH₅₀ = 7.10），与 Huang 拟合 pH 对 SIC 含量的 SHAP 贡献互补，并与方解石平衡 pH（约 8.2）相联系。
7. **情景与归因的诚实性**：Huang 说明了没有考虑的过程（植物阳离子吸收、硫沉降、石灰施用、CO₂ 对土壤 pH 的影响），并解释为什么强调 SSP5-8.5。v9 的 SM Text S6 列出 11 条局限，正文最后一段集中写主要 caveat，并说明哪些结论不受影响（符号稳健，量级依赖假设）。
8. **SM 结构**：Materials and Methods（按主题分段，段首加粗）→ Supplementary Text（编号 1–7）→ Figs. S1–S21 → Tables S1–S12（其中 Table S1 是文献对比表，S3 是 CV 指标表，S9 是曲线参数表，S11 是 N 情景损失表）→ References 编号接正文。v9 SM 完全按这一结构编排。
9. **政策含义的写法**：Huang 讨论部分点名 IPCC/GCP “隐含假设 SIC 惰性需修订”，并具体到“氮肥管理、灌溉”。v9 讨论部分分三点：（i）碳酸盐增加不应抵扣 SOC 损失（IPCC/NDC）；（ii）Tier 1 只统计 0–30 cm SOC，只覆盖 34% 的 SOC 和 12% 的 SIC；（iii）氮管理、石灰施用与增强岩石风化同时影响两个碳库。措辞保持克制。

## 二、v9 的主要改动
1. **重写叙事主线**（正文约 4,100 词，v8 正文主体较短且以列表为主）：联合清单 → 干旱度经 pH 控制碳的分配（阈值：P/PET≈0.74、MAP≈457 mm、pH≈6.6、观测 sigmoid pH₅₀=7.10）→ 平衡态 SOC↓≈SIC↑ → 时间受限下转为净损失（SSP5-8.5：−182 Pg，90% CI 119–266）→ POC 在本世纪就兑现损失，MAOC 承担更大的滞后（committed）损失 → 氮酸化结果主要取决于 N 情景（IMAGE 1.8–2.5 Pg；要复现 10–23 Pg，需要把 N 投入放大 9.2–12.7 倍）→ 政策含义与局限。
2. **新增 Science 格式要素**：结构化摘要（INTRODUCTION/RATIONALE/RESULTS/CONCLUSION）、120 词摘要、一句话总结（≤125 字符）、Materials and methods summary、Acknowledgments 占位、Science 风格编号参考文献（只给有把握的真实 DOI，不确定的省略）。
3. **修正图 3/图 5 与头条数字的口径不一致**（这是本次最重要的修正）：
   - 头条（正文、fig. S13、Table S7）用的是 bootstrap(10) × 6 GCM 集合的中位数和 90% CI：SSP5-8.5 ΔSOC −246 (−318 to −157)，ΔSIC +290 (95 to 355)。
   - 图 3/图 5 的地图用的是全数据中心模型的 6-GCM 平均场，全球求和为 ΔSOC −206、ΔSIC +206 Pg（json 中 zone_shift 的 dSOC_total/dSIC_total；中心模型的 GCM 范围为 −175 至 −238），这个结果落在集合 CI 之内。
   - 正文专门写了一段说明，图 3、图 5 的图例和 SM Text S2 都写明了口径。MAOC/POC 的未来变化使用另一套模型、不含有机层、基准期为 1970–2000，因此不能与 ΔSOC 直接相加，这一点也已写明。
4. **修正图 4 的标签错误**（图已重绘，保存在 `figs/v9_main/Fig4_N_acidification.png`，其余 6 张主图从 v8 原样复制）：v8 的面板 e 标为“Topsoil SIC loss”，但数值 13.8/18.1/18.4 实际是 0–200 cm 的 loss-only 合计；面板 b 写的是“by 2100”，实际期间是 2020–2050。新图 e 并列给出 0–30 cm（1.8/2.4/2.5）和 0–200 cm 两组柱，b 的标签改为“0–200 cm, 2020–2050”。脚本为 `scripts/48_v9_fig4_fix.py`。
5. **SM 全面扩充**：14 个方法小节、6 条 Supplementary Text、13 张 SI 图（附详细图例），以及 Table S1–S12（QC 流程、协变量、CV 指标、超参数、储量、文献对比、未来变化、气候带迁移、N 情景、MAOC/POC、驱动归因/阈值/路径系数、组分数据筛选）。所有表格都由 `paper/v9/build.py` 直接从 json 生成，没有手工抄写数字。
6. **数字来源**：全部来自 `out/v8/paper_numbers_v8.json`（v7 json 内容与之相同）。另有两处补充数据：(a) Table S9 中的“施肥+沉降”、净损失（不只计损失）、第 90 百分位 N_in、ΔpH<0 的格点比例，以及 SM Text S4 中 2020–2100 的延伸结果，均取自 `out/v6/N_huang_formula.json`（v8 json 中 N 数字的上游文件）；(b) 正文中的面积比例（表层 SOC 下降的土地面积占 70%/80%，SIC 占 TC>60% 的土地占 26%、<5% 的占 44%）以及区域 SIC 增减格局，是用现有地图（`out/v5/maps_b0.npz`、`out/v6/shift_585.npz`、`out/v7/maps10_*.npz`）直接计算或从图中读取的，没有新建模型。
7. **语言**：去掉 v8 中的“v8 addition”、版本号和内部路径等工作稿痕迹，改为 Science 正文语体；局限集中写，措辞不夸张。

## 三、投稿前仍需作者处理的问题（如实列出）
1. **未来预测的模型版本**：集合预测（bootstrap×GCM）用的是 v5 一代模型（同样的协变量和结构，但早于最终 QC 和去聚类）。正文局限段和 SM 已经如实说明，但最好用 v7 最终模型重新运行。
2. **现状储量没有 CI**：v8 json 只有中心值，建议补 bootstrap，以及 BD/CF/基岩深度的不确定性（Huang 给的是 ±1 SD）。
3. **SIC 总量 1603 Pg 比 Huang 低 30%**，略低于其 ±1 SD 下限；**表层 SOC 偏高 20–25%**（LUCAS 偏差 +28.6 Mg/ha，R² = −0.46）。两点都已写入正文和 SM，审稿人一定会问。
4. **30″ 产品**：气候协变量由 10′ 插值得到；30″ 表层 SIC 比 10′ 低 44%；深层 30″ SOC 积分偏高，未使用。
5. **N 情景**：没有 GLOBIOM/INMS 文件，也没有 IMAGE 的 SSP2-4.5；ΔpH 公式基于中国数据标定，外推到其他地区有风险。
6. **参考文献**：已尽量只保留有把握的 DOI；Kim 2020、Song 2022、Plaza 2018、Lal 1999、IPCC 等条目没有给 DOI，请逐条核对卷期页码和 DOI。
7. **作者、单位、基金、贡献、数据仓库 DOI** 均为占位符。
