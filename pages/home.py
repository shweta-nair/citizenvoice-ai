"""CitizenVoice AI — Home Page"""

import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, kpi_card
from utils.state import get_data

apply_theme()

df = get_data()

st.markdown(
    """<div class="cv-header-bar">
        <h1>🏛 CitizenVoice AI</h1>
        <p>AI-Powered Public Complaint Intelligence and Analytics Platform — turning citizen-support
        conversations into actionable intelligence for government decision-makers.</p>
    </div>""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Top-level KPIs
# --------------------------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total Conversations", f"{len(df):,}")
with c2:
    kpi_card("Departments Covered", f"{df['department'].nunique()}")
with c3:
    kpi_card("Districts Monitored", f"{df['district'].nunique()}")
with c4:
    high_priority = int(df["priority"].isin(["High", "Critical"]).sum())
    kpi_card("High / Critical Cases", f"{high_priority:,}")

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Project overview
# --------------------------------------------------------------------------

col_left, col_right = st.columns([1.4, 1])

with col_left:
    st.markdown(
        """<div class="cv-card">
        <h3>📋 Project Overview</h3>
        <p style="color:#3D4A5C; line-height:1.7;">
        Government departments receive thousands of citizen complaints every day through
        support calls, help desks, and grievance centers. These conversations contain
        valuable information but are largely unstructured and difficult to analyze.
        </p>
        <p style="color:#3D4A5C; line-height:1.7;">
        <b>CitizenVoice AI</b> is not another complaint portal — it is an intelligence layer
        that sits on top of citizen-support conversations. The platform automatically classifies
        which department a complaint belongs to, detects sentiment and urgency, extracts
        keywords and locations, and surfaces district-level and department-level trends so
        decision-makers can see which public services are deteriorating and where to act first.
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="cv-card">
        <h3>🔁 How It Works</h3>
        <p style="color:#3D4A5C; line-height:2;">
        <b>1.</b> A citizen speaks to a support executive about an issue<br>
        <b>2.</b> The executive records the conversation or uploads the transcript<br>
        <b>3.</b> The AI Analysis Engine classifies department, sentiment, priority, and keywords<br>
        <b>4.</b> Results flow into the Analytics Dashboard and District Intelligence views<br>
        <b>5.</b> Government departments get real-time, data-driven insight into citizen issues
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        """<div class="cv-card">
        <h3>⚙ System Capabilities</h3>
        <ul style="color:#3D4A5C; line-height:2.1;">
            <li>🤖 <b>Complaint Classification</b> — auto-routes to the responsible department</li>
            <li>💬 <b>Sentiment Analysis</b> — Positive / Neutral / Negative with a confidence score</li>
            <li>🚨 <b>Priority Detection</b> — Low / Medium / High / Critical urgency tiers</li>
            <li>🔑 <b>Keyword Extraction</b> — recurring issues, entities, and locations</li>
            <li>📈 <b>Trend Analysis</b> — department, district, and time-based patterns</li>
            <li>🗺 <b>District Intelligence</b> — filterable district-level deep dives</li>
            <li>📥 <b>Reporting</b> — one-click CSV and PDF intelligence reports</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="cv-card">
        <h3>🏷 Categories Monitored</h3>
        <p style="color:#3D4A5C;">Water Supply · Electricity · Roads · Waste Management ·
        Healthcare · Transport · Education · Internet Services · Public Safety ·
        Government Documentation</p>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.info("👉 Use the sidebar to upload new conversations, run AI analysis, or explore the analytics dashboard.")
