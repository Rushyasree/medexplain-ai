from __future__ import annotations

import re
from functools import lru_cache

from modules.lab_reference import lab_aliases, load_lab_references


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
        for canonical, aliases in lab_aliases().items()
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

    for canonical, aliases in lab_aliases().items():
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
    references = load_lab_references()
    for test, value in lab_values.items():
        if test not in references:
            continue
        reference = references[test]
        low = reference["low"]
        high = reference["high"]
        if value < low:
            status = "LOW"
            meaning = reference["meaning_low"]
        elif value > high:
            status = "HIGH"
            meaning = reference["meaning_high"]
        else:
            status = "NORMAL"
            meaning = "Within the configured reference range"
        abnormalities[test] = {
            "status": status,
            "range": f"{low:g}-{high:g} {reference['unit']}",
            "meaning": meaning,
        }
    return abnormalities
