#!/usr/bin/env python3
"""LLM 客户端抽象层（抽取流水线依赖）

后端（backend）：
- "tokenplan"：书生·墨点计划 OpenAI 兼容接口（详见 tokenplan-guide.tex）
    base_url = https://discovery-api.intern-ai.org.cn/v1
    默认模型 = deepseek-v4-flash-0731（1M 上下文 / 性价比首选）
    鉴权：Authorization: Bearer $TOKENPLAN_API_KEY
- "mock"：不联网，返回确定性占位 JSON，用于 dry-run / 框架自测（无密钥可跑）
- "local"：预留，开发机 CPU 档本地跑开源抽取模型（后续接入，本期不实现）

设计要点（对齐 tokenplan-guide 错误处理章节）：
- 429 必须区分：rate_limit_exceeded → 指数退避重试；quota_exceeded → 不重试，抛错。
- 401/403/404/参数错误/额度不足 → 一律不重试。
- 500/502/503/504 → 有限次指数退避重试。
- 非流式；流式一旦吐字不重试（本项目用非流式即可）。

仅依赖标准库（urllib），无需 requests / openai。
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

TOKENPLAN_BASE_URL = "https://discovery-api.intern-ai.org.cn/v1"
TOKENPLAN_DEFAULT_MODEL = "deepseek-v4-flash-0731"


class LLMError(RuntimeError):
    """LLM 调用相关错误；带是否需要退避的标记。"""


@dataclass
class ChatResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict = field(default_factory=dict)


class BaseLLMClient(ABC):
    backend: str = "base"

    @abstractmethod
    def complete(self, messages: list[dict], **kwargs) -> ChatResult:
        ...


class MockClient(BaseLLMClient):
    """确定性占位后端：返回一条"宁可 null 不许编"风格的记录，置信度压到 0.6
    以演示"低置信强制进复核队列"逻辑。不联网、不需要密钥。"""
    backend = "mock"

    def __init__(self, model: str = "mock-model", **_):
        self.model = model

    # 经典晶胞占位（仅用于跑通流程，非真实抽取结果，落库后会被回滚）
    _PLACEHOLDER = {
        "PET":  {"a_A": 4.56, "b_A": 5.94, "c_A": 10.75,
                 "alpha_deg": 98.5, "beta_deg": 118.0, "gamma_deg": 112.0,
                 "z": 1, "rho_crystal_gcm3": 1.455, "space_group": "P-1",
                 "crystal_system": "triclinic", "polymorph_label": "triclinic",
                 "fiber_period_A": 10.75, "t_c_celsius": 150, "tm_celsius": 255},
        "PTT":  {"a_A": 4.637, "b_A": 6.226, "c_A": 18.64,
                 "alpha_deg": 98.4, "beta_deg": 93.0, "gamma_deg": 111.5,
                 "z": 1, "rho_crystal_gcm3": 1.414, "space_group": "P-1",
                 "crystal_system": "triclinic", "polymorph_label": "triclinic",
                 "chain_conformation": "tggt", "t_c_celsius": 150},
        "PBT":  {"a_A": 4.83, "b_A": 5.94, "c_A": 11.59,
                 "alpha_deg": 99.7, "beta_deg": 115.2, "gamma_deg": 110.2,
                 "z": 1, "rho_crystal_gcm3": 1.40, "space_group": "P-1",
                 "crystal_system": "triclinic", "polymorph_label": "alpha"},
        "PLA":  {"a_A": 10.66, "b_A": 6.16, "c_A": 28.83,
                 "alpha_deg": 90.0, "beta_deg": 90.0, "gamma_deg": 90.0,
                 "z": 2, "rho_crystal_gcm3": 1.29, "space_group": "P212121",
                 "crystal_system": "orthorhombic", "polymorph_label": "alpha",
                 "t_c_celsius": 120, "tm_celsius": 170},
    }

    def complete(self, messages: list[dict], **kwargs) -> ChatResult:
        # 从最后一条 user 消息里粗略抓 polymer_abbr（pipeline 会在 prompt 里写明）
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        abbr = "PET"
        for cand in ("PET", "PTT", "PBT", "PLA", "PEN", "PBN", "PCL",
                    "PGA", "PBS", "PBSA", "PHB", "PHBV"):
            if cand in last_user:
                abbr = cand
                break
        cell = self._PLACEHOLDER.get(abbr, {})
        payload = {
            "polymer_abbr": abbr,
            "polymorph_label": cell.get("polymorph_label"),
            "crystal_system": cell.get("crystal_system"),
            "space_group": cell.get("space_group"),
            "a_A": cell.get("a_A"), "b_A": cell.get("b_A"), "c_A": cell.get("c_A"),
            "alpha_deg": cell.get("alpha_deg"), "beta_deg": cell.get("beta_deg"),
            "gamma_deg": cell.get("gamma_deg"), "z": cell.get("z"),
            "rho_crystal_gcm3": cell.get("rho_crystal_gcm3"),
            "fiber_period_A": cell.get("fiber_period_A"),
            "chain_conformation": cell.get("chain_conformation"),
            "t_c_celsius": cell.get("t_c_celsius"),
            "tm_celsius": cell.get("tm_celsius"),
            "evidence": "MOCK-EVIDENCE (dry-run placeholder, NOT real extraction)",
            "confidence": 0.6,
            "unknown_fields": ["tm0_celsius", "tg_celsius", "delta_hf_jg",
                               "xtallinity_pct", "growth_rate_nms", "avrami_n"],
        }
        return ChatResult(content=json.dumps(payload, ensure_ascii=False),
                          model=self.model, prompt_tokens=0, completion_tokens=0)


class TokenPlanClient(BaseLLMClient):
    """墨点计划 OpenAI 兼容接口（urllib 实现，无第三方依赖）。"""
    backend = "tokenplan"

    def __init__(self, model: str = TOKENPLAN_DEFAULT_MODEL,
                 base_url: str = TOKENPLAN_BASE_URL,
                 api_key: Optional[str] = None,
                 max_retries: int = 5, timeout: int = 120):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("TOKENPLAN_API_KEY")
        self.max_retries = max_retries
        self.timeout = timeout
        if not self.api_key:
            raise LLMError(
                "未找到 TOKENPLAN_API_KEY 环境变量，也无法从参数传入。"
                "请先 `export TOKENPLAN_API_KEY=<YOUR_KEY>`（见 tokenplan-guide.tex）。"
            )

    def complete(self, messages: list[dict], **kwargs) -> ChatResult:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.0),
            "response_format": kwargs.get("response_format", {"type": "json_object"}),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = json.dumps(payload).encode("utf-8")

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                choice = body["choices"][0]["message"]["content"]
                usage = body.get("usage", {})
                return ChatResult(
                    content=choice,
                    model=body.get("model", self.model),
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    raw=body,
                )
            except urllib.error.HTTPError as e:
                err_body = self._safe_read(e)
                code = self._err_code(err_body)
                if e.code == 429:
                    if code == "quota_exceeded":
                        raise LLMError("墨点额度不足 (quota_exceeded)：不要自动重试，请补充额度。")
                    # rate_limit_exceeded：退避重试
                    self._sleep(attempt)
                    last_err = e
                    continue
                if e.code in (401, 403, 404):
                    raise LLMError(f"不可重试的 HTTP {e.code}（{code}）：检查 Key / 模型 ID / 路径。")
                if e.code >= 500:
                    self._sleep(attempt)
                    last_err = e
                    continue
                raise LLMError(f"HTTP {e.code}: {err_body}")
            except urllib.error.URLError as e:
                # 网络层错误（DNS / 连接），有限次退避
                self._sleep(attempt)
                last_err = e
                continue
        raise LLMError(f"调用在 {self.max_retries} 次重试后仍失败：{last_err}")

    @staticmethod
    def _safe_read(err: urllib.error.HTTPError) -> str:
        try:
            return err.read().decode("utf-8", "ignore")
        except Exception:
            return ""

    @staticmethod
    def _err_code(body: str) -> Optional[str]:
        try:
            return json.loads(body).get("error", {}).get("code")
        except Exception:
            return None

    @staticmethod
    def _sleep(attempt: int) -> None:
        time.sleep(min(2 ** attempt, 30) + (attempt * 0.1))


def get_client(backend: str = "mock", **kwargs) -> BaseLLMClient:
    backend = (backend or "mock").lower()
    if backend == "mock":
        return MockClient(**kwargs)
    if backend == "tokenplan":
        return TokenPlanClient(**kwargs)
    if backend == "local":
        raise NotImplementedError("local 后端（开发机 CPU 开源模型）尚未实现，本期用 tokenplan/mock。")
    raise ValueError(f"未知 backend: {backend}（可选 mock / tokenplan / local）")
