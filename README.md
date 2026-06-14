# 📊 Business Reporting Automation Dashboard

A full-stack business intelligence tool built with **Python, Streamlit, SQL, Plotly, and OpenPyXL** — featuring automated ETL, KPI views, data validation, interactive charts, and Excel exports.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?logo=postgresql)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

| Feature | Details |
|---|---|
| **ETL Pipeline** | Fetch → Clean → Validate → Load |
| **SQL KPI Views** | Revenue trend, category performance, AOV, regional sales |
| **Data Validation** | Null checks, deduplication, date range, negative value detection |
| **Interactive Charts** | Plotly line, bar, pie, heatmap, funnel charts |
| **Excel Export** | Pivot tables, charts, conditional formatting via OpenPyXL |
| **Filters** | Date range, category, region, status — all real-time |
| **PostgreSQL Ready** | Drop-in connection template for production DB |

---

## 🗂️ Project Structure

```
business_reporting_dashboard/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml               # Streamlit theme & server config
├── utils/
│   ├── data_generator.py         # Synthetic data + ETL pipeline
│   └── excel_exporter.py         # Automated Excel report builder
├── sql/
│   └── kpi_queries.sql           # PostgreSQL KPI view definitions
└── data/                         # (gitignored) local data storage
```

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/business-reporting-dashboard.git
cd business-reporting-dashboard
```

### 2. Create and activate a virtual environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗄️ PostgreSQL Integration

Replace the synthetic data generator with a real DB connection:

```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="your-host",
    database="your-database",
    user="your-user",
    password="your-password",
    port=5432
)

df = pd.read_sql("SELECT * FROM vw_revenue_trend", conn)
conn.close()
```

Then run the SQL views from `sql/kpi_queries.sql` in your PostgreSQL instance.

### Storing secrets safely (Streamlit Cloud)
Create `.streamlit/secrets.toml` (never commit this):
```toml
[postgres]
host = "your-host"
database = "your-db"
user = "your-user"
password = "your-password"
port = 5432
```

Access in Python:
```python
import streamlit as st
conn_str = st.secrets["postgres"]
```

---

## 📊 SQL KPI Views

All views are in `sql/kpi_queries.sql`:

| View | Description |
|---|---|
| `vw_revenue_trend` | Monthly revenue + order volume |
| `vw_category_performance` | Revenue, AOV, units per category |
| `vw_regional_sales` | Orders, revenue, customers per region |
| `vw_order_status` | Status distribution with % share |
| `vw_payment_methods` | Revenue by payment type |
| `vw_data_quality` | Live validation counts |
| `vw_top_orders` | Top 10 orders by revenue |
| `vw_daily_sales_30d` | Last 30 days daily sales |

---

## 🧰 Tech Stack

- **Frontend**: Streamlit, Plotly, custom CSS
- **Data Processing**: Pandas, NumPy
- **Database**: PostgreSQL + psycopg2 + SQLAlchemy
- **Excel Automation**: OpenPyXL (charts, conditional formatting, pivot-style tables)
- **Validation**: Custom Python ETL pipeline

---

## 📄 License

MIT License — free to use and modify.
