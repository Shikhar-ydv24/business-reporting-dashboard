import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Business Reporting Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to inject a clean dark navy / red accent theme
st.markdown("""
<style>
    .main { background-color: #0A1128; color: #FFFFFF; }
    .stMetric { background-color: #1C2541; padding: 15px; border-radius: 10px; border-left: 5px solid #E94560; }
    div[data-testid="stMetricValue"] { color: #FFFFFF; font-size: 28px; }
    div[data-testid="stMetricLabel"] { color: #8D99AE; }
    .stTabs [data-baseweb="tab"] { color: #8D99AE; font-size: 16px; }
    .stTabs [data-baseweb="tab"]:hover { color: #E94560; }
    .stTabs [aria-selected="true"] { color: #E94560; border-bottom-color: #E94560; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOCK DATA GENERATOR & ETL PIPELINE
# ==========================================
@st.cache_data(ttl=3600)
def load_and_validate_data():
    """Simulates an ETL pipeline: fetches, cleans, and validates business data."""
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)
    date_list = [start_date + timedelta(days=x) for x in range(180)]
    
    categories = ['Electronics', 'Apparel', 'Home & Kitchen', 'Beauty']
    regions = ['North', 'East', 'West', 'South']
    statuses = ['Delivered', 'Delivered', 'Delivered', 'Shipped', 'Cancelled', 'Returned']
    
    data = []
    for date in date_list:
        num_orders = np.random.randint(40, 120)
        for _ in range(num_orders):
            category = np.random.choice(categories)
            region = np.random.choice(regions)
            status = np.random.choice(statuses)
            
            # Intentionally introducing minor data flaws for the validation engine to catch
            if np.random.rand() < 0.005:
                units = np.nan  # Missing value
            else:
                units = int(np.random.randint(1, 5))
                
            if np.random.rand() < 0.002:
                price = -50.0  # Inconsistency/Error
            else:
                price = float(np.random.uniform(15.0, 350.0))
                
            order_id = f"ORD-{np.random.randint(100000, 999999)}"
            
            data.append({
                "order_id": order_id,
                "date": date,
                "category": category,
                "region": region,
                "units": units,
                "price": price,
                "status": status
            })
            
    df = pd.DataFrame(data)
    
    # --- DATA QUALITY RUN ---
    total_records = len(df)
    missing_units = df['units'].isna().sum()
    invalid_prices = (df['price'] <= 0).sum()
    duplicate_count = df.duplicated(subset=['order_id']).sum()
    
    # --- CLEANING PHASE ---
    df['units'] = df['units'].fillna(1)
    df['price'] = df['price'].apply(lambda x: abs(x) if x <= 0 else x)
    df['revenue'] = df['units'] * df['price']
    
    dq_summary = {
        "Total Scanned": total_records,
        "Missing Values Corrected": missing_units,
        "Pricing Inconsistencies Fixed": invalid_prices,
        "Duplicate Rows Handled": duplicate_count,
        "Data Health Score": round(((total_records - (missing_units + invalid_prices)) / total_records) * 100, 2)
    }
    
    return df, dq_summary

# Execute data engine
df, dq_metrics = load_and_validate_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.title("📊 Control Panel")
st.sidebar.markdown("---")

available_categories = ["All"] + list(df['category'].unique())
selected_category = st.sidebar.selectbox("Select Category", available_categories)

available_regions = ["All"] + list(df['region'].unique())
selected_region = st.sidebar.selectbox("Select Region", available_regions)

# Apply global filters to data view
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['region'] == selected_region]

# ==========================================
# 4. MAIN DASHBOARD CONTENT
# ==========================================
st.title("Business Reporting Automation Dashboard")
st.markdown("An end-to-end analytics application built to automate KPI extraction, data quality validation, and performance reporting.")
st.markdown("---")

# Global KPIs
total_rev = filtered_df['revenue'].sum()
total_orders = filtered_df['order_id'].nunique()
aov = total_rev / total_orders if total_orders > 0 else 0
total_items = filtered_df['units'].sum