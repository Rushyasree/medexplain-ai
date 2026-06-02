# Model Card

## Model Purpose

MedExplain AI uses a hybrid clinical-intelligence approach:

- rule-based extraction for symptoms and laboratory values
- abnormality detection against reference ranges
- dataset-based recommendation ranking
- RAG context retrieval
- Gemini-generated patient/doctor explanations

The project is designed for education, triage support, and portfolio demonstration. It is not a certified diagnostic device.

## Baseline Evaluation

Run:

```bash
python scripts/evaluate_model.py
```

This generates:

- `artifacts/evaluation_report.json`
- `artifacts/confusion_matrix.csv`

The baseline evaluator trains a TF-IDF + balanced Logistic Regression classifier on `data/final_medical_dataset.csv` and reports:

- accuracy
- macro F1
- weighted F1
- top-3 accuracy
- classification report
- confusion matrix

## Known Limitations

- The dataset has class imbalance.
- Some labels are broad, such as `multiple conditions`.
- Predictions are not clinically validated.
- Lab interpretation uses simplified reference ranges.
- LLM explanations depend on prompt quality and retrieved context.

## Safety Controls

- Red-flag symptom detection
- Privacy redaction before LLM calls
- Grounded prompts that prohibit confirmed diagnosis and treatment prescription
- Patient/doctor role separation
- Audit logs and feedback tracking

## Recommended Next Step

Improve recommendation quality using biomedical embeddings, curated guideline documents, calibrated confidence scoring, and doctor-reviewed feedback.
