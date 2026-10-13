# Gold Set 人工策展工作表
> 更新：2026-10-14（已完成分级预填 8 条，剩余 12 条待你核填）
> 每槽位挂一个**独立、on-topic、在语料内、CrossRef 已核验**的 DOI。
## 状态图例
- ✅ high：数值可确认出自该篇本身（已填）
- ⚠️ low：该文很可能报道通行值，但**未确认**等于本篇数字，**必须**打开原文核对
- ⬜ 预留：论文不含均聚物晶胞或无 DOI，待补检索/补填

## 填写规范
- 单位：晶胞 Å / 角 ° / ρ g·cm⁻³ / 温度 °C / ΔHf J·g⁻¹（kJ/mol 须 ÷ 重复单元 MW）
- ref_table 必须填原文表/图号（可回溯红线）
- 改一条：`python src/annotation/gold_set_annotator.py edit <GOLD_ID> --json '{...}'`
- 全填完：`validate` → `export-db` → `evaluate`

## PET
| 槽位 | 状态 | 置信 | DOI | 文献 | 待办 |
|---|---|---|---|---|---|
| PET-001 | ⚠️ filled | low | `10.1016/0032-3861(95)91437-c` | Morphology and crystal structure of an a axis oriented, hi… | 核对数值 + 补 ref_table + 补热力学量 |
| PET-002 | ⚠️ filled | low | `10.1016/0032-3861(88)90201-7` | The crystal modulus and structure of oriented poly(ethylen… | 核对数值 + 补 ref_table + 补热力学量 |
| PET-003 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |
| PET-004 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |
| PET-005 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |

## PTT
| 槽位 | 状态 | 置信 | DOI | 文献 | 待办 |
|---|---|---|---|---|---|
| PTT-001 | ✅ filled | high | `10.1016/0032-3861(79)90064-8` | The crystal structure of poly(trimethylene terephthalate) … | 核对数值 + 补 ref_table + 补热力学量 |
| PTT-002 | ⚠️ filled | low | `10.1021/ma000210w` | Crystal Structure and Banded Spherulite of Poly(trimethyle… | 核对数值 + 补 ref_table + 补热力学量 |
| PTT-003 | ⬜ reserved | — | `10.58837/chula.the.2003.1976` | Shear-induced crystallization in poly (trimethylene tereph… | 论文不含均聚物晶胞/无法获取 |
| PTT-004 | ⬜ reserved | — | `10.58837/chula.the.2004.2118` | Crystallization kinetics of poly(trimethylene terephthalat… | 论文不含均聚物晶胞/无法获取 |
| PTT-005 | ⬜ reserved | — | `10.5604/01.3001.0015.6465` | Interfacial Structure of Polytrimethylene Terephthalate/Po… | 论文不含均聚物晶胞/无法获取 |

## PBT
| 槽位 | 状态 | 置信 | DOI | 文献 | 待办 |
|---|---|---|---|---|---|
| PBT-001 | ✅ filled | high | `10.1002/pol.1975.180131109` | The crystal structure of poly(tetramethylene terephthalate… | 核对数值 + 补 ref_table + 补热力学量 |
| PBT-002 | ⬜ reserved | — | `10.1139/v85-510` | On the structure of poly(tetramethylene terephthalate). St… | 论文不含均聚物晶胞/无法获取 |
| PBT-003 | ⬜ reserved | — | `10.1021/ma00229a037` | Light scattering studies on the morphology and deformation… | 论文不含均聚物晶胞/无法获取 |
| PBT-004 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |
| PBT-005 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |

## PLA
| 槽位 | 状态 | 置信 | DOI | 文献 | 待办 |
|---|---|---|---|---|---|
| PLA-001 | ⚠️ filled | low | `10.1021/ma0348674` | Helix Distortion and Crystal Structure of the α-Form of Po… | 核对数值 + 补 ref_table + 补热力学量 |
| PLA-002 | ⚠️ filled | low | `10.1016/j.polymer.2019.05.020` | Crystal structure and unique lamellar thickening for poly(… | 核对数值 + 补 ref_table + 补热力学量 |
| PLA-003 | ✅ filled | high | `10.1021/ma001630o` | Crystal Structure of the α-Form of Poly(<scp>l</scp>-lacti… | 核对数值 + 补 ref_table + 补热力学量 |
| PLA-004 | ⬜ reserved | — | `10.1021/scimeetings.1c00181` | Growth and dissolution of crystal nuclei in poly(L-lactic … | 论文不含均聚物晶胞/无法获取 |
| PLA-005 | ⬜ reserved | — | `—` | — | 先补检索分配 DOI |

---

**已填 8 条**（high 3 / low 5），**预留 12 条**。
⚠️ low 的 5 条数值**不可**当作已核验真值，务必按上表待办核对后再用于正式评测。
