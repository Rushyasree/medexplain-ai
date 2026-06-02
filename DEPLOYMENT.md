# Deployment Guide

## Local Demo

1. Create `.env` from `.env.example`.
2. Set `GEMINI_API_KEY` and `JWT_SECRET`.
3. Run `streamlit run app.py`.

## Docker

```bash
docker compose up --build
```

## Cloud Options

- Streamlit Community Cloud: easiest demo deployment, but limited for private medical data.
- Render/Railway: good portfolio deployment with PostgreSQL.
- Azure App Service: strong enterprise placement story.
- AWS ECS/Fargate: scalable production-style deployment.

## Production Checklist

- Use PostgreSQL instead of SQLite.
- Rotate all secrets and store them in the cloud secret manager.
- Enable HTTPS only.
- Add object storage for encrypted uploaded reports.
- Add structured logs and monitoring.
- Run dependency and secret scanning in CI.
- Add backup and retention policy.
