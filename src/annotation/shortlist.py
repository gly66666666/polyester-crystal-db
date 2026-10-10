#!/usr/bin/env python3
"""Gold Set 候选文献排序 + 人工标注工作表生成（任务9 配套，推进 P1）

作用：帮你在 657 篇候选文献里快速定位"最可能给出晶胞/晶型数据"的论文，
把**书目信息**（DOI / 题录 / 年份 / 期刊）预填进 gold_set.json 各槽位的 `suggested` 字段，
并生成 docs/gold_set_curation.md 工作表。

⚠️ 重要：本脚本**只填书目，绝不自作主张填入晶胞参数与热力学数值**。
Gold Set 是评估 LLM 抽取准确率的基准，数值必须由人打开原文逐条核验后填写
（项目合规红线：每条须挂单一 DOI + 数值可回溯 + 人工核验）。

打分逻辑：
- 正向：unit cell / crystal structure / polymorph / space group / 电子衍射 /
        纤维周期 / 链构象 / WAXD / 晶系名 / 平衡熔点 等关键词（标题命中权重×2）
- 硬排除：蛋白/酶/水解酶/突变体/PDB 条目（如 "crystal structure of a mutant PET hydrolase"
        是蛋白质晶体，不是聚酯晶体，必须剔除）
- 软扣分：biodegradation / nanocomposite / blend 等与晶胞数据相关性低的主题

用法：
  python src/annotation/shortlist.py                      # 默认每成员 top-5
  python src/annotation/shortlist.py --per-polymer 8      # 多给几个备选
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
GOLD_PATH = PROJECT_ROOT / "data" / "gold_set" / "gold_set.json"
DOCS_DIR = PROJECT_ROOT / "docs"
WORKSHEET = DOCS_DIR / "gold_set_curation.md"

TARGET_POLYMERS = ["PET", "PTT", "PBT", "PLA"]

# 目标聚合物的"身份词"：候选文献必须在标题/摘要中出现这些词之一，
# 否则一律剔除。这是精度的关键——检索结果里混入了大量小分子晶体学论文
# （卟啉 / 氧化铀 / 药物 / 方法学章节），它们同样含 "crystal structure"，
# 但与聚酯结晶毫无关系。
POLYMER_TERMS = {
    "PET": ["ethylene terephthalate", "ethylene terephtalate"],
    "PTT": ["trimethylene terephthalate", "propylene terephthalate",
            "trimethylene terephtalate"],
    "PBT": ["butylene terephthalate", "tetramethylene terephthalate",
            "butylene terephtalate"],
    "PLA": ["lactic acid", "lactide", "polylactide"],
    # ---- 其余 8 个 Tier1 成员（2026-10-10 补齐，供分层抽样与后续 shortlist 使用）----
    "PEN": ["ethylene naphthalate", "naphthalene dicarboxylate",
            "naphthalate", "naphthoate"],
    "PBN": ["butylene naphthalate", "tetramethylene naphthalate"],
    "PCL": ["caprolactone", "polycaprolactone"],
    "PGA": ["glycolic acid", "glycolide", "polyglycolide", "polyglycolic"],
    "PBS": ["butylene succinate", "tetramethylene succinate",
            "butylene succinate adipate"],
    "PBSA": ["butylene succinate adipate", "butylene succinate co adipate",
             "butylene succinate adipate copolyester", "succinate adipate"],
    "PHB": ["hydroxybutyrate", "polyhydroxybutyrate", "hydroxybutyrate co",
            "hydroxyalkanoate"],
    "PHBV": ["hydroxyvalerate", "hydroxybutyrate hydroxyvalerate",
             "hydroxybutyrate co hydroxyvalerate", "hydroxyalkanoate"],
}

# 单独出现的缩写（词边界匹配，避免 petroleum / plan / place / PGA=磷酸甘油酸 之类误命中）
POLYMER_ABBR = {"PET": "pet", "PTT": "ptt", "PBT": "pbt", "PLA": "pla",
                "PEN": "pen", "PBN": "pbn", "PCL": "pcl", "PGA": "pga",
                "PBS": "pbs", "PBSA": "pbsa", "PHB": "phb", "PHBV": "phbv"}

# 缩写歧义防护：PET 也指"正电子发射断层(PET)扫描仪"，PBT/PLA 亦有其它含义。
# 仅凭缩写命中时，必须同时出现下列聚合物语境词之一，才算真的在讲这种高分子。
POLYMER_CONTEXT = [
    "polyester", "terephthalate", "polymer", "polymeric", "copolyester",
    "crystallization", "crystallisation", "spherulite", "lamellar",
    "fiber", "fibre", "film", "resin", "macromolecule", "melt spun",
    "oligomer",
    # 其余成员语境佐证（缩写在生物/医学领域常有其它含义，需语境才计分）
    "naphthalate", "succinate", "caprolactone", "lactide", "glycolide",
    "hydroxyalkanoate", "biopolyester", "polyesteramide",
]

# 正向关键词（权重）
POSITIVES = {
    "unit cell": 5, "unitcell": 5, "crystal structure": 4, "single crystal": 4,
    "polymorph": 4, "crystallography": 4, "space group": 4,
    "electron diffraction": 3, "fiber period": 3, "chain conformation": 3,
    "waxd": 3, "waxs": 2, "x ray": 2, "xray": 2, "wide angle": 2,
    "lamellar": 2, "triclinic": 2, "monoclinic": 2, "orthorhombic": 2,
    "equilibrium melting": 2, "heat of fusion": 2, "helix": 1,
    "crystal": 1, "crystallization": 1, "melting": 1, "dsc": 1,
    "saxs": 1, "density": 1, "conformation": 1, "enthalpy": 1,
}

# 硬排除（命中即剔除）
HARD_NEGATIVES = {
    "hydrolase", "esterase", "lipase", "cutinase", "enzyme", "protein",
    "mutant", "proteindatabank", "worldwide protein data bank",
}

# 软扣分
SOFT_NEGATIVES = {
    "biodegradation": 3, "biodegradable": 2, "nanocomposite": 2,
    "blend": 1, "composite": 1, "membrane": 1, "drug": 3, "tissue": 3,
}


def norm(text: str) -> str:
    """归一化：小写、连字符/下划线转空格、压缩空白。"""
    t = (text or "").lower()
    t = re.sub(r"[‐-―\-_/]", " ", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def mentions_polymer(poly: str, text: str) -> bool:
    """文本（已归一化）是否真正提到该聚合物。"""
    for term in POLYMER_TERMS.get(poly, []):
        if term in text:
            return True
    abbr = POLYMER_ABBR.get(poly)
    if not abbr:
        return False
    # 词边界匹配：norm 后两侧补空格，避免 petroleum / place 之类误命中
    if f" {abbr} " not in f" {text} ":
        return False
    # 缩写有歧义（PET=正电子发射断层扫描仪…），需额外聚合物语境佐证
    return any(ctx in text for ctx in POLYMER_CONTEXT)


def is_supplementary(doi: str) -> bool:
    """ACS 等出版商的补充材料 DOI（如 .s001 / .s002），非正文，一律剔除。"""
    return bool(re.search(r"\.s\d{3}$", doi or ""))


def score_item(it: dict, poly: str | None = None) -> int | None:
    """返回打分；命中硬排除 / 未提到目标聚合物 / 补充材料 → None。"""
    title = norm(it.get("title"))
    journal = norm(it.get("journal"))
    doi = (it.get("doi") or "").lower()
    abstract = norm(it.get("abstract") or "")

    blob = f"{title} {journal}"
    for bad in HARD_NEGATIVES:
        if bad in blob:
            return None
    if doi.startswith("10.2210/pdb"):
        return None
    if is_supplementary(doi):
        return None
    # 精度核心：必须真的在讲这个聚合物
    if poly and not (mentions_polymer(poly, title) or mentions_polymer(poly, abstract)):
        return None

    s = 0
    for phrase, w in POSITIVES.items():
        if phrase in title:
            s += w * 2
        if phrase in abstract:
            s += w
    for phrase, w in SOFT_NEGATIVES.items():
        if phrase in title:
            s -= w * 2
        elif phrase in abstract:
            s -= w
    return s


def rank(polymers: list[str]) -> dict[str, list[dict]]:
    data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for poly in polymers:
        items = data.get(poly, [])
        scored = []
        for it in items:
            s = score_item(it, poly)
            if s is None:
                continue
            scored.append((s, it))
        scored.sort(key=lambda x: -x[0])
        out[poly] = [
            {
                "doi": it.get("doi"), "title": it.get("title"),
                "journal": it.get("journal"), "year": it.get("year"),
                "authors": it.get("authors"), "score": s,
            }
            for s, it in scored
        ]
    return out


def write_suggestions(ranked: dict[str, list[dict]], per_polymer: int) -> int:
    """把候选书目写入 gold_set.json 各槽位的 suggested（不覆盖已填记录）。"""
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    n = 0
    for rec in gold["records"]:
        if rec.get("status") == "filled":
            continue  # 已人工标注的槽位不动
        poly = rec["polymer_abbr"]
        cands = ranked.get(poly, [])
        idx = int(rec["gold_id"].split("-")[-1]) - 1
        if 0 <= idx < len(cands) and idx < per_polymer:
            c = cands[idx]
            rec["suggested"] = {
                "doi": c["doi"], "title": c["title"], "journal": c["journal"],
                "year": c["year"], "score": c["score"],
                "note": "候选书目（自动排序，非人工核验数值）；请打开原文确认后再填数值",
            }
            n += 1
    GOLD_PATH.write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
    return n


def write_worksheet(ranked: dict[str, list[dict]], per_polymer: int) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gold Set 人工标注工作表",
        "",
        "> 生成器：`src/annotation/shortlist.py`（自动重跑可刷新候选）",
        "> **数值必须由人打开原文逐条核验后填写**——本表只给书目线索，不含任何晶胞/热力学数值。",
        "> 合规红线：每条须挂单一 DOI；只记数值性事实 + 表/图号；禁止插值或推测。",
        "",
        "## 填写字段清单（每个槽位）",
        "",
        "| 分组 | 字段 | 单位 |",
        "|---|---|---|",
        "| 晶型 | polymorph_label, crystal_system, space_group, chain_conformation | — |",
        "| 晶胞 | a, b, c | Å |",
        "| 晶系角 | alpha, beta, gamma | ° |",
        "| 其它结构 | z, rho_crystal, fiber_period | 个 / g·cm⁻³ / Å |",
        "| 热历史 | t_c | °C |",
        "| 热力学 | tm, tm0, delta_hf, tg | °C / °C / J·g⁻¹ / °C |",
        "| 其它 | xtallinity_pct, growth_rate | % / nm·s⁻¹ |",
        "| 溯源 | doi, ref_year, ref_source, ref_table(表/图号), confidence, annotator | — |",
        "",
    ]
    for poly in TARGET_POLYMERS:
        cands = ranked.get(poly, [])[:per_polymer]
        lines.append(f"## {poly}（候选 {len(cands)} 篇）")
        lines.append("")
        lines.append("| 槽位 | 分数 | 年份 | 期刊 | 标题 | DOI |")
        lines.append("|---|---|---|---|---|---|")
        for i, c in enumerate(cands, 1):
            title = (c["title"] or "")[:70]
            lines.append(
                f"| {poly}-{i:03d} | {c['score']} | {c['year'] or '?'} | "
                f"{c['journal'] or '?'} | {title} | `{c['doi']}` |"
            )
        lines.append("")
    lines += [
        "## 填写命令模板",
        "",
        "打开原文找到晶胞表后，用下面模板录入（数值替换为原文值，`ref_table` 写清表/图号）：",
        "",
        "```bash",
        "python src/annotation/gold_set_annotator.py add --json '{",
        '  \"gold_id\": \"PET-001\",',
        '  \"polymer_abbr\": \"PET\",',
        '  \"doi\": \"<原文 DOI>\",',
        '  \"ref_year\": 1954, \"ref_source\": \"<期刊>\", \"ref_table\": \"Table 2\",',
        '  \"polymorph_label\": \"triclinic\", \"crystal_system\": \"triclinic\",',
        '  \"space_group\": \"P-1\",',
        '  \"a\": 4.56, \"b\": 5.94, \"c\": 10.75,',
        '  \"alpha\": 98.5, \"beta\": 118.0, \"gamma\": 112.0,',
        '  \"z\": 1, \"rho_crystal\": 1.455, \"fiber_period\": 10.75,',
        '  \"tm\": 255.0, \"tm0\": 280.0, \"delta_hf\": 140.0, \"tg\": 75.0,',
        '  \"annotator\": \"葛陆熠\", \"confidence\": \"high\",',
        '  \"notes\": \"已核对原文 Table 2\"',
        "}'",
        "```",
        "",
        "填完用以下命令校验与统计：",
        "```bash",
        "python src/annotation/gold_set_annotator.py validate",
        "python src/annotation/gold_set_annotator.py stats",
        "python src/annotation/gold_set_annotator.py export-db",
        "```",
        "",
    ]
    WORKSHEET.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gold Set 候选排序与标注工作表")
    ap.add_argument("--per-polymer", type=int, default=5, help="每成员保留的候选数（默认5）")
    ap.add_argument("--no-write-gold", action="store_true", help="只生成工作表，不写 gold_set.json")
    args = ap.parse_args()

    ranked = rank(TARGET_POLYMERS)
    total_avail = {p: len(v) for p, v in ranked.items()}
    print("各成员可用候选（已剔除蛋白/酶/PDB 干扰项）：")
    for p in TARGET_POLYMERS:
        print(f"  {p}: {total_avail.get(p, 0)} 篇")

    n = 0 if args.no_write_gold else write_suggestions(ranked, args.per_polymer)
    write_worksheet(ranked, args.per_polymer)

    print(f"✓ 已为 {n} 个槽位写入候选书目建议（suggested 字段）")
    print(f"✓ 工作表已生成：{WORKSHEET}")


if __name__ == "__main__":
    main()
