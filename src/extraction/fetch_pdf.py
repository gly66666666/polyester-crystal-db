#!/usr/bin/env python3
"""开放获取（OA）全文 PDF 获取

为什么需要：晶胞参数几乎不会出现在摘要里，只抽取摘要会导致抽取结果大量为空。
本模块负责把**合法开放获取**的全文 PDF 拉到本地，供 corpus/pipeline 使用全文而非摘要。

⚠️ 合规前提（务必遵守）：
- 只获取 Unpaywall 判定为**合法开放获取**的版本，**绝不绕过付费墙**；
- 下载内容仅存本地 data/literature/（已 gitignore，不入库、不分发）；
- 只存数值性事实与出处定位进库，PDF 本身不进版本库、不外传。

实测（2026-10-10，40 篇 Gold Set 候选抽样）：OA 比例约 18%，
其中可直接下载 PDF 的约 18%；其余需通过学校图书馆订阅（南大已订阅 Wiley/Elsevier/ACS）
或馆际互借获取。因此本模块是"能拿的先自动拿"，不能替代机构访问。

流程：
  1) Unpaywall API（免费，仅需邮箱做 polite pool）按 DOI 查是否有合法 OA 版本；
  2) 优先取 url_for_pdf，其次 OA 的 landing url；
  3) 下载并以 PDF 魔数 %PDF 校验；若落到 HTML 落地页（DOI 解析页/付费页），
     判定为"仅有链接，需人工"，不伪装成 PDF；
  4) 结果写入 data/literature/oa_availability.json，供人工按图索骥。

用法：
  python -m src.extraction.fetch_pdf --from-gold --check-only   # 只查 Gold Set 候选的 OA 情况
  python -m src.extraction.fetch_pdf --from-gold --download     # 顺带下载
  python -m src.extraction.fetch_pdf --polymers PLA --top 15 --download
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .corpus import LIT_DIR, pdf_path_for

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
AVAIL_PATH = LIT_DIR / "oa_availability.json"
GOLD_PATH = PROJECT_ROOT / "data" / "gold_set" / "gold_set.json"

# Unpaywall polite pool：请换成你自己的邮箱
EMAIL = "251840135@smail.nju.edu.cn"
UNPAYWALL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UA = "poly-crystal-db/0.1 (OA fulltext fetch; mailto:{})".format(EMAIL)


def unpaywall(doi: str, retries: int = 2) -> Optional[dict]:
    """查询 Unpaywall；失败返回 None（不计为封闭，避免误判）。

    实测有相当比例请求会超时/限流，故做有限次退避重试。
    """
    url = UNPAYWALL.format(doi=urllib.parse.quote(doi), email=urllib.parse.quote(EMAIL))
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None
    return None


def _pdf_url(rec: dict) -> Optional[str]:
    """优先取可直接下 PDF 的链接。"""
    for loc in ([rec.get("best_oa_location")] if rec.get("best_oa_location") else []) + \
               (rec.get("oa_locations") or []):
        u = loc.get("url_for_pdf")
        if u:
            return u
    best = rec.get("best_oa_location") or {}
    return best.get("url") if rec.get("is_oa") else None


def download_pdf(url: str, dest: Path) -> tuple[bool, str]:
    """下载并用 PDF 魔数校验；落到 HTML 页面则判定失败。"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "application/pdf,*/*",
        })
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except Exception as e:
        return False, f"下载失败：{e}"
    if data[:4] == b"%PDF":
        dest.write_bytes(data)
        return True, f"已保存 {dest.name}（{len(data)//1024} KB）"
    head = data[:200].decode("utf-8", "ignore")
    return False, "返回的不是 PDF（疑似 HTML 落地页，需人工获取）" + (
        " | 片段：" + head[:80].replace("\n", " ") if head else "")


def load_targets(args) -> list[dict]:
    """待处理的目标：(polymer_abbr, doi, title)。"""
    out: list[dict] = []
    if args.from_gold:
        gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
        for rec in gold["records"]:
            sug = rec.get("suggested")
            if sug and sug.get("doi"):
                out.append({"polymer_abbr": rec["polymer_abbr"],
                            "doi": sug["doi"], "title": sug.get("title")})
        return out
    # 否则按检索结果排序取前 N（复用 src/annotation/shortlist.py 的排序保证相关度）
    return ranked_dois(args.polymers, args.top)


def ranked_dois(polymers: str, top: int) -> list[dict]:
    """动态加载 src/annotation/shortlist.py 的排序器（跨子目录，避免包内循环依赖）。"""
    import importlib.util
    spec_path = PROJECT_ROOT / "src" / "annotation" / "shortlist.py"
    spec = importlib.util.spec_from_file_location("_shortlist", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    polys = [p.strip().upper() for p in (polymers or "").split(",") if p.strip()]
    ranked = mod.rank(polys)
    out: list[dict] = []
    for poly in polys:
        for c in ranked.get(poly, [])[:top]:
            out.append({"polymer_abbr": poly, "doi": c["doi"], "title": c.get("title")})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="开放获取全文 PDF 获取（不绕付费墙）")
    ap.add_argument("--from-gold", action="store_true", help="只处理 Gold Set 的候选 DOI（默认推荐）")
    ap.add_argument("--polymers", default="PET,PTT,PBT,PLA", help="逗号分隔成员")
    ap.add_argument("--top", type=int, default=10, help="每成员取前 N 篇（按相关度排序）")
    ap.add_argument("--check-only", action="store_true", help="只查可用性，不下载")
    ap.add_argument("--download", action="store_true", help="下载可获取的 OA PDF")
    ap.add_argument("--sleep", type=float, default=0.35, help="Unpaywall 请求间隔")
    ap.add_argument("--report", action="store_true",
                    help="生成 docs/fulltext_acquisition.md 人工获取清单")
    args = ap.parse_args()

    if not args.download and not args.check_only:
        args.check_only = True  # 默认只查不下载，避免误以为在批量抓全文

    try:
        targets = load_targets(args)
    except Exception as e:
        print(f"✗ 取目标失败：{e}")
        return
    if not targets:
        print("✗ 没有可处理的目标 DOI。")
        return

    print(f"待查 {len(targets)} 个 DOI（{'Gold Set 候选' if args.from_gold else '检索结果前 N'}）…\n")
    LIT_DIR.mkdir(parents=True, exist_ok=True)
    avail = json.loads(AVAIL_PATH.read_text(encoding="utf-8")) if AVAIL_PATH.exists() else {}

    n_oa = n_pdf = n_manual = n_closed = n_fail = 0
    for t in targets:
        doi = t["doi"]
        rec = unpaywall(doi)
        time.sleep(args.sleep)
        if rec is None:
            n_fail += 1
            avail[doi] = {"polymer_abbr": t["polymer_abbr"], "title": t.get("title"),
                          "status": "query_failed"}
            continue

        is_oa = bool(rec.get("is_oa"))
        url = _pdf_url(rec)
        entry = {
            "polymer_abbr": t["polymer_abbr"], "title": t.get("title"),
            "journal": rec.get("journal_name"), "year": rec.get("year"),
            "is_oa": is_oa, "host_type": (rec.get("best_oa_location") or {}).get("host_type"),
            "pdf_url": url,
        }
        if not is_oa or not url:
            entry["status"] = "closed"
            n_closed += 1
            print(f"  封闭  {t['polymer_abbr']:4s} {doi}")
        elif args.download:
            dest = pdf_path_for(doi)
            ok, msg = download_pdf(url, dest)
            entry["status"] = "downloaded" if ok else "link_only"
            entry["pdf_path"] = str(dest.name) if ok else None
            if ok:
                n_pdf += 1
                print(f"  ✓PDF   {t['polymer_abbr']:4s} {doi}  {msg}")
            else:
                n_manual += 1
                print(f"  !链接  {t['polymer_abbr']:4s} {doi}  {msg}")
        else:
            entry["status"] = "oa_available"
            n_oa += 1
            print(f"  OA     {t['polymer_abbr']:4s} {doi}  [{entry['host_type']}] {url}")
        avail[doi] = entry

    AVAIL_PATH.write_text(json.dumps(avail, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n汇总：封闭 {n_closed} | OA 可下 {n_oa} | 已下载 {n_pdf} | "
          f"仅链接需人工 {n_manual} | 查询失败 {n_fail}")
    print(f"✓ 可用性明细：{AVAIL_PATH}")
    if n_closed:
        print("\n提示：封闭获取的论文需走学校图书馆订阅（南大已订阅 Wiley/Elsevier/ACS）"
              "或馆际互借；下载后的 PDF 放入 data/literature/ 即可被抽取流水线自动优先使用全文。")

    if args.report:
        write_report(avail)


def write_report(avail: dict) -> None:
    """生成人工获取清单：哪些必须走图书馆、哪些是 OA 但只有落地页链接。"""
    docs = PROJECT_ROOT / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    out = docs / "fulltext_acquisition.md"
    by_poly: dict[str, list] = {}
    for doi, e in avail.items():
        by_poly.setdefault(e.get("polymer_abbr") or "?", []).append((doi, e))

    lines = [
        "# 全文获取清单（人工下载用）",
        "",
        "> 生成器：`python -m src.extraction.fetch_pdf --from-gold --check-only --report`",
        ">",
        "> **结论（2026-10-10 实测）**：本课题目标文献绝大多数为订阅制，"
        "开放获取(OA)比例约 4–18%，其中**含直链可自动下载 PDF 的仅约 2%**。",
        "> 因此自动抓取无法支撑规模化（P2 需 ≥150 条观测），"
        "**必须走学校图书馆订阅 / 馆际互借**，或由你手动下载 PDF 放入 `data/literature/`。",
        "> 放入后抽取流水线会自动优先使用全文（晶胞参数几乎只在全文表里，摘要里没有）。",
        "",
    ]
    for poly in sorted(by_poly):
        lines += [f"## {poly}", "",
                  "| DOI | 标题 | 状态 | 获取方式 |", "|---|---|---|---|"]
        for doi, e in sorted(by_poly[poly], key=lambda x: (x[1].get("status") or "", x[0])):
            st = e.get("status")
            if st == "downloaded":
                how = f"已下载 `{e.get('pdf_path')}`"
            elif st == "oa_available" or st == "link_only":
                how = f"OA 但多为落地页，需浏览器打开 → {e.get('pdf_url')}"
            elif st == "query_failed":
                how = "查询失败，需重跑"
            else:
                how = "**封闭**：走图书馆订阅 / 馆际互借"
            lines.append(f"| `{doi}` | {(e.get('title') or '')[:58]} | {st} | {how} |")
        lines.append("")
    lines += [
        "## 下载后怎么用",
        "",
        "1. 把 PDF 命名为 `<DOI 中的 / 替换为 _>.pdf`，放入 `data/literature/`；",
        "   （脚本 `corpus.pdf_path_for()` 用的就是这个命名规则，`fetch_pdf --download` 已自动处理）",
        "2. 直接跑抽取流水线即可自动优先使用全文：",
        "   `python -m src.extraction.pipeline --backend tokenplan --polymers PET --limit 20`",
        "3. PDF 已被 `.gitignore` 排除，**不会**进入 GitHub 仓库（版权合规）。",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ 人工获取清单已生成：{out}")


if __name__ == "__main__":
    main()
