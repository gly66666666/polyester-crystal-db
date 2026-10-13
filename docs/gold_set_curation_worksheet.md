# Gold Set 人工策展工作表（基准重建后）
> 生成时间：2026-10-13　来源：`rebuild_gold_benchmark.py` + `corpus_quality.py`
> 每个槽位已挂一个**独立、on-topic、在语料内、CrossRef 已核验**的 DOI；数值**全部留空**，> 需你打开原文逐条填写后把 `status` 改为 `filled`，再跑 `export-db` 同步主库。
## 填写规范
- 单位：晶胞 Å / 角度 ° / $\rho_c$ g·cm⁻³ / 温度 °C / $\Delta H_f$ J·g⁻¹（kJ/mol 必须 ÷ 重复单元 MW 换算）
- `ref_table` 必须填原文表号/图号（如 `Table 2`）；这是合规红线要求的可回溯定位
- 填完一条：`python src/annotation/gold_set_annotator.py edit <GOLD_ID> --json '{...}'`
- 全部填完：`validate` → `export-db` → 之后 `evaluate` 才能按 (polymer,doi) 命中

## PET
| 槽位 | DOI | 年份 | 期刊 | 标题 | 待填 | 完成 |
|---|---|---|---|---|---|---|
| PET-001 | `10.1016/0032-3861(95)91437-c` | 1995 | Polymer | Morphology and crystal structure of an a axis oriented, highly | 晶胞+热力学+ref_table | ☐ |
| PET-002 | `10.1016/0032-3861(88)90201-7` | 1988 | Polymer | The crystal modulus and structure of oriented poly(ethylene te | 晶胞+热力学+ref_table | ☐ |
| PET-003 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |
| PET-004 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |
| PET-005 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |

## PTT
| 槽位 | DOI | 年份 | 期刊 | 标题 | 待填 | 完成 |
|---|---|---|---|---|---|---|
| PTT-001 | `10.1016/0032-3861(79)90064-8` | 1979 | Polymer | The crystal structure of poly(trimethylene terephthalate) by X | 晶胞+热力学+ref_table | ☐ |
| PTT-002 | `10.1021/ma000210w` | 2000 | Macromolecules | Crystal Structure and Banded Spherulite of Poly(trimethylene t | 晶胞+热力学+ref_table | ☐ |
| PTT-003 | `10.58837/chula.the.2003.1976` | — | — | Shear-induced crystallization in poly (trimethylene terephthal | 晶胞+热力学+ref_table | ☐ |
| PTT-004 | `10.58837/chula.the.2004.2118` | — | — | Crystallization kinetics of poly(trimethylene terephthalate) : | 晶胞+热力学+ref_table | ☐ |
| PTT-005 | `10.5604/01.3001.0015.6465` | 2022 | Fibres and Textiles in Eastern Europe | Interfacial Structure of Polytrimethylene Terephthalate/Polyet | 晶胞+热力学+ref_table | ☐ |

## PBT
| 槽位 | DOI | 年份 | 期刊 | 标题 | 待填 | 完成 |
|---|---|---|---|---|---|---|
| PBT-001 | `10.1002/pol.1975.180131109` | 1975 | Journal of Polymer Science: Polymer Physics Edition | The crystal structure of poly(tetramethylene terephthalate) | 晶胞+热力学+ref_table | ☐ |
| PBT-002 | `10.1139/v85-510` | 1985 | Canadian Journal of Chemistry | On the structure of poly(tetramethylene terephthalate). Struct | 晶胞+热力学+ref_table | ☐ |
| PBT-003 | `10.1021/ma00229a037` | 1982 | Macromolecules | Light scattering studies on the morphology and deformation mec | 晶胞+热力学+ref_table | ☐ |
| PBT-004 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |
| PBT-005 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |

## PLA
| 槽位 | DOI | 年份 | 期刊 | 标题 | 待填 | 完成 |
|---|---|---|---|---|---|---|
| PLA-001 | `10.1021/ma0348674` | 2003 | Macromolecules | Helix Distortion and Crystal Structure of the α-Form of Poly(< | 晶胞+热力学+ref_table | ☐ |
| PLA-002 | `10.1016/j.polymer.2019.05.020` | 2019 | Polymer | Crystal structure and unique lamellar thickening for poly(l-la | 晶胞+热力学+ref_table | ☐ |
| PLA-003 | `10.1021/ma001630o` | 2001 | Macromolecules | Crystal Structure of the α-Form of Poly(<scp>l</scp>-lactide) | 晶胞+热力学+ref_table | ☐ |
| PLA-004 | `10.1021/scimeetings.1c00181` | 2021 | — | Growth and dissolution of crystal nuclei in poly(L-lactic acid | 晶胞+热力学+ref_table | ☐ |
| PLA-005 | `—` | — | — | （预留，待补检索） | 先分配 DOI | ☐ |
---

**合计**：14 个槽位已挂 DOI（待填值），6 个槽位预留待补检索。
**注意**：`canonical_reference.json` 里的权威参考值仅作 sanity 参考，**不可**直接抄进 gold（它们不绑定单一文献，且与某些槽位论文的实际报道值有差异，如 PTT：Poulin-Dandurand vs Desborough；PBT：Yokouchi vs Mencik）。
