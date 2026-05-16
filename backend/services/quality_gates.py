"""Quality gates — validation checks between pipeline stages.

Inspired by Agents Orchestrator: no phase advancement without meeting quality standards.
"""

from __future__ import annotations

from typing import Any


def gate_embed(result: Any) -> tuple[bool, str]:
    if result is None:
        return False, "Embedding is None"
    if not hasattr(result, "embedding") or not result.embedding:
        return False, "Embedding vector is empty"
    if len(result.embedding) < 100:
        return False, f"Embedding too short: {len(result.embedding)} dims"
    return True, "ok"


def gate_search(result: Any) -> tuple[bool, str]:
    if result is None:
        return False, "Search result is None"
    if not hasattr(result, "hits"):
        return False, "Search result missing hits"
    return True, "ok"


def gate_compute(result: Any) -> tuple[bool, str]:
    if result is None:
        return False, "Compute result is None"
    if not hasattr(result, "confidence_range"):
        return False, "Missing confidence_range"
    cr = result.confidence_range
    if cr:
        p10 = cr.get("p10", 0)
        p50 = cr.get("p50", 0)
        p90 = cr.get("p90", 0)
        if p10 < 0 or p50 < 0 or p90 < 0:
            return False, "Negative values in confidence range"
        if p10 > p50 or p50 > p90:
            return False, "Percentiles not monotonic"
    return True, "ok"


def gate_explain(result: Any) -> tuple[bool, str]:
    if result is None:
        return False, "Explain result is None"
    if not hasattr(result, "contributions"):
        return False, "Missing contributions"
    if result.contributions:
        total_weight = sum(c.get("weight", 0) for c in result.contributions)
        if not (0.9 <= total_weight <= 1.1):
            return False, f"Weight sum {total_weight:.3f} not within [0.9, 1.1]"
    return True, "ok"


def gate_generate(result: Any) -> tuple[bool, str]:
    if result is None:
        return False, "Generate result is None"
    if not hasattr(result, "response_text"):
        return False, "Missing response_text"
    if not result.response_text or not result.response_text.strip():
        return False, "Empty response"
    if "Error:" in result.response_text:
        return False, "Response contains error pattern"
    return True, "ok"


GATE_MAP = {
    "embed": gate_embed,
    "search": gate_search,
    "compute": gate_compute,
    "explain": gate_explain,
    "generate": gate_generate,
}
