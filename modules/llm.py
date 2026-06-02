from __future__ import annotations

from modules.config import settings
from modules.rag import format_context


def _model():
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel("gemini-2.5-flash-lite")
    except Exception:
        return None


def _generate(prompt: str) -> str:
    model = _model()
    if not model:
        return (
            "AI explanation is unavailable because the Gemini API key or package is not configured. "
            "The extracted findings and dataset recommendations are still shown."
        )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        return f"AI explanation could not be generated: {exc}"


def doctor_analysis(
    input_text: str,
    entities: dict,
    context: list[dict],
    predictions: list[dict],
    language: str = "English",
) -> str:
    prompt = f"""
You are a clinical decision-support assistant for licensed clinicians.
Use only the provided report, extracted findings, predictions, and retrieved evidence.
Do not claim a confirmed diagnosis. Do not prescribe treatment.

Report:
{input_text}

Extracted findings:
{entities}

Model suggestions:
{predictions}

Retrieved evidence:
{format_context(context)}

Write the final response in: {language}.

Return:
- Concise clinical summary
- Differential diagnoses with confidence qualifiers
- Abnormal or missing tests to verify
- Evidence used
- Safety warnings and recommended clinician follow-up
"""
    return _generate(prompt)


def patient_explanation(
    input_text: str,
    entities: dict,
    abnormalities: dict,
    context: list[dict],
    language: str = "English",
) -> str:
    prompt = f"""
Explain this medical report to a patient in simple English.
Use only the supplied report and evidence. Do not diagnose or prescribe.

Report:
{input_text}

Extracted findings:
{entities}

Abnormalities:
{abnormalities}

Evidence:
{format_context(context)}

Write the final response in: {language}.

Return:
- What this report seems to show
- Values that may need attention
- Questions to ask a doctor
- When to seek urgent care
"""
    return _generate(prompt)


def report_chat(question: str, report: dict, context: list[dict], language: str = "English") -> str:
    prompt = f"""
You are a careful medical report education assistant.
Answer only from the report, prior AI summary, diagnoses, and retrieved evidence below.
Do not diagnose, prescribe, or invent facts. If the answer is not supported, say what information is missing.

Question:
{question}

Report:
{report.get("text", "")}

Prior summary:
{report.get("summary", "")}

Stored diagnosis suggestions:
{report.get("diagnoses", [])}

Evidence:
{format_context(context)}

Write the final response in: {language}.
Keep it concise and include questions the user can ask a clinician when helpful.
"""
    return _generate(prompt)
