from __future__ import annotations

import streamlit as st

from modules.database import User, log_audit, session_scope
from modules.security import create_access_token, hash_password, verify_password


VALID_ROLES = ("patient", "doctor", "admin")


def _set_session(user: User) -> None:
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user.id
    st.session_state["username"] = user.username
    st.session_state["role"] = user.role
    st.session_state["access_token"] = create_access_token(user.id, user.role)


def register_panel() -> None:
    st.sidebar.markdown("### Create account")
    st.sidebar.caption("Create a role-based workspace for patient, doctor, or admin demos.")
    username = st.sidebar.text_input("Username", key="register_username")
    full_name = st.sidebar.text_input("Full name", key="register_full_name")
    password = st.sidebar.text_input("Password", type="password", key="register_password")
    role = st.sidebar.selectbox("Role", VALID_ROLES, key="register_role")
    consent = st.sidebar.checkbox("I consent to storing report analysis data")

    if st.sidebar.button("Register", type="primary", use_container_width=True):
        if not username or not password:
            st.sidebar.error("Username and password are required.")
            return
        if len(password) < 8:
            st.sidebar.error("Use at least 8 characters for the password.")
            return
        if not consent:
            st.sidebar.error("Consent is required for healthcare data processing.")
            return

        created_user_id = None
        with session_scope() as session:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                st.sidebar.error("User already exists.")
                return
            user = User(
                username=username,
                full_name=full_name,
                password_hash=hash_password(password),
                role=role,
                consent_given=1,
            )
            session.add(user)
            session.flush()
            created_user_id = user.id
        log_audit("user_registered", created_user_id, {"role": role})
        st.sidebar.success("Registration successful. Please log in.")


def login_panel() -> None:
    st.sidebar.markdown("### Login")
    st.sidebar.caption("Use a demo account or your registered workspace.")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")

    st.sidebar.markdown(
        """
        <div style="
            font-size:0.80rem;
            color:rgba(255,255,255,0.82);
            margin:0.45rem 0 0.85rem 0;
            padding:0.7rem;
            border-radius:8px;
            border:1px solid rgba(255,255,255,0.16);
            background:rgba(255,255,255,0.10);
            line-height:1.45;">
            <b style="color:#ffffff;">Demo credentials</b><br>
            Patient: <b style="color:#ffffff;">patient_demo</b> / <b style="color:#ffffff;">Patient@123</b><br>
            Doctor: <b style="color:#ffffff;">doctor_demo</b> / <b style="color:#ffffff;">Doctor@123</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Login", type="primary", use_container_width=True):
        with session_scope() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user or not verify_password(password, user.password_hash):
                st.sidebar.error("Invalid credentials.")
                return
            user_id = user.id
            role = user.role
            _set_session(user)
        log_audit("user_logged_in", user_id, {"role": role})
        st.rerun()


def auth_gate() -> bool:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        role = st.session_state.get("role", "patient")
        username = st.session_state.get("username", "user")
        st.sidebar.success(f"{username} · {role.title()}")
        if st.sidebar.button("Logout", use_container_width=True):
            log_audit("user_logged_out", st.session_state.get("user_id"))
            st.session_state.clear()
            st.rerun()
        return True

    choice = st.sidebar.radio("Account", ["Login", "Register"])
    if choice == "Register":
        register_panel()
    else:
        login_panel()
    return False
