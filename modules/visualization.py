from __future__ import annotations

import pandas as pd
import plotly.express as px


def lab_value_chart(values_dict: dict):
    df = pd.DataFrame(
        [{"Lab": key.replace("_", " ").title(), "Value": value} for key, value in values_dict.items()]
    )
    return px.bar(
        df,
        x="Lab",
        y="Value",
        text="Value",
        color="Lab",
        title="Lab Values Overview",
    )


def condition_frequency_chart(df: pd.DataFrame):
    counts = df["diagnosis"].value_counts().reset_index()
    counts.columns = ["Condition", "Count"]
    return px.bar(counts, x="Condition", y="Count", title="Dataset Condition Distribution")


def risk_distribution_chart(rows: list[dict]):
    df = pd.DataFrame(rows or [{"Risk": "none", "Count": 0}])
    return px.pie(df, names="Risk", values="Count", title="Analyzed Report Risk Distribution")
