#!/usr/bin/env python3
"""Gold Set 标注工具（任务9）

作用：为 LLM 抽取流水线建立**人工核验的金标准**（gold standard），
用于后续评估抽取准确率（precision / recall / F1）。

设计要点（对齐执行计划 §3 四层模型与 schema.sql v1.1）：
- 金标准与本项目的"一条 = L2 观测行"口径一致，每条 gold 记录映射一组
  晶胞参数 + 热力学/动力学量，可 1:1 对照 LLM 抽取出的 observations 行。
- 金标准**只存人工从原文逐条核验过的数值**，每条必须挂单一 DOI（合规红线）。
- 任务9 目标：从 PET / PTT / PBT / PLA（=PLLA）各标 5 条 → 共 20 条基准。
- gold 数据先落在 data/gold_set/gold_set.json（与主库解耦），
  经 validate 后可用 export-db 写入主库 observations（review_status='gold'），
  并 find-or-create 对应 polymorphs 行。

子命令：
  init                 生成空白骨架（4 成员 × 5 槽位 = 20 条），幂等
  list-candidates POLY 从 search_results.json 列出某成员的候选文献（帮选 DOI）
  list                 查看当前已填 / 空槽位
  add                  交互式或 --json 新增一条 gold 记录（带校验）
  edit GOLD_ID         编辑已有记录（--json 覆盖字段）
  validate             校验所有已填记录，打印问题与警告
  stats                统计覆盖情况（各成员已标几条 / 共几条）
  export-db            将 gold 记录写入主库 observations（review_status='gold'）
  benchmark EXTRACTED  对比一份抽取结果 JSON，逐字段算准确率（前瞻，P2 用）

仅依赖标准库（json / sqlite3 / argparse / datetime / re）。
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---- 路径解析（与 init_db.py 一致：脚本位置反推项目根）----
HERE = Path(__file__).resolve().parent            # …/src/annotation
PROJECT_ROOT = HERE.parents[1]                    # …/polyester-crystal-db
DB_PATH = PROJECT_ROOT / "data" / "polymer_crystal.db"
GOLD_DIR = PROJECT_ROOT / "data" / "gold_set"
GOLD_PATH = GOLD_DIR / "gold_set.json"
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"

# ---- 任务9 目标成员与配额 ----
TARGET_POLYMERS = ["PET", "PTT", "PBT", "PLA"]
PER_POLYMER = 5

# 建议起点文献（仅书目信息，**不**内置数值；金标准数值必须由人工从原文逐条核验）
# 标注时请打开原文，把表/图中的晶胞参数、热力学量抄入，并填好 ref_table。
#
# ⚠️ 2026-10-10 修正：此前的 DOI 系凭记忆填写，经 CrossRef 核验全部错误
#    （如 PET 的旧 DOI 实为 "Transport and relaxation phenomena"，与 PET 晶体结构无关）。
#    以下 DOI 均已通过 CrossRef API 核验题录（年份 / 期刊 / 标题）一致。
SUGGESTED_START = {
    "PET": [
        {"doi": "10.1098/rspa.1954.0273",
         "cite": "The crystal structure of polyethylene terephthalate (1954) Proc. R. Soc. A",
         "note": "PET 三斜 P-1 经典晶胞的源头文献；务必从原文表核对 a/b/c/α/β/γ 与 ρ"},
        {"doi": "10.1007/bf01202554",
         "cite": "Refinement of the crystal structure of polyethylene terephthalate (1975) J. Cryst. Mol. Struct.",
         "note": "对 1954 晶胞的精修，可与上一条互为交叉校验"},
    ],
    "PTT": [
        {"doi": "10.1016/0032-3861(79)90064-8",
         "cite": "The crystal structure of poly(trimethylene terephthalate) by X-ray (1979) Polymer",
         "note": "PTT 晶胞经典文献；注意其近 tggt 构象"},
        {"doi": "10.1021/ma000210w",
         "cite": "Crystal Structure and Banded Spherulite of Poly(trimethylene terephthalate) (2000) Macromolecules",
         "note": "同时给晶胞与环带球晶信息"},
    ],
    "PBT": [
        {"doi": "10.1016/j.polymer.2017.07.076",
         "cite": "Crystal reorganization of poly (butylene terephthalate) (2017) Polymer",
         "note": "⚠️ PBT 的「聚合物本体」晶胞经典文献（Yokouchi/Mencik 1970s）在现有检索集中覆盖薄弱，"
                "已补 tetramethylene terephthalate / PTMT 同义词重新检索；若仍不足需人工补检"},
        {"doi": "10.1295/polymj.23.949",
         "cite": "Crystal Structure of Cyclic Dimer of Poly(butylene terephthalate) (1991) Polymer Journal",
         "note": "这是环状二聚体（模型化合物）而非聚合物本体，作结构参考时务必注明，勿当作 PBT 晶胞"},
    ],
    "PLA": [
        {"doi": "10.1021/ma001630o",
         "cite": "Crystal Structure of the α-Form of Poly(L-lactide) (2001) Macromolecules",
         "note": "PLLA α 型晶胞的权威来源"},
        {"doi": "10.1080/00222349108245788",
         "cite": "Crystal structure of stereocomplex of poly(L-lactide) and poly(D-lactide) (1991) J. Macromol. Sci. B",
         "note": "立构复合晶(sc)；与 α 型分属不同 polymorph_label"},
    ],
}

# 数值型字段及其单位（与 schema 单位约定一致）
NUMERIC_FIELDS = {
    "a": "Å", "b": "Å", "c": "Å",
    "alpha": "°", "beta": "°", "gamma": "°",
    "z": "count", "rho_crystal": "g/cm3", "fiber_period": "Å",
    "tm": "°C", "tm0": "°C", "tg": "°C",
    "delta_hf": "J/g", "xtallinity_pct": "%", "growth_rate": "nm/s",
}

DOI_RE = re.compile(r"^10\.\d{4,9}/.+")


# --------------------------------------------------------------------------- #
# 骨架与存储
# --------------------------------------------------------------------------- #
def _empty_record(polymer_abbr: str, idx: int) -> dict:
    return {
        "gold_id": f"{polymer_abbr}-{idx:03d}",
        "polymer_abbr": polymer_abbr,
        "status": "empty",
        "doi": None, "ref_year": None, "ref_source": None, "ref_table": None,
        "source_field": "measured",
        "polymorph_label": None, "crystal_system": None, "space_group": None,
        "a": None, "b": None, "c": None,
        "alpha": None, "beta": None, "gamma": None,
        "z": None, "chain_conformation": None, "rho_crystal": None,
        "fiber_period": None, "helix_type": None,
        "tm": None, "tm0": None, "delta_hf": None, "tg": None,
        "xtallinity_pct": None, "growth_rate": None,
        "annotator": None, "annotation_date": None,
        "confidence": None, "notes": None,
    }


def init_gold() -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    if GOLD_PATH.exists():
        existing = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
        print(f"✓ 已存在 gold_set.json（{len(existing['records'])} 条），init 跳过覆盖。")
        print("  如需重置请先备份后删除该文件。")
        return
    records = []
    for poly in TARGET_POLYMERS:
        for i in range(1, PER_POLYMER + 1):
            records.append(_empty_record(poly, i))
    payload = {
        "meta": {
            "version": "1.0",
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "description": "Gold standard annotations for LLM extraction benchmark",
            "target_polymers": TARGET_POLYMERS,
            "per_polymer": PER_POLYMER,
            "schema_ref": "src/database/schema.sql",
            "rules": "每条必须挂单一 DOI；数值须人工从原文核验；单位见 NUMERIC_FIELDS",
        },
        "records": records,
    }
    GOLD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 已生成骨架: {GOLD_PATH}")
    print(f"✓ {len(records)} 个空槽位（{', '.join(TARGET_POLYMERS)} 各 {PER_POLYMER} 条）")


def _load() -> dict:
    if not GOLD_PATH.exists():
        print("✗ gold_set.json 不存在，请先运行: python gold_set_annotator.py init", file=sys.stderr)
        sys.exit(1)
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def _save(payload: dict) -> None:
    GOLD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _known_abbrs() -> set:
    if not DB_PATH.exists():
        return set(TARGET_POLYMERS)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT abbr FROM polymers").fetchall()
    conn.close()
    return {r[0] for r in rows}


# --------------------------------------------------------------------------- #
# 校验
# --------------------------------------------------------------------------- #
def validate_record(rec: dict, known: set) -> list[str]:
    """返回该记录的问题列表（空 = 通过）。仅对 status=='filled' 的记录报错。"""
    problems: list[str] = []
    if rec.get("status") != "filled":
        return problems

    if rec.get("polymer_abbr") not in known:
        problems.append(f"polymer_abbr 未知: {rec.get('polymer_abbr')}")
    doi = rec.get("doi")
    if not doi:
        problems.append("缺少 doi（合规红线：每条须挂单一 DOI）")
    elif not DOI_RE.match(str(doi)):
        problems.append(f"doi 格式可疑: {doi}")
    if not rec.get("annotator"):
        problems.append("缺少 annotator（标注人）")
    if rec.get("confidence") not in (None, "high", "medium", "low"):
        problems.append("confidence 须为 high/medium/low")

    # 晶胞长度必须为正
    for f in ("a", "b", "c", "fiber_period", "rho_crystal"):
        v = rec.get(f)
        if v is not None and not (isinstance(v, (int, float)) and v > 0):
            problems.append(f"{f} 必须为正实数 (Å / g/cm3)")
    # 晶系角范围
    for f in ("alpha", "beta", "gamma"):
        v = rec.get(f)
        if v is not None and not (0 < v <= 180):
            problems.append(f"{f} 须 ∈ (0,180] °")
    # 整数类
    if rec.get("z") is not None and (not isinstance(rec["z"], int) or rec["z"] < 1):
        problems.append("z 须为 ≥1 整数")
    # 结晶度
    xp = rec.get("xtallinity_pct")
    if xp is not None and not (0 <= xp <= 100):
        problems.append("xtallinity_pct 须 ∈ [0,100]")
    # 至少要有晶胞或一项热力学量，否则这条记录无意义
    has_cell = all(rec.get(k) is not None for k in ("a", "b", "c"))
    has_thermo = any(rec.get(k) is not None for k in ("tm", "tm0", "delta_hf", "tg"))
    if not (has_cell or has_thermo):
        problems.append("至少填写晶胞 a/b/c 之一 或 一项热力学量 (tm/tm0/delta_hf/tg)")
    return problems


def validate_all() -> int:
    payload = _load()
    known = _known_abbrs()
    n_filled = 0
    n_err = 0
    for rec in payload["records"]:
        if rec.get("status") != "filled":
            continue
        n_filled += 1
        probs = validate_record(rec, known)
        if probs:
            n_err += 1
            print(f"✗ {rec['gold_id']} ({rec.get('polymer_abbr')}):")
            for p in probs:
                print(f"    - {p}")
    print(f"\n已填 {n_filled} 条，其中 {n_err} 条存在问题。")
    return n_err


# --------------------------------------------------------------------------- #
# 候选文献浏览
# --------------------------------------------------------------------------- #
def list_candidates(poly: str, top: int = 25) -> None:
    if not SEARCH_PATH.exists():
        print("✗ 未找到 search_results.json，请先完成任务8文献检索。", file=sys.stderr)
        sys.exit(1)
    data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    items = data.get(poly)
    if not items:
        print(f"✗ 检索结果中没有成员 {poly} 的文献。")
        return
    print(f"=== {poly} 候选文献（前 {min(top, len(items))} / 共 {len(items)} 篇）===")
    for i, it in enumerate(items[:top], 1):
        print(f"[{i:2d}] {it.get('year','?')} | {it.get('journal','?')}")
        print(f"     {it.get('title','')[:90]}")
        print(f"     DOI: {it.get('doi','')}")
    print("\n提示：用 `add --json '{...}'` 录入人工核验过的数值，doi 填上方真实 DOI。")


# --------------------------------------------------------------------------- #
# 增 / 改
# --------------------------------------------------------------------------- #
def _prompt(text: str, default=None, cast=str):
    suf = f" [{default}]" if default is not None else ""
    val = input(f"{text}{suf}: ").strip()
    if not val and default is not None:
        return default
    if not val:
        return None
    try:
        return cast(val)
    except ValueError:
        print(f"  ! 无法解析为 {cast.__name__}，已忽略")
        return None


def add_record(json_str: str | None) -> None:
    payload = _load()
    known = _known_abbrs()
    rec: dict
    if json_str:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"✗ JSON 解析失败: {e}", file=sys.stderr)
            sys.exit(1)
        gold_id = data.get("gold_id")
        if gold_id:
            rec = next((r for r in payload["records"] if r["gold_id"] == gold_id), None)
            if rec is None:
                print(f"✗ 未找到 gold_id={gold_id}", file=sys.stderr)
                sys.exit(1)
        else:
            rec = _empty_record(data.get("polymer_abbr", "PET"), 999)
            payload["records"].append(rec)
        rec.update({k: v for k, v in data.items() if k in rec})
        rec["status"] = "filled"
        rec.setdefault("annotation_date", datetime.now(timezone.utc).date().isoformat())
    else:
        # 交互式
        print("=== 交互式新增 gold 记录（回车留空 = 跳过该字段）===")
        poly = _prompt("polymer_abbr", cast=str) or "PET"
        rec = _empty_record(poly, 999)
        payload["records"].append(rec)
        rec["doi"] = _prompt("doi")
        rec["ref_year"] = _prompt("ref_year", cast=int)
        rec["ref_source"] = _prompt("ref_source (期刊/书名)")
        rec["ref_table"] = _prompt("ref_table (原文表/图号)")
        rec["polymorph_label"] = _prompt("polymorph_label (e.g. triclinic/alpha)")
        rec["crystal_system"] = _prompt("crystal_system")
        rec["space_group"] = _prompt("space_group (e.g. P-1)")
        for f in ("a", "b", "c", "alpha", "beta", "gamma", "z",
                  "rho_crystal", "fiber_period", "tm", "tm0", "delta_hf",
                  "tg", "xtallinity_pct", "growth_rate"):
            rec[f] = _prompt(f, cast=float)
        rec["chain_conformation"] = _prompt("chain_conformation (e.g. tggt)")
        rec["annotator"] = _prompt("annotator (标注人)")
        rec["confidence"] = _prompt("confidence (high/medium/low)")
        rec["notes"] = _prompt("notes")
        rec["status"] = "filled"
        rec["annotation_date"] = datetime.now(timezone.utc).date().isoformat()

    probs = validate_record(rec, known)
    if probs:
        print("⚠ 该记录存在以下问题（仍可保存，请用 validate 复查）：")
        for p in probs:
            print(f"    - {p}")
    _save(payload)
    print(f"✓ 已保存记录 {rec['gold_id']}（polymer={rec['polymer_abbr']}, doi={rec.get('doi')}）")


def edit_record(gold_id: str, json_str: str) -> None:
    payload = _load()
    rec = next((r for r in payload["records"] if r["gold_id"] == gold_id), None)
    if rec is None:
        print(f"✗ 未找到 gold_id={gold_id}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"✗ JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)
    rec.update({k: v for k, v in data.items() if k in rec})
    rec["status"] = "filled"
    _save(payload)
    print(f"✓ 已更新 {gold_id}")


# --------------------------------------------------------------------------- #
# 列表 / 统计
# --------------------------------------------------------------------------- #
def list_records() -> None:
    payload = _load()
    by_poly: dict[str, list] = {p: [] for p in TARGET_POLYMERS}
    for r in payload["records"]:
        by_poly.setdefault(r["polymer_abbr"], []).append(r)
    for poly in TARGET_POLYMERS:
        recs = by_poly.get(poly, [])
        filled = sum(1 for r in recs if r.get("status") == "filled")
        print(f"\n{poly}: {filled}/{len(recs)} 已填")
        for r in recs:
            mark = "✓" if r.get("status") == "filled" else "·"
            doi = r.get("doi") or "(空)"
            print(f"  [{mark}] {r['gold_id']}  {doi}")


def stats() -> None:
    payload = _load()
    total = len(payload["records"])
    filled = sum(1 for r in payload["records"] if r.get("status") == "filled")
    print(f"总槽位 {total}，已填 {filled}，空 {total - filled}")
    for poly in TARGET_POLYMERS:
        recs = [r for r in payload["records"] if r["polymer_abbr"] == poly]
        f = sum(1 for r in recs if r.get("status") == "filled")
        bar = "█" * f + "░" * (len(recs) - f)
        print(f"  {poly}: {bar} {f}/{len(recs)}")


# --------------------------------------------------------------------------- #
# 导出到主库（find-or-create polymorphs + 写入 observations）
# --------------------------------------------------------------------------- #
def export_db() -> None:
    if not DB_PATH.exists():
        print("✗ 主库不存在，请先运行 init_db.py", file=sys.stderr)
        sys.exit(1)
    payload = _load()
    known = _known_abbrs()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    abbr2id = dict(cur.execute("SELECT abbr, polymer_id FROM polymers").fetchall())

    # 幂等：gold 观测行只由本工具从 gold_set.json 产生，重跑前先清空，避免重复累积。
    # （polymorphs 用 find-or-create，不清空，可复用。）
    n_cleared = cur.execute(
        "DELETE FROM observations WHERE review_status='gold'"
    ).rowcount
    if n_cleared:
        print(f"  · 已清空 {n_cleared} 条旧 gold 观测行（幂等重导）")

    # confidence 文本 → 数值（便于下游区分"自动预填"与"人工核验"）
    CONF_MAP = {"high": 0.9, "medium": 0.5, "low": 0.2}

    n_insert = 0
    for rec in payload["records"]:
        if rec.get("status") != "filled":
            continue
        if rec["polymer_abbr"] not in abbr2id:
            print(f"  ! 跳过 {rec['gold_id']}：polymer_abbr 不在主库")
            continue
        pid = abbr2id[rec["polymer_abbr"]]

        # find-or-create polymorphs 行（按 polymer_id + polymorph_label）
        polymorph_id = None
        label = rec.get("polymorph_label")
        if label:
            row = cur.execute(
                "SELECT polymorph_id FROM polymorphs WHERE polymer_id=? AND polymorph_label=?",
                (pid, label),
            ).fetchone()
            if row:
                polymorph_id = row[0]
            else:
                cur.execute(
                    """INSERT INTO polymorphs
                       (polymer_id, polymorph_label, crystal_system, space_group,
                        a, b, c, alpha, beta, gamma, z, chain_conformation,
                        rho_crystal, fiber_period)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (pid, label, rec.get("crystal_system"), rec.get("space_group"),
                     rec.get("a"), rec.get("b"), rec.get("c"),
                     rec.get("alpha"), rec.get("beta"), rec.get("gamma"),
                     rec.get("z"), rec.get("chain_conformation"),
                     rec.get("rho_crystal"), rec.get("fiber_period")),
                )
                polymorph_id = cur.lastrowid

        # 写入 observations（金标准行）
        # reviewed_by 保留"auto-pre-fill"标记、extraction_confidence 保留 medium=0.5，
        # 使下游能区分"自动预填·需人工复核"与真正人工核验的 gold，避免误当最终真值。
        conf = CONF_MAP.get(rec.get("confidence"))
        reviewed_by = rec.get("annotator") or "auto-pre-fill"
        cur.execute(
            """INSERT INTO observations
               (polymer_id, polymorph_id, doi, ref_year, ref_source, ref_table,
                source_field, tm, tm0, delta_hf, tg, xtallinity_pct,
                growth_rate, reviewed_by, extraction_confidence,
                review_status, conflict_flag)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'gold',0)""",
            (pid, polymorph_id, rec.get("doi"), rec.get("ref_year"),
             rec.get("ref_source"), rec.get("ref_table"), rec.get("source_field"),
             rec.get("tm"), rec.get("tm0"), rec.get("delta_hf"), rec.get("tg"),
             rec.get("xtallinity_pct"), rec.get("growth_rate"),
             reviewed_by, conf),
        )
        n_insert += 1
    conn.commit()
    conn.close()
    print(f"✓ 已向主库写入 {n_insert} 条 gold observations（review_status='gold'，"
          f"其中 reviewed_by='auto-pre-fill' / extraction_confidence=0.5 标记自动预填，需人工复核）")


# --------------------------------------------------------------------------- #
# 前瞻：与抽取结果对比（P2 抽取流水线就绪后启用）
# --------------------------------------------------------------------------- #
def benchmark(extracted_path: str, tol: float = 0.02) -> None:
    """对比抽取结果 JSON 与 gold set，逐字段算相对误差内的命中率。
    extracted_path 文件格式：与 gold_set.json 同构（records 列表，含 gold_id 或 doi+polymer_abbr 对齐）。
    """
    payload = _load()
    gold_by_id = {r["gold_id"]: r for r in payload["records"] if r.get("status") == "filled"}
    ext = json.loads(Path(extracted_path).read_text(encoding="utf-8"))
    ext_recs = ext.get("records", ext if isinstance(ext, list) else [])

    matched = 0
    field_hits: dict[str, list[bool]] = {f: [] for f in NUMERIC_FIELDS}
    for er in ext_recs:
        gid = er.get("gold_id") or f"{er.get('polymer_abbr')}-{er.get('idx')}"
        gr = gold_by_id.get(gid)
        if not gr:
            continue
        matched += 1
        for f in NUMERIC_FIELDS:
            gv, ev = gr.get(f), er.get(f)
            if gv is None or ev is None:
                continue
            rel = abs(ev - gv) / max(abs(gv), 1e-9)
            field_hits[f].append(rel <= tol)
    print(f"匹配到 {matched} 条 gold 记录。各字段命中率（相对误差 ≤ {tol*100:.0f}%）：")
    for f, hits in field_hits.items():
        if hits:
            print(f"  {f:16s} {sum(hits)}/{len(hits)} = {sum(hits)/len(hits)*100:.1f}%")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="Gold Set 标注工具（任务9）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="生成空白骨架（4×5=20 槽位）")
    p_cand = sub.add_parser("list-candidates", help="列出某成员候选文献")
    p_cand.add_argument("polymer", choices=TARGET_POLYMERS)
    p_cand.add_argument("--top", type=int, default=25)
    sub.add_parser("list", help="查看槽位填充情况")
    sub.add_parser("validate", help="校验已填记录")
    sub.add_parser("stats", help="统计覆盖")
    p_add = sub.add_parser("add", help="新增 gold 记录")
    p_add.add_argument("--json", help="JSON 字符串（非交互）")
    p_edit = sub.add_parser("edit", help="编辑已有记录")
    p_edit.add_argument("gold_id")
    p_edit.add_argument("--json", required=True)
    sub.add_parser("export-db", help="写入主库 observations (gold)")
    p_bm = sub.add_parser("benchmark", help="对比抽取结果算准确率")
    p_bm.add_argument("extracted")
    p_bm.add_argument("--tol", type=float, default=0.02)

    args = ap.parse_args()
    if args.cmd == "init":
        init_gold()
    elif args.cmd == "list-candidates":
        list_candidates(args.polymer, args.top)
    elif args.cmd == "list":
        list_records()
    elif args.cmd == "validate":
        sys.exit(0 if validate_all() == 0 else 1)
    elif args.cmd == "stats":
        stats()
    elif args.cmd == "add":
        add_record(args.json)
    elif args.cmd == "edit":
        edit_record(args.gold_id, args.json)
    elif args.cmd == "export-db":
        export_db()
    elif args.cmd == "benchmark":
        benchmark(args.extracted, args.tol)


if __name__ == "__main__":
    main()
