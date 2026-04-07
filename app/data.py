from __future__ import annotations

import csv
from pathlib import Path

from app.models import District, School, ZipDistrictSuggestion


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "districts.csv"
SCHOOLS_PATH = Path(__file__).resolve().parent.parent / "data" / "schools.csv"
ZIP_SUGGESTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "zip_districts.csv"


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
    return School(
        school_id=row["school_id"],
        school_name=row["school_name"],
        district_id=row["district_id"],
        district_name=row["district_name"],
        city=row["city"],
        state=row["state"],
        zip_code=row["zip_code"],
        school_type=row["school_type"],
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
