from __future__ import annotations

import csv
from pathlib import Path

from app.models import District


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "districts.csv"


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
