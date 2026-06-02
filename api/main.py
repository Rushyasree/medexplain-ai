from __future__ import annotations

from fastapi import FastAPI, HTTPException

from api.schemas import AnalyzeRequest, AnalyzeResponse, LoginRequest, RegisterRequest, TokenResponse
from modules.data_loader import load_dataset
from modules.database import User, init_db, session_scope
from modules.llm import patient_explanation
from modules.nlp import detect_abnormalities, extract_entities, extract_lab_values
from modules.predictor import predict_from_dataset
from modules.privacy import redact_sensitive_text
from modules.rag import load_vector_db, retrieve_context
from modules.safety import emergency_findings, risk_level
from modules.security import create_access_token, hash_password, verify_password


app = FastAPI(
    title="MedExplain AI API",
    version="1.0.0",
    description="API-ready backend skeleton for medical report interpretation.",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest) -> TokenResponse:
    if payload.role not in {"patient", "doctor", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    if not payload.consent_given:
        raise HTTPException(status_code=400, detail="Consent is required")

    with session_scope() as session:
        existing = session.query(User).filter(User.username == payload.username).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")
        user = User(
            username=payload.username,
            full_name=payload.full_name,
            role=payload.role,
            password_hash=hash_password(payload.password),
            consent_given=1,
        )
        session.add(user)
        session.flush()
        token = create_access_token(user.id, user.role)
        return TokenResponse(access_token=token, role=user.role)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    with session_scope() as session:
        user = session.query(User).filter(User.username == payload.username).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(user.id, user.role)
        return TokenResponse(access_token=token, role=user.role)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    df = load_dataset()
    vector_db = load_vector_db()
    safe_text = redact_sensitive_text(payload.text)
    entities = extract_entities(payload.text)
    lab_values = extract_lab_values(payload.text)
    abnormalities = detect_abnormalities(lab_values)
    emergencies = emergency_findings(payload.text)
    risk = risk_level(abnormalities, len(emergencies))
    predictions = predict_from_dataset(payload.text, df)
    context = retrieve_context(payload.text, vector_db)
    explanation = patient_explanation(safe_text, entities, abnormalities, context, payload.language)

    return AnalyzeResponse(
        report_id=None,
        risk_level=risk,
        entities=entities,
        lab_values=lab_values,
        abnormalities=abnormalities,
        predictions=predictions,
        emergency_findings=emergencies,
        explanation=explanation,
    )
