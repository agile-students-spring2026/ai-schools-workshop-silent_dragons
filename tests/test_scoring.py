from __future__ import annotations

import pytest

from app.models import District, Preferences
from app.scoring import clamp_0_100, district_score, normalize_weights


def sample_district() -> District:
    return District(
        district_id="AA-01",
        district_name="Alpha",
        state="AA",
        grad_rate=90,
        math_proficiency=80,
        reading_proficiency=82,
        student_teacher_ratio=15,
        teacher_salary_usd=75000,
        safety_incidents_per_1000=3,
        diversity_index=0.7,
        free_lunch_pct=30,
        special_ed_rating=8,
    )


def test_clamp_0_100_bounds() -> None:
    assert clamp_0_100(-5) == 0
    assert clamp_0_100(120) == 100
    assert clamp_0_100(55.5) == 55.5


def test_normalize_weights_returns_sum_one() -> None:
    prefs = normalize_weights(Preferences(academics_weight=1, safety_weight=1))
    total = (
        prefs.academics_weight
        + prefs.safety_weight
        + prefs.affordability_weight
        + prefs.diversity_weight
        + prefs.special_ed_weight
        + prefs.teacher_support_weight
        + prefs.class_size_weight
    )
    assert total == pytest.approx(1.0)


def test_normalize_weights_rejects_zero_sum() -> None:
    with pytest.raises(ValueError):
        normalize_weights(
            Preferences(
                academics_weight=0,
                safety_weight=0,
                affordability_weight=0,
                diversity_weight=0,
                special_ed_weight=0,
                teacher_support_weight=0,
                class_size_weight=0,
            )
        )


def test_district_score_stable_value() -> None:
    score = district_score(sample_district(), Preferences())
    assert score == pytest.approx(76.7, abs=0.01)
