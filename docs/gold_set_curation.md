# Gold Set 人工标注工作表

> 生成器：`src/annotation/shortlist.py`（自动重跑可刷新候选）
> **数值必须由人打开原文逐条核验后填写**——本表只给书目线索，不含任何晶胞/热力学数值。
> 合规红线：每条须挂单一 DOI；只记数值性事实 + 表/图号；禁止插值或推测。

## 填写字段清单（每个槽位）

| 分组 | 字段 | 单位 |
|---|---|---|
| 晶型 | polymorph_label, crystal_system, space_group, chain_conformation | — |
| 晶胞 | a, b, c | Å |
| 晶系角 | alpha, beta, gamma | ° |
| 其它结构 | z, rho_crystal, fiber_period | 个 / g·cm⁻³ / Å |
| 热历史 | t_c | °C |
| 热力学 | tm, tm0, delta_hf, tg | °C / °C / J·g⁻¹ / °C |
| 其它 | xtallinity_pct, growth_rate | % / nm·s⁻¹ |
| 溯源 | doi, ref_year, ref_source, ref_table(表/图号), confidence, annotator | — |

## PET（候选 5 篇）

| 槽位 | 分数 | 年份 | 期刊 | 标题 | DOI |
|---|---|---|---|---|---|
| PET-001 | 26 | 2014 | Crystal Research and Technology | Isothermal crystallization behavior and crystal structure of poly(ethy | `10.1002/crat.201300369` |
| PET-002 | 19 | 2007 | Journal of Polymer Science Part B: Polymer Physics | Sequence distribution and crystal structure of poly(ethylene/butylene  | `10.1002/polb.21032` |
| PET-003 | 10 | 1995 | Polymer | Morphology and crystal structure of an a axis oriented, highly crystal | `10.1016/0032-3861(95)91437-c` |
| PET-004 | 10 | 2005 | Polymer | Sequence distribution and crystal structure of poly(ethylene/trimethyl | `10.1016/j.polymer.2005.04.030` |
| PET-005 | 2 | 1988 | Polymer | The crystal modulus and structure of oriented poly(ethylene terephthal | `10.1016/0032-3861(88)90201-7` |

## PTT（候选 5 篇）

| 槽位 | 分数 | 年份 | 期刊 | 标题 | DOI |
|---|---|---|---|---|---|
| PTT-001 | 20 | 1979 | Polymer | The crystal structure of poly(trimethylene terephthalate) by X-ray and | `10.1016/0032-3861(79)90064-8` |
| PTT-002 | 10 | 2000 | Macromolecules | Crystal Structure and Banded Spherulite of Poly(trimethylene terephtha | `10.1021/ma000210w` |
| PTT-003 | 10 | 2005 | Polymer | Sequence distribution and crystal structure of poly(ethylene/trimethyl | `10.1016/j.polymer.2005.04.030` |
| PTT-004 | 7 | ? | ? | Shear-induced crystallization in poly (trimethylene terephthalate) | `10.58837/chula.the.2003.1976` |
| PTT-005 | 7 | ? | ? | Crystallization kinetics of poly(trimethylene terephthalate) : macrosc | `10.58837/chula.the.2004.2118` |

## PBT（候选 5 篇）

| 槽位 | 分数 | 年份 | 期刊 | 标题 | DOI |
|---|---|---|---|---|---|
| PBT-001 | 26 | 1975 | Journal of Polymer Science: Polymer Physics Edition | The crystal structure of poly(tetramethylene terephthalate) | `10.1002/pol.1975.180131109` |
| PBT-002 | 17 | 1985 | Canadian Journal of Chemistry | On the structure of poly(tetramethylene terephthalate). Structural, in | `10.1139/v85-510` |
| PBT-003 | 12 | 2024 | Materials Science Forum | Correlation of Wear Behavior of PBT/PC Blend with Crystallographic Str | `10.4028/p-8jeg9d` |
| PBT-004 | 10 | 1991 | Polymer Journal | Crystal Structure of Cyclic Dimer of Poly(butylene terephthalate) | `10.1295/polymj.23.949` |
| PBT-005 | 5 | 1985 | Die Makromolekulare Chemie | Crystallization behaviour of poly(ethylene terephthalate) and poly(tet | `10.1002/macp.1985.021860317` |

## PLA（候选 5 篇）

| 槽位 | 分数 | 年份 | 期刊 | 标题 | DOI |
|---|---|---|---|---|---|
| PLA-001 | 14 | 2017 | Macromolecules | Crystal Structure of Poly(lactic acid) Stereocomplex: Random Packing M | `10.1021/acs.macromol.7b01468` |
| PLA-002 | 14 | 2019 | Polymer | Crystal structure and unique lamellar thickening for poly(l-lactide) i | `10.1016/j.polymer.2019.05.020` |
| PLA-003 | 12 | 2003 | Macromolecules | Helix Distortion and Crystal Structure of the α-Form of Poly(<scp>l</s | `10.1021/ma0348674` |
| PLA-004 | 10 | 1991 | Journal of Macromolecular Science, Part B | Crystal structure of stereocomplex of poly(L-lactide) and poly(D-lacti | `10.1080/00222349108245788` |
| PLA-005 | 10 | 2001 | Macromolecules | Crystal Structure of the α-Form of Poly(<scp>l</scp>-lactide) | `10.1021/ma001630o` |

## 填写命令模板

打开原文找到晶胞表后，用下面模板录入（数值替换为原文值，`ref_table` 写清表/图号）：

```bash
python src/annotation/gold_set_annotator.py add --json '{
  "gold_id": "PET-001",
  "polymer_abbr": "PET",
  "doi": "<原文 DOI>",
  "ref_year": 1954, "ref_source": "<期刊>", "ref_table": "Table 2",
  "polymorph_label": "triclinic", "crystal_system": "triclinic",
  "space_group": "P-1",
  "a": 4.56, "b": 5.94, "c": 10.75,
  "alpha": 98.5, "beta": 118.0, "gamma": 112.0,
  "z": 1, "rho_crystal": 1.455, "fiber_period": 10.75,
  "tm": 255.0, "tm0": 280.0, "delta_hf": 140.0, "tg": 75.0,
  "annotator": "葛陆熠", "confidence": "high",
  "notes": "已核对原文 Table 2"
}'
```

填完用以下命令校验与统计：
```bash
python src/annotation/gold_set_annotator.py validate
python src/annotation/gold_set_annotator.py stats
python src/annotation/gold_set_annotator.py export-db
```
