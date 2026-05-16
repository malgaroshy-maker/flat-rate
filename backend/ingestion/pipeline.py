"""Orchestration pipeline: chunk -> embed -> store."""

import os
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from config import settings
from dictionary_store import dictionary_store
from embedding_router import embedding_router
from ingestion.docx_parser import parse_dictionary
from ingestion.normalizer import Normalizer
from ingestion.xlsx_parser import LaborRecord, parse_xlsx
from vector_store import add_to_collection, get_or_create_collection, reset_collection


def _chunk_records(records: list[LaborRecord]) -> list[dict]:
    """Group records by (Model, Labor Code) for embedding isolation."""
    groups: dict[tuple[str, str], list[LaborRecord]] = defaultdict(list)
    for r in records:
        key = (r.model, r.code)
        groups[key].append(r)

    chunks: list[dict] = []
    for (model, code), group in groups.items():
        qtys = [r.qty for r in group]
        prices = [r.price for r in group]
        descriptions = list({r.description for r in group})
        departments = list({r.department for r in group})
        franchises = list({r.franchise for r in group})

        # Detect compound descriptions (multi-operation records)
        compound_counts = [_count_operations(r.description) for r in group]
        compound_any = any(c > 1 for c in compound_counts)
        compound_max = max(compound_counts) if compound_any else 0
        compound_pct = sum(1 for c in compound_counts if c > 1) / len(compound_counts)

        # Weighted QTY: divide compound record QTY by operation count for unit estimates
        weighted_qtys = [
            r.qty / _count_operations(r.description) for r in group
        ]

        combined_text = f"Model: {model}. Code: {code}. Franchise: {franchises[0]}. " + " ".join(descriptions)

        chunks.append(
            {
                "id": f"{model}_{code}",
                "model": model,
                "code": code,
                "description": combined_text,
                "qty_values": qtys,
                "price_values": prices,
                "qty_count": len(qtys),
                "qty_mean": sum(qtys) / len(qtys) if qtys else 0.0,
                "qty_median": _median(sorted(qtys)) if qtys else 0.0,
                "qty_p10": _percentile(sorted(qtys), 10) if qtys else 0.0,
                "qty_p25": _percentile(sorted(qtys), 25) if qtys else 0.0,
                "qty_p75": _percentile(sorted(qtys), 75) if qtys else 0.0,
                "qty_p90": _percentile(sorted(qtys), 90) if qtys else 0.0,
                "price_mean": sum(prices) / len(prices) if prices else 0.0,
                "departments": departments,
                "franchises": franchises,
                # Compound operation flags
                "compound": compound_any,
                "compound_max_ops": compound_max,
                "compound_pct": round(compound_pct, 2),
                # Weighted QTY (unit estimate) percentiles
                "weighted_qty_p50": _median(sorted(weighted_qtys)) if weighted_qtys else 0.0,
                "weighted_qty_p90": _percentile(sorted(weighted_qtys), 90) if weighted_qtys else 0.0,
            }
        )

    return chunks


def _count_operations(description: str) -> int:
    """Count sub-operations in a compound description.

    Uses newlines as primary delimiter. Falls back to 'و'/'مع' conjunctions
    for single-line compound descriptions.
    """
    lines = [l.strip() for l in description.split("\n") if l.strip()]
    if len(lines) >= 2:
        return len(lines)
    # Single line: count ' و ' or ' مع ' conjunctions as operation separators
    if " و " in description or ("مع " in description and "معا" not in description):
        parts = description.replace(" و ", "|").replace("مع ", "|").split("|")
        parts = [p.strip() for p in parts if len(p.strip()) > 3]
        if len(parts) >= 2:
            return len(parts)
    return 1


def _median(sorted_values: list[float]) -> float:
    n = len(sorted_values)
    if n == 0:
        return 0.0
    if n % 2 == 0:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    return sorted_values[n // 2]


def _percentile(sorted_values: list[float], p: int) -> float:
    if not sorted_values:
        return 0.0
    idx = (p / 100) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def run_pipeline(
    xlsx_paths: list[str | Path],
    docx_path: str | Path | None = None,
    reset: bool = False,
) -> dict:
    print("=== Phase 1: Data Pipeline ===")
    t0 = time.time()

    # 1. Parse Excel(s) — merge and dedup
    all_records: list[LaborRecord] = []
    seen_invoices: set[str] = set()
    for xp in xlsx_paths:
        print(f"\n[1/5] Parsing XLSX: {xp}")
        records = parse_xlsx(xp)
        new_count = 0
        for r in records:
            key = r.invoice_number.strip() if r.invoice_number else ""
            if key and key not in seen_invoices:
                seen_invoices.add(key)
                all_records.append(r)
                new_count += 1
            elif not key:
                all_records.append(r)
                new_count += 1
        print(f"       Loaded {len(records)} records ({new_count} new after dedup)")
    print(f"       Total unique records: {len(all_records)}")

    # 2. Parse dictionary
    normalizer: Normalizer | None = None
    if docx_path and Path(docx_path).exists():
        print(f"\n[2/5] Parsing dictionary: {docx_path}")
        dictionary = parse_dictionary(docx_path)
        normalizer = Normalizer(dictionary)
        print(f"       Loaded {len(dictionary)} terms across categories")
        # Seed into persistent dictionary store
        seeded = dictionary_store.seed_terms(dictionary)
        print(f"       Seeded {seeded} terms into dictionary store")
    else:
        print("\n[2/5] No dictionary provided, skipping normalization")

    # 3. Normalize descriptions
    if normalizer:
        print("\n[3/5] Normalizing descriptions")
        for r in all_records:
            r.description = normalizer.normalize_description(r.description)
        print("       Done")
        # Extract unique Arabic slang terms from POS descriptions into dictionary
        print("       Extracting terms from POS descriptions...")
        unique_terms: set[str] = set()
        for r in all_records:
            found = normalizer.find_terms_in_text(r.description)
            for ft in found:
                arabic = ft.get("arabic_term", "").strip()
                if arabic and len(arabic) > 2:
                    unique_terms.add(arabic)
        if unique_terms:
            auto_entries = [{"arabic_term": t, "category": normalizer.get_dominant_category(t), "english_term": t}
                          for t in sorted(unique_terms)]
            added = dictionary_store.seed_terms(auto_entries)
            print(f"       Extracted {len(unique_terms)} unique terms ({added} new in store)")
    else:
        print("\n[3/5] Skipping normalization (no dictionary)")

    # 4. Chunk by (Model, Code)
    print("\n[4/5] Chunking records by (Model, Labor Code)")
    chunks = _chunk_records(all_records)
    print(f"       Created {len(chunks)} chunks")

    # 5. Embed
    print("\n[5/5] Generating embeddings")
    texts = [c["description"] for c in chunks]
    ids = [c["id"] for c in chunks]
    print(f"       Encoding {len(texts)} texts...")
    embedded_model = "paraphrase-multilingual-MiniLM-L12-v2"
    use_gemini = bool(settings.GEMINI_API_KEY)
    if use_gemini:
        print(f"       Using: {settings.GEMINI_EMBEDDING_MODEL}")
        try:
            embeddings = embedding_router.encode_cloud(texts)
            embedded_model = settings.GEMINI_EMBEDDING_MODEL
        except Exception as e:
            print(f"       Gemini failed ({e}), falling back to local")
            use_gemini = False
    if not use_gemini:
        print("       Using: paraphrase-multilingual-MiniLM-L12-v2")
        from sentence_transformers import SentenceTransformer
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*unauthenticated.*")
            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # 6. Store in ChromaDB
    print("\n[6/6] Storing in ChromaDB")
    collection = reset_collection() if reset else get_or_create_collection()
    if reset:
        collection.modify(metadata={"embedding_model": embedded_model})

    metadatas = []
    for c in chunks:
        metadatas.append(
            {
                "model": c["model"],
                "code": c["code"],
                "qty_count": c["qty_count"],
                "qty_mean": c["qty_mean"],
                "qty_median": c["qty_median"],
                "qty_p10": c["qty_p10"],
                "qty_p25": c["qty_p25"],
                "qty_p75": c["qty_p75"],
                "qty_p90": c["qty_p90"],
                "price_mean": c["price_mean"],
                "departments": ", ".join(c["departments"]),
                "franchises": ", ".join(c["franchises"]),
                "compound": str(c["compound"]).lower(),
                "compound_max_ops": str(c["compound_max_ops"]),
                "compound_pct": str(c["compound_pct"]),
                "weighted_qty_p50": str(c["weighted_qty_p50"]),
                "weighted_qty_p90": str(c["weighted_qty_p90"]),
            }
        )

    add_to_collection(collection, ids, embeddings if isinstance(embeddings, list) else embeddings.tolist(), metadatas, texts)
    print(f"       Stored {len(ids)} vectors")

    elapsed = time.time() - t0
    result = {
        "records": len(all_records),
        "chunks": len(chunks),
        "dictionary_terms": len(normalizer.known_arabic_terms) if normalizer else 0,
        "elapsed_seconds": round(elapsed, 1),
    }
    print(f"\nPipeline complete in {elapsed:.1f}s")
    print(f"  Records: {result['records']}")
    print(f"  Chunks:  {result['chunks']}")
    print(f"  Terms:   {result['dictionary_terms']}")

    return result
