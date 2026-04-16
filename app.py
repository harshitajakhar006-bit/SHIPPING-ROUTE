import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Shipping Intelligence Dashboard", layout="wide")

st.title("🚀 Shipping Intelligence Dashboard")

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")

# ================= DATE CLEAN =================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Order Date', 'Ship Date'])

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# ================= USE AVAILABLE COLUMNS =================
state_col = "State/Province"
ship_col = "Ship Mode"
city_col = "City"

# Route using City instead of Factory
df['Route'] = df[city_col].astype(str) + " → " + df[state_col].astype(str)

# ================= SIDEBAR =================
st.sidebar.header("Filters")

states = st.sidebar.multiselect("Select State", df[state_col].unique())
ships = st.sidebar.multiselect("Select Ship Mode", df[ship_col].unique())

filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df[state_col].isin(states)]

if ships:
    filtered_df = filtered_df[filtered_df[ship_col].isin(ships)]

# ================= KPIs =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(), 2))
col2.metric("Orders", filtered_df.shape[0])
col3.metric("Routes", filtered_df['Route'].nunique())
col4.metric("Max Delay", filtered_df['Lead Time'].max())

# ================= GRAPHS =================
st.subheader("Lead Time Distribution")
st.plotly_chart(px.histogram(filtered_df, x="Lead Time"), use_container_width=True)

st.subheader("Top Routes")
top_routes = filtered_df.groupby('Route')['Lead Time'].mean().nsmallest(10).reset_index()
st.plotly_chart(px.bar(top_routes, x='Route', y='Lead Time'), use_container_width=True)

st.subheader("Worst Routes")
worst_routes = filtered_df.groupby('Route')['Lead Time'].mean().nlargest(10).reset_index()
st.plotly_chart(px.bar(worst_routes, x='Route', y='Lead Time'), use_container_width=True)

st.subheader("State Performance")
state_perf = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()
st.plotly_chart(px.bar(state_perf, x=state_col, y='Lead Time'), use_container_width=True)

st.subheader("Ship Mode Comparison")
st.plotly_chart(px.box(filtered_df, x=ship_col, y='Lead Time'), use_container_width=True)

st.subheader("Orders Over Time")
time_data = filtered_df.groupby('Order Date').size().reset_index(name='Orders')
st.plotly_chart(px.line(time_data, x='Order Date', y='Orders'), use_container_width=True)

st.subheader("City Performance")
city_perf = filtered_df.groupby(city_col)['Lead Time'].mean().reset_index()
st.plotly_chart(px.bar(city_perf, x=city_col, y='Lead Time'), use_container_width=True)

# ================= HEATMAP =================
st.subheader("Geographical Heatmap")

try:
    fig_map = px.choropleth(
        state_perf,
        locations=state_col,
        locationmode="USA-states",
        color="Lead Time"
    )
    st.plotly_chart(fig_map, use_container_width=True)
except:
    st.warning("Heatmap not supported")

# ================= LEADERBOARD =================
st.subheader("Leaderboard")

leaderboard = filtered_df.groupby('Route')['Lead Time'].mean().sort_values().reset_index()
st.dataframe(leaderboard.head(10))
