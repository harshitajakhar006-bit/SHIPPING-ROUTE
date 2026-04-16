import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Advanced Shipping Dashboard", layout="wide")

st.title("🚀 Advanced Shipping Route Efficiency Dashboard")

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")

# ================= DATE CLEAN =================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Order Date', 'Ship Date'])

# ================= FEATURES =================
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# Auto detect columns
factory_col = [c for c in df.columns if 'factory' in c.lower() or 'plant' in c.lower()][0]
state_col = [c for c in df.columns if 'state' in c.lower()][0]
ship_col = [c for c in df.columns if 'ship' in c.lower()][0]

df['Route'] = df[factory_col].astype(str) + " → " + df[state_col].astype(str)

# ================= SIDEBAR FILTERS =================
st.sidebar.header("🔍 Filters")

state_filter = st.sidebar.multiselect("Select State", df[state_col].unique())
ship_filter = st.sidebar.multiselect("Select Ship Mode", df[ship_col].unique())

filtered_df = df.copy()

if state_filter:
    filtered_df = filtered_df[filtered_df[state_col].isin(state_filter)]

if ship_filter:
    filtered_df = filtered_df[filtered_df[ship_col].isin(ship_filter)]

# ================= KPIs =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Avg Lead Time", round(filtered_df['Lead Time'].mean(), 2))
col2.metric("📦 Orders", filtered_df.shape[0])
col3.metric("🚚 Routes", filtered_df['Route'].nunique())
col4.metric("⚠️ Max Delay", filtered_df['Lead Time'].max())

# ================= GRAPH 1 =================
st.subheader("📈 Lead Time Distribution")
fig1 = px.histogram(filtered_df, x="Lead Time")
st.plotly_chart(fig1, use_container_width=True)

# ================= GRAPH 2 =================
st.subheader("🚀 Top Routes")
top_routes = filtered_df.groupby('Route')['Lead Time'].mean().reset_index().sort_values(by='Lead Time').head(10)
fig2 = px.bar(top_routes, x='Route', y='Lead Time')
st.plotly_chart(fig2, use_container_width=True)

# ================= GRAPH 3 =================
st.subheader("⚠️ Worst Routes")
worst_routes = filtered_df.groupby('Route')['Lead Time'].mean().reset_index().sort_values(by='Lead Time', ascending=False).head(10)
fig3 = px.bar(worst_routes, x='Route', y='Lead Time')
st.plotly_chart(fig3, use_container_width=True)

# ================= GRAPH 4 =================
st.subheader("🌍 State-wise Performance")
state_perf = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()
fig4 = px.bar(state_perf, x=state_col, y='Lead Time')
st.plotly_chart(fig4, use_container_width=True)

# ================= GRAPH 5 =================
st.subheader("🚚 Ship Mode Comparison")
fig5 = px.box(filtered_df, x=ship_col, y='Lead Time')
st.plotly_chart(fig5, use_container_width=True)

# ================= GRAPH 6 =================
st.subheader("📅 Orders Over Time")
time_data = filtered_df.groupby('Order Date').size().reset_index(name='Orders')
fig6 = px.line(time_data, x='Order Date', y='Orders')
st.plotly_chart(fig6, use_container_width=True)

# ================= GRAPH 7 =================
st.subheader("🏭 Factory Performance")
factory_perf = filtered_df.groupby(factory_col)['Lead Time'].mean().reset_index()
fig7 = px.bar(factory_perf, x=factory_col, y='Lead Time')
st.plotly_chart(fig7, use_container_width=True)

# ================= HEATMAP =================
st.subheader("🌍 Geographic Efficiency Heatmap")

heat_data = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()

fig_map = px.choropleth(
    heat_data,
    locations=state_col,
    locationmode="USA-states",
    color="Lead Time",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_map, use_container_width=True)

# ================= LEADERBOARD =================
st.subheader("🏆 Top Performing Routes Leaderboard")

leaderboard = filtered_df.groupby('Route')['Lead Time'].mean().reset_index().sort_values(by='Lead Time')
st.dataframe(leaderboard.head(10))

# ================= DATA =================
st.subheader("📋 Data Preview")
st.dataframe(filtered_df.head(20))