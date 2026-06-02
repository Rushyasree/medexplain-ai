# Upgrade Log

## Latest Platform Update

This update adds privacy, admin observability, downloadable outputs, and an API-ready backend layer to MedExplain AI.

## Added Capabilities

- Privacy redaction before LLM calls
  - Emails, Indian phone numbers, and common ID-like numbers are redacted before report text is sent to the LLM.
  - Implemented in `modules/privacy.py`.

- Real admin console
  - Admin users can view dashboard metrics, feedback average, report risk distribution, recent reports, and audit logs.
  - Implemented through `modules/report_service.py` and the admin page in `app.py`.

- Feedback metrics
  - User feedback is stored in the `feedback` table.
  - Admin dashboard shows total feedback count and average usefulness rating.

- Recent reports and risk distribution
  - Recent analyzed reports are visible to admins.
  - Risk levels are visualized with a Plotly chart.

- Report summary download
  - After analysis, users can download the generated AI summary as a `.txt` file.

- FastAPI backend skeleton
  - API package added under `api/`.
  - Current endpoints:
    - `GET /health`
    - `POST /auth/register`
    - `POST /auth/login`
    - `POST /analyze`

- Pydantic API schemas
  - Request/response validation lives in `api/schemas.py`.

- Updated API documentation and requirements
  - `API.md` now includes local API run instructions.
  - `requirements.txt` now includes FastAPI, Uvicorn, and Pydantic.

- Import cleanup
  - Some Streamlit-dependent modules now include fallbacks, making them easier to import from scripts and API routes.

## Demo Value

This update makes the project stronger for:

- Placement demonstrations
- Final-year review
- Hackathon judging
- Research/prototype explanation
- Resume discussion around security, privacy, API design, and observability

## Verification

- Python syntax check completed with `compileall`.
- Smoke checks passed for privacy redaction and RAG context formatting.

Full app/API execution still requires installing project dependencies from `requirements.txt`.

## Placement Readiness Update

Added artifacts to help present the project during college placements:

- `PLACEMENT_BRIEF.md` with one-line pitch, resume bullets, demo script, and metrics to mention
- `MODEL_CARD.md` with model purpose, safety controls, limitations, and evaluation plan
- `scripts/evaluate_model.py` now writes `artifacts/evaluation_report.json`
- `scripts/evaluate_model.py` now writes `artifacts/confusion_matrix.csv`
- Admin console now includes a `Model Metrics` tab
- README now links the placement brief and model card
