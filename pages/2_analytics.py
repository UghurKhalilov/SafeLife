import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import generate_history

st.set_page_config(page_title="SafeLife — Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.metric-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🆘 SafeLife")
    st.markdown("*AI-Powered Emergency Detection*")
    st.divider()
    st.page_link("app.py",                  label="🏠 Home")
    st.page_link("pages/1_live_monitor.py", label="📡 Live Monitor")
    st.page_link("pages/2_analytics.py",    label="📊 Analytics")
    st.page_link("pages/3_simulation.py",   label="🎮 Simulation")
    st.page_link("pages/4_danger_map.py",   label="🗺️ Danger Map")
    st.page_link("pages/5_competitor.py",   label="📋 Comparison")
    st.divider()
    st.caption("SafeLife MVP — RSM Demo · Avqust 2026")

st.markdown("# 📊 Qəza Analitikası")
st.markdown("Son 30 günün sintetik məlumatları əsasında qəza statistikası")
st.divider()

if "history_df" not in st.session_state:
    with st.spinner("Məlumatlar yüklənir..."):
        st.session_state.history_df = generate_history(300)

df = st.session_state.history_df

total     = len(df)
accidents = df["accident"].sum()
false_pos = len(df[(df["risk_score"] > 70) & (~df["accident"])])
avg_risk  = df["risk_score"].mean()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2.2rem;font-weight:800;color:#63b3ed">{total}</div>
        <div style="color:#a0aec0">Ümumi hadisə</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2.2rem;font-weight:800;color:#fc8181">{accidents}</div>
        <div style="color:#a0aec0">Qəza aşkarlandı</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2.2rem;font-weight:800;color:#f6ad55">{false_pos}</div>
        <div style="color:#a0aec0">Yanlış alarm</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2.2rem;font-weight:800;color:#68d391">{avg_risk:.1f}%</div>
        <div style="color:#a0aec0">Orta risk skoru</div>
    </div>""", unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Risk Skoru Paylanması")
    fig = px.histogram(
        df, x="risk_score", nbins=20,
        color_discrete_sequence=["#e53e3e"]
    )
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(color="#a0aec0"), height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor="#1a1f2e"),
        yaxis=dict(gridcolor="#1a1f2e"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🚦 Rejim üzrə qəzalar")
    mode_acc = df[df["accident"]].groupby("mode").size().reset_index(name="count")
    fig2 = px.pie(
        mode_acc, values="count", names="mode",
        color_discrete_sequence=["#e53e3e", "#f6ad55", "#63b3ed"]
    )
    fig2.update_layout(
        paper_bgcolor="#0d1117",
        font=dict(color="#a0aec0"),
        height=300, margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("#### 📋 Ssenaari üzrə breakdown")
sc_stats = df.groupby("scenario").agg(
    hadise=("risk_score", "count"),
    ort_risk=("risk_score", "mean"),
    qeza=("accident", "sum")
).reset_index()
sc_stats["ort_risk"] = sc_stats["ort_risk"].round(1)
sc_stats.columns = ["Ssenaari", "Hadisə sayı", "Orta Risk (%)", "Qəza sayı"]
st.dataframe(sc_stats, use_container_width=True, hide_index=True)

st.markdown("#### 🔍 Akselerometr vs Risk")
fig3 = px.scatter(
    df, x="accelerometer", y="risk_score",
    color="accident",
    color_discrete_map={True: "#fc8181", False: "#68d391"},
    labels={"accelerometer": "Akselerometr (g)", "risk_score": "Risk Skoru (%)"},
    opacity=0.7
)
fig3.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(color="#a0aec0"), height=350,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(gridcolor="#1a1f2e"),
    yaxis=dict(gridcolor="#1a1f2e"),
)
st.plotly_chart(fig3, use_container_width=True)

