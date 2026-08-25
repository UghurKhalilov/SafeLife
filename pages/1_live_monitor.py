import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import generate_realtime_frame, SCENARIOS, MODES
from datetime import datetime

st.set_page_config(page_title="SafeLife — Live Monitor", page_icon="📡", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.sensor-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 8px;
}
.sensor-val { font-size: 1.8rem; font-weight: 800; }
.sensor-label { font-size: 0.8rem; color: #a0aec0; margin-top: 4px; }
.risk-low    { color: #68d391; }
.risk-medium { color: #f6ad55; }
.risk-high   { color: #fc8181; }
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

st.markdown("# 📡 Live Sensor Monitor")
st.markdown("7 sensor real-time izlənilir — qəza aşkarlaması aktiv")
st.divider()

col1, col2 = st.columns([1, 3])
with col1:
    mode     = st.selectbox("🚦 Rejim", list(MODES.keys()))
    scenario = st.selectbox("📋 Ssenaari", list(SCENARIOS.keys()))
    refresh  = st.slider("Yeniləmə (san)", 0.5, 3.0, 1.0, 0.5)
    running  = st.toggle("▶️ Monitor aktiv", value=True)

placeholder   = st.empty()
chart_placeholder = st.empty()
history = []

if running:
    for _ in range(200):
        frame = generate_realtime_frame(scenario, datetime.now(), mode)
        history.append(frame)
        if len(history) > 30:
            history.pop(0)

        risk = frame["risk_score"]
        risk_color = "risk-low" if risk < 40 else ("risk-medium" if risk < 70 else "risk-high")
        risk_label = "TƏHLÜKƏSİZ" if risk < 40 else ("DİQQƏT" if risk < 70 else "⚠️ RİSK!")

        with placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#63b3ed">{frame['accelerometer']}</div>
                    <div class="sensor-label">Akselerometr (g)</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#b794f4">{frame['gyroscope']}</div>
                    <div class="sensor-label">Gyroscope (rad/s)</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#68d391">{frame['gps_speed']}</div>
                    <div class="sensor-label">GPS Sürəti (km/h)</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#f6ad55">{frame['microphone']}</div>
                    <div class="sensor-label">Mikrofon (dB)</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#fc8181">{frame['barometer']}</div>
                    <div class="sensor-label">Bərometr (hPa Δ)</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#fbd38d">{frame['light_sensor']}</div>
                    <div class="sensor-label">İşıq Sensoru</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val" style="color:#81e6d9">{frame['magnetometer']}</div>
                    <div class="sensor-label">Maqnetometr (μT)</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="sensor-card">
                    <div class="sensor-val {risk_color}">{risk}%</div>
                    <div class="sensor-label">AI Risk — {risk_label}</div>
                </div>""", unsafe_allow_html=True)

        if len(history) > 2:
            df = pd.DataFrame(history)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(df))),
                y=df["risk_score"],
                fill="tozeroy",
                line=dict(color="#e53e3e", width=2),
                fillcolor="rgba(229,62,62,0.15)",
            ))
            fig.add_hline(y=70, line_dash="dash", line_color="#f6ad55",
                          annotation_text="Yüksək risk")
            fig.add_hline(y=40, line_dash="dash", line_color="#68d391",
                          annotation_text="Normal")
            fig.update_layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                font=dict(color="#a0aec0"),
                height=200, margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(range=[0, 100], gridcolor="#1a1f2e"),
                xaxis=dict(gridcolor="#1a1f2e"),
                showlegend=False
            )
            chart_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(refresh)
else:
    st.info("Monitor dayandırılıb. Aktivləşdirmək üçün toggle-u açın.")

    