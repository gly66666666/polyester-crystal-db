#!/usr/bin/env python3
"""抽取质量评测（执行计划 P1 验收指标：字段级准确率 ≥ 80%）

对比 gold set（人工核验基准）与抽取结果，按 (polymer_abbr, doi) 匹配，
逐数值字段计算 precision / recall / F1（相对误差 ≤ tol 视为命中）。

用法：
  python -m src.extraction.evaluate --extracted data/processed/extraction_output.json
  python -m src.extraction.evaluate --extracted data/processed/extraction_output.json --tol 0.05

gold set 默认读取 data/gold_set/gold_set.json（只取 status=='filled' 的记录）。
抽取结果可以是 pipeline --dry-run 的输出，或真实批次落库后导出的 JSON。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
GOLD_PATH = PROJECT_ROOT / "data" / "gold_set" / "gold_set.json"

# 参与评测的数值字段（gold 与 extracted 共用的 schema 列名）
NUMERIC_FIELDS = [
    "a", "b", "c", "alpha", "beta", "gamma", "z", "rho_crystal",
    "fiber_period", "tm", "tm0", "delta_hf", "tg", "xtallinity_pct", "growth_rate",
]


def _load_gold(path: str = None) -> dict:
    p = Path(path) if path else GOLD_PATH
    if not p.exists():
        print(f"✗ 未找到 gold 文件：{p}（请先完成任务9标注或指定 --gold）。", file=sys.stderr)
        sys.exit(1)
    data = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for r in data["records"]:
        if r.get("status") != "filled" or not r.get("doi"):
            continue
        out.setdefault(r["polymer_abbr"], {})[r["doi"]] = r
    return out


def _load_extracted(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("records", [])
    out = {}
    for r in items:
        doi = r.get("doi")
        abbr = r.get("polymer_abbr")
        if not doi or not abbr:
            continue
        # 兼容两种结构：dry-run 的 {obs:flat} 或扁平 {doi, ..., a:..}
        obs = r.get("obs", r)
        if "a" not in obs and "flat" in r:
            obs = r["flat"]
        out.setdefault(abbr, {})[doi] = obs
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="抽取字段级 P/R/F1 评测")
    ap.add_argument("--extracted", required=True, help="抽取结果 JSON（pipeline dry-run 输出或批次导出）")
    ap.add_argument("--gold", default=str(GOLD_PATH))
    ap.add_argument("--tol", type=float, default=0.02, help="相对误差容忍（默认 2%）")
    args = ap.parse_args()

    gold = _load_gold(args.gold)
    ext = _load_extracted(args.extracted)

    # 统计
    stats = {f: {"tp": 0, "fp": 0, "fn": 0} for f in NUMERIC_FIELDS}
    matched = 0
    for abbr, by_doi in gold.items():
        for doi, g in by_doi.items():
            e = ext.get(abbr, {}).get(doi)
            if not e:
                # gold 有、extracted 无 → 全部 FN
                for f in NUMERIC_FIELDS:
                    if g.get(f) is not None:
                        stats[f]["fn"] += 1
                continue
            matched += 1
            for f in NUMERIC_FIELDS:
                gv, ev = g.get(f), e.get(f)
                if gv is None:
                    # gold 未标注该字段 → 视为中性，不计入（避免惩罚抽取出的额外正确数据）
                    continue
                if ev is None:
                    stats[f]["fn"] += 1
                    continue
                rel = abs(ev - gv) / max(abs(gv), 1e-9)
                if rel <= args.tol:
                    stats[f]["tp"] += 1
                else:
                    stats[f]["fp"] += 1
                    stats[f]["fn"] += 1

    print(f"匹配到 gold 记录 {matched} 条（按 polymer+doi）。相对误差容忍 {args.tol*100:.0f}%。\n")
    print(f"{'字段':<16}{'P':>8}{'R':>8}{'F1':>8}{'TP/FP/FN':>14}")
    tot = {"tp": 0, "fp": 0, "fn": 0}
    for f in NUMERIC_FIELDS:
        s = stats[f]
        p = s["tp"] / (s["tp"] + s["fp"]) if (s["tp"] + s["fp"]) else 0.0
        r = s["tp"] / (s["tp"] + s["fn"]) if (s["tp"] + s["fn"]) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        tot["tp"] += s["tp"]; tot["fp"] += s["fp"]; tot["fn"] += s["fn"]
        print(f"{f:<16}{p*100:>7.1f}%{r*100:>7.1f}%{f1*100:>7.1f}%"
              f"{s['tp']}/{s['fp']}/{s['fn']:>5}")
    p = tot["tp"] / (tot["tp"] + tot["fp"]) if (tot["tp"] + tot["fp"]) else 0.0
    r = tot["tp"] / (tot["tp"] + tot["fn"]) if (tot["tp"] + tot["fn"]) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    print(f"\n{'微平均(合并统计)':<16}{p*100:>7.1f}%{r*100:>7.1f}%{f1*100:>7.1f}%")

    verdict = "通过（≥80%）" if f1 >= 0.8 else "未达标（<80%，需提高人工复核比例，不进入规模化）"
    print(f"\nP1 验收（字段级 F1 ≥ 80%）：{verdict}")


if __name__ == "__main__":
    main()
