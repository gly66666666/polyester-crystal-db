#!/usr/bin/env python3
"""生成「全文获取优先级清单」——把 on-topic 语料转成可执行的人工下载任务表

为什么需要它：
  晶胞参数**几乎只出现在全文表格里**，只抽摘要基本抽不到（2026-10-10 实测结论）。
  而目标文献绝大多数为订阅制：Unpaywall 实测 OA 比例 4–18%，但含直链可自动下载
  PDF 的仅约 2%。所以「拿到 PDF」这一步必须由人完成——本脚本就是给这一步用的工单。

排序逻辑（先拿性价比最高的）：
  1. 晶胞级强信号优先（crystal structure / unit cell / x-ray / electron diffraction）
  2. 同年中，标题越像"结构测定"越靠前（crystal structure > polymorphism > morphology）
  3. 再按年份倒序（新的更易拿到电子版）

并按出版商分组给出获取途径建议（南大图书馆订阅情况见 PUBLISHER_HINT）。

用法：
  python src/annotation/make_fetch_list.py
  python src/annotation/make_fetch_list.py --top 40
产物：docs/fulltext_fetch_list.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
Q_PATH = PROJECT_ROOT / "data" / "processed" / "corpus_quality.json"
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
OUT_PATH = PROJECT_ROOT / "docs" / "fulltext_fetch_list.md"

# 出版商识别（按 DOI 前缀）—— 用于给出获取途径建议
PUBLISHER_PREFIX = [
    ("10.1002", "Wiley"),
    ("10.1016", "Elsevier"),
    ("10.1021", "ACS"),
    ("10.1039", "RSC"),
    ("10.1007", "Springer"),
    ("10.1080", "Taylor & Francis"),
    ("10.1088", "IOP"),
    ("10.1063", "AIP"),
    ("10.1149", "ECS"),
    ("10.1007", "Springer"),
]

# 南大图书馆订阅情况（2026-10 口径，需人工复核；以实际电子资源导航为准）
PUBLISHER_HINT = {
    "Wiley":            "图书馆已订 → 校内 IP 直接下",
    "Elsevier":         "图书馆已订（ScienceDirect）→ 校内 IP 直接下",
    "ACS":              "图书馆已订 → 校内 IP 直接下",
    "RSC":              "图书馆已订 → 优先试",
    "Springer":         "多数已订（含 Polymer Bulletin 等）→ 试校内 IP",
    "Taylor & Francis": "部分已订 → 试校内 IP，不行走馆际互借",
    "IOP":              "部分已订 → 试校内 IP，不行走馆际互借",
    "AIP":              "部分已订 → 试校内 IP，不行走馆际互借",
    "ECS":              "未确认 → 走馆际互借",
    "其他":             "未确认 → 走馆际互借 / 作者主页 / ResearchGate 索抽印本",
}

# 标题语义强度（越大越像真正的结构测定论文）
STRONG = [("crystal structure", 5), ("unit cell", 5), ("electron diffraction", 5),
          ("x-ray", 4), ("polymorph", 4), ("helix", 3), ("conformation", 2),
          ("crystal", 2), ("lattice", 3)]
WEAK = [("morpholog", -1), ("kinetics", -2), ("spherulite", -1),
        ("scimeetings", -3), ("interface", -2), ("model", -2)]


def publisher_of(doi: str) -> str:
    for pre, pub in PUBLISHER_PREFIX:
        if (doi or "").lower().startswith(pre):
            return pub
    return "其他"


def strength(title: str) -> int:
    t = (title or "").lower()
    s = 0
    for k, w in STRONG:
        if k in t:
            s += w
    for k, w in WEAK:
        if k in t:
            s += w
    return s


def main(top: int | None = None) -> None:
    q = json.loads(Q_PATH.read_text(encoding="utf-8"))
    # corpus_quality.json 只带 doi/title/year/journal/cell_signal；
    # pdf_url / oa_status 在主语料里，按 DOI 关联补上（否则「可自动下载」永远是 0）
    extra = {}
    for _p, _items in json.loads(SEARCH_PATH.read_text(encoding="utf-8")).items():
        for _i in _items:
            extra[(_i.get("doi") or "").lower()] = _i

    rows = []
    for poly, buckets in q.items():
        for it in buckets.get("ontopic", []):
            rows.append({
                "polymer": poly,
                "doi": it.get("doi") or "",
                "title": (it.get("title") or "").strip(),
                "year": it.get("year"),
                "journal": it.get("journal") or "",
                "cell": bool(it.get("cell_signal")),
                "publisher": publisher_of(it.get("doi") or ""),
                "score": strength(it.get("title") or ""),
                "pdf_url": (extra.get((it.get("doi") or "").lower(), {})
                            .get("pdf_url") or ""),
                "oa": (extra.get((it.get("doi") or "").lower(), {})
                       .get("oa_status") or "closed"),
            })
    # 有 OA 直链的排最前（可脚本批量下，零人工）；其余按晶胞级信号与语义强度
    rows.sort(key=lambda r: (-int(bool(r["pdf_url"])), -int(r["cell"]),
                             -r["score"], -(r["year"] or 0)))
    if top:
        rows = rows[:top]

    by_pub: dict[str, int] = {}
    for r in rows:
        by_pub[r["publisher"]] = by_pub.get(r["publisher"], 0) + 1

    n_cell = sum(1 for r in rows if r["cell"])
    lines = [
        "# 全文获取优先级清单",
        "",
        f"自动生成：`src/annotation/make_fetch_list.py`（源 `corpus_quality.json`，"
        f"共 {len(rows)} 条 on-topic，其中晶胞级强信号 {n_cell} 条）。",
        "",
        "> **为什么要有这份清单**：晶胞参数几乎只在全文表格里，只抽摘要抽不到。"
        "经 OpenAlex 实测，325 条 on-topic 中 **81 条（25%）有 OA 直链**可脚本批量下载，"
        "其余仍靠图书馆订阅 / 馆际互借（2026-10-15 更新；"
        "此前 2026-10-10 用 Unpaywall 估的「约 2%」严重低估了 green-OA 仓储稿，已作废）。",
        "> PDF 放入 `data/literature/`，命名 `<sanitized_doi>.pdf`（已 gitignore，不入库不分发）。",
        "",
        "## 一、按出版商汇总与获取途径",
        "",
        "| 出版商 | 条数 | 建议获取途径 |",
        "|---|---:|---|",
    ]
    for pub, n in sorted(by_pub.items(), key=lambda x: -x[1]):
        lines.append(f"| {pub} | {n} | {PUBLISHER_HINT.get(pub, PUBLISHER_HINT['其他'])} |")

    n_auto = sum(1 for r in rows if r["pdf_url"])
    lines += [
        "",
        f"## 二、逐篇清单（按性价比排序，共 {len(rows)} 条）",
        "",
        f"先处理前 **{n_auto}** 条「可自动下载」的（有 OA 直链，脚本批量下即可）；",
        "剩下的再走图书馆 / 馆际互借。",
        "",
        "| # | 自动 | 优先 | 成员 | 标题 | 期刊 / 年 | DOI | 途径 | 已下 |",
        "|---:|:---:|:---:|:---:|---|---|---|---|:---:|",
    ]
    for i, r in enumerate(rows, 1):
        auto = "⚡" if r["pdf_url"] else ""
        prio = "★★" if r["cell"] else "★"
        title = re.sub(r"\s+", " ", r["title"])[:66]
        journal = f"{r['journal']} / {r['year']}" if r["journal"] else str(r["year"])
        lines.append(
            f"| {i} | {auto} | {prio} | {r['polymer']} | {title} | {journal} "
            f"| `{r['doi']}` | {r['publisher']} | ☐ |"
        )

    lines += [
        "",
        "## 三、操作说明",
        "",
        "1. **先跑自动下载**（有 ⚡ 标记的）："
        "`python src/extraction/fetch_pdf.py --on-topic-only`；"
        "注意直链可能失效或需要校园网，需实测确认。",
        "2. 自动下载失败的，按「途径」列在校内 IP / 图书馆电子资源导航里人工下载；",
        "3. PDF 放到 `data/literature/`，命名为 `<sanitized_doi>.pdf`"
        "（与 `corpus.pdf_path_for` 一致，否则流水线拾取不到）；",
        "4. 下载后在「已下」列打勾，便于统计完成度；",
        "5. **不要**整包抓取第三方数据库，也不要把 PDF 提交进仓库或对外分发。",
        "",
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ 已写入 {OUT_PATH}")
    print(f"  on-topic {len(rows)} 条（晶胞级 {n_cell} 条）")
    for pub, n in sorted(by_pub.items(), key=lambda x: -x[1]):
        print(f"    {pub:18s} {n}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=None)
    main(ap.parse_args().top)
