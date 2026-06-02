from __future__ import annotations

import streamlit as st

from modules.auth import auth_gate
from modules.data_loader import load_dataset
from modules.database import init_db
from modules.llm import doctor_analysis, patient_explanation, report_chat
from modules.nlp import detect_abnormalities, extract_entities, extract_lab_values
from modules.pdf_reader import extract_text_from_pdf
from modules.privacy import redact_sensitive_text, summarize_privacy_actions
from modules.predictor import predict_from_dataset
from modules.rag import load_vector_db, retrieve_context
from modules.model_metrics import load_evaluation_report
from modules.report_service import (
    dashboard_metrics,
    admin_report_rows,
    feedback_summary,
    latest_report_for_user,
    latest_audit_logs,
    list_user_reports,
    risk_distribution,
    save_analysis,
    save_feedback,
)
from modules.safety import emergency_findings, risk_level
from modules.visualization import condition_frequency_chart, lab_value_chart, risk_distribution_chart


st.set_page_config(page_title="MedExplain AI", page_icon="M+", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; }
    .metric-card {
        padding: 1rem;
        border: 1px solid #e6ecf2;
        border-radius: 12px;
        background: #ffffff;
    }
    .risk-low { color: #087f5b; font-weight: 700; }
    .risk-elevated { color: #b7791f; font-weight: 700; }
    .risk-moderate { color: #c05621; font-weight: 700; }
    .risk-critical { color: #c53030; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


@st.cache_resource(show_spinner="Loading medical knowledge index...")
def get_db():
    return load_vector_db()


def dashboard(df):
    st.title("MedExplain AI")
    st.caption("Secure medical report interpretation with NLP, RAG, explainability, and responsible AI guardrails.")

    metrics = dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Reports analyzed", metrics["reports"])
    col2.metric("AI suggestions generated", metrics["diagnoses"])
    col3.metric("Users served", metrics["users"])
    col4.metric("Critical alerts", metrics["critical"])

    st.subheader("Dataset Intelligence")
    st.plotly_chart(condition_frequency_chart(df), use_container_width=True)


def analyze_report(df, vector_db):
    st.title("Analyze Medical Report")
    st.caption("Upload a PDF or paste report text. This tool supports education and triage, not final diagnosis.")

    source_type = "manual"
    filename = None
    uploaded_file = st.file_uploader("Upload medical report PDF", type=["pdf"])
    manual_text = st.text_area("Or paste symptoms/report text", height=180)
    language = st.selectbox("Explanation language", ["English", "Hindi", "Telugu", "Tamil"])

    text_data = ""
    if uploaded_file:
        source_type = "pdf"
        filename = uploaded_file.name
        try:
            text_data = extract_text_from_pdf(uploaded_file)
            st.success("PDF text extracted successfully.")
            with st.expander("Extracted text"):
                st.write(text_data)
        except Exception as exc:
            st.error(str(exc))
            return
    elif manual_text.strip():
        text_data = manual_text.strip()

    if not st.button("Analyze", type="primary"):
        return
    if not text_data:
        st.warning("Please upload a report or enter text.")
        return

    emergencies = emergency_findings(text_data)
    llm_text = redact_sensitive_text(text_data)
    privacy = summarize_privacy_actions(text_data, llm_text)
    entities = extract_entities(text_data)
    lab_values = extract_lab_values(text_data)
    abnormalities = detect_abnormalities(lab_values)
    risk = risk_level(abnormalities, len(emergencies))
    predictions = predict_from_dataset(text_data, df)
    context = retrieve_context(text_data, vector_db)

    st.subheader("Report Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Symptoms found", len(entities["symptoms"]))
    c2.metric("Lab values found", len(lab_values))
    c3.markdown(f"Risk level: <span class='risk-{risk}'>{risk.title()}</span>", unsafe_allow_html=True)

    if emergencies:
        st.error("Emergency red flags detected. Seek immediate medical care if these symptoms are present.")
        st.dataframe(emergencies, use_container_width=True)

    if privacy["redacted"]:
        st.info("Personal identifiers were redacted before sending text to the AI explanation model.")

    tab_findings, tab_ai, tab_evidence = st.tabs(["Findings", "AI Explanation", "Evidence"])
    with tab_findings:
        left, right = st.columns(2)
        left.write("Extracted entities")
        left.json(entities)
        right.write("Lab abnormalities")
        right.json(abnormalities)
        if lab_values:
            st.plotly_chart(lab_value_chart(lab_values), use_container_width=True)

        st.write("Dataset-based suggestions")
        if predictions:
            st.dataframe(predictions, use_container_width=True)
        else:
            st.info("Insufficient matching information for dataset-based suggestions.")

    role = st.session_state.get("role", "patient")
    with tab_ai:
        with st.spinner("Generating grounded explanation..."):
            if role in {"doctor", "admin"}:
                summary = doctor_analysis(llm_text, entities, context, predictions, language=language)
            else:
                summary = patient_explanation(llm_text, entities, abnormalities, context, language=language)
        st.write(summary)
        st.warning("This system does not provide a confirmed diagnosis or treatment plan. Consult a qualified clinician.")

    with tab_evidence:
        if context:
            for index, item in enumerate(context, start=1):
                with st.expander(f"Evidence {index}: {item['source']}"):
                    st.write(item["content"])
        else:
            st.info("No vector evidence available. Build/install RAG dependencies to enable retrieval.")

    report_id = save_analysis(
        st.session_state["user_id"],
        source_type,
        filename,
        text_data,
        risk,
        predictions,
        summary,
    )
    st.success("Analysis saved to report history.")
    st.download_button(
        "Download summary",
        data=summary,
        file_name=f"medexplain_report_{report_id}.txt",
        mime="text/plain",
    )

    with st.expander("Rate this explanation"):
        rating = st.slider("Usefulness", 1, 5, 4)
        comments = st.text_area("Feedback for improving the assistant")
        if st.button("Save feedback"):
            save_feedback(st.session_state["user_id"], report_id, rating, comments)
            st.success("Feedback saved.")


def assistant_chat(vector_db):
    st.title("Medical Report Chat")
    st.caption("Ask follow-up questions about your latest saved report.")

    report = latest_report_for_user(st.session_state["user_id"])
    if not report:
        st.info("Analyze a report first, then come back here to chat about it.")
        return

    st.write(f"Latest report: #{report['id']} - Risk: {report['risk'].title()}")
    language = st.selectbox("Response language", ["English", "Hindi", "Telugu", "Tamil"], key="chat_language")
    question = st.text_area("Ask a question", placeholder="Example: Why is my WBC value high?")

    if st.button("Ask assistant", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
            return
        safe_report = {**report, "text": redact_sensitive_text(report["text"])}
        context = retrieve_context(question + "\n" + safe_report["text"], vector_db)
        with st.spinner("Checking your report and evidence..."):
            answer = report_chat(question, safe_report, context, language=language)
        st.write(answer)
        st.warning("For medical decisions, confirm this with a qualified clinician.")


def history():
    st.title("Report History")
    rows = list_user_reports(st.session_state["user_id"])
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No reports analyzed yet.")


def admin_notes():
    st.title("Admin Console")
    metrics = dashboard_metrics()
    feedback = feedback_summary()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Users", metrics["users"])
    col2.metric("Reports", metrics["reports"])
    col3.metric("Feedback items", feedback["count"])
    col4.metric("Avg rating", feedback["average_rating"])

    st.subheader("Risk Distribution")
    st.plotly_chart(risk_distribution_chart(risk_distribution()), use_container_width=True)

    tab_reports, tab_audit, tab_model = st.tabs(["Recent Reports", "Audit Logs", "Model Metrics"])
    with tab_reports:
        st.dataframe(admin_report_rows(), use_container_width=True)
    with tab_audit:
        st.dataframe(latest_audit_logs(), use_container_width=True)
    with tab_model:
        report = load_evaluation_report()
        if not report.get("available"):
            st.info(report["message"])
            st.code("python scripts/evaluate_model.py", language="powershell")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", report["rows"])
            c2.metric("Accuracy", report["accuracy"])
            c3.metric("Macro F1", report["macro_f1"])
            c4.metric("Top-3 accuracy", report["top_3_accuracy"])
            st.write("Model:", report["model"])
            st.write("Labels:", ", ".join(report["labels"]))


def main():
    st.sidebar.title("MedExplain AI")
    if not auth_gate():
        return

    df = load_dataset()
    vector_db = get_db()

    role = st.session_state.get("role", "patient")
    pages = ["Dashboard", "Analyze Report", "Medical Report Chat", "Report History"]
    if role == "admin":
        pages.append("Admin Notes")
    page = st.sidebar.radio("Navigation", pages)

    if page == "Dashboard":
        dashboard(df)
    elif page == "Analyze Report":
        analyze_report(df, vector_db)
    elif page == "Medical Report Chat":
        assistant_chat(vector_db)
    elif page == "Report History":
        history()
    else:
        admin_notes()


if __name__ == "__main__":
    main()
