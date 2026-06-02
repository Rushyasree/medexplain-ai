# Architecture

```mermaid
flowchart TD
    U["Patient / Doctor / Admin"] --> S["Streamlit UI"]
    S --> A["Role-Based Auth"]
    A --> DB["SQL Database"]
    S --> P["PDF Parser"]
    S --> N["NLP Extraction"]
    N --> L["Lab Abnormality Engine"]
    N --> R["Hybrid Recommender"]
    S --> V["FAISS RAG Index"]
    V --> G["Grounded Gemini Prompt"]
    R --> G
    L --> G
    G --> O["Role-Specific Explanation"]
    O --> DB
    S --> C["Report Chat"]
    C --> V
    C --> G
    S --> D["Dashboard / History / Analytics"]
    S --> ADM["Admin Console"]
    ADM --> DB
    ADM --> AUD["Audit Logs"]
    API["FastAPI Skeleton"] --> DB
    API --> N
    API --> G
    DB --> D
```

## Modules

- `modules/config.py`: environment, paths, secrets
- `modules/database.py`: SQLAlchemy models and sessions
- `modules/security.py`: password hashing and JWT utilities
- `modules/auth.py`: Streamlit authentication panels
- `modules/nlp.py`: entity and lab value extraction
- `modules/predictor.py`: confidence-ranked dataset recommendations
- `modules/rag.py`: persistent FAISS retrieval
- `modules/llm.py`: grounded Gemini prompts
- `modules/safety.py`: red-flag detection and risk levels
- `modules/visualization.py`: Plotly charts
- `modules/report_service.py`: report persistence, feedback, history, and dashboard metrics
- `modules/privacy.py`: redacts sensitive identifiers before LLM calls
- `api/main.py`: FastAPI backend skeleton
- `api/schemas.py`: Pydantic request/response schemas

## Database Tables

- `users`: accounts, roles, consent
- `reports`: uploaded/manual report analyses
- `diagnoses`: prediction labels, confidence, evidence
- `feedback`: clinician or user feedback
- `audit_logs`: login, registration, report-analysis events
