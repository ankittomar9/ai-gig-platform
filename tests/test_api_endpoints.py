import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "app": "ai-gig-platform"}

def test_cors_security_preflight():
    # Foreign origin preflight should be rejected
    resp_foreign = client.options("/api/jobs", headers={
        "Origin": "https://malicious-site.com",
        "Access-Control-Request-Method": "GET"
    })
    assert resp_foreign.status_code == 400
    assert "access-control-allow-origin" not in resp_foreign.headers

    # Local origin preflight should be accepted
    resp_local = client.options("/api/jobs", headers={
        "Origin": "http://localhost:8000",
        "Access-Control-Request-Method": "GET"
    })
    assert resp_local.status_code == 200
    assert resp_local.headers.get("access-control-allow-origin") == "http://localhost:8000"

def test_settings_preserves_model():
    # Set model to gemini-1.5-pro first
    resp1 = client.post("/api/settings", json={"gemini_model": "gemini-1.5-pro"})
    assert resp1.status_code == 200

    # Now update only api key
    resp2 = client.post("/api/settings", json={"gemini_api_key": "test-key-999"})
    assert resp2.status_code == 200

    # Model should remain gemini-1.5-pro
    settings = client.get("/api/settings").json()
    assert settings["gemini_model"] == "gemini-1.5-pro"

    # Reset back to default gemini-3.8-flash
    client.post("/api/settings", json={"gemini_model": "gemini-3.8-flash"})

def test_resume_upload_path_traversal_rejection():
    # Malicious path traversal filename
    files = {"file": ("../../etc/shadow", b"fake shadow data", "text/plain")}
    resp = client.post("/api/profile/upload-resume", files=files)
    assert resp.status_code == 400
    assert "Invalid filename" in resp.json()["detail"]
