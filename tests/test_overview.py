from __future__ import annotations

import pytest

from app.models import District, School
from app.overview import (
    _avg,
    _quick_flags,
    _school_matches_grade_band,
    district_overview_payload,
    school_detail_payload,
)


def sample_district() -> District:
    return District(
        district_id="D-1",
        district_name="Sample District",
        state="XY",
        grad_rate=91,
        math_proficiency=70,
        reading_proficiency=73,
        student_teacher_ratio=16,
        teacher_salary_usd=80000,
        safety_incidents_per_1000=3.5,
        diversity_index=0.7,
        free_lunch_pct=28,
        special_ed_rating=7.4,
    )


def sample_schools() -> list[School]:
    return [
        School(
            school_id="S-1",
            school_name="Sample Elementary",
            district_id="D-1",
            district_name="Sample District",
            city="One",
            state="XY",
            zip_code="12345",
            school_type="Elementary",
            grade_span="K-5",
            enrollment=500,
            charter_status="traditional",
            absenteeism_pct=7.0,
            outcomes_index=78.0,
            climate_index=80.0,
            advanced_coursework_pct=None,
        ),
        School(
            school_id="S-2",
            school_name="Sample High",
            district_id="D-1",
            district_name="Sample District",
            city="Two",
            state="XY",
            zip_code="12346",
            school_type="High",
            grade_span="9-12",
            enrollment=900,
            charter_status="charter",
            absenteeism_pct=16.0,
            outcomes_index=76.0,
            climate_index=55.0,
            advanced_coursework_pct=40.0,
        ),
    ]


def test_avg_handles_empty_and_values() -> None:
    assert _avg([]) is None
    assert _avg([None, 10.0, 20.0]) == 15.0


def test_school_matches_grade_band() -> None:
    elementary, high = sample_schools()
    assert _school_matches_grade_band(elementary, "all") is True
    assert _school_matches_grade_band(elementary, "elementary") is True
    assert _school_matches_grade_band(elementary, "middle") is False
    assert _school_matches_grade_band(high, "high") is True


def test_quick_flags_branches() -> None:
    elementary, high = sample_schools()
    assert _quick_flags(elementary) == ["Strong outcomes"]
    assert "Attendance watch" in _quick_flags(high)
    assert "Climate support needed" in _quick_flags(high)


def test_district_overview_payload_success_and_filters() -> None:
    payload = district_overview_payload(
        district_id="D-1",
        districts=[sample_district()],
        schools=sample_schools(),
        grade_band="high",
        school_type="High",
    )
    assert payload["district_name"] == "Sample District"
    assert payload["summary"]["parent"]
    assert payload["summary"]["educator"]
    assert len(payload["metrics"]) == 7
    assert len(payload["schools"]) == 1
    assert payload["schools"][0]["school_id"] == "S-2"


def test_district_overview_not_found() -> None:
    with pytest.raises(ValueError):
        district_overview_payload("NOPE", [sample_district()], sample_schools())


def test_school_detail_payload_success_and_missing_note() -> None:
    payload = school_detail_payload(
        school_id="S-1",
        districts=[sample_district()],
        schools=sample_schools(),
    )
    assert payload["school_name"] == "Sample Elementary"
    assert payload["district_context"]["district_name"] == "Sample District"
    assert len(payload["metrics"]) == 5
    assert payload["missing_notes"]
    assert payload["qa"]["what_stands_out"]["citations"]


def test_school_detail_errors() -> None:
    with pytest.raises(ValueError):
        school_detail_payload("NOPE", [sample_district()], sample_schools())

    school = sample_schools()[0]
    broken_school = School(
        school_id=school.school_id,
        school_name=school.school_name,
        district_id="MISSING",
        district_name=school.district_name,
        city=school.city,
        state=school.state,
        zip_code=school.zip_code,
        school_type=school.school_type,
        grade_span=school.grade_span,
        enrollment=school.enrollment,
        charter_status=school.charter_status,
        absenteeism_pct=school.absenteeism_pct,
        outcomes_index=school.outcomes_index,
        climate_index=school.climate_index,
        advanced_coursework_pct=school.advanced_coursework_pct,
    )
    with pytest.raises(ValueError):
        school_detail_payload("S-1", [sample_district()], [broken_school])
