import pandas as pd

from modules.predictor import predict_from_dataset


def test_predict_from_dataset_returns_ranked_predictions():
    df = pd.DataFrame(
        [
            {"symptoms": "fever, cough", "diagnosis": "Flu", "lab_values": ""},
            {"symptoms": "high glucose, fatigue", "diagnosis": "Diabetes", "lab_values": ""},
        ]
    )

    predictions = predict_from_dataset("I have fever and cough", df)

    assert predictions
    assert predictions[0]["label"] == "Flu"
    assert predictions[0]["confidence"] > 0
    assert "fever" in predictions[0]["evidence"]
