import pandas as pd
diabetes = pd.read_csv("data/diabetes.csv")
disease = pd.read_csv("data/disease.csv")
patients = pd.read_excel("data/patients.xlsx")
print("Diabetes Columns:", diabetes.columns)
print("Disease Columns:", disease.columns)
print("Patients Columns:", patients.columns)
def process_diabetes(df):
    def convert(row):
        symptoms = []
        if row["blood_glucose_level"] > 140:
            symptoms.append("high glucose")
        if row["bmi"] > 30:
            symptoms.append("obesity")
        if row["age"] > 45:
            symptoms.append("fatigue")
        if row["hypertension"] == 1:
            symptoms.append("high blood pressure")
        if row["heart_disease"] == 1:
            symptoms.append("heart disease")
        diagnosis = "diabetes" if row["diabetes"] == 1 else "normal"
        lab = f"glucose:{row['blood_glucose_level']}"
        return pd.Series([", ".join(symptoms), diagnosis, lab])
    df[["symptoms", "diagnosis", "lab_values"]] = df.apply(convert, axis=1)
    return df[["symptoms", "diagnosis", "lab_values"]]
def process_disease(df):
    def combine_symptoms(row):
        symptoms = [
            str(row["Symptom_1"]),
            str(row["Symptom_2"]),
            str(row["Symptom_3"])
        ]
        return ", ".join(symptoms)
    df["symptoms"] = df.apply(combine_symptoms, axis=1)
    df["diagnosis"] = df["Diagnosis"]
    df["lab_values"] = df.apply(
        lambda row: f"bp:{row['Blood_Pressure_mmHg']}, temp:{row['Body_Temperature_C']}",
        axis=1
    )
    return df[["symptoms", "diagnosis", "lab_values"]]
def process_patients(df):
    def convert(row):
        symptoms = []
        if row["BMI"] > 30:
            symptoms.append("obesity")
        if row["HadHeartAttack"] == "Yes":
            symptoms.append("heart attack")
        if row["HadStroke"] == "Yes":
            symptoms.append("stroke")
        if row["HadDiabetes"] == "Yes":
            symptoms.append("diabetes")
        if row["HadAsthma"] == "Yes":
            symptoms.append("asthma")
        diagnosis = "multiple conditions"
        lab = f"bmi:{row['BMI']}"
        return pd.Series([", ".join(symptoms), diagnosis, lab])
    df[["symptoms", "diagnosis", "lab_values"]] = df.apply(convert, axis=1)
    return df[["symptoms", "diagnosis", "lab_values"]]
d1 = process_diabetes(diabetes)
d2 = process_disease(disease)
d3 = process_patients(patients)
final_df = pd.concat([d1, d2, d3], ignore_index=True)
final_df.drop_duplicates(inplace=True)
final_df.reset_index(drop=True, inplace=True)
final_df.to_csv("data/final_medical_dataset.csv", index=False)
print("✅ Final dataset created successfully!")