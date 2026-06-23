"""CitizenVoice AI — Upload Conversations Page"""

import os
import sys
from datetime import date

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import apply_theme, sentiment_badge, priority_badge
from utils.state import get_db_connection, refresh_data
from utils.inference import analyze_transcript
from database.db import insert_conversation

apply_theme()

st.markdown(
    """<div class="cv-header-bar">
        <h1>📤 Upload Conversations</h1>
        <p>Upload a CSV of transcripts, a plain text file, or paste a single conversation directly.</p>
    </div>""",
    unsafe_allow_html=True,
)

conn = get_db_connection()

DISTRICTS = [
    "Ernakulam", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Alappuzha",
    "Kannur", "Kottayam", "Palakkad", "Idukki", "Wayanad",
]

if "pending_batch" not in st.session_state:
    st.session_state["pending_batch"] = None  # list of dicts: {transcript, district, date}

tab_csv, tab_txt, tab_paste = st.tabs(["📄 Upload CSV", "📝 Upload TXT", "✍️ Paste Transcript"])

# --------------------------------------------------------------------------
# CSV upload
# --------------------------------------------------------------------------
with tab_csv:
    st.markdown(
        "Upload a CSV with at least a **`transcript`** column. Optional columns: "
        "`district`, `date` (YYYY-MM-DD). Rows missing `district`/`date` default to "
        "Ernakulam and today's date."
    )
    csv_file = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_uploader")
    if csv_file is not None:
        try:
            csv_df = pd.read_csv(csv_file)
            if "transcript" not in csv_df.columns:
                st.error("The CSV must contain a 'transcript' column.")
            else:
                st.success(f"Loaded {len(csv_df)} rows.")
                st.dataframe(csv_df.head(10), use_container_width=True, height=220)
                batch = []
                for _, row in csv_df.iterrows():
                    batch.append({
                        "transcript": str(row.get("transcript", "")),
                        "district": str(row.get("district", "Ernakulam")) if pd.notna(row.get("district", None)) else "Ernakulam",
                        "date": str(row.get("date", date.today().isoformat())) if pd.notna(row.get("date", None)) else date.today().isoformat(),
                    })
                st.session_state["pending_batch"] = batch
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

# --------------------------------------------------------------------------
# TXT upload
# --------------------------------------------------------------------------
with tab_txt:
    st.markdown(
        "Upload a `.txt` file. Use a line containing only `---` to separate multiple "
        "transcripts in one file (otherwise the whole file is treated as one conversation)."
    )
    txt_file = st.file_uploader("Choose a TXT file", type=["txt"], key="txt_uploader")
    txt_district = st.selectbox("District for this upload", DISTRICTS, key="txt_district")
    txt_date = st.date_input("Date", value=date.today(), key="txt_date")
    if txt_file is not None:
        content = txt_file.read().decode("utf-8", errors="ignore")
        parts = [p.strip() for p in content.split("\n---\n") if p.strip()]
        if not parts:
            parts = [content.strip()]
        st.success(f"Found {len(parts)} transcript(s) in file.")
        with st.expander("Preview"):
            for p in parts[:3]:
                st.text(p[:400] + ("..." if len(p) > 400 else ""))
        batch = [{"transcript": p, "district": txt_district, "date": txt_date.isoformat()} for p in parts]
        st.session_state["pending_batch"] = batch

# --------------------------------------------------------------------------
# Manual paste
# --------------------------------------------------------------------------
with tab_paste:
    paste_text = st.text_area("Paste a conversation transcript", height=180,
                               placeholder="Support Executive: Thank you for calling...\nCitizen: ...")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        paste_district = st.selectbox("District", DISTRICTS, key="paste_district")
    with p_col2:
        paste_date = st.date_input("Date", value=date.today(), key="paste_date")

    if st.button("➕ Add to Batch", key="add_paste"):
        if paste_text.strip():
            batch = st.session_state.get("pending_batch") or []
            batch.append({
                "transcript": paste_text.strip(),
                "district": paste_district,
                "date": paste_date.isoformat(),
            })
            st.session_state["pending_batch"] = batch
            st.success("Added to batch below. Click Analyze to run the AI pipeline.")
        else:
            st.warning("Please paste a transcript first.")

# --------------------------------------------------------------------------
# Batch summary + actions
# --------------------------------------------------------------------------
st.markdown("---")
batch = st.session_state.get("pending_batch")

if batch:
    st.markdown(f"### 🗂 Ready to analyze: {len(batch)} conversation(s)")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        analyze_clicked = st.button("🤖 Analyze", type="primary", use_container_width=True)
    with col_b:
        clear_clicked = st.button("🧹 Clear", use_container_width=True)

    if clear_clicked:
        st.session_state["pending_batch"] = None
        st.rerun()

    if analyze_clicked:
        results = []
        progress = st.progress(0, text="Running AI analysis pipeline...")
        for i, item in enumerate(batch):
            analysis = analyze_transcript(item["transcript"])
            record = {
                "date": item["date"],
                "district": item["district"],
                "locality": None,
                "category": None,
                "department": analysis["department"],
                "transcript": item["transcript"],
                "sentiment": analysis["sentiment"],
                "sentiment_score": analysis["sentiment_confidence"],
                "priority": analysis["priority"],
                "confidence": analysis["department_confidence"],
                "source": "upload",
            }
            insert_conversation(conn, record)
            results.append({**record, "keywords": analysis["keywords"]})
            progress.progress((i + 1) / len(batch), text=f"Analyzed {i + 1}/{len(batch)}")

        refresh_data()
        st.session_state["uploaded_results"] = results
        st.session_state["pending_batch"] = None
        st.success(f"✅ Analyzed and saved {len(results)} conversation(s) to the database.")
        st.rerun()
else:
    st.caption("No conversations queued yet. Upload a file or paste a transcript above.")

# --------------------------------------------------------------------------
# Show most recent upload results
# --------------------------------------------------------------------------
if st.session_state.get("uploaded_results"):
    st.markdown("### ✅ Most Recent Analysis Results")
    for r in st.session_state["uploaded_results"][:10]:
        with st.container():
            st.markdown(
                f"""<div class="cv-card">
                <b>{r['district']}</b> · {r['date']} · <b>{r['department']}</b><br>
                {sentiment_badge(r['sentiment'])} {priority_badge(r['priority'])}
                <p style="color:#5A6B7E; margin-top:10px; font-size:13.5px;">
                {r['transcript'][:220].replace(chr(10), ' ')}{'...' if len(r['transcript']) > 220 else ''}
                </p>
                <p style="color:#0066CC; font-size:12.5px;">Keywords: {', '.join(r['keywords']) if r['keywords'] else '—'}</p>
                </div>""",
                unsafe_allow_html=True,
            )
    st.info("👉 Visit the **AI Analysis** page for detailed prediction cards, or **Dashboard** to see updated analytics.")
