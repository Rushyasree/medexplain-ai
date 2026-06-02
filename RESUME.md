# Resume-Ready Description

**MedExplain AI: Explainable Healthcare Report Assistant**

Built a secure AI healthcare assistant that analyzes medical reports, extracts symptoms and lab values, flags abnormalities, retrieves supporting evidence with RAG, and generates role-specific explanations for patients and doctors.

## Technical Highlights

- Developed a Streamlit healthcare dashboard with role-based patient, doctor, and admin workflows.
- Implemented secure authentication using bcrypt password hashing and JWT token generation.
- Designed SQLAlchemy database schema for users, reports, diagnoses, feedback, and audit logs.
- Built NLP extraction for symptoms, conditions, lab values, blood pressure, and abnormality detection.
- Integrated FAISS-based retrieval and Gemini-powered grounded explanations.
- Added dynamic analytics, report history, report-aware chatbot, multilingual explanations, feedback capture, emergency red-flag detection, Docker deployment, and CI tests.

## Metrics To Add After Evaluation

- Number of medical records processed
- Top-3 diagnosis recommendation accuracy
- Macro F1 score
- Average explanation usefulness score from users/doctors
- Report processing latency
