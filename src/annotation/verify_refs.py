#!/usr/bin/env python3
"""参考文献 DOI 核验工具（论文写作用）

合规红线：任何 DOI 写入论文 / 代码 / 数据前，必须经 CrossRef 核验题录。
本脚本只做「检索 + 打印真实题录」，供人工挑选，绝不臆造 DOI。

用法：
    python src/annotation/verify_refs.py            # 跑内置候选清单
    python src/annotation/verify_refs.py "标题关键词"  # 单条检索
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

MAILTO = "251840135@nju.edu.cn"
BASE = "https://api.crossref.org/works"


def query(title: str, rows: int = 3) -> list[dict]:
    params = urllib.parse.urlencode(
        {"query.bibliographic": title, "rows": rows, "mailto": MAILTO,
         "select": "DOI,title,container-title,issued,author,type,volume,page"}
    )
    req = urllib.request.Request(
        f"{BASE}?{params}",
        headers={"User-Agent": f"polyester-crystal-db/1.0 (mailto:{MAILTO})"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)
    out = []
    for it in data.get("message", {}).get("items", []):
        out.append({
            "doi": it.get("DOI"),
            "title": (it.get("title") or [""])[0],
            "journal": (it.get("container-title") or [""])[0],
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "type": it.get("type"),
            "author": ", ".join(
                f"{a.get('family','')}" for a in (it.get("author") or [])[:3]
            ),
        })
    return out


def query_doi(doi: str) -> dict | None:
    try:
        req = urllib.request.Request(
            f"{BASE}/{urllib.parse.quote(doi)}",
            headers={"User-Agent": f"polyester-crystal-db/1.0 (mailto:{MAILTO})"},
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            it = json.load(r)["message"]
        return {
            "doi": it.get("DOI"),
            "title": (it.get("title") or [""])[0],
            "journal": (it.get("container-title") or [""])[0],
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
        }
    except Exception as e:  # noqa: BLE001
        return {"doi": doi, "error": str(e)}


CANDIDATES = [
    # --- 领域经典：聚酯 / 高分子结晶 ---
    "The crystal structure of polyethylene terephthalate",
    "Crystal structure and morphology of poly(L-lactide) alpha form",
    "Crystal structure of poly(butylene terephthalate)",
    "Melting process and the equilibrium melting temperature of polychlorotrifluoroethylene",
    "Theory of formation of polymer crystals with folded chains in dilute solution",
    # --- 现有数据库 / 资源 ---
    "Crystallography Open Database an open-access collection of crystal structures",
    "The Cambridge Structural Database",
    "Commentary: The Materials Project: A materials genome approach",
    "PoLyInfo polymer database polymeric materials design",
    # --- 文本挖掘 / LLM 抽取 ---
    "ChemDataExtractor: A toolkit for automated extraction of chemical information",
    "Large language models for scientific information extraction from materials science literature",
    "Extracting structured data from polymer literature using large language models",
    "Assessment of large language models for materials science text mining",
    "A large language model for materials discovery",
    # --- 数据质量 / 本体 ---
    "Reproducibility and data quality in materials databases",
]


def main() -> None:
    args = sys.argv[1:]
    targets = args if args else CANDIDATES
    for t in targets:
        print("=" * 78)
        print("QUERY:", t)
        if t.lower().startswith("10."):
            print(json.dumps(query_doi(t), ensure_ascii=False, indent=2))
            continue
        try:
            for hit in query(t, rows=3):
                print(f"  DOI  : {hit['doi']}")
                print(f"  TITLE: {hit['title']}")
                print(f"  JOURNAL: {hit['journal']} ({hit['year']}) [{hit['type']}]")
                print(f"  AUTH : {hit['author']}")
                print("  -")
        except Exception as e:  # noqa: BLE001
            print("  ERROR:", e)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
