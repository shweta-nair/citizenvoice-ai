"""
CitizenVoice AI - Report Generator

Generates downloadable CSV and PDF reports from a filtered conversations
DataFrame, including an executive summary and department breakdown.
"""

import io
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

PRIMARY = colors.HexColor("#0066CC")
SECONDARY = colors.HexColor("#1E8E3E")
DARK = colors.HexColor("#0B2540")
LIGHT_BG = colors.HexColor("#F5F7FA")


def generate_csv_report(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def _summary_table_data(df: pd.DataFrame):
    total = len(df)
    top_dept = df["department"].value_counts().idxmax() if total else "N/A"
    top_district = df["district"].value_counts().idxmax() if total else "N/A"
    neg_pct = (df["sentiment"] == "Negative").mean() * 100 if total else 0
    high_priority = df["priority"].isin(["High", "Critical"]).sum()

    return [
        ["Total Complaints", str(total)],
        ["Most Complained Department", top_dept],
        ["Most Affected District", top_district],
        ["Negative Sentiment %", f"{neg_pct:.1f}%"],
        ["High / Critical Priority Cases", str(high_priority)],
    ]


def generate_pdf_report(df: pd.DataFrame, title="CitizenVoice AI — Intelligence Report") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], textColor=DARK, fontSize=20, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], textColor=colors.HexColor("#5A6B7E"), fontSize=10,
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], textColor=PRIMARY, spaceBefore=16, spaceAfter=8,
    )
    body_style = styles["BodyText"]

    elements = []
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M')} · "
        f"{len(df)} conversations analyzed", subtitle_style,
    ))
    elements.append(Spacer(1, 14))

    # Executive summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_data = _summary_table_data(df)
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DCE5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # Department summary
    elements.append(Paragraph("Department Summary", heading_style))
    dept_counts = df["department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Complaints"]
    dept_rows = [["Department", "Complaints", "% of Total"]]
    total = len(df)
    for _, row in dept_counts.iterrows():
        pct = (row["Complaints"] / total * 100) if total else 0
        dept_rows.append([row["Department"], str(row["Complaints"]), f"{pct:.1f}%"])

    dept_table = Table(dept_rows, colWidths=[8 * cm, 4 * cm, 4 * cm])
    dept_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DCE5")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(dept_table)
    elements.append(Spacer(1, 16))

    # Priority breakdown
    elements.append(Paragraph("Priority Breakdown", heading_style))
    order = ["Critical", "High", "Medium", "Low"]
    prio_counts = df["priority"].value_counts().reindex(order).fillna(0).astype(int)
    prio_rows = [["Priority", "Cases"]] + [[p, str(c)] for p, c in prio_counts.items()]
    prio_table = Table(prio_rows, colWidths=[8 * cm, 4 * cm])
    prio_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DCE5")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(prio_table)

    elements.append(Spacer(1, 16))
    elements.append(Paragraph("District Summary", heading_style))
    dist_counts = df["district"].value_counts().reset_index()
    dist_counts.columns = ["District", "Complaints"]
    dist_rows = [["District", "Complaints"]] + dist_counts.astype(str).values.tolist()
    dist_table = Table(dist_rows, colWidths=[8 * cm, 4 * cm])
    dist_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DCE5")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(dist_table)

    doc.build(elements)
    buf.seek(0)
    return buf.read()
