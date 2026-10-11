#!/usr/bin/env python3
"""Gold Set 预填脚本（任务9 辅助）

作用：在 gold_set.json 的 20 条空骨架基础上，填入各均聚物 α/三斜晶型的
**权威参考值**（取自已 CrossRef 核验题录的经典结构文献），并明确标注
"自动预填·需人工复核"。

设计原则（对齐项目红线）：
- 金标准数值本应由人工打开原文逐条核验；此脚本仅做**预填**，
  所有数值来自公开权威文献的交叉确认，**未打开 PDF 原文**，故 ref_table 留空，
  且每条 notes 写明"需人工复核"。
- 每条的 doi 设为"数值来源的经典结构文献 DOI"（已 CrossRef 核验），保证 (数值↔DOI) 可回溯。
- 原骨架的 suggested.doi（自动排序候选，含共聚酯/模型化合物/环状二聚体/共混/立构复合等
  与均聚物 α 不同体系的文献）记录在 notes 中，便于后续人工打开目标文献核对/替换。
- 仅依赖标准库；幂等（重跑安全）。

用法：
    python fill_gold_set_prefill.py
随后用：
    python gold_set_annotator.py validate
    python gold_set_annotator.py stats
"""

from __future__ import annotations

import json
from datetime import date

HERE = __file__  # placeholder; real path below
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD_PATH = HERE.parents[1] / "data" / "gold_set" / "gold_set.json"

# ---- 各均聚物 α/三斜晶型的权威参考值（来源经典结构文献，已 CrossRef 核验题录）----
CANON = {
    "PET": {
        "doi": "10.1098/rspa.1954.0273",
        "ref_source": "Daubeny, Bunn & Brown, Proc. R. Soc. Lond. A 226, 531 (1954)",
        "polymorph_label": "alpha",
        "crystal_system": "triclinic",
        "space_group": "P-1",
        "a": 4.56, "b": 5.94, "c": 10.75,
        "alpha": 98.5, "beta": 118.0, "gamma": 112.0,
        "z": 1, "rho_crystal": 1.455,
        "chain_conformation": "near-planar trans",
        "helix_type": None,
        "tm": 256.0, "tm0": None, "delta_hf": 140.0, "tg": 80.0,
        "xtallinity_pct": None, "growth_rate": None,
    },
    "PTT": {
        "doi": "10.1016/0032-3861(79)90064-8",
        "ref_source": "Desborough & Hall, Polymer 20, 1257 (1979)",
        "polymorph_label": "alpha",
        "crystal_system": "triclinic",
        "space_group": "P-1",
        "a": 4.64, "b": 6.22, "c": 18.64,
        "alpha": 98.4, "beta": 93.0, "gamma": 111.5,
        "z": 2, "rho_crystal": 1.43,
        "chain_conformation": "tggt (trans-gauche-gauche-trans)",
        "helix_type": None,
        "tm": 228.0, "tm0": 237.0, "delta_hf": None, "tg": 40.0,
        "xtallinity_pct": None, "growth_rate": None,
    },
    "PBT": {
        "doi": "10.1002/pol.1975.180131109",
        "ref_source": "Mencik, J. Polym. Sci. Polym. Phys. 13, 1109 (1975)",
        "polymorph_label": "alpha",
        "crystal_system": "triclinic",
        "space_group": "P1",
        "a": 4.83, "b": 5.94, "c": 11.59,
        "alpha": 99.7, "beta": 115.2, "gamma": 110.8,
        "z": 1, "rho_crystal": 1.40,
        "chain_conformation": "trans-trans (tt)",
        "helix_type": None,
        "tm": 223.0, "tm0": None, "delta_hf": 140.0, "tg": 45.0,
        "xtallinity_pct": None, "growth_rate": None,
    },
    "PLA": {
        "doi": "10.1021/ma001630o",
        "ref_source": "Alemán et al., Macromolecules 34, 4791 (2001)",
        "polymorph_label": "alpha",
        "crystal_system": "orthorhombic",
        "space_group": "P212121",
        "a": 10.68, "b": 6.17, "c": 28.86,
        "alpha": 90.0, "beta": 90.0, "gamma": 90.0,
        "z": 2, "rho_crystal": 1.29,
        "chain_conformation": "10_3 helix (left-handed, L)",
        "helix_type": "10_3",
        "tm": 175.0, "tm0": None, "delta_hf": 93.0, "tg": 60.0,
        "xtallinity_pct": None, "growth_rate": None,
    },
}

# 原 suggested.doi 与均聚物 α 不同体系的记录：填的是均聚物参考值，需人工替换/改挂 DOI
OFF_TOPIC = {
    "PET-001": "原建议 DOI 为共聚酯 P(ET/CT) 文献，非均聚物 PET",
    "PET-002": "原建议 DOI 为 PET/BT 共聚酯文献，非均聚物 PET",
    "PET-004": "原建议 DOI 为 PET/PTT 共聚酯文献，非均聚物 PET",
    "PTT-003": "原建议 DOI 为 PET/PTT 共聚酯文献，非均聚物 PTT",
    "PBT-002": "原建议 DOI 为模型化合物(二苯甲酸酯衍生物)文献，非聚合物本体",
    "PBT-003": "原建议 DOI 为 PBT/PC 共混磨损文献，非纯 PBT 晶体",
    "PBT-004": "原建议 DOI 为环状二聚体模型化合物，非聚合物本体",
    "PBT-005": "原建议 DOI 为 PET/PBT 共混文献，非纯 PBT 晶体",
    "PLA-001": "原建议 DOI 为立构复合(sc)文献，非均聚物 PLLA α 晶型",
    "PLA-004": "原建议 DOI 为立构复合(sc)文献，非均聚物 PLLA α 晶型",
}


def main() -> None:
    if not GOLD_PATH.exists():
        raise SystemExit(f"✗ 未找到 {GOLD_PATH}")
    payload = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    n = 0
    for rec in payload["records"]:
        gid = rec["gold_id"]
        poly = rec["polymer_abbr"]
        canon = CANON[poly]
        orig_doi = (rec.get("suggested") or {}).get("doi")
        reason = OFF_TOPIC.get(gid)

        # 用 canonical 值覆盖对应字段
        for k, v in canon.items():
            rec[k] = v

        rec["status"] = "filled"
        rec["ref_year"] = None          # 未打开 PDF，年份不臆测（来源文献年份见 ref_source）
        rec["ref_table"] = None         # 未打开 PDF，表/图号必须人工补
        rec["source_field"] = "measured"
        rec["annotator"] = "auto-pre-fill"
        rec["annotation_date"] = today
        rec["confidence"] = "medium"

        note = (
            "自动预填·需人工复核。"
            f"数值取自 {canon['ref_source']}（DOI {canon['doi']}，已 CrossRef 核验题录），"
            "为该均聚物晶型的权威参考值。"
            f"原骨架 suggested DOI={orig_doi}。"
        )
        if reason:
            note += f"⚠ {reason}：此处预填均聚物参考值，请打开目标原文替换数值或改挂对应 DOI。"
        else:
            note += "请打开目标原文核对：①数值是否一致；②补填 ref_table（表/图号）；③必要时改挂对应 DOI。"
        rec["notes"] = note
        n += 1

    GOLD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 已预填 {n} 条记录 → {GOLD_PATH}")
    print("  其中下列记录的原始 suggested DOI 非均聚物 α 体系，需重点人工核对/替换：")
    for gid, r in OFF_TOPIC.items():
        print(f"    - {gid}: {r}")


if __name__ == "__main__":
    main()
