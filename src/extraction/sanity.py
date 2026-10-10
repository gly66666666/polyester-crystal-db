#!/usr/bin/env python3
"""交叉校验 / 越界 sanity（执行计划 §4.3）

§4.3 原文要求：
- 用 Tm/Tg/结晶温度的分布做 sanity check，超出家族合理区间的记录打 conflict_flag 回看原文。
- 成员自身的重复测定分布本身就是质量信号：把同一 polymer_id 下所有 rho_crystal
  画成一维散点，离群值必然是手写 / 单位 / 单位换算错误。

本模块做两件事：
1. **硬区间检查**：值超出"聚酯家族可能范围"→ 标记（几乎一定是录入或单位错误）。
2. **稳健离群检查**：同一成员同一字段的多次测定，用 中位数 + MAD（中位数绝对偏差）
   计算稳健 z 值，|z| > 阈值 → 标记。用 MAD 而非均值/标准差，是因为少量严重错误值
   会把均值和标准差本身带偏（这正是离群点检测的经典陷阱）。
   同时输出一维文本散点（sparkline），便于肉眼确认分布形态。

注意：PoLyInfo 仅作校验源、不入库；本模块只在库内数据上做自洽性检查。
"""

from __future__ import annotations

import sqlite3
from statistics import median
from typing import Optional

# 家族合理硬区间（聚酯半结晶高分子；超出几乎必然是错误）
HARD_RANGES = {
    "a": (0.3, 60.0), "b": (0.3, 60.0), "c": (0.3, 60.0),
    "fiber_period": (0.5, 60.0),
    "alpha": (30.0, 180.0), "beta": (30.0, 180.0), "gamma": (30.0, 180.0),
    "rho_crystal": (0.8, 2.0),
    "t_c": (-50.0, 350.0),
    "tm": (0.0, 400.0), "tm0": (0.0, 420.0), "tg": (-150.0, 250.0),
    "delta_hf": (0.0, 400.0),
    "xtallinity_pct": (0.0, 100.0),
    "growth_rate": (1e-6, 1e5),
    "long_period": (1.0, 200.0), "lamellar_thickness": (0.5, 200.0),
    "z": (1.0, 16.0), "mw": (100.0, 1e7), "mn": (100.0, 1e7),
    "pdi": (1.0, 50.0), "t_half": (1e-4, 1e5), "anneal_t": (-50.0, 350.0),
}

# 稳健 z 阈值；样本数下限（太少点 MAD 不稳，不做统计离群判定）
Z_THRESHOLD = 3.5
MIN_N_FOR_OUTLIER = 4

# 参与 sanity 的字段
CHECK_FIELDS = list(HARD_RANGES.keys())

# **实验条件**字段（研究者主动设定的自变量）：不同取值是合法实验设计，不是错误。
# 这类字段只做硬区间检查（Tc=999°C 仍是不可能的），
# **不做**统计离群判定——否则多温度点的实验会被整片误报为"离群"。
CONDITION_FIELDS = {"t_c", "anneal_t", "anneal_time_h", "cooling_rate", "draw_ratio"}


def _sparkline(values: list[float], width: int = 40) -> str:
    """一维文本散点：把值映射到 width 列，同一列多个值用数字表示堆叠。"""
    if not values:
        return "(无数据)"
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return "▁" * min(len(values), width) + f"  全部≈{lo:g}"
    buckets = [0] * width
    for v in values:
        idx = int((v - lo) / (hi - lo) * (width - 1))
        buckets[idx] += 1
    blocks = "▁▂▃▄▅▆▇█"
    line = "".join(blocks[min(c, len(blocks) - 1)] if c else "·" for c in buckets)
    return f"{line}  [{lo:g} … {hi:g}]"


# 晶体结构字段：在 schema 中属于 polymorphs(L1)，不直接挂在 observations 上
STRUCT_FIELDS = ["a", "b", "c", "alpha", "beta", "gamma", "z",
                 "rho_crystal", "fiber_period"]


def load_full_observations(conn: sqlite3.Connection) -> list[dict]:
    """取出"每条观测行的完整数值视图"。

    结构字段（a/b/c/α/β/γ/z/ρ/fiber_period）在 schema 里属于 polymorphs(L1)，
    而 L1 是按 (polymer, 晶型标签) 去重的——若两篇文献给同一晶型不同晶胞，
    直接读 L1 只会看到其中一份，违反 §4.4"保留全部分歧"。
    因此取值优先级为：
        properties(L2.5，该观测专属的分歧值)  >  polymorphs(L1，去重后的代表值)
    store.persist_record 会在检测到分歧时把后到的值写入 properties，从而不丢数据。
    """
    obs_cols = {r[1] for r in conn.execute("PRAGMA table_info(observations)")}
    base = [c for c in ["obs_id", "polymer_id", "polymorph_id", "doi",
                        "ref_year", "source_field", "t_c"] if c in obs_cols]
    meas = [f for f in CHECK_FIELDS if f in obs_cols]
    cols = base + meas
    names = cols + ["abbr"] + STRUCT_FIELDS + ["polymorph_label"]
    rows = conn.execute(
        "SELECT o.{}, p.abbr, pm.{}, pm.polymorph_label "
        "FROM observations o "
        "LEFT JOIN polymers p ON p.polymer_id = o.polymer_id "
        "LEFT JOIN polymorphs pm ON pm.polymorph_id = o.polymorph_id".format(
            ", o.".join(cols), ", pm.".join(STRUCT_FIELDS))
    ).fetchall()
    out = [dict(zip(names, r)) for r in rows]

    # L2.5 分歧值覆盖 L1 代表值
    if {r[1] for r in conn.execute("PRAGMA table_info(properties)")}:
        over: dict[int, dict] = {}
        for oid, name, val in conn.execute(
            "SELECT obs_id, property_name, property_value FROM properties"
        ):
            over.setdefault(oid, {})[name] = val
        for d in out:
            for f in STRUCT_FIELDS:
                v = over.get(d.get("obs_id"), {}).get(f)
                if v is not None:
                    d[f] = v
    return out


def load_observations(conn: sqlite3.Connection) -> list[dict]:
    """兼容旧名：等价于 load_full_observations。"""
    return load_full_observations(conn)


def check_sanity(conn: sqlite3.Connection) -> tuple[list[dict], dict]:
    """返回 (问题列表, 分布统计)。问题条目含 obs_id / field / value / kind / detail。"""
    obs = load_full_observations(conn)
    issues: list[dict] = []
    dist: dict[str, dict[str, list[float]]] = {}

    # 1) 硬区间
    for r in obs:
        for f in CHECK_FIELDS:
            v = r.get(f)
            if v is None:
                continue
            lo, hi = HARD_RANGES[f]
            if not (lo <= v <= hi):
                issues.append({
                    "obs_id": r["obs_id"], "abbr": r.get("abbr"), "field": f,
                    "value": v, "kind": "hard_range",
                    "detail": f"{v:g} 超出家族合理区间 [{lo:g}, {hi:g}]（疑似单位/录入错误，回看原文）",
                })

    # 2) 稳健离群（按 polymer + field 分组）
    groups: dict[tuple, list[tuple]] = {}
    for r in obs:
        for f in CHECK_FIELDS:
            v = r.get(f)
            if v is None:
                continue
            groups.setdefault((r.get("abbr"), f), []).append((r["obs_id"], v))
            dist.setdefault(r.get("abbr") or "?", {}).setdefault(f, []).append(v)

    for (abbr, f), items in groups.items():
        if f in CONDITION_FIELDS:
            continue  # 实验条件不做统计离群判定，避免把多温度点实验误报为错误
        vals = [v for _, v in items]
        if len(vals) < MIN_N_FOR_OUTLIER:
            continue
        med = median(vals)
        mad = median([abs(v - med) for v in vals])
        if mad > 0:
            scale = 1.4826 * mad
            for oid, v in items:
                z = abs(v - med) / scale
                if z > Z_THRESHOLD:
                    issues.append({
                        "obs_id": oid, "abbr": abbr, "field": f, "value": v,
                        "kind": "outlier",
                        "detail": f"稳健 z={z:.1f}（中位数 {med:g}，MAD {mad:g}）→ 疑似手写/单位/换算错误",
                    })
        else:
            # MAD=0（多数值完全相同）：少数不同者按相对偏差判定
            for oid, v in items:
                if med and abs(v - med) / abs(med) > 0.05:
                    issues.append({
                        "obs_id": oid, "abbr": abbr, "field": f, "value": v,
                        "kind": "outlier",
                        "detail": f"多数记录一致为 {med:g}，本记录 {v:g}（偏差 >5%）",
                    })

    return issues, dist


def report(dist: dict, fields: Optional[list[str]] = None) -> None:
    """打印各成员关键字段的一维分布（§4.3 要求的"一维散点"）。"""
    fields = fields or ["rho_crystal", "tm", "tg", "delta_hf"]
    for abbr in sorted(dist):
        print(f"  [{abbr}]")
        for f in fields:
            vals = dist.get(abbr, {}).get(f, [])
            if not vals:
                continue
            med = median(vals)
            print(f"    {f:<18} n={len(vals):<3} 中位数={med:<8g} {_sparkline(vals)}")
