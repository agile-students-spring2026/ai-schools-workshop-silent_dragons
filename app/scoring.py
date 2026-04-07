from __future__ import annotations

from app.models import District, Preferences


def clamp_0_100(value: float) -> float:
    return max(0.0, min(100.0, value))


def normalize_weights(prefs: Preferences) -> Preferences:
    total = (
        prefs.academics_weight
        + prefs.safety_weight
        + prefs.affordability_weight
        + prefs.diversity_weight
        + prefs.special_ed_weight
        + prefs.teacher_support_weight
        + prefs.class_size_weight
    )
    if total <= 0:
        raise ValueError("At least one weight must be greater than zero.")

    return Preferences(
        academics_weight=prefs.academics_weight / total,
        safety_weight=prefs.safety_weight / total,
        affordability_weight=prefs.affordability_weight / total,
        diversity_weight=prefs.diversity_weight / total,
        special_ed_weight=prefs.special_ed_weight / total,
        teacher_support_weight=prefs.teacher_support_weight / total,
        class_size_weight=prefs.class_size_weight / total,
        min_grad_rate=prefs.min_grad_rate,
        max_student_teacher_ratio=prefs.max_student_teacher_ratio,
    )


def district_score(district: District, prefs: Preferences) -> float:
    p = normalize_weights(prefs)

    academics = (district.grad_rate + district.math_proficiency + district.reading_proficiency) / 3
    safety = clamp_0_100(100 - district.safety_incidents_per_1000 * 3)
    affordability = clamp_0_100(district.free_lunch_pct)
    diversity = clamp_0_100(district.diversity_index * 100)
    special_ed = clamp_0_100(district.special_ed_rating * 10)
    teacher_support = clamp_0_100((district.teacher_salary_usd - 35000) / 400)
    class_size = clamp_0_100(100 - (district.student_teacher_ratio - 10) * 4)

    score = (
        academics * p.academics_weight
        + safety * p.safety_weight
        + affordability * p.affordability_weight
        + diversity * p.diversity_weight
        + special_ed * p.special_ed_weight
        + teacher_support * p.teacher_support_weight
        + class_size * p.class_size_weight
    )
    return round(score, 2)
