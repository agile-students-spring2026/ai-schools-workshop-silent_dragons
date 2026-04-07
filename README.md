## District Insight

District Insight is a FastAPI service and web app that helps parents and educators evaluate US school districts using transparent, publicly-available-style metrics.

The current app shell supports:

- audience entry path selection (**Parent** or **Educator**)
- search by ZIP, city, district name, or school name
- likely district suggestions for ZIP searches (instead of a single guaranteed assignment)
- separate district and school result cards with plain-language summaries

- graduation and proficiency performance
- safety signals
- affordability proxy (free lunch share)
- diversity
- special education support
- teacher pay and class size

The API returns ranked district recommendations based on customizable priorities and constraints.

## Data provenance (current workshop state)

- `data/districts.csv`: workshop sample district metrics (modeled after common public education indicators).
- `data/schools.csv`: workshop sample school directory records linked to district IDs.
- `data/zip_districts.csv`: workshop sample ZIP-to-likely-district mapping with explicit `source_name` and `source_year` columns.

Important: ZIP matches are shown as likely options, not guaranteed attendance assignments.

## Quickstart

### Prerequisites

- Python 3.11+

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run the API + web app

```bash
uvicorn app.main:app --reload
```

Service URL: `http://127.0.0.1:8000`
Web UI: `http://127.0.0.1:8000/`
API docs: `http://127.0.0.1:8000/docs`

## API Endpoints

- `GET /health`
- `GET /search`
  - Query params: `query`, `audience` (`parent` or `educator`)
- `GET /districts`
  - Query params include `top_k`, all weight params, `min_grad_rate`, `max_student_teacher_ratio`
- `GET /districts/{district_id}/score`

Example:

```bash
curl "http://127.0.0.1:8000/search?query=10027&audience=parent"
```

```bash
curl "http://127.0.0.1:8000/districts?top_k=5&min_grad_rate=90&safety_weight=0.3"
```

## Testing and Coverage

Run the full test suite with coverage gate at 100%:

```bash
pytest
```

## Build and Deploy

Container build:

```bash
docker build -t district-insight:latest .
docker run --rm -p 8000:8000 district-insight:latest
```

This image can be deployed to any OCI-compatible host (for example, Render, Fly.io, GCP Cloud Run, or AWS App Runner).
