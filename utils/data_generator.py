"""
Generates synthetic business data for demo purposes.
In production, replace with real DB/API connections.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", "Food & Beverage"]
REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
STATUSES = ["Completed", "Pending", "Cancelled", "Refunded"]
STATUS_WEIGHTS = [0.75, 0.10, 0.10, 0.05]

def generate_orders(n=2000, start_date="2023-01-01", end_date="2024-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = (end - start).days

    order_ids = [f"ORD-{10000 + i}" for i in range(n)]
    dates = [start + timedelta(days=random.randint(0, delta)) for _ in range(n)]
    categories = random.choices(CATEGORIES, k=n)
    regions = random.choices(REGIONS, k=n)
    payment_methods = random.choices(PAYMENT_METHODS, k=n)
    statuses = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=n)

    base_prices = {
        "Electronics": (500, 50000),
        "Clothing": (200, 5000),
        "Home & Garden": (300, 20000),
        "Sports": (250, 15000),
        "Books": (100, 2000),
        "Toys": (150, 5000),
        "Food & Beverage": (50, 3000),
    }

    revenues = []
    quantities = []
    for cat in categories:
        low, high = base_prices[cat]
        qty = random.randint(1, 10)
        price = round(random.uniform(low, high), 2)
        revenues.append(round(price * qty, 2))
        quantities.append(qty)

    # Inject some data quality issues for demo
    for i in random.sample(range(n), 30):
        revenues[i] = np.nan  # missing values
    dupe_indices = random.sample(range(n), 10)
    order_ids_list = list(order_ids)
    for i in dupe_indices[5:]:
        order_ids_list[i] = order_ids_list[dupe_indices[0]]  # duplicates

    df = pd.DataFrame({
        "order_id": order_ids_list,
        "order_date": dates,
        "category": categories,
        "region": regions,
        "payment_method": payment_methods,
        "status": statuses,
        "revenue": revenues,
        "quantity": quantities,
        "customer_id": [f"CUST-{random.randint(1000, 9999)}" for _ in range(n)],
    })
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").reset_index(drop=True)
    return df


def clean_and_validate(df: pd.DataFrame):
    issues = []
    original_len = len(df)

    # Missing values
    missing = df["revenue"].isna().sum()
    if missing:
        issues.append({"type": "Missing Values", "count": int(missing), "action": "Filled with category median"})
        df["revenue"] = df.groupby("category")["revenue"].transform(lambda x: x.fillna(x.median()))

    # Duplicates
    dupes = df.duplicated(subset="order_id").sum()
    if dupes:
        issues.append({"type": "Duplicate Order IDs", "count": int(dupes), "action": "Removed duplicates"})
        df = df.drop_duplicates(subset="order_id")

    # Negative revenue
    neg_rev = (df["revenue"] < 0).sum()
    if neg_rev:
        issues.append({"type": "Negative Revenue", "count": int(neg_rev), "action": "Removed rows"})
        df = df[df["revenue"] >= 0]

    # Date range
    future_dates = (df["order_date"] > datetime.now()).sum()
    if future_dates:
        issues.append({"type": "Future Dates", "count": int(future_dates), "action": "Flagged"})

    issues.append({"type": "Records After Cleaning", "count": len(df), "action": f"Started with {original_len}"})
    return df, issues


def compute_kpis(df: pd.DataFrame):
    completed = df[df["status"] == "Completed"]
    total_revenue = completed["revenue"].sum()
    total_orders = len(df)
    avg_order_value = completed["revenue"].mean()
    cancellation_rate = (df["status"] == "Cancelled").mean() * 100
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "cancellation_rate": round(cancellation_rate, 2),
        "completed_orders": len(completed),
        "unique_customers": df["customer_id"].nunique(),
    }


def revenue_by_month(df: pd.DataFrame):
    df2 = df[df["status"] == "Completed"].copy()
    df2["month"] = df2["order_date"].dt.to_period("M").astype(str)
    return df2.groupby("month")["revenue"].sum().reset_index().rename(columns={"revenue": "total_revenue"})


def revenue_by_category(df: pd.DataFrame):
    df2 = df[df["status"] == "Completed"].copy()
    return df2.groupby("category")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)


def orders_by_region(df: pd.DataFrame):
    return df.groupby("region").agg(
        total_orders=("order_id", "count"),
        total_revenue=("revenue", "sum")
    ).reset_index()


def aov_by_category(df: pd.DataFrame):
    df2 = df[df["status"] == "Completed"].copy()
    return df2.groupby("category")["revenue"].mean().reset_index().rename(columns={"revenue": "avg_order_value"})


def status_distribution(df: pd.DataFrame):
    return df["status"].value_counts().reset_index().rename(columns={"index": "status", "count": "orders"})
