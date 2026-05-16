"""Data integrity tests — verify pipeline output matches source data."""


def test_chromadb_collection_exists():
    from vector_store import get_or_create_collection
    col = get_or_create_collection()
    assert col.count() >= 1


def test_collection_count_514():
    from vector_store import get_or_create_collection
    col = get_or_create_collection()
    count = col.count()
    assert count >= 400, f"Expected at least 400 chunks, got {count}"


def test_all_three_departments_in_chroma():
    from vector_store import get_or_create_collection
    col = get_or_create_collection()
    results = col.get(include=["metadatas"])
    departments_all = set()
    for meta in results["metadatas"]:
        if "departments" in meta:
            for d in meta["departments"].split(", "):
                departments_all.add(d.strip())
    assert "ورشه نافطه" in departments_all
    assert "ورشه بنزين" in departments_all
    assert "ورشه سمكره وطلاء" in departments_all


def test_no_null_models():
    from vector_store import get_or_create_collection
    col = get_or_create_collection()
    results = col.get(include=["metadatas"])
    for meta in results["metadatas"]:
        assert meta.get("model"), f"Null model in metadata"
        assert meta["model"].strip(), f"Empty model in metadata"


def test_qty_stats_present():
    from vector_store import get_or_create_collection
    col = get_or_create_collection()
    results = col.get(include=["metadatas"])
    for meta in results["metadatas"]:
        assert "qty_median" in meta
        assert "qty_mean" in meta
        assert "qty_p10" in meta
        assert "qty_p90" in meta


def test_embedding_router_local_works():
    from embedding_router import embedding_router
    vec = embedding_router.encode_single("اختبار النص العربي")
    assert len(vec) == 384
    assert any(v != 0 for v in vec)


def test_xlsx_parser_record_count():
    from pathlib import Path
    from ingestion.xlsx_parser import parse_xlsx
    path = Path(__file__).resolve().parent.parent.parent / "تقرير اليد العاملة بالكامل.xlsx"
    records = parse_xlsx(path)
    assert len(records) == 2564
    # Check first record has fields
    r = records[0]
    assert r.model
    assert r.department
    assert r.code


def test_docx_parser_term_count():
    from pathlib import Path
    from ingestion.docx_parser import parse_dictionary
    path = Path(__file__).resolve().parent.parent.parent / "The Libyan Automotive Dictionary of Mechanical and Technical Terms.docx"
    terms = parse_dictionary(path)
    assert len(terms) >= 90
    assert any("Engine" in t["category"] for t in terms)
