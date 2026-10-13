#!/usr/bin/env python3
"""语料质量分类器（任务：基准重建的前置）

背景（2026-10-13 实测发现）：
  search_results.json 里混入了大量**与本项目无关**的条目，直接喂给流水线会白白烧 API 额度：
  1. 缩写歧义：PET 被当成 Positron Emission Tomography（正电子发射断层），
     PTT 被当成 photothermal therapy（光热治疗）；
  2. 无关小分子/蛋白晶体结构：Ganciclovir / Guanfacine / 3-hydroxyisobutyrate dehydrogenase /
     LiLaP4O12 / carbaporphyrinoid 等，只是标题里带 "crystal structure"；
  3. 非正文条目：.s001/.s002 补充材料、/pdb 蛋白库条目、/v1/review1 审稿意见与决定信。

本模块把每条语料分为三档：
  ontopic  —— 确为该均聚物的晶体/结晶研究（可用作基准与抽取目标）
  offtopic —— 同家族但非均聚物本体：共聚酯 / 共混 / 立构复合 / 环状二聚体 / 模型化合物等
  junk     —— 无关领域、缩写歧义、补充材料、PDB、审稿文件（应直接排除）

用法：
  python src/annotation/corpus_quality.py                 # 打印统计 + 写报告
  python src/annotation/corpus_quality.py --verify        # 额外用 CrossRef 核验 on-topic DOI 题录
产物：data/processed/corpus_quality.json
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "corpus_quality.json"

TARGETS = ["PET", "PTT", "PBT", "PLA"]

# 成员同义词（标题里出现任一即认为在谈该聚合物）—— 覆盖全部 12 个 Tier1 成员
SYNONYMS = {
    "PET":  ["ethylene terephthalate", "(pet)", "poly(ethylene terephthalate)"],
    "PTT":  ["trimethylene terephthalate", "polytrimethylene", "(ptt)", "3gt"],
    "PBT":  ["butylene terephthalate", "tetramethylene terephthalate",
             "(pbt)", "polybutylene terephthalate"],
    "PEN":  ["ethylene naphthalate", "(pen)", "poly(ethylene naphthalate)"],
    "PBN":  ["butylene naphthalate", "(pbn)", "poly(butylene naphthalate)"],
    "PLA":  ["lactic acid", "lactide", "polylactide", "(pla)"],
    "PGA":  ["glycolic acid", "polyglycolide", "(pga)", "poly(glycolic acid)"],
    "PCL":  ["caprolactone", "(pcl)", "poly(caprolactone)"],
    "PBS":  ["butylene succinate", "(pbs)", "poly(butylene succinate)"],
    "PBSA": ["succinate-co-adipate", "butylene succinate-co-adipate", "(pbsa)"],
    "PHB":  ["hydroxybutyrate", "(phb)", "poly(3-hydroxybutyrate)"],
    "PHBV": ["hydroxybutyrate-co-valerate", "(phbv)",
             "poly(3-hydroxybutyrate-co-3-hydroxyvalerate)"],
}

# 缩写歧义/医学影像/光热治疗 —— 与高分子结晶无关
MED_TERMS = ["positron", "tomograph", "detector", "sipm", "scintillator",
             "photothermal", "nanoagent", "tumor", "therapy", "radiotracer",
             "imaging", "pixilated", "pixellated"]

# 同家族但非均聚物本体
OFFTOPIC_TERMS = ["copolyester", "copolymer", "blend", "composite", "nanocomposite",
                  "inclusion", "stereocomplex", "cyclic dimer", "model compound",
                  "graphene", "nanofiber", "elastomer", "recycl", "wear",
                  "brassylate", "adipate", "succinate", "grafted", "cellulose",
                  "cyclodextrin", "mutant", "enzyme", "hydrolase"]

# 明确无关的小分子/蛋白晶体结构等（标题特征）
JUNK_TERMS = ["ganciclovir", "guanfacine", "meclofenoxate", "carbaporphyrinoid",
              "lilap4o12", "dehydrogenase", "allergen", "pollen", "prime numbers"]

# 晶体/结晶语义词
CRYST_TERMS = ["crystal", "crystallin", "unit cell", "lattice",
               "spherulite", "morpholog", "structure"]


def is_junk_doi(doi: str) -> bool:
    """非正文条目：补充材料 / PDB / 审稿意见 / 决定信 / 多媒体附件。"""
    s = (doi or "").lower()
    return (bool(re.search(r"\.s\d+$", s))
            or "/pdb" in s
            or bool(re.search(r"/(v\d+/)?(review|decision)", s))
            or "/mm1" in s)


def classify(title: str, doi: str, polymer: str) -> str:
    t = (title or "").lower()
    if is_junk_doi(doi) or any(k in t for k in JUNK_TERMS):
        return "junk"
    if any(k in t for k in MED_TERMS):
        return "junk"
    if any(k in t for k in OFFTOPIC_TERMS):
        return "offtopic"
    # 防御：未知成员不至于 KeyError，退化为按缩写匹配
    syns = SYNONYMS.get(polymer, [polymer.lower()])
    ident = any(s in t for s in syns)
    cryst = any(k in t for k in CRYST_TERMS)
    return "ontopic" if (ident and cryst) else "offtopic"


def verify_doi(doi: str) -> dict | None:
    """CrossRef 核验题录（项目红线：任何 DOI 入库前必须机器核验）。"""
    if not doi:
        return None
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": "polyester-crystal-db/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            msg = json.loads(r.read().decode("utf-8"))["message"]
    except Exception:
        return None
    return {
        "title": (msg.get("title") or [""])[0],
        "year": (msg.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "journal": (msg.get("container-title") or [""])[0],
    }


def build_index(polymers: list[str] | None = None) -> dict:
    data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    out = {}
    for poly in (polymers or TARGETS):
        buckets = {"ontopic": [], "offtopic": [], "junk": []}
        for it in data.get(poly, []):
            cat = classify(it.get("title", ""), it.get("doi", ""), poly)
            buckets[cat].append({
                "doi": it.get("doi"), "title": it.get("title"),
                "year": it.get("year"), "journal": it.get("journal"),
            })
        out[poly] = buckets
    return out


def main(verify: bool = False) -> None:
    idx = build_index()
    for poly in TARGETS:
        b = idx[poly]
        total = sum(len(v) for v in b.values())
        print(f"{poly}: 总 {total:3d} | ontopic {len(b['ontopic']):2d} "
              f"| offtopic {len(b['offtopic']):2d} | junk {len(b['junk']):2d}")
        for it in b["ontopic"]:
            print(f"    - [{it['year']}] {(it['title'] or '')[:74]}")
            print(f"      {it['doi']}")

    if verify:
        print("\n=== CrossRef 核验 on-topic DOI ===")
        for poly in TARGETS:
            for it in idx[poly]["ontopic"]:
                v = verify_doi(it["doi"])
                mark = "OK " if v else "FAIL"
                print(f"  [{mark}] {poly} {it['doi']}"
                      + (f" -> {v['year']} {v['journal']}" if v else ""))
                it["verified"] = bool(v)
                if v:
                    it["cr_title"] = v["title"]
                    it["cr_year"] = v["year"]
                    it["cr_journal"] = v["journal"]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ 语料质量报告已写入 {OUT_PATH}")


if __name__ == "__main__":
    import argparse
    import urllib.parse  # noqa: F401  (供 verify_doi 使用)
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    main(ap.parse_args().verify)
