import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="APL Logistics | Delivery Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0d1117; }
    .stApp { background-color: #0d1117; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-label { color: #8892a4; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { color: #e2e8f0; font-size: 32px; font-weight: 700; line-height: 1; }
    .kpi-delta { font-size: 13px; margin-top: 6px; }
    .kpi-good { color: #48bb78; }
    .kpi-bad { color: #fc8181; }
    .kpi-neutral { color: #63b3ed; }

    /* Section Headers */
    .section-header {
        color: #e2e8f0;
        font-size: 18px;
        font-weight: 600;
        padding: 16px 0 8px 0;
        border-bottom: 2px solid #2d3748;
        margin-bottom: 16px;
    }

    /* Sidebar - FIXED */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937 !important;
        display: block !important;
        visibility: visible !important;
    }
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        color: white !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1f2e; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8892a4; border-radius: 6px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/apl_logistics_data.csv", encoding="latin1")
    if "Order Date" not in df.columns:
        import random
        from datetime import datetime, timedelta
        random.seed(42)
        start = datetime(2023, 1, 1)
        df["Order Date"] = [
            (start + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d")
            for _ in range(len(df))
        ]
    if "Delay Gap" not in df.columns:
        df["Delay Gap"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
    if "Delivery Class" not in df.columns:
        df["Delivery Class"] = df["Delay Gap"].apply(
            lambda x: "Early" if x < 0 else ("On-Time" if x == 0 else "Delayed")
        )
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df
df = load_data()

# ─── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚚 APL Logistics")
    st.markdown("**Delivery Intelligence Platform**")
    st.markdown("---")

    st.markdown("### 🔍 Filters")

    # Date range
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    date_range = st.date_input("📅 Order Date Range", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)

    # Market
    markets = ["All"] + sorted(df["Market"].unique().tolist())
    selected_market = st.selectbox("🌍 Market", markets)

    # Shipping Mode
    modes = ["All"] + sorted(df["Shipping Mode"].unique().tolist())
    selected_mode = st.selectbox("🚢 Shipping Mode", modes)

    # Customer Segment
    segments = ["All"] + sorted(df["Customer Segment"].unique().tolist())
    selected_segment = st.selectbox("👤 Customer Segment", segments)

    # Order Status
    statuses = ["All"] + sorted(df["Order Status"].unique().tolist())
    selected_status = st.selectbox("📦 Order Status", statuses)

    st.markdown("---")
    st.markdown("### 📊 Dataset Info")
    st.info(f"**Total Records:** {len(df):,}\n\n**Date Range:** {min_date} to {max_date}")

    if st.button("🔄 Reset Filters"):
        st.rerun()

# ─── Apply Filters ──────────────────────────────────────────────────────────────
filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Order Date"].dt.date >= date_range[0]) &
        (filtered["Order Date"].dt.date <= date_range[1])
    ]
if selected_market != "All":
    filtered = filtered[filtered["Market"] == selected_market]
if selected_mode != "All":
    filtered = filtered[filtered["Shipping Mode"] == selected_mode]
if selected_segment != "All":
    filtered = filtered[filtered["Customer Segment"] == selected_segment]
if selected_status != "All":
    filtered = filtered[filtered["Order Status"] == selected_status]

# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(90deg, #1a365d 0%, #2a4a7f 50%, #1a365d 100%);
     border-radius: 12px; padding: 24px 32px; margin-bottom: 24px;
     border: 1px solid #2d5da6;'>
    <div style='display:flex; align-items:center; gap:16px;'>
        <div style='font-size:48px;'>🚚</div>
        <div>
            <h1 style='color:#e2e8f0; margin:0; font-size:28px; font-weight:700;'>APL Logistics — KWE Group</h1>
            <p style='color:#90cdf4; margin:4px 0 0 0; font-size:15px;'>Delivery Performance Intelligence Dashboard</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ──────────────────────────────────────────────────────────────────
total = len(filtered)
on_time = (filtered["Delivery Class"] == "On-Time").sum()
delayed = (filtered["Late_delivery_risk"] == 1).sum()
early = (filtered["Delivery Class"] == "Early").sum()
on_time_pct = round((on_time / total * 100) if total > 0 else 0, 1)
late_risk_ratio = round((delayed / total * 100) if total > 0 else 0, 1)
avg_delay = round(filtered[filtered["Delay Gap"] > 0]["Delay Gap"].mean(), 2) if delayed > 0 else 0
avg_benefit = round(filtered["Benefit per order"].mean(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

def kpi(label, value, delta_text, delta_class):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {delta_class}">{delta_text}</div>
    </div>"""

with col1:
    st.markdown(kpi("📦 Total Orders", f"{total:,}", f"{len(df):,} total records", "kpi-neutral"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi("✅ On-Time Rate", f"{on_time_pct}%", f"{on_time:,} orders on time", "kpi-good"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi("⚠️ Late Risk Ratio", f"{late_risk_ratio}%", f"{delayed:,} at risk", "kpi-bad"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi("⏱️ Avg Delay (Days)", f"{avg_delay}d", "Among delayed shipments", "kpi-bad"), unsafe_allow_html=True)
with col5:
    st.markdown(kpi("💰 Avg Benefit/Order", f"${avg_benefit}", "Net profit per order", "kpi-neutral"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Delivery Overview",
    "⚠️ Delay Risk Analysis",
    "🚢 Shipping Mode Efficiency",
    "🌍 Regional & Market",
    "👥 Customer Segments"
])

COLORS = {
    "On-Time": "#48bb78", "Delayed": "#fc8181", "Early": "#63b3ed",
    "Late delivery": "#fc8181", "Shipping on time": "#48bb78",
    "Advanced shipping": "#63b3ed", "Shipping canceled": "#f6ad55",
    "bg": "#1a1f2e", "grid": "#2d3748", "text": "#e2e8f0"
}

PLOTLY_THEME = dict(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font_color="#e2e8f0",
    font_family="Inter",
)

# ════════════════════════════════════════════════════════
# TAB 1 – DELIVERY OVERVIEW
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 Overall Delivery Performance</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Delivery Class Donut
        class_counts = filtered["Delivery Class"].value_counts().reset_index()
        class_counts.columns = ["Class", "Count"]
        color_map = {"On-Time": "#48bb78", "Delayed": "#fc8181", "Early": "#63b3ed"}
        fig = px.pie(class_counts, names="Class", values="Count",
                     hole=0.55, color="Class", color_discrete_map=color_map,
                     title="Delivery Classification Breakdown")
        fig.update_traces(textposition='outside', textinfo='percent+label', pull=[0.03]*3)
        fig.update_layout(**PLOTLY_THEME, title_font_size=15,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Delivery Status Bar
        status_counts = filtered["Delivery Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = [COLORS.get(s, "#90cdf4") for s in status_counts["Status"]]
        fig = go.Figure(go.Bar(
            x=status_counts["Count"], y=status_counts["Status"],
            orientation="h", marker_color=colors,
            text=status_counts["Count"], textposition="outside"
        ))
        fig.update_layout(**PLOTLY_THEME, title="Delivery Status Distribution",
                          title_font_size=15, xaxis_gridcolor="#2d3748",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    # Monthly Trend
    st.markdown('<div class="section-header">📈 Monthly Delivery Trend</div>', unsafe_allow_html=True)
    monthly = filtered.copy()
    monthly["Month"] = monthly["Order Date"].dt.to_period("M").astype(str)
    monthly_grp = monthly.groupby(["Month", "Delivery Class"]).size().reset_index(name="Count")
    fig = px.line(monthly_grp, x="Month", y="Count", color="Delivery Class",
                  color_discrete_map=color_map,
                  title="Monthly Orders by Delivery Class",
                  markers=True)
    fig.update_layout(**PLOTLY_THEME, xaxis_gridcolor="#2d3748", yaxis_gridcolor="#2d3748",
                      title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

    # Delay Gap Distribution
    st.markdown('<div class="section-header">📉 Delay Gap Distribution</div>', unsafe_allow_html=True)
    fig = px.histogram(filtered, x="Delay Gap", nbins=30,
                       color_discrete_sequence=["#63b3ed"],
                       title="Distribution of Delivery Delay Gap (Actual − Scheduled Days)")
    fig.add_vline(x=0, line_dash="dash", line_color="#fc8181",
                  annotation_text="On-Time Threshold", annotation_position="top right")
    fig.update_layout(**PLOTLY_THEME, xaxis_gridcolor="#2d3748", yaxis_gridcolor="#2d3748",
                      title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 2 – DELAY RISK ANALYSIS
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">⚠️ Late Delivery Risk Diagnostics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        risk_counts = filtered["Late_delivery_risk"].map({1: "At Risk", 0: "Safe"}).value_counts().reset_index()
        risk_counts.columns = ["Risk", "Count"]
        fig = px.pie(risk_counts, names="Risk", values="Count", hole=0.55,
                     color="Risk",
                     color_discrete_map={"At Risk": "#fc8181", "Safe": "#48bb78"},
                     title="Late Delivery Risk Distribution")
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Risk by Order Status
        risk_status = filtered.groupby("Order Status")["Late_delivery_risk"].mean().reset_index()
        risk_status["Risk %"] = (risk_status["Late_delivery_risk"] * 100).round(1)
        risk_status = risk_status.sort_values("Risk %", ascending=True)
        fig = go.Figure(go.Bar(
            x=risk_status["Risk %"], y=risk_status["Order Status"],
            orientation="h", marker_color="#f6ad55",
            text=risk_status["Risk %"].astype(str) + "%",
            textposition="outside"
        ))
        fig.update_layout(**PLOTLY_THEME, title="Late Risk % by Order Status",
                          title_font_size=15, xaxis_gridcolor="#2d3748")
        st.plotly_chart(fig, use_container_width=True)

    # Delay Gap by Category
    st.markdown('<div class="section-header">📦 Delay by Product Category</div>', unsafe_allow_html=True)
    cat_delay = filtered.groupby("Category Name")["Delay Gap"].mean().reset_index()
    cat_delay = cat_delay.sort_values("Delay Gap", ascending=False)
    cat_delay["Color"] = cat_delay["Delay Gap"].apply(lambda x: "#fc8181" if x > 0 else "#48bb78")
    fig = go.Figure(go.Bar(
        x=cat_delay["Category Name"], y=cat_delay["Delay Gap"],
        marker_color=cat_delay["Color"],
        text=cat_delay["Delay Gap"].round(2),
        textposition="outside"
    ))
    fig.add_hline(y=0, line_color="#e2e8f0", line_dash="dash")
    fig.update_layout(**PLOTLY_THEME, title="Avg Delay Gap by Product Category",
                      title_font_size=15, xaxis_gridcolor="#2d3748", yaxis_gridcolor="#2d3748")
    st.plotly_chart(fig, use_container_width=True)

    # Profit vs Delay
    st.markdown('<div class="section-header">💸 Profit Impact of Delays</div>', unsafe_allow_html=True)
    sample = filtered.sample(min(500, len(filtered)))
    fig = px.scatter(sample, x="Delay Gap", y="Order Profit Per Order",
                     color="Late_delivery_risk",
                     color_continuous_scale=["#48bb78", "#fc8181"],
                     title="Profit vs Delay Gap (Sample of 500)",
                     hover_data=["Shipping Mode", "Market", "Customer Segment"])
    fig.add_vline(x=0, line_dash="dash", line_color="#f6ad55")
    fig.update_layout(**PLOTLY_THEME, title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3 – SHIPPING MODE EFFICIENCY
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🚢 Shipping Mode Performance</div>', unsafe_allow_html=True)

    mode_stats = filtered.groupby("Shipping Mode").agg(
        Orders=("Late_delivery_risk", "count"),
        Late_Risk_Pct=("Late_delivery_risk", lambda x: round(x.mean()*100, 1)),
        Avg_Delay=("Delay Gap", "mean"),
        Avg_Profit=("Order Profit Per Order", "mean")
    ).reset_index()
    mode_stats["Avg_Delay"] = mode_stats["Avg_Delay"].round(2)
    mode_stats["Avg_Profit"] = mode_stats["Avg_Profit"].round(2)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(mode_stats, x="Shipping Mode", y="Late_Risk_Pct",
                     color="Late_Risk_Pct", color_continuous_scale=["#48bb78", "#f6ad55", "#fc8181"],
                     title="Late Delivery Risk % by Shipping Mode",
                     text="Late_Risk_Pct")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(mode_stats, x="Shipping Mode", y="Avg_Delay",
                     color="Avg_Delay", color_continuous_scale=["#48bb78", "#f6ad55", "#fc8181"],
                     title="Avg Delay Gap by Shipping Mode", text="Avg_Delay")
        fig.update_traces(texttemplate="%{text}d", textposition="outside")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Mode Stacked Bar – Delivery Class
    st.markdown('<div class="section-header">📊 Delivery Class Distribution per Mode</div>', unsafe_allow_html=True)
    mode_class = filtered.groupby(["Shipping Mode", "Delivery Class"]).size().reset_index(name="Count")
    fig = px.bar(mode_class, x="Shipping Mode", y="Count", color="Delivery Class",
                 color_discrete_map=color_map, barmode="stack",
                 title="Delivery Class Distribution by Shipping Mode")
    fig.update_layout(**PLOTLY_THEME, title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

    # Stats Table
    st.markdown('<div class="section-header">📋 Shipping Mode KPI Summary</div>', unsafe_allow_html=True)
    styled = mode_stats.rename(columns={
        "Late_Risk_Pct": "Late Risk %",
        "Avg_Delay": "Avg Delay (days)",
        "Avg_Profit": "Avg Profit ($)"
    })
    st.dataframe(styled.set_index("Shipping Mode").style.background_gradient(
        subset=["Late Risk %"], cmap="RdYlGn_r"
    ).format({"Late Risk %": "{:.1f}%", "Avg Delay (days)": "{:.2f}d", "Avg Profit ($)": "${:.2f}"}),
    use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 – REGIONAL & MARKET
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🌍 Regional & Market Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        mkt = filtered.groupby("Market").agg(
            Late_Risk=("Late_delivery_risk", "mean"),
            Orders=("Late_delivery_risk", "count")
        ).reset_index()
        mkt["Late Risk %"] = (mkt["Late_Risk"] * 100).round(1)
        fig = px.bar(mkt.sort_values("Late Risk %"), x="Market", y="Late Risk %",
                     color="Late Risk %", color_continuous_scale=["#48bb78", "#f6ad55", "#fc8181"],
                     title="Late Risk % by Market", text="Late Risk %")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        region = filtered.groupby("Order Region").agg(
            Late_Risk=("Late_delivery_risk", "mean"),
            Orders=("Late_delivery_risk", "count")
        ).reset_index()
        region["Late Risk %"] = (region["Late_Risk"] * 100).round(1)
        region = region.sort_values("Late Risk %", ascending=True).tail(12)
        fig = go.Figure(go.Bar(
            x=region["Late Risk %"], y=region["Order Region"],
            orientation="h",
            marker_color=px.colors.sequential.Reds[3:],
            text=region["Late Risk %"].astype(str) + "%",
            textposition="outside"
        ))
        fig.update_layout(**PLOTLY_THEME, title="Top Regions by Late Risk %", title_font_size=15)
        st.plotly_chart(fig, use_container_width=True)

    # Geographic scatter
    st.markdown('<div class="section-header">🗺️ Geographic Delay Heatmap</div>', unsafe_allow_html=True)
    geo_sample = filtered.sample(min(2000, len(filtered)))
    fig = px.scatter_geo(geo_sample, lat="Latitude", lon="Longitude",
                         color="Late_delivery_risk",
                         color_continuous_scale=["#48bb78", "#fc8181"],
                         hover_data=["Order Country", "Market", "Shipping Mode"],
                         title="Geographic Distribution of Late Delivery Risk",
                         size_max=6, opacity=0.6,
                         projection="natural earth")
    fig.update_layout(**PLOTLY_THEME, title_font_size=15,
                      geo=dict(bgcolor="#1a1f2e", showland=True, landcolor="#2d3748",
                               showocean=True, oceancolor="#111827",
                               showcountries=True, countrycolor="#3d4a5e"))
    st.plotly_chart(fig, use_container_width=True)

    # Country Table
    st.markdown('<div class="section-header">🏳️ Country-Level Risk Ranking</div>', unsafe_allow_html=True)
    country_tbl = filtered.groupby(["Order Country", "Market"]).agg(
        Orders=("Late_delivery_risk", "count"),
        Late_Risk_Pct=("Late_delivery_risk", lambda x: round(x.mean()*100, 1)),
        Avg_Delay=("Delay Gap", lambda x: round(x.mean(), 2))
    ).reset_index().sort_values("Late_Risk_Pct", ascending=False).head(15)
    st.dataframe(country_tbl.style.background_gradient(subset=["Late_Risk_Pct"], cmap="RdYlGn_r"),
                 use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 5 – CUSTOMER SEGMENTS
# ════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">👥 Customer Segment Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        seg = filtered.groupby("Customer Segment").agg(
            Orders=("Late_delivery_risk", "count"),
            Late_Risk=("Late_delivery_risk", "mean"),
            Avg_Sales=("Sales", "mean"),
            Avg_Profit=("Order Profit Per Order", "mean")
        ).reset_index()
        seg["Late Risk %"] = (seg["Late_Risk"] * 100).round(1)
        fig = px.bar(seg, x="Customer Segment", y="Late Risk %",
                     color="Customer Segment",
                     color_discrete_sequence=["#63b3ed", "#f6ad55", "#fc8181"],
                     title="Late Delivery Risk by Customer Segment",
                     text="Late Risk %")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        seg2 = filtered.groupby(["Customer Segment", "Delivery Class"]).size().reset_index(name="Count")
        fig = px.bar(seg2, x="Customer Segment", y="Count", color="Delivery Class",
                     color_discrete_map=color_map, barmode="group",
                     title="Delivery Class Split by Customer Segment")
        fig.update_layout(**PLOTLY_THEME, title_font_size=15)
        st.plotly_chart(fig, use_container_width=True)

    # Segment × Shipping Mode Heatmap
    st.markdown('<div class="section-header">🔥 Segment × Shipping Mode Risk Heatmap</div>', unsafe_allow_html=True)
    hm = filtered.groupby(["Customer Segment", "Shipping Mode"])["Late_delivery_risk"].mean().reset_index()
    hm["Late Risk %"] = (hm["Late_delivery_risk"] * 100).round(1)
    hm_pivot = hm.pivot(index="Customer Segment", columns="Shipping Mode", values="Late Risk %")
    fig = go.Figure(go.Heatmap(
        z=hm_pivot.values,
        x=hm_pivot.columns.tolist(),
        y=hm_pivot.index.tolist(),
        colorscale=[[0, "#48bb78"], [0.5, "#f6ad55"], [1, "#fc8181"]],
        text=hm_pivot.values.round(1),
        texttemplate="%{text}%",
        colorbar=dict(title="Late Risk %")
    ))
    fig.update_layout(**PLOTLY_THEME, title="Late Risk % Heatmap: Segment × Shipping Mode",
                      title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

    # Sales & Profit by Segment
    st.markdown('<div class="section-header">💰 Financial Performance by Segment</div>', unsafe_allow_html=True)
    fin = filtered.groupby("Customer Segment").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Order Profit Per Order", "sum"),
        Avg_Benefit=("Benefit per order", "mean")
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(fin, x="Customer Segment", y="Total_Sales",
                     color="Customer Segment",
                     color_discrete_sequence=["#63b3ed", "#f6ad55", "#fc8181"],
                     title="Total Sales by Customer Segment",
                     text_auto=True)
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(fin, x="Customer Segment", y="Total_Profit",
                     color="Customer Segment",
                     color_discrete_sequence=["#63b3ed", "#f6ad55", "#fc8181"],
                     title="Total Profit by Customer Segment", text_auto=True)
        fig.update_layout(**PLOTLY_THEME, title_font_size=15, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#4a5568; font-size:13px; padding:12px;'>
    🚚 <strong>APL Logistics Delivery Intelligence Platform</strong> — KWE Group &nbsp;|&nbsp;
    Built with Streamlit & Plotly &nbsp;|&nbsp;
    Data-Driven Operations
</div>
""", unsafe_allow_html=True)