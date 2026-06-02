from __future__ import annotations

import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "artifacts"
EVALUATION_REPORT = ARTIFACT_DIR / "evaluation_report.json"


def load_evaluation_report() -> dict:
    if not EVALUATION_REPORT.exists():
        return {
            "available": False,
            "message": "Run scripts/evaluate_model.py to generate model metrics.",
        }
    with EVALUATION_REPORT.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data["available"] = True
    return data
