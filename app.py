import pandas as pd
import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Shipping Dashboard", layout="wide")

st.title("📦 Shipping Route Efficiency Dashboard")

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")

# ================= DATE CLEANING =================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

# Remove invalid rows
df = df.dropna(subset=['Order Date', 'Ship Date'])

# ================= FEATURE ENGINEERING =================
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# ================= AUTO COLUMN DETECTION =================
# find factory column
factory_col = [col for col in df.columns if 'factory' in col.lower() or 'plant' in col.lower()]
factory_col = factory_col[0] if factory_col else df.columns[0]

# find state column
state_col = [col for col in df.columns if 'state' in col.lower()]
state_col = state_col[0] if state_col else df.columns[1]

# find ship mode column
ship_col = [col for col in df.columns if 'ship' in col.lower()]
ship_col = ship_col[0] if ship_col else None

# ================= ROUTE =================
df['Route'] = df[factory_col].astype(str) + " → " + df[state_col].astype(str)

# ================= KPIs =================
col1, col2, col3 = st.columns(3)

col1.metric("📊 Avg Lead Time", round(df['Lead Time'].mean(), 2))
col2.metric("📦 Total Orders", df.shape[0])
col3.metric("🚚 Unique Routes", df['Route'].nunique())

# ================= TOP ROUTES =================
st.subheader("🚀 Top Efficient Routes")
top_routes = df.groupby('Route')['Lead Time'].mean().sort_values().head(10)
st.bar_chart(top_routes)

# ================= WORST ROUTES =================
st.subheader("⚠️ Least Efficient Routes")
worst_routes = df.groupby('Route')['Lead Time'].mean().sort_values(ascending=False).head(10)
st.bar_chart(worst_routes)

# ================= STATE ANALYSIS =================
st.subheader("🌍 State-wise Performance")
state_perf = df.groupby(state_col)['Lead Time'].mean().sort_values()
st.bar_chart(state_perf)

# ================= SHIP MODE =================
if ship_col:
    st.subheader("🚚 Ship Mode Comparison")
    mode_perf = df.groupby(ship_col)['Lead Time'].mean()
    st.bar_chart(mode_perf)

# ================= DATA PREVIEW =================
st.subheader("📋 Raw Data Preview")
st.dataframe(df.head(20))