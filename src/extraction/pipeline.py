#!/usr/bin/env python3
"""抽取流水线编排（执行计划 §4.2）

用法（无需密钥即可演示）：
  python -m src.extraction.pipeline --backend mock --limit 10 --dry-run
  python -m src.extraction.pipeline --backend mock --limit 10        # 落库（mock 数据，测试用）
  python -m src.extraction.pipeline --backend tokenplan --polymers PET,PLA --limit 50
  python -m src.extraction.pipeline --backend tokenplan --resume     # 断点续跑

流程：
  corpus(build_jobs) → 逐篇 extract_from_document → normalize → [dry-run? 写JSON : store.persist_record]
  带 checkpoint（已处理的 doi 落盘 data/processed/extraction_checkpoint.json），可断点续跑、幂等。

幂等性：store 已按 (doi, polymer, polymorph, t_c, a,b,c) 去重；checkpoint 避免重复调 API 花钱。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from . import store
from .corpus import build_jobs
from .extractor import extract_from_document
from .llm_client import get_client
from .normalizer import normalize

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHECKPOINT = PROCESSED_DIR / "extraction_checkpoint.json"
OUT_DEFAULT = PROCESSED_DIR / "extraction_output.json"


def _load_checkpoint() -> set:
    if CHECKPOINT.exists():
        return set(json.loads(CHECKPOINT.read_text(encoding="utf-8")).get("done", []))
    return set()


def _save_checkpoint(done: set) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps({"done": sorted(done)}, ensure_ascii=False),
                          encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="聚酯结晶数据抽取流水线")
    ap.add_argument("--backend", default="mock", choices=["mock", "tokenplan", "local"])
    ap.add_argument("--model", default=None, help="TokenPlan 模型 ID（默认 deepseek-v4-flash-0731）")
    ap.add_argument("--polymers", default=None, help="逗号分隔成员缩写，如 PET,PLA")
    ap.add_argument("--limit", type=int, default=None, help="最多处理 N 篇（快速验证用）")
    ap.add_argument("--dry-run", action="store_true", help="只写抽取 JSON，不落库")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="dry-run 输出 JSON 路径")
    ap.add_argument("--resume", dest="resume", action="store_true", default=True)
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    ap.add_argument("--require-text", action="store_true", help="跳过无文本（无PDF且无摘要）的条目")
    ap.add_argument("--on-topic-only", action="store_true",
                    help="只处理 on-topic 条目（过滤缩写歧义/小分子晶体结构/补充材料/PDB/审稿文件/共聚共混），"
                         "强烈建议开启以免浪费 API 额度")
    args = ap.parse_args()

    polymers = [p.strip().upper() for p in args.polymers.split(",")] if args.polymers else None
    jobs = build_jobs(polymers=polymers, limit=args.limit, require_text=args.require_text,
                      on_topic_only=args.on_topic_only)
    if not jobs:
        print("✗ 没有可处理的任务，请检查 --polymers / 文献检索结果。")
        sys.exit(1)

    done = _load_checkpoint() if args.resume else set()
    pending = [j for j in jobs if j["doi"] not in done] if args.resume else jobs
    print(f"任务总数 {len(jobs)}，待处理 {len(pending)}（resume={args.resume}）。")

    client = get_client(args.backend, model=args.model or "")

    conn = None if args.dry_run else store.get_connection()
    if conn is None and not args.dry_run and not store.DB_PATH.exists():
        print("✗ 主库不存在，请先运行 src/database/init_db.py", file=sys.stderr)
        sys.exit(1)

    summary = {"inserted": 0, "skipped": 0, "no_doi": 0, "parse_fail": 0,
               "pending_review": 0, "auto": 0}
    dry_results: list[dict] = []
    processed = 0

    try:
        for job in pending:
            extracted = extract_from_document(client, job["polymer_abbr"], job["text"])
            normalized = normalize(
                extracted, doi=job["doi"], ref_year=job["year"],
                ref_source=job["journal"], extraction_model=client.model,
            )
            normalized["lit"]["title"] = job["title"]
            normalized["lit"]["authors"] = job["authors"]
            normalized["lit"]["abstract"] = job["abstract"]   # 仅 CrossRef 元数据，非全文

            if not normalized["parse_ok"]:
                summary["parse_fail"] += 1
            if normalized["review_status"] == "pending_review":
                summary["pending_review"] += 1
            else:
                summary["auto"] += 1

            if args.dry_run:
                dry_results.append({
                    "doi": job["doi"], "polymer_abbr": job["polymer_abbr"],
                    "meta": normalized["meta"], "obs": normalized["flat"],
                    "poly": normalized["poly"],
                    "issues": normalized["issues"], "review_status": normalized["review_status"],
                })
            else:
                status = store.persist_record(conn, normalized)
                summary[status] = summary.get(status, 0) + 1
                conn.commit()

            done.add(job["doi"])
            processed += 1
            if processed % 10 == 0:
                _save_checkpoint(done)
                print(f"  …已处理 {processed}/{len(pending)}")
    finally:
        _save_checkpoint(done)
        if conn:
            conn.close()

    if args.dry_run:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(dry_results, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print(f"✓ dry-run 完成，抽取结果写入 {args.out}（{len(dry_results)} 条，未落库）")
    else:
        print(f"✓ 落库完成。")
    print(f"  处理 {processed} 篇 | 插入 {summary['inserted']} | 跳过(重复) {summary['skipped']} "
          f"| 无DOI {summary['no_doi']} | 解析失败 {summary['parse_fail']}")
    print(f"  置信≥0.7(auto) {summary['auto']} | 待人工复核(pending_review) {summary['pending_review']}")


if __name__ == "__main__":
    main()
