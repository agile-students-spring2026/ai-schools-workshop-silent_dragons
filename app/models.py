from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class District:
    district_id: str
    district_name: str
    state: str
    grad_rate: float
    math_proficiency: float
    reading_proficiency: float
    student_teacher_ratio: float
    teacher_salary_usd: float
    safety_incidents_per_1000: float
    diversity_index: float
    free_lunch_pct: float
    special_ed_rating: float


@dataclass(frozen=True)
class Preferences:
    academics_weight: float = 0.25
    safety_weight: float = 0.2
    affordability_weight: float = 0.15
    diversity_weight: float = 0.1
    special_ed_weight: float = 0.15
    teacher_support_weight: float = 0.1
    class_size_weight: float = 0.05
    min_grad_rate: float = 0.0
    max_student_teacher_ratio: float = 100.0


@dataclass(frozen=True)
class School:
    school_id: str
    school_name: str
    district_id: str
    district_name: str
    city: str
    state: str
    zip_code: str
    school_type: str


@dataclass(frozen=True)
class ZipDistrictSuggestion:
    zip_code: str
    district_id: str
    likelihood_rank: int
    why_it_matches: str
    source_name: str = "Unknown source"
    source_year: int | None = None
