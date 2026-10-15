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

import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "corpus_quality.json"

# 全部 12 个 Tier1 成员（2026-10-15 起默认全量扫描；此前只跑 4 个先导成员）
TARGETS = ["PET", "PTT", "PBT", "PEN", "PBN", "PLA",
           "PGA", "PCL", "PBS", "PBSA", "PHB", "PHBV"]

# 成员同义词（标题里出现任一即认为在谈该聚合物）—— 覆盖全部 12 个 Tier1 成员
SYNONYMS = {
    "PET":  ["ethylene terephthalate", "(pet)", "poly(ethylene terephthalate)"],
    "PTT":  ["trimethylene terephthalate", "polytrimethylene", "(ptt)", "3gt"],
    "PBT":  ["butylene terephthalate", "tetramethylene terephthalate",
             "(pbt)", "polybutylene terephthalate"],
    # PBN：本体名常写作 butylene-2,6-naphthalate（归一化后 = butylene naphthalate）
    "PEN":  ["ethylene naphthalate", "naphthalate", "(pen)",
             "poly(ethylene naphthalate)"],
    "PBN":  ["butylene naphthalate", "naphthalate", "(pbn)",
             "poly(butylene naphthalate)"],
    "PLA":  ["lactic acid", "lactide", "polylactide", "(pla)"],
    "PGA":  ["glycolic acid", "polyglycolide", "(pga)", "poly(glycolic acid)"],
    "PCL":  ["caprolactone", "polycaprolactone", "(pcl)", "poly(caprolactone)"],
    # PBS/PBSA：succinate/adipate 是本体名，绝不可当共聚信号（2026-10-15 修）
    "PBS":  ["butylene succinate", "(pbs)", "poly(butylene succinate)",
             "poly(butylene succinate)"],
    "PBSA": ["succinate co adipate", "succinate-co-adipate", "(pbsa)",
             "butylene succinate co adipate", "succinate adipate"],
    "PHB":  ["hydroxybutyrate", "(phb)", "poly(3-hydroxybutyrate)",
             "polyhydroxybutyrate"],
    "PHBV": ["hydroxybutyrate co valerate", "hydroxybutyrate-co-valerate",
             "(phbv)", "hydroxybutyrate co hydroxyvalerate",
             "poly(3-hydroxybutyrate-co-3-hydroxyvalerate)"],
}

# 衍生体系（共聚/共混/复合/改性等）—— 非均聚物本体
# 注意：不可含 succinate / adipate / brassylate，它们是 PBS/PBSA 的本体名
DERIV_TERMS = ["copolyester", "copolymer", " blend", "blends", "composite",
               "nanocomposite", "inclusion", "stereocomplex", "cyclic dimer",
               "model compound", "graphene", "nanofib", "elastomer",
               "recycl", "wear", "graft", "cellulose", "cyclodextrin",
               "mutant", "enzyme", "hydrolase", "nanocrystal", "nanoparticle",
               "thin film", "modification", "aminolysis",
               # 生物医学/组织工程方向：这类论文不做晶胞测定（2026-10-15 补，
               # PCL/PLA/PHB 的检索结果里占比极高，不排除会淹没本体晶胞论文）
               "electrospin", "scaffold", "tissue engineering", "hydroxyapatite",
               "gelatin", "in vitro", "in vivo", "drug", "lipase",
               "biodegradation", "degradation", "hydrolysis", "antioxidant",
               "plant extract", "zein", "chitosan", "silicate"]

# 共聚连接符（归一化后形如 "succinate co adipate"）
CO_JOINERS = [" co ", "-co-", " co-", "-co "]

# 本体即为共聚酯的成员：对它们 "co" 连接符不是衍生信号（2026-10-15 修，
# 否则 PHBV/PBSA 的本体研究会被自己名字里的 -co- 全部误杀）
COPOLYMER_BY_NATURE = {"PBSA", "PHBV"}

# 允许「裸缩写」词边界匹配的成员：这些缩写在其他领域几乎不作为独立词出现。
# 反例（不可开）：PBS=PbS 硫化铅、PCL=PCl 氯化磷、PET=pet、PEN=pen 钢笔。
BARE_ABBREV = {"PHB": "phb", "PHBV": "phbv", "PBSA": "pbsa", "PBN": "pbn"}

# 缩写歧义/医学影像/光热治疗 —— 与高分子结晶无关
MED_TERMS = ["positron", "tomograph", "detector", "sipm", "scintillator",
             "photothermal", "nanoagent", "tumor", "therapy", "radiotracer",
             "imaging", "pixilated", "pixellated"]

# 明确无关的小分子/蛋白/无机晶体结构等（标题特征）
# 含第三类缩写歧义：pbs=PbS 硫化铅、pcl=PCl 氯化磷（2026-10-15 补）
JUNK_TERMS = ["ganciclovir", "guanfacine", "meclofenoxate", "carbaporphyrinoid",
              "lilap4o12", "dehydrogenase", "allergen", "pollen", "prime numbers",
              "pbs nanocrystal", "pbs island", "pbs-bas", "pcl3", "pcl5",
              "diaphorite", "hexachlorophosphate", "single crystal methods",
              "ilvaite", "crystallographic texture", "lattice-dynamical",
              "dibutyltin", "prime number"]

# 晶体/结晶语义词（宽口径：只要谈结晶就先留下）
CRYST_TERMS = ["crystal", "crystallin", "unit cell", "lattice",
               "spherulite", "morpholog", "structure", "conformation"]

# 晶胞级强信号：这类论文才真的可能给出 a/b/c/α/β/γ，应优先获取全文
CELL_TERMS = ["crystal structure", "unit cell", "lattice", "electron diffraction",
              "x-ray", "x ray", "polymorph", "helix", "crystal", "wide angle",
              "waxd", "diffraction"]


def is_junk_doi(doi: str) -> bool:
    """非正文条目：补充材料 / PDB / 审稿意见 / 决定信 / 多媒体附件。"""
    s = (doi or "").lower()
    return (bool(re.search(r"\.s\d+$", s))
            or "/pdb" in s
            or bool(re.search(r"/(v\d+/)?(review|decision)", s))
            or "/mm1" in s)


_TAG_RE = re.compile(r"<[^>]+>")


def normalize(title: str) -> str:
    """标题归一化：解 HTML 实体 -> 去标签 -> 连字符/不换行连字符转空格
    -> 去掉萘环位置标记（2,6- / 1,4- 等）-> 压缩空白。

    目的（2026-10-15 修）：
      * "poly(butylene-2,6-naphthalate)"  -> "poly(butylene naphthalate)"  方可匹配 PBN
      * "poly(butylene succinate)-<i>co</i>-adipate" -> "... succinate co adipate"
      * "&amp;epsilon;-caprolactone"     -> "ε-caprolactone"
    """
    t = html.unescape(title or "")
    t = _TAG_RE.sub(" ", t)
    t = t.replace("\u2011", "-").replace("\u2010", "-").replace("\u2013", "-")
    t = re.sub(r"\b\d,\d\b", " ", t)      # 2,6-naphthalate -> naphthalate
    t = t.replace("-", " ")
    t = t.lower()
    return re.sub(r"\s+", " ", t).strip()


def _is_derivative(t: str, polymer: str) -> bool:
    """是否衍生体系（共聚/共混/复合…）而非均聚物本体。

    PBSA 是特例：它本身就是共聚酯（succinate-co-adipate），
    所以 "co" 连接符对它不是衍生信号；但三元共混/纳米复合仍是。
    """
    if any(k in t for k in DERIV_TERMS):
        return True
    if polymer in COPOLYMER_BY_NATURE:
        return False
    return any(j in t for j in CO_JOINERS)


def classify(title: str, doi: str, polymer: str) -> str:
    t = normalize(title)
    if is_junk_doi(doi) or any(k in t for k in JUNK_TERMS):
        return "junk"
    if any(k in t for k in MED_TERMS):
        return "junk"
    if _is_derivative(t, polymer):
        return "offtopic"
    # 防御：未知成员不至于 KeyError，退化为按缩写匹配
    syns = SYNONYMS.get(polymer, [polymer.lower()])
    ident = any(s in t for s in syns)
    if not ident and polymer in BARE_ABBREV:
        # 形如 "unit cell of biopolymer PHB"（无括号），子串匹配不到，用词边界正则
        ident = bool(re.search(r"\b" + BARE_ABBREV[polymer] + r"\b", t))
    cryst = any(k in t for k in CRYST_TERMS)
    return "ontopic" if (ident and cryst) else "offtopic"


def has_cell_signal(title: str) -> bool:
    """标题是否含晶胞级强信号（决定该文是否值得优先获取全文）。"""
    t = normalize(title)
    return any(k in t for k in CELL_TERMS)


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
                "cell_signal": has_cell_signal(it.get("title", ""))
                if cat == "ontopic" else None,
            })
        out[poly] = buckets
    return out


def main(verify: bool = False, polymers: list[str] | None = None) -> None:
    targets = polymers or TARGETS
    idx = build_index(polymers)
    for poly in targets:
        b = idx[poly]
        total = sum(len(v) for v in b.values())
        print(f"{poly}: 总 {total:3d} | ontopic {len(b['ontopic']):2d} "
              f"| offtopic {len(b['offtopic']):2d} | junk {len(b['junk']):2d}")
        for it in b["ontopic"]:
            print(f"    - [{it['year']}] {(it['title'] or '')[:74]}")
            print(f"      {it['doi']}")

    if verify:
        print("\n=== CrossRef 核验 on-topic DOI ===")
        for poly in targets:
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
    ap.add_argument("--verify", action="store_true", help="CrossRef 核验 on-topic DOI 题录")
    ap.add_argument("--polymers", default=None,
                    help="逗号分隔的成员列表，默认全部 12 个 Tier1 成员")
    a = ap.parse_args()
    main(a.verify, [p.strip() for p in a.polymers.split(",")] if a.polymers else None)
