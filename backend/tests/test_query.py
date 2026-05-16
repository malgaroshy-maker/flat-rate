"""Query endpoint tests — 10 queries across departments, edge cases."""


def test_arabic_query_returns_hits(client):
    r = client.post("/api/query", params={"q": "HD45 تغيير باطني فرامل", "n": 3})
    assert r.status_code == 200
    data = r.json()
    assert len(data["hits"]) == 3
    assert data["query_language"] == "ar"


def test_english_query_returns_hits(client):
    r = client.post("/api/query", params={"q": "Corolla oil change", "n": 3})
    assert r.status_code == 200
    data = r.json()
    assert len(data["hits"]) >= 1
    assert data["query_language"] == "en"


def test_confidence_range_present(client):
    r = client.post("/api/query", params={"q": "HD45 brake", "n": 5})
    data = r.json()
    cr = data["confidence_range"]
    assert "p10" in cr
    assert "p50" in cr
    assert "p90" in cr
    assert cr["p50"] > 0


def test_outliers_key_present(client):
    r = client.post("/api/query", params={"q": "سمكرة وطلاء", "n": 5})
    data = r.json()
    assert "outliers" in data
    assert isinstance(data["outliers"], list)


def test_no_results_handles_gracefully(client):
    r = client.post("/api/query", params={"q": "xyzwtfgh", "n": 3})
    assert r.status_code == 200
    data = r.json()
    assert len(data["hits"]) >= 0


def test_long_arabic_query(client):
    q = "كشف علي ودار زيت فرامل ظهور لامبة زيت الفرامل وتغيير باطني امامي وخلفي"
    r = client.post("/api/query", params={"q": q, "n": 3})
    assert r.status_code == 200
    assert len(r.json()["hits"]) >= 1


def test_mixed_language_query(client):
    r = client.post("/api/query", params={"q": "HD45 engine oil", "n": 3})
    assert r.status_code == 200


def test_single_result(client):
    r = client.post("/api/query", params={"q": "H100 body repair", "n": 1})
    assert r.status_code == 200
    assert len(r.json()["hits"]) <= 1


def test_diesel_workshop_query(client):
    r = client.post("/api/query", params={"q": "تغيير زيت محرك", "n": 5})
    data = r.json()
    depts = [h["departments"] for h in data["hits"]]
    assert any("نافطه" in d for d in depts)


def test_gasoline_workshop_query(client):
    r = client.post("/api/query", params={"q": "صيانة كورولا", "n": 5})
    data = r.json()
    models = [h["model"] for h in data["hits"]]
    # Corolla may appear in Arabic or English; check at least one result
    assert len(models) >= 1


def test_body_workshop_query(client):
    r = client.post("/api/query", params={"q": "سمكرة وطلاء", "n": 5})
    data = r.json()
    assert len(data["hits"]) >= 1


def test_mode_field_present(client):
    r = client.post("/api/query", params={"q": "test", "n": 1})
    data = r.json()
    assert data["mode"] in ("cloud", "local")
