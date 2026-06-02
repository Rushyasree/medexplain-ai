from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8)
    role: str = "patient"
    full_name: str | None = None
    consent_given: bool = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=5)
    language: str = "English"


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    evidence: list[str]
    explanation: str


class AnalyzeResponse(BaseModel):
    report_id: int | None = None
    risk_level: str
    entities: dict
    lab_values: dict
    abnormalities: dict
    predictions: list[PredictionResponse]
    emergency_findings: list[dict]
    explanation: str
