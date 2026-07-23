"""RAG query engine — search ChromaDB + compute confidence intervals + detect outliers + explainability."""

from __future__ import annotations

import json
import math
import time
from typing import Any, Optional

from embedding_router import embedding_router
from llm_router import llm_router
from qa.pipeline_observability import _STAGE_TIMINGS, reset_timings
from term_expander import expand_query
from vector_store import get_or_create_collection, query_collection, search_with_metadata


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (p / 100.0) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def _detect_outliers(
    qtys: list[float], threshold_sigma: float = 2.0
) -> list[dict]:
    if len(qtys) < 3:
        return []
    mean = sum(qtys) / len(qtys)
    variance = sum((q - mean) ** 2 for q in qtys) / len(qtys)
    sigma = math.sqrt(variance) if variance > 0 else 0.0
    if sigma == 0.0:
        return []
    outliers = []
    for q in qtys:
        if abs(q - mean) > threshold_sigma * sigma:
            outliers.append({
                "value": q,
                "mean": round(mean, 2),
                "sigma": round(sigma, 2),
                "deviation": round((q - mean) / sigma, 1),
            })
    return outliers


def _detect_language(text: str) -> str:
    """Return 'ar' if Arabic-dominant, 'en' otherwise."""
    arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
    if arabic_count > len(text) * 0.2:
        return "ar"
    return "en"


def execute_query(
    query_text: str,
    n_results: int = 5,
    department_filter: Optional[str] = None,
) -> dict:
    t_total = time.perf_counter()

    t0 = time.perf_counter()
    query_lang = _detect_language(query_text)
    _STAGE_TIMINGS["language_detect"].append(round(time.perf_counter() - t0, 6))

    # Expand Libyan-dialect terms (e.g. براونطي) with their fusha/English
    # equivalent before embedding — the historical records were normalized
    # toward fusha at ingestion time, so the raw dialect query alone can
    # under-match against them.
    t0 = time.perf_counter()
    expanded_text, matched_terms = expand_query(query_text)
    query_embedding = embedding_router.encode_single(expanded_text)
    _STAGE_TIMINGS["embed"].append(round(time.perf_counter() - t0, 6))

    col = get_or_create_collection()

    where_clause = None
    if department_filter:
        where_clause = {"departments": {"$contains": department_filter}}

    t0 = time.perf_counter()
    result = query_collection(col, query_embedding, n_results=n_results, where=where_clause)
    _STAGE_TIMINGS["search"].append(round(time.perf_counter() - t0, 6))

    t0 = time.perf_counter()

    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        dist = result["distances"][0][i]
        doc = result["documents"][0][i]

        qty_values = [
            meta["qty_p10"], meta["qty_p25"], meta["qty_median"],
            meta["qty_p75"], meta["qty_p90"],
        ]
        sorted_qtys = sorted([v for v in qty_values if v > 0])

        hit = {
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
            "document": doc[:200],
            # Compound operation flags
            "compound": meta.get("compound", "false") == "true",
            "compound_max_ops": int(meta.get("compound_max_ops", "0") or 0),
            "compound_pct": float(meta.get("compound_pct", "0") or 0),
            "weighted_qty_p50": float(meta.get("weighted_qty_p50", "0") or 0),
            "weighted_qty_p90": float(meta.get("weighted_qty_p90", "0") or 0),
        }
        hits.append(hit)

    confidence_range = {}
    if hits:
        all_p10 = [h["confidence_range"]["p10"] for h in hits if h["confidence_range"]["p10"] > 0]
        all_p50 = [h["confidence_range"]["median"] for h in hits if h["confidence_range"]["median"] > 0]
        all_p90 = [h["confidence_range"]["p90"] for h in hits if h["confidence_range"]["p90"] > 0]
        if all_p50:
            confidence_range = {
                "p10": round(_percentile(sorted(all_p10), 50) if all_p10 else min(all_p50), 1),
                "p50": round(_percentile(sorted(all_p50), 50), 1),
                "p90": round(_percentile(sorted(all_p90), 50) if all_p90 else max(all_p50), 1),
            }

    outliers = []
    for h in hits:
        vals = [h["confidence_range"]["p10"], h["confidence_range"]["p25"],
                h["confidence_range"]["median"], h["confidence_range"]["p75"],
                h["confidence_range"]["p90"]]
        vals = [v for v in vals if v > 0]
        detected = _detect_outliers(vals)
        if detected:
            outliers.append({"model": h["model"], "anomalies": detected})

    _STAGE_TIMINGS["compute"].append(round(time.perf_counter() - t0, 6))

    total_elapsed = round(time.perf_counter() - t_total, 6)
    _STAGE_TIMINGS["total"].append(total_elapsed)

    return {
        "query": query_text,
        "query_language": query_lang,
        "hits": hits,
        "confidence_range": confidence_range,
        "outliers": outliers,
        "matched_terms": matched_terms,
        "mode": "cloud" if embedding_router.use_cloud else "local",
        "timing_ms": round(total_elapsed * 1000, 1),
    }


def generate_natural_response(query_result: dict, output_language: str = "ar") -> str:
    hits = query_result.get("hits", [])
    cr = query_result.get("confidence_range", {})

    if not hits:
        if output_language == "ar":
            return "لم يتم العثور على نتائج مطابقة لهذا الاستفسار."
        return "No matching results found for this query."

    prompt = _build_prompt(query_result, output_language)

    try:
        system = (
            "You are a helpful automotive service advisor assistant. "
            "Respond concisely in the requested language. "
            "If asked in Arabic, respond in Arabic. "
            "Provide labor hour estimates with confidence ranges."
        )
        response = llm_router.generate(prompt, system=system)
        return response
    except Exception:
        if output_language == "ar":
            p50 = cr.get("p50", "?")
            p10 = cr.get("p10", "?")
            p90 = cr.get("p90", "?")
            return f"التقدير: {p10} إلى {p90} ساعة (المتوسط: {p50} ساعة)"
        p50 = cr.get("p50", "?")
        p10 = cr.get("p10", "?")
        p90 = cr.get("p90", "?")
        return f"Estimate: {p10} to {p90} hours (median: {p50}h)"


def _build_prompt(query_result: dict, output_language: str) -> str:
    hits = query_result.get("hits", [])
    cr = query_result.get("confidence_range", {})
    query = query_result.get("query", "")

    parts = [f"Query: {query}"]
    parts.append(f"\nHistorical data (top {len(hits)} matches):")
    for i, h in enumerate(hits):
        parts.append(
            f"  {i+1}. {h['model']} (code={h['code']}): "
            f"median={h['qty_median']}h, range={h['confidence_range']['p10']}-{h['confidence_range']['p90']}h, "
            f"{h['qty_count']} records, dept={h['departments']}"
        )

    if cr:
        parts.append(f"\nAggregated estimate: {cr['p10']}-{cr['p90']} hours (median: {cr['p50']}h)")

    lang_instr = "Respond in Arabic." if output_language == "ar" else "Respond in English."
    parts.append(f"\n{lang_instr}")
    parts.append("Provide a concise labor estimate with the confidence range.")

    return "\n".join(parts)


def explain_estimate(query_result: dict) -> dict:
    """Generate an explainable breakdown of why the estimate was given.

    Returns per-hit contribution weights and the aggregated evidence
    that drove the final confidence interval. Inspired by SHAP-style
    explainability from Model QA Specialist patterns.
    """
    hits = query_result.get("hits", [])
    cr = query_result.get("confidence_range", {})

    if not hits:
        return {"contributions": [], "summary": "no_matches"}

    total_similarity = sum(h["similarity"] for h in hits) or 1.0
    contributions = []
    for h in hits:
        weight = round(h["similarity"] / total_similarity, 4)
        contributions.append(
            {
                "model": h["model"],
                "code": h["code"],
                "similarity": h["similarity"],
                "weight": weight,
                "median_hours": h["qty_median"],
                "range": [
                    h["confidence_range"]["p10"],
                    h["confidence_range"]["p90"],
                ],
                "record_count": h["qty_count"],
                "departments": h["departments"],
            }
        )

    p50 = cr.get("p50", 0)
    p10 = cr.get("p10", 0)
    p90 = cr.get("p90", 0)

    return {
        "contributions": contributions,
        "aggregated_estimate": {"p10": p10, "p50": p50, "p90": p90},
        "range_width": round(p90 - p10, 1) if p90 > p10 else 0,
        "confidence": _estimate_confidence(hits),
        "top_model": contributions[0]["model"] if contributions else None,
        "model_count": len({c["model"] for c in contributions}),
    }


def _estimate_confidence(hits: list[dict]) -> str:
    """Rate estimate confidence based on data quantity and agreement."""
    if not hits:
        return "none"
    total_records = sum(h.get("qty_count", 0) for h in hits)
    models = len({h.get("model", "") for h in hits})
    top_sim = hits[0].get("similarity", 0)

    if total_records >= 50 and models <= 2 and top_sim >= 0.9:
        return "high"
    if total_records >= 15:
        return "medium"
    return "low"
