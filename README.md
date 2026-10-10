# 聚酯家族结晶数据库构建与智能检索系统

> AI 驱动的半结晶性聚酯家族结晶结构数据库 + 抽取 / 检索流水线
>
> 南京大学「金种子」早期科研训练项目 · 有训书院 · 导师：胡文兵（高分子结晶领域 APS Fellow）

---

## 1. 项目是什么

本仓库构建一个面向**半结晶性聚酯家族**的结晶结构数据库，并配套一套
**文献 → LLM 抽取 → 结构化入库 → 检索** 的自动化流水线。

一句话定位：**聚焦"一类"高分子（聚酯家族），而非所有高分子、也非单一聚合物。**
目标成员为 12 个 Tier1 聚酯（PET / PBT / PEN / PBN / PLLA / PCL / PGA / PBS / PBSA / PHB / PHBV
+ 芳香族/脂肪族分类），并以"一条 = 一个观测行（一组 Tc / 一组结构）"为计数口径，
规模化阶段目标 ≥ 300 条观测。

---

## 2. 项目组成（目录与模块）

```
polyester-crystal-db/
│
├── data/                          # 数据层
│   ├── polymer_crystal.db          # ★ SQLite 主库（当前 12 个聚合物成员，观测行待抽取填充）
│   ├── gold_set/
│   │   └── gold_set.json          # Gold Set 基准：20 个空槽位骨架（PET/PTT/PBT/PLA 各 5）
│   ├── literature/
│   │   └── search_results.json     # 文献检索结果：657 篇不重复（CrossRef，按成员分组）
│   ├── processed/                  # 抽取流水线中间产物（checkpoint / 抽取输出，gitignore）
│   └── raw_cifs/                   # CIF 抓取目录（gitignore，受 COD/CCDC 许可约束）
│
├── src/
│   ├── database/                   # 数据模型
│   │   ├── schema.sql              # 数据库 schema v1.1（7 张表，四层模型，见 §3）
│   │   └── init_db.py              # 初始化脚本：写入 12 个 Tier1 成员（cru_smiles 留空待回填）
│   │
│   ├── extraction/                 # 抽取流水线（P2 框架）
│   │   ├── literature_search.py    # 文献检索（CrossRef REST API + mailto polite pool + DOI 去重）
│   │   ├── search_terms.json       # 12 成员检索词（中英文 + 晶型专项词）
│   │   ├── llm_client.py           # LLM 后端抽象：TokenPlan（墨点计划）/ mock / local
│   │   ├── prompts.py              # 抽取输出合约（宁 null 不许编 / 置信自评 / 出处定位）
│   │   ├── extractor.py            # LLM 返回 JSON 鲁棒解析 + 字段映射到 schema 列名
│   │   ├── normalizer.py           # 结构→polymorphs(L1) / 实测→observations(L2) 拆分 + 置信阈值
│   │   ├── store.py                # 幂等落库（L3→L1→L2，按 doi+polymer+polymorph+t_c 去重）
│   │   ├── corpus.py               # 检索结果 → 抽取任务（PDF 优先，摘要兜底）
│   │   ├── pipeline.py             # 编排 + checkpoint/resume + --dry-run
│   │   └── evaluate.py             # Gold Set 字段级 Precision/Recall/F1 评测（P1 验收 ≥80%）
│   │
│   └── annotation/                 # 标注工具
│       ├── gold_set_annotator.py   # Gold Set 标注：init / list-candidates / add / validate / stats / export-db
│       ├── shortlist.py            # 候选文献相关性打分排序（12 成员身份词 + 缩写语境保护）
│       ├── verify_refs.py          # 参考文献DOI的CrossRef核验（写入前必须核验）
│       ├── fetch_citations.py      # 批量抓取已核验DOI的完整题录（论文引用用）
│       ├── oa_survey.py            # 全文可获取性分层抽样实测（论文结果可复现）
│       └── make_oa_table.py        # 把实测统计渲染为论文LaTeX表格
│
├── paper/                          # 论文（中文稿）
│   ├── main.tex                    # 四层数据模型 + 抽取流水线 + 质量治理（XeLaTeX 编译 ×2）
│   ├── tab_oa.tex                  # OA实测表（由 make_oa_table.py 自动生成，勿手改）
│   └── main.pdf
│
├── docs/                           # 数据字典 / 抽取决议 / CHANGELOG（规划中，待补）
├── requirements.txt                # Python 依赖清单
└── .gitignore
```

> 设计总纲见项目同级的《聚酯家族结晶数据库-执行计划.md》（含 P0–P7 时间表、预算、合规红线）。

---

## 3. 数据模型（四层，对齐 schema v1.1）

| 层级 | 表 | 内容 |
|------|----|------|
| **L0** | `polymers` | 聚合物成员：缩写、中英文名、家族分支、分子量、手性、立构策略、Tier |
| **L1** | `polymorphs` | 晶型：晶体结构 **a/b/c、α/β/γ、z、ρ_crystal、空间群、晶系、链构象、纤维周期** |
| **L2** | `observations` | 观测行：一条 = 一组 Tc/结构 + 热力学/动力学实测（tm/tm0/tg/ΔHf/结晶度/生长速率…）+ 溯源 DOI |
| **L2.5** | `atomic_coordinates` / `properties` | 全原子坐标（高分子 CIF 罕见，预留）/ 通用物性扩展表 |
| **L3** | `literature_sources` | 文献来源：DOI、题录、抽取模型版本、抽取时间、`raw_snippet`（仅数值性事实片段） |

**关键约定**：晶胞参数属于 L1（`polymorphs`），`observations` 通过 `polymorph_id` 关联，
**不**在 L2 重复存晶胞——同一聚合物不同文献的略不同晶胞作为"分歧记录"全部保留（冲突消解见计划 §4.4）。

---

## 4. 工作流与当前进度

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 | 仓库骨架、schema、12 成员初始化、检索词、文献检索（657 篇）、Gold Set 工具、抽取流水线框架 | ✅ 已完成 |
| **P1** | **Gold Set 标注（≥20 条人工 100% 复核）+ 字段抽取准确率报告（≥80%）** | 🚧 进行中（0/20 已填） |
| P2 | 规模化抽取（≥150 条观测、覆盖 ≥8 成员、单位归一 + 冲突消解） | 🧩 框架就绪，待接入墨点密钥跑真实批次 |
| P3–P5 | 建模（T1/T2/T3）/ 语义检索 / 前端开源 | ⏳ 规划 |
| P6–P7 | 论文（中文核心驱动结题 + 英文非 OA 期刊）/ 结题 | ⏳ 规划 |

**本次已提交内容**：P0 全部（任务 1–9）+ P2 抽取流水线框架。

---

## 5. 快速开始

```bash
# 1) 环境（Python ≥ 3.11）
pip install -r requirements.txt

# 2) 初始化数据库（写入 12 个 Tier1 成员）
python src/database/init_db.py

# 3) 文献检索（首次会向 data/literature/search_results.json 写入候选文献）
python -m src.extraction.literature_search --polymers PET,PLA --per-term 5   # 快速验证
python -m src.extraction.literature_search                                 # 全量

# 4) Gold Set 标注（PET/PTT/PBT/PLA 各标 5 条人工基准）
python src/annotation/gold_set_annotator.py init
python src/annotation/gold_set_annotator.py list-candidates PET   # 选 DOI
python src/annotation/gold_set_annotator.py add --json '{...}'    # 录入（见工具 --help）
python src/annotation/gold_set_annotator.py validate
python src/annotation/gold_set_annotator.py export-db            # 落地到主库 observations(review_status='gold')

# 5) 抽取流水线（无需密钥即可用 mock 跑通全流程）
python -m src.extraction.pipeline --backend mock --limit 10 --dry-run
#    配好墨点密钥后跑真实抽取：
export TOKENPLAN_API_KEY=<YOUR_KEY>        # 书生·墨点计划，见 tokenplan-guide.tex
python -m src.extraction.pipeline --backend tokenplan --polymers PET,PLA --limit 50

# 6) 评测字段级准确率（Gold Set vs 抽取结果）
python -m src.extraction.evaluate --extracted data/processed/extraction_output.json
```

流水线支持断点续跑（`--resume` 默认开启，已处理 DOI 落盘 `data/processed/extraction_checkpoint.json`），
重复跑不会重复花钱。

---

## 6. 合规与版权红线

- **PoLyInfo（NIMS）仅作交叉校验，绝不入库**——课题组有注册账号，但受版权与注册制约束。
- **所有抽取值必须可回溯到单一 DOI**；无 DOI 的一律不入库（合规硬约束）。
- **只存数值性事实 + 出处定位（表/图号）**，不整段复制原文、不复制图表、不整包抓取第三方数据库。
- 每条抽取记录保留 `extraction_model` / `extraction_version` / `extraction_time`，
  一旦外部格式变化可只重跑受影响批次。

---

## 7. 技术栈

- 存储：SQLite（单文件，零运维）
- 检索源：CrossRef REST API（文献元数据）、PoLyInfo（仅校验）
- LLM 抽取：书生·墨点计划（OpenAI 兼容，`deepseek-v4-flash-0731` 性价比首选），可切换本地/开发机 CPU 档
- 语义检索（规划）：sentence-transformers + faissegg
- 前端/服务（规划）：Gradio / Flask
- 运行约束：开发机仅用于 T2/T3 批量推理，**不挂 Gradio**（7×24h 上限 + 无公网）

---

## 8. 许可证与声明

本仓库代码以 MIT 许可证开源；**数据库内容**为科研结构化抽取成果，引用文献数据版权归原作者，
使用须遵守原始出版方与 PoLyInfo 等来源的使用条款。
