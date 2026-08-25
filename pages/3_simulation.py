import streamlit as st
import time
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import generate_realtime_frame, SCENARIOS, MODES
from datetime import datetime

st.set_page_config(page_title="SafeLife — Simulation", page_icon="🎮", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.phone-frame {
    background: #1a1f2e;
    border: 3px solid #2d3748;
    border-radius: 40px;
    padding: 20px;
    max-width: 320px;
    margin: 0 auto;
    min-height: 580px;
    position: relative;
}
.phone-status {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: #a0aec0;
    margin-bottom: 16px;
    padding: 0 4px;
}
.screen-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #e2e8f0;
    text-align: center;
    margin-bottom: 8px;
}
.screen-sub {
    font-size: 0.85rem;
    color: #a0aec0;
    text-align: center;
    margin-bottom: 20px;
}
.mode-btn {
    background: #1a1f2e;
    border: 2px solid #2d3748;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin-bottom: 10px;
    cursor: pointer;
}
.sensor-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #0d1117;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 0.85rem;
}
.sos-card {
    background: #1a0505;
    border: 2px solid #fc8181;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 10px;
}
.notify-card {
    background: #0d1117;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.85rem;
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

st.markdown("# 🎮 Qəza Simulyasiyası")
st.markdown("SafeLife-ın real iş axınını interaktiv demo ilə izləyin")
st.divider()

# Session state
if "sim_step" not in st.session_state:
    st.session_state.sim_step = 1
if "sim_mode" not in st.session_state:
    st.session_state.sim_mode = None
if "countdown" not in st.session_state:
    st.session_state.countdown = 10

left, mid, right = st.columns([1, 2, 1])

with mid:
    # ── SCREEN 1: MOD SEÇİMİ ──────────────────────────
    if st.session_state.sim_step == 1:
        st.markdown("""
        <div class="phone-frame">
            <div class="phone-status"><span>9:41</span><span>▲ 🔋</span></div>
            <div style="text-align:center;margin-bottom:16px">
                <span style="font-size:2rem">🆘</span>
                <div style="font-weight:800;color:#e53e3e;font-size:1.1rem">SafeLife</div>
            </div>
            <div class="screen-title">Rejim Seçin</div>
            <div class="screen-sub">Fəaliyyət növünüzü seçin</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🚶\nPiyada", use_container_width=True):
                st.session_state.sim_mode = "Pedestrian"
                st.session_state.sim_step = 2
                st.rerun()
        with c2:
            if st.button("🏍️\nMotosiklet", use_container_width=True):
                st.session_state.sim_mode = "Motorcycle"
                st.session_state.sim_step = 2
                st.rerun()
        with c3:
            if st.button("🚗\nAvtomobil", use_container_width=True):
                st.session_state.sim_mode = "Vehicle"
                st.session_state.sim_step = 2
                st.rerun()

    # ── SCREEN 2: MONİTORİNG AKTİV ────────────────────
    elif st.session_state.sim_step == 2:
        mode_emoji = {"Pedestrian": "🚶", "Motorcycle": "🏍️", "Vehicle": "🚗"}
        emoji = mode_emoji.get(st.session_state.sim_mode, "🚶")

        st.markdown(f"""
        <div class="phone-frame">
            <div class="phone-status"><span>9:41</span><span>▲ 🔋</span></div>
            <div style="text-align:center;margin-bottom:12px">
                <span style="background:#276749;color:#9ae6b4;
                      padding:4px 12px;border-radius:20px;font-size:0.8rem">
                    🟢 Monitoring Aktiv
                </span>
            </div>
            <div class="screen-title">{emoji} {st.session_state.sim_mode} Rejimi</div>
            <div class="screen-sub">7 sensor arxa planda işləyir</div>
            <div class="sensor-row"><span>📡 Akselerometr</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>🌀 Gyroscope</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>📍 GPS</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>🎙️ Mikrofon</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>🌡️ Bərometr</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>💡 İşıq sensoru</span><span style="color:#68d391">● Aktiv</span></div>
            <div class="sensor-row"><span>🧲 Maqnetometr</span><span style="color:#68d391">● Aktiv</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚠️ Qəza simulyasiya et", use_container_width=True, type="primary"):
            st.session_state.sim_step = 3
            st.rerun()

    # ── SCREEN 3: ZƏRBƏ AŞKARLANDI ────────────────────
    elif st.session_state.sim_step == 3:
        st.markdown("""
        <div class="phone-frame">
            <div class="phone-status"><span>9:41</span><span>▲ 🔋</span></div>
            <div class="sos-card">
                <div style="font-size:2.5rem">⚠️</div>
                <div style="font-size:1.2rem;font-weight:800;color:#fc8181;margin:8px 0">
                    ZƏRBƏ AŞKARLANDI
                </div>
                <div style="font-size:0.85rem;color:#a0aec0">
                    Ani zərbə qeydə alındı.<br>Sensorlar analiz edilir...
                </div>
            </div>
            <div style="margin-top:12px">
                <div style="font-size:0.8rem;color:#a0aec0;margin-bottom:6px">AI analizi:</div>
                <div class="sensor-row"><span>Akselerometr</span><span style="color:#fc8181">12.4g ⬆️</span></div>
                <div class="sensor-row"><span>Gyroscope</span><span style="color:#fc8181">9.8 rad/s ⬆️</span></div>
                <div class="sensor-row"><span>GPS sürəti</span><span style="color:#f6ad55">0 km/h ⬇️</span></div>
                <div class="sensor-row"><span>Risk skoru</span><span style="color:#fc8181">94% 🔴</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner("Analiz edilir..."):
            time.sleep(2)
        st.session_state.sim_step = 4
        st.session_state.countdown = 10
        st.rerun()

    # ── SCREEN 4: COUNTDOWN ───────────────────────────
    elif st.session_state.sim_step == 4:
        cnt = st.session_state.countdown
        color = "#68d391" if cnt > 6 else ("#f6ad55" if cnt > 3 else "#fc8181")

        st.markdown(f"""
        <div class="phone-frame">
            <div class="phone-status"><span>9:41</span><span>▲ 🔋</span></div>
            <div class="screen-title" style="margin-top:20px">Yaxşısınızmı?</div>
            <div class="screen-sub">Cavab olmasa avtomatik SOS göndəriləcək</div>
            <div style="text-align:center;margin:20px 0">
                <div style="width:120px;height:120px;border-radius:50%;
                     border:6px solid {color};margin:0 auto;
                     display:flex;align-items:center;justify-content:center">
                    <span style="font-size:3rem;font-weight:900;color:{color}">{cnt}</span>
                </div>
            </div>
            <div style="font-size:0.8rem;color:#a0aec0;text-align:center;margin-bottom:20px">
                Cavab olmadıqda SOS avtomatik göndəriləcək
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yaxşıyam", use_container_width=True):
                st.session_state.sim_step = 2
                st.session_state.countdown = 10
                st.rerun()
        with c2:
            if st.button("📞 Zəng et", use_container_width=True, type="primary"):
                st.session_state.sim_step = 5
                st.rerun()

        if cnt > 0:
            time.sleep(1)
            st.session_state.countdown -= 1
            st.rerun()
        else:
            st.session_state.sim_step = 5
            st.rerun()

    # ── SCREEN 5: SOS GÖNDƏRİLDİ ─────────────────────
    elif st.session_state.sim_step == 5:
        st.markdown("""
        <div class="phone-frame">
            <div class="phone-status"><span>9:41</span><span>▲ 🔋</span></div>
            <div style="text-align:center;margin:16px 0">
                <div style="font-size:3rem">✅</div>
                <div style="font-size:1.4rem;font-weight:800;color:#68d391">SOS Göndərildi</div>
                <div style="font-size:0.8rem;color:#a0aec0;margin-top:4px">
                    Bütün təcili əlaqələr xəbərdar edildi
                </div>
            </div>
            <div class="notify-card">
                <span style="color:#63b3ed">📍</span>
                <strong style="color:#e2e8f0"> GPS Paylaşıldı</strong><br>
                <span style="color:#a0aec0;font-size:0.8rem">40.4093°N, 49.8671°E · Nizami, Bakı</span>
            </div>
            <div class="notify-card">
                <span style="color:#68d391">👥</span>
                <strong style="color:#e2e8f0"> Əlaqələr Bildirildi</strong><br>
                <span style="color:#a0aec0;font-size:0.8rem">2 nəfər xəbərdar edildi</span>
            </div>
            <div class="notify-card">
                <span style="color:#f6ad55">🏥</span>
                <strong style="color:#e2e8f0"> Ən Yaxın Xəstəxana</strong><br>
                <span style="color:#a0aec0;font-size:0.8rem">
                    Bakı Şəhər Klinik Xəstəxanası — 1.2 km
                </span>
            </div>
            <div class="notify-card">
                <span style="color:#fc8181">🩺</span>
                <strong style="color:#e2e8f0"> Tibbi ID Göndərildi</strong><br>
                <span style="color:#a0aec0;font-size:0.8rem">
                    Qan qrupu: A+ · Allergiya: Yoxdur
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Yenidən başla", use_container_width=True):
            st.session_state.sim_step = 1
            st.session_state.sim_mode = None
            st.session_state.countdown = 10
            st.rerun()

with right:
    if st.session_state.sim_step > 1:
        st.markdown("#### 📊 Cari mərhələ")
        steps = {
            1: "Rejim seçimi",
            2: "Monitoring aktiv",
            3: "Zərbə aşkarlandı",
            4: "Geri sayım",
            5: "SOS göndərildi"
        }
        for num, label in steps.items():
            color = "#68d391" if num < st.session_state.sim_step else (
                "#e53e3e" if num == st.session_state.sim_step else "#2d3748"
            )
            icon = "✅" if num < st.session_state.sim_step else (
                "🔴" if num == st.session_state.sim_step else "⚪"
            )
            st.markdown(f"{icon} **{label}**" if num == st.session_state.sim_step
                        else f"{icon} {label}")