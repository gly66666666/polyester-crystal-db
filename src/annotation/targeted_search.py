#!/usr/bin/env python3
"""定向补检索：用 CrossRef 找回被原检索漏掉的「晶胞级」文献

为什么需要它（2026-10-15 实测）：
  现有 data/literature/search_results.json（725 篇）经 corpus_quality 过滤后
  只有 29 篇 on-topic，其中 **PCL / PBS 为 0 篇**。查证后确认不是分类器误杀：
    * PCL 语料里 4 条含 caprolactone 的"晶体结构"全是
      cyclohexanone monooxygenase 复合物 与 Polygonatum cyrtonema lectin (PCL)
      —— 第五类缩写歧义（百合凝集素也叫 PCL）；
    * PBS 语料里的候选全是 ran-/co-/grafted/composite 衍生体系，排除正确。
  → 原始检索 query 本身就没捞到均聚物本体晶胞论文，必须定向补检索。

设计要点：
  1. 走 CrossRef REST API（本机可达；沙箱白名单允许 api.crossref.org）。
     **所有结果天然经过 CrossRef 核验**，天然满足项目「DOI 入库前必须机器核验」红线。
  2. 用「聚合物全名 + 晶胞级关键词」构造 query，避免缩写歧义。
     （这是原检索的教训：用缩写 PCL/PBS 检索必然捞回 PbS、PCl、凝集素）
  3. 结果立即过 corpus_quality.classify，只留 ontopic；并标 has_cell_signal。
  4. 与既有语料按 DOI 去重，只输出新增部分。

用法：
  python src/annotation/targeted_search.py                      # 全 12 成员
  python src/annotation/targeted_search.py --polymers PCL,PBS
  python src/annotation/targeted_search.py --merge              # 并回主语料（先自动备份）

产物：data/literature/search_results_targeted.json
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from corpus_quality import classify, has_cell_signal, normalize

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
OUT_PATH = PROJECT_ROOT / "data" / "literature" / "search_results_targeted.json"
API = "https://api.crossref.org/works"
UA = "polyester-crystal-db/1.0 (mailto:251840135@smail.nju.edu.cn)"

# 检索用词：**只用聚合物全名**，杜绝缩写歧义
QUERY_NAMES = {
    "PET":  "poly(ethylene terephthalate)",
    "PTT":  "poly(trimethylene terephthalate)",
    "PBT":  "poly(butylene terephthalate)",
    "PEN":  "poly(ethylene naphthalate)",
    "PBN":  "poly(butylene naphthalate)",
    "PLA":  "poly(l-lactide)",
    "PGA":  "poly(glycolic acid)",
    "PCL":  "poly(epsilon-caprolactone)",
    "PBS":  "poly(butylene succinate)",
    "PBSA": "poly(butylene succinate-co-adipate)",
    "PHB":  "poly(3-hydroxybutyrate)",
    "PHBV": "poly(3-hydroxybutyrate-co-3-hydroxyvalerate)",
}

# 晶胞级关键词：这才是我们真正要抽的东西（a/b/c/α/β/γ）
CELL_QUERIES = [
    "crystal structure",
    "unit cell",
    "crystal modification",
    "polymorphism",
]

# 备用全名（提高召回；同一成员多个写法）
ALT_NAMES = {
    "PLA":  ["polylactide", "poly(lactic acid)"],
    "PGA":  ["polyglycolide"],
    "PCL":  ["polycaprolactone"],
    "PBS":  ["polybutylene succinate"],
    "PHB":  ["polyhydroxybutyrate", "poly(3 hydroxybutyrate)"],
    "PBT":  ["poly(tetramethylene terephthalate)"],
    "PTT":  ["poly(propylene terephthalate)"],
    "PHBV": ["poly(hydroxybutyrate-co-hydroxyvalerate)"],
    "PBN":  ["poly(butylene 2,6-naphthalate)"],
    "PEN":  ["poly(ethylene 2,6-naphthalate)"],
}


def _get(params: dict, retries: int = 3) -> dict | None:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if k == retries - 1:
                print(f"    ! 请求失败 {e}")
                return None
            time.sleep(2 * (k + 1))
    return None


def search_one(query: str, rows: int = 20) -> list[dict]:
    resp = _get({
        "query.bibliographic": query,
        "rows": rows,
        "select": "DOI,title,author,container-title,issued,type,abstract",
    })
    if not resp:
        return []
    out = []
    for it in resp.get("message", {}).get("items", []):
        if it.get("type") not in ("journal-article", None):
            continue
        doi = (it.get("DOI") or "").lower()
        if not doi:
            continue
        title = (it.get("title") or [""])[0] or ""
        authors = "; ".join(
            " ".join(x for x in [a.get("given"), a.get("family")] if x)
            for a in (it.get("author") or [])[:6]
        )
        year = ((it.get("issued", {}).get("date-parts") or [[None]])[0][0])
        out.append({
            "doi": doi,
            "title": title,
            "authors": authors,
            "journal": (it.get("container-title") or [""])[0],
            "year": year,
            "abstract": (it.get("abstract") or "")[:1000],
            "url": f"https://doi.org/{doi}",
        })
    return out


def run(polymers: list[str], rows: int, pause: float = 0.6) -> dict:
    existing = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    known = {p: {(i.get("doi") or "").lower() for i in v} for p, v in existing.items()}

    result: dict[str, list[dict]] = {}
    for poly in polymers:
        names = [QUERY_NAMES.get(poly, poly)] + ALT_NAMES.get(poly, [])
        seen: dict[str, dict] = {}
        print(f"[{poly}] 检索中 …")
        for name in names:
            for cellq in CELL_QUERIES:
                q = f"{name} {cellq}"
                hits = search_one(q, rows=rows)
                for h in hits:
                    seen.setdefault(h["doi"], h)
                time.sleep(pause)
        kept = []
        for doi, h in seen.items():
            if doi in known.get(poly, set()):
                continue  # 主语料已有，不重复
            if classify(h["title"], doi, poly) != "ontopic":
                continue
            h["cell_signal"] = has_cell_signal(h["title"])
            h["query_hit"] = True
            kept.append(h)
        # 有晶胞强信号的排前面
        kept.sort(key=lambda x: (not x["cell_signal"], -(x.get("year") or 0)))
        result[poly] = kept
        print(f"  -> 新检索 {len(seen)} 条，去重后新增 on-topic {len(kept)} 条"
              f"（其中晶胞级 {sum(1 for k in kept if k['cell_signal'])}）")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--polymers", default=None, help="逗号分隔；默认全部 12 个 Tier1 成员")
    ap.add_argument("--rows", type=int, default=20, help="每个 query 取回条数（默认 20）")
    ap.add_argument("--merge", action="store_true", help="并回 search_results.json（先备份）")
    a = ap.parse_args()

    from corpus_quality import TARGETS  # 单一真源
    polymers = [p.strip() for p in a.polymers.split(",")] if a.polymers else TARGETS

    res = run(polymers, a.rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ 定向检索结果已写入 {OUT_PATH}")

    total = sum(len(v) for v in res.values())
    strong = sum(1 for v in res.values() for i in v if i["cell_signal"])
    print(f"  合计新增 on-topic {total} 条，其中晶胞级 {strong} 条")

    if a.merge:
        data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
        bak = SEARCH_PATH.with_suffix(".json.bak")
        bak.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        for poly, items in res.items():
            have = {(i.get("doi") or "").lower() for i in data.get(poly, [])}
            for it in items:
                if it["doi"] not in have:
                    data.setdefault(poly, []).append(it)
        SEARCH_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 已并入主语料（备份 {bak.name}）")


if __name__ == "__main__":
    main()
