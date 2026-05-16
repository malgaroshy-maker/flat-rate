"""High-level query service using the pipeline orchestrator.

Wraps query_engine.py stages as orchestrated pipeline stages.
Includes LRU response cache for repeat queries.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from typing import Optional

from embedding_router import embedding_router
from query_engine import _build_prompt, _detect_language, _percentile, explain_estimate
from services.orchestrator import PipelineOrchestrator
from services.pipeline_stages import (
    ComputeInput,
    ComputeOutput,
    EmbedInput,
    EmbedOutput,
    ExplainInput,
    ExplainOutput,
    GenerateInput,
    GenerateOutput,
    SearchInput,
    SearchOutput,
)
from vector_store import get_or_create_collection, query_collection

_orchestrator: Optional[PipelineOrchestrator] = None
_cache: OrderedDict[str, tuple[dict, float]] = OrderedDict()
CACHE_MAX_SIZE = 100
CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_key(query_text: str, n_results: int, department_filter: Optional[str]) -> str:
    raw = f"{query_text}|{n_results}|{department_filter or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def invalidate_cache() -> None:
    _cache.clear()


def _get_cached(key: str) -> Optional[dict]:
    if key in _cache:
        result, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            _cache.move_to_end(key)
            return result
        del _cache[key]
    return None


def _set_cache(key: str, result: dict) -> None:
    if len(_cache) >= CACHE_MAX_SIZE:
        _cache.popitem(last=False)
    _cache[key] = (result, time.time())
    _cache.move_to_end(key)

_orchestrator: Optional[PipelineOrchestrator] = None


def _get_orchestrator() -> PipelineOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        orch = PipelineOrchestrator()
        orch.set_embed_stage(_embed_stage)
        orch.set_search_stage(_search_stage)
        orch.set_compute_stage(_compute_stage)
        orch.set_explain_stage(_explain_stage)
        orch.set_generate_stage(_generate_stage)
        _orchestrator = orch
    return _orchestrator


def _embed_stage(input_data: EmbedInput) -> EmbedOutput:
    query_lang = _detect_language(input_data.query_text)
    embedding = embedding_router.encode_single(input_data.query_text)
    return EmbedOutput(embedding=embedding, query_language=query_lang)


def _search_stage(input_data: SearchInput) -> SearchOutput:
    col = get_or_create_collection()
    where_clause = None
    if input_data.department_filter:
        where_clause = {"departments": {"$contains": input_data.department_filter}}

    result = query_collection(col, input_data.embedding, n_results=input_data.n_results, where=where_clause)

    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        dist = result["distances"][0][i]
        doc = result["documents"][0][i]
        hits.append({
            "id": result["ids"][0][i],
            "model": meta["model"],
            "code": meta["code"],
            "qty_count": meta["qty_count"],
            "qty_median": meta["qty_median"],
            "qty_mean": meta["qty_mean"],
            "confidence_range": {
                "p10": meta["qty_p10"],
                "p25": meta["qty_p25"],
                "median": meta["qty_median"],
                "p75": meta["qty_p75"],
                "p90": meta["qty_p90"],
            },
            "price_mean": meta["price_mean"],
            "departments": meta["departments"],
            "franchises": meta["franchises"],
            "similarity": round(1.0 - dist, 3),
            "document": doc[:200] if doc else "",
        })
    return SearchOutput(hits=hits, mode="cloud" if embedding_router.use_cloud else "local")


def _compute_stage(input_data: ComputeInput) -> ComputeOutput:
    hits = input_data.hits
    confidence_range: dict = {}
    if hits:
        all_p10 = [h["confidence_range"]["p10"] for h in hits if float(h["confidence_range"]["p10"]) > 0]
        all_p50 = [h["confidence_range"]["median"] for h in hits if float(h["confidence_range"]["median"]) > 0]
        all_p90 = [h["confidence_range"]["p90"] for h in hits if float(h["confidence_range"]["p90"]) > 0]
        if all_p50:
            confidence_range = {
                "p10": round(_percentile(sorted(all_p10), 50) if all_p10 else min(all_p50), 1),
                "p50": round(_percentile(sorted(all_p50), 50), 1),
                "p90": round(_percentile(sorted(all_p90), 50) if all_p90 else max(all_p50), 1),
            }

    outliers = []
    for h in hits:
        vals = [
            float(h["confidence_range"]["p10"]), float(h["confidence_range"]["p25"]),
            float(h["confidence_range"]["median"]), float(h["confidence_range"]["p75"]),
            float(h["confidence_range"]["p90"]),
        ]
        vals = [v for v in vals if v > 0]
        if len(vals) >= 3:
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
            sigma = variance ** 0.5 if variance > 0 else 0
            if sigma > 0:
                flagged = [{"value": v, "mean": round(mean, 2), "sigma": round(sigma, 2)} for v in vals if abs(v - mean) > 2 * sigma]
                if flagged:
                    outliers.append({"model": h["model"], "anomalies": flagged})

    return ComputeOutput(confidence_range=confidence_range, outliers=outliers)


def _explain_stage(input_data: ExplainInput) -> ExplainOutput:
    result = explain_estimate({"hits": input_data.hits, "confidence_range": input_data.confidence_range})
    return ExplainOutput(
        contributions=result.get("contributions", []),
        confidence=result.get("confidence", "none"),
        top_model=result.get("top_model"),
        model_count=result.get("model_count", 0),
    )


def _generate_stage(input_data: GenerateInput) -> GenerateOutput:
    from llm_router import llm_router

    query_result = {
        "query": input_data.query_text,
        "hits": input_data.hits,
        "confidence_range": input_data.confidence_range,
    }
    prompt = _build_prompt(query_result, input_data.output_language)
    system = (
        "You are a helpful automotive service advisor assistant. "
        "Respond concisely in the requested language."
    )
    try:
        response = llm_router.generate(prompt, system=system)
        return GenerateOutput(response_text=response)
    except Exception:
        cr = input_data.confidence_range or {}
        p50 = cr.get("p50", "?")
        p10 = cr.get("p10", "?")
        p90 = cr.get("p90", "?")
        if input_data.output_language == "ar":
            return GenerateOutput(response_text=f"التقدير: {p10} إلى {p90} ساعة (المتوسط: {p50} ساعة)")
        return GenerateOutput(response_text=f"Estimate: {p10} to {p90} hours (median: {p50}h)")


def query_with_orchestrator(
    query_text: str,
    n_results: int = 5,
    department_filter: Optional[str] = None,
    lang: str = "ar",
    generate: bool = False,
) -> dict:
    if not generate:
        ck = _cache_key(query_text, n_results, department_filter)
        cached = _get_cached(ck)
        if cached is not None:
            return cached

    orch = _get_orchestrator()
    result, _ = orch.run_query_pipeline(
        query_text=query_text,
        n_results=n_results,
        department_filter=department_filter,
        output_language=lang,
        generate_response=generate,
    )

    if not generate:
        _set_cache(ck, result)
    return result
