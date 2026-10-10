#!/usr/bin/env python3
"""抽取器：调用 LLM → 解析 JSON → 映射为 schema 列名

输出一个 dict，包含：
- "record"：已映射到 schema 列名的观测字段（含 null）
- "meta"：polymer_abbr / polymorph_label / evidence / confidence / unknown_fields / raw_text(截断)
- "parse_ok"：JSON 是否成功解析
- "raw"：LLM 原始返回（用于审计）
"""

from __future__ import annotations

import json
import re
from typing import Optional

from . import prompts
from .llm_client import BaseLLMClient, ChatResult

# 需要从 LLM 输出里剔除、不进 record 的元字段
_META_KEYS = {"polymer_abbr", "polymorph_label", "crystal_system", "space_group",
              "evidence", "confidence", "unknown_fields"}


def _extract_json_obj(text: str) -> Optional[dict]:
    """从 LLM 返回里尽量鲁棒地取出第一个 JSON 对象。"""
    if text is None:
        return None
    s = text.strip()
    # 去掉可能的 ```json ... ``` 包裹
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
        s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # 退化策略：找第一个 { 到最后一个 } 的子串
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(s[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None


def extract_from_document(client: BaseLLMClient, polymer_abbr: str, text: str,
                          polymorph_hint: str = "", temperature: float = 0.0) -> dict:
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": prompts.build_user_prompt(polymer_abbr, text, polymorph_hint)},
    ]
    result: ChatResult = client.complete(messages, temperature=temperature)
    raw_text = result.content or ""
    obj = _extract_json_obj(raw_text)

    if obj is None:
        return {
            "record": {},
            "meta": {
                "polymer_abbr": polymer_abbr,
                "polymorph_label": None, "evidence": None,
                "confidence": 0.0, "unknown_fields": list(prompts.FIELD_MAP.keys()),
            },
            "parse_ok": False,
            "raw": raw_text,
            "model": result.model,
        }

    # 映射到 schema 列名
    record: dict = {}
    for src_key, (col, is_int) in prompts.FIELD_MAP.items():
        if src_key in _META_KEYS:
            continue
        val = obj.get(src_key)
        if val is None:
            continue
        if is_int:
            try:
                record[col] = int(val)
            except (TypeError, ValueError):
                record[col] = None
        else:
            try:
                record[col] = float(val)
            except (TypeError, ValueError):
                # 非数值字段（如 chain_conformation / cryst_route）保留字符串
                record[col] = val if isinstance(val, str) else None

    meta = {
        "polymer_abbr": obj.get("polymer_abbr", polymer_abbr),
        "polymorph_label": obj.get("polymorph_label"),
        "crystal_system": obj.get("crystal_system"),
        "space_group": obj.get("space_group"),
        "evidence": (obj.get("evidence") or "")[:200],
        "confidence": obj.get("confidence"),
        "unknown_fields": obj.get("unknown_fields", []),
    }
    return {
        "record": record,
        "meta": meta,
        "parse_ok": True,
        "raw": raw_text,
        "model": result.model,
    }
