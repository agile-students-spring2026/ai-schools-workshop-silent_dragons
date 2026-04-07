## District Insight

District Insight is a FastAPI service and web app that helps parents and educators evaluate US school districts using transparent, publicly-available-style metrics:

- graduation and proficiency performance
- safety signals
- affordability proxy (free lunch share)
- diversity
- special education support
- teacher pay and class size

The API returns ranked district recommendations based on customizable priorities and constraints.

## Quickstart

### Prerequisites

- Python 3.11+

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run the API

```bash
uvicorn app.main:app --reload
```

Service URL: `http://127.0.0.1:8000`
Web UI: `http://127.0.0.1:8000/`

## API Endpoints

- `GET /health`
- `GET /districts`
  - Query params include `top_k`, all weight params, `min_grad_rate`, `max_student_teacher_ratio`
- `GET /districts/{district_id}/score`

Example:

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

--
# 1) Create virtual environment
python3 -m venv .venv

# 2) Activate it (Mac/zsh)
source .venv/bin/activate

# 3) Install dependencies (use the one your project has)
# Option A:
pip install -r requirements.txt
# Option B:
pip install -e .
# If neither exists, install minimum:
pip install fastapi uvicorn

# 4) Run app
uvicorn app.main:app --reload
