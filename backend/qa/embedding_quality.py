"""Embedding quality validation: model isolation in vector space.

Inspired by AI Engineer + Model QA Specialist: validates that the
Model-weighted embedding strategy actually isolates vehicle models.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from embedding_router import embedding_router
from vector_store import get_or_create_collection


@dataclass
class IsolationReport:
    intra_model_mean: float = 0.0
    inter_model_mean: float = 0.0
    isolation_ratio: float = 0.0
    models_tested: int = 0
    per_model: list[dict] = field(default_factory=list)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = float(np.dot(a_arr, b_arr))
    norm_a = float(np.linalg.norm(a_arr))
    norm_b = float(np.linalg.norm(b_arr))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return round(dot / (norm_a * norm_b), 4)


def evaluate_embedding_isolation() -> IsolationReport:
    """Validate that same-model chunks cluster tighter than cross-model chunks.

    For each model, compute:
    - intra-model similarity: avg cosine between chunks of the SAME model
    - inter-model similarity: avg cosine between chunks of DIFFERENT models

    A healthy isolation ratio (intra/inter) should be > 1.0.
    """
    col = get_or_create_collection()
    all_data = col.get(include=["embeddings", "metadatas"])

    if not all_data["ids"]:
        return IsolationReport()

    ids = all_data["ids"]
    embeddings_raw = all_data["embeddings"]
    metas = all_data["metadatas"] or []
    if embeddings_raw is None or len(embeddings_raw) == 0:
        return IsolationReport()
    embeddings = [list(e) for e in embeddings_raw]

    model_chunks: dict[str, list[tuple[str, list[float]]]] = defaultdict(list)
    for i, chunk_id in enumerate(ids):
        if i < len(metas) and i < len(embeddings):
            model = metas[i].get("model", "unknown")
            model_chunks[model].append((chunk_id, embeddings[i]))

    models_with_multiple = {m: chunks for m, chunks in model_chunks.items() if len(chunks) >= 2}
    if len(models_with_multiple) < 2:
        return IsolationReport()

    report = IsolationReport()
    intra_sims: list[float] = []
    inter_sims: list[float] = []

    model_names = list(models_with_multiple.keys())
    for model in model_names:
        chunks = models_with_multiple[model]
        model_intra: list[float] = []
        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                sim = _cosine_similarity(chunks[i][1], chunks[j][1])
                model_intra.append(sim)
                intra_sims.append(sim)

        model_inter: list[float] = []
        for other_model in model_names:
            if other_model == model:
                continue
            other_chunks = models_with_multiple[other_model]
            sample_other = other_chunks[min(len(chunks) - 1, len(other_chunks) - 1)]
            for chunk in chunks[: min(3, len(chunks))]:
                sim = _cosine_similarity(chunk[1], sample_other[1])
                model_inter.append(sim)
                inter_sims.append(sim)

        report.per_model.append({
            "model": model,
            "chunk_count": len(chunks),
            "intra_mean": round(sum(model_intra) / len(model_intra), 4) if model_intra else 0.0,
            "inter_mean": round(sum(model_inter) / len(model_inter), 4) if model_inter else 0.0,
        })

    report.models_tested = len(model_names)
    if intra_sims:
        report.intra_model_mean = round(sum(intra_sims) / len(intra_sims), 4)
    if inter_sims:
        report.inter_model_mean = round(sum(inter_sims) / len(inter_sims), 4)
    if report.inter_model_mean > 0:
        report.isolation_ratio = round(report.intra_model_mean / report.inter_model_mean, 2)

    return report
