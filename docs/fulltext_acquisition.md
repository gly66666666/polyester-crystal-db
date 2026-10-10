# 全文获取清单（人工下载用）

> 生成器：`python -m src.extraction.fetch_pdf --from-gold --check-only --report`
>
> **结论（2026-10-10 实测）**：本课题目标文献绝大多数为订阅制，开放获取(OA)比例约 4–18%，其中**含直链可自动下载 PDF 的仅约 2%**。
> 因此自动抓取无法支撑规模化（P2 需 ≥150 条观测），**必须走学校图书馆订阅 / 馆际互借**，或由你手动下载 PDF 放入 `data/literature/`。
> 放入后抽取流水线会自动优先使用全文（晶胞参数几乎只在全文表里，摘要里没有）。

## PBT

| DOI | 标题 | 状态 | 获取方式 |
|---|---|---|---|
| `10.1002/macp.1985.021860317` | Crystallization behaviour of poly(ethylene terephthalate)  | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1002/pol.1975.180131109` | The crystal structure of poly(tetramethylene terephthalate | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1295/polymj.23.949` | Crystal Structure of Cyclic Dimer of Poly(butylene terepht | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1139/v85-510` | On the structure of poly(tetramethylene terephthalate). St | oa_available | OA 但多为落地页，需浏览器打开 → https://cdnsciencepub.com/doi/pdf/10.1139/v85-510 |
| `10.4028/p-8jeg9d` | Correlation of Wear Behavior of PBT/PC Blend with Crystall | oa_available | OA 但多为落地页，需浏览器打开 → https://doi.org/10.4028/p-8jeg9d |

## PET

| DOI | 标题 | 状态 | 获取方式 |
|---|---|---|---|
| `10.1002/crat.201300369` | Isothermal crystallization behavior and crystal structure  | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1002/polb.21032` | Sequence distribution and crystal structure of poly(ethyle | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1016/0032-3861(88)90201-7` | The crystal modulus and structure of oriented poly(ethylen | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1016/0032-3861(95)91437-c` | Morphology and crystal structure of an a axis oriented, hi | closed | **封闭**：走图书馆订阅 / 馆际互借 |

## PLA

| DOI | 标题 | 状态 | 获取方式 |
|---|---|---|---|
| `10.1021/acs.macromol.7b01468` | Crystal Structure of Poly(lactic acid) Stereocomplex: Rand | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1021/ma001630o` | Crystal Structure of the α-Form of Poly(<scp>l</scp>-lacti | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1021/ma0348674` | Helix Distortion and Crystal Structure of the α-Form of Po | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1080/00222349108245788` | Crystal structure of stereocomplex of poly(L-lactide) and  | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1016/j.polymer.2019.05.020` | Crystal structure and unique lamellar thickening for poly( | oa_available | OA 但多为落地页，需浏览器打开 → https://doi.org/10.1016/j.polymer.2019.05.020 |

## PTT

| DOI | 标题 | 状态 | 获取方式 |
|---|---|---|---|
| `10.1016/0032-3861(79)90064-8` | The crystal structure of poly(trimethylene terephthalate)  | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1016/j.polymer.2005.04.030` | Sequence distribution and crystal structure of poly(ethyle | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.1021/ma000210w` | Crystal Structure and Banded Spherulite of Poly(trimethyle | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.58837/chula.the.2003.1976` | Shear-induced crystallization in poly (trimethylene tereph | closed | **封闭**：走图书馆订阅 / 馆际互借 |
| `10.58837/chula.the.2004.2118` | Crystallization kinetics of poly(trimethylene terephthalat | closed | **封闭**：走图书馆订阅 / 馆际互借 |

## 下载后怎么用

1. 把 PDF 命名为 `<DOI 中的 / 替换为 _>.pdf`，放入 `data/literature/`；
   （脚本 `corpus.pdf_path_for()` 用的就是这个命名规则，`fetch_pdf --download` 已自动处理）
2. 直接跑抽取流水线即可自动优先使用全文：
   `python -m src.extraction.pipeline --backend tokenplan --polymers PET --limit 20`
3. PDF 已被 `.gitignore` 排除，**不会**进入 GitHub 仓库（版权合规）。
