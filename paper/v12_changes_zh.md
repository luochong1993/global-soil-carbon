# v12 结构调整说明（相对 v11）

构建：`python3 paper/v12/build.py` → `paper/manuscript_v12_Science.docx`、`paper/SM_v12_Science.docx`；PDF 渲染检查：`paper/v12/render_check/`。
原则：**数值、图件文件、公式均未改动**；只重排/改写正文、标题、过渡句，并按代码修正若干方法描述。所有正文数值均可在 v11 正文或 SM 中找到（脚本核对：新增的“数字”仅为引用编号重排）。

## 主线（一句话）
全球土壤碳净变化 = SOC 损失 − SIC 补偿；SOC 损失的性质（快/可逆 vs 慢/承诺性）由 POC/MAOC 决定。

## 引言（4 段，按要求逻辑）
1. 土壤是陆地最大活性碳库 → 全球评估几乎只看 SOC → SIC 在干旱区占主导却常被忽略 → 土壤总碳（TC）在气候变化下的净命运未知 → 需要 SOC+SIC 统一框架。
2. 两库驱动相反：SOC 直接受温度/水分控制；SIC 受干旱度与 pH 控制；氮致酸化溶解碳酸盐 → 提出“此消彼长（trade-off）”与“同降（co-loss）”两种假设，并置于 Köppen 气候带迁移背景下；同时指出 SOC 快、SIC 慢的时间尺度问题。
3. 为什么拆分 SOC：POC 周转快、对气候和投入敏感；MAOC 受矿物保护、稳定；损失落在哪个组分决定可逆性。
4. 本文做法与核算主线（沿用 Huang et al. 框架并扩展）。

## Results 小节（Science 式陈述句标题）
| 顺序 | 新标题 | 内容 | 图 |
|---|---|---|---|
| (i) | Inorganic carbon is a large, deep, and dryland-concentrated share of soil carbon | 数据/模型、CV、现状 TC=4105 Pg（先给总碳再拆 SOC/SIC）、SIC 占 39%、深度分布、国家构成、30″ | Fig. 1, 2 |
| (ii) | Climate controls organic carbon directly but inorganic carbon through soil pH | SHAP（SOC 气候主导，SIC 经 pH）、路径模型 aridity→pH→SIC、非线性阈值 | Fig. 3（原 Fig. 7） |
| (iii) | Organic losses outweigh carbonate gains, leaving a net loss of total soil carbon | 平衡态 SOC −378 / SIC +229 / TC −150；trade-off 69 Mkm²（≈54%）vs 同降 ≈17%；Köppen 迁移；时限响应 TC −180 | Fig. 4（原 Fig. 3）、Fig. 5 |
| (iv) | Nitrogen-driven acidification erodes the carbonate compensation | IMAGE 氮情景 SIC 损失 1.6–2.2 Pg（表层）/13.4–17.4 Pg（0–2 m）；与 2100 年实现的气候 SIC 增益（7 Pg）同量级（明确声明二者不可相加）；与 Huang 差异来源 | Fig. 6（原 Fig. 4） |
| (v) | Particulate carbon carries the near-term organic loss; mineral-associated carbon carries the committed loss | f_MAOC 受质地控制（原在驱动小节，移到此处）、MAOC/POC 库存、平衡 −78/−39 vs 2100 年 −37/−39 | Fig. 7（原 Fig. 6） |
| 讨论 | Net soil carbon change is organic loss minus inorganic compensation | 只看 SOC 高估损失（378 vs 150 Pg）；忽略 SIC 低估风险；MAOC/POC 决定持久性；IPCC 30 cm 深度问题；分区政策：干旱区→控酸化/保 SIC，湿润/寒冷区→维持投入保 POC；局限；结尾回到主线 | — |

## 图序映射（图片文件不变，仅改编号/图注顺序/交叉引用）
新 Fig. 1 = 原 1；新 2 = 原 2；新 3 = 原 7（驱动）；新 4 = 原 3（气候变化）；新 5 = 原 5（双变量）；新 6 = 原 4（氮酸化）；新 7 = 原 6（MAOC/POC）。
已同步：正文图引用（首次引用顺序 1→7）、Fig. 5 图注“as in Fig. 4”、SM 文本 S2（Figs. 4 and 5；Fig. 7；Fig. 6）、SM 公式说明（Fig. 7B）。表 S8 中“Fig. 5A”不变。SM 图 S1–S14 编号不变。

## 按代码修正的方法描述
- **CF**：明确为每层单一值（训练剖面样条协调后 WoSIS 观测的中位数），非逐格网（SM 存量计算段、主文方法摘要与主文公式说明）。
- **SoilGrids 协变量**：不做深度加权，每个属性一张图、三层共用（SM 协变量段、表 S2、主文方法摘要）。
- **协变量数**：代码为 32 个（19 bio + PET + logAI + elev + slope + TPI + clay + sand + silt + CEC + GLiM 类别 + 3 个岩性指示），SIC 模型另加 predicted pH（第 33 个）。原文“33 covariates”已改。
- **CV**（代码核查附带修正）：表 S3 的 CV 指标来自超参数搜索脚本（32_v7_hp_cv.py），该搜索额外使用了 3 个点采样 1 km SoilGrids 100–200 cm 协变量（cfvo、bdod、clay）且未加去聚类权重，并同时比较了随机森林（XGBoost 全部胜出）；已在 SM 中如实说明，并删去“Huang 还比较了 RF”的对比措辞。
- **R² = MEC**：主文 CV 段与方法摘要注明 R² 为模型效率系数（SM 公式说明原已注明）。
- **Lin’s CCC**：v11 正文/SM/表格中经全文检索未发现 CCC 表述，无需删除（SM 图 S1 图片本身未改）。
- **高氮敏感性**：改述为“Huang 损失量 / 本文 IMAGE 损失量”的比值 k_N（约 6–11），未用放大氮输入重跑 SIC 模型；SM 方法、S4、主文 (iv) 均已统一；“three sensitivity analyses”改为“two sensitivity analyses and one diagnostic”。

## 其他
- 标题不变；一句话摘要改为：“Slow carbonate gains offset only part of fast organic carbon losses, so soils lose carbon this century.”
- 结构化摘要与摘要按新逻辑改写，数值不变。
- 参考文献按新引用顺序自动重编号（主文仍 51 条，总 52 条）。
- 字数：主文 4196（v11 4143）；摘要 143；结构化摘要 604（v11 580）。
- 新增的解释性比较（需作者确认）：(iv) 中“2050 年前氮致 0–2 m SIC 损失与 2100 年实现的气候 SIC 增益同量级”，已注明二者来自不同实验、不可相加。
