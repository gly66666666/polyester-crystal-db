#!/usr/bin/env python3
"""冲突消解（执行计划 §4.4）

§4.4 规则（本模块严格照此实现）：
1. 同一 (polymer, polymorph, 近似条件) 多条记录数值不一致 → **保留全部**，
   不删除、不人为合并；
2. 这些记录互相置 `conflict_flag=1`，并把对方的 obs_id 写入 `clash_with_ids`；
3. 择优策略**外置**：本模块只给出推荐排序（直接实测 > 综述转引，其次年份新者优先），
   由调用方决定是否采用；原始次源记录永远保留；
4. 前端可据此展示"这条有分歧，几篇给的分别是什么"——这是本库的价值展示而非瑕疵。

额外能力：
- **量级/单位错误识别**：若两值之比接近 10 / 100 / 1000（±8%），额外标注
  "疑似单位或量级错误"，因为这类冲突几乎都是 Å↔nm、J/g↔kJ/mol 之类的换算事故，
  与真实的学术分歧应区别对待。

"近似条件"的定义：同一 polymer + 同一 polymorph + 结晶温度 t_c 落入同一个
±bucket/2 的区间（默认 bucket=5 °C）。t_c 缺失时只按 (polymer, polymorph) 聚合。
"""

from __future__ import annotations

import sqlite3
from statistics import median
from typing import Optional

from . import sanity

# 参与冲突判定的数值字段（t_c 是分组条件本身，不参与）
CONFLICT_FIELDS = [
    "a", "b", "c", "alpha", "beta", "gamma", "z",
    "rho_crystal", "fiber_period",
    "tm", "tm0", "tg", "delta_hf",
    "xtallinity_pct", "growth_rate", "long_period", "lamellar_thickness",
]

# 相对偏差超过该比例即视为冲突
DEFAULT_TOL = 0.02

# 疑似单位/量级错误的倍数
MAGNITUDE_RATIOS = [10, 100, 1000, 0.1, 0.01, 0.001]


def _bucket(v: Optional[float], size: float) -> Optional[float]:
    if v is None:
        return None
    return round(v / size) * size


def load_for_conflict(conn: sqlite3.Connection) -> list[dict]:
    """复用 sanity 的完整数值视图：结构字段取"该观测专属值(properties) > L1 代表值"，
    这样同一晶型不同文献给出的不同晶胞才会被真正比较到，而不是被 L1 去重遮蔽。"""
    return sanity.load_full_observations(conn)


def detect_conflicts(conn: sqlite3.Connection, tol: float = DEFAULT_TOL,
                     tc_bucket: float = 5.0) -> list[dict]:
    """找出所有冲突组。每组含成员记录、冲突字段及各自取值。"""
    obs = load_for_conflict(conn)

    groups: dict[tuple, list[dict]] = {}
    for r in obs:
        key = (r["polymer_id"], r["polymorph_id"], _bucket(r.get("t_c"), tc_bucket))
        groups.setdefault(key, []).append(r)

    result: list[dict] = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        conflicts: list[dict] = []
        for f in CONFLICT_FIELDS:
            vals = [(m["obs_id"], m.get(f)) for m in members if m.get(f) is not None]
            if len(vals) < 2:
                continue
            numbers = [v for _, v in vals]
            med = median(numbers)
            if med and (max(numbers) - min(numbers)) / abs(med) > tol:
                ratio = max(numbers) / min(numbers) if min(numbers) else None
                suspect = None
                if ratio:
                    for r_ in MAGNITUDE_RATIOS:
                        if abs(ratio / r_ - 1) < 0.08:
                            suspect = f"×{r_:g}"
                            break
                conflicts.append({
                    "field": f,
                    "values": vals,
                    "median": med,
                    "ratio": ratio,
                    "unit_suspect": suspect,
                    "detail": f"{f}: {', '.join(f'{v:g}' for _, v in vals)}"
                              + (f"  【疑似单位/量级错误 {suspect}】" if suspect else ""),
                })
        if conflicts:
            result.append({
                "key": key, "members": members, "conflicts": conflicts,
                "preferred": rank_preferred(members),
            })
    return result


def rank_preferred(members: list[dict]) -> list[dict]:
    """推荐排序（择优策略外置，由调用方决定是否采用）：
    直接实测(measured) 优于 综述转引(review-cited)；同级按年份新者优先。
    永远不删除任何记录。"""
    def score(m: dict):
        sf = (m.get("source_field") or "").lower()
        measured = 0 if sf == "measured" else 1
        return (measured, -(m.get("ref_year") or 0))
    return sorted(members, key=score)


def apply_conflicts(conn: sqlite3.Connection, groups: list[dict]) -> int:
    """把冲突标记写回 observations：conflict_flag=1 + clash_with_ids 互写。"""
    n = 0
    for g in groups:
        ids = [m["obs_id"] for m in g["members"]]
        for m in g["members"]:
            others = [str(i) for i in ids if i != m["obs_id"]]
            conn.execute(
                "UPDATE observations SET conflict_flag=1, clash_with_ids=? WHERE obs_id=?",
                (",".join(others), m["obs_id"]),
            )
            n += 1
    return n
