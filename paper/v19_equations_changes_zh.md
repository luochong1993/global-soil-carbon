# manuscript_v19_equations_Science 修改说明

## 目的
在不改动科学结论、数字与主图风格的前提下，把主文 Materials and methods summary 中的正式编号公式（原生 Word OMML）恢复为与 v16 一致的 Science 体例。

## 交付文件
- 主文交付：`/workspace/soil_global/paper/manuscript_v19_equations_Science.docx`
- 未覆盖改写：`manuscript_v18_v14style_Science.docx`（仍保留原先仅有残缺 (1)(2) 占位的版本，便于对照）
- SM 未改：`SM_v18_v14style_Science.docx`

## 主文公式恢复（Key equations，编号 1–10）
自 v16 原稿整段拷贝并插入到「Materials and methods summary」正文段落后、「References and Notes」之前；同时删除 v18 中误标为 (1)(2)、实为原 Eq. 6–7 的两处残缺占位。

| 编号 | 内容 |
|------|------|
| (1) | 等面积样条（equal-area spline）层位调和 |
| (2) | 两步（hurdle）SIC 期望含量 + Duan smearing |
| (3) | SOC 层储量公式 |
| (4) | SIC 层储量公式 |
| (5) | 全球面积求和（Pg C） |
| (6) | 平衡态气候驱动 ΔX |
| (7) | 限时一阶动力学 ΔX_TL |
| (8) | ΔpH = −0.06 N_in + 0.11 |
| (9) | 氮致酸化下的 ΔSIC_N |
| (10) | MAOC/POC 分割 |

保留各式前后的 “where …” / “with t = 85 years …” 定义段，以及末句对补充材料 eqs. S1–S57 的指向。

## 正文引用（不增写新主张）
- 动力学段：在 `Δ(t) = Δeq[1 − exp(−t/τ)] … t = 85 years` 后加 **(Eq. 7)**
- 酸化段：在 `ΔpH = −0.06 Nin + 0.11` 后加 **(Eq. 8)**（原有文献引用 (6, 23) 保留）

未改：主图/图注、表格数字、关联≠因果等 caveat、氮与气候分开叙述、τ 为假定等。

## 校验
- 主文 oMath：v18 = 2 → v19 = 10（与 v16 一致）
- SM oMath：57（未改动）
- 无空编号占位（无数学的孤立 “(n)”）
