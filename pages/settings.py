"""CitizenVoice AI — Settings Page"""

import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme
from utils.state import get_data, get_models, refresh_data
from database.db import init_db, seed_from_csv

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>⚙ Settings</h1>
        <p>System information, model status, and data management.</p>
    </div>""",
    unsafe_allow_html=True,
)

df = get_data()
models = get_models()

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""<div class="cv-card">
        <h3>🧠 AI Model Status</h3>
        <p style="color:#3D4A5C;">
        ✅ Department Classifier — loaded (TF-IDF + Logistic Regression)<br>
        ✅ Sentiment Model — loaded (TF-IDF + Logistic Regression)<br>
        ✅ Priority Model — loaded (TF-IDF + Logistic Regression)
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="cv-card">
        <h3>🗄 Database</h3>
        <p style="color:#3D4A5C;">
        Engine: SQLite<br>
        Records: <b>{len(df):,}</b><br>
        Districts: <b>{df['district'].nunique()}</b><br>
        Departments: <b>{df['department'].nunique()}</b>
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """<div class="cv-card">
        <h3>ℹ About CitizenVoice AI</h3>
        <p style="color:#3D4A5C; line-height:1.7;">
        An AI-powered public complaint intelligence platform that transforms citizen-support
        conversations into actionable analytics for government departments. Built with
        Streamlit, scikit-learn, and Plotly as a one-week proof-of-concept MVP.
        </p>
        <p style="color:#5A6B7E; font-size:13px;">Version 1.0.0 (MVP)</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.markdown("### 🧹 Data Management")
    st.caption("Resets the database back to the original 1,000-record seed dataset and removes any uploaded conversations.")
    confirm = st.checkbox("I understand this will remove uploaded conversations.")
    if st.button("♻ Reset Database to Seed Data", disabled=not confirm):
        conn = init_db(reset=True)
        seed_from_csv(conn)
        refresh_data()
        st.success("Database reset to the original seed dataset.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
