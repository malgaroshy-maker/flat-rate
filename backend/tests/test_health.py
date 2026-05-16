"""Health endpoint tests."""


def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "mode" in data
    assert data["mode"] in ("cloud", "local")
    assert "embedding_model" in data
    assert "local_llm_backend" in data


def test_health_mode_detection(client):
    r = client.get("/api/health")
    data = r.json()
    assert data["mode"] in ("cloud", "local")
