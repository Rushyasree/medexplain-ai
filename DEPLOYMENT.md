# Deployment Guide

## Local Demo

1. Create `.env` from `.env.example`.
2. Set `GEMINI_API_KEY` and `JWT_SECRET`.
3. Run `streamlit run app.py`.

## Docker

```bash
docker compose up --build
```

## Render Deployment

This repository includes a Render Blueprint file:

```text
render.yaml
```

It deploys the Streamlit app as a Docker web service using:

```text
Dockerfile.render
requirements-render.txt
```

The Render-specific Dockerfile uses a lightweight dependency set so the demo deploy is faster and less likely to exceed free-instance limits. Heavy optional RAG/embedding dependencies are intentionally excluded from the Render build; the app falls back gracefully when vector retrieval packages are unavailable.

### Deploy Steps

1. Push the latest code to GitHub.
2. Open Render Dashboard.
3. Choose **Blueprints** or **New + > Blueprint**.
4. Connect the GitHub repository:

```text
Rushyasree/medexplain-ai
```

5. Render will detect `render.yaml`.
6. Add the required secret environment variable:

```text
GEMINI_API_KEY
```

7. Deploy.

If you create a normal Web Service instead of a Blueprint, use:

```text
Runtime: Docker
Dockerfile Path: ./Dockerfile.render
Health Check Path: /_stcore/health
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
