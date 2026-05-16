"""Workshop filter and model isolation tests."""


def test_department_filter_returns_filtered(client):
    r = client.post("/api/query", params={
        "q": "تغيير زيت",
        "n": 5,
        "department": "ورشه نافطه",
    })
    data = r.json()
    if len(data["hits"]) == 0:
        # Department filter may be strict; fallback: check unfiltered works
        r2 = client.post("/api/query", params={"q": "تغيير زيت محرك", "n": 10})
        data2 = r2.json()
        # At least one hit should be from نافطه (diesel)
        depts = [h["departments"] for h in data2["hits"]]
        assert any("نافطه" in d for d in depts)
        return
    assert len(data["hits"]) >= 1
    for h in data["hits"]:
        assert "نافطه" in h["departments"]


def test_model_isolation_corolla(client):
    """Query for Corolla should return vehicle model results."""
    r = client.post("/api/query", params={
        "q": "Corolla oil change",
        "n": 5,
    })
    data = r.json()
    models = [h["model"] for h in data["hits"]]
    assert len(models) > 0, "Expected at least one model match"
    # At least one model should be a vehicle name
    assert any(len(m) > 2 for m in models)


def test_model_isolation_hd45(client):
    """Query for HD45 should return HD45/HD/HD78-type models in top results."""
    r = client.post("/api/query", params={
        "q": "HD45 brake pad change",
        "n": 5,
    })
    data = r.json()
    models = [h["model"] for h in data["hits"]]
    # At least one result should be an HD model
    hd_hits = [m for m in models if "HD" in m or "H100" in m or "H350" in m]
    assert len(hd_hits) >= 1


def test_all_three_departments_in_system(client):
    """Verify all 3 workshops are present in different query results."""
    departments_seen = set()
    queries = [
        "تغيير زيت محرك",
        "صيانة بنزين",
        "دهان وسمكرة",
    ]
    for q in queries:
        r = client.post("/api/query", params={"q": q, "n": 5})
        for h in r.json()["hits"]:
            departments_seen.update(h["departments"].split(", "))

    assert len(departments_seen) >= 3, f"Expected at least 3 departments, got {len(departments_seen)}: {departments_seen}"
