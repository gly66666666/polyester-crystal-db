#!/usr/bin/env python3
"""单位归一（P2 交付项之一）

schema v1.1 规定了入库值的规范单位。本模块负责把**非规范单位**的观测值换算到规范单位，
并显式记录换算过程（便于溯源与只重跑受影响批次）。

规范单位约定（与 schema.sql 头部注释一致）：
  a/b/c/fiber_period  Å      alpha/beta/gamma      °
  rho_crystal         g/cm³  t_c/tm/tm0/tg/anneal_t °C
  delta_hf            J/g    growth_rate            nm/s
  long_period/lamellar_thickness nm                 t_half min / anneal_time_h h
  mw/mn g/mol         xtallinity_pct %              z count

⚠️ 换算陷阱（本模块专门处理）：
- kJ/mol ↔ J/g 必须知道重复单元分子量 MW：ΔHf[J/g] = ΔHf[kJ/mol] × 1000 / MW
  忘记换算会得到差 1~2 个数量级的值，是本项目最容易出现的系统性错误。
- K ↔ °C 是偏移而非比例；°F 需要 (v-32)×5/9。
- nm 与 Å 差 10 倍；long_period 常用 nm 而晶胞用 Å，两者别混。

用法：
  from src.extraction.units import convert, normalize_record
  convert("delta_hf", 12.0, "kJ/mol", mw=192.17)   # -> (~62.4, note)
  normalize_record({"tm": 528.15, ...}, {"tm": "K"}, mw=None)
"""

from __future__ import annotations

from typing import Optional

# 字段 → 规范单位
CANONICAL_UNIT = {
    "a": "Å", "b": "Å", "c": "Å", "fiber_period": "Å",
    "alpha": "°", "beta": "°", "gamma": "°",
    "rho_crystal": "g/cm3",
    "t_c": "°C", "tm": "°C", "tm0": "°C", "tg": "°C", "anneal_t": "°C",
    "delta_hf": "J/g",
    "growth_rate": "nm/s",
    "long_period": "nm", "lamellar_thickness": "nm",
    "t_half": "min", "anneal_time_h": "h",
    "mw": "g/mol", "mn": "g/mol",
    "xtallinity_pct": "%", "z": "count", "pdi": "ratio",
}

# 线性换算：(乘数, 偏移)。None 表示需要分子量（见 _MW_DEPENDENT）
_LINEAR = {
    "a": {"Å": (1, 0), "A": (1, 0), "angstrom": (1, 0),
          "nm": (10, 0), "pm": (0.01, 0), "um": (10000, 0), "µm": (10000, 0)},
    "b": None, "c": None, "fiber_period": None,  # 与 a 同规则，运行时回落到 a
    "alpha": {"°": (1, 0), "deg": (1, 0), "rad": (57.29577951308232, 0)},
    "beta": None, "gamma": None,
    "rho_crystal": {"g/cm3": (1, 0), "g/cm^3": (1, 0), "gcc": (1, 0),
                    "kg/m3": (0.001, 0), "kg/m^3": (0.001, 0),
                    "Mg/m3": (1, 0), "g/ml": (1, 0)},
    "t_c": {"°C": (1, 0), "C": (1, 0), "celsius": (1, 0),
            "K": (1, -273.15), "kelvin": (1, -273.15),
            "°F": (5 / 9, -32 * 5 / 9), "F": (5 / 9, -32 * 5 / 9)},
    "tm": None, "tm0": None, "tg": None, "anneal_t": None,  # 与 t_c 同规则
    "delta_hf": {"J/g": (1, 0), "j/g": (1, 0), "kJ/kg": (1, 0),
                 "cal/g": (4.184, 0), "kJ/g": (1000, 0)},
    "growth_rate": {"nm/s": (1, 0), "um/s": (1000, 0), "µm/s": (1000, 0),
                    "um/min": (1000 / 60, 0), "µm/min": (1000 / 60, 0),
                    "nm/min": (1 / 60, 0), "mm/s": (1e6, 0), "A/s": (0.1, 0),
                    "Å/s": (0.1, 0)},
    "long_period": {"nm": (1, 0), "A": (0.1, 0), "Å": (0.1, 0),
                    "pm": (0.001, 0), "um": (1000, 0), "µm": (1000, 0)},
    "lamellar_thickness": None,
    "t_half": {"min": (1, 0), "s": (1 / 60, 0), "sec": (1 / 60, 0), "h": (60, 0)},
    "anneal_time_h": {"h": (1, 0), "min": (1 / 60, 0), "s": (1 / 3600, 0)},
    "mw": {"g/mol": (1, 0), "kg/mol": (1000, 0), "Da": (1, 0)},
    "mn": None,
    "xtallinity_pct": {"%": (1, 0), "percent": (1, 0), "fraction": (100, 0)},
    "z": {"count": (1, 0)}, "pdi": {"ratio": (1, 0)},
}

# 需要重复单元分子量 MW 的换算：单位 → (分子, 分母说明)
# ΔHf[J/g] = value[unit] × 1000 / MW  （kJ/mol）
_MW_DEPENDENT = {
    "delta_hf": {
        "kJ/mol": 1000.0,     # value * 1000 / MW
        "J/mol": 1.0,         # value * 1 / MW
        "kcal/mol": 4184.0,   # value * 4184 / MW
        "cal/mol": 4.184,
    }
}

# 与 a / t_c / long_period 等共享换算规则的字段
_ALIAS_GROUP = {
    "b": "a", "c": "a", "fiber_period": "a",
    "beta": "alpha", "gamma": "alpha",
    "tm": "t_c", "tm0": "t_c", "tg": "t_c", "anneal_t": "t_c",
    "lamellar_thickness": "long_period",
    "mn": "mw",
}


def _norm_unit(u: str) -> str:
    return (u or "").strip().replace("³", "3").replace("⁻", "-")


def convert(field: str, value: float, unit: Optional[str],
            mw: Optional[float] = None) -> tuple[Optional[float], str]:
    """把 value 从 unit 换算到该字段的规范单位。

    返回 (换算后的值, 说明)。无法换算时返回 (None, 原因)。
    """
    if value is None:
        return None, "值为空"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None, "非数值"

    if not unit:
        return v, f"未给单位，按规范单位 {CANONICAL_UNIT.get(field, '?')} 直接采用"

    u = _norm_unit(unit)
    canon = CANONICAL_UNIT.get(field)
    if canon and u == _norm_unit(canon):
        return v, f"已是规范单位 {canon}"

    # 分子量相关（ΔHf kJ/mol 等）
    deps = _MW_DEPENDENT.get(field, {})
    if u in deps:
        if not mw:
            return None, f"{unit} → {canon} 需要重复单元分子量 MW，但未提供（polymers.repeat_unit_mw 为空？）"
        return v * deps[u] / mw, f"{v}{unit} × {deps[u]} / MW({mw}) → {canon}"

    table = _LINEAR.get(field)
    if table is None:
        base = _ALIAS_GROUP.get(field)
        table = _LINEAR.get(base) if base else None
    if table:
        for alias, (mult, off) in table.items():
            if _norm_unit(alias) == u:
                out = v * mult + off
                return out, f"{v}{unit} → {canon}（×{mult}{'' if not off else f' +{off}'}）"

    return None, f"未知单位 {unit}（字段 {field} 规范单位 {canon}）"


def normalize_record(record: dict, units: dict, mw: Optional[float] = None) -> tuple[dict, list[str]]:
    """按 units={字段: 单位} 批量换算一条记录。

    返回 (换算后的记录副本, 说明/问题列表)。
    未出现在 units 里的字段按规范单位原样保留。
    """
    out = dict(record)
    notes: list[str] = []
    for field, unit in (units or {}).items():
        if field not in out:
            continue
        val, note = convert(field, out.get(field), unit, mw=mw)
        if val is None and out.get(field) is not None:
            notes.append(f"[单位] {field}: {note}（该值已置空，需人工确认）")
            out[field] = None
        else:
            out[field] = val
            if note and not note.startswith("已是规范单位"):
                notes.append(f"[单位] {field}: {note}")
    return out, notes


def mw_of(conn, polymer_id: int) -> Optional[float]:
    """取该聚合物的重复单元分子量（用于 kJ/mol ↔ J/g 换算）。"""
    row = conn.execute(
        "SELECT repeat_unit_mw FROM polymers WHERE polymer_id=?", (polymer_id,)
    ).fetchone()
    return row[0] if row and row[0] is not None else None
