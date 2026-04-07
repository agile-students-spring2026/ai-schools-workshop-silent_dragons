from __future__ import annotations

from app.data import load_districts, load_schools, load_zip_district_suggestions
from app.models import ZipDistrictSuggestion
from app.search import search_catalog


def test_search_catalog_zip_returns_suggestions_and_limited_cards() -> None:
    payload = search_catalog(
        query="10027",
        audience="parent",
        districts=load_districts(),
        schools=load_schools(),
        zip_suggestions=load_zip_district_suggestions(),
    )
    assert payload["intent"] == "zip"
    assert len(payload["district_suggestions"]) >= 1
    assert len(payload["districts"]) <= 8
    assert len(payload["schools"]) <= 10


def test_search_catalog_district_query_matches_by_name() -> None:
    payload = search_catalog(
        query="Palo Alto Unified",
        audience="educator",
        districts=load_districts(),
        schools=load_schools(),
        zip_suggestions=load_zip_district_suggestions(),
    )
    assert payload["intent"] in {"district", "general"}
    assert any(item["title"] == "Palo Alto Unified" for item in payload["districts"])


def test_search_catalog_general_query_can_match_school() -> None:
    payload = search_catalog(
        query="Scarsdale",
        audience="parent",
        districts=load_districts(),
        schools=load_schools(),
        zip_suggestions=load_zip_district_suggestions(),
    )
    assert payload["intent"] in {"general", "city"}
    assert any("Scarsdale" in school["title"] for school in payload["schools"])


def test_search_catalog_skips_zip_suggestion_when_district_missing() -> None:
    payload = search_catalog(
        query="99999",
        audience="parent",
        districts=load_districts(),
        schools=load_schools(),
        zip_suggestions=[
            ZipDistrictSuggestion(
                zip_code="99999",
                district_id="NOPE",
                likelihood_rank=1,
                why_it_matches="Synthetic test row",
            )
        ],
    )
    assert payload["intent"] == "zip"
    assert payload["district_suggestions"] == []


def test_search_catalog_general_gibberish_returns_empty() -> None:
    payload = search_catalog(
        query="zzzxxyy",
        audience="parent",
        districts=load_districts(),
        schools=load_schools(),
        zip_suggestions=load_zip_district_suggestions(),
    )
    assert payload["intent"] == "general"
    assert payload["districts"] == []
    assert payload["schools"] == []
