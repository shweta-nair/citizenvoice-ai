"""CitizenVoice AI — District Intelligence Page"""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, kpi_card
from utils.state import get_data
from utils.preprocessing import extract_corpus_keywords
from utils import charts

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>🗺 District Intelligence</h1>
        <p>Filter by district, date range, and department to surface dominant issues,
        sentiment trends, and priority hotspots.</p>
    </div>""",
    unsafe_allow_html=True,
)

df = get_data()
if df.empty:
    st.warning("No data available yet.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# --------------------------------------------------------------------------
# Filters
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([1, 1.4, 1])

with f1:
    districts = ["All Districts"] + sorted(df["district"].unique().tolist())
    selected_district = st.selectbox("District", districts)

with f2:
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

with f3:
    depts = ["All Departments"] + sorted(df["department"].unique().tolist())
    selected_dept = st.selectbox("Department", depts)
st.markdown('</div>', unsafe_allow_html=True)

filtered = df.copy()
if selected_district != "All Districts":
    filtered = filtered[filtered["district"] == selected_district]
if selected_dept != "All Departments":
    filtered = filtered[filtered["department"] == selected_dept]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

if filtered.empty:
    st.warning("No conversations match the selected filters.")
    st.stop()

# --------------------------------------------------------------------------
# KPIs for filtered view
# --------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Complaint Volume", f"{len(filtered):,}")
with k2:
    kpi_card("Dominant Issue", filtered["department"].value_counts().idxmax())
with k3:
    neg_pct = (filtered["sentiment"] == "Negative").mean() * 100
    kpi_card("Negative Sentiment", f"{neg_pct:.1f}%")
with k4:
    crit = int((filtered["priority"] == "Critical").sum())
    kpi_card("Critical Cases", f"{crit:,}")

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Charts
# --------------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.complaints_by_department(filtered), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.plotly_chart(charts.priority_distribution(filtered), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="cv-card">', unsafe_allow_html=True)
if selected_district != "All Districts":
    st.plotly_chart(charts.sentiment_trend_by_district(df, selected_district), use_container_width=True)
else:
    st.plotly_chart(charts.sentiment_distribution(filtered), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.plotly_chart(charts.district_dept_heatmap(filtered), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.plotly_chart(charts.priority_heatmap(filtered), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Top keywords for this filtered slice
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
keyword_counts = extract_corpus_keywords(filtered["transcript"].tolist(), top_n=12)
st.plotly_chart(charts.top_keywords_chart(keyword_counts), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("🔎 Browse filtered conversation records"):
    st.dataframe(
        filtered[["date", "district", "department", "sentiment", "priority", "transcript"]]
        .sort_values("date", ascending=False),
        use_container_width=True, height=350,
    )
