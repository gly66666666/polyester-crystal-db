#!/usr/bin/env python3
"""重建 Gold Set 基准：每槽位挂一个**独立、on-topic、在语料内**的 DOI。

为什么要重建（2026-10-13）：
  1. evaluate.py 按 (polymer_abbr, doi) 匹配。原 Gold Set 每成员 5 条**共用 1 个经典 DOI**，
     且其中 PET 的 Daubeny 1954 **根本不在语料里** → 抽取永远产不出该 DOI → 实测匹配 0 条。
  2. 更严重：原先填的数值存在**归因错误**。例：
       · PTT 的 4.64/6.22/18.64/98.4/93/111.5 出自 Poulin-Dandurand，
         而语料中 1979 那篇是 Desborough（报 a=4.59/b=6.21/c=18.31/β≈90）；
       · PBT 的 4.83/5.94/11.59 出自 Yokouchi 1976，Mencik 1975 报的是 c≈11.3~11.62、γ≈113.8。
     把 A 文的数值挂到 B 文的 DOI 上，基准结论将是错的。

因此本脚本采取**保守且正确**的做法：
  - 每个槽位分配一个独立、on-topic、在语料内、且已 CrossRef 核验的 DOI；
  - **数值一律清空**，status='reserved'（不参与 validate / export / evaluate），
    由人工打开原文后逐条填写（合规红线：金标准数值须人工从原文核验）；
  - 公开权威的"同晶型参考值"另行写入 canonical_reference.json，
    仅作 sanity 参考，**不绑定具体文献、不作为 gold**。

用法：
  python src/annotation/rebuild_gold_benchmark.py            # 预览（不写文件）
  python src/annotation/rebuild_gold_benchmark.py --apply    # 落盘
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
GOLD_PATH = PROJECT_ROOT / "data" / "gold_set" / "gold_set.json"
QUALITY_PATH = PROJECT_ROOT / "data" / "processed" / "corpus_quality.json"
REF_PATH = PROJECT_ROOT / "data" / "gold_set" / "canonical_reference.json"

TARGETS = ["PET", "PTT", "PBT", "PLA"]
PER_POLYMER = 5

# 数字字段（清空用）
NUM_FIELDS = ["a", "b", "c", "alpha", "beta", "gamma", "z", "rho_crystal",
              "fiber_period", "tm", "tm0", "delta_hf", "tg",
              "xtallinity_pct", "growth_rate"]
TEXT_FIELDS = ["polymorph_label", "crystal_system", "space_group",
               "chain_conformation", "helix_type"]

# 公开权威的"同晶型参考值"：仅作 sanity 参考，不绑定具体某一篇文献，不作 gold
CANONICAL_REFERENCE = {
    "_note": ("公开权威来源的同晶型参考值（非逐篇核验），仅供 sanity 检查与教学参考。"
              "**不可**作为 evaluate 的 gold，也**未**绑定到下列任何单一 DOI。"
              "逐篇精确值请以各文献原文为准。"),
    "PET": {"crystal_system": "triclinic", "space_group": "P-1",
            "a": 4.56, "b": 5.94, "c": 10.75, "alpha": 98.5, "beta": 118.0,
            "gamma": 112.0, "z": 1, "rho_crystal": 1.455,
            "tm": 256.0, "tg": 80.0, "delta_hf": 140.0,
            "sources": ["Daubeny/Bunn/Brown 1954 (10.1098/rspa.1954.0273)"]},
    "PBT": {"crystal_system": "triclinic", "space_group": "P1",
            "a": 4.83, "b": 5.94, "c": 11.59, "alpha": 99.7, "beta": 115.2,
            "gamma": 110.8, "z": 1, "rho_crystal": 1.40,
            "tm": 223.0, "tg": 45.0, "delta_hf": 140.0,
            "sources": ["Yokouchi 1976 / Mencik 1975 系列；注意 Mencik 1975 单篇报 c≈11.3~11.62、γ≈113.8"]},
    "PTT": {"crystal_system": "triclinic", "space_group": "P-1",
            "a": 4.64, "b": 6.22, "c": 18.64, "alpha": 98.4, "beta": 93.0,
            "gamma": 111.5, "z": 2, "rho_crystal": 1.43,
            "tm": 228.0, "tm0": 237.0, "tg": 40.0,
            "sources": ["Poulin-Dandurand 系列；注意 Desborough 1979 报 a=4.59/b=6.21/c=18.31/β≈90"]},
    "PLA": {"crystal_system": "orthorhombic", "space_group": "P212121",
            "a": 10.68, "b": 6.17, "c": 28.86, "alpha": 90.0, "beta": 90.0,
            "gamma": 90.0, "z": 2, "rho_crystal": 1.29,
            "tm": 175.0, "tg": 60.0, "delta_hf": 93.0, "helix_type": "10_3",
            "sources": ["Alemán 2001 (10.1021/ma001630o) 等 α 型报道"]},
}


# 标题质量词：真正报道晶体结构的优先；仅形貌/界面/模型化合物/会议摘要的靠后
STRONG_TERMS = ["crystal structure", "unit cell", "lattice", "electron diffraction",
                "x-ray", "polymorph", "helix", "crystal"]
WEAK_TERMS = ["morphology", "crystallization", "spherulite", "deformation",
              "light scattering", "interface", "interfacial", "model",
              "scimeetings", "kinetics", "shear", "modulus"]


def _rank(item: dict) -> tuple:
    """排序：晶体结构语义越强越靠前；弱语义/会议/学位其次；再按正式期刊优先。"""
    t = (item.get("title") or "").lower()
    strong = sum(1 for k in STRONG_TERMS if k in t)
    weak = sum(1 for k in WEAK_TERMS if k in t)
    has_journal = bool(item.get("journal"))
    has_year = item.get("year") is not None
    formal = 0 if (has_journal and has_year) else (1 if has_year else 2)
    return (-strong, weak, formal, -(item.get("year") or 0))


def pick(polymer: str, buckets: dict) -> list[dict]:
    on = sorted(buckets[polymer]["ontopic"], key=_rank)
    return on[:PER_POLYMER]


def main(apply: bool = False) -> None:
    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))

    assignment: dict[str, list[dict]] = {}
    for p in TARGETS:
        assignment[p] = pick(p, quality)

    print("=== 重建方案：每槽位一个独立 on-topic DOI ===")
    worksheet = []
    for p in TARGETS:
        print(f"\n{p}: 语料内 on-topic {len(quality[p]['ontopic'])} 篇，分配 {len(assignment[p])} 个槽位")
        for i, it in enumerate(assignment[p], 1):
            print(f"  {p}-{i:03d}  {it['doi']}")
            print(f"         [{it.get('year')}] {(it.get('title') or '')[:70]}")
            worksheet.append((f"{p}-{i:03d}", it))
        for j in range(len(assignment[p]) + 1, PER_POLYMER + 1):
            print(f"  {p}-{j:03d}  （无更多 on-topic 文献，槽位预留）")

    if not apply:
        print("\n（预览模式，未写文件。加 --apply 落盘。）")
        return

    # ---- 落盘：清空数值、挂独立 DOI、标记 reserved ----
    by_id = {r["gold_id"]: r for r in gold["records"]}
    for p in TARGETS:
        for i, it in enumerate(assignment[p], 1):
            gid = f"{p}-{i:03d}"
            rec = by_id.get(gid)
            if rec is None:
                continue
            rec["doi"] = it["doi"]
            rec["ref_year"] = it.get("year")
            rec["ref_source"] = it.get("journal")
            rec["ref_table"] = None
            rec["status"] = "reserved"
            for f in NUM_FIELDS:
                rec[f] = None
            for f in TEXT_FIELDS:
                rec[f] = None
            rec["annotator"] = None
            rec["confidence"] = None
            rec["notes"] = (
                "基准槽位（独立 DOI，on-topic，已在语料内且 CrossRef 核验）。"
                f"目标文献：[{it.get('year')}] {(it.get('title') or '')[:60]}。"
                "数值待人工打开原文逐条填写（晶胞 a/b/c/α/β/γ/z/ρ 与 Tm/Tm0/Tg/ΔHf 等），"
                "并补 ref_table 表/图号；填完后将 status 改为 filled。"
            )
        for j in range(len(assignment[p]) + 1, PER_POLYMER + 1):
            gid = f"{p}-{j:03d}"
            rec = by_id.get(gid)
            if rec is None:
                continue
            rec["doi"] = None
            rec["ref_year"] = None
            rec["ref_source"] = None
            rec["status"] = "reserved"
            for f in NUM_FIELDS:
                rec[f] = None
            for f in TEXT_FIELDS:
                rec[f] = None
            rec["notes"] = ("预留槽位：当前语料内已无更多 on-topic 均聚物晶体文献。"
                            "需补充定向检索（建议用单元晶胞/晶型同义词）后再分配 DOI 并填值。")

    gold["meta"]["benchmark_note"] = (
        "2026-10-13 重建：每槽位挂独立 on-topic DOI（语料内、CrossRef 核验）；"
        "数值清空待人工按原文填写（status=reserved）。"
        "公开权威参考值见 canonical_reference.json（不绑定单一文献，不作 gold）。"
    )
    GOLD_PATH.write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")

    # 参考值另存
    REF_PATH.parent.mkdir(parents=True, exist_ok=True)
    REF_PATH.write_text(json.dumps(CANONICAL_REFERENCE, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n✓ Gold Set 已重建 → {GOLD_PATH}")
    print(f"✓ 公开权威参考值（不作 gold）→ {REF_PATH}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    main(ap.parse_args().apply)
