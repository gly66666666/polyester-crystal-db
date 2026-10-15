#!/usr/bin/env python3
"""OpenAlex 定向检索：召回强、带 OA/PDF 直链、带摘要全文

为什么改用它（2026-10-15 实测对比）：
  * CrossRef `query.bibliographic` 对 "poly(butylene succinate) crystal structure"
    只返回 2 条；OpenAlex 同一 query 命中 4251 条。CrossRef 召回率根本不够用。
  * OpenAlex 额外提供三项 CrossRef 没有、但对本项目至关重要的信息：
      1. `open_access.oa_status` + `best_oa_location.pdf_url`
         → 直接判断这篇能不能**自动下载 PDF**（2026-10-10 实测：可自动下载的仅约 2%，
           这个数字决定了 P2 能否规模化，必须逐篇实测而不是估）
      2. `abstract_inverted_index` —— 摘要全文。部分论文的摘要里就写了晶胞参数，
         即使拿不到 PDF 也可能抽到值。
      3. `cited_by_count` —— 用于判断该值是否为「通行引用值」，辅助 §4.4 冲突消解。
  * OpenAlex 结果天然带 DOI，且源自 CrossRef 元数据，满足「DOI 入库前核验」红线；
    本脚本另对最终入选条目做一次 CrossRef 复核（--verify 默认开）。

产物：data/literature/openalex_results.json
     data/processed/openalex_oa_report.md   （OA 可得性实测报告）

用法：
  python src/annotation/openalex_search.py
  python src/annotation/openalex_search.py --polymers PCL,PBS --per-page 50
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from corpus_quality import (TARGETS, classify, has_cell_signal, verify_doi)
from targeted_search import ALT_NAMES, CELL_QUERIES, QUERY_NAMES

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
OUT_PATH = PROJECT_ROOT / "data" / "literature" / "openalex_results.json"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "openalex_oa_report.md"
API = "https://api.openalex.org/works"
UA = "polyester-crystal-db/1.0 (mailto:251840135@smail.nju.edu.cn)"


def _get(params: dict, retries: int = 3) -> dict | None:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if k == retries - 1:
                print(f"    ! 失败 {e}")
                return None
            time.sleep(2 * (k + 1))
    return None


def abstract_from_index(inv: dict | None) -> str:
    """OpenAlex 的 abstract_inverted_index {词: [位置...]} -> 还原为文本。"""
    if not inv:
        return ""
    slots: dict[int, str] = {}
    for word, positions in inv.items():
        for p in positions:
            slots[p] = word
    if not slots:
        return ""
    return " ".join(slots[i] for i in sorted(slots))


def search_one(query: str, per_page: int) -> list[dict]:
    resp = _get({
        "search": query,
        "per-page": per_page,
        "select": ("doi,title,publication_year,primary_location,best_oa_location,"
                   "open_access,abstract_inverted_index,cited_by_count,type"),
    })
    if not resp:
        return []
    out = []
    for w in resp.get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        if not doi:
            continue
        pl = (w.get("primary_location") or {}).get("source") or {}
        oa = (w.get("best_oa_location") or {})
        out.append({
            "doi": doi,
            "title": w.get("title") or "",
            "year": w.get("publication_year"),
            "journal": pl.get("display_name") or "",
            "abstract": abstract_from_index(w.get("abstract_inverted_index")),
            "cited_by": w.get("cited_by_count") or 0,
            "oa_status": (w.get("open_access") or {}).get("oa_status") or "closed",
            "pdf_url": oa.get("pdf_url") or "",
            "landing_page": oa.get("landing_page_url") or "",
            "url": f"https://doi.org/{doi}",
        })
    return out


def run(polymers: list[str], per_page: int, pause: float = 0.4,
        verify: bool = True) -> dict:
    known = {p: {(i.get("doi") or "").lower() for i in v}
             for p, v in json.loads(SEARCH_PATH.read_text(encoding="utf-8")).items()}
    res: dict[str, list[dict]] = {}
    for poly in polymers:
        names = [QUERY_NAMES.get(poly, poly)] + ALT_NAMES.get(poly, [])
        seen: dict[str, dict] = {}
        print(f"[{poly}] OpenAlex 检索中 …")
        for name in names:
            for cq in CELL_QUERIES:
                for h in search_one(f"{name} {cq}", per_page):
                    prev = seen.get(h["doi"])
                    # 同一 DOI 多次命中时保留信息更全的那条
                    if prev is None or len(h["abstract"]) > len(prev["abstract"]):
                        seen[h["doi"]] = h
                time.sleep(pause)

        kept = []
        for doi, h in seen.items():
            if classify(h["title"], doi, poly) != "ontopic":
                continue
            h["cell_signal"] = has_cell_signal(h["title"])
            h["in_main_corpus"] = doi in known.get(poly, set())
            h["source"] = "openalex"
            kept.append(h)
        kept.sort(key=lambda x: (not x["cell_signal"], -x["cited_by"]))
        res[poly] = kept
        n_pdf = sum(1 for k in kept if k["pdf_url"])
        n_abs = sum(1 for k in kept if len(k["abstract"]) > 200)
        print(f"  -> 召回 {len(seen)}，on-topic {len(kept)}"
              f"（晶胞级 {sum(1 for k in kept if k['cell_signal'])}，"
              f"有 OA PDF 直链 {n_pdf}，有摘要 {n_abs}）")

    if verify:
        print("\n=== CrossRef 复核入选 DOI ===")
        bad = 0
        for poly, items in res.items():
            for it in items:
                v = verify_doi(it["doi"])
                it["crossref_ok"] = bool(v)
                if not v:
                    bad += 1
                    print(f"  [FAIL] {poly} {it['doi']}")
        print(f"  复核完成，失败 {bad} 条")

    return res


def write_report(res: dict) -> None:
    tot = sum(len(v) for v in res.values())
    pdf = sum(1 for v in res.values() for i in v if i["pdf_url"])
    absc = sum(1 for v in res.values() for i in v if len(i["abstract"]) > 200)
    gold = sum(1 for v in res.values() for i in v if i["oa_status"] == "gold")
    green = sum(1 for v in res.values() for i in v if i["oa_status"] == "green")
    lines = [
        "# OpenAlex 定向检索 + OA 可得性实测报告",
        "",
        f"源：{OUT_PATH.name}｜on-topic 合计 **{tot}** 条",
        "",
        "## 一、关键结论",
        "",
        f"| 指标 | 条数 | 占比 |",
        "|---|---:|---:|",
        f"| on-topic 合计 | {tot} | 100% |",
        f"| **有 OA PDF 直链（可自动下载）** | {pdf} | "
        f"{pdf / tot * 100:.1f}% |" if tot else "| 有 OA PDF 直链 | 0 | — |",
        f"| 有摘要全文（>200 字符，可无 PDF 抽取） | {absc} | "
        f"{absc / tot * 100:.1f}% |" if tot else "| 有摘要全文 | 0 | — |",
        f"| Gold OA | {gold} | "
        f"{gold / tot * 100:.1f}% |" if tot else "| Gold OA | 0 | — |",
        f"| Green OA（仓储自存） | {green} | "
        f"{green / tot * 100:.1f}% |" if tot else "| Green OA | 0 | — |",
        "",
        "## 二、逐成员明细",
        "",
        "| 成员 | on-topic | 晶胞级 | OA PDF 直链 | 有摘要 |",
        "|:---|---:|---:|---:|---:|",
    ]
    for poly in TARGETS:
        items = res.get(poly, [])
        if not items:
            continue
        lines.append(
            f"| {poly} | {len(items)} | {sum(1 for i in items if i['cell_signal'])} "
            f"| {sum(1 for i in items if i['pdf_url'])} "
            f"| {sum(1 for i in items if len(i['abstract']) > 200)} |"
        )
    lines += [
        "",
        "## 三、怎么读这份报告",
        "",
        "1. **OA PDF 直链占比** 决定「自动抓取」能不能支撑 P2 规模化。若远低于 50%，",
        "   就必须走南大图书馆订阅 / 馆际互借 / 人工下载，不要指望爬虫。",
        "2. **有摘要** 的条目即使拿不到 PDF 也能进流水线——但晶胞参数多在全文表格，",
        "   走摘要的召回率会明显偏低，需在设计 F1 指标时单独统计这组。",
        "3. `cited_by` 高的条目更可能是「通行引用值」，在 §4.4 冲突消解里权重更高。",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ OA 报告已写入 {REPORT_PATH}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--polymers", default=None)
    ap.add_argument("--per-page", type=int, default=25)
    ap.add_argument("--no-verify", action="store_true")
    a = ap.parse_args()
    polymers = [p.strip() for p in a.polymers.split(",")] if a.polymers else TARGETS
    res = run(polymers, a.per_page, verify=not a.no_verify)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ 已写入 {OUT_PATH}")
    write_report(res)


if __name__ == "__main__":
    main()
