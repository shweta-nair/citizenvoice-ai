"""CitizenVoice AI — Reports Page"""

import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, kpi_card
from utils.state import get_data
from utils.report_generator import generate_csv_report, generate_pdf_report

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>📥 Reports</h1>
        <p>Generate downloadable CSV exports and formatted PDF intelligence reports for
        government decision-makers.</p>
    </div>""",
    unsafe_allow_html=True,
)

df = get_data()
if df.empty:
    st.warning("No data available yet.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# --------------------------------------------------------------------------
# Report scope filters
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.markdown("#### Report Scope")
f1, f2, f3 = st.columns(3)
with f1:
    districts = ["All Districts"] + sorted(df["district"].unique().tolist())
    rep_district = st.selectbox("District", districts, key="rep_district")
with f2:
    depts = ["All Departments"] + sorted(df["department"].unique().tolist())
    rep_dept = st.selectbox("Department", depts, key="rep_dept")
with f3:
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    rep_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="rep_range")
st.markdown('</div>', unsafe_allow_html=True)

scoped = df.copy()
if rep_district != "All Districts":
    scoped = scoped[scoped["district"] == rep_district]
if rep_dept != "All Departments":
    scoped = scoped[scoped["department"] == rep_dept]
if isinstance(rep_range, tuple) and len(rep_range) == 2:
    start, end = pd.to_datetime(rep_range[0]), pd.to_datetime(rep_range[1])
    scoped = scoped[(scoped["date"] >= start) & (scoped["date"] <= end)]

st.markdown(f"**{len(scoped):,}** conversations match the selected report scope.")

# --------------------------------------------------------------------------
# Summary preview
# --------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    kpi_card("Conversations in Scope", f"{len(scoped):,}")
with c2:
    top_dept = scoped["department"].value_counts().idxmax() if not scoped.empty else "N/A"
    kpi_card("Top Department", top_dept)
with c3:
    crit = int((scoped["priority"] == "Critical").sum()) if not scoped.empty else 0
    kpi_card("Critical Cases", f"{crit:,}")

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Downloads
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.markdown("#### 📄 Download Reports")
dl1, dl2 = st.columns(2)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

with dl1:
    if not scoped.empty:
        csv_bytes = generate_csv_report(scoped)
        st.download_button(
            "⬇ Download CSV Report",
            data=csv_bytes,
            file_name=f"citizenvoice_report_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇ Download CSV Report", disabled=True, use_container_width=True)

with dl2:
    if not scoped.empty:
        pdf_bytes = generate_pdf_report(scoped)
        st.download_button(
            "⬇ Download PDF Intelligence Report",
            data=pdf_bytes,
            file_name=f"citizenvoice_report_{timestamp}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.button("⬇ Download PDF Intelligence Report", disabled=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Department summary table
# --------------------------------------------------------------------------
st.markdown('<div class="cv-card">', unsafe_allow_html=True)
st.markdown("#### 🏛 Department Summary")
if not scoped.empty:
    summary = scoped.groupby("department").agg(
        total=("id", "count"),
        critical=("priority", lambda s: (s == "Critical").sum()),
        high=("priority", lambda s: (s == "High").sum()),
        negative_pct=("sentiment", lambda s: round((s == "Negative").mean() * 100, 1)),
    ).reset_index().sort_values("total", ascending=False)
    summary.columns = ["Department", "Total Complaints", "Critical", "High", "Negative %"]
    st.dataframe(summary, use_container_width=True, hide_index=True)
else:
    st.info("No records in the current scope.")
st.markdown('</div>', unsafe_allow_html=True)
