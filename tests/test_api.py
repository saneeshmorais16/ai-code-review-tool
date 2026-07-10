from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_code_review_endpoint(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path / 'reviews.db'}"
    monkeypatch.setattr("app.database.DATABASE_URL", db_url)
    monkeypatch.setattr("app.storage.get_connection", lambda: __import__("app.database").database.get_connection(db_url))
    monkeypatch.setattr("app.storage.init_db", lambda: __import__("app.database").database.init_db(db_url))

    client = TestClient(app)
    response = client.post(
        "/review/code",
        json={"file_path": "demo.py", "code": "token = \"1234567890abcdef\"\nprint(eval('1+1'))"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] >= 1
    assert body["summary"]["issue_count"] >= 2
    assert any(issue["issue_type"] == "hardcoded_secret" for issue in body["issues"])
