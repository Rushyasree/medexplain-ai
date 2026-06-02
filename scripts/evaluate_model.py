from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def evaluate(dataset: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(dataset).fillna("")
    x_train, x_test, y_train, y_test = train_test_split(
        df["symptoms"],
        df["diagnosis"],
        test_size=0.25,
        random_state=42,
        stratify=df["diagnosis"],
    )
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)
    labels = list(model.classes_)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    top_k = min(3, len(labels))

    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)
    matrix_df.to_csv(output_dir / "confusion_matrix.csv")

    result = {
        "dataset": str(dataset),
        "rows": int(len(df)),
        "labels": labels,
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "model": "TF-IDF n-grams + balanced Logistic Regression",
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(report["macro avg"]["f1-score"]), 4),
        "weighted_f1": round(float(report["weighted avg"]["f1-score"]), 4),
        "top_3_accuracy": round(
            float(top_k_accuracy_score(y_test, probabilities, k=top_k, labels=labels)), 4
        ),
        "classification_report": report,
        "confusion_matrix_csv": str(output_dir / "confusion_matrix.csv"),
    }

    with (output_dir / "evaluation_report.json").open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:")
    print(matrix)
    print("Accuracy:", result["accuracy"])
    print("Macro F1:", result["macro_f1"])
    print("Top-3 accuracy:", result["top_3_accuracy"])
    print("Saved:", output_dir / "evaluation_report.json")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/final_medical_dataset.csv")
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    evaluate(Path(args.dataset), Path(args.output_dir))
