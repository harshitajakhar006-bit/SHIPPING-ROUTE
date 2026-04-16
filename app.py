import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Shipping Intelligence Dashboard", layout="wide")

# ================= CUSTOM CSS (PRO UI) =================
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    h1, h2, h3 {color: #ffffff;}
    .stMetric {background-color: #1c1f26; padding: 15px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Shipping Intelligence Dashboard")

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")

# ================= DATE CLEAN =================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Order Date', 'Ship Date'])

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# ================= SAFE COLUMN DETECTION =================
def find_col(keywords):
    for col in df.columns:
        for k in keywords:
            if k in col.lower():
                return col
    return None

factory_col = find_col(['factory', 'plant', 'source'])
state_col = find_col(['state', 'province'])
ship_col = find_col(['ship'])

if not factory_col or not state_col:
    st.error("❌ Required columns not found. Showing dataset columns below:")
    st.write(df.columns)
    st.stop()

df['Route'] = df[factory_col].astype(str) + " → " + df[state_col].astype(str)

# ================= SIDEBAR =================
st.sidebar.header("🔍 Filters")

states = st.sidebar.multiselect("Select State", df[state_col].unique())
ships = st.sidebar.multiselect("Select Ship Mode", df[ship_col].unique() if ship_col else [])

filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df[state_col].isin(states)]

if ship_col and ships:
    filtered_df = filtered_df[filtered_df[ship_col].isin(ships)]

# ================= KPIs =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Avg Lead Time", round(filtered_df['Lead Time'].mean(), 2))
col2.metric("📦 Orders", filtered_df.shape[0])
col3.metric("🚚 Routes", filtered_df['Route'].nunique())
col4.metric("⚠️ Max Delay", filtered_df['Lead Time'].max())

# ================= GRAPH 1 =================
st.subheader("📈 Lead Time Distribution")
fig1 = px.histogram(filtered_df, x="Lead Time", color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig1, use_container_width=True)

# ================= GRAPH 2 =================
st.subheader("🚀 Top Efficient Routes")
top_routes = filtered_df.groupby('Route')['Lead Time'].mean().nsmallest(10).reset_index()
fig2 = px.bar(top_routes, x='Route', y='Lead Time', color='Lead Time')
st.plotly_chart(fig2, use_container_width=True)

# ================= GRAPH 3 =================
st.subheader("⚠️ Worst Routes")
worst_routes = filtered_df.groupby('Route')['Lead Time'].mean().nlargest(10).reset_index()
fig3 = px.bar(worst_routes, x='Route', y='Lead Time', color='Lead Time')
st.plotly_chart(fig3, use_container_width=True)

# ================= GRAPH 4 =================
st.subheader("🌍 State-wise Performance")
state_perf = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()
fig4 = px.bar(state_perf, x=state_col, y='Lead Time', color='Lead Time')
st.plotly_chart(fig4, use_container_width=True)

# ================= GRAPH 5 =================
if ship_col:
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
fig7 = px.bar(factory_perf, x=factory_col, y='Lead Time', color='Lead Time')
st.plotly_chart(fig7, use_container_width=True)

# ================= GRAPH 8 =================
st.subheader("📊 Correlation Insight")
fig8 = px.scatter(filtered_df, x='Lead Time', y='Lead Time')
st.plotly_chart(fig8, use_container_width=True)

# ================= HEATMAP =================
st.subheader("🌍 Geographic Efficiency Heatmap")

try:
    heat_data = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()

    fig_map = px.choropleth(
        heat_data,
        locations=state_col,
        locationmode="USA-states",
        color="Lead Time",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig_map, use_container_width=True)
except:
    st.warning("⚠️ Heatmap not supported for this dataset.")

# ================= LEADERBOARD =================
st.subheader("🏆 Leaderboard (Top Routes)")

leaderboard = filtered_df.groupby('Route')['Lead Time'].mean().sort_values().reset_index()
st.dataframe(leaderboard.head(10))

# ================= DATA =================
st.subheader("📋 Data Preview")
st.dataframe(filtered_df.head(20))
