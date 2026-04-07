from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_homepage_serves_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Find your best-fit district and schools" in response.text
    assert "Parent" in response.text
    assert "Educator" in response.text


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


def test_search_zip_returns_likely_districts_and_schools() -> None:
    client = TestClient(app)
    response = client.get("/search?query=10027&audience=parent")
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "zip"
    assert len(payload["district_suggestions"]) >= 1
    assert len(payload["districts"]) >= 1
    assert "likely district options" in payload["helper_text"].lower()
    first_suggestion = payload["district_suggestions"][0]
    assert "source_name" in first_suggestion


def test_search_school_name_returns_school_match() -> None:
    client = TestClient(app)
    response = client.get("/search?query=Scarsdale+High+School&audience=educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["audience"] == "educator"
    assert any("Scarsdale High School" in school["title"] for school in payload["schools"])


def test_search_invalid_audience_rejected() -> None:
    client = TestClient(app)
    response = client.get("/search?query=orlando&audience=student")
    assert response.status_code == 422
