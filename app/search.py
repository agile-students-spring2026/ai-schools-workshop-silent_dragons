from __future__ import annotations

from app.ai import (
    classify_search_intent,
    extract_zip_code,
    fuzzy_match,
    interpret_fuzzy_query,
    to_plain_language_label,
)
from app.models import District, School, ZipDistrictSuggestion


def _district_cities(schools: list[School]) -> dict[str, set[str]]:
    cities: dict[str, set[str]] = {}
    for school in schools:
        cities.setdefault(school.district_id, set()).add(school.city)
    return cities


def _district_card(district: District, cities: set[str], audience: str) -> dict:
    city_text = ", ".join(sorted(cities)) if cities else "Multiple communities"
    if audience == "parent":
        summary = (
            f"Family view: graduation is {district.grad_rate:.0f}%, class size is about "
            f"{district.student_teacher_ratio:.0f}:1, and safety incidents are {district.safety_incidents_per_1000:.1f} per 1,000 students."
        )
        focus = ["Student experience", "Daily attendance", "Safety and support"]
    else:
        summary = (
            f"Educator view: poverty context is {district.free_lunch_pct:.0f}%, diversity index is "
            f"{district.diversity_index:.2f}, and special-ed support rating is {district.special_ed_rating:.1f}/10."
        )
        focus = ["Student need context", "Resource planning", "Instructional climate"]

    return {
        "district_id": district.district_id,
        "title": district.district_name,
        "subtitle": f"{district.state} • Serves {city_text}",
        "summary": summary,
        "focus_for": focus,
        "plain_language_metrics": [
            to_plain_language_label("grad_rate"),
            to_plain_language_label("student_teacher_ratio"),
            to_plain_language_label("special_ed_rating"),
        ],
    }


def _school_card(school: School, audience: str) -> dict:
    if audience == "parent":
        summary = (
            "Family view: this card emphasizes attendance, climate, and grade-span fit to support day-to-day decision making."
        )
    else:
        summary = (
            "Educator view: this card emphasizes student-need, outcomes, and climate signals for planning supports."
        )

    return {
        "school_id": school.school_id,
        "title": school.school_name,
        "subtitle": (
            f"{school.school_type} • {school.city}, {school.state} {school.zip_code}"
        ),
        "district_id": school.district_id,
        "district_name": school.district_name,
        "summary": summary,
    }


def _zip_suggestions(
    zip_code: str,
    suggestions: list[ZipDistrictSuggestion],
    districts_by_id: dict[str, District],
) -> list[dict]:
    results = [item for item in suggestions if item.zip_code == zip_code]
    results.sort(key=lambda item: item.likelihood_rank)
    payload: list[dict] = []
    for item in results:
        district = districts_by_id.get(item.district_id)
        if not district:
            continue
        payload.append(
            {
                "district_id": district.district_id,
                "district_name": district.district_name,
                "state": district.state,
                "likelihood_rank": item.likelihood_rank,
                "why_it_matches": item.why_it_matches,
                "source_name": item.source_name,
                "source_year": item.source_year,
            }
        )
    return payload


def _helper_text(intent: str, audience: str) -> str:
    persona = "families" if audience == "parent" else "educators"
    messages = {
        "zip": (
            "ZIP searches return likely district options, because attendance zones and choice "
            "patterns can overlap."
        ),
        "school": "Showing schools first, with linked district context for easy comparison.",
        "district": "Showing district-level matches with plain-language summaries.",
        "city": "Showing schools and districts connected to the city you entered.",
        "general": "Showing best matches based on your text. Try adding a ZIP or school name.",
    }
    return f"Built for {persona}. {messages.get(intent, messages['general'])}"


def search_catalog(
    query: str,
    audience: str,
    districts: list[District],
    schools: list[School],
    zip_suggestions: list[ZipDistrictSuggestion],
) -> dict:
    interpreted_query = interpret_fuzzy_query(query)
    known_cities = {school.city for school in schools}
    intent = classify_search_intent(query, known_cities)

    districts_by_id = {district.district_id: district for district in districts}
    district_city_index = _district_cities(schools)

    zip_code = extract_zip_code(query)
    suggestion_cards = _zip_suggestions(zip_code, zip_suggestions, districts_by_id) if zip_code else []

    district_cards: list[dict] = []
    school_cards: list[dict] = []

    district_term = interpreted_query if intent != "zip" else ""
    school_term = interpreted_query if intent != "zip" else ""

    for district in districts:
        cities = district_city_index.get(district.district_id, set())
        city_blob = " ".join(cities)
        if intent in {"district", "general", "city"} and (
            fuzzy_match(district.district_name, district_term)
            or fuzzy_match(city_blob, district_term)
        ):
            district_cards.append(_district_card(district, cities, audience))

    for school in schools:
        searchable = f"{school.school_name} {school.city} {school.district_name}"
        if intent in {"school", "general", "city", "district"} and fuzzy_match(searchable, school_term):
            school_cards.append(_school_card(school, audience))

    if intent == "zip" and suggestion_cards:
        zip_district_ids = {item["district_id"] for item in suggestion_cards}
        district_cards = [
            _district_card(districts_by_id[district_id], district_city_index.get(district_id, set()), audience)
            for district_id in zip_district_ids
            if district_id in districts_by_id
        ]
        school_cards = [
            _school_card(school, audience) for school in schools if school.district_id in zip_district_ids
        ]

    if intent == "zip" and not suggestion_cards:
        helper_text = (
            "Built for families. We could not find ZIP-linked district suggestions for this code yet. "
            "Try a nearby ZIP, city, district, or school name."
            if audience == "parent"
            else "Built for educators. We could not find ZIP-linked district suggestions for this code yet. "
            "Try a nearby ZIP, city, district, or school name."
        )
    else:
        helper_text = _helper_text(intent, audience)

    return {
        "audience": audience,
        "query": query,
        "interpreted_query": interpreted_query,
        "intent": intent,
        "helper_text": helper_text,
        "district_suggestions": suggestion_cards,
        "districts": district_cards[:8],
        "schools": school_cards[:10],
    }
