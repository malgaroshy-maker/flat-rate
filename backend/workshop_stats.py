"""Compute workshop statistics from the live ChromaDB collection instead of
hardcoding numbers in the system prompt that go stale as new data is
ingested (the branch and operation counts previously lived as fixed text
inside system_prompt.py).

Note: a chunk's "departments" metadata field frequently lists all three
workshops (and job-type codes like GR/COF) on the same record — the source
data doesn't cleanly separate department per operation — so per-department
breakdowns would double-count and mislead. Only the reliably computable
totals are reported here; workshop-level distinction stays a per-hit
concern the RAG context already handles via `departments` on each match.
"""

from __future__ import annotations

from functools import lru_cache

from vector_store import get_or_create_collection


@lru_cache(maxsize=1)
def get_workshop_stats() -> dict:
    """Aggregate total record/model counts from ChromaDB.

    Cached for the process lifetime — the dataset only changes on a fresh
    ingestion run, which happens outside the running server.
    """
    try:
        collection = get_or_create_collection()
        result = collection.get(include=["metadatas"])
        metadatas = result.get("metadatas", [])
    except Exception:
        return {"total_records": 0, "total_chunks": 0, "models": 0}

    models: set[str] = set()
    total_records = 0
    for meta in metadatas:
        total_records += int(meta.get("qty_count", 0) or 0)
        models.add(meta.get("model", ""))

    return {
        "total_records": total_records,
        "total_chunks": len(metadatas),
        "models": len(models - {""}),
    }


def format_workshop_stats(lang: str = "ar") -> str:
    """Render the stats as the short context block used in the system prompt."""
    stats = get_workshop_stats()
    if not stats["total_records"]:
        return ""

    if lang == "ar":
        return (
            f"- {stats['models']} موديل مختلف عبر ثلاث ورش (نافطه/ديزل، بنزين، سمكرة وطلاء)\n"
            f"- إجمالي البيانات: {stats['total_records']} عملية مسجلة ({stats['total_chunks']} مجموعة موديل+كود)"
        )
    return (
        f"- {stats['models']} distinct models across three workshops (diesel, gasoline, body & paint)\n"
        f"- Total data: {stats['total_records']} recorded operations ({stats['total_chunks']} model+code groups)"
    )
