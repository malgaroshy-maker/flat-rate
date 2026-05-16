"""Dictionary CRUD endpoint tests."""


def test_create_term(client):
    r = client.post("/api/dictionary", json={
        "arabic_term": "باطني",
        "standard_category": "Brakes",
        "english_term": "Brake Pads",
    })
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["arabic_term"] == "باطني"
    return data["id"]


def test_list_terms(client):
    client.post("/api/dictionary", json={
        "arabic_term": "فرامل_اختبار",
        "standard_category": "Brakes",
    })
    r = client.get("/api/dictionary")
    assert r.status_code == 200
    data = r.json()
    assert "terms" in data
    assert "count" in data
    assert data["count"] >= 1


def test_search_terms(client):
    client.post("/api/dictionary", json={
        "arabic_term": "محرك_بحث",
        "standard_category": "Engine",
    })
    r = client.get("/api/dictionary", params={"search": "محرك_بحث"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert data["terms"][0]["arabic_term"] == "محرك_بحث"


def test_update_term(client):
    term_id = test_create_term(client)
    r = client.put(f"/api/dictionary/{term_id}", json={
        "english_term": "Disc Brake Pads",
    })
    assert r.status_code == 200
    assert r.json()["english_term"] == "Disc Brake Pads"


def test_delete_term(client):
    term_id = test_create_term(client)
    r = client.delete(f"/api/dictionary/{term_id}")
    assert r.status_code == 200
    r2 = client.get("/api/dictionary")
    ids = [t["id"] for t in r2.json()["terms"]]
    assert term_id not in ids


def test_delete_nonexistent(client):
    r = client.delete("/api/dictionary/nonexistent")
    assert r.status_code == 404


def test_update_nonexistent(client):
    r = client.put("/api/dictionary/nonexistent", json={"english_term": "X"})
    assert r.status_code == 404


def test_create_without_arabic_fails(client):
    r = client.post("/api/dictionary", json={
        "standard_category": "Brakes",
    })
    assert r.status_code == 422  # Pydantic validation
