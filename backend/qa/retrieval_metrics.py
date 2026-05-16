"""Retrieval quality metrics: MRR, NDCG, precision@k.

Inspired by AI Engineer: retrieval accuracy tracking.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from embedding_router import embedding_router
from vector_store import get_or_create_collection, query_collection


@dataclass
class RetrievalReport:
    mrr: float = 0.0
    precision_at_1: float = 0.0
    precision_at_3: float = 0.0
    precision_at_5: float = 0.0
    ndcg_at_3: float = 0.0
    ndcg_at_5: float = 0.0
    queries_run: int = 0
    per_query: list[dict] = field(default_factory=list)


def _dcg(relevance_scores: list[float], k: int) -> float:
    dcg = 0.0
    for i, rel in enumerate(relevance_scores[:k]):
        dcg += (2 ** rel - 1) / math.log2(i + 2)
    return dcg


def _ndcg(relevance_scores: list[float], k: int) -> float:
    ideal = sorted(relevance_scores, reverse=True)
    dcg_val = _dcg(relevance_scores, k)
    idcg_val = _dcg(ideal, k)
    return dcg_val / idcg_val if idcg_val > 0 else 0.0


def evaluate_retrieval(
    n_results: int = 5,
    max_queries: Optional[int] = None,
    department_filter: Optional[str] = None,
) -> RetrievalReport:
    """Evaluate retrieval quality by querying each chunk as its own ground truth.

    For each chunk in ChromaDB, the chunk's own text is the query,
    and the correct result is that chunk itself (rank should be 1).
    """
    col = get_or_create_collection()
    all_data = col.get(include=["documents", "metadatas"])

    if not all_data["ids"]:
        return RetrievalReport()

    ids = all_data["ids"]
    docs = all_data["documents"] or []
    metas = all_data["metadatas"] or []
    total = len(ids)

    if max_queries is not None and max_queries == 0:
        return RetrievalReport()
    elif max_queries is not None and max_queries < total:
        step = max(total // max_queries, 1)
        indices = list(range(0, total, step))[:max_queries]
    else:
        indices = list(range(total))

    report = RetrievalReport()
    reciprocal_ranks: list[float] = []
    precisions_1: list[float] = []
    precisions_3: list[float] = []
    precisions_5: list[float] = []
    ndcgs_3: list[float] = []
    ndcgs_5: list[float] = []

    for idx in indices:
        query_text = docs[idx] if docs else ""
        chunk_id = ids[idx]
        query_embedding = embedding_router.encode_single(query_text)

        where_clause = None
        if department_filter:
            where_clause = {"departments": {"$contains": department_filter}}

        result = query_collection(col, query_embedding, n_results=n_results, where=where_clause)
        result_ids = result["ids"][0]

        if not result_ids:
            rank = n_results + 1
        else:
            try:
                rank = result_ids.index(chunk_id) + 1
            except ValueError:
                rank = n_results + 1

        rr = 1.0 / rank
        reciprocal_ranks.append(rr)

        relevance = [1 if rid == chunk_id else 0 for rid in result_ids[:n_results]]
        precisions_1.append(1.0 if rank == 1 else 0.0)
        precisions_3.append(sum(relevance[:3]) / max(1, min(3, len(relevance))))
        precisions_5.append(sum(relevance[:5]) / max(1, min(5, len(relevance))))
        ndcgs_3.append(_ndcg([float(r) for r in relevance], 3))
        ndcgs_5.append(_ndcg([float(r) for r in relevance], 5))

        report.per_query.append({
            "chunk_id": chunk_id,
            "model": metas[idx].get("model", "") if idx < len(metas) else "",
            "code": metas[idx].get("code", "") if idx < len(metas) else "",
            "rank": rank,
            "reciprocal_rank": round(rr, 4),
        })

    report.queries_run = len(indices)
    if report.queries_run > 0:
        report.mrr = round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4)
        report.precision_at_1 = round(sum(precisions_1) / len(precisions_1), 4)
        report.precision_at_3 = round(sum(precisions_3) / len(precisions_3), 4)
        report.precision_at_5 = round(sum(precisions_5) / len(precisions_5), 4)
        report.ndcg_at_3 = round(sum(ndcgs_3) / len(ndcgs_3), 4)
        report.ndcg_at_5 = round(sum(ndcgs_5) / len(ndcgs_5), 4)

    return report
