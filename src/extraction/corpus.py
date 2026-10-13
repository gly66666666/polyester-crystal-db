#!/usr/bin/env python3
"""语料装配：把检索结果（search_results.json）转成抽取任务

每个 job：
{
  "doi", "title", "authors", "journal", "year",
  "polymer_abbr", "text"   # text = PDF 全文（若已下载）或 abstract 兜底
}

- 优先用本地已下载的 PDF（data/literature/<sanitized_doi>.pdf）提取文本；
- 无 PDF 时用 CrossRef 摘要兜底（足以抽取部分热/动力学量，完整晶胞仍需 PDF）。
- 按 polymer_abbr 分组（search_results.json 顶层键即成员缩写）。
"""

from __future__ import annotations

from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEARCH_PATH = PROJECT_ROOT / "data" / "literature" / "search_results.json"
LIT_DIR = PROJECT_ROOT / "data" / "literature"


def _sanitize(doi: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", doi or "")


def pdf_path_for(doi: str) -> Path:
    """该 DOI 对应的本地 PDF 路径（corpus 与 fetch_pdf 共用，保证命名一致）。"""
    return LIT_DIR / f"{_sanitize(doi)}.pdf"


def _pdf_text(doi: str) -> Optional[str]:
    """若本地有该 DOI 的 PDF，用 pdfplumber 提取文本（可选依赖，缺失则跳过）。"""
    pdf = pdf_path_for(doi)
    if not pdf.exists():
        return None
    try:
        import pdfplumber  # 任务3 已装
    except ImportError:
        return None
    try:
        with pdfplumber.open(pdf) as pdfdoc:
            return "\n".join((pg.extract_text() or "") for pg in pdfdoc.pages)
    except Exception:
        return None


def _classify_fn():
    """延迟导入语料质量分类器（跨目录：src/annotation/corpus_quality.py）。

    背景：search_results.json 含大量无关条目（缩写歧义、小分子晶体结构、
    补充材料 .s001、PDB、审稿文件），直接跑会白白消耗 API 额度。
    """
    import sys
    ann = PROJECT_ROOT / "src" / "annotation"
    s = str(ann)
    if s not in sys.path:
        sys.path.insert(0, s)
    from corpus_quality import classify  # noqa: E402
    return classify


def build_jobs(polymers: list[str] | None = None, limit: int | None = None,
               require_text: bool = False, on_topic_only: bool = False) -> list[dict]:
    """装配抽取任务。

    on_topic_only=True 时只保留确为该均聚物晶体/结晶研究的条目
    （过滤缩写歧义、小分子晶体结构、补充材料、PDB、审稿文件、共聚/共混等）。
    """
    if not SEARCH_PATH.exists():
        raise FileNotFoundError("未找到 search_results.json，请先完成任务8文献检索。")
    data = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))

    clf = _classify_fn() if on_topic_only else None
    jobs: list[dict] = []
    for poly, items in data.items():
        if polymers and poly not in polymers:
            continue
        for it in items:
            if clf and clf(it.get("title", ""), it.get("doi", ""), poly) != "ontopic":
                continue
            text = _pdf_text(it.get("doi")) or it.get("abstract") or ""
            if require_text and not text.strip():
                continue
            jobs.append({
                "doi": it.get("doi"),
                "title": it.get("title"),
                "authors": it.get("authors"),
                "journal": it.get("journal"),
                "year": it.get("year"),
                "polymer_abbr": poly,
                "abstract": it.get("abstract"),   # CrossRef 元数据（非全文），仅作 provenance
                "text": text,                      # 抽取用文本（PDF 全文或 abstract 兜底）
            })
            if limit and len(jobs) >= limit:
                return jobs
    return jobs
