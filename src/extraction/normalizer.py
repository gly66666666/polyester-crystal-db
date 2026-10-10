#!/usr/bin/env python3
"""归一化与校验：把 extractor 产出的扁平 record 拆成 schema 两层

按 schema v1.1 的分工：
- 晶体结构（a/b/c/α/β/γ/z/ρ/fiber_period/晶系/空间群/链构象/晶型）→ polymorphs (L1)
- 实测条件与热力学/动力学（t_c/tm/tm0/tg/ΔHf/结晶度/生长速率/...）→ observations (L2)，通过 polymorph_id 关联
- 同时保留一份 flat（结构+实测合并）供评测脚本逐字段对比，不落库

单位已在 contract 层固定（Å/°/g·cm³/°C/J·g⁻¹/%/nm/nm·s⁻¹/min）。
置信度阈值：<0.7 → review_status='pending_review'；否则 'auto'。
范围 sanity 仅标记，不拦截（计划 §4.3：保留全部、标记待复核）。
"""

from __future__ import annotations

from typing import Optional

# 结构字段（归入 polymorphs L1）
STRUCT_COLS = {
    "polymorph_label", "crystal_system", "space_group", "chain_conformation",
    "a", "b", "c", "alpha", "beta", "gamma", "z", "rho_crystal", "fiber_period",
}

# 实测/热历史字段（归入 observations L2）
MEAS_COLS = {
    "mw", "mn", "pdi", "t_c", "tm", "tm0", "tg", "delta_hf",
    "xtallinity_pct", "long_period", "lamellar_thickness", "growth_rate",
    "avrami_n", "avrami_k", "t_half", "anneal_t", "anneal_time_h",
    "draw_ratio", "cooling_rate", "cryst_route",
}

# 可信家族区间（宽松，仅做 sanity flag）
_RANGES = {
    "a": (0.5, 50.0), "b": (0.5, 50.0), "c": (0.5, 200.0),
    "alpha": (0.0, 180.0), "beta": (0.0, 180.0), "gamma": (0.0, 180.0),
    "rho_crystal": (0.5, 3.0), "fiber_period": (0.5, 200.0),
    "tm": (-50.0, 400.0), "tm0": (-50.0, 400.0), "tg": (-150.0, 300.0),
    "delta_hf": (0.0, 400.0), "xtallinity_pct": (0.0, 100.0),
    "growth_rate": (1e-4, 1e4), "long_period": (0.5, 500.0),
    "lamellar_thickness": (0.5, 500.0), "avrami_n": (0.0, 6.0),
}

REVIEW_THRESHOLD = 0.7


def normalize(extracted: dict, doi: Optional[str], ref_year=None,
              ref_source=None, extraction_model="mock",
              extraction_version="ext-v0.1") -> dict:
    record = dict(extracted.get("record", {}))   # 扁平：结构 + 实测混在一起
    meta = extracted.get("meta", {})
    issues: list[str] = []

    # 数值清洗
    numeric_cols = set(_RANGES.keys()) | {
        "avrami_k", "t_half", "mw", "mn", "pdi",
        "anneal_t", "anneal_time_h", "draw_ratio", "cooling_rate",
    }
    for col in numeric_cols:
        v = record.get(col)
        if v is None:
            continue
        try:
            record[col] = float(v)
        except (TypeError, ValueError):
            issues.append(f"{col} 非数值，已置空")
            record[col] = None

    # 范围 sanity（仅标记）
    for col, (lo, hi) in _RANGES.items():
        v = record.get(col)
        if v is not None and not (lo <= v <= hi):
            issues.append(f"{col}={v} 超出合理区间 [{lo},{hi}]，已保留但标记待复核")

    # 置信度与复核状态
    conf = meta.get("confidence")
    try:
        conf = float(conf) if conf is not None else None
    except (TypeError, ValueError):
        conf = None
    review_status = "pending_review" if (conf is None or conf < REVIEW_THRESHOLD) else "auto"

    # —— L1 晶体结构 ——
    poly = {
        "polymorph_label": meta.get("polymorph_label"),
        "crystal_system": meta.get("crystal_system"),
        "space_group": meta.get("space_group"),
        "chain_conformation": record.get("chain_conformation"),
        "a": record.get("a"), "b": record.get("b"), "c": record.get("c"),
        "alpha": record.get("alpha"), "beta": record.get("beta"), "gamma": record.get("gamma"),
        "z": record.get("z"),
        "rho_crystal": record.get("rho_crystal"),
        "fiber_period": record.get("fiber_period"),
    }

    # —— L2 实测观测 ——
    obs = {
        "doi": doi, "ref_year": ref_year, "ref_source": ref_source,
        "ref_table": meta.get("evidence"), "source_field": "measured",
        "mw": record.get("mw"), "mn": record.get("mn"), "pdi": record.get("pdi"),
        "t_c": record.get("t_c"), "cryst_route": record.get("cryst_route"),
        "anneal_t": record.get("anneal_t"), "anneal_time_h": record.get("anneal_time_h"),
        "draw_ratio": record.get("draw_ratio"), "cooling_rate": record.get("cooling_rate"),
        "xtallinity_pct": record.get("xtallinity_pct"),
        "long_period": record.get("long_period"),
        "lamellar_thickness": record.get("lamellar_thickness"),
        "growth_rate": record.get("growth_rate"),
        "avrami_n": record.get("avrami_n"), "avrami_k": record.get("avrami_k"),
        "t_half": record.get("t_half"),
        "tm": record.get("tm"), "tm0": record.get("tm0"),
        "delta_hf": record.get("delta_hf"), "tg": record.get("tg"),
        "extraction_confidence": conf, "reviewed_by": None,
        "review_status": review_status, "conflict_flag": 0,
    }

    # —— flat（评测用，结构+实测合并）——
    flat = dict(record)
    flat["doi"] = doi
    flat["polymer_abbr"] = meta.get("polymer_abbr")
    flat["polymorph_label"] = meta.get("polymorph_label")
    flat["confidence"] = conf
    flat["evidence"] = meta.get("evidence")

    lit = {
        "doi": doi, "title": None, "authors": None, "journal": ref_source,
        "year": ref_year, "abstract": None,
        "extraction_model": extraction_model, "extraction_version": extraction_version,
        "raw_snippet": meta.get("evidence"),
    }

    return {
        "obs": obs, "poly": poly, "flat": flat, "lit": lit, "meta": meta,
        "issues": issues, "review_status": review_status, "confidence": conf,
        "parse_ok": extracted.get("parse_ok", True),
    }
