from modules.nlp import detect_abnormalities, extract_entities, extract_lab_values


def test_extract_lab_values_and_abnormalities():
    text = "Hemoglobin 10.5, WBC: 13000, BP 150/95, glucose 180"
    values = extract_lab_values(text)

    assert values["hemoglobin"] == 10.5
    assert values["wbc"] == 13000
    assert values["bp_systolic"] == 150
    assert values["bp_diastolic"] == 95
    assert values["glucose"] == 180

    abnormalities = detect_abnormalities(values)
    assert abnormalities["hemoglobin"]["status"] == "LOW"
    assert abnormalities["wbc"]["status"] == "HIGH"
    assert abnormalities["bp_systolic"] == "HIGH"


def test_extract_entities():
    entities = extract_entities("Patient has fever, cough and possible diabetes.")
    assert "fever" in entities["symptoms"]
    assert "cough" in entities["symptoms"]
    assert "diabetes" in entities["conditions"]
