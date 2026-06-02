# Placement Brief

## Project Name

MedExplain AI: Explainable Healthcare Report Assistant

## One-Line Pitch

Built a secure AI healthcare assistant that explains medical reports using NLP, RAG, LLMs, role-based dashboards, privacy redaction, and FastAPI-ready backend architecture.

## Why This Project Is Strong For Placements

- Solves a real healthcare communication problem.
- Demonstrates full-stack thinking with Streamlit UI and FastAPI-ready backend.
- Shows AI/ML skills through NLP, RAG, LLM prompting, and model evaluation.
- Includes software engineering practices: modular code, database models, Docker, CI, docs, tests.
- Includes security and responsible AI: password hashing, privacy redaction, audit logs, medical guardrails.
- Has admin analytics and measurable model metrics for demo credibility.

## Resume Bullets

- Developed an explainable AI healthcare assistant using Streamlit, Gemini, FAISS, NLP, and SQLAlchemy to analyze medical reports and generate role-specific patient/doctor summaries.
- Implemented secure authentication with password hashing, role-based access, audit logs, privacy redaction before LLM calls, and database-backed report history.
- Built a hybrid recommendation engine with symptom extraction, lab abnormality detection, confidence-ranked predictions, RAG evidence retrieval, and emergency red-flag detection.
- Added FastAPI backend skeleton, Pydantic schemas, Docker deployment files, CI workflow, model evaluation script, and admin analytics dashboard.

## Demo Script

1. Log in with `patient_demo`.
2. Paste a sample report with fever, cough, WBC, hemoglobin, glucose, and phone/email values.
3. Show privacy redaction notice, extracted findings, risk level, prediction table, AI summary, evidence, and download summary.
4. Open Medical Report Chat and ask: `Why is my WBC value high?`
5. Log in with `admin_demo`.
6. Show admin console: users, reports, feedback, risk chart, audit logs, and model metrics.
7. Show FastAPI docs with `uvicorn api.main:app --reload` and `http://localhost:8000/docs`.

## Metrics To Mention After Running Evaluation

- Dataset rows processed
- Accuracy
- Macro F1
- Weighted F1
- Top-3 accuracy
- Number of report analyses stored
- Average user feedback rating
