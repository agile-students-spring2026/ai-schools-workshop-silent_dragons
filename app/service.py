from __future__ import annotations

from app.models import District, Preferences
from app.scoring import district_score


def matches_constraints(district: District, prefs: Preferences) -> bool:
    return (
        district.grad_rate >= prefs.min_grad_rate
        and district.student_teacher_ratio <= prefs.max_student_teacher_ratio
    )


def rank_districts(districts: list[District], prefs: Preferences, top_k: int = 10) -> list[dict]:
    eligible = [district for district in districts if matches_constraints(district, prefs)]
    scored = [
        {
            "district_id": district.district_id,
            "district_name": district.district_name,
            "state": district.state,
            "score": district_score(district, prefs),
        }
        for district in eligible
    ]
    scored.sort(key=lambda district: district["score"], reverse=True)
    return scored[:top_k]
