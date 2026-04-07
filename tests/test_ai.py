from __future__ import annotations

from app.ai import (
    classify_search_intent,
    extract_zip_code,
    fuzzy_match,
    interpret_fuzzy_query,
    to_plain_language_label,
)


def test_classify_search_intent_for_zip_and_school_and_district() -> None:
    assert classify_search_intent("good schools near 10027") == "zip"
    assert classify_search_intent("Scarsdale High School") == "school"
    assert classify_search_intent("Palo Alto Unified district") == "district"


def test_classify_search_intent_for_city_and_general() -> None:
    assert classify_search_intent("Orlando", {"Orlando", "Austin"}) == "city"
    assert classify_search_intent("") == "general"


def test_extract_zip_code() -> None:
    assert extract_zip_code("near 10027") == "10027"
    assert extract_zip_code("no zip here") is None


def test_interpret_fuzzy_query() -> None:
    assert interpret_fuzzy_query("good schools near 10027") == "10027"
    assert interpret_fuzzy_query("best district in orlando please") == "in orlando"


def test_fuzzy_match_exact_and_fuzzy_and_empty() -> None:
    assert fuzzy_match("Scarsdale High School", "scarsdale") is True
    assert fuzzy_match("Princeton Public Schools", "princton public schools", threshold=0.5) is True
    assert fuzzy_match("Princeton Public Schools", "") is False


def test_fuzzy_match_can_fail_ratio_threshold() -> None:
    assert fuzzy_match("Princeton Public Schools", "xyzxyz", threshold=0.9) is False


def test_fuzzy_match_short_query_without_hit_returns_false() -> None:
    assert fuzzy_match("Princeton Public Schools", "zzzz") is False


def test_fuzzy_match_ratio_fallback_can_pass_with_low_threshold() -> None:
    assert fuzzy_match("Princeton Public Schools", "zzzzzzzz", threshold=0.0) is True


def test_fuzzy_match_substring_branch_for_short_query() -> None:
    assert fuzzy_match("Palo Alto Unified", "pa") is True


def test_to_plain_language_label() -> None:
    assert to_plain_language_label("student_teacher_ratio") == "Average class size"
    assert to_plain_language_label("custom_metric") == "Custom Metric"
