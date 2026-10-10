#!/usr/bin/env python3
"""文献检索脚本（任务8，改进版）

用法:
  python src/extraction/literature_search.py                          # 全量检索 12 个成员
  python src/extraction/literature_search.py --polymers PET,PLA --per-term 5   # 快速验证

说明:
  - 数据源：CrossRef REST API（开放、无需密钥）。通过 mailto 进入 polite pool 降低限流。
  - 只取元数据（DOI / 标题 / 作者 / 期刊 / 年份 / 摘要片段），不做全文抓取——
    全文 PDF 里的晶胞参数抽取是后续人工 / PDF 解析阶段（任务9）的工作。
  - 结果按 DOI 去重，保存到 data/literature/search_results.json。
  - PoLyInfo 因需 NIMS 账号登录、无公开 API，无法脚本化；其用途是“交叉校验”，
    在核验阶段由人工在网页端完成，不在此脚本内。
"""

import argparse
import json
import time
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEARCH_TERMS_PATH = PROJECT_ROOT / "src" / "extraction" / "search_terms.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"

# 用于 CrossRef polite pool；可改成你自己的邮箱
MAILTO = "251840135@smail.nju.edu.cn"
CROSSREF_API = "https://api.crossref.org/works"
HEADERS = {"User-Agent": f"PolyesterCrystalDB/0.1 (mailto:{MAILTO})"}


def search_one(query: str, per_term: int, session: requests.Session) -> list:
    params = {
        "query.bibliographic": query,
        "rows": per_term,
        "select": "DOI,title,author,container-title,published-print,published,abstract,URL",
        "sort": "relevance",
    }
    try:
        r = session.get(CROSSREF_API, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        items = r.json()["message"]["items"]
    except Exception as e:  # noqa: BLE001
        print(f"    x 检索失败 [{query[:40]}]: {e}")
        return []

    out = []
    for it in items:
        doi = it.get("DOI")
        if not doi:
            continue
        authors = ", ".join(
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in it.get("author", [])
        )
        year = (it.get("published-print") or it.get("published") or {}).get(
            "date-parts", [[None]]
        )[0][0]
        out.append(
            {
                "doi": doi,
                "title": (it.get("title") or [""])[0],
                "authors": authors,
                "journal": (it.get("container-title") or [""])[0],
                "year": year,
                "abstract": (it.get("abstract") or "")[:1000],
                "url": it.get("URL", ""),
            }
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--polymers", default=None, help="逗号分隔的子集，如 PET,PLA")
    ap.add_argument("--per-term", type=int, default=10, help="每个检索词最多返回条数")
    ap.add_argument("--sleep", type=float, default=0.3, help="请求间隔秒数，避免限流")
    args = ap.parse_args()

    terms = json.loads(SEARCH_TERMS_PATH.read_text(encoding="utf-8"))
    selected = {
        k: v
        for k, v in terms.items()
        if not args.polymers or k in set(args.polymers.split(","))
    }

    session = requests.Session()
    results: dict = {}
    total = 0
    for abbr, meta in selected.items():
        print(f"> {abbr} ({meta['name_en']})")
        seen = set()
        collected = []
        for term in meta["search_terms"]:
            print(f"    - {term}")
            for rec in search_one(term, args.per_term, session):
                if rec["doi"] not in seen:
                    seen.add(rec["doi"])
                    collected.append(rec)
            time.sleep(args.sleep)
        results[abbr] = collected
        total += len(collected)
        print(f"    -> 去重后 {len(collected)} 篇\n")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已保存: {OUTPUT_PATH}")
    print(f"合计 {total} 篇不重复文献")


if __name__ == "__main__":
    main()
