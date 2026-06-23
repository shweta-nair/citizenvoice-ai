"""
CitizenVoice AI - Chart Utilities

Centralized Plotly figure builders used across the Dashboard and District
Intelligence pages, themed to match the "Government Command Center" palette.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Brand palette
PRIMARY = "#0066CC"
SECONDARY = "#1E8E3E"
ACCENT = "#00B5D8"
BG = "#F5F7FA"

SEQUENTIAL_BLUES = ["#D6E9FF", "#9CC8FF", "#5FA3F5", "#2E7FE0", "#0066CC", "#004C99"]

SENTIMENT_COLORS = {"Positive": "#1E8E3E", "Neutral": "#F2A900", "Negative": "#D93025"}
PRIORITY_COLORS = {"Low": "#1E8E3E", "Medium": "#F2A900", "High": "#FF7A00", "Critical": "#D93025"}

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", color="#1A2330", size=13),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=30, r=20, t=50, b=30),
    title_font=dict(size=16, color="#0B2540"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _style(fig, title=None, height=380):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if title:
        fig.update_layout(title=title)
    return fig


def complaints_by_department(df: pd.DataFrame):
    counts = df["department"].value_counts().reset_index()
    counts.columns = ["department", "count"]
    counts = counts.sort_values("count", ascending=True)
    fig = px.bar(
        counts, x="count", y="department", orientation="h",
        color="count", color_continuous_scale=SEQUENTIAL_BLUES,
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return _style(fig, "Complaints by Department", height=420)


def complaints_by_district(df: pd.DataFrame):
    counts = df["district"].value_counts().reset_index()
    counts.columns = ["district", "count"]
    fig = px.bar(
        counts, x="district", y="count", color="count",
        color_continuous_scale=SEQUENTIAL_BLUES, text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_xaxes(tickangle=-30)
    return _style(fig, "Complaints by District")


def sentiment_distribution(df: pd.DataFrame):
    counts = df["sentiment"].value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    fig = px.pie(
        counts, names="sentiment", values="count", hole=0.55,
        color="sentiment", color_discrete_map=SENTIMENT_COLORS,
    )
    fig.update_traces(textinfo="percent+label")
    return _style(fig, "Sentiment Distribution")


def priority_distribution(df: pd.DataFrame):
    order = ["Low", "Medium", "High", "Critical"]
    counts = df["priority"].value_counts().reindex(order).fillna(0).reset_index()
    counts.columns = ["priority", "count"]
    fig = px.bar(
        counts, x="priority", y="count", color="priority",
        color_discrete_map=PRIORITY_COLORS, text="count",
        category_orders={"priority": order},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    return _style(fig, "Priority Distribution")


def monthly_trends(df: pd.DataFrame):
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.to_period("M").astype(str)
    counts = d.groupby("month").size().reset_index(name="count")
    counts = counts.sort_values("month")
    fig = px.line(
        counts, x="month", y="count", markers=True,
        line_shape="spline",
    )
    fig.update_traces(line_color=PRIMARY, marker=dict(size=7, color=ACCENT))
    fig.update_xaxes(tickangle=-30)
    return _style(fig, "Monthly Complaint Trends")


def top_keywords_chart(keyword_counts):
    """keyword_counts: list of (word, count) tuples"""
    if not keyword_counts:
        return go.Figure()
    df = pd.DataFrame(keyword_counts, columns=["keyword", "count"]).sort_values("count")
    fig = px.bar(
        df, x="count", y="keyword", orientation="h",
        color="count", color_continuous_scale=SEQUENTIAL_BLUES, text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return _style(fig, "Top Keywords", height=420)


def district_dept_heatmap(df: pd.DataFrame):
    pivot = pd.crosstab(df["district"], df["department"])
    fig = px.imshow(
        pivot, color_continuous_scale=SEQUENTIAL_BLUES, aspect="auto",
        labels=dict(x="Department", y="District", color="Complaints"),
    )
    fig.update_xaxes(tickangle=-30)
    return _style(fig, "District × Department Heatmap", height=460)


def priority_heatmap(df: pd.DataFrame):
    order = ["Low", "Medium", "High", "Critical"]
    pivot = pd.crosstab(df["district"], df["priority"])
    pivot = pivot.reindex(columns=order, fill_value=0)
    fig = px.imshow(
        pivot, color_continuous_scale=["#E8F5E9", "#FDD835", "#FF7A00", "#D93025"],
        aspect="auto", labels=dict(x="Priority", y="District", color="Cases"),
    )
    return _style(fig, "Priority Heatmap by District", height=460)


def sentiment_trend_by_district(df: pd.DataFrame, district: str):
    d = df[df["district"] == district].copy()
    if d.empty:
        return go.Figure()
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.to_period("M").astype(str)
    grouped = d.groupby(["month", "sentiment"]).size().reset_index(name="count")
    fig = px.line(
        grouped.sort_values("month"), x="month", y="count", color="sentiment",
        color_discrete_map=SENTIMENT_COLORS, markers=True,
    )
    fig.update_xaxes(tickangle=-30)
    return _style(fig, f"Sentiment Trend — {district}")
