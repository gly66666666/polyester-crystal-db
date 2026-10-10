#!/usr/bin/env python3
"""落库：把 normalized 后的抽取记录写入 SQLite（L3→L1→L2）

设计（对齐 schema v1.1 与计划 §4.2 provenance）：
- literature_sources（L3）：doi UNIQUE，upsert（抽取模型版本 + 抽取时间 + raw_snippet）。
- polymorphs（L1）：按 (polymer_id, polymorph_label) find-or-create，回填 observations.polymorph_id。
- observations（L2）：只存实测/热历史字段 + polymorph_id 关联，**不含晶胞参数**（晶胞在 L1）。
- 幂等：同一 (doi, polymer, polymorph, t_c) 已存在则跳过，避免重复跑批产生脏数据。
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Optional

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
DB_PATH = PROJECT_ROOT / "data" / "polymer_crystal.db"

# observations 表中本模块写入的列（实测 + provenance，不含晶胞结构）
OBS_COLS = [
    "polymer_id", "polymorph_id", "doi", "ref_year", "ref_source", "ref_table",
    "source_field", "mw", "mn", "pdi", "t_c", "cryst_route",
    "anneal_t", "anneal_time_h", "draw_ratio", "cooling_rate",
    "xtallinity_pct", "long_period", "lamellar_thickness",
    "growth_rate", "avrami_n", "avrami_k", "t_half",
    "tm", "tm0", "delta_hf", "tg",
    "extraction_confidence", "reviewed_by", "review_status", "conflict_flag",
]


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _abbr_to_id(conn: sqlite3.Connection) -> dict:
    return dict(conn.execute("SELECT abbr, polymer_id FROM polymers").fetchall())


def _upsert_literature(conn: sqlite3.Connection, lit: dict) -> None:
    if not lit.get("doi"):
        return
    conn.execute(
        """
        INSERT INTO literature_sources
            (doi, title, authors, journal, year, abstract,
             extraction_model, extraction_version, extraction_time, raw_snippet)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(doi) DO UPDATE SET
            extraction_model=excluded.extraction_model,
            extraction_version=excluded.extraction_version,
            extraction_time=excluded.extraction_time,
            raw_snippet=excluded.raw_snippet
        """,
        (lit.get("doi"), lit.get("title"), lit.get("authors"), lit.get("journal"),
         lit.get("year"), lit.get("abstract"), lit.get("extraction_model"),
         lit.get("extraction_version"),
         datetime.now(timezone.utc).isoformat(timespec="seconds"),
         lit.get("raw_snippet")),
    )


def _find_or_create_polymorph(conn: sqlite3.Connection, polymer_id: int, poly: dict) -> Optional[int]:
    label = poly.get("polymorph_label")
    if not label:
        return None
    row = conn.execute(
        "SELECT polymorph_id FROM polymorphs WHERE polymer_id=? AND polymorph_label=?",
        (polymer_id, label),
    ).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        """INSERT INTO polymorphs
           (polymer_id, polymorph_label, crystal_system, space_group,
            a, b, c, alpha, beta, gamma, z, chain_conformation,
            rho_crystal, fiber_period)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (polymer_id, label, poly.get("crystal_system"), poly.get("space_group"),
         poly.get("a"), poly.get("b"), poly.get("c"),
         poly.get("alpha"), poly.get("beta"), poly.get("gamma"), poly.get("z"),
         poly.get("chain_conformation"), poly.get("rho_crystal"), poly.get("fiber_period")),
    )
    return cur.lastrowid


def _exists_obs(conn: sqlite3.Connection, polymer_id, polymorph_id, doi, t_c) -> bool:
    return conn.execute(
        """SELECT 1 FROM observations
           WHERE polymer_id=? AND coalesce(polymorph_id,-1)=coalesce(?,-1)
             AND coalesce(doi,'')=coalesce(?,'') AND coalesce(t_c,'')=coalesce(?, '')
           LIMIT 1""",
        (polymer_id, polymorph_id, doi, t_c),
    ).fetchone() is not None


def persist_record(conn: sqlite3.Connection, normalized: dict) -> str:
    """写入一条记录；返回 'inserted' / 'skipped' / 'no_polymer' / 'no_doi'。"""
    obs = dict(normalized["obs"])
    poly = normalized["poly"]
    lit = normalized["lit"]
    abbr = normalized["meta"].get("polymer_abbr")
    abbr2id = _abbr_to_id(conn)
    if abbr not in abbr2id:
        return "no_polymer"
    if not obs.get("doi"):
        return "no_doi"

    polymer_id = abbr2id[abbr]
    _upsert_literature(conn, lit)
    polymorph_id = _find_or_create_polymorph(conn, polymer_id, poly)
    obs["polymer_id"] = polymer_id
    obs["polymorph_id"] = polymorph_id

    if _exists_obs(conn, polymer_id, polymorph_id, obs.get("doi"), obs.get("t_c")):
        return "skipped"

    cols = [c for c in OBS_COLS if c in obs]
    placeholders = ", ".join("?" for _ in cols)
    col_sql = ", ".join(cols)
    vals = [obs.get(c) for c in cols]
    conn.execute(
        f"INSERT INTO observations ({col_sql}) VALUES ({placeholders})", vals
    )
    return "inserted"
