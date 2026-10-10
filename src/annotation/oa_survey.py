#!/usr/bin/env python3
"""全文可获取性分层抽样实测（论文结果用，可复现）

与 fetch_pdf.py 的区别：
- fetch_pdf 是**生产工具**（为流水线抓 PDF，结果写入 oa_availability.json）；
- 本脚本是**测量工具**（为论文产出可复现的统计），不会覆盖生产结果，
  且会把"Open Access"进一步拆分为：
      · oa_pdf       —— Unpaywall 给出 url_for_pdf，且实际取回内容确为 PDF（可自动下载）
      · oa_landing   —— 判定为 OA，但链接是出版商落地页 / HTML，无法自动下载
      · closed       —— 无合法 OA 版本
      · query_failed —— Unpaywall 查询失败（不计入分母结论，单独报告）

这样区分很重要：只看 Unpaywall 的 is_oa 会显著高估可自动化获取的比例。

用法：
  python src/annotation/oa_survey.py --per-polymer 5           # 默认 12 成员 × 5
  python src/annotation/oa_survey.py --polymers PET,PLA --per-polymer 10
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
OUT = PROJECT_ROOT / "data" / "processed" / "oa_survey.json"

EMAIL = "251840135@smail.nju.edu.cn"
UNPAYWALL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UA = f"poly-crystal-db/0.1 (OA survey; mailto:{EMAIL})"

ALL_POLYMERS = ["PET", "PBT", "PTT", "PEN", "PBN", "PLA",
                "PCL", "PGA", "PBS", "PBSA", "PHB", "PHBV"]


def ranked(polymers: list[str], top: int) -> list[dict]:
    spec_path = PROJECT_ROOT / "src" / "annotation" / "shortlist.py"
    spec = importlib.util.spec_from_file_location("_shortlist", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ranked_all = mod.rank(polymers)
    out = []
    for p in polymers:
        for c in ranked_all.get(p, [])[:top]:
            out.append({"polymer_abbr": p, "doi": c["doi"], "title": c.get("title")})
    return out


def unpaywall(doi: str, retries: int = 2):
    url = UNPAYWALL.format(doi=urllib.parse.quote(doi), email=urllib.parse.quote(EMAIL))
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None
    return None


def pdf_url(rec: dict):
    locs = ([rec.get("best_oa_location")] if rec.get("best_oa_location") else []) + \
           (rec.get("oa_locations") or [])
    for loc in locs:
        if loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
    return None


def is_really_pdf(url: str) -> tuple[bool, str]:
    """取回前 2 KB，用 %PDF 魔数判断是否为可直接下载的 PDF。"""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"})
        with urllib.request.urlopen(req, timeout=45) as r:
            head = r.read(2048)
    except Exception as e:  # noqa: BLE001
        return False, f"err:{type(e).__name__}"
    return head[:4] == b"%PDF", ("pdf" if head[:4] == b"%PDF" else "html/landing")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--polymers", default=",".join(ALL_POLYMERS))
    ap.add_argument("--per-polymer", type=int, default=5)
    ap.add_argument("--sleep", type=float, default=0.35)
    args = ap.parse_args()

    polys = [p.strip().upper() for p in args.polymers.split(",") if p.strip()]
    targets = ranked(polys, args.per_polymer)
    print(f"分层抽样：{len(polys)} 个成员 × {args.per_polymer} = {len(targets)} 条\n")

    rows = []
    for i, t in enumerate(targets, 1):
        rec = unpaywall(t["doi"])
        time.sleep(args.sleep)
        row = {"polymer_abbr": t["polymer_abbr"], "doi": t["doi"], "title": t.get("title")}
        if rec is None:
            row.update(status="query_failed", is_oa=None, has_pdf_url=None, real_pdf=None)
        else:
            is_oa = bool(rec.get("is_oa"))
            u = pdf_url(rec)
            real = None
            if u:
                ok, why = is_really_pdf(u)
                real = bool(ok)
                row["pdf_check"] = why
            row.update(is_oa=is_oa, has_pdf_url=bool(u), real_pdf=real,
                       oa_host_type=(rec.get("best_oa_location") or {}).get("host_type"))
            row["status"] = ("oa_pdf" if real else
                             "oa_landing" if is_oa else "closed")
        rows.append(row)
        print(f"[{i:>3}/{len(targets)}] {row.get('status'):<12} "
              f"{t['polymer_abbr']:<5} {t['doi']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    c = collections.Counter(r.get("status") for r in rows)
    n = len(rows)
    ok_n = n - c.get("query_failed", 0)
    print("\n===== 分层抽样结果 =====")
    for k in ["closed", "oa_landing", "oa_pdf", "query_failed"]:
        if c.get(k):
            print(f"  {k:<12} {c[k]:>3}  ({c[k]/n:6.1%} / 有效样本 {c[k]/max(ok_n,1):6.1%})")
    print(f"  有效样本 {ok_n}/{n}")
    is_oa_n = sum(1 for r in rows if r.get("is_oa"))
    print(f"  Unpaywall is_oa=True：{is_oa_n} ({is_oa_n/max(ok_n,1):.1%})；"
          f"其中可自动下载 PDF：{c.get('oa_pdf',0)}")
    print(f"\n明细已写入 {OUT}")


if __name__ == "__main__":
    main()
