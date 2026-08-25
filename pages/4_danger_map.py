import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import BAKU_HOTSPOTS

st.set_page_config(page_title="SafeLife — Danger Map", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.metric-card {
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

st.markdown("# 🗺️ Bakı Təhlükə Xəritəsi")
st.markdown("İstifadəçi məlumatlarına əsasən formalaşan qəza sıxlığı xəritəsi")
st.divider()

df = pd.DataFrame(BAKU_HOTSPOTS)

c1, c2, c3 = st.columns(3)
with c1:
    high = len(df[df["severity"] == "high"])
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2rem;font-weight:800;color:#fc8181">{high}</div>
        <div style="color:#a0aec0">Yüksək risk zona</div>
    </div>""", unsafe_allow_html=True)
with c2:
    total_inc = df["incidents"].sum()
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:2rem;font-weight:800;color:#f6ad55">{total_inc}</div>
        <div style="color:#a0aec0">Ümumi qəza (30 gün)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    worst = df.loc[df["incidents"].idxmax(), "zone"]
    st.markdown(f"""<div class="metric-card">
        <div style="font-size:1.4rem;font-weight:800;color:#fc8181">{worst}</div>
        <div style="color:#a0aec0">Ən təhlükəli zona</div>
    </div>""", unsafe_allow_html=True)

st.divider()

color_map = {"high": "#fc8181", "medium": "#f6ad55", "low": "#68d391"}
df["color"] = df["severity"].map(color_map)

fig = go.Figure()
for _, row in df.iterrows():
    fig.add_trace(go.Scattermap(
        lat=[row["lat"]],
        lon=[row["lon"]],
        mode="markers",
        marker=dict(
            size=max(20, row["incidents"] // 2),
            color=row["color"],
            opacity=0.75
        ),
        text=f"{row['zone']}<br>Qəza: {row['incidents']}<br>Səviyyə: {row['severity'].upper()}",
        hoverinfo="text",
        name=row["zone"]
    ))

fig.update_layout(
    map=dict(
        style="carto-darkmatter",
        center=dict(lat=40.4093, lon=49.8671),
        zoom=11
    ),
    paper_bgcolor="#0d1117",
    font=dict(color="#a0aec0"),
    height=500,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("#### 📋 Zona detalları")
display_df = df[["zone", "incidents", "severity"]].copy()
display_df.columns = ["Zona", "Qəza sayı", "Səviyyə"]
display_df = display_df.sort_values("Qəza sayı", ascending=False)
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.info("💡 Bu məlumatlar bələdiyyə və nəqliyyat qurumları ilə paylaşılaraq gələcəkdə təhlükəli yolların müəyyənləşdirilməsinə kömək edəcək.")
