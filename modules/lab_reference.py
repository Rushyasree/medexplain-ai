from __future__ import annotations

from functools import lru_cache

import pandas as pd

from modules.config import DATA_DIR


DEFAULT_REFERENCES = {
    "hemoglobin": {
        "aliases": ["hemoglobin", "hb", "hgb"],
        "low": 12.0,
        "high": 16.0,
        "unit": "g/dL",
        "meaning_low": "May suggest anemia or blood loss",
        "meaning_high": "May suggest dehydration or high red blood cell concentration",
    },
    "wbc": {
        "aliases": ["wbc", "white blood cell", "white blood cells"],
        "low": 4000.0,
        "high": 11000.0,
        "unit": "cells/uL",
        "meaning_low": "May suggest low immunity",
        "meaning_high": "May suggest infection inflammation or stress response",
    },
    "platelets": {
        "aliases": ["platelets", "platelet count"],
        "low": 150000.0,
        "high": 450000.0,
        "unit": "cells/uL",
        "meaning_low": "May increase bleeding risk",
        "meaning_high": "May suggest inflammation infection or clotting risk",
    },
    "crp": {
        "aliases": ["crp", "c reactive protein", "c-reactive protein"],
        "low": 0.0,
        "high": 10.0,
        "unit": "mg/L",
        "meaning_low": "Usually not clinically concerning",
        "meaning_high": "May suggest inflammation or infection",
    },
    "glucose": {
        "aliases": ["glucose", "blood sugar", "blood glucose"],
        "low": 70.0,
        "high": 140.0,
        "unit": "mg/dL",
        "meaning_low": "May suggest hypoglycemia",
        "meaning_high": "May suggest diabetes risk or poor glucose control",
    },
    "hba1c": {
        "aliases": ["hba1c", "hb a1c", "glycated hemoglobin"],
        "low": 4.0,
        "high": 5.7,
        "unit": "%",
        "meaning_low": "Usually not clinically concerning",
        "meaning_high": "May suggest prediabetes or diabetes risk",
    },
}


@lru_cache(maxsize=1)
def load_lab_references() -> dict:
    path = DATA_DIR / "lab_reference_ranges.csv"
    if not path.exists():
        return DEFAULT_REFERENCES

    df = pd.read_csv(path).fillna("")
    references = {}
    for _, row in df.iterrows():
        test_name = str(row["test_name"]).strip().lower()
        references[test_name] = {
            "aliases": [alias.strip().lower() for alias in str(row["aliases"]).split("|") if alias.strip()],
            "low": float(row["low"]),
            "high": float(row["high"]),
            "unit": str(row["unit"]),
            "meaning_low": str(row["meaning_low"]),
            "meaning_high": str(row["meaning_high"]),
        }
    return references


def lab_aliases() -> dict[str, list[str]]:
    return {name: details["aliases"] for name, details in load_lab_references().items()}
