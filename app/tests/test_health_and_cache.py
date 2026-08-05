import pytest
from fastapi.testclient import TestClient
from main import app
from cache import cache_set, cache_get, cache_delete

client = TestClient(app)

def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readyz_endpoint():
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "database" in data
    assert "cache" in data

def test_cache_set_and_get():
    key = "test_key_phase1"
    val = {"status": "success", "count": 42}
    cache_set(key, val, expire_seconds=60)
    
    res = cache_get(key)
    assert res is not None
    assert res["status"] == "success"
    assert res["count"] == 42
    
    cache_delete(key)
    assert cache_get(key) is None
