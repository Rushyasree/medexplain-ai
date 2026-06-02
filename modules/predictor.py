from __future__ import annotations

import math
import re
from dataclasses import dataclass

import pandas as pd


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]*", str(text).lower()) if len(token) > 2}


@dataclass
class Prediction:
    label: str
    confidence: float
    evidence: list[str]
    explanation: str


class HybridMedicalRecommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df.fillna("").copy()
        self.df["_tokens"] = self.df["symptoms"].apply(_tokens)

    def predict(self, user_input: str, top_k: int = 3) -> list[Prediction]:
        query_tokens = _tokens(user_input)
        if not query_tokens:
            return []

        scored: dict[str, dict] = {}
        for _, row in self.df.iterrows():
            symptom_tokens = row["_tokens"]
            if not symptom_tokens:
                continue
            overlap = query_tokens.intersection(symptom_tokens)
            if not overlap:
                continue
            jaccard = len(overlap) / len(query_tokens.union(symptom_tokens))
            label = str(row["diagnosis"]).strip()
            if label not in scored or jaccard > scored[label]["score"]:
                scored[label] = {
                    "score": jaccard,
                    "evidence": sorted(overlap),
                    "symptoms": row["symptoms"],
                }

        predictions = []
        for label, item in sorted(scored.items(), key=lambda pair: pair[1]["score"], reverse=True)[:top_k]:
            confidence = min(0.92, 0.35 + math.sqrt(item["score"]) * 0.65)
            predictions.append(
                Prediction(
                    label=label,
                    confidence=round(confidence, 2),
                    evidence=item["evidence"],
                    explanation=f"Matched report terms with dataset symptoms: {item['symptoms']}",
                )
            )
        return predictions


def predict_from_dataset(user_input: str, df: pd.DataFrame, top_k: int = 3) -> list[dict]:
    recommender = HybridMedicalRecommender(df)
    return [prediction.__dict__ for prediction in recommender.predict(user_input, top_k=top_k)]
