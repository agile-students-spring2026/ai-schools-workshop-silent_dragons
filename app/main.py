from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.data import (
    load_district_geography,
    load_districts,
    load_schools,
    load_zip_district_suggestions,
)
from app.models import Preferences
from app.overview import district_overview_payload, school_detail_payload
from app.search import search_catalog
from app.service import rank_districts

app = FastAPI(title="District Insight API", version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def homepage() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/district/{district_id}")
def district_page(district_id: str) -> FileResponse:
    _ = district_id
    return FileResponse(STATIC_DIR / "district.html")


@app.get("/school/{school_id}")
def school_page(school_id: str) -> FileResponse:
    _ = school_id
    return FileResponse(STATIC_DIR / "school.html")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/districts")
def get_ranked_districts(
    top_k: int = Query(default=10, ge=1, le=50),
    academics_weight: float = 0.25,
    safety_weight: float = 0.2,
    affordability_weight: float = 0.15,
    diversity_weight: float = 0.1,
    special_ed_weight: float = 0.15,
    teacher_support_weight: float = 0.1,
    class_size_weight: float = 0.05,
    min_grad_rate: float = Query(default=0.0, ge=0.0, le=100.0),
    max_student_teacher_ratio: float = Query(default=100.0, ge=1.0, le=100.0),
) -> dict:
    prefs = Preferences(
        academics_weight=academics_weight,
        safety_weight=safety_weight,
        affordability_weight=affordability_weight,
        diversity_weight=diversity_weight,
        special_ed_weight=special_ed_weight,
        teacher_support_weight=teacher_support_weight,
        class_size_weight=class_size_weight,
        min_grad_rate=min_grad_rate,
        max_student_teacher_ratio=max_student_teacher_ratio,
    )
    districts = load_districts()
    return {"results": rank_districts(districts, prefs, top_k=top_k)}


@app.get("/districts/{district_id}/score")
def get_district_score(district_id: str) -> dict:
    districts = load_districts()
    matches = [district for district in districts if district.district_id == district_id]
    if not matches:
        raise HTTPException(status_code=404, detail="District not found")

    return {
        "district_id": matches[0].district_id,
        "district_name": matches[0].district_name,
        "state": matches[0].state,
        "score": rank_districts([matches[0]], Preferences(), top_k=1)[0]["score"],
    }


@app.get("/search")
def search(
    query: str = Query(min_length=2),
    audience: str = Query(default="parent", pattern="^(parent|educator)$"),
) -> dict:
    districts = load_districts()
    schools = load_schools()
    zip_suggestions = load_zip_district_suggestions()
    return search_catalog(
        query=query,
        audience=audience,
        districts=districts,
        schools=schools,
        zip_suggestions=zip_suggestions,
    )


@app.get("/districts/{district_id}/overview")
def district_overview(
    district_id: str,
    audience: str = Query(default="parent", pattern="^(parent|educator)$"),
    grade_band: str = Query(default="all", pattern="^(all|elementary|middle|high)$"),
    school_type: str = Query(default="all", pattern="^(all|Elementary|Middle|High|Career)$"),
) -> dict:
    try:
        return district_overview_payload(
            district_id=district_id,
            districts=load_districts(),
            schools=load_schools(),
            geographies=load_district_geography(),
            audience=audience,
            grade_band=grade_band,
            school_type=school_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/schools/{school_id}/detail")
def school_detail(
    school_id: str,
    audience: str = Query(default="parent", pattern="^(parent|educator)$"),
) -> dict:
    try:
        return school_detail_payload(
            school_id=school_id,
            districts=load_districts(),
            schools=load_schools(),
            audience=audience,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
