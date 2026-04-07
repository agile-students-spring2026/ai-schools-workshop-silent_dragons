from __future__ import annotations

import csv
from pathlib import Path

from app.models import District, DistrictGeography, School, ZipDistrictSuggestion


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "districts.csv"
SCHOOLS_PATH = Path(__file__).resolve().parent.parent / "data" / "schools.csv"
ZIP_SUGGESTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "zip_districts.csv"
DISTRICT_GEOGRAPHY_PATH = Path(__file__).resolve().parent.parent / "data" / "district_geography.csv"


def load_districts(path: Path = DATA_PATH) -> list[District]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [to_district(row) for row in rows]


def to_district(row: dict[str, str]) -> District:
    return District(
        district_id=row["district_id"],
        district_name=row["district_name"],
        state=row["state"],
        grad_rate=float(row["grad_rate"]),
        math_proficiency=float(row["math_proficiency"]),
        reading_proficiency=float(row["reading_proficiency"]),
        student_teacher_ratio=float(row["student_teacher_ratio"]),
        teacher_salary_usd=float(row["teacher_salary_usd"]),
        safety_incidents_per_1000=float(row["safety_incidents_per_1000"]),
        diversity_index=float(row["diversity_index"]),
        free_lunch_pct=float(row["free_lunch_pct"]),
        special_ed_rating=float(row["special_ed_rating"]),
    )


def load_schools(path: Path = SCHOOLS_PATH) -> list[School]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [to_school(row) for row in rows]


def to_school(row: dict[str, str]) -> School:
    enrollment_raw = row.get("enrollment", "").strip()
    absenteeism_raw = row.get("absenteeism_pct", "").strip()
    outcomes_raw = row.get("outcomes_index", "").strip()
    climate_raw = row.get("climate_index", "").strip()
    advanced_raw = row.get("advanced_coursework_pct", "").strip()
    return School(
        school_id=row["school_id"],
        school_name=row["school_name"],
        district_id=row["district_id"],
        district_name=row["district_name"],
        city=row["city"],
        state=row["state"],
        zip_code=row["zip_code"],
        school_type=row["school_type"],
        grade_span=row.get("grade_span", "Unknown"),
        enrollment=int(enrollment_raw) if enrollment_raw else None,
        charter_status=row.get("charter_status", "traditional"),
        absenteeism_pct=float(absenteeism_raw) if absenteeism_raw else None,
        outcomes_index=float(outcomes_raw) if outcomes_raw else None,
        climate_index=float(climate_raw) if climate_raw else None,
        advanced_coursework_pct=float(advanced_raw) if advanced_raw else None,
    )


def load_zip_district_suggestions(path: Path = ZIP_SUGGESTIONS_PATH) -> list[ZipDistrictSuggestion]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [to_zip_district_suggestion(row) for row in rows]


def to_zip_district_suggestion(row: dict[str, str]) -> ZipDistrictSuggestion:
    source_year_raw = row.get("source_year", "").strip()
    return ZipDistrictSuggestion(
        zip_code=row["zip_code"],
        district_id=row["district_id"],
        likelihood_rank=int(row["likelihood_rank"]),
        why_it_matches=row["why_it_matches"],
        source_name=row.get("source_name", "Unknown source"),
        source_year=int(source_year_raw) if source_year_raw else None,
    )


def load_district_geography(path: Path = DISTRICT_GEOGRAPHY_PATH) -> list[DistrictGeography]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [to_district_geography(row) for row in rows]


def to_district_geography(row: dict[str, str]) -> DistrictGeography:
    source_year_raw = row.get("source_year", "").strip()
    return DistrictGeography(
        district_id=row["district_id"],
        center_lat=float(row["center_lat"]),
        center_lon=float(row["center_lon"]),
        min_lat=float(row["min_lat"]),
        max_lat=float(row["max_lat"]),
        min_lon=float(row["min_lon"]),
        max_lon=float(row["max_lon"]),
        source_name=row.get("source_name", "Unknown source"),
        source_year=int(source_year_raw) if source_year_raw else None,
    )
