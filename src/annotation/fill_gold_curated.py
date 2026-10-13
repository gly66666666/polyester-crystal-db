#!/usr/bin/env python3
"""按"可归因性"分级填充 Gold Set 基准槽位（2026-10-14）

填值规则（承 2026-10-13 归因错误教训）：
  high  —— 数值可确认出自**该篇论文本身**（不同文献同晶型数值确有差异，必须逐篇归属）
  low   —— 该论文很可能报道该晶型的通行值，但**无法确认等于本篇实际数字**，
           显式标注"务必打开原文核对"，不得当作已核验真值
  不填  —— 论文本身不含均聚物晶胞数据（模型化合物 / 纯形貌 / 界面 / 会议摘要 /
           无法获取的学位论文）→ 保持 reserved

已核实的可归因数值：
  · Desborough 1979（PTT-001）：a=4.59 b=6.21 c=18.31 α=98.0 β=90.0 γ=111.7
    （注意：常被引用的 4.64/6.22/18.64/β=93 出自 Poulin-Dandurand，不是这一篇）
  · Mencik 1975（PBT-001）：a=4.83 b=5.96 c=11.62 α=99.9 β=115.2 γ=113.8，ρcalc=1.41
    （注意：4.83/5.94/11.59/γ=110.8 出自 Yokouchi 1976；Mencik 单篇另有 c≈11.3 的说法）
  · Alemán 2001（PLA-003）：a=10.683 b=6.170 c=28.860，正交 P212121，10_3 螺旋，z=2
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
GOLD_PATH = PROJECT_ROOT / "data" / "gold_set" / "gold_set.json"

TODAY = date.today().isoformat()
ANNOTATOR = "auto-pre-fill"

# ---------- 各晶型数值（按来源分组） ----------
CELL = {
    "PET_canonical": dict(crystal_system="triclinic", space_group="P-1",
                          a=4.56, b=5.94, c=10.75, alpha=98.5, beta=118.0, gamma=112.0,
                          z=1, rho_crystal=1.455, chain_conformation="near-planar trans"),
    "PTT_desborough": dict(crystal_system="triclinic", space_group="P-1",
                           a=4.59, b=6.21, c=18.31, alpha=98.0, beta=90.0, gamma=111.7,
                           z=2, rho_crystal=None, chain_conformation="tggt"),
    "PTT_canonical": dict(crystal_system="triclinic", space_group="P-1",
                          a=4.64, b=6.22, c=18.64, alpha=98.4, beta=93.0, gamma=111.5,
                          z=2, rho_crystal=1.43, chain_conformation="tggt"),
    "PBT_mencik": dict(crystal_system="triclinic", space_group="P1",
                       a=4.83, b=5.96, c=11.62, alpha=99.9, beta=115.2, gamma=113.8,
                       z=1, rho_crystal=1.41, chain_conformation="tt"),
    "PLA_aleman": dict(crystal_system="orthorhombic", space_group="P212121",
                       a=10.683, b=6.170, c=28.860, alpha=90.0, beta=90.0, gamma=90.0,
                       z=2, rho_crystal=1.29, helix_type="10_3",
                       chain_conformation="10_3 helix"),
    "PLA_canonical": dict(crystal_system="orthorhombic", space_group="P212121",
                          a=10.68, b=6.17, c=28.86, alpha=90.0, beta=90.0, gamma=90.0,
                          z=2, rho_crystal=1.29, helix_type="10_3",
                          chain_conformation="10_3 helix"),
}

# ---------- 逐槽位策展（gold_id -> 使用哪组值 / 置信 / 备注） ----------
CURATED = {
    "PET-001": ("PET_canonical", "low",
                "1995 年 a 轴取向高结晶 PET 的形态与晶体结构研究，应报道 PET 通行三斜晶胞；"
                "未确认等于本篇实际数字，务必打开原文核对表号与数值。"),
    "PET-002": ("PET_canonical", "low",
                "1988 年取向 PET 晶体模量与结构，应引用 PET 通行三斜晶胞；"
                "未确认等于本篇实际数字，务必核对。"),
    "PTT-001": ("PTT_desborough", "high",
                "Desborough & Hall 1979 原文报道值（a=4.59/b=6.21/c=18.31/β≈90）。"
                "⚠ 常被引用的 4.64/6.22/18.64/β=93 出自 Poulin-Dandurand，非本篇。"),
    "PTT-002": ("PTT_canonical", "low",
                "Macromolecules 2000 环带球晶与晶体结构研究，应报道 PTT 通行三斜晶胞；"
                "未确认等于本篇实际数字，务必核对。"),
    "PBT-001": ("PBT_mencik", "high",
                "Mencik 1975 索引的 α 晶胞（含 ρcalc≈1.41）。"
                "⚠ 4.83/5.94/11.59/γ=110.8 出自 Yokouchi 1976；Mencik 另有 c≈11.3 的说法，"
                "若原文与此处不符请以原文为准。"),
    "PLA-001": ("PLA_canonical", "low",
                "本篇为 2003 年「α 型螺旋畸变与晶体结构」(ma0348674)，应报道接近的 α 型正交晶胞；"
                "未确认等于本篇实际数字，务必核对。"),
    "PLA-002": ("PLA_canonical", "low",
                "本篇为 2019 年「高压诱导 PLLA 片晶增厚」(polymer.2019.05.020)，应报道 α 型正交晶胞；"
                "高压条件可能使数值略有偏移，务必核对。"),
    "PLA-003": ("PLA_aleman", "high",
                "Alemán 2001 原文报道值（10.683/6.170/28.860，P212121，10_3 螺旋，z=2）。"),
}

# 明确不填（论文不含均聚物晶胞），保持 reserved
SKIP = {
    "PBT-002": "1985 年文为四亚甲基二醇二苯甲酸酯**模型化合物**研究，非聚合物本体晶胞，不适合填均聚物晶胞。",
    "PBT-003": "1982 年文为光散射形貌与形变机理，不含晶胞参数。",
    "PTT-003": "Chulalongkorn 学位论文（剪切诱导结晶），当前无法获取全文核验，保持预留。",
    "PTT-004": "Chulalongkorn 学位论文（结晶动力学），当前无法获取全文核验，保持预留。",
    "PTT-005": "2022 年文为 PTT/PET **界面结构**，非均聚物本体晶胞。",
    "PLA-004": "2021 年 SciMeetings 会议摘要，数据不充分。",
}


def main(apply: bool = False) -> None:
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    by_id = {r["gold_id"]: r for r in gold["records"]}

    n_high = n_low = n_skip = 0
    for gid, (cell_key, conf, note) in CURATED.items():
        rec = by_id.get(gid)
        if rec is None or not rec.get("doi"):
            print(f"  ! 跳过 {gid}：无 DOI")
            continue
        cell = CELL[cell_key]
        for k, v in cell.items():
            rec[k] = v
        rec["polymorph_label"] = "alpha"
        rec["source_field"] = "measured"
        rec["status"] = "filled"
        rec["annotator"] = ANNOTATOR
        rec["annotation_date"] = TODAY
        rec["confidence"] = conf
        rec["notes"] = (
            f"自动预填（confidence={conf}）。{note} "
            "ref_table 待补原文表/图号；热力学量（Tm/Tm0/Tg/ΔHf）本类结构文献通常未给，留空待补。"
        )
        n_high += (conf == "high")
        n_low += (conf == "low")
        print(f"  填 {gid}  [{conf:4s}]  {rec['doi']}")

    for gid, why in SKIP.items():
        rec = by_id.get(gid)
        if rec is None:
            continue
        rec["status"] = "reserved"
        rec["notes"] = f"保持预留：{why}"
        n_skip += 1
        print(f"  预留 {gid}  {why[:56]}")

    print(f"\n合计：high {n_high} / low {n_low} / 预留 {n_skip}")

    if not apply:
        print("（预览模式，未写文件。加 --apply 落盘。）")
        return

    GOLD_PATH.write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 已写入 {GOLD_PATH}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    main(ap.parse_args().apply)
