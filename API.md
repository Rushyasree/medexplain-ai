# API Design

The current implementation is Streamlit-first, and an API-ready FastAPI skeleton now lives in `api/main.py`.

Currently implemented endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health check |
| POST | `/auth/register` | Register a user and return an access token |
| POST | `/auth/login` | Authenticate a user and return an access token |
| POST | `/analyze` | Analyze report text and return extracted findings, risk, predictions, and explanation |

Recommended future endpoints:

| Method | Path | Purpose | Roles |
| --- | --- | --- | --- |
| POST | `/auth/register` | Create user | public |
| POST | `/auth/login` | Issue access/refresh tokens | public |
| POST | `/reports` | Upload report | patient, doctor |
| GET | `/reports` | List report history | patient, doctor, admin |
| GET | `/reports/{id}` | Read report analysis | owner, doctor, admin |
| POST | `/reports/{id}/feedback` | Add feedback | doctor, patient |
| GET | `/analytics/summary` | Dashboard metrics | doctor, admin |
| POST | `/chat` | Ask report-aware questions | patient, doctor |

Use Pydantic schemas for request/response validation and keep protected health data encrypted at rest.

Run locally after installing requirements:

```bash
uvicorn api.main:app --reload
```

Swagger docs:

```text
http://localhost:8000/docs
```
