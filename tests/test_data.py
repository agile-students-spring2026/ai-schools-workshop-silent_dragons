from __future__ import annotations

from pathlib import Path

from app.data import (
    load_districts,
    load_schools,
    load_zip_district_suggestions,
    to_district,
    to_school,
    to_zip_district_suggestion,
)


def test_to_district_casts_fields() -> None:
    district = to_district(
        {
            "district_id": "XX-1",
            "district_name": "Test District",
            "state": "XX",
            "grad_rate": "90",
            "math_proficiency": "70",
            "reading_proficiency": "71",
            "student_teacher_ratio": "15",
            "teacher_salary_usd": "60000",
            "safety_incidents_per_1000": "3.3",
            "diversity_index": "0.5",
            "free_lunch_pct": "40",
            "special_ed_rating": "7.5",
        }
    )
    assert district.district_name == "Test District"
    assert district.teacher_salary_usd == 60000.0


def test_load_districts_reads_csv(tmp_path: Path) -> None:
    file = tmp_path / "districts.csv"
    file.write_text(
        "district_id,district_name,state,grad_rate,math_proficiency,reading_proficiency,"
        "student_teacher_ratio,teacher_salary_usd,safety_incidents_per_1000,"
        "diversity_index,free_lunch_pct,special_ed_rating\n"
        "YY-2,Sample,YY,88,66,70,16,50000,4.1,0.66,44,7.0\n",
        encoding="utf-8",
    )
    districts = load_districts(file)
    assert len(districts) == 1
    assert districts[0].district_id == "YY-2"


def test_to_school_casts_fields() -> None:
    school = to_school(
        {
            "school_id": "SCH-1",
            "school_name": "Sample High",
            "district_id": "YY-2",
            "district_name": "Sample",
            "city": "Example City",
            "state": "YY",
            "zip_code": "12345",
            "school_type": "High",
        }
    )
    assert school.school_name == "Sample High"
    assert school.zip_code == "12345"


def test_load_schools_reads_csv(tmp_path: Path) -> None:
    file = tmp_path / "schools.csv"
    file.write_text(
        "school_id,school_name,district_id,district_name,city,state,zip_code,school_type\n"
        "SCH-2,School Name,YY-2,Sample District,Sample City,YY,12345,Middle\n",
        encoding="utf-8",
    )
    schools = load_schools(file)
    assert len(schools) == 1
    assert schools[0].district_id == "YY-2"


def test_to_zip_district_suggestion_casts_fields() -> None:
    item = to_zip_district_suggestion(
        {
            "zip_code": "12345",
            "district_id": "YY-2",
            "likelihood_rank": "2",
            "why_it_matches": "Nearby communities often compare this district.",
            "source_name": "NCES GRF",
            "source_year": "2023",
        }
    )
    assert item.zip_code == "12345"
    assert item.likelihood_rank == 2
    assert item.source_name == "NCES GRF"
    assert item.source_year == 2023


def test_load_zip_district_suggestions_reads_csv(tmp_path: Path) -> None:
    file = tmp_path / "zip_districts.csv"
    file.write_text(
        "zip_code,district_id,likelihood_rank,why_it_matches,source_name,source_year\n"
        "12345,YY-2,1,Strong local fit,NCES GRF,2023\n",
        encoding="utf-8",
    )
    suggestions = load_zip_district_suggestions(file)
    assert len(suggestions) == 1
    assert suggestions[0].district_id == "YY-2"
    assert suggestions[0].source_name == "NCES GRF"
