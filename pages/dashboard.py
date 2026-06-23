"""CitizenVoice AI — Analytics Dashboard Page"""

import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, kpi_card
from utils.state import get_data
from utils.preprocessing import extract_corpus_keywords
from utils import charts

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>📊 Analytics Dashboard</h1>
        <p>Department, district, sentiment, and priority intelligence across all citizen conversations.</p>
    </div>""",
    unsafe_allow_html=True,
)

df = get_data()

if df.empty:
    st.warning("No data available yet.")
    st.stop()

# --------------------------------------------------------------------------
# KPIs
# --------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    kpi_card("Total Complaints", f"{len(df):,}")
with c2:
    top_dept = df["department"].value_counts().idxmax()
    kpi_card("Top Department", top_dept)
with c3:
    neg_pct = (df["sentiment"] == "Negative").mean() * 100
    kpi_card("Negative Sentiment", f"{neg_pct:.1f}%")
with c4:
    high_count = df["priority"].isin(["High", "Critical"]).sum()
    kpi_card("High Priority Cases", f"{high_count:,}")
with c5:
    top_district = df["district"].value_counts().idxmax()
    kpi_card("Most Affected District", top_district)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Charts row 1
# --------------------------------------------------------------------------
col1, col2 = st.columns([1.2, 1])
with col1:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.complaints_by_department(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.sentiment_distribution(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Charts row 2
# --------------------------------------------------------------------------
col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.complaints_by_district(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.priority_distribution(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Charts row 3
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.plotly_chart(charts.monthly_trends(df), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="cv-card">', unsafe_allow_html=True)
keyword_counts = extract_corpus_keywords(df["transcript"].tolist(), top_n=15)
st.plotly_chart(charts.top_keywords_chart(keyword_counts), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Raw data explorer
# --------------------------------------------------------------------------
with st.expander("🔎 Browse raw conversation records"):
    st.dataframe(
        df[["date", "district", "department", "sentiment", "priority", "transcript"]]
        .sort_values("date", ascending=False),
        use_container_width=True, height=350,
    )
