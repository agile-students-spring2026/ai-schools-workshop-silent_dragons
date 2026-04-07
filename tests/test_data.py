from __future__ import annotations

from pathlib import Path

from app.data import (
    load_districts,
    load_district_geography,
    load_schools,
    load_zip_district_suggestions,
    to_district,
    to_district_geography,
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
            "grade_span": "9-12",
            "enrollment": "1200",
            "charter_status": "traditional",
            "absenteeism_pct": "11.2",
            "outcomes_index": "74",
            "climate_index": "69",
            "advanced_coursework_pct": "47",
        }
    )
    assert school.school_name == "Sample High"
    assert school.zip_code == "12345"
    assert school.grade_span == "9-12"
    assert school.enrollment == 1200


def test_load_schools_reads_csv(tmp_path: Path) -> None:
    file = tmp_path / "schools.csv"
    file.write_text(
        "school_id,school_name,district_id,district_name,city,state,zip_code,school_type,"
        "grade_span,enrollment,charter_status,absenteeism_pct,outcomes_index,climate_index,advanced_coursework_pct\n"
        "SCH-2,School Name,YY-2,Sample District,Sample City,YY,12345,Middle,6-8,700,traditional,9.2,71,66,40\n",
        encoding="utf-8",
    )
    schools = load_schools(file)
    assert len(schools) == 1
    assert schools[0].district_id == "YY-2"
    assert schools[0].enrollment == 700


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


def test_to_district_geography_casts_fields() -> None:
    item = to_district_geography(
        {
            "district_id": "YY-2",
            "center_lat": "40.1",
            "center_lon": "-75.2",
            "min_lat": "39.9",
            "max_lat": "40.3",
            "min_lon": "-75.4",
            "max_lon": "-75.0",
            "source_name": "EDGE",
            "source_year": "2023",
        }
    )
    assert item.district_id == "YY-2"
    assert item.source_name == "EDGE"
    assert item.source_year == 2023


def test_load_district_geography_reads_csv(tmp_path: Path) -> None:
    file = tmp_path / "district_geography.csv"
    file.write_text(
        "district_id,center_lat,center_lon,min_lat,max_lat,min_lon,max_lon,source_name,source_year\n"
        "YY-2,40.1,-75.2,39.9,40.3,-75.4,-75.0,EDGE,2023\n",
        encoding="utf-8",
    )
    items = load_district_geography(file)
    assert len(items) == 1
    assert items[0].district_id == "YY-2"
