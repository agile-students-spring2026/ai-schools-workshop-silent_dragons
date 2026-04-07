from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_homepage_serves_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "District Insight" in response.text


def test_static_asset_served() -> None:
    client = TestClient(app)
    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "runSearch" in response.text


def test_healthcheck() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_ranked_districts() -> None:
    client = TestClient(app)
    response = client.get("/districts?top_k=3&min_grad_rate=90")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) <= 3
    assert all("score" in item for item in payload["results"])


def test_get_single_district_score_success() -> None:
    client = TestClient(app)
    response = client.get("/districts/CA-001/score")
    assert response.status_code == 200
    payload = response.json()
    assert payload["district_id"] == "CA-001"
    assert payload["score"] > 0


def test_get_single_district_score_not_found() -> None:
    client = TestClient(app)
    response = client.get("/districts/NOPE/score")
    assert response.status_code == 404
    assert response.json()["detail"] == "District not found"
