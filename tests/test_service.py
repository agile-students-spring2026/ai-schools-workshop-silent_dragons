from __future__ import annotations

from app.models import District, Preferences
from app.service import matches_constraints, rank_districts


def districts() -> list[District]:
    return [
        District("A", "A District", "AA", 96, 92, 91, 12, 90000, 1.5, 0.65, 12, 8.2),
        District("B", "B District", "BB", 85, 62, 68, 19, 50000, 6.0, 0.82, 58, 7.0),
    ]


def test_matches_constraints_true_and_false() -> None:
    prefs = Preferences(min_grad_rate=90, max_student_teacher_ratio=14)
    assert matches_constraints(districts()[0], prefs) is True
    assert matches_constraints(districts()[1], prefs) is False


def test_rank_districts_sorted_and_limited() -> None:
    results = rank_districts(districts(), Preferences(), top_k=1)
    assert len(results) == 1
    assert results[0]["district_id"] == "A"
