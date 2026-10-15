# 全文获取优先级清单

自动生成：`src/annotation/make_fetch_list.py`（源 `corpus_quality.json`，共 325 条 on-topic，其中晶胞级强信号 245 条）。

> **为什么要有这份清单**：晶胞参数几乎只在全文表格里，只抽摘要抽不到。经 OpenAlex 实测，325 条 on-topic 中 **81 条（25%）有 OA 直链**可脚本批量下载，其余仍靠图书馆订阅 / 馆际互借（2026-10-15 更新；此前 2026-10-10 用 Unpaywall 估的「约 2%」严重低估了 green-OA 仓储稿，已作废）。
> PDF 放入 `data/literature/`，命名 `<sanitized_doi>.pdf`（已 gitignore，不入库不分发）。

## 一、按出版商汇总与获取途径

| 出版商 | 条数 | 建议获取途径 |
|---|---:|---|
| Elsevier | 86 | 图书馆已订（ScienceDirect）→ 校内 IP 直接下 |
| 其他 | 77 | 未确认 → 走馆际互借 / 作者主页 / ResearchGate 索抽印本 |
| ACS | 65 | 图书馆已订 → 校内 IP 直接下 |
| Wiley | 64 | 图书馆已订 → 校内 IP 直接下 |
| Springer | 18 | 多数已订（含 Polymer Bulletin 等）→ 试校内 IP |
| RSC | 7 | 图书馆已订 → 优先试 |
| AIP | 4 | 部分已订 → 试校内 IP，不行走馆际互借 |
| Taylor & Francis | 3 | 部分已订 → 试校内 IP，不行走馆际互借 |
| IOP | 1 | 部分已订 → 试校内 IP，不行走馆际互借 |

## 二、逐篇清单（按性价比排序，共 325 条）

先处理前 **81** 条「可自动下载」的（有 OA 直链，脚本批量下即可）；
剩下的再走图书馆 / 馆际互借。

| # | 自动 | 优先 | 成员 | 标题 | 期刊 / 年 | DOI | 途径 | 已下 |
|---:|:---:|:---:|:---:|---|---|---|---|:---:|
| 1 | ⚡ | ★★ | PBN | Effect of self‐seed crystal structure on growth of polymorphs in p | Journal of Polymer Science / 2024 | `10.1002/pol.20230810` | Wiley | ☐ |
| 2 | ⚡ | ★★ | PCL | Polymers of ε-Caprolactone Using New Copper(II) and Zinc(II) Compl | Polymers / 2018 | `10.3390/polym10111239` | 其他 | ☐ |
| 3 | ⚡ | ★★ | PBN | Melting behavior of polymorphic crystals of poly(trimethylene 2,6- | Journal of Applied Crystallography / 2007 | `10.1107/s002188980700461x` | 其他 | ☐ |
| 4 | ⚡ | ★★ | PLA | Influence of the supramolecular and crystal structure of polylacti | Известия Российской академии наук Серия физическая / 2023 | `10.31857/s036767652370134x` | 其他 | ☐ |
| 5 | ⚡ | ★★ | PTT | Crystal Structure and Vibrational Spectra of Poly(trimethylene ter | The Journal of Physical Chemistry B / 2014 | `10.1021/jp411560r` | ACS | ☐ |
| 6 | ⚡ | ★★ | PLA | Quantitative DSC Assessment of the Polymorph-Specific Crystallinit | Polymers / 2025 | `10.3390/polym17091267` | 其他 | ☐ |
| 7 | ⚡ | ★★ | PLA | Crystallization-Driven Design of Multilayered Poly(l-lactide) Foam | Journal of Polymers and the Environment / 2026 | `10.1007/s10924-026-03812-8` | Springer | ☐ |
| 8 | ⚡ | ★★ | PLA | Multistep Relaxation Pathway from Glass to Crystal Development in  | Macromolecules / 2025 | `10.1021/acs.macromol.5c02464` | ACS | ☐ |
| 9 | ⚡ | ★★ | PBS | Enhanced Melt Memory Effects in Poly(butylene succinate) Through I | Polymers / 2025 | `10.3390/polym17081086` | 其他 | ☐ |
| 10 | ⚡ | ★★ | PLA | Transformation of poly( l -lactide) crystals composed of linear ch | Polymer Chemistry / 2024 | `10.1039/d3py01370g` | RSC | ☐ |
| 11 | ⚡ | ★★ | PBS | Homogeneous Crystal Nucleation in Poly (butylene succinate- ran -b | The Journal of Physical Chemistry B / 2024 | `10.1021/acs.jpcb.4c06101` | ACS | ☐ |
| 12 | ⚡ | ★★ | PGA | Influence of a Multiple Epoxy Chain Extender on the Rheological Be | Polymers / 2023 | `10.3390/polym15132764` | 其他 | ☐ |
| 13 | ⚡ | ★★ | PCL | Effect of Molecular Weight on the Crystallization and Melt Memory  | Macromolecules / 2023 | `10.1021/acs.macromol.3c00234` | ACS | ☐ |
| 14 | ⚡ | ★★ | PCL | Impact of Soft Segment Composition on Phase Separation and Crystal | Crystals / 2023 | `10.3390/cryst13101447` | 其他 | ☐ |
| 15 | ⚡ | ★★ | PLA | Effect of the structural features of biobased linear polyester pla | International Journal of Biological Macromolecules / 2022 | `10.1016/j.ijbiomac.2022.06.056` | Elsevier | ☐ |
| 16 | ⚡ | ★★ | PLA | Polylactide cocrystals and gels | SPE Polymers / 2022 | `10.1002/pls2.10083` | Wiley | ☐ |
| 17 | ⚡ | ★★ | PHB | Polyhydroxybutyrate: a review of experimental and simulation studi | Polymer International / 2022 | `10.1002/pi.6402` | Wiley | ☐ |
| 18 | ⚡ | ★★ | PBT | Temperature-Modulated Scanning Calorimetry of Melting–Recrystalliz | Polymers / 2021 | `10.3390/polym13010152` | 其他 | ☐ |
| 19 | ⚡ | ★★ | PLA | Investigation on the α/δ Crystal Transition of Poly(l-lactic Acid) | Polymers / 2021 | `10.3390/polym13193280` | 其他 | ☐ |
| 20 | ⚡ | ★★ | PLA | In-Situ Isothermal Crystallization of Poly(l-lactide) | Polymers / 2021 | `10.3390/polym13193377` | 其他 | ☐ |
| 21 | ⚡ | ★★ | PLA | Temperature dependent poly( l -lactide) crystallization investigat | Materials Advances / 2021 | `10.1039/d1ma00195g` | RSC | ☐ |
| 22 | ⚡ | ★★ | PCL | Surface Crystal Nucleation and Growth in Poly (ε-caprolactone): At | Polymers / 2021 | `10.3390/polym13122008` | 其他 | ☐ |
| 23 | ⚡ | ★★ | PBS | Dependence of Crystallization Behavior of Interacting Telechelic P | Crystals / 2021 | `10.3390/cryst11121530` | 其他 | ☐ |
| 24 | ⚡ | ★★ | PHB | Determining paracrystallinity in mixed-tacticity polyhydroxybutyra | Journal of Applied Crystallography / 2021 | `10.1107/s1600576720015794` | 其他 | ☐ |
| 25 | ⚡ | ★★ | PLA | Impact of Nanoconfinement on Polylactide Crystallization and Gas B | ACS Applied Materials & Interfaces / 2020 | `10.1021/acsami.9b21391` | ACS | ☐ |
| 26 | ⚡ | ★★ | PLA | Temperature and Time Dependence of the Solvent-Induced Crystalliza | Polymers / 2020 | `10.3390/polym12051065` | 其他 | ☐ |
| 27 | ⚡ | ★★ | PLA | Amorphous rigidification and cooperativity drop in semi−crystallin | Polymer / 2020 | `10.1016/j.polymer.2020.122373` | Elsevier | ☐ |
| 28 | ⚡ | ★★ | PBN | Crystallization of poly(butylene 2,6‐naphthalate) containing dieth | POLYMER CRYSTALLIZATION / 2019 | `10.1002/pcr2.10044` | Wiley | ☐ |
| 29 | ⚡ | ★★ | PLA | Structural Evolution in Isothermal Crystallization Process of Poly | Materials / 2019 | `10.3390/ma12111872` | 其他 | ☐ |
| 30 | ⚡ | ★★ | PLA | Diverse nature of femtosecond laser ablation of poly(L-lactide) an | Scientific Reports / 2019 | `10.1038/s41598-019-39640-1` | 其他 | ☐ |
| 31 | ⚡ | ★★ | PEN | Crystallization of poly(butylene 2,6‐naphthalate) containing dieth | Polymer Crystallization / 2018 | `10.1002/pcr2.10044` | Wiley | ☐ |
| 32 | ⚡ | ★★ | PBS | Epitaxial Crystallization Behavior of Poly(butylene adipate) on Or | Polymers / 2018 | `10.3390/polym10020110` | 其他 | ☐ |
| 33 | ⚡ | ★★ | PEN | Crystallinity of poly(ethylene naphthalate) and its relation to te | Japanese Journal of Applied Physics / 2017 | `10.7567/jjap.56.032402` | 其他 | ☐ |
| 34 | ⚡ | ★★ | PBN | Crystallinity of poly(ethylene naphthalate) and its relation to te | Japanese Journal of Applied Physics / 2017 | `10.7567/jjap.56.032402` | 其他 | ☐ |
| 35 | ⚡ | ★★ | PBSA | Poly(lactide)-g-poly(butylene succinate-co-adipate) with High Crys | Materials / 2016 | `10.3390/ma9050313` | 其他 | ☐ |
| 36 | ⚡ | ★★ | PHB | Crystallization behavior of polyhydroxybutyrate (PHB) | AIP conference proceedings / 2016 | `10.1063/1.4965523` | AIP | ☐ |
| 37 | ⚡ | ★★ | PEN | Cocrystalline Copolyimides of Poly(ethylene 2,6-naphthalate) | ACS Macro Letters / 2014 | `10.1021/mz500357z` | ACS | ☐ |
| 38 | ⚡ | ★★ | PHB | Crystallization and preliminary crystallographic analysis of poly( | Acta Crystallographica Section F Structural Biology Communications / 2014 | `10.1107/s2053230x14019347` | 其他 | ☐ |
| 39 | ⚡ | ★★ | PLA | Impact of crystallinity of poly(lactide) on helium and oxygen barr | European Polymer Journal / 2012 | `10.1016/j.eurpolymj.2012.01.014` | Elsevier | ☐ |
| 40 | ⚡ | ★★ | PLA | Effect of crystallization on barrier properties of formulated poly | Polymer International / 2011 | `10.1002/pi.3167` | Wiley | ☐ |
| 41 | ⚡ | ★★ | PTT | Effective nucleating chemical agents for the crystallization of po | Journal of Applied Polymer Science / 2004 | `10.1002/app.20487` | Wiley | ☐ |
| 42 | ⚡ | ★★ | PET | Crystallization of poly(ethylene terephthalate) modified with codi | Journal of Applied Polymer Science / 2001 | `10.1002/app.1381` | Wiley | ☐ |
| 43 | ⚡ | ★★ | PEN | Preferential Orientation of Poly(ethylene 2,6-naphthalate) Melt-Cr | Sen i Gakkaishi / 1998 | `10.2115/fiber.54.10_544` | 其他 | ☐ |
| 44 | ⚡ | ★★ | PBT | ELASTIC MODULUS OF THE CRYSTAL REGIONS IN THE DIRECTION PERPENDICU | Sen i Gakkaishi / 1980 | `10.2115/fiber.36.t33` | 其他 | ☐ |
| 45 | ⚡ | ★★ | PBS | The Semicrystalline Morphology of Polybutylene Succinate Supports  | Macromolecular Chemistry and Physics / 2023 | `10.1002/macp.202200459` | Wiley | ☐ |
| 46 | ⚡ | ★★ | PLA | Morphology and melt crystallization of poly( L ‐lactide) obtained  | Polymer Engineering and Science / 2006 | `10.1002/pen.20617` | Wiley | ☐ |
| 47 | ⚡ | ★★ | PHB | Homogeneous Crystal Nucleation of Poly(3-hydroxybutyrate): Kinetic | Macromolecules / 2025 | `10.1021/acs.macromol.5c02381` | ACS | ☐ |
| 48 | ⚡ | ★★ | PHB | Effect of Chain Stereoconfiguration on Poly(3-hydroxybutyrate) Cry | Biomacromolecules / 2022 | `10.1021/acs.biomac.2c00682` | ACS | ☐ |
| 49 | ⚡ | ★★ | PGA | Fast-Scanning Chip-Calorimetry Measurement of Crystallization Kine | Polymers / 2021 | `10.3390/polym13060891` | 其他 | ☐ |
| 50 | ⚡ | ★★ | PHB | Isothermal Crystallization Kinetics of Poly(4-hydroxybutyrate) Bio | Materials / 2019 | `10.3390/ma12152488` | 其他 | ☐ |
| 51 | ⚡ | ★ | PGA | Conformational behavior of stereo regular substituted polyglycolid | Journal of Biophysical Chemistry / 2011 | `10.4236/jbpc.2011.23033` | 其他 | ☐ |
| 52 | ⚡ | ★ | PBS | Electrospun Polybutylene Succinate Coatings for Sustainable Cardbo | Macromolecular Rapid Communications / 2025 | `10.1002/marc.202500048` | Wiley | ☐ |
| 53 | ⚡ | ★ | PBSA | The biodegradable polymer poly(butylene succinate-co-adipate) modu | Scientific Reports / 2025 | `10.1038/s41598-025-90282-y` | 其他 | ☐ |
| 54 | ⚡ | ★ | PET | Iridescence from tuned microstructures in poly(octamethylene terep | eXPRESS Polymer Letters / 2023 | `10.3144/expresspolymlett.2023.64` | 其他 | ☐ |
| 55 | ⚡ | ★ | PBT | Structure–Property–Processing Relations of Short‐Chain Branched Po | Macromolecular Materials and Engineering / 2022 | `10.1002/mame.202200208` | Wiley | ☐ |
| 56 | ⚡ | ★ | PLA | The Study of Properties and Structure of Polylactide–Graphite Nano | Polymer Crystallization / 2022 | `10.1155/2022/4367582` | 其他 | ☐ |
| 57 | ⚡ | ★ | PCL | Biodegradable Mulching Films Based on Polycaprolactone and Its Por | Polymers / 2022 | `10.3390/polym14245340` | 其他 | ☐ |
| 58 | ⚡ | ★ | PLA | Ultrahigh performance polylactide achieved by the design of molecu | Materials & Design / 2021 | `10.1016/j.matdes.2021.109779` | Elsevier | ☐ |
| 59 | ⚡ | ★ | PHB | Structure and Properties of Biopolymeric Fibrous Materials Based o | Russian Journal of General Chemistry / 2021 | `10.1134/s1070363221030245` | 其他 | ☐ |
| 60 | ⚡ | ★ | PHB | The Investigation of the Structure and Properties of Nonwoven Fibr | IOP Conference Series Materials Science and Engineering / 2021 | `10.1088/1757-899x/1093/1/012032` | IOP | ☐ |
| 61 | ⚡ | ★ | PCL | Mesophase in melt-spun poly(ϵ-caprolactone) filaments: Structure–m | Polymer / 2020 | `10.1016/j.polymer.2020.122870` | Elsevier | ☐ |
| 62 | ⚡ | ★ | PCL | Effect of Ionizing Radiation on the Chemical Structure and the Phy | Polymers / 2018 | `10.3390/polym10040397` | 其他 | ☐ |
| 63 | ⚡ | ★ | PHB | Branched Polyurethanes Based on Synthetic Polyhydroxybutyrate with | Polymers / 2018 | `10.3390/polym10080826` | 其他 | ☐ |
| 64 | ⚡ | ★ | PHB | The supramolecular structure of polyhydroxybutyrate fibers modifie | AIP conference proceedings / 2018 | `10.1063/1.5084503` | AIP | ☐ |
| 65 | ⚡ | ★ | PHB | Structure of the Catalytic Domain of the Class I Polyhydroxybutyra | Journal of Biological Chemistry / 2016 | `10.1074/jbc.m116.756833` | 其他 | ☐ |
| 66 | ⚡ | ★ | PHB | Synthesis of Polyhydroxybutyrate Particles with Micro-to-Nanosized | Nanomaterials / 2016 | `10.3390/nano7010005` | 其他 | ☐ |
| 67 | ⚡ | ★ | PLA | Cell wall structure and function in lactic acid bacteria | Microbial Cell Factories / 2014 | `10.1186/1475-2859-13-s1-s9` | 其他 | ☐ |
| 68 | ⚡ | ★ | PTT | Structure and Mechanical Properties of Poly(trimethylene terephtha | Sen i Gakkaishi / 2013 | `10.2115/fiber.69.107` | 其他 | ☐ |
| 69 | ⚡ | ★ | PBT | In situ study of fiber structure development of poly(butylene tere | Polymer Journal / 2012 | `10.1038/pj.2012.65` | 其他 | ☐ |
| 70 | ⚡ | ★ | PET | Surface structure and properties of poly-(ethylene terephthalate)  | Polymer Degradation and Stability / 2010 | `10.1016/j.polymdegradstab.2010.06.011` | Elsevier | ☐ |
| 71 | ⚡ | ★ | PLA | Structure of Melt Electrospun Poly(lactic acid) Fibers | Sen i Gakkaishi / 2010 | `10.2115/fiber.66.124` | 其他 | ☐ |
| 72 | ⚡ | ★ | PTT | Initial structure development in the CO2 laser-heated drawing of p | Polymer / 2008 | `10.1016/j.polymer.2008.10.022` | Elsevier | ☐ |
| 73 | ⚡ | ★ | PBT | Fine structure and physical properties of poly(butylene terephthal | e-Polymers / 2008 | `10.1515/epoly.2008.8.1.1242` | 其他 | ☐ |
| 74 | ⚡ | ★ | PBT | Structure and Exothermic Behavior of Poly (butylene terephthalate) | Seikei-Kakou / 2005 | `10.4325/seikeikakou.17.842` | 其他 | ☐ |
| 75 | ⚡ | ★ | PHB | Influence of Rheological and Morphological Characteristics of Poly | Materials / 2023 | `10.3390/ma16196525` | 其他 | ☐ |
| 76 | ⚡ | ★ | PCL | The effect of temperature and pressure on polycaprolactone morphol | Polymer / 2020 | `10.1016/j.polymer.2020.122227` | Elsevier | ☐ |
| 77 | ⚡ | ★ | PTT | Interior Lamellar Assembly and Optical Birefringence in Poly(trime | Crystals / 2017 | `10.3390/cryst7020056` | 其他 | ☐ |
| 78 | ⚡ | ★ | PLA | Multi-scale analysis of the impact of polylactide morphology on ga | Polymer / 2016 | `10.1016/j.polymer.2016.11.047` | Elsevier | ☐ |
| 79 | ⚡ | ★ | PCL | Development of lyophilized spherical particles of poly(epsilon-cap | Journal of Drug Delivery Science and Technology / 2014 | `10.1016/s1773-2247(14)50031-7` | Elsevier | ☐ |
| 80 | ⚡ | ★ | PLA | A morphological study of membranes obtained from the systems polyl | Journal of Polymer Science Part B Polymer Physics / 1996 | `10.1002/(sici)1099-0488(19961115)34:15<2569::aid-polb4>3.0.co;2-o` | Wiley | ☐ |
| 81 | ⚡ | ★ | PBT | On the structure of poly(tetramethylene terephthalate). Structural | Canadian Journal of Chemistry / 1985 | `10.1139/v85-510` | 其他 | ☐ |
| 82 |  | ★★ | PTT | The crystal structure of poly(trimethylene terephthalate) by X-ray | Polymer / 1979 | `10.1016/0032-3861(79)90064-8` | Elsevier | ☐ |
| 83 |  | ★★ | PHB | X-ray Crystal Structure Analysis of Poly(3-hydroxybutyrate) β-Form | Macromolecules / 2019 | `10.1021/acs.macromol.9b00225` | ACS | ☐ |
| 84 |  | ★★ | PLA | Crystal Structure Analysis of Poly( l -lactic Acid) α Form On the  | Macromolecules / 2011 | `10.1021/ma2006624` | ACS | ☐ |
| 85 |  | ★★ | PHB | Crystal Structures, Thermal Behaviors, and C−H···O═C Hydrogen Bond | Macromolecules / 2008 | `10.1021/ma702222a` | ACS | ☐ |
| 86 |  | ★★ | PLA | Helix Distortion and Crystal Structure of the α-Form of Poly(<scp> | Macromolecules / 2003 | `10.1021/ma0348674` | ACS | ☐ |
| 87 |  | ★★ | PBT | Electron diffraction and computer modeling studies of the crystal  | Journal of Macromolecular Science Part B / 1997 | `10.1080/00222349708220430` | Taylor & Francis | ☐ |
| 88 |  | ★★ | PET | Poly(ethylene terephthalate) fibers. 1. Crystal structure and morp | Macromolecules / 1993 | `10.1021/ma00061a007` | ACS | ☐ |
| 89 |  | ★★ | PBT | The conformations of poly(butylene-terephthalate) and poly(butylen | Polymer / 2002 | `10.1016/s0032-3861(02)00506-2` | Elsevier | ☐ |
| 90 |  | ★★ | PBN | The conformations of poly(butylene-terephthalate) and poly(butylen | Polymer / 2002 | `10.1016/s0032-3861(02)00506-2` | Elsevier | ☐ |
| 91 |  | ★★ | PLA | Crystal structure, conformation and morphology of solution-spun po | Macromolecules / 1990 | `10.1021/ma00204a041` | ACS | ☐ |
| 92 |  | ★★ | PLA | Dependence of the crystal structure on the d-units amount in semi- | International Journal of Biological Macromolecules / 2024 | `10.1016/j.ijbiomac.2024.136296` | Elsevier | ☐ |
| 93 |  | ★★ | PCL | Peculiar Crystal Structure in Poly(ε-caprolactone) and Poly(ε-capr | Polymer Science, Series A / 2024 | `10.1134/s0965545x24600133` | 其他 | ☐ |
| 94 |  | ★★ | PLA | Effect of the Supramolecular and Crystal Structure of Polylactide  | Bulletin of the Russian Academy of Sciences Physics / 2023 | `10.3103/s1062873823701903` | 其他 | ☐ |
| 95 |  | ★★ | PGA | Crystal Structure of Poly(glycolic acid) β Form | Macromolecules / 2023 | `10.1021/acs.macromol.3c01909` | ACS | ☐ |
| 96 |  | ★★ | PLA | Crystal structure and unique lamellar thickening for poly(l-lactid | Polymer / 2019 | `10.1016/j.polymer.2019.05.020` | Elsevier | ☐ |
| 97 |  | ★★ | PLA | Phase Transition Mechanism of Poly( l -lactic acid) among the α, δ | Macromolecules / 2017 | `10.1021/acs.macromol.7b00272` | ACS | ☐ |
| 98 |  | ★★ | PLA | Molecular weight increase driven by evolution of crystal structure | Polymer / 2017 | `10.1016/j.polymer.2017.08.036` | Elsevier | ☐ |
| 99 |  | ★★ | PHB | Reinvestigation of Crystal Structure and Intermolecular Interactio | Macromolecules / 2016 | `10.1021/acs.macromol.5b02310` | ACS | ☐ |
| 100 |  | ★★ | PLA | Deterioration of metal–organic framework crystal structure during  | Polymer International / 2013 | `10.1002/pi.4478` | Wiley | ☐ |
| 101 |  | ★★ | PTT | Crystal structure and thermal behavior of cold-crystallized poly(t | Colloid and Polymer Science / 2012 | `10.1007/s00396-012-2786-8` | Springer | ☐ |
| 102 |  | ★★ | PLA | Crystal structures of poly(l-lactide)–CO2 complex and its emptied  | Polymer / 2012 | `10.1016/j.polymer.2012.07.044` | Elsevier | ☐ |
| 103 |  | ★★ | PLA | Crystal structure and disorder in Poly(l-lactic acid) δ form (α′ f | Polymer / 2011 | `10.1016/j.polymer.2011.10.046` | Elsevier | ☐ |
| 104 |  | ★★ | PLA | Thermal Behavior and Crystal Structure of Poly( l -lactic acid) wi | The Journal of Physical Chemistry B / 2011 | `10.1021/jp2037312` | ACS | ☐ |
| 105 |  | ★★ | PLA | Effects of carbon nanotubes on dynamic mechanical property, therma | Journal of Polymer Science Part B Polymer Physics / 2009 | `10.1002/polb.21872` | Wiley | ☐ |
| 106 |  | ★★ | PEN | Relationships Between the Crystal Structures and the Multiple Melt | Macromolecular Materials and Engineering / 2004 | `10.1002/mame.200300257` | Wiley | ☐ |
| 107 |  | ★★ | PBS | The effect of 60Co γ‐rays on the crystal structure, melting and cr | Polymer International / 2004 | `10.1002/pi.1579` | Wiley | ☐ |
| 108 |  | ★★ | PLA | Crystal Structure of the α-Form of Poly(<scp>l</scp>-lactide) | Macromolecules / 2001 | `10.1021/ma001630o` | ACS | ☐ |
| 109 |  | ★★ | PET | Direct methods in polymer fiber diffraction – the crystal structur | Zeitschrift für Kristallographie - Crystalline Materials / 1998 | `10.1524/zkri.1998.213.9.445` | 其他 | ☐ |
| 110 |  | ★★ | PBN | Crystal structure of poly(butylene-2,6-naphthalate) | Polymer / 1998 | `10.1016/s0032-3861(97)00618-6` | Elsevier | ☐ |
| 111 |  | ★★ | PET | Crystal Structure of Cyclic Di(ethylene terephthalate) | Polymer Journal / 1995 | `10.1295/polymj.27.840` | 其他 | ☐ |
| 112 |  | ★★ | PET | Crystal Structure of the Higher Temperature Phase (Type B) of Cycl | Polymer Journal / 1992 | `10.1295/polymj.24.1099` | 其他 | ☐ |
| 113 |  | ★★ | PCL | Crystal structure of poly(iε-caprolactone) | Macromolecules / 1990 | `10.1021/ma00223a017` | ACS | ☐ |
| 114 |  | ★★ | PBT | The crystal structure of poly(tetramethylene terephthalate) | Journal of Polymer Science: Polymer Physics Edition / 1975 | `10.1002/pol.1975.180131109` | Wiley | ☐ |
| 115 |  | ★★ | PGA | Structural studies of polyesters. I. Crystal structure of polyglyc | Die Makromolekulare Chemie / 1968 | `10.1002/macp.1968.021130119` | Wiley | ☐ |
| 116 |  | ★★ | PBN | Effect of Crystal Polymorphism on Elastic Modulus and Hardness of  | Polymer Engineering &amp; Science / 2026 | `10.1002/pen.70832` | Wiley | ☐ |
| 117 |  | ★★ | PBN | Shear-induced crystallization of polymorphic poly(butylene 2,6-nap | Journal of Rheology / 2025 | `10.1122/8.0001131` | 其他 | ☐ |
| 118 |  | ★★ | PLA | Melt extension-induced shish-kebabs with heterogeneous spatial dis | Polymer / 2020 | `10.1016/j.polymer.2020.122875` | Elsevier | ☐ |
| 119 |  | ★★ | PLA | Effect of a small amount of poly(ethylene oxide) on crystal polymo | Polymer Bulletin / 2020 | `10.1007/s00289-020-03464-1` | Springer | ☐ |
| 120 |  | ★★ | PLA | Isothermal crystalline polymorphs of poly(l-lactic acid) by FTIR c | Spectrochimica Acta Part A Molecular and Biomolecular Spectroscopy / 2019 | `10.1016/j.saa.2019.117953` | Elsevier | ☐ |
| 121 |  | ★★ | PLA | Influence of α′‐/α‐crystal polymorphism on properties of poly( l ‐ | Polymer International / 2018 | `10.1002/pi.5707` | Wiley | ☐ |
| 122 |  | ★★ | PLA | Influence of Boron Nitride Nanosheets on the Crystallization and P | The Journal of Physical Chemistry B / 2018 | `10.1021/acs.jpcb.8b03211` | ACS | ☐ |
| 123 |  | ★★ | PET | Investigation of polymorphism for amorphous and semi-crystalline p | Journal of the Korean Physical Society / 2017 | `10.3938/jkps.70.382` | 其他 | ☐ |
| 124 |  | ★★ | PLA | Characterizing polymorphism and crystal transformation of polylact | Polymer Testing / 2017 | `10.1016/j.polymertesting.2016.11.017` | Elsevier | ☐ |
| 125 |  | ★★ | PLA | Preferential Formation of β-Form Crystals and Temperature-Dependen | Macromolecules / 2017 | `10.1021/acs.macromol.7b01705` | ACS | ☐ |
| 126 |  | ★★ | PLA | Temperature-dependent polymorphic crystallization of poly(l-lactid | Polymer / 2017 | `10.1016/j.polymer.2017.11.069` | Elsevier | ☐ |
| 127 |  | ★★ | PLA | Influence of chain structure on crystal polymorphism of poly(lacti | Colloid & Polymer Science / 2013 | `10.1007/s00396-013-3081-z` | Springer | ☐ |
| 128 |  | ★★ | PLA | Influence of crystal polymorphism on crystallinity calculation of  | Vibrational Spectroscopy / 2013 | `10.1016/j.vibspec.2013.10.003` | Elsevier | ☐ |
| 129 |  | ★★ | PLA | Effect of Film Formation Method and Annealing on Morphology and Cr | Journal of Manufacturing Science and Engineering / 2013 | `10.1115/1.4025909` | 其他 | ☐ |
| 130 |  | ★★ | PLA | Influence of crystal polymorphism on mechanical and barrier proper | European Polymer Journal / 2011 | `10.1016/j.eurpolymj.2011.02.009` | Elsevier | ☐ |
| 131 |  | ★★ | PLA | Crystal polymorphism of poly(l-lactic acid) and its influence on t | Thermochimica Acta / 2011 | `10.1016/j.tca.2010.12.027` | Elsevier | ☐ |
| 132 |  | ★★ | PLA | Crystal structure and morphology influenced by shear effect of pol | Polymer / 2011 | `10.1016/j.polymer.2011.05.044` | Elsevier | ☐ |
| 133 |  | ★★ | PLA | Blending Effects on Polymorphic Crystallization of Poly( l -lactid | Macromolecules / 2009 | `10.1021/ma8024943` | ACS | ☐ |
| 134 |  | ★★ | PLA | Polymorphic Transition in Disordered Poly( l -lactide) Crystals In | Macromolecules / 2008 | `10.1021/ma800343g` | ACS | ☐ |
| 135 |  | ★★ | PLA | Polymorphous Crystallization and Multiple Melting Behavior of Poly | Macromolecules / 2007 | `10.1021/ma071258d` | ACS | ☐ |
| 136 |  | ★★ | PBN | X-ray and DSC studies on the melt-recrystallization process of pol | Thermochimica Acta / 2003 | `10.1016/s0040-6031(02)00531-2` | Elsevier | ☐ |
| 137 |  | ★★ | PBN | Crystal polymorphism of poly(butylene-2,6-naphthalate) prepared by | Polymer / 2002 | `10.1016/s0032-3861(01)00808-4` | Elsevier | ☐ |
| 138 |  | ★★ | PTT | Morphology and crystal structure of CTFMP and bulk polymerized pol | Polymer / 2001 | `10.1016/s0032-3861(01)00044-1` | Elsevier | ☐ |
| 139 |  | ★★ | PTT | Crystal orientation function of poly(trimethylene terephthalate) b | Polymer Bulletin / 2001 | `10.1007/s002890170061` | Springer | ☐ |
| 140 |  | ★★ | PTT | Crystal Structure and Banded Spherulite of Poly(trimethylene terep | Macromolecules / 2000 | `10.1021/ma000210w` | ACS | ☐ |
| 141 |  | ★★ | PLA | Epitaxial crystallization and crystalline polymorphism of polylact | Polymer / 2000 | `10.1016/s0032-3861(00)00234-2` | Elsevier | ☐ |
| 142 |  | ★★ | PBT | Time-resolved X-ray studies of structure development in poly(butyl | Polymer / 1999 | `10.1016/s0032-3861(98)00573-4` | Elsevier | ☐ |
| 143 |  | ★★ | PET | Crystal structure and morphology of poly(ethylene terephthalate) s | Journal of Macromolecular Science Part B / 1997 | `10.1080/00222349708220415` | Taylor & Francis | ☐ |
| 144 |  | ★★ | PET | Morphology and crystal structure of an a axis oriented, highly cry | Polymer / 1995 | `10.1016/0032-3861(95)91437-c` | Elsevier | ☐ |
| 145 |  | ★★ | PLA | Crystal Polymorphism and Morphology of Polylactides | Advances in polymer science / 2017 | `10.1007/12_2016_15` | Springer | ☐ |
| 146 |  | ★★ | PLA | Influence of chain structure on crystal polymorphism of poly(lacti | Colloid & Polymer Science / 2015 | `10.1007/s00396-015-3709-2` | Springer | ☐ |
| 147 |  | ★★ | PLA | Isothermal crystallization kinetics and crystal structure of poly( | Journal of Applied Polymer Science / 2010 | `10.1002/app.32728` | Wiley | ☐ |
| 148 |  | ★★ | PLA | Kinetics and crystal structure of poly(lactic acid) crystallized n | Polymer Composites / 2010 | `10.1002/pc.21004` | Wiley | ☐ |
| 149 |  | ★★ | PLA | Kinetics and crystal structure of isothermal crystallization of po | Journal of Applied Polymer Science / 2010 | `10.1002/app.32225` | Wiley | ☐ |
| 150 |  | ★★ | PHB | Temperature influence on changes of parameters of the unit cell of | Polymer / 1996 | `10.1016/0032-3861(96)82922-3` | Elsevier | ☐ |
| 151 |  | ★★ | PET | Crystal lattice deformation and the mesophase in poly(ethylene ter | Polymer / 1988 | `10.1016/0032-3861(88)90099-7` | Elsevier | ☐ |
| 152 |  | ★★ | PET | Unit cell dimensions of poly(ethylene terephthalate) | Die Makromolekulare Chemie / 1975 | `10.1002/macp.1975.021760821` | Wiley | ☐ |
| 153 |  | ★★ | PBN | Polymorphic structure in ultrasonic microinjection-molded poly(but | Polymer / 2022 | `10.1016/j.polymer.2022.125275` | Elsevier | ☐ |
| 154 |  | ★★ | PLA | Modeling of polymorphic composition development during isothermal  | Polymer / 2022 | `10.1016/j.polymer.2022.124618` | Elsevier | ☐ |
| 155 |  | ★★ | PLA | Conformational Energy Settled Crystallization Behaviors of Poly( l | ACS Applied Polymer Materials / 2019 | `10.1021/acsapm.9b00722` | ACS | ☐ |
| 156 |  | ★★ | PLA | Polymorph control of a complex BaCO3 superstructure through the co | Reactive and Functional Polymers / 2009 | `10.1016/j.reactfunctpolym.2009.08.004` | Elsevier | ☐ |
| 157 |  | ★★ | PTT | In situ study of structure development in poly(trimethylene tereph | Polymer / 2001 | `10.1016/s0032-3861(01)00042-8` | Elsevier | ☐ |
| 158 |  | ★★ | PTT | In situ study of structure development during continuous hot-drawi | Polymer / 2001 | `10.1016/s0032-3861(01)00045-3` | Elsevier | ☐ |
| 159 |  | ★★ | PET | On the mechanical properties of poly(ethylene terephthalate). Forc | Journal of Polymer Science Part B Polymer Physics / 1996 | `10.1002/(sici)1099-0488(19960415)34:5<963::aid-polb14>3.0.co;2-9` | Wiley | ☐ |
| 160 |  | ★★ | PLA | Texture Induced by Molecular Weight Dispersity: Polymorphism withi | Chinese Journal of Polymer Science / 2020 | `10.1007/s10118-020-2464-0` | Springer | ☐ |
| 161 |  | ★★ | PHB | Structural Investigation of Poly(3-hydroxybutyrate) Spherulites by | Macromolecular Chemistry and Physics / 2001 | `10.1002/1521-3935(20010501)202:8<1405::aid-macp1405>3.0.co;2-5` | Wiley | ☐ |
| 162 |  | ★★ | PBN | Intraspherulitic Melting-Temperature Distribution of Poly(butylene | Macromolecules / 2025 | `10.1021/acs.macromol.5c00542` | ACS | ☐ |
| 163 |  | ★★ | PBS | Imperfect Crystals of Poly(butylene succinate) Formed at High Supe | Macromolecular Chemistry and Physics / 2025 | `10.1002/macp.202500079` | Wiley | ☐ |
| 164 |  | ★★ | PBS | The effect of calcium salt of carboxylic acid on the crystallizati | Journal of Polymer Research / 2025 | `10.1007/s10965-025-04429-6` | Springer | ☐ |
| 165 |  | ★★ | PHBV | Comparative Study on Crystallization Behaviour of Poly(3-Hydroxybu | 2025 | `10.2139/ssrn.5096032` | 其他 | ☐ |
| 166 |  | ★★ | PHBV | Comparative study on crystallization behaviour of poly(3-hydroxybu | Polymer / 2025 | `10.1016/j.polymer.2025.128319` | Elsevier | ☐ |
| 167 |  | ★★ | PET | Crystallization of Poly(ethylene terephthalate): A Review | Polymers / 2024 | `10.3390/polym16141975` | 其他 | ☐ |
| 168 |  | ★★ | PLA | Superior Barrier Performance of Poly(lactic acid) Films via Constr | ACS Applied Polymer Materials / 2024 | `10.1021/acsapm.4c01327` | ACS | ☐ |
| 169 |  | ★★ | PGA | Crystal structural evolution and cavitation in biodegradable polyg | Polymer / 2024 | `10.1016/j.polymer.2024.127517` | Elsevier | ☐ |
| 170 |  | ★★ | PBS | Reorganization of Poly(Butylene Succinate) Containing Crystals of  | Macromolecular Rapid Communications / 2024 | `10.1002/marc.202400273` | Wiley | ☐ |
| 171 |  | ★★ | PBS | Crystallization manipulation of poly(butylene succinate) via hydra | Polymer / 2024 | `10.1016/j.polymer.2024.126933` | Elsevier | ☐ |
| 172 |  | ★★ | PTT | Lamellar crystallization of poly(trimethylene terephthalate) | Polymer Journal / 2023 | `10.1038/s41428-023-00777-6` | 其他 | ☐ |
| 173 |  | ★★ | PLA | Modeling of the kinetics of polymorphic isothermal crystallization | Polymer / 2023 | `10.1016/j.polymer.2023.126126` | Elsevier | ☐ |
| 174 |  | ★★ | PLA | Sn(II)2-ethylhexanoate-catalyzed polymerizations of l-lactide in s | Polymer / 2022 | `10.1016/j.polymer.2022.125142` | Elsevier | ☐ |
| 175 |  | ★★ | PLA | Broadband infrared absorption spectroscopy of low-frequency inter- | Physica B Condensed Matter / 2022 | `10.1016/j.physb.2022.414488` | Elsevier | ☐ |
| 176 |  | ★★ | PLA | Growth and dissolution of crystal nuclei in poly(L-lactic acid) (P | 2021 | `10.1021/scimeetings.1c00181` | ACS | ☐ |
| 177 |  | ★★ | PCL | Effect of Porous and Nonporous Polycaprolactone Fiber Meshes on Ca | Crystal Growth & Design / 2020 | `10.1021/acs.cgd.0c00803` | ACS | ☐ |
| 178 |  | ★★ | PBN | Cover Image: Crystallization of poly(butylene 2,6‐naphthalate) con | POLYMER CRYSTALLIZATION / 2019 | `10.1002/pcr2.10120` | Wiley | ☐ |
| 179 |  | ★★ | PBN | Melt Crystallization of Poly(butylene 2,6-naphthalate) | Chinese Journal of Polymer Science / 2019 | `10.1007/s10118-020-2354-5` | Springer | ☐ |
| 180 |  | ★★ | PHB | Crystallization of Poly[(R)-3-hydroxybutyrate] | Advances in polymer science / 2019 | `10.1007/12_2019_50` | Springer | ☐ |
| 181 |  | ★★ | PBN | Smectic liquid crystal Schlieren texture in rapidly cooled poly(bu | European Polymer Journal / 2018 | `10.1016/j.eurpolymj.2018.02.010` | Elsevier | ☐ |
| 182 |  | ★★ | PLA | Influence of the Rigid Amorphous Fraction and Crystallinity on Pol | Macromolecules / 2018 | `10.1021/acs.macromol.8b00833` | ACS | ☐ |
| 183 |  | ★★ | PCL | Preparation of Random and Aligned Polycaprolactone Fiber as Templa | Springer eBooks / 2018 | `10.1007/978-981-13-1002-7_25` | Springer | ☐ |
| 184 |  | ★★ | PET | 3D structure of nano-oriented crystals of poly(ethylene terephthal | Polymer Journal / 2017 | `10.1038/s41428-017-0003-9` | 其他 | ☐ |
| 185 |  | ★★ | PBT | Crystal reorganization of poly (butylene terephthalate) | Polymer / 2017 | `10.1016/j.polymer.2017.07.076` | Elsevier | ☐ |
| 186 |  | ★★ | PLA | Crystallization-induced microcellular foaming of poly (lactic acid | Polymer Degradation and Stability / 2017 | `10.1016/j.polymdegradstab.2017.08.022` | Elsevier | ☐ |
| 187 |  | ★★ | PHB | Acceleration of the crystal growth rate of low molecular weight or | CrystEngComm / 2017 | `10.1039/c6ce02177h` | RSC | ☐ |
| 188 |  | ★★ | PLA | Melting of α′- and α-crystals of poly(lactic acid) | AIP conference proceedings / 2016 | `10.1063/1.4949583` | AIP | ☐ |
| 189 |  | ★★ | PGA | Crystallization behavior and crystalline structural changes of pol | CrystEngComm / 2016 | `10.1039/c6ce01623e` | RSC | ☐ |
| 190 |  | ★★ | PBT | Density of heterogeneous and homogeneous crystal nuclei in poly (b | European Polymer Journal / 2015 | `10.1016/j.eurpolymj.2015.02.013` | Elsevier | ☐ |
| 191 |  | ★★ | PLA | Development of polylactide bead foams with double crystal melting  | Polymer / 2015 | `10.1016/j.polymer.2015.05.048` | Elsevier | ☐ |
| 192 |  | ★★ | PLA | Enthalpy of melting of α′- and α-crystals of poly(l-lactic acid) | European Polymer Journal / 2015 | `10.1016/j.eurpolymj.2015.07.024` | Elsevier | ☐ |
| 193 |  | ★★ | PLA | Tailoring the crystallization behavior of poly(L-lactide) with sel | European Polymer Journal / 2015 | `10.1016/j.eurpolymj.2015.07.040` | Elsevier | ☐ |
| 194 |  | ★★ | PLA | Single Crystals of the Frustrated β-Phase and Genesis of the Disor | ACS Macro Letters / 2015 | `10.1021/acsmacrolett.5b00205` | ACS | ☐ |
| 195 |  | ★★ | PHB | Crystallization properties of polyhydroxybutyrate with modified si | Journal of Polymer Research / 2015 | `10.1007/s10965-015-0706-6` | Springer | ☐ |
| 196 |  | ★★ | PLA | Significantly Improving Oxygen Barrier Properties of Polylactide v | Biomacromolecules / 2014 | `10.1021/bm500167u` | ACS | ☐ |
| 197 |  | ★★ | PBS | Radiopaque iodinated poly(ester-urethane)s based on poly(butylene  | Polymer / 2014 | `10.1016/j.polymer.2014.04.023` | Elsevier | ☐ |
| 198 |  | ★★ | PLA | Crystal Nucleation in Glassy Poly( l -lactic acid) | Macromolecules / 2013 | `10.1021/ma401036j` | ACS | ☐ |
| 199 |  | ★★ | PLA | NMR crystallography of α-poly(l-lactide) | Physical Chemistry Chemical Physics / 2013 | `10.1039/c2cp43174b` | RSC | ☐ |
| 200 |  | ★★ | PLA | Influence of the chain extension on the crystallization behavior o | Polymer Engineering and Science / 2013 | `10.1002/pen.23595` | Wiley | ☐ |
| 201 |  | ★★ | PLA | Shear effects on crystalline structures of poly(l-lactide) | CrystEngComm / 2013 | `10.1039/c3ce40466h` | RSC | ☐ |
| 202 |  | ★★ | PHB | The Role of the Crystallization Temperature on the Nanophase Struc | The Journal of Physical Chemistry B / 2013 | `10.1021/jp4063127` | ACS | ☐ |
| 203 |  | ★★ | PLA | Complex Crystal Formation of Poly( l -lactide) with Solvent Molecu | Macromolecules / 2012 | `10.1021/ma202324g` | ACS | ☐ |
| 204 |  | ★★ | PBS | Reversible Lamellar Thickening Induced by Crystal Transition in Po | Macromolecules / 2012 | `10.1021/ma300530a` | ACS | ☐ |
| 205 |  | ★★ | PHB | The Role of the Rigid Amorphous Fraction on Cold Crystallization o | Macromolecules / 2012 | `10.1021/ma3010907` | ACS | ☐ |
| 206 |  | ★★ | PET | Coupling between Crystal Melting and Rigid Amorphous Fraction Mobi | Macromolecules / 2010 | `10.1021/ma101035h` | ACS | ☐ |
| 207 |  | ★★ | PTT | Cold Crystallization of Poly(trimethylene terephthalate) As Reveal | Macromolecules / 2009 | `10.1021/ma902188c` | ACS | ☐ |
| 208 |  | ★★ | PBT | Crystallization of Poly(butylene terephthalate) from the Glass | Macromolecules / 2009 | `10.1021/ma9017058` | ACS | ☐ |
| 209 |  | ★★ | PTT | Cold-Crystallization of Poly(trimethylene terephthalate) Studied b | Macromolecules / 2008 | `10.1021/ma801119n` | ACS | ☐ |
| 210 |  | ★★ | PEN | Crystallization Behaviors of Poly(ethylene 2,6-naphthalate) in the | Industrial & Engineering Chemistry Research / 2008 | `10.1021/ie061668a` | ACS | ☐ |
| 211 |  | ★★ | PLA | Influence of dispersed organophilic montmorillonite at nanometer‐s | Polymer Engineering and Science / 2008 | `10.1002/pen.21057` | Wiley | ☐ |
| 212 |  | ★★ | PGA | Structure development during crystallization and solid‐state proce | Journal of Applied Polymer Science / 2008 | `10.1002/app.29000` | Wiley | ☐ |
| 213 |  | ★★ | PGA | Crystalline structure of sequential poly(ester amide)s derived fro | Journal of Polymer Science Part B Polymer Physics / 2008 | `10.1002/polb.21630` | Wiley | ☐ |
| 214 |  | ★★ | PHB | Surface structure of folded-chain crystals of poly(R-3-hydroxybuty | Polymer / 2008 | `10.1016/j.polymer.2008.08.026` | Elsevier | ☐ |
| 215 |  | ★★ | PLA | Crystallization and Melting Behavior of Poly ( l -lactic Acid) | Macromolecules / 2007 | `10.1021/ma070082c` | ACS | ☐ |
| 216 |  | ★★ | PLA | Crystal density and heat of fusion for a stereo‐complex of poly( L | Journal of Polymer Science Part B Polymer Physics / 2007 | `10.1002/polb.21270` | Wiley | ☐ |
| 217 |  | ★★ | PLA | Structure and mechanical properties of poly( L ‐lactic acid) cryst | Journal of Polymer Science Part B Polymer Physics / 2007 | `10.1002/polb.21131` | Wiley | ☐ |
| 218 |  | ★★ | PLA | Transcrystalline structures of poly(l-lactide) | Polymer / 2007 | `10.1016/j.polymer.2007.06.012` | Elsevier | ☐ |
| 219 |  | ★★ | PLA | Crystallization behavior of poly(l-lactic acid) | Polymer / 2006 | `10.1016/j.polymer.2006.08.054` | Elsevier | ☐ |
| 220 |  | ★★ | PLA | Stereoselective Crystallization and Specific Interactions in Polyl | Macromolecules / 2005 | `10.1021/ma051266z` | ACS | ☐ |
| 221 |  | ★★ | PTT | Structural formation and gelation behavior of cold-crystallized po | Polymer / 2004 | `10.1016/j.polymer.2004.10.002` | Elsevier | ☐ |
| 222 |  | ★★ | PBT | Orientation Behavior of the Three Principal Crystallographic Axes  | Macromolecules / 2004 | `10.1021/ma030347x` | ACS | ☐ |
| 223 |  | ★★ | PHB | Effect of lignin particles as a nucleating agent on crystallizatio | Journal of Applied Polymer Science / 2004 | `10.1002/app.21204` | Wiley | ☐ |
| 224 |  | ★★ | PHB | The deformation of the chain molecules and crystallites in poly([R | Polymer Degradation and Stability / 2004 | `10.1016/j.polymdegradstab.2004.04.006` | Elsevier | ☐ |
| 225 |  | ★★ | PTT | Effect of aging on the mechanical properties of cold-crystallized  | Polymer / 2003 | `10.1016/s0032-3861(03)00282-9` | Elsevier | ☐ |
| 226 |  | ★★ | PHB | Characteristic Interactions between Poly(hydroxybutyrate) Depolyme | Macromolecular Bioscience / 2003 | `10.1002/mabi.200300004` | Wiley | ☐ |
| 227 |  | ★★ | PEN | Nanostructure of atmospheric and high-pressure crystallized poly(e | Polymer / 2002 | `10.1016/s0032-3861(02)00777-2` | Elsevier | ☐ |
| 228 |  | ★★ | PLA | Crystalline and supermolecular structure of polylactide in relatio | Journal of Applied Polymer Science / 2002 | `10.1002/app.11280` | Wiley | ☐ |
| 229 |  | ★★ | PET | CHARACTERIZATION OF THE TWO-PHASE STRUCTURE IN SEMICRYSTALLINE POL | Acta Physica Sinica / 2001 | `10.7498/aps.50.1132` | 其他 | ☐ |
| 230 |  | ★★ | PEN | Nanostructure of atmospheric and high-pressure crystallised poly(e | Journal of Materials Science / 2001 | `10.1023/a:1012931416958` | 其他 | ☐ |
| 231 |  | ★★ | PEN | Effect of shearing on crystallization behavior of poly(ethylene na | Polymer / 2000 | `10.1016/s0032-3861(99)00703-x` | Elsevier | ☐ |
| 232 |  | ★★ | PEN | Two-dimensional vibrational correlation spectroscopic study on cry | AIP conference proceedings / 2000 | `10.1063/1.1302867` | AIP | ☐ |
| 233 |  | ★★ | PTT | Crystallization and melting behaviors of poly(trimethylene terepht | Journal of Polymer Research / 1999 | `10.1007/s10965-006-0096-x` | Springer | ☐ |
| 234 |  | ★★ | PEN | Solvent induced crystallization behavior of poly(ethylene 2,6-naph | Polymer / 1999 | `10.1016/s0032-3861(98)00783-6` | Elsevier | ☐ |
| 235 |  | ★★ | PHBV | The effect of seeding on the crystallisation of poly(hydroxybutyra | Polymer / 1999 | `10.1016/s0032-3861(98)00732-0` | Elsevier | ☐ |
| 236 |  | ★★ | PET | New Aspects Concerning the Structure and Degree of Crystallinity i | Macromolecules / 1996 | `10.1021/ma960466v` | ACS | ☐ |
| 237 |  | ★★ | PET | Structure analysis of the noncrystalline material in poly(ethylene | Macromolecular Chemistry and Physics / 1994 | `10.1002/macp.1994.021950236` | Wiley | ☐ |
| 238 |  | ★★ | PET | Structural formation of poly (ethylene terephthalate) during the i | Polymer / 1992 | `10.1016/0032-3861(92)90399-h` | Elsevier | ☐ |
| 239 |  | ★★ | PET | The crystal modulus and structure of oriented poly(ethylene tereph | Polymer / 1988 | `10.1016/0032-3861(88)90201-7` | Elsevier | ☐ |
| 240 |  | ★★ | PET | Crystalline structures of poly(ethylene terephthalate) fibers | Journal of Applied Polymer Science / 1987 | `10.1002/app.1987.070330504` | Wiley | ☐ |
| 241 |  | ★★ | PBN | Higher order modes and crystallographic axis angular dependence of | 1987 Twelth International Conference on Infrared and Millimeter Waves / 1987 | `10.1109/irmm.1987.9126948` | 其他 | ☐ |
| 242 |  | ★★ | PBT | Surface controlled crystallization of poly(tetramethylene terephth | Journal of Materials Science / 1983 | `10.1007/bf00700779` | Springer | ☐ |
| 243 |  | ★★ | PBT | Elastic modulus of crystalline regions of poly(butylene terephthal | Journal of Polymer Science Polymer Physics Edition / 1982 | `10.1002/pol.1982.180200213` | Wiley | ☐ |
| 244 |  | ★★ | PBT | Influence of the Crosslinking on the Crystallization of Poly(tetra | Polymer Journal / 1978 | `10.1295/polymj.10.495` | 其他 | ☐ |
| 245 |  | ★★ | PBT | A comparison of published crystalline structures of poly(tetrameth | Polymer / 1977 | `10.1016/0032-3861(77)90189-6` | Elsevier | ☐ |
| 246 |  | ★★ | PET | Single crystals of poly(ethylene terephthalate) | Journal of Polymer Science Part A General Papers / 1965 | `10.1002/pol.1965.100030110` | Wiley | ☐ |
| 247 |  | ★★ | PTT | Shear-induced crystallization in poly (trimethylene terephthalate) | None | `10.58837/chula.the.2003.1976` | 其他 | ☐ |
| 248 |  | ★★ | PBS | Evolution of Crystal Morphology in Polylactic Acid Foaming Process | SSRN Electronic Journal / 2026 | `10.2139/ssrn.6160787` | 其他 | ☐ |
| 249 |  | ★★ | PLA | Lamellar Morphology of Disorder α′-Crystals of Poly( L -Lactic Aci | Crystal Growth & Design / 2024 | `10.1021/acs.cgd.3c01498` | ACS | ☐ |
| 250 |  | ★★ | PBS | Poly (butylene succinate): Low-temperature nucleation and crystall | Polymer / 2023 | `10.1016/j.polymer.2023.126311` | Elsevier | ☐ |
| 251 |  | ★★ | PBN | Curly morphology of β’-crystals of poly(butylene-2,6-naphthalate) | Materials Letters / 2022 | `10.1016/j.matlet.2022.133570` | Elsevier | ☐ |
| 252 |  | ★★ | PBN | Morphology of α-crystals of poly (butylene 2,6-naphthalate) crysta | Polymer / 2020 | `10.1016/j.polymer.2020.122404` | Elsevier | ☐ |
| 253 |  | ★★ | PTT | Novel approaches to study the crystal assembly in banded spherulit | CrystEngComm / 2016 | `10.1039/c6ce01261b` | RSC | ☐ |
| 254 |  | ★★ | PLA | Mesophase-Mediated Crystallization of Poly( l -lactide): Determini | Macromolecules / 2016 | `10.1021/acs.macromol.6b01442` | ACS | ☐ |
| 255 |  | ★★ | PLA | Enhancing mechanical performance of polylactide by tailoring cryst | Polymer / 2014 | `10.1016/j.polymer.2014.10.059` | Elsevier | ☐ |
| 256 |  | ★★ | PLA | Control of Crystal Morphology in Poly( l -lactide) by Adding Nucle | Macromolecules / 2011 | `10.1021/ma102439t` | ACS | ☐ |
| 257 |  | ★★ | PLA | Crystalline Structure and Morphology of Poly( l -lactide) Formed u | Macromolecules / 2008 | `10.1021/ma800766h` | ACS | ☐ |
| 258 |  | ★★ | PGA | Alternating poly(ester amide)s of glycolic acid and ω‐amino acids: | Journal of Polymer Science Part B Polymer Physics / 2007 | `10.1002/polb.21077` | Wiley | ☐ |
| 259 |  | ★★ | PEN | Crystallization behavior and morphology of poly(ethylene 2,6-napht | Polymer / 2003 | `10.1016/j.polymer.2003.08.002` | Elsevier | ☐ |
| 260 |  | ★★ | PLA | Morphology of poly(l-lactide) solution-grown crystals | Polymer / 1997 | `10.1016/s0032-3861(96)00987-1` | Elsevier | ☐ |
| 261 |  | ★★ | PET | Morphology and crystallization of poly(ethylene terephthalate) | Polymer International / 1994 | `10.1002/pi.1994.210350209` | Wiley | ☐ |
| 262 |  | ★★ | PET | Morphology and melting behavior of semicrystalline poly(ethylene t | Journal of Polymer Science Polymer Physics Edition / 1980 | `10.1002/pol.1980.180180613` | Wiley | ☐ |
| 263 |  | ★★ | PLA | Dual Cold Crystallization Kinetics of Heterogeneous Amorphous Stru | Chinese Journal of Polymer Science / 2025 | `10.1007/s10118-025-3331-9` | Springer | ☐ |
| 264 |  | ★★ | PLA | Kinetics of Nucleation and Growth of Crystals of Poly(l-lactic aci | Advances in polymer science / 2017 | `10.1007/12_2016_13` | Springer | ☐ |
| 265 |  | ★★ | PBN | Equilibrium melting temperature and crystallization kinetics of α- | Polymer Journal / 2011 | `10.1038/pj.2011.112` | 其他 | ☐ |
| 266 |  | ★★ | PLA | Crystallization Kinetics of Linear and Long-Chain-Branched Polylac | Industrial & Engineering Chemistry Research / 2011 | `10.1021/ie2011966` | ACS | ☐ |
| 267 |  | ★★ | PGA | Crystallization kinetics of poly(glycolic acid-alt-6-aminohexanoic | European Polymer Journal / 2006 | `10.1016/j.eurpolymj.2006.01.013` | Elsevier | ☐ |
| 268 |  | ★★ | PLA | Crystallization kinetics of poly(L‐lactide) in contact with pressu | Polymer Engineering and Science / 2004 | `10.1002/pen.20017` | Wiley | ☐ |
| 269 |  | ★★ | PTT | Phase transformation of poly(trimethylene terephthalate) in crysta | Fibers and Polymers / 2000 | `10.1007/bf02874872` | Springer | ☐ |
| 270 |  | ★★ | PEN | Growth habits and kinetics of crystallization of poly(ethylene 2,6 | Journal of Macromolecular Science Part B / 1998 | `10.1080/00222349808220489` | Taylor & Francis | ☐ |
| 271 |  | ★★ | PET | Thermomechanical Properties of the Crystal Phase of Poly(ethylene  | Macromolecules / 1997 | `10.1021/ma961800q` | ACS | ☐ |
| 272 |  | ★★ | PLA | Structure and crystallization kinetics of poly( L ‐lactic acid) | Die Makromolekulare Chemie / 1992 | `10.1002/macp.1992.021930704` | Wiley | ☐ |
| 273 |  | ★★ | PBT | X‐ray investigation of the structure of poly(tetramethylene tereph | Journal of Polymer Science Polymer Physics Edition / 1979 | `10.1002/pol.1979.180170613` | Wiley | ☐ |
| 274 |  | ★★ | PTT | Crystallization kinetics of poly(trimethylene terephthalate) : mac | None | `10.58837/chula.the.2004.2118` | 其他 | ☐ |
| 275 |  | ★★ | PGA | Isothermal crystallization kinetics and spherulitic morphology of  | Journal of Polymer Science Part B Polymer Physics / 2007 | `10.1002/polb.21268` | Wiley | ☐ |
| 276 |  | ★★ | PBSA | Crystallization kinetics and morphology of poly(butylene succinate | Journal of Polymer Science Part B Polymer Physics / 2005 | `10.1002/polb.20539` | Wiley | ☐ |
| 277 |  | ★ | PBS | Conformational characteristics and configurational properties of p | Polymer / 2014 | `10.1016/j.polymer.2014.11.003` | Elsevier | ☐ |
| 278 |  | ★ | PEN | Conformational Characteristics, Configurational Properties, and Th | Macromolecules / 2009 | `10.1021/ma802804n` | ACS | ☐ |
| 279 |  | ★ | PBT | Chain conformation of poly(tetramethylene terephthalate) and its c | Polymer / 1976 | `10.1016/0032-3861(76)90036-7` | Elsevier | ☐ |
| 280 |  | ★ | PBT | Effect of Gamma Radiation on the Chemical Structure and Physical P | Polymers / 2026 | `10.3390/polym18172123` | 其他 | ☐ |
| 281 |  | ★ | PHB | Investigation of the effect of calcium phosphates on the structure | Perspektivnye Materialy / 2026 | `10.30791/1028-978x-2026-6-15-25` | 其他 | ☐ |
| 282 |  | ★ | PTT | Structure–property evolution of poly(ethylene terephthalate)/poly( | Journal of Applied Polymer Science / 2023 | `10.1002/app.54905` | Wiley | ☐ |
| 283 |  | ★ | PLA | Application of infrared spectroscopy in the multiscale structure c | Polymer / 2023 | `10.1016/j.polymer.2023.125985` | Elsevier | ☐ |
| 284 |  | ★ | PTT | Interfacial Structure of Polytrimethylene Terephthalate/Polyethyle | Fibres and Textiles in Eastern Europe / 2022 | `10.5604/01.3001.0015.6465` | 其他 | ☐ |
| 285 |  | ★ | PBN | Elucidation of Structures, Electronic Properties, and Chemical Bon | Condensed Matter / 2022 | `10.3390/condmat7040066` | 其他 | ☐ |
| 286 |  | ★ | PGA | Structure–Property Relationships of Poly(glycolic acid) and Poly(2 | Macromolecules / 2019 | `10.1021/acs.macromol.9b00459` | ACS | ☐ |
| 287 |  | ★ | PHB | Structures of Mixed-Tacticity Polyhydroxybutyrates | Macromolecules / 2018 | `10.1021/acs.macromol.8b01047` | ACS | ☐ |
| 288 |  | ★ | PLA | Synthesis, characterization and comparison of polyaniline 1D-struc | Superlattices and Microstructures / 2016 | `10.1016/j.spmi.2015.10.038` | Elsevier | ☐ |
| 289 |  | ★ | PBT | Smectic structure and glass transition in poly(butylene terephthal | Polymer Journal / 2010 | `10.1038/pj.2010.5` | 其他 | ☐ |
| 290 |  | ★ | PLA | Effect of the structure of the biodegradable triblock polymer poly | Polymer Science Series A / 2010 | `10.1134/s0965545x10100032` | 其他 | ☐ |
| 291 |  | ★ | PLA | Plastic Deformation of Amorphous Poly( l / dl -lactide): Structure | Biomacromolecules / 2007 | `10.1021/bm061229v` | ACS | ☐ |
| 292 |  | ★ | PTT | Phase structure and sorption/de-sorption in poly(trimethylene tere | Thermochimica Acta / 2003 | `10.1016/s0040-6031(02)00525-7` | Elsevier | ☐ |
| 293 |  | ★ | PCL | Effect of molecular weight of poly(ε-caprolactone) on interpenetra | Biomaterials / 2003 | `10.1016/s0142-9612(02)00579-3` | Elsevier | ☐ |
| 294 |  | ★ | PTT | Orientation and Structure Development in Poly(trimethylene terepht | Macromolecules / 2001 | `10.1021/ma010317z` | ACS | ☐ |
| 295 |  | ★ | PTT | Effect of zone drawing on the structure and properties of melt‐spu | Journal of Applied Polymer Science / 2001 | `10.1002/app.1803` | Wiley | ☐ |
| 296 |  | ★ | PLA | The frustrated structure of poly( l -lactide) | Polymer / 2000 | `10.1016/s0032-3861(00)00235-4` | Elsevier | ☐ |
| 297 |  | ★ | PBT | Syntheses, Characterizations, and Structures of a New Series of Al | Macromolecules / 1999 | `10.1021/ma991375b` | ACS | ☐ |
| 298 |  | ★ | PLA | Microstructure of Poly(lactide). Phase-Sensitive HETCOR Spectra of | Macromolecules / 1999 | `10.1021/ma9806864` | ACS | ☐ |
| 299 |  | ★ | PGA | Hierarchically structured polyglycolide - a biomaterial mimicking  | Macromolecular Rapid Communications / 1998 | `10.1002/(sici)1521-3927(19981201)19:12<613::aid-marc613>3.0.co;2-m` | Wiley | ☐ |
| 300 |  | ★ | PGA | Hierarchically structured polyglycolide – a biomaterial mimicking  | Macromolecular Rapid Communications / 1998 | `10.1002/(sici)1521-3927(19981201)19:12<613::aid-marc613>3.3.co;2-d` | Wiley | ☐ |
| 301 |  | ★ | PEN | Mesophase structures in poly(ethylene terephthalate), poly(ethylen | Polymers for Advanced Technologies / 1997 | `10.1002/(sici)1099-1581(199710)8:10<592::aid-pat713>3.0.co;2-h` | Wiley | ☐ |
| 302 |  | ★ | PEN | Structure and Physical Properties of Naphthalene Containing Polyes | Polymer Journal / 1996 | `10.1295/polymj.28.177` | 其他 | ☐ |
| 303 |  | ★ | PBN | Structure and Physical Properties of Naphthalene Containing Polyes | Polymer Journal / 1996 | `10.1295/polymj.28.177` | 其他 | ☐ |
| 304 |  | ★ | PET | Analysis of structure and properties of poly(ethylene terephthalat | Journal of Polymer Science Part B Polymer Physics / 1994 | `10.1002/polb.1994.090321316` | Wiley | ☐ |
| 305 |  | ★ | PET | Relating microhardness of poly(ethylene terephthalate) to microstr | Journal of Polymer Science Part B Polymer Physics / 1991 | `10.1002/polb.1991.090290706` | Wiley | ☐ |
| 306 |  | ★ | PBT | Poly(Ether/Ester)s based on poly(tetramethylene terephthalate) and | Die Makromolekulare Chemie / 1990 | `10.1002/macp.1990.021911012` | Wiley | ☐ |
| 307 |  | ★ | PEN | Processing characteristics, structure development, and properties  | Polymer Engineering and Science / 1990 | `10.1002/pen.760301205` | Wiley | ☐ |
| 308 |  | ★ | PET | Effect of chain composition of poly(ethylene terephthalate) struct | Die Makromolekulare Chemie / 1981 | `10.1002/macp.1981.021820120` | Wiley | ☐ |
| 309 |  | ★ | PTT | The structure of poly(trimethylene terephthalate) | Polymer / 1979 | `10.1016/0032-3861(79)90163-0` | Elsevier | ☐ |
| 310 |  | ★ | PET | Structure of terephthalate polymers I—Infra-red spectra and molecu | Polymer / 1969 | `10.1016/0032-3861(69)90047-0` | Elsevier | ☐ |
| 311 |  | ★ | PLA | Defects in polylactide spherulites: Ring line cracks and micropore | Polymer Degradation and Stability / 2020 | `10.1016/j.polymdegradstab.2020.109416` | Elsevier | ☐ |
| 312 |  | ★ | PTT | Three types of banded structures in highly birefringent poly(trime | Journal of Polymer Science Part B Polymer Physics / 2016 | `10.1002/polb.24037` | Wiley | ☐ |
| 313 |  | ★ | PLA | Wavenumber Dependence of FT-IR Image of Molecular Orientation in B | Macromolecules / 2013 | `10.1021/ma302560q` | ACS | ☐ |
| 314 |  | ★ | PHB | On Morphology of Polyhydroxybutyrate | Apple Academic Press eBooks / 2013 | `10.1201/b13964-25` | 其他 | ☐ |
| 315 |  | ★ | PTT | High birefringence of poly(trimethylene terephthalate) spherulite | Polymer / 2006 | `10.1016/j.polymer.2005.12.067` | Elsevier | ☐ |
| 316 |  | ★ | PTT | Miscibility, Morphology, and Thermal Properties of Poly(Trimethyle | Journal of Macromolecular Science Part B / 2004 | `10.1081/mb-200033308` | 其他 | ☐ |
| 317 |  | ★ | PLA | Structural Study of Poly( l -lactic acid) Spherulites | Biomacromolecules / 2003 | `10.1021/bm0343951` | ACS | ☐ |
| 318 |  | ★ | PEN | Excimer Laser Ablation and Morphology of Uniaxially Stretched Poly | Polymer Journal / 1999 | `10.1295/polymj.31.524` | 其他 | ☐ |
| 319 |  | ★ | PBT | Surface morphology and annealing of poly(butylene terephthalate) | Polymer International / 1995 | `10.1002/pi.1995.210380410` | Wiley | ☐ |
| 320 |  | ★ | PBT | Morphology and melting behaviour of poly(butylene terephthalate) | Polymer International / 1995 | `10.1002/pi.1995.210370106` | Wiley | ☐ |
| 321 |  | ★ | PBT | Light scattering studies on the morphology and deformation mechani | Macromolecules / 1984 | `10.1021/ma00139a024` | ACS | ☐ |
| 322 |  | ★ | PBT | Light scattering studies on the morphology and deformation mechani | Macromolecules / 1982 | `10.1021/ma00229a037` | ACS | ☐ |
| 323 |  | ★ | PET | Morphological Studies of Cold Drawn Poly(ethylene terephthalate) | Polymer Journal / 1973 | `10.1295/polymj.5.72` | 其他 | ☐ |
| 324 |  | ★ | PTT | Solvent Induced Cracking and Morphology in Banded Spherulite of Po | Polymer Journal / 2008 | `10.1295/polymj.pj2007194` | 其他 | ☐ |
| 325 |  | ★ | PBT | Morphological study on three kinds of two-dimensional spherulites  | Polymer / 2007 | `10.1016/j.polymer.2007.07.035` | Elsevier | ☐ |

## 三、操作说明

1. **先跑自动下载**（有 ⚡ 标记的）：`python src/extraction/fetch_pdf.py --on-topic-only`；注意直链可能失效或需要校园网，需实测确认。
2. 自动下载失败的，按「途径」列在校内 IP / 图书馆电子资源导航里人工下载；
3. PDF 放到 `data/literature/`，命名为 `<sanitized_doi>.pdf`（与 `corpus.pdf_path_for` 一致，否则流水线拾取不到）；
4. 下载后在「已下」列打勾，便于统计完成度；
5. **不要**整包抓取第三方数据库，也不要把 PDF 提交进仓库或对外分发。
