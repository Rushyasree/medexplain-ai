# MedExplain AI

MedExplain AI is a healthcare AI platform for explaining medical reports, extracting clinical findings, detecting abnormal lab values, retrieving medical evidence, and generating role-specific patient or doctor summaries.

This upgraded version turns the original Streamlit prototype into a portfolio-ready architecture with secure authentication, database-backed report history, role-based workflows, safer AI prompts, dynamic analytics, Docker support, and tests.

Latest upgrade details are tracked in [UPGRADE_LOG.md](UPGRADE_LOG.md).
Placement-specific talking points are available in [PLACEMENT_BRIEF.md](PLACEMENT_BRIEF.md), and model limitations/evaluation notes are documented in [MODEL_CARD.md](MODEL_CARD.md).

## Features

- Role-based authentication for patients, doctors, and admins
- Bcrypt password hashing
- JWT access token generation for future API expansion
- SQLAlchemy database models for users, reports, diagnoses, feedback, and audit logs
- PDF report parsing with file size and encryption checks
- Structured extraction for symptoms, conditions, lab values, and abnormalities
- Curated lab reference range dataset for explainable abnormality detection
- Sample reports for quick demonstrations
- Confidence-ranked dataset recommendations
- Persistent FAISS RAG index support
- Patient-friendly and doctor-facing Gemini explanations
- Multilingual explanations in English, Hindi, Telugu, and Tamil
- Report-aware chatbot for follow-up questions
- Feedback capture for future doctor-in-the-loop improvement
- Privacy redaction before LLM calls
- Admin console with audit logs, feedback metrics, recent reports, and risk distribution
- Downloadable report summaries
- FastAPI backend skeleton with Pydantic schemas
- Model evaluation script with JSON and confusion-matrix artifacts
- Model card and placement-ready project brief
- Emergency red-flag detection
- Dynamic dashboard metrics from stored report data
- Plotly analytics charts
- Docker and Docker Compose deployment files
- CI test workflow

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/seed_demo_users.py
streamlit run app.py
```

For Docker:

```bash
docker compose up --build
```

Open `http://localhost:8501`.

Demo accounts:

| Username | Password | Role |
| --- | --- | --- |
| `patient_demo` | `Patient@123` | patient |
| `doctor_demo` | `Doctor@123` | doctor |
| `admin_demo` | `Admin@123` | admin |

## Suggested Production Database

The app defaults to SQLite for local demos. For PostgreSQL, set:

```env
DATABASE_URL=postgresql+psycopg://medexplain:password@postgres:5432/medexplain
```

Add `psycopg[binary]` to `requirements.txt` when deploying with PostgreSQL.

## Responsible AI Disclaimer

MedExplain AI is an educational and clinical-support prototype. It must not be used as a standalone diagnostic or treatment system. All outputs should be verified by qualified healthcare professionals.

## API Backend Preview

After installing requirements, run the FastAPI skeleton:

```bash
uvicorn api.main:app --reload
```

Open Swagger docs at `http://localhost:8000/docs`.

## Deploy On Render

This repo includes Render-ready files:

- `render.yaml`
- `Dockerfile.render`
- `requirements-render.txt`

In Render, create a Blueprint from `Rushyasree/medexplain-ai`, set `GEMINI_API_KEY`, and deploy. See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

## Generate Model Metrics

Run the baseline evaluator before demos:

```bash
python scripts/evaluate_model.py
```

The admin console will display generated metrics from `artifacts/evaluation_report.json`.

## Demo Sample Reports

Use the files in `data/sample_reports/` for fast demos:

- `cbc_infection_report.txt`
- `diabetes_risk_report.txt`
- `anemia_report.txt`
