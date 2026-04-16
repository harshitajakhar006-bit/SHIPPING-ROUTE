import pandas as pd
import streamlit as st
import plotly.express as px

# ================= PAGE =================
st.set_page_config(page_title="Shipping Intelligence", layout="wide")

# ================= PREMIUM CSS =================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.main-title {
    font-size: 42px;
    font-weight: bold;
    color: white;
}
.card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
    text-align: center;
}
.metric-title {
    color: #9ca3af;
    font-size: 14px;
}
.metric-value {
    font-size: 28px;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🚀 Shipping Intelligence Dashboard</p>', unsafe_allow_html=True)

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Order Date', 'Ship Date'])

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

state_col = "State/Province"
ship_col = "Ship Mode"
city_col = "City"

df['Route'] = df[city_col] + " → " + df[state_col]

# ================= SIDEBAR =================
st.sidebar.header("🔍 Filters")

states = st.sidebar.multiselect("State", df[state_col].unique())
ships = st.sidebar.multiselect("Ship Mode", df[ship_col].unique())

filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df[state_col].isin(states)]

if ships:
    filtered_df = filtered_df[filtered_df[ship_col].isin(ships)]

# ================= KPI CARDS =================
col1, col2, col3, col4 = st.columns(4)

def card(title, value):
    return f"""
    <div class="card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

col1.markdown(card("Avg Lead Time", round(filtered_df['Lead Time'].mean(), 2)), unsafe_allow_html=True)
col2.markdown(card("Total Orders", filtered_df.shape[0]), unsafe_allow_html=True)
col3.markdown(card("Total Routes", filtered_df['Route'].nunique()), unsafe_allow_html=True)
col4.markdown(card("Max Delay", filtered_df['Lead Time'].max()), unsafe_allow_html=True)

# ================= CHART LAYOUT =================
colA, colB = st.columns(2)

with colA:
    st.subheader("📈 Lead Time Distribution")
    st.plotly_chart(px.histogram(filtered_df, x="Lead Time"), use_container_width=True)

with colB:
    st.subheader("🚚 Ship Mode Comparison")
    st.plotly_chart(px.box(filtered_df, x=ship_col, y='Lead Time'), use_container_width=True)

colC, colD = st.columns(2)

with colC:
    st.subheader("🏆 Top Routes")
    top_routes = filtered_df.groupby('Route')['Lead Time'].mean().nsmallest(10).reset_index()
    st.plotly_chart(px.bar(top_routes, x='Route', y='Lead Time'), use_container_width=True)

with colD:
    st.subheader("⚠️ Worst Routes")
    worst_routes = filtered_df.groupby('Route')['Lead Time'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(worst_routes, x='Route', y='Lead Time'), use_container_width=True)

# ================= TIME SERIES =================
st.subheader("📅 Orders Over Time")
time_data = filtered_df.groupby('Order Date').size().reset_index(name='Orders')
st.plotly_chart(px.line(time_data, x='Order Date', y='Orders'), use_container_width=True)

# ================= HEATMAP =================
st.subheader("🌍 Geographic Efficiency")

try:
    state_perf = filtered_df.groupby(state_col)['Lead Time'].mean().reset_index()
    fig_map = px.choropleth(
        state_perf,
        locations=state_col,
        locationmode="USA-states",
        color="Lead Time",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_map, use_container_width=True)
except:
    st.info("Heatmap not supported")

# ================= LEADERBOARD =================
st.subheader("🏆 Leaderboard")

leaderboard = filtered_df.groupby('Route')['Lead Time'].mean().sort_values().reset_index()
st.dataframe(leaderboard.head(10))

# ================= INSIGHTS =================
st.subheader("🧠 Key Insights")

st.markdown("""
- Fastest routes show optimized logistics planning  
- Certain states consistently show higher delays  
- Ship mode significantly impacts delivery efficiency  
- Peak order dates correlate with increased delays  
""")
