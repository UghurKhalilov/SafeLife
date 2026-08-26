import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
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

color_map = {"high": "red", "medium": "orange", "low": "green"}

m = folium.Map(
    location=[40.3953, 49.8822],
    zoom_start=12,
    tiles="CartoDB dark_matter"
)

for _, row in df.iterrows():
    color = color_map.get(row["severity"], "blue")
    radius = max(15, row["incidents"] // 2)

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        tooltip=f"""
            <b>{row['zone']}</b><br>
            Qəza sayı: {row['incidents']}<br>
            Səviyyə: {row['severity'].upper()}
        """
    ).add_to(m)

    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=folium.DivIcon(
            html=f"""<div style="
                font-size:11px;
                font-weight:700;
                color:white;
                background:{color};
                padding:3px 7px;
                border-radius:6px;
                white-space:nowrap;
                box-shadow:0 2px 6px rgba(0,0,0,0.4)
            ">{row['zone']}</div>""",
            icon_size=(120, 30),
            icon_anchor=(60, 30)
        )
    ).add_to(m)

st_folium(m, width=None, height=520, use_container_width=True)

st.divider()
st.markdown("#### 📋 Zona detalları")
display_df = df[["zone", "incidents", "severity"]].copy()
display_df.columns = ["Zona", "Qəza sayı", "Səviyyə"]
display_df = display_df.sort_values("Qəza sayı", ascending=False)
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.info("💡 Bu məlumatlar bələdiyyə və nəqliyyat qurumları ilə paylaşılaraq gələcəkdə təhlükəli yolların müəyyənləşdirilməsinə kömək edəcək.")