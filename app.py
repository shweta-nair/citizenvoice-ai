"""
CitizenVoice AI — Main Application Entry Point
AI-Powered Public Complaint Intelligence and Analytics Platform

Run with:  streamlit run app.py
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(__file__))

st.set_page_config(
    page_title="CitizenVoice AI",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import apply_theme
from utils.state import get_db_connection, get_models, get_data

apply_theme()

# Warm up shared resources once at startup (cached across pages/sessions)
get_db_connection()
get_models()

# --------------------------------------------------------------------------
# Sidebar branding (appears above the page nav on every page)
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        "<h2 class='cv-sidebar-title'>🏛 CitizenVoice <span style='color:#00B5D8;'>AI</span></h2>"
        "<p class='cv-sidebar-subtitle'>Public Complaint Intelligence Platform</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

# --------------------------------------------------------------------------
# Page registry (explicit titles/icons/order, independent of filenames)
# --------------------------------------------------------------------------

home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
upload_page = st.Page("pages/upload.py", title="Upload Data", icon="📤")
analysis_page = st.Page("pages/analysis.py", title="AI Analysis", icon="🤖")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")
district_page = st.Page("pages/district.py", title="District Intelligence", icon="🗺")
reports_page = st.Page("pages/reports.py", title="Reports", icon="📥")
settings_page = st.Page("pages/settings.py", title="Settings", icon="⚙")

nav = st.navigation([
    home_page, upload_page, analysis_page, dashboard_page,
    district_page, reports_page, settings_page,
])

# Footer status (below nav, still in sidebar)
with st.sidebar:
    st.markdown("---")
    df_preview = get_data()
    st.caption(f"📡 Live database: **{len(df_preview)}** conversations")
    st.caption("Status: 🟢 All systems operational")

nav.run()
