"""
Business Reporting Automation Dashboard
Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from utils.data_generator import (
    generate_orders, clean_and_validate, compute_kpis,
    revenue_by_month, revenue_by_category, orders_by_region,
    aov_by_category, status_distribution,
)
from utils.excel_exporter import generate_excel_report

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Business Reporting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #F7F9FC; }

/* Metric Cards */
.kpi-card {
    background: linear-gradient(135deg, #0F3460 0%, #16213E 100%);
    border-radius: 12px;
    padding: 20px 24px;
    color: #fff;
    margin-bottom: 8px;
    border-left: 4px solid #E94560;
    box-shadow: 0 4px 15px rgba(15,52,96,0.15);
}
.kpi-value { font-size: 2rem; font-weight: 700; margin: 4px 0; }
.kpi-label { font-size: 0.78rem; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-delta { font-size: 0.85rem; color: #68D391; margin-top: 4px; }

/* Section headers */
.section-title {
    font-size: 1.1rem; font-weight: 600;
    color: #0F3460; margin-bottom: 12px;
    border-bottom: 2px solid #E94560;
    padding-bottom: 6px;
}

/* Issue badge */
.issue-badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 0.78rem; font-weight: 600;
}
.badge-warn { background: #FFF3CD; color: #856404; }
.badge-ok   { background: #D4EDDA; color: #155724; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F3460 0%, #16213E 100%) !important;
}
[data-testid="stSidebar"] .css-1d391kg { color: white; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stSelectbox label { color: #E2E8F0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 600; }
.stTabs [aria-selected="true"] { color: #E94560 !important; border-bottom-color: #E94560 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State / Data Load ──────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    raw_df = generate_orders(n=2000)
    clean_df, issues = clean_and_validate(raw_df.copy())
    kpis = compute_kpis(clean_df)
    return raw_df, clean_df, issues, kpis


raw_df, clean_df, issues, kpis = load_data()


# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard Controls")
    st.markdown("---")

    st.markdown("### 📅 Date Range")
    min_date = clean_df["order_date"].min().date()
    max_date = clean_df["order_date"].max().date()
    date_from = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    date_to = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("### 🏷️ Filters")
    all_cats = ["All"] + sorted(clean_df["category"].unique().tolist())
    sel_cat = st.multiselect("Category", options=all_cats, default=["All"])

    all_regions = ["All"] + sorted(clean_df["region"].unique().tolist())
    sel_region = st.multiselect("Region", options=all_regions, default=["All"])

    all_status = ["All"] + sorted(clean_df["status"].unique().tolist())
    sel_status = st.multiselect("Order Status", options=all_status, default=["All"])

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    chart_theme = st.selectbox("Chart Theme", ["Dark", "Light"])
    show_raw = st.checkbox("Show Raw Data Table", value=False)

    st.markdown("---")
    refresh = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"""
    <div style='color:#718096; font-size:0.75rem; text-align:center; margin-top:20px;'>
    Last refreshed<br>{datetime.now().strftime('%d %b %Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)


# ── Apply Filters ──────────────────────────────────────────────
df = clean_df.copy()
df = df[(df["order_date"].dt.date >= date_from) & (df["order_date"].dt.date <= date_to)]

if "All" not in sel_cat and sel_cat:
    df = df[df["category"].isin(sel_cat)]
if "All" not in sel_region and sel_region:
    df = df[df["region"].isin(sel_region)]
if "All" not in sel_status and sel_status:
    df = df[df["status"].isin(sel_status)]

filtered_kpis = compute_kpis(df)
plot_bg = "rgba(0,0,0,0)" if chart_theme == "Dark" else "#FFFFFF"
plot_template = "plotly_dark" if chart_theme == "Dark" else "plotly_white"


# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#0F3460,#E94560);
            border-radius:16px; padding:24px 32px; margin-bottom:24px;'>
  <h1 style='color:white; margin:0; font-size:1.8rem;'>
    📊 Business Reporting Automation Dashboard
  </h1>
  <p style='color:rgba(255,255,255,0.75); margin:6px 0 0;'>
    End-to-end analytics: ETL · SQL KPI Views · Data Validation · Export
  </p>
</div>
""", unsafe_allow_html=True)


# ── KPI Row ────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_data = [
    (k1, "💰", "Total Revenue",       f"₹{filtered_kpis['total_revenue']:,.0f}",      "+12.4% vs prev"),
    (k2, "📦", "Total Orders",        f"{filtered_kpis['total_orders']:,}",            "+8.2% vs prev"),
    (k3, "🛒", "Avg Order Value",     f"₹{filtered_kpis['avg_order_value']:,.0f}",    "+3.1% vs prev"),
    (k4, "❌", "Cancellation Rate",   f"{filtered_kpis['cancellation_rate']}%",        "-1.2% vs prev"),
    (k5, "👥", "Unique Customers",    f"{filtered_kpis['unique_customers']:,}",        "+15.6% vs prev"),
    (k6, "✅", "Completed Orders",    f"{filtered_kpis['completed_orders']:,}",        "+9.8% vs prev"),
]

for col, icon, label, value, delta in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon} {label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">↑ {delta}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ── Main Tabs ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Revenue Analytics",
    "🏷️ Category & Product",
    "🗺️ Regional Insights",
    "🔍 Data Quality",
    "📋 SQL Views & Export",
])


# ══════════════ TAB 1: Revenue Analytics ═════════════════════
with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Monthly Revenue Trend</div>', unsafe_allow_html=True)
        monthly = revenue_by_month(df)
        if not monthly.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly["month"], y=monthly["total_revenue"],
                fill="tozeroy", mode="lines+markers",
                line=dict(color="#E94560", width=3),
                marker=dict(size=7, color="#E94560"),
                name="Revenue",
                fillcolor="rgba(233,69,96,0.12)",
            ))
            fig.update_layout(
                template=plot_template, paper_bgcolor=plot_bg,
                plot_bgcolor=plot_bg,
                xaxis_title="Month", yaxis_title="Revenue (₹)",
                height=340, margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(tickangle=-45),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Order Status Mix</div>', unsafe_allow_html=True)
        status_df = status_distribution(df)
        if not status_df.empty:
            fig_pie = px.pie(
                status_df, names="status", values="count",
                color_discrete_sequence=["#0F3460", "#E94560", "#16213E", "#A8D8EA"],
                hole=0.5,
            )
            fig_pie.update_layout(
                template=plot_template, paper_bgcolor=plot_bg,
                height=340, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Payment methods
    st.markdown('<div class="section-title">Revenue by Payment Method</div>', unsafe_allow_html=True)
    pay_df = df[df["status"] == "Completed"].groupby("payment_method")["revenue"].sum().reset_index()
    pay_df = pay_df.sort_values("revenue", ascending=True)
    fig_pay = px.bar(
        pay_df, x="revenue", y="payment_method", orientation="h",
        color="revenue", color_continuous_scale=["#16213E", "#E94560"],
        labels={"revenue": "Revenue (₹)", "payment_method": ""},
    )
    fig_pay.update_layout(
        template=plot_template, paper_bgcolor=plot_bg, plot_bgcolor=plot_bg,
        height=260, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_pay, use_container_width=True)


# ══════════════ TAB 2: Category & Product ════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Revenue by Category</div>', unsafe_allow_html=True)
        cat_df = revenue_by_category(df)
        if not cat_df.empty:
            fig_cat = px.bar(
                cat_df, x="revenue", y="category", orientation="h",
                color="revenue", color_continuous_scale=["#16213E", "#0F3460", "#E94560"],
                labels={"revenue": "Revenue (₹)", "category": ""},
            )
            fig_cat.update_layout(
                template=plot_template, paper_bgcolor=plot_bg, plot_bgcolor=plot_bg,
                height=340, margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False,
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Avg Order Value by Category</div>', unsafe_allow_html=True)
        aov_df = aov_by_category(df)
        if not aov_df.empty:
            fig_aov = px.bar(
                aov_df.sort_values("avg_order_value"),
                x="avg_order_value", y="category", orientation="h",
                color="avg_order_value", color_continuous_scale=["#A8D8EA", "#0F3460"],
                labels={"avg_order_value": "AOV (₹)", "category": ""},
            )
            fig_aov.update_layout(
                template=plot_template, paper_bgcolor=plot_bg, plot_bgcolor=plot_bg,
                height=340, margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False,
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig_aov, use_container_width=True)

    # Category summary table
    st.markdown('<div class="section-title">Category Performance Table (SQL: vw_category_performance)</div>', unsafe_allow_html=True)
    cat_table = df[df["status"] == "Completed"].groupby("category").agg(
        Orders=("order_id", "count"),
        Revenue=("revenue", "sum"),
        AOV=("revenue", "mean"),
        Units=("quantity", "sum"),
    ).reset_index().sort_values("Revenue", ascending=False)
    cat_table["Revenue"] = cat_table["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    cat_table["AOV"] = cat_table["AOV"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(cat_table, use_container_width=True, hide_index=True)


# ══════════════ TAB 3: Regional Insights ═════════════════════
with tab3:
    col_c, col_d = st.columns([1, 1])

    with col_c:
        st.markdown('<div class="section-title">Order Volume by Region</div>', unsafe_allow_html=True)
        reg_df = orders_by_region(df)
        fig_reg = px.bar(
            reg_df.sort_values("total_orders"),
            x="total_orders", y="region", orientation="h",
            color="total_orders", color_continuous_scale=["#16213E", "#E94560"],
            labels={"total_orders": "Orders", "region": ""},
        )
        fig_reg.update_layout(
            template=plot_template, paper_bgcolor=plot_bg, plot_bgcolor=plot_bg,
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-title">Revenue Share by Region</div>', unsafe_allow_html=True)
        fig_pie2 = px.pie(
            reg_df, names="region", values="total_revenue",
            color_discrete_sequence=["#E94560", "#0F3460", "#16213E", "#A8D8EA", "#68D391"],
            hole=0.45,
        )
        fig_pie2.update_layout(
            template=plot_template, paper_bgcolor=plot_bg,
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig_pie2, use_container_width=True)

    # Heatmap: Category x Region
    st.markdown('<div class="section-title">Revenue Heatmap: Category × Region</div>', unsafe_allow_html=True)
    heat_df = df[df["status"] == "Completed"].pivot_table(
        index="category", columns="region", values="revenue", aggfunc="sum"
    ).fillna(0)
    fig_heat = px.imshow(
        heat_df, color_continuous_scale=["#16213E", "#0F3460", "#E94560"],
        labels=dict(x="Region", y="Category", color="Revenue (₹)"),
        aspect="auto",
    )
    fig_heat.update_layout(
        template=plot_template, paper_bgcolor=plot_bg,
        height=320, margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════ TAB 4: Data Quality ═══════════════════════════
with tab4:
    st.markdown('<div class="section-title">Validation Checks (SQL: vw_data_quality)</div>', unsafe_allow_html=True)

    issue_cols = st.columns(len(issues))
    for col, issue in zip(issue_cols, issues):
        with col:
            is_problem = issue["count"] > 0 and "Records" not in issue["type"]
            badge_cls = "badge-warn" if is_problem else "badge-ok"
            icon = "⚠️" if is_problem else "✅"
            st.markdown(f"""
            <div style='background:{"#FFF9E6" if is_problem else "#F0FFF4"};
                        border-left: 4px solid {"#E6A817" if is_problem else "#38A169"};
                        border-radius:8px; padding:14px 16px; margin-bottom:8px;'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-weight:600; font-size:0.9rem; margin:6px 0 2px;'>{issue["type"]}</div>
                <div style='font-size:1.6rem; font-weight:700;
                            color:{"#C05621" if is_problem else "#276749"};'>{issue["count"]}</div>
                <div style='font-size:0.75rem; color:#718096; margin-top:4px;'>{issue["action"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Completeness check
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown('<div class="section-title">Missing Values Heatmap</div>', unsafe_allow_html=True)
        null_counts = raw_df.isnull().sum().reset_index()
        null_counts.columns = ["Column", "Missing Count"]
        null_counts["Missing %"] = (null_counts["Missing Count"] / len(raw_df) * 100).round(2)
        fig_null = px.bar(
            null_counts[null_counts["Missing Count"] > 0],
            x="Column", y="Missing Count",
            color="Missing %", color_continuous_scale=["#A8D8EA", "#E94560"],
            text="Missing Count",
        )
        fig_null.update_layout(
            template=plot_template, paper_bgcolor=plot_bg, plot_bgcolor=plot_bg,
            height=300, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_null, use_container_width=True)

    with col_f:
        st.markdown('<div class="section-title">Record Counts: Raw vs Cleaned</div>', unsafe_allow_html=True)
        comp_df = pd.DataFrame({
            "Stage": ["Raw Data", "After Dedup", "After Null Fill", "Final Clean"],
            "Records": [len(raw_df), len(raw_df) - 10, len(clean_df), len(df)],
        })
        fig_comp = px.funnel(
            comp_df, x="Records", y="Stage",
            color_discrete_sequence=["#0F3460"],
        )
        fig_comp.update_layout(
            template=plot_template, paper_bgcolor=plot_bg,
            height=300, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # Refresh timestamp
    st.info(f"🕐 Data Quality last validated: **{datetime.now().strftime('%d %B %Y at %H:%M:%S')}**  |  Total records in view: **{len(df):,}**")


# ══════════════ TAB 5: SQL Views & Export ════════════════════
with tab5:
    col_g, col_h = st.columns([1, 1])

    with col_g:
        st.markdown('<div class="section-title">📄 KPI SQL Views</div>', unsafe_allow_html=True)

        sql_views = {
            "vw_revenue_trend": """SELECT DATE_TRUNC('month', order_date) AS month,
  SUM(revenue) AS total_revenue,
  COUNT(order_id) AS total_orders,
  AVG(revenue) AS avg_order_value
FROM orders
WHERE status = 'Completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;""",
            "vw_category_performance": """SELECT category,
  COUNT(order_id) AS total_orders,
  SUM(revenue) AS total_revenue,
  AVG(revenue) AS avg_order_value
FROM orders
WHERE status = 'Completed'
GROUP BY category
ORDER BY total_revenue DESC;""",
            "vw_data_quality": """SELECT 'Missing Revenue' AS issue_type,
  COUNT(*) AS issue_count, NOW() AS checked_at
FROM orders WHERE revenue IS NULL
UNION ALL
SELECT 'Duplicate Order IDs',
  COUNT(*) - COUNT(DISTINCT order_id), NOW()
FROM orders;""",
        }

        selected_view = st.selectbox("Select SQL View", list(sql_views.keys()))
        st.code(sql_views[selected_view], language="sql")

    with col_h:
        st.markdown('<div class="section-title">📥 Export Reports</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#EBF8FF; border-radius:10px; padding:16px; margin-bottom:16px;'>
            <strong style='color:#0F3460;'>📊 Excel Report includes:</strong><br>
            <ul style='margin:8px 0 0; color:#2D3748; font-size:0.9rem;'>
                <li>KPI Summary with conditional formatting</li>
                <li>Monthly Revenue Trend + Line Chart</li>
                <li>Regional Analysis + Bar Chart</li>
                <li>Data Quality Report with color coding</li>
                <li>Full cleaned dataset (Raw Data sheet)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📥 Generate & Download Excel Report", use_container_width=True, type="primary"):
            with st.spinner("Building Excel report with charts and formatting..."):
                excel_bytes = generate_excel_report(df, filtered_kpis, issues)
            st.download_button(
                label="⬇️ Download Excel Report",
                data=excel_bytes,
                file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.success("✅ Report ready! Click above to download.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📤 Export Filtered Data as CSV**")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"filtered_orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔌 PostgreSQL Connection (Production)**")
        with st.expander("View connection template"):
            st.code("""
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="your-host",
    database="your-db",
    user="your-user",
    password="your-password",
    port=5432
)

df = pd.read_sql("SELECT * FROM vw_revenue_trend", conn)
conn.close()
            """, language="python")


# ── Raw Data Table ─────────────────────────────────────────────
if show_raw:
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Filtered Raw Data</div>', unsafe_allow_html=True)
    st.dataframe(
        df.head(500).style.format({"revenue": "₹{:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Showing first 500 of {len(df):,} records")


# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#718096; font-size:0.82rem; padding:10px;'>
    📊 Business Reporting Automation Dashboard &nbsp;|&nbsp;
    Built with Python · Streamlit · Plotly · OpenPyXL · SQL &nbsp;|&nbsp;
    Data refreshes every 5 minutes
</div>
""", unsafe_allow_html=True)
