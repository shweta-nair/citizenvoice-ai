"""
CitizenVoice AI - Shared Theme

Applies the "Government Command Center" visual theme. Call apply_theme()
near the top of every page script (st.set_page_config is called only once,
in app.py, but CSS injection is safe to repeat on every page).
"""

import streamlit as st

PRIMARY = "#0066CC"
SECONDARY = "#1E8E3E"
ACCENT = "#00B5D8"
BG = "#F5F7FA"

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Malayalam:wght@400;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', 'Noto Sans Malayalam', sans-serif;
}

:root {
    --cv-primary: #0066CC;
    --cv-secondary: #1E8E3E;
    --cv-accent: #00B5D8;
    --cv-bg: #F5F7FA;
    --cv-text: #0B2540;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--cv-bg);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B2540 0%, #0E2F52 100%);
}
[data-testid="stSidebar"] * {
    color: #E8F0FB !important;
}

h1, h2, h3 {
    color: var(--cv-text);
    font-weight: 700;
}

.cv-card {
    background: white;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(11, 37, 64, 0.06);
    border: 1px solid #E7ECF2;
    margin-bottom: 14px;
}

.cv-kpi-label {
    font-size: 13px;
    font-weight: 600;
    color: #5A6B7E;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.cv-kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: var(--cv-primary);
    margin-top: 2px;
}

.cv-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.cv-badge-critical { background: #FDEAEA; color: #D93025; }
.cv-badge-high { background: #FFF1E0; color: #FF7A00; }
.cv-badge-medium { background: #FFF8E1; color: #B8860B; }
.cv-badge-low { background: #E8F5E9; color: #1E8E3E; }

.cv-badge-positive { background: #E8F5E9; color: #1E8E3E; }
.cv-badge-neutral { background: #FFF8E1; color: #B8860B; }
.cv-badge-negative { background: #FDEAEA; color: #D93025; }

.cv-header-bar {
    background: linear-gradient(135deg, #0066CC 0%, #00B5D8 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-bottom: 22px;
}
.cv-header-bar h1 { color: white !important; margin-bottom: 4px; }
.cv-header-bar p { color: #E8F4FF; margin: 0; font-size: 15px; }

div[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
    border: 1px solid #E7ECF2;
    box-shadow: 0 2px 10px rgba(11, 37, 64, 0.05);
}

.stButton > button {
    background-color: var(--cv-primary);
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    padding: 0.5em 1.4em;
}
.stButton > button:hover {
    background-color: #004C99;
    color: white;
}

.cv-sidebar-title {
    color: white !important;
    margin-bottom: 0;
}
.cv-sidebar-subtitle {
    color: #9FB3C8 !important;
    font-size: 12.5px;
    margin-top: 2px;
}
</style>
"""


def apply_theme():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def sentiment_badge(label: str) -> str:
    cls = {"Positive": "cv-badge-positive", "Neutral": "cv-badge-neutral", "Negative": "cv-badge-negative"}.get(label, "cv-badge-neutral")
    return f'<span class="cv-badge {cls}">{label}</span>'


def priority_badge(label: str) -> str:
    cls = {"Low": "cv-badge-low", "Medium": "cv-badge-medium", "High": "cv-badge-high", "Critical": "cv-badge-critical"}.get(label, "cv-badge-low")
    return f'<span class="cv-badge {cls}">{label}</span>'


def kpi_card(label: str, value: str):
    st.markdown(
        f"""<div class="cv-card">
                <div class="cv-kpi-label">{label}</div>
                <div class="cv-kpi-value">{value}</div>
            </div>""",
        unsafe_allow_html=True,
    )
