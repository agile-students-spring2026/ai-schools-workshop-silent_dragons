from __future__ import annotations

from app.models import District, DistrictGeography, School


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

PARENT_LABELS = {
    "enrollment": "Students enrolled",
    "num_schools": "Schools in district",
    "poverty_context": "Students needing financial support",
    "per_pupil_spending": "Estimated spending per student",
    "chronic_absenteeism": "Students missing many school days",
    "graduation_rate": "Students graduating",
    "climate_equity": "School environment support score",
    "school_absenteeism": "Students missing many school days",
    "school_outcomes": "Academic outcomes snapshot",
    "school_climate": "School climate and belonging",
    "advanced_coursework": "Access to advanced classes",
}


def _metric(
    metric_key: str,
    label: str,
    value: float | int | None,
    unit: str = "",
    audience: str = "educator",
) -> dict:
    source_name, source_year, level = METRIC_SOURCES[metric_key]
    effective_label = PARENT_LABELS.get(metric_key, label) if audience == "parent" else label
    return {
        "metric_key": metric_key,
        "label": effective_label,
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


def _quick_flags(school: School, audience: str) -> list[str]:
    flags: list[str] = []
    if school.absenteeism_pct is not None and school.absenteeism_pct > 15:
        flags.append("Attendance concern" if audience == "parent" else "Chronic absenteeism > 15%")
    if school.outcomes_index is not None and school.outcomes_index >= 75:
        flags.append("Strong outcomes")
    if school.climate_index is not None and school.climate_index < 60:
        flags.append("Climate concern" if audience == "parent" else "Climate index < 60")
    return flags or ["Data still loading"]


def _audience_objective(audience: str) -> str:
    if audience == "parent":
        return "Parent mode helps families compare day-to-day experience, support, and fit."
    return "Educator mode helps staff compare student-need context, resource pressure, and intervention signals."


def _district_summary_parent(district_name: str, metrics: dict[str, float | int | None]) -> str:
    missing = [name for name, value in metrics.items() if value is None]
    missing_text = (
        " Some data is missing and shown as unavailable."
        if missing
        else ""
    )
    return (
        f"{district_name} serves about {metrics['enrollment'] or 'unknown'} students across "
        f"{metrics['num_schools'] or 'unknown'} schools. For a family decision, start with graduation "
        f"({metrics['graduation_rate'] or 'not reported'}%), attendance stability "
        f"({metrics['chronic_absenteeism'] or 'not reported'}% chronic absenteeism), and school climate."
        f"{missing_text}"
    )


def _district_summary_educator(district_name: str, metrics: dict[str, float | int | None]) -> str:
    return (
        f"{district_name} shows a poverty context indicator of {metrics['poverty_context'] or 'unknown'}% "
        f"with estimated per-pupil spending of ${metrics['per_pupil_spending'] or 'not available'}. "
        f"For educator planning, prioritize attendance ({metrics['chronic_absenteeism'] or 'not reported'}%), "
        f"climate/equity index ({metrics['climate_equity'] or 'not reported'}), and resource alignment."
    )


def _map_preview_payload(geo: DistrictGeography | None, focus_cities: list[str]) -> dict:
    if geo is None:
        return {
            "title": "Map preview",
            "description": "District map coordinates are not available yet for this district.",
            "focus_cities": focus_cities,
            "embed_url": None,
            "source_name": "Unavailable",
            "source_year": None,
        }

    bbox = f"{geo.min_lon}%2C{geo.min_lat}%2C{geo.max_lon}%2C{geo.max_lat}"
    marker = f"{geo.center_lat}%2C{geo.center_lon}"
    embed_url = (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={bbox}&layer=mapnik&marker={marker}"
    )
    return {
        "title": "Map preview",
        "description": "Approximate district footprint preview from EDGE-style geocode context.",
        "focus_cities": focus_cities,
        "embed_url": embed_url,
        "source_name": geo.source_name,
        "source_year": geo.source_year,
    }


def district_overview_payload(
    district_id: str,
    districts: list[District],
    schools: list[School],
    geographies: list[DistrictGeography],
    audience: str = "parent",
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
            "quick_flags": _quick_flags(school, audience),
        }
        for school in filtered_schools
    ]

    unique_cities = sorted({school.city for school in district_schools})
    locale = "Urban" if len(unique_cities) >= 3 else "Suburban"
    geo = next((item for item in geographies if item.district_id == district_id), None)

    return {
        "district_id": district.district_id,
        "district_name": district.district_name,
        "state": district.state,
        "locale": locale,
        "map_preview": _map_preview_payload(geo, unique_cities),
        "metrics": [
            _metric("enrollment", "Enrollment", district_metrics_raw["enrollment"], audience=audience),
            _metric("num_schools", "Number of schools", district_metrics_raw["num_schools"], audience=audience),
            _metric("poverty_context", "Poverty context", district_metrics_raw["poverty_context"], "%", audience=audience),
            _metric("per_pupil_spending", "Per-pupil spending", district_metrics_raw["per_pupil_spending"], "$", audience=audience),
            _metric("chronic_absenteeism", "Chronic absenteeism", district_metrics_raw["chronic_absenteeism"], "%", audience=audience),
            _metric("graduation_rate", "Graduation rate", district_metrics_raw["graduation_rate"], "%", audience=audience),
            _metric("climate_equity", "Climate and equity index", district_metrics_raw["climate_equity"], "/100", audience=audience),
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
        "active_summary": (
            _district_summary_parent(district.district_name, district_metrics_raw)
            if audience == "parent"
            else _district_summary_educator(district.district_name, district_metrics_raw)
        ),
        "audience": audience,
        "audience_objective": _audience_objective(audience),
        "audience_differences": {
            "parent": "Prioritizes student experience, attendance, and day-to-day family fit.",
            "educator": "Prioritizes student need context, resource planning, and climate supports.",
        },
    }


def school_detail_payload(
    school_id: str,
    districts: list[District],
    schools: list[School],
    audience: str = "parent",
) -> dict:
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
            _metric("enrollment", "Enrollment", school.enrollment, audience=audience),
            _metric("school_absenteeism", "Absenteeism", school.absenteeism_pct, "%", audience=audience),
            _metric("school_outcomes", "Outcomes index", school.outcomes_index, "/100", audience=audience),
            _metric("school_climate", "Climate index", school.climate_index, "/100", audience=audience),
            _metric("advanced_coursework", "Advanced coursework access", school.advanced_coursework_pct, "%", audience=audience),
        ],
        "district_context": district_context,
        "fit_explanations": {
            "parent": (
                f"{school.school_name} serves grades {school.grade_span}. For families, check attendance "
                "stability, climate indicators, and course access to judge everyday fit and support level."
            ),
            "educator": (
                f"For educators, combine {school.school_name} attendance and climate trends with district "
                "poverty and spending context to target interventions and program supports."
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
        "audience": audience,
        "audience_objective": _audience_objective(audience),
    }
