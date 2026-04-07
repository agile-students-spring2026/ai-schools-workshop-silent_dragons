from __future__ import annotations

from pathlib import Path

from app.data import load_districts, to_district


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
