#!/usr/bin/env python3
"""质量校验统一入口（执行计划 §4.3 + §4.4）

用法：
  python -m src.extraction.qa                    # 只体检，不写库
  python -m src.extraction.qa --apply            # 把冲突/越界标记写回 observations
  python -m src.extraction.qa --json qa.json     # 导出体检报告
  python -m src.extraction.qa --self-test        # 只跑单位换算表自检

三步体检：
1. **单位换算表自检**（units.py）：确认 K→°C、nm→Å、kJ/mol→J/g 等换算正确
   —— 量级/单位错误是本项目最容易出现的系统性错误，先确保尺子本身准。
2. **越界 sanity**（§4.3）：硬区间 + 中位数/MAD 稳健离群 + 一维分布散点。
3. **冲突消解**（§4.4）：同 (polymer, polymorph, 近似 t_c) 多值不一致 →
   保留全部、互相标记 conflict_flag + clash_with_ids，并给出推荐排序。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import units
from . import sanity
from . import conflict
from .store import DB_PATH, get_connection


def self_test_units() -> bool:
    """单位换算表自检：任一项不符即视为尺子不准，必须修。"""
    cases = [
        # (字段, 值, 原单位, MW, 期望值, 容差)
        ("tm", 528.15, "K", None, 255.0, 0.05),          # K → °C（偏移，非比例）
        ("a", 1.075, "nm", None, 10.75, 1e-6),           # nm → Å（×10）
        ("rho_crystal", 1455, "kg/m3", None, 1.455, 1e-6),  # kg/m³ → g/cm³（÷1000）
        ("delta_hf", 26.9, "kJ/mol", 192.17, 139.98, 0.5),  # kJ/mol → J/g（需 MW）
        ("growth_rate", 0.0005, "um/s", None, 0.5, 1e-9),
        ("long_period", 107.5, "A", None, 10.75, 1e-9),  # Å → nm（÷10）
        ("xtallinity_pct", 0.42, "fraction", None, 42.0, 1e-9),
    ]
    ok = True
    print("=== 1) 单位换算自检 ===")
    for field, val, unit, mw, expect, tol in cases:
        got, note = units.convert(field, val, unit, mw=mw)
        good = got is not None and abs(got - expect) <= tol
        ok &= good
        print(f"  {'✓' if good else '✗'} {field}: {val}{unit} -> {got if got is None else round(got, 4)}"
              f"（期望≈{expect}）  {note}")
    # 缺 MW 时必须明确失败，不能静默给错值
    got, note = units.convert("delta_hf", 26.9, "kJ/mol", mw=None)
    ok &= (got is None)
    print(f"  {'✓' if got is None else '✗'} 缺 MW 时 kJ/mol→J/g 正确拒绝：{note}")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="数据质量校验（§4.3 越界 + §4.4 冲突）")
    ap.add_argument("--apply", action="store_true", help="把 conflict_flag / clash_with_ids 写回数据库")
    ap.add_argument("--json", default=None, help="导出体检报告 JSON")
    ap.add_argument("--tol", type=float, default=conflict.DEFAULT_TOL, help="冲突相对偏差阈值")
    ap.add_argument("--tc-bucket", type=float, default=5.0, help="结晶温度聚合桶大小(°C)")
    ap.add_argument("--self-test", action="store_true", help="只跑单位换算自检")
    ap.add_argument("--db", default=None, help="指定数据库（默认 data/polymer_crystal.db）")
    args = ap.parse_args()

    if args.self_test:
        ok = self_test_units()
        print("\n自检" + ("通过 ✓" if ok else "失败 ✗"))
        sys.exit(0 if ok else 1)

    if not DB_PATH.exists():
        print("✗ 主库不存在，请先运行 src/database/init_db.py", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(Path(args.db) if args.db else None)

    ok = self_test_units()

    print("\n=== 2) 越界 sanity（§4.3）===")
    issues, dist = sanity.check_sanity(conn)
    if not issues:
        print("  未发现越界/离群问题。")
    else:
        for it in issues:
            print(f"  [{'硬区间' if it['kind'] == 'hard_range' else '离群'}] "
                  f"obs#{it['obs_id']} {it.get('abbr')} {it['field']}={it['value']:g}")
            print(f"      {it['detail']}")
    print("  各成员关键字段分布（§4.3 要求的“一维散点”）：")
    sanity.report(dist)

    print("\n=== 3) 冲突消解（§4.4）===")
    groups = conflict.detect_conflicts(conn, tol=args.tol, tc_bucket=args.tc_bucket)
    if not groups:
        print("  未发现同条件数值冲突。")
    for g in groups:
        abbr = g["members"][0].get("abbr")
        tcs = [m.get("t_c") for m in g["members"] if m.get("t_c") is not None]
        tc_txt = f"t_c≈{min(tcs):g}~{max(tcs):g}°C" if tcs else "t_c 未标注"
        print(f"  冲突组 [{abbr}] {tc_txt}  共 {len(g['members'])} 条：")
        for c in g["conflicts"]:
            print(f"      - {c['detail']}")
        pref = g["preferred"][0]
        print(f"      推荐优先采用：obs#{pref['obs_id']}"
              f"（{pref.get('source_field')}, {pref.get('ref_year')}）— 其余记录保留不删")

    n_flag = 0
    if args.apply:
        conflict.apply_conflicts(conn, groups)
        # 冲突组 + 越界/离群 取并集后统一置位（避免重叠计数）
        flagged = {m["obs_id"] for g in groups for m in g["members"]}
        flagged |= {it["obs_id"] for it in issues
                    if it["kind"] in ("hard_range", "outlier")}
        for oid in sorted(flagged):
            conn.execute("UPDATE observations SET conflict_flag=1 WHERE obs_id=?", (oid,))
        conn.commit()
        n_flag = len(flagged)
        print(f"\n✓ 已写回标记：{n_flag} 条记录置 conflict_flag=1")

    conn.close()

    if args.json:
        Path(args.json).write_text(json.dumps({
            "unit_self_test_ok": ok,
            "sanity_issues": issues,
            "conflict_groups": [
                {
                    "members": [m["obs_id"] for m in g["members"]],
                    "conflicts": g["conflicts"],
                    "preferred_obs_id": g["preferred"][0]["obs_id"],
                } for g in groups
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 报告已导出：{args.json}")

    print(f"\n体检完成：越界/离群 {len(issues)} 项，冲突组 {len(groups)} 组，"
          f"单位自检{'通过' if ok else '未通过'}。")


if __name__ == "__main__":
    main()
