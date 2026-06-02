from __future__ import annotations

import pandas as pd

try:
    import streamlit as st
except Exception:
    class _CacheFallback:
        @staticmethod
        def cache_data(*args, **kwargs):
            def decorator(func):
                return func

            return decorator

    st = _CacheFallback()

from modules.config import DATA_DIR


@st.cache_data(show_spinner=False)
def load_dataset() -> pd.DataFrame:
    path = DATA_DIR / "final_medical_dataset.csv"
    df = pd.read_csv(path)
    for column in ("symptoms", "diagnosis", "lab_values"):
        if column not in df.columns:
            raise ValueError(f"Dataset is missing required column: {column}")
    return df.fillna("")
