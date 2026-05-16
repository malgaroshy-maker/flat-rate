"""Pending inbox endpoint tests."""


def test_add_pending(client):
    r = client.post("/api/dictionary/pending", json={
        "term_text": "طرمبة",
        "query_text": "كشف طرمبة زيت",
    })
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    return data["id"]


def test_list_pending_empty(client):
    r = client.get("/api/dictionary/pending")
    assert r.status_code == 200
    assert "pending" in r.json()


def test_resolve_pending_creates_term(client):
    pid = test_add_pending(client)
    r = client.post(f"/api/dictionary/pending/{pid}/resolve", json={
        "arabic_term": "طرمبة_ماء",
        "standard_category": "Cooling",
        "english_term": "Water Pump",
    })
    assert r.status_code == 200
    data = r.json()
    assert "resolved_term_id" in data

    # Verify term now in dictionary
    r = client.get("/api/dictionary", params={"search": "طرمبة_ماء"})
    assert r.json()["count"] >= 1


def test_resolve_nonexistent(client):
    r = client.post("/api/dictionary/pending/bad-id/resolve", json={
        "arabic_term": "X",
        "standard_category": "Y",
    })
    assert r.status_code == 404
