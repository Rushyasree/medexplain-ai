from __future__ import annotations

import re
from functools import lru_cache


SYMPTOMS = {
    "fever",
    "cough",
    "pain",
    "fatigue",
    "vomiting",
    "headache",
    "shortness of breath",
    "chest pain",
    "dizziness",
    "weakness",
    "nausea",
    "sore throat",
}

LAB_ALIASES = {
    "hemoglobin": ["hemoglobin", "hb", "hgb"],
    "wbc": ["wbc", "white blood cell", "white blood cells"],
    "platelets": ["platelets", "platelet count"],
    "crp": ["crp", "c reactive protein", "c-reactive protein"],
    "glucose": ["glucose", "blood sugar", "blood glucose"],
    "hba1c": ["hba1c", "hb a1c", "glycated hemoglobin"],
    "bp_systolic": ["systolic", "bp"],
}

CONDITIONS = {
    "infection",
    "anemia",
    "diabetes",
    "hypertension",
    "bronchitis",
    "pneumonia",
    "flu",
    "cold",
}

NORMAL_RANGES = {
    "hemoglobin": (12.0, 16.0, "g/dL"),
    "wbc": (4000.0, 11000.0, "cells/uL"),
    "platelets": (150000.0, 450000.0, "cells/uL"),
    "crp": (0.0, 10.0, "mg/L"),
    "glucose": (70.0, 140.0, "mg/dL"),
    "hba1c": (4.0, 5.7, "%"),
}


@lru_cache(maxsize=1)
def _load_biomedical_ner():
    try:
        from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

        model_name = "d4data/biomedical-ner-all"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        return pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    except Exception:
        return None


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def extract_entities(text: str) -> dict:
    normalized = clean_text(text)
    symptoms = {item for item in SYMPTOMS if item in normalized}
    labs = {
        canonical
        for canonical, aliases in LAB_ALIASES.items()
        if any(alias in normalized for alias in aliases)
    }
    conditions = {item for item in CONDITIONS if item in normalized}

    ner = _load_biomedical_ner()
    if ner:
        for item in ner(text[:4000]):
            entity = str(item.get("word", "")).lower().replace("##", "").strip()
            if len(entity) < 3:
                continue
            if entity in SYMPTOMS:
                symptoms.add(entity)
            elif entity in CONDITIONS:
                conditions.add(entity)

    return {
        "symptoms": sorted(symptoms),
        "labs": sorted(labs),
        "conditions": sorted(conditions),
    }


def extract_lab_values(text: str) -> dict:
    normalized = clean_text(text)
    lab_values: dict[str, float] = {}

    for canonical, aliases in LAB_ALIASES.items():
        alias_pattern = "|".join(re.escape(alias) for alias in aliases)
        pattern = rf"\b({alias_pattern})\b\s*(?:is|=|:|-)?\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, normalized)
        if match:
            lab_values[canonical] = float(match.group(2))

    bp_match = re.search(r"\b(?:bp|blood pressure)\s*(?:is|=|:|-)?\s*(\d{2,3})\s*/\s*(\d{2,3})", normalized)
    if bp_match:
        lab_values["bp_systolic"] = float(bp_match.group(1))
        lab_values["bp_diastolic"] = float(bp_match.group(2))

    return lab_values


def detect_abnormalities(lab_values: dict) -> dict:
    abnormalities = {}
    for test, value in lab_values.items():
        if test == "bp_systolic":
            abnormalities[test] = "HIGH" if value >= 140 else "NORMAL"
            continue
        if test == "bp_diastolic":
            abnormalities[test] = "HIGH" if value >= 90 else "NORMAL"
            continue
        if test not in NORMAL_RANGES:
            continue
        low, high, unit = NORMAL_RANGES[test]
        if value < low:
            status = "LOW"
        elif value > high:
            status = "HIGH"
        else:
            status = "NORMAL"
        abnormalities[test] = {"status": status, "range": f"{low:g}-{high:g} {unit}"}
    return abnormalities
