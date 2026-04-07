from __future__ import annotations

from app.models import District, School


METRIC_SOURCES = {
    "enrollment": ("CCD (workshop sample)", 2023, "district"),
    "num_schools": ("CCD (workshop sample)", 2023, "district"),
    "poverty_context": ("SAIPE-style proxy (workshop sample)", 2023, "district"),
    "per_pupil_spending": ("F-33-style proxy (workshop sample)", 2022, "district"),
    "chronic_absenteeism": ("EDFacts (workshop sample)", 2023, "district"),
    "graduation_rate": ("EDFacts (workshop sample)", 2023, "district"),
    "climate_equity": ("CRDC-style climate index (workshop sample)", 2023, "district"),
    "school_absenteeism": ("EDFacts (workshop sample)", 2023, "school"),
    "school_outcomes": ("EDFacts (workshop sample)", 2023, "school"),
    "school_climate": ("CRDC-style climate index (workshop sample)", 2023, "school"),
    "advanced_coursework": ("EDFacts (workshop sample)", 2023, "school"),
}


def _metric(metric_key: str, label: str, value: float | int | None, unit: str = "") -> dict:
    source_name, source_year, level = METRIC_SOURCES[metric_key]
    return {
        "metric_key": metric_key,
        "label": label,
        "value": value,
        "unit": unit,
        "source_name": source_name,
        "source_year": source_year,
        "level": level,
    }


def _avg(values: list[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    if not usable:
        return None
    return round(sum(usable) / len(usable), 1)


def _school_matches_grade_band(school: School, grade_band: str) -> bool:
    if grade_band == "all":
        return True
    span = school.grade_span.upper()
    if grade_band == "elementary":
        return "K" in span or "5" in span
    if grade_band == "middle":
        return "6" in span or "7" in span or "8" in span
    return "9" in span or "10" in span or "11" in span or "12" in span


def _quick_flags(school: School) -> list[str]:
    flags: list[str] = []
    if school.absenteeism_pct is not None and school.absenteeism_pct > 15:
        flags.append("Attendance watch")
    if school.outcomes_index is not None and school.outcomes_index >= 75:
        flags.append("Strong outcomes")
    if school.climate_index is not None and school.climate_index < 60:
        flags.append("Climate support needed")
    return flags or ["Data still loading"]


def _district_summary_parent(district_name: str, metrics: dict[str, float | int | None]) -> str:
    missing = [name for name, value in metrics.items() if value is None]
    missing_text = (
        " Some data is missing and shown as unavailable."
        if missing
        else ""
    )
    return (
        f"{district_name} serves about {metrics['enrollment'] or 'unknown'} students across "
        f"{metrics['num_schools'] or 'unknown'} schools. Graduation rate is "
        f"{metrics['graduation_rate'] or 'not reported'}%, and chronic absenteeism is "
        f"{metrics['chronic_absenteeism'] or 'not reported'}%.{missing_text}"
    )


def _district_summary_educator(district_name: str, metrics: dict[str, float | int | None]) -> str:
    return (
        f"{district_name} shows a poverty context indicator of {metrics['poverty_context'] or 'unknown'}% "
        f"and estimated per-pupil spending of ${metrics['per_pupil_spending'] or 'not available'}. "
        f"Use climate and attendance metrics together when planning supports."
    )


def district_overview_payload(
    district_id: str,
    districts: list[District],
    schools: list[School],
    grade_band: str = "all",
    school_type: str = "all",
) -> dict:
    district = next((item for item in districts if item.district_id == district_id), None)
    if district is None:
        raise ValueError("District not found")

    district_schools = [school for school in schools if school.district_id == district_id]
    filtered_schools = [
        school
        for school in district_schools
        if _school_matches_grade_band(school, grade_band)
        and (school_type == "all" or school.school_type.lower() == school_type.lower())
    ]

    district_metrics_raw: dict[str, float | int | None] = {
        "enrollment": sum((school.enrollment or 0) for school in district_schools) or None,
        "num_schools": len(district_schools),
        "poverty_context": round(district.free_lunch_pct, 1),
        "per_pupil_spending": round(district.teacher_salary_usd * 1.42),
        "chronic_absenteeism": _avg([school.absenteeism_pct for school in district_schools]),
        "graduation_rate": round(district.grad_rate, 1),
        "climate_equity": _avg([school.climate_index for school in district_schools]),
    }

    schools_payload = [
        {
            "school_id": school.school_id,
            "school_name": school.school_name,
            "grade_span": school.grade_span,
            "enrollment": school.enrollment,
            "school_type": school.school_type,
            "charter_status": school.charter_status,
            "quick_flags": _quick_flags(school),
        }
        for school in filtered_schools
    ]

    unique_cities = sorted({school.city for school in district_schools})
    locale = "Urban" if len(unique_cities) >= 3 else "Suburban"

    return {
        "district_id": district.district_id,
        "district_name": district.district_name,
        "state": district.state,
        "locale": locale,
        "map_preview": {
            "title": "Map preview",
            "description": "Approximate district footprint preview based on EDGE-style geo context.",
            "focus_cities": unique_cities,
        },
        "metrics": [
            _metric("enrollment", "Enrollment", district_metrics_raw["enrollment"]),
            _metric("num_schools", "Number of schools", district_metrics_raw["num_schools"]),
            _metric("poverty_context", "Poverty context", district_metrics_raw["poverty_context"], "%"),
            _metric("per_pupil_spending", "Per-pupil spending", district_metrics_raw["per_pupil_spending"], "$"),
            _metric("chronic_absenteeism", "Chronic absenteeism", district_metrics_raw["chronic_absenteeism"], "%"),
            _metric("graduation_rate", "Graduation rate", district_metrics_raw["graduation_rate"], "%"),
            _metric("climate_equity", "Climate and equity index", district_metrics_raw["climate_equity"], "/100"),
        ],
        "schools": schools_payload,
        "filters": {
            "grade_band": grade_band,
            "school_type": school_type,
        },
        "summary": {
            "parent": _district_summary_parent(district.district_name, district_metrics_raw),
            "educator": _district_summary_educator(district.district_name, district_metrics_raw),
        },
    }


def school_detail_payload(school_id: str, districts: list[District], schools: list[School]) -> dict:
    school = next((item for item in schools if item.school_id == school_id), None)
    if school is None:
        raise ValueError("School not found")
    district = next((item for item in districts if item.district_id == school.district_id), None)
    if district is None:
        raise ValueError("District not found")

    district_context = {
        "district_name": district.district_name,
        "poverty_context": round(district.free_lunch_pct, 1),
        "per_pupil_spending": round(district.teacher_salary_usd * 1.42),
        "graduation_rate": round(district.grad_rate, 1),
    }

    missing_notes = []
    if school.advanced_coursework_pct is None:
        missing_notes.append("Advanced coursework access is currently unavailable.")

    return {
        "school_id": school.school_id,
        "school_name": school.school_name,
        "district_id": school.district_id,
        "district_name": school.district_name,
        "city": school.city,
        "state": school.state,
        "grade_span": school.grade_span,
        "school_type": school.school_type,
        "charter_status": school.charter_status,
        "metrics": [
            _metric("enrollment", "Enrollment", school.enrollment),
            _metric("school_absenteeism", "Absenteeism", school.absenteeism_pct, "%"),
            _metric("school_outcomes", "Outcomes index", school.outcomes_index, "/100"),
            _metric("school_climate", "Climate index", school.climate_index, "/100"),
            _metric("advanced_coursework", "Advanced coursework access", school.advanced_coursework_pct, "%"),
        ],
        "district_context": district_context,
        "fit_explanations": {
            "parent": (
                f"{school.school_name} serves grades {school.grade_span}. Review attendance, climate, "
                "and advanced coursework together for day-to-day student fit."
            ),
            "educator": (
                f"Use {school.school_name} attendance and climate trends with district poverty and "
                "funding context when planning supports."
            ),
        },
        "qa": {
            "what_stands_out": {
                "answer": "Attendance, outcomes, and climate are the top comparison anchors shown on this page.",
                "citations": ["school_absenteeism", "school_outcomes", "school_climate"],
            },
            "what_concerns": {
                "answer": "Focus on higher absenteeism and low climate scores where shown.",
                "citations": ["school_absenteeism", "school_climate"],
            },
            "compare_to_district": {
                "answer": "The district context section gives graduation, poverty, and spending benchmarks.",
                "citations": ["graduation_rate", "poverty_context", "per_pupil_spending"],
            },
        },
        "missing_notes": missing_notes,
    }
