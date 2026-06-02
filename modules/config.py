from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
VECTOR_DIR = STORAGE_DIR / "vector_index"
LOG_DIR = STORAGE_DIR / "logs"

for directory in (STORAGE_DIR, UPLOAD_DIR, VECTOR_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def _get_secret(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        return str(st.secrets.get(name, default))
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "MedExplain AI"
    environment: str = os.getenv("MEDEXPLAIN_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(STORAGE_DIR / 'medexplain.db').as_posix()}"
    )
    gemini_api_key: str = _get_secret("GEMINI_API_KEY")
    jwt_secret: str = _get_secret("JWT_SECRET", "change-this-dev-secret")
    encryption_key: str = _get_secret("ENCRYPTION_KEY", "")
    max_pdf_mb: int = int(os.getenv("MAX_PDF_MB", "10"))
    default_embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
