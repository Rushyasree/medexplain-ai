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
        --med-bg: #eef6f7;
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
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.13), transparent 28rem),
            radial-gradient(circle at 78% 18%, rgba(37, 99, 235, 0.10), transparent 24rem),
            linear-gradient(180deg, #f8fbfc 0%, #eef6f7 100%);
        color: var(--med-ink);
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #0b3142 0%, #0f766e 48%, #123b5d 100%);
        border-right: 0;
        box-shadow: 10px 0 28px rgba(15, 23, 42, 0.10);
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: rgba(255,255,255,0.90);
    }

    [data-testid="stSidebar"] small {
        color: rgba(255,255,255,0.72);
    }

    .app-brand {
        padding: 0.85rem;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 8px;
        margin-bottom: 1rem;
        background: rgba(255,255,255,0.10);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.16);
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #ffffff;
        color: #0f766e;
        font-weight: 800;
        margin-right: 0.5rem;
    }

    .brand-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #ffffff;
    }

    .brand-subtitle {
        display: block;
        color: rgba(255,255,255,0.72);
        font-size: 0.78rem;
        margin-top: 0.15rem;
    }

    .sidebar-mini-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.45rem;
        margin-top: 0.85rem;
    }

    .sidebar-mini {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 8px;
        padding: 0.55rem;
    }

    .sidebar-mini-value {
        color: #ffffff;
        font-weight: 900;
        font-size: 1rem;
        line-height: 1.1;
    }

    .sidebar-mini-label {
        color: rgba(255,255,255,0.70);
        font-size: 0.68rem;
        margin-top: 0.15rem;
    }

    .sidebar-note {
        margin-top: 0.75rem;
        padding: 0.7rem;
        border-radius: 8px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.78);
        font-size: 0.78rem;
        line-height: 1.35;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 8px;
        padding: 0.35rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 8px;
        padding: 0.25rem 0.35rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.10);
    }

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="input"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(255,255,255,0.44);
        border-radius: 8px;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: #ffffff;
        color: #0f766e;
        border: 0;
        box-shadow: 0 8px 18px rgba(2, 6, 23, 0.18);
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #e9fffb;
        color: #0b5f58;
        border: 0;
    }

    .page-shell {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(219,229,238,0.9);
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.045);
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

    .dashboard-hero {
        background:
            linear-gradient(135deg, rgba(15, 118, 110, 0.96), rgba(37, 99, 235, 0.92)),
            linear-gradient(90deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0));
        border-radius: 8px;
        padding: 1.35rem 1.45rem;
        margin-bottom: 1rem;
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .dashboard-hero-title {
        font-size: 2.15rem;
        line-height: 1.12;
        font-weight: 900;
        margin: 0;
        color: #ffffff;
    }

    .dashboard-hero-copy {
        max-width: 820px;
        margin-top: 0.45rem;
        color: rgba(255,255,255,0.88);
        font-size: 0.98rem;
    }

    .hero-chip {
        display: inline-block;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px;
        padding: 0.26rem 0.72rem;
        margin: 0.25rem 0.35rem 0 0;
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .login-stage {
        min-height: calc(100vh - 3rem);
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
        gap: 1rem;
        align-items: stretch;
    }

    .login-hero {
        background:
            linear-gradient(135deg, rgba(20, 33, 61, 0.96), rgba(15, 118, 110, 0.92)),
            linear-gradient(180deg, rgba(37, 99, 235, 0.34), rgba(255, 255, 255, 0));
        color: #ffffff;
        border-radius: 8px;
        padding: 2rem;
        min-height: 520px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid rgba(255,255,255,0.18);
    }

    .login-hero h1 {
        color: #ffffff;
        font-size: 3rem;
        line-height: 1.05;
        font-weight: 900;
        margin: 0.4rem 0 0 0;
        max-width: 760px;
    }

    .login-hero p {
        color: rgba(255,255,255,0.86);
        font-size: 1rem;
        max-width: 680px;
        margin-top: 0.85rem;
        line-height: 1.55;
    }

    .login-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        margin-top: 1.2rem;
    }

    .login-stat {
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 8px;
        padding: 0.85rem;
    }

    .login-stat-value {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 900;
    }

    .login-stat-label {
        color: rgba(255,255,255,0.76);
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    .login-panel {
        background: #ffffff;
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 1.35rem;
        min-height: 520px;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
    }

    .feature-list {
        display: grid;
        gap: 0.7rem;
        margin-top: 1rem;
    }

    .feature-item {
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 0.9rem;
        background: #fbfdff;
    }

    .feature-title {
        color: var(--med-ink);
        font-weight: 850;
        font-size: 0.95rem;
    }

    .feature-copy {
        color: var(--med-muted);
        font-size: 0.84rem;
        margin-top: 0.2rem;
        line-height: 1.42;
    }

    .demo-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        margin-top: 1rem;
    }

    .demo-card {
        border-radius: 8px;
        border: 1px solid var(--med-line);
        padding: 0.8rem;
        background: #ffffff;
    }

    .demo-role {
        color: var(--med-teal);
        font-size: 0.75rem;
        font-weight: 900;
        text-transform: uppercase;
    }

    .demo-login {
        color: var(--med-ink);
        font-size: 0.84rem;
        font-weight: 760;
        margin-top: 0.25rem;
        overflow-wrap: anywhere;
    }

    @media (max-width: 900px) {
        .login-stage {
            grid-template-columns: 1fr;
        }
        .login-grid,
        .demo-strip {
            grid-template-columns: 1fr;
        }
        .login-hero h1 {
            font-size: 2.15rem;
        }
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
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
    }

    .metric-tile.accent-teal { border-top: 4px solid #0f766e; }
    .metric-tile.accent-blue { border-top: 4px solid #2563eb; }
    .metric-tile.accent-amber { border-top: 4px solid #b54708; }
    .metric-tile.accent-red { border-top: 4px solid #b42318; }

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
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }

    .workflow-card {
        background: #ffffff;
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 150px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }

    .workflow-step {
        color: var(--med-teal);
        font-size: 0.76rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .workflow-title {
        color: var(--med-ink);
        font-size: 1rem;
        font-weight: 850;
        margin-top: 0.35rem;
    }

    .workflow-copy {
        color: var(--med-muted);
        font-size: 0.86rem;
        margin-top: 0.35rem;
        line-height: 1.45;
    }

    .readiness-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.72rem 0;
        border-bottom: 1px solid var(--med-line);
    }

    .readiness-row:last-child { border-bottom: 0; }

    .readiness-label {
        color: var(--med-ink);
        font-weight: 760;
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
        border: 1px solid #0f766e;
    }

    div[data-testid="stTabs"] button {
        font-weight: 750;
    }

    textarea, input, select {
        border-radius: 8px !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        border: 1px solid #cbd5e1;
        background: #ffffff;
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
            <div class="sidebar-mini-grid">
                <div class="sidebar-mini">
                    <div class="sidebar-mini-value">AI</div>
                    <div class="sidebar-mini-label">report explain</div>
                </div>
                <div class="sidebar-mini">
                    <div class="sidebar-mini-value">RAG</div>
                    <div class="sidebar-mini-label">evidence flow</div>
                </div>
            </div>
            <div class="sidebar-note">
                Secure patient, doctor, and admin workflows for placement-ready healthcare AI demos.
            </div>
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


def metric_tile(label: str, value, note: str = "", accent: str = "") -> None:
    accent_class = f" accent-{accent}" if accent else ""
    st.markdown(
        f"""
        <div class="metric-tile{accent_class}">
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


def login_landing() -> None:
    st.markdown(
        """
        <div class="login-stage">
            <div class="login-hero">
                <div>
                    <div class="page-eyebrow" style="color:rgba(255,255,255,0.82);">Healthcare AI platform</div>
                    <h1>Explain medical reports with clarity, evidence, and safety.</h1>
                    <p>
                        MedExplain AI turns report text, PDF findings, lab values, and clinical signals into
                        patient-friendly explanations and doctor-oriented summaries with privacy-aware AI workflows.
                    </p>
                    <div class="login-grid">
                        <div class="login-stat">
                            <div class="login-stat-value">8K+</div>
                            <div class="login-stat-label">medical rows processed</div>
                        </div>
                        <div class="login-stat">
                            <div class="login-stat-value">3</div>
                            <div class="login-stat-label">role-based workspaces</div>
                        </div>
                        <div class="login-stat">
                            <div class="login-stat-value">4</div>
                            <div class="login-stat-label">explanation languages</div>
                        </div>
                    </div>
                </div>
                <div>
                    <span class="hero-chip">NLP extraction</span>
                    <span class="hero-chip">Lab abnormality detection</span>
                    <span class="hero-chip">RAG evidence</span>
                    <span class="hero-chip">Admin analytics</span>
                </div>
            </div>
            <div class="login-panel">
                <div class="page-eyebrow">Demo access</div>
                <h2 style="margin:0;color:#14213d;">Start with a demo account</h2>
                <p class="page-subtitle" style="margin-bottom:1rem;">
                    Use the sidebar to log in. The accounts below are seeded for quick placement demos.
                </p>
                <div class="demo-strip">
                    <div class="demo-card">
                        <div class="demo-role">Patient</div>
                        <div class="demo-login">patient_demo<br>Patient@123</div>
                    </div>
                    <div class="demo-card">
                        <div class="demo-role">Doctor</div>
                        <div class="demo-login">doctor_demo<br>Doctor@123</div>
                    </div>
                    <div class="demo-card">
                        <div class="demo-role">Admin</div>
                        <div class="demo-login">admin_demo<br>Admin@123</div>
                    </div>
                </div>
                <div class="feature-list">
                    <div class="feature-item">
                        <div class="feature-title">Analyze reports in seconds</div>
                        <div class="feature-copy">Upload a PDF or paste sample report text to extract symptoms, labs, risk signals, and explanations.</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-title">Designed for placement demos</div>
                        <div class="feature-copy">Includes sample reports, model card, FastAPI skeleton, Docker, Render config, and admin console.</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-title">Responsible AI built in</div>
                        <div class="feature-copy">Privacy redaction, emergency detection, audit logs, confidence ranking, and medical disclaimers are included.</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard(df):
    st.markdown(
        """
        <div class="dashboard-hero">
            <div class="page-eyebrow" style="color:rgba(255,255,255,0.82);">Operations dashboard</div>
            <h1 class="dashboard-hero-title">MedExplain command center</h1>
            <div class="dashboard-hero-copy">
                A polished clinical AI workspace for analyzing reports, tracking risk signals, reviewing model readiness,
                and presenting healthcare intelligence in placement demos.
            </div>
            <div style="margin-top:0.75rem;">
                <span class="hero-chip">Privacy-first</span>
                <span class="hero-chip">Role-based</span>
                <span class="hero-chip">RAG-ready</span>
                <span class="hero-chip">Demo-ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = dashboard_metrics()
    feedback = feedback_summary()
    model_report = load_evaluation_report()
    risk_rows = risk_distribution()
    recent_rows = list_user_reports(st.session_state["user_id"], limit=5)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_tile("Reports analyzed", metrics["reports"], "Stored report reviews", "teal")
    with col2:
        metric_tile("AI suggestions", metrics["diagnoses"], "Generated candidates", "blue")
    with col3:
        metric_tile("Avg feedback", feedback["average_rating"], f"{feedback['count']} rating entries", "amber")
    with col4:
        metric_tile("Critical alerts", metrics["critical"], "Emergency flags", "red")

    flow_cols = st.columns(4)
    steps = [
        ("01", "Upload or paste report", "PDF and manual text workflows support quick demos and real report review."),
        ("02", "Extract findings", "Symptoms, conditions, lab values, and abnormality meanings are structured."),
        ("03", "Generate explanation", "Patient and doctor modes receive different grounded summaries."),
        ("04", "Track outcomes", "Audit logs, feedback, reports, and metrics support project evaluation."),
    ]
    for column, (step, title, copy) in zip(flow_cols, steps):
        with column:
            st.markdown(
                f"""
                <div class="workflow-card">
                    <div class="workflow-step">{step}</div>
                    <div class="workflow-title">{title}</div>
                    <div class="workflow-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        section_title("Dataset intelligence")
        st.plotly_chart(condition_frequency_chart(df), use_container_width=True)
    with right:
        section_title("Risk distribution")
        st.plotly_chart(risk_distribution_chart(risk_rows), use_container_width=True)

    lower_left, lower_right = st.columns([0.95, 1.05], gap="large")
    with lower_left:
        section_title("Platform readiness")
        model_status = "Ready" if model_report.get("available") else "Pending"
        st.markdown(
            f"""
            <div class="insight-panel">
                <div class="readiness-row">
                    <span class="readiness-label">Privacy redaction</span>
                    <span class="status-pill risk-low">Active</span>
                </div>
                <div class="readiness-row">
                    <span class="readiness-label">Emergency detection</span>
                    <span class="status-pill risk-low">Active</span>
                </div>
                <div class="readiness-row">
                    <span class="readiness-label">Model metrics</span>
                    <span class="status-pill risk-{'low' if model_report.get('available') else 'elevated'}">{model_status}</span>
                </div>
                <div class="readiness-row">
                    <span class="readiness-label">Demo accounts</span>
                    <span class="status-pill risk-low">Seeded</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with lower_right:
        section_title("Recent activity")
        if recent_rows:
            st.dataframe(recent_rows, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="insight-panel">
                    <b>No report history yet</b><br>
                    <span class="muted">Open Analyze Report and use a sample report to populate this dashboard.</span>
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
        login_landing()
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
