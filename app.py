from __future__ import annotations

import streamlit as st

from modules.auth import auth_gate
from modules.data_loader import load_dataset
from modules.database import init_db
from modules.llm import doctor_analysis, patient_explanation, report_chat
from modules.model_metrics import load_evaluation_report
from modules.nlp import detect_abnormalities, extract_entities, extract_lab_values
from modules.pdf_reader import extract_text_from_pdf
from modules.privacy import redact_sensitive_text, summarize_privacy_actions
from modules.predictor import predict_from_dataset
from modules.rag import load_vector_db, retrieve_context
from modules.report_service import (
    admin_report_rows,
    dashboard_metrics,
    feedback_summary,
    latest_audit_logs,
    latest_report_for_user,
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
    :root {
        --med-bg: #f7fafc;
        --med-panel: #ffffff;
        --med-ink: #14213d;
        --med-muted: #5f6b7a;
        --med-line: #dbe5ee;
        --med-blue: #2563eb;
        --med-teal: #0f766e;
        --med-red: #b42318;
        --med-amber: #b54708;
    }

    .stApp {
        background: var(--med-bg);
        color: var(--med-ink);
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--med-line);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--med-ink);
    }

    .app-brand {
        padding: 0.35rem 0 1rem 0;
        border-bottom: 1px solid var(--med-line);
        margin-bottom: 1rem;
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #0f766e;
        color: white;
        font-weight: 800;
        margin-right: 0.5rem;
    }

    .brand-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--med-ink);
    }

    .brand-subtitle {
        display: block;
        color: var(--med-muted);
        font-size: 0.78rem;
        margin-top: 0.15rem;
    }

    .page-shell {
        background: #ffffff;
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
    }

    .page-eyebrow {
        color: var(--med-teal);
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 0.35rem;
    }

    .page-title {
        color: var(--med-ink);
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 850;
        margin: 0;
    }

    .page-subtitle {
        color: var(--med-muted);
        font-size: 0.98rem;
        margin: 0.45rem 0 0 0;
        max-width: 780px;
    }

    .section-title {
        color: var(--med-ink);
        font-size: 1.02rem;
        font-weight: 800;
        margin: 1.1rem 0 0.5rem 0;
    }

    .metric-tile {
        background: #ffffff;
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 0.95rem;
        min-height: 104px;
    }

    .metric-label {
        color: var(--med-muted);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .metric-value {
        color: var(--med-ink);
        font-size: 1.8rem;
        font-weight: 850;
        line-height: 1.2;
        margin-top: 0.35rem;
    }

    .metric-note {
        color: var(--med-muted);
        font-size: 0.82rem;
        margin-top: 0.2rem;
    }

    .insight-panel {
        background: #ffffff;
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.85rem;
    }

    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 0.26rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 800;
        border: 1px solid transparent;
    }

    .risk-low {
        color: #05603a;
        background: #ecfdf3;
        border-color: #abefc6;
    }

    .risk-elevated {
        color: #93370d;
        background: #fffaeb;
        border-color: #fedf89;
    }

    .risk-moderate {
        color: #9c2a10;
        background: #fff4ed;
        border-color: #fdb022;
    }

    .risk-critical {
        color: #912018;
        background: #fef3f2;
        border-color: #fecdca;
    }

    .callout {
        border-left: 4px solid var(--med-teal);
        background: #f0fdfa;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        color: #134e4a;
    }

    .muted {
        color: var(--med-muted);
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 750;
    }

    div[data-testid="stTabs"] button {
        font-weight: 750;
    }

    textarea, input, select {
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


@st.cache_resource(show_spinner="Loading medical knowledge index...")
def get_db():
    return load_vector_db()


def sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="app-brand">
            <span class="brand-mark">M+</span>
            <span class="brand-title">MedExplain AI</span>
            <span class="brand-subtitle">Clinical report intelligence</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-shell">
            <div class="page-eyebrow">{eyebrow}</div>
            <h1 class="page-title">{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_tile(label: str, value, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-tile">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def risk_badge(risk: str) -> str:
    normalized = risk or "low"
    return f'<span class="status-pill risk-{normalized}">{normalized.title()}</span>'


def dashboard(df):
    page_header(
        "Operations dashboard",
        "Healthcare AI workspace",
        "Monitor report activity, safety alerts, dataset coverage, and clinical-assist usage from one focused view.",
    )

    metrics = dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_tile("Reports analyzed", metrics["reports"], "Stored report reviews")
    with col2:
        metric_tile("AI suggestions", metrics["diagnoses"], "Generated candidates")
    with col3:
        metric_tile("Users served", metrics["users"], "Registered accounts")
    with col4:
        metric_tile("Critical alerts", metrics["critical"], "Emergency flags")

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        section_title("Dataset intelligence")
        st.plotly_chart(condition_frequency_chart(df), use_container_width=True)
    with right:
        section_title("System posture")
        st.markdown(
            """
            <div class="insight-panel">
                <b>Privacy layer</b><br>
                <span class="muted">Identifiers are redacted before LLM calls.</span>
            </div>
            <div class="insight-panel">
                <b>Clinical safety</b><br>
                <span class="muted">Emergency red flags are surfaced before analysis.</span>
            </div>
            <div class="insight-panel">
                <b>Evidence flow</b><br>
                <span class="muted">RAG context is shown when retrieval data is available.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def analyze_report(df, vector_db):
    page_header(
        "Report analysis",
        "Analyze a medical report",
        "Extract clinical findings, identify abnormal values, retrieve evidence, and generate a role-specific explanation.",
    )

    source_type = "manual"
    filename = None
    input_col, settings_col = st.columns([1.25, 0.75], gap="large")

    with input_col:
        section_title("Report input")
        uploaded_file = st.file_uploader("Upload medical report PDF", type=["pdf"])
        manual_text = st.text_area("Paste symptoms or report text", height=210)

    with settings_col:
        section_title("Analysis settings")
        language = st.selectbox("Explanation language", ["English", "Hindi", "Telugu", "Tamil"])
        st.markdown(
            """
            <div class="callout">
                Use the sample reports in <b>data/sample_reports</b> for a quick demo.
            </div>
            """,
            unsafe_allow_html=True,
        )
        analyze_clicked = st.button("Analyze report", type="primary", use_container_width=True)

    text_data = ""
    if uploaded_file:
        source_type = "pdf"
        filename = uploaded_file.name
        try:
            text_data = extract_text_from_pdf(uploaded_file)
            st.success("PDF text extracted successfully.")
            with st.expander("Extracted report text"):
                st.write(text_data)
        except Exception as exc:
            st.error(str(exc))
            return
    elif manual_text.strip():
        text_data = manual_text.strip()

    if not analyze_clicked:
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

    section_title("Report summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_tile("Symptoms found", len(entities["symptoms"]), "Detected from text")
    with c2:
        metric_tile("Lab values found", len(lab_values), "Parsed measurements")
    with c3:
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-label">Risk level</div>
                <div style="margin-top:0.7rem;">{risk_badge(risk)}</div>
                <div class="metric-note">Based on red flags and abnormalities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if emergencies:
        st.error("Emergency red flags detected. Seek immediate medical care if these symptoms are present.")
        st.dataframe(emergencies, use_container_width=True)

    if privacy["redacted"]:
        st.info("Personal identifiers were redacted before sending text to the AI explanation model.")

    tab_findings, tab_ai, tab_evidence = st.tabs(["Findings", "AI Explanation", "Evidence"])
    with tab_findings:
        left, right = st.columns(2, gap="large")
        with left:
            section_title("Extracted clinical data")
            st.json(entities)
        with right:
            section_title("Lab abnormality panel")
            st.json(abnormalities)

        if lab_values:
            section_title("Lab values overview")
            st.plotly_chart(lab_value_chart(lab_values), use_container_width=True)

        section_title("Dataset-based suggestions")
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

        st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
        st.write(summary)
        st.markdown("</div>", unsafe_allow_html=True)
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

    action_col, feedback_col = st.columns([0.45, 0.55], gap="large")
    with action_col:
        st.download_button(
            "Download summary",
            data=summary,
            file_name=f"medexplain_report_{report_id}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with feedback_col:
        with st.expander("Rate this explanation"):
            rating = st.slider("Usefulness", 1, 5, 4)
            comments = st.text_area("Feedback for improving the assistant")
            if st.button("Save feedback", use_container_width=True):
                save_feedback(st.session_state["user_id"], report_id, rating, comments)
                st.success("Feedback saved.")


def assistant_chat(vector_db):
    page_header(
        "Report chat",
        "Ask about your latest report",
        "Continue the conversation with a report-aware assistant that uses stored summary and evidence context.",
    )

    report = latest_report_for_user(st.session_state["user_id"])
    if not report:
        st.info("Analyze a report first, then come back here to chat about it.")
        return

    summary_col, chat_col = st.columns([0.42, 0.58], gap="large")
    with summary_col:
        section_title("Latest report")
        st.markdown(
            f"""
            <div class="insight-panel">
                <b>Report #{report['id']}</b><br>
                <span class="muted">Created: {report['created_at']}</span><br><br>
                {risk_badge(report['risk'])}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if report.get("diagnoses"):
            st.dataframe(report["diagnoses"], use_container_width=True)

    with chat_col:
        section_title("Question")
        language = st.selectbox("Response language", ["English", "Hindi", "Telugu", "Tamil"], key="chat_language")
        question = st.text_area("Ask a question", placeholder="Example: Why is my WBC value high?", height=140)

        if st.button("Ask assistant", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("Enter a question first.")
                return
            safe_report = {**report, "text": redact_sensitive_text(report["text"])}
            context = retrieve_context(question + "\n" + safe_report["text"], vector_db)
            with st.spinner("Checking your report and evidence..."):
                answer = report_chat(question, safe_report, context, language=language)
            st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
            st.write(answer)
            st.markdown("</div>", unsafe_allow_html=True)
            st.warning("For medical decisions, confirm this with a qualified clinician.")


def history():
    page_header(
        "Report history",
        "Previous analyses",
        "Review stored reports, risk levels, source type, and generated summary snippets.",
    )
    rows = list_user_reports(st.session_state["user_id"])
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No reports analyzed yet.")


def admin_notes():
    page_header(
        "Admin console",
        "Operational monitoring",
        "Track usage, feedback, audit events, report risk distribution, and model evaluation artifacts.",
    )

    metrics = dashboard_metrics()
    feedback = feedback_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_tile("Users", metrics["users"], "Registered accounts")
    with col2:
        metric_tile("Reports", metrics["reports"], "Analyses stored")
    with col3:
        metric_tile("Feedback", feedback["count"], "Rating entries")
    with col4:
        metric_tile("Avg rating", feedback["average_rating"], "Usefulness score")

    section_title("Risk distribution")
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
            with c1:
                metric_tile("Rows", report["rows"], "Evaluation dataset")
            with c2:
                metric_tile("Accuracy", report["accuracy"], "Baseline classifier")
            with c3:
                metric_tile("Macro F1", report["macro_f1"], "Class-balanced signal")
            with c4:
                metric_tile("Top-3", report["top_3_accuracy"], "Candidate coverage")
            st.markdown(f"**Model:** {report['model']}")
            st.markdown(f"**Labels:** {', '.join(report['labels'])}")


def main():
    sidebar_brand()
    if not auth_gate():
        return

    df = load_dataset()
    vector_db = get_db()

    role = st.session_state.get("role", "patient")
    pages = ["Dashboard", "Analyze Report", "Medical Report Chat", "Report History"]
    if role == "admin":
        pages.append("Admin Console")
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
