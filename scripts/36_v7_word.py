# Build a Word document with methods summary + key numbers for the user
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json, os, glob
O='/workspace/soil_global/out/v7'; F='/workspace/soil_global/figs/v7_main'
doc=Document()
doc.add_heading('全球土壤有机碳与无机碳：方法、数字与图件（v7 草稿材料）',0)
p=doc.add_paragraph('本文档供 Science 格式论文起草使用。精度以随机交叉验证为主（与 Huang et al. 2024 一致）。完整机器可读数字见 out/v7/paper_numbers_v7.json；方法细则见 methods_notes_v7.md。')

doc.add_heading('1. 相对 v1–v6 的重新分析（不可靠项已重做）',1)
for t in [
 'QC：按 Huang SM 剔除 1970 年前样品、有机/凋落物层、深度不一致与重复层，并输出 qc_flow.json。',
 '深度：等面积样条（Bishop/Malone）统一到 0–30、30–100、100–200 cm。',
 '模型：XGBoost/RF 超参搜索，以随机 10 折 CV 选优（AUC/F1 或 R²/RMSE）。',
 'SOC 高估：有机层 hurdle + PEATMAP 面积锚定 + 0.5° 格子疏化权重；CF 优先 SoilGrids 1 km。',
 '分辨率：目标最终图 30″（≈1 km）。训练在样点；30″ 分块预测（气候用 WorldClim 30″ bio/vsizip；未来用 30″ 现状 + 10′ CMIP6 距平）。若某步未完成 30″，在 paper_numbers 中标明回退到 10′ 及原因。',
 'N 路径：Huang ΔpH=−0.06·Nin+0.11 + 本模型 SIC–pH 有限差分；并给出高 N 敏感性以对照 Huang 的 10–23 Pg。',
 'SOC 未来：平衡态 + 分层一阶周转（文献约束的 τ，标为假设）；不再把临时 τ 当作唯一结论。',
]:
  doc.add_paragraph(t, style='List Number')

doc.add_heading('2. 关键数字',1)
qc=json.load(open(f'{O}/qc_flow.json'))
doc.add_paragraph(f"QC 后剖面数：{qc['profiles_with_any_after_QC']:,}；SOC 0–30 剖面：{qc['profiles_with_SOC_0_30']:,}；SIC 0–30：{qc['profiles_with_SIC_0_30']:,}；pH 0–30：{qc['profiles_with_pH_0_30']:,}。Huang 报告 55,077 剖面 / 223,593 层。")
if os.path.exists(f'{O}/stocks10.json'):
  s=json.load(open(f'{O}/stocks10.json'))
  tot_soc=sum(s[k]['SOC'] for k in s); tot_sic=sum(s[k]['SIC'] for k in s)
  doc.add_paragraph(f"现状储量（10′ 积分，疏化训练）：SOC 0–200 ≈ {tot_soc:.0f} Pg；SIC 0–200 ≈ {tot_sic:.0f} Pg。分层见 JSON。")
if os.path.exists(f'{O}/hp_cv.json') or os.path.exists(f'{O}/hp_cv_checkpoint.json'):
  hp=json.load(open(f'{O}/hp_cv.json' if os.path.exists(f'{O}/hp_cv.json') else f'{O}/hp_cv_checkpoint.json'))
  if '_0_30' in hp.get('results',{}):
    r=hp['results']['_0_30']
    doc.add_paragraph(f"随机 CV（0–30 cm）：pH R²={r.get('pH',{}).get('r2','—')}；SIC AUC={r.get('SIC',{}).get('AUC', r.get('SIC_clf',{}).get('AUC'))}，SIC R²={r.get('SIC',{}).get('r2','—')}；矿质 SOC R²={r.get('SOC_mineral',{}).get('r2','—')}。")

doc.add_heading('3. 主图与支撑图',1)
doc.add_paragraph('主图目录：figs/v7_main/（≥5）；支撑图：figs/v7_SI/（≥6）。图注见 out/v7/figure_captions_v7.md。')
for folder in [F,'/workspace/soil_global/figs/v7_SI']:
  if os.path.isdir(folder):
    for f in sorted(glob.glob(folder+'/*.png')):
      try: doc.add_picture(f, width=Inches(6.3)); doc.add_paragraph(os.path.basename(f))
      except Exception as e: doc.add_paragraph(f'{f}: {e}')

doc.add_heading('4. 仍存局限',1)
for t in ['pH/SIC 随机 R² 仍低于 Huang（协变量与质控、目标定义不同，讨论中如实报告）。','GLOBIOM/INMS 氮情景未获得，用 IMAGE + 高 N 敏感性对照。','30″ 全球制图若未全部写完，以已完成的 COG 瓦片为准并在 JSON 标明。','瞬态 τ 为文献区间假设，非站点 ¹⁴C 逐格标定。']:
  doc.add_paragraph(t, style='List Bullet')

path=f'{O}/v7_methods_and_numbers.docx'
doc.save(path); print('saved',path)
