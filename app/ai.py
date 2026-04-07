from __future__ import annotations

import re
from difflib import SequenceMatcher


ZIP_PATTERN = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
FILLER_WORDS = {
    "best",
    "good",
    "great",
    "top",
    "near",
    "nearby",
    "around",
    "schools",
    "school",
    "district",
    "districts",
    "for",
    "me",
    "please",
    "find",
}


def classify_search_intent(query: str, known_cities: set[str] | None = None) -> str:
    lowered = query.lower().strip()
    if not lowered:
        return "general"
    if ZIP_PATTERN.search(lowered):
        return "zip"
    if any(word in lowered for word in ["elementary", "middle", "high school"]):
        return "school"
    if "district" in lowered or "isd" in lowered:
        return "district"
    if known_cities and lowered in {city.lower() for city in known_cities}:
        return "city"
    return "general"


def extract_zip_code(query: str) -> str | None:
    match = ZIP_PATTERN.search(query)
    if not match:
        return None
    return match.group(1)


def interpret_fuzzy_query(query: str) -> str:
    lowered = query.lower().strip()
    zip_match = extract_zip_code(lowered)
    if zip_match:
        return zip_match

    tokens = [token for token in re.split(r"\W+", lowered) if token]
    meaningful = [token for token in tokens if token not in FILLER_WORDS]
    return " ".join(meaningful) or lowered


def fuzzy_match(text: str, query: str, threshold: float = 0.72) -> bool:
    text_l = text.lower()
    query_l = query.lower().strip()
    if not query_l:
        return False

    query_tokens = [token for token in re.split(r"\W+", query_l) if len(token) >= 3]
    if query_tokens and any(token in text_l for token in query_tokens):
        return True

    if query_l in text_l:
        return True

    if len(query_l) < 5:
        return False
    return SequenceMatcher(None, text_l, query_l).ratio() >= threshold


def to_plain_language_label(metric_name: str) -> str:
    mapping = {
        "grad_rate": "Graduation success",
        "math_proficiency": "Math performance",
        "reading_proficiency": "Reading performance",
        "student_teacher_ratio": "Average class size",
        "safety_incidents_per_1000": "Safety incidents",
        "special_ed_rating": "Special education support",
    }
    return mapping.get(metric_name, metric_name.replace("_", " ").title())
