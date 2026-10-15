#!/usr/bin/env python3
"""摘要/OA 信息回填：按 DOI 向 OpenAlex 补齐主语料的 abstract 与 pdf_url

为什么需要它（2026-10-15 实测）：
  search_results.json 里 61 条 on-topic 中**只有 14 条（23%）带摘要**，
  其余 47 条没有可抽取文本 —— 没有 PDF 就完全跑不了抽取。
  而 OpenAlex 对绝大多数条目都提供 `abstract_inverted_index`，
  回填后即使拿不到 PDF 也能先跑一轮真实抽取（召回率会偏低，但能出数、能量化差距）。

回填字段（只补空值，不覆盖已有）：
  abstract      —— 摘要全文（抽取文本源）
  oa_status     —— closed / green / gold / hybrid / bronze
  pdf_url       —— OA 直链（有则可自动下载，无需人工）
  landing_page  —— OA 落地页
  openalex_cited_by —— 被引数（§4.4 冲突消解权重参考）
  abstract_src  —— 'openalex'，标记文本出处，便于 provenance 回溯

用法：
  python src/annotation/backfill_abstracts.py              # 只回填 on-topic 条目
  python src/annotation/backfill_abstracts.py --all        # 全部条目（慢，不建议）
  python src/annotation/backfill_abstracts.py --dry-run    # 只报数不写盘
产物：直接改写 data/literature/search_results.json（先备份 .bak）
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from corpus_quality import classify
from openalex_search import abstract_from_index

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
UA = "polyester-crystal-db/1.0 (mailto:251840135@smail.nju.edu.cn)"
API = "https://api.openalex.org/works/https://doi.org/"


def fetch(doi: str, retries: int = 2) -> dict | None:
    url = (API + urllib.parse.quote(doi, safe="")
           + "?select=doi,title,abstract_inverted_index,open_access,"
             "best_oa_location,cited_by_count")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            if k == retries - 1:
                return None
            time.sleep(1.5 * (k + 1))
    return None


def main(only_ontopic: bool = True, dry_run: bool = False, pause: float = 0.3) -> None:
    data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    targets = []
    for poly, items in data.items():
        for it in items:
            if only_ontopic and classify(it.get("title", ""), it.get("doi", ""),
                                         poly) != "ontopic":
                continue
            targets.append((poly, it))

    need = [(p, i) for p, i in targets if len((i.get("abstract") or "")) < 100]
    print(f"on-topic {len(targets)} 条，其中缺摘要 {len(need)} 条，开始回填 …")

    got_abs = got_pdf = 0
    for n, (poly, it) in enumerate(need, 1):
        doi = (it.get("doi") or "").lower()
        if not doi:
            continue
        w = fetch(doi)
        if not w:
            continue
        ab = abstract_from_index(w.get("abstract_inverted_index"))
        if ab and len(ab) >= len(it.get("abstract") or ""):
            it["abstract"] = ab
            it["abstract_src"] = "openalex"
            got_abs += 1
        oa = w.get("best_oa_location") or {}
        if oa.get("pdf_url"):
            it["pdf_url"] = oa["pdf_url"]
            got_pdf += 1
        it["oa_status"] = (w.get("open_access") or {}).get("oa_status") or "closed"
        it["landing_page"] = oa.get("landing_page_url") or ""
        it["openalex_cited_by"] = w.get("cited_by_count") or 0
        if n % 10 == 0:
            print(f"  … {n}/{len(need)}（已补摘要 {got_abs}，OA 直链 {got_pdf}）")
        time.sleep(pause)

    print(f"\n回填完成：新增摘要 {got_abs} 条，发现 OA PDF 直链 {got_pdf} 条")
    if dry_run:
        print("--dry-run：未写盘")
        return

    bak = SEARCH_PATH.with_suffix(".json.bak")
    bak.write_text(SEARCH_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    SEARCH_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 已写回 {SEARCH_PATH.name}（备份 {bak.name}）")

    have = sum(1 for _, i in targets if len((i.get("abstract") or "")) >= 100)
    print(f"  on-topic 有可抽取文本：{have}/{len(targets)} "
          f"({have / max(len(targets),1) * 100:.0f}%)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="处理全部条目而非仅 on-topic")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    main(only_ontopic=not a.all, dry_run=a.dry_run)
