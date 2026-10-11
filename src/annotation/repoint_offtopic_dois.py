#!/usr/bin/env python3
"""将 10 条 off-topic 记录的 notes 改写为"已按用户指示改挂均聚物经典文献"口径。

前提：fill_gold_set_prefill.py 已把全部 20 条的 doi 统一设为对应均聚物经典文献 DOI，
故这 10 条的 doi 字段已是经典文献。本脚本只修正 notes 文字，消除"请改挂 DOI"的歧义，
并记录原始 suggested DOI 与 off-topic 原因，保留"打开经典文献补 ref_table / 复核"的提示。

幂等：重跑安全。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD_PATH = HERE.parents[1] / "data" / "gold_set" / "gold_set.json"

SHORT = {
    "PET-001": "共聚酯 P(ET/CT)",
    "PET-002": "PET/BT 共聚酯",
    "PET-004": "PET/PTT 共聚酯",
    "PTT-003": "PET/PTT 共聚酯",
    "PBT-002": "模型化合物(二苯甲酸酯衍生物)",
    "PBT-003": "PBT/PC 共混磨损",
    "PBT-004": "环状二聚体模型化合物",
    "PBT-005": "PET/PBT 共混",
    "PLA-001": "立构复合(sc)文献",
    "PLA-004": "立构复合(sc)文献",
}


def main() -> None:
    payload = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    n = 0
    for rec in payload["records"]:
        gid = rec["gold_id"]
        if gid not in SHORT:
            continue
        canon = {k: rec.get(k) for k in ("ref_source", "doi", "polymer_abbr")}
        orig_doi = (rec.get("suggested") or {}).get("doi")
        rec["notes"] = (
            "自动预填·需人工复核。"
            f"数值取自 {canon['ref_source']}（DOI {canon['doi']}，已 CrossRef 核验题录），"
            "为该均聚物晶型的权威参考值。"
            f"原骨架 suggested DOI={orig_doi}（{SHORT[gid]}），"
            "已按用户指示将该记录 DOI 统一改挂到上述均聚物经典文献。"
            "仍请打开该经典文献原文：① 补填 ref_table（表/图号）；② 复核晶胞/热力学数值。"
        )
        n += 1
    GOLD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 已更新 {n} 条 off-topic 记录的 notes（doi 字段此前已为经典文献）。")


if __name__ == "__main__":
    main()
