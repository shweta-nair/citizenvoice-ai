"""CitizenVoice AI — AI Analysis Page"""

import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, sentiment_badge, priority_badge
from utils.inference import analyze_transcript

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>🤖 AI Analysis</h1>
        <p>Run the full NLP pipeline on any transcript and inspect department routing,
        sentiment, priority, and extracted keywords with confidence scores.</p>
    </div>""",
    unsafe_allow_html=True,
)

sample_options = {
    "— Type your own —": "",
    "Critical electricity outage": (
        "Support Executive: Thank you for calling the citizen helpline, how can I help you today?\n"
        "Citizen: Hello, calling from Kozhikode. A transformer exploded near Market Road and the "
        "entire area has had no electricity since last night. This is an emergency, we need help right now.\n"
        "Support Executive: I understand, escalating this immediately."
    ),
    "Routine water supply query": (
        "Support Executive: Thank you for calling the citizen helpline, how can I help you today?\n"
        "Citizen: Hi, I just wanted to ask about the water supply schedule for Ward 7 this week.\n"
        "Support Executive: Sure, let me check that for you."
    ),
    "Appreciation for road repair": (
        "Support Executive: Thank you for calling the citizen helpline, how can I help you today?\n"
        "Citizen: I just wanted to thank the Public Works Department, the road repair work near "
        "MG Road in Thrissur was completed very quickly and the quality is excellent.\n"
        "Support Executive: That's wonderful to hear, I will pass it on to the team."
    ),
}

choice = st.selectbox("Try a sample transcript, or write your own below:", list(sample_options.keys()))
default_text = sample_options[choice]

transcript_input = st.text_area(
    "Conversation Transcript",
    value=default_text,
    height=200,
    placeholder="Paste or type a citizen-support conversation transcript here...",
)

run = st.button("🔍 Run AI Analysis", type="primary")

if run:
    if not transcript_input.strip():
        st.warning("Please enter a transcript first.")
    else:
        with st.spinner("Running classification, sentiment, and priority models..."):
            result = analyze_transcript(transcript_input)

        st.markdown("### 📋 Transcript")
        st.markdown(
            f"""<div class="cv-card"><p style="color:#3D4A5C; white-space:pre-wrap;">{transcript_input}</p></div>""",
            unsafe_allow_html=True,
        )

        st.markdown("### 🎯 Prediction Cards")
        c1, c2, c3 = st.columns(3)

        with c1:
            conf = result["department_confidence"]
            conf_pct = f"{conf*100:.1f}%" if conf is not None else "N/A"
            st.markdown(
                f"""<div class="cv-card">
                <div class="cv-kpi-label">Detected Department</div>
                <div class="cv-kpi-value" style="font-size:22px;">{result['department']}</div>
                <p style="color:#5A6B7E; margin-top:8px; font-size:13px;">Confidence: <b>{conf_pct}</b></p>
                </div>""",
                unsafe_allow_html=True,
            )

        with c2:
            conf = result["sentiment_confidence"]
            conf_pct = f"{conf*100:.1f}%" if conf is not None else "N/A"
            st.markdown(
                f"""<div class="cv-card">
                <div class="cv-kpi-label">Sentiment</div>
                <div style="margin-top:6px;">{sentiment_badge(result['sentiment'])}</div>
                <p style="color:#5A6B7E; margin-top:10px; font-size:13px;">Confidence: <b>{conf_pct}</b></p>
                </div>""",
                unsafe_allow_html=True,
            )

        with c3:
            conf = result["priority_confidence"]
            conf_pct = f"{conf*100:.1f}%" if conf is not None else "N/A"
            st.markdown(
                f"""<div class="cv-card">
                <div class="cv-kpi-label">Priority</div>
                <div style="margin-top:6px;">{priority_badge(result['priority'])}</div>
                <p style="color:#5A6B7E; margin-top:10px; font-size:13px;">Confidence: <b>{conf_pct}</b></p>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("### 🔑 Keywords & Locations")
        kw_col, loc_col = st.columns(2)
        with kw_col:
            kw_html = " ".join(
                f'<span class="cv-badge" style="background:#E8F0FB; color:#0066CC; margin:3px;">{k}</span>'
                for k in result["keywords"]
            ) or "<i>No significant keywords extracted.</i>"
            st.markdown(f"""<div class="cv-card"><b>Issue Keywords</b><br><br>{kw_html}</div>""", unsafe_allow_html=True)
        with loc_col:
            loc_html = " ".join(
                f'<span class="cv-badge" style="background:#E8F5E9; color:#1E8E3E; margin:3px;">{l.title()}</span>'
                for l in result["locations"]
            ) or "<i>No district names detected in text.</i>"
            st.markdown(f"""<div class="cv-card"><b>Detected Locations</b><br><br>{loc_html}</div>""", unsafe_allow_html=True)

        st.caption(
            "Note: this analysis is a preview run and is not automatically saved to the database. "
            "Use the **Upload Data** page to analyze and persist conversations into the live dataset."
        )
