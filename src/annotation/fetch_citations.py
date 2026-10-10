#!/usr/bin/env python3
"""批量抓取已核验 DOI 的完整题录，输出 BibTeX 与 human-readable 清单

用途：论文写作阶段生成参考文献。所有 DOI 均由 CrossRef 实时拉取，
      **题录（作者/标题/期刊/卷/页/年）一律以 CrossRef 返回为准**，绝不手抄。

用法：
    python src/annotation/fetch_citations.py 10.xxxx 10.yyyy ...
    python src/annotation/fetch_citations.py --preset      # 用下文的 PRESET 清单
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

MAILTO = "251840135@nju.edu.cn"

# 论文引用预设（全部经 CrossRef 核验存在；题录仍以实时拉取为准）
PRESET = [
    "10.1098/rspa.1954.0273",          # PET 晶胞经典
    "10.1021/ma001630o",               # PLLA α 晶型
    "10.1002/pol.1975.180131109",      # PBT (PTMT) 晶胞
    "10.6028/jres.066a.003",           # Hoffman-Weeks 平衡熔点
    "10.6028/jres.064a.007",           # Lauritzen-Hoffman 折叠链
    "10.1107/s0021889809016690",       # COD
    "10.1093/nar/gkr900",              # COD (NAR)
    "10.1107/s2052520616003954",       # CSD
    "10.1063/1.4812323",               # Materials Project
    "10.1109/eidwt.2011.13",           # PoLyInfo
    "10.1080/27660400.2024.2354651",   # PoLyInfo (II)
    "10.1021/acs.jcim.6b00207",        # ChemDataExtractor
    "10.1021/acs.jcim.1c01031",        # Polymer informatics benchmark
    "10.1039/d4dd00362d",              # LLM KG from tables
    "10.1039/d4dd00337c",              # LLM porous organic cages
    "10.1039/d4sc00924j",              # Fine-tuning LLM chemical text mining
    "10.1016/j.commatsci.2025.113855",  # LLM-driven materials DB
]


def fetch(doi: str) -> dict:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url, headers={"User-Agent": f"polyester-crystal-db/1.0 (mailto:{MAILTO})"}
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        it = json.load(r)["message"]
    authors = []
    for a in it.get("author") or []:
        fam = a.get("family", "")
        giv = a.get("given", "")
        authors.append(f"{fam}, {giv}".strip(", ") if fam else giv)
    return {
        "doi": it.get("DOI"),
        "title": (it.get("title") or [""])[0],
        "journal": (it.get("container-title") or [""])[0],
        "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "volume": it.get("volume"),
        "issue": it.get("issue"),
        "page": it.get("page"),
        "authors": authors,
    }


def main() -> None:
    args = sys.argv[1:]
    preset = "--preset" in args
    args = [a for a in args if not a.startswith("--")]
    dois = PRESET if preset else args
    if not dois:
        print(__doc__)
        return

    recs = []
    for d in dois:
        try:
            r = fetch(d)
            recs.append(r)
        except Exception as e:  # noqa: BLE001
            recs.append({"doi": d, "error": str(e)})
        time.sleep(0.3)

    print(json.dumps(recs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
