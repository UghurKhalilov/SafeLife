import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import COMPETITORS

st.set_page_config(page_title="SafeLife — Comparison", page_icon="📋", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.win-card {
    background: linear-gradient(135deg, #1a2e1a, #0d1117);
    border: 1px solid #276749;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.lose-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 16px;
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

st.markdown("# 📋 Rəqib Müqayisəsi")
st.markdown("SafeLife vs mövcud həllər — xüsusiyyət üzrə tam müqayisə")
st.divider()

df = pd.DataFrame(COMPETITORS)
cols = ["SafeLife", "RealRider SOS", "Detecht", "SOSmart"]

scores = {}
for col in cols:
    scores[col] = df[col].tolist().count("✅")

c1, c2, c3, c4 = st.columns(4)
for i, (col, score) in enumerate(scores.items()):
    card_class = "win-card" if col == "SafeLife" else "lose-card"
    color = "#68d391" if col == "SafeLife" else "#a0aec0"
    with [c1, c2, c3, c4][i]:
        st.markdown(f"""<div class="{card_class}">
            <div style="font-size:2rem;font-weight:800;color:{color}">{score}/13</div>
            <div style="color:#a0aec0;font-size:0.9rem">{col}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

st.markdown("#### 📊 Tam xüsusiyyət müqayisəsi")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Feature":       st.column_config.TextColumn("Xüsusiyyət", width="large"),
        "SafeLife":      st.column_config.TextColumn("🆘 SafeLife", width="small"),
        "RealRider SOS": st.column_config.TextColumn("RealRider",  width="small"),
        "Detecht":       st.column_config.TextColumn("Detecht",    width="small"),
        "SOSmart":       st.column_config.TextColumn("SOSmart",    width="small"),
    }
)

st.divider()
st.markdown("#### 🕸️ Radar Analizi")

categories = [
    "Hədəf auditoriya", "Sensor analizi", "AI qərar",
    "Əlçatımlılıq", "Tibbi inteqrasiya", "İcma funksiyası"
]
values = {
    "SafeLife":      [95, 90, 85, 90, 95, 95],
    "RealRider SOS": [40, 45, 30, 50, 10, 10],
    "Detecht":       [55, 60, 50, 70, 10, 15],
    "SOSmart":       [30, 30, 20, 65, 10, 10],
}
colors = {
    "SafeLife":      "#e53e3e",
    "RealRider SOS": "#63b3ed",
    "Detecht":       "#f6ad55",
    "SOSmart":       "#68d391",
}

fig = go.Figure()
for name, vals in values.items():
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name,
        line=dict(color=colors[name], width=2),
        fillcolor=colors[name],
        opacity=0.25 if name == "SafeLife" else 0.1
    ))

fig.update_layout(
    polar=dict(
        bgcolor="#0d1117",
        radialaxis=dict(
            visible=True, range=[0, 100],
            gridcolor="#2d3748", color="#a0aec0"
        ),
        angularaxis=dict(gridcolor="#2d3748", color="#a0aec0")
    ),
    paper_bgcolor="#0d1117",
    font=dict(color="#a0aec0"),
    height=450,
    legend=dict(bgcolor="#0d1117"),
    margin=dict(l=40, r=40, t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.success("✅ SafeLife 13/13 xüsusiyyətdə rəqibləri üstələyir — bazarda analoqu olmayan həlldir.")